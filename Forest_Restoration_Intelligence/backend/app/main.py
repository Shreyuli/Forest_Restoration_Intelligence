from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import chain_engine, completeness, composer, db_models, geo_lookup, parser
from .db import get_db, init_db
from .schemas import (
    AnalyzeRequest,
    ChainEvidenceResponse,
    ChatRequest,
    ChatResponse,
    SessionStateResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Forest Restoration Intelligence", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_or_create_session(db: Session, session_id: Optional[str]) -> db_models.SessionRecord:
    if session_id:
        session = db.query(db_models.SessionRecord).filter_by(session_id=session_id).first()
        if session:
            return session
    session = db_models.SessionRecord(variables={}, history=[])
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _merge_variables(old: dict, new: dict) -> dict:
    merged = dict(old)
    for key, value in new.items():
        if value is not None:
            merged[key] = value
    return merged


def _record_result(db: Session, session_id: Optional[str], result_dict: dict) -> None:
    record = db_models.ChainResultRecord(
        result_id=result_dict["result_id"],
        session_id=session_id,
        payload=result_dict,
    )
    db.add(record)
    db.commit()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    session = _get_or_create_session(db, req.session_id)

    extracted = parser.extract_variables(req.message)
    variables = _merge_variables(
        session.variables or {},
        {
            "deforestation": extracted["deforestation"],
            "fragmentation": extracted["fragmentation"],
            "temperature_trend": extracted["temperature_trend"],
            "rainfall_trend": extracted["rainfall_trend"],
            "region": extracted["region"],
        },
    )

    history = list(session.history or [])
    history.append({"role": "user", "content": req.message})

    clarifying = completeness.check_completeness(variables)
    if clarifying:
        history.append({"role": "assistant", "content": clarifying})
        session.variables = variables
        session.history = history
        db.add(session)
        db.commit()
        return ChatResponse(session_id=session.session_id, type="clarifying_question", message=clarifying)

    result_dict = chain_engine.run_chain_result(db, variables, session.session_id)
    note = completeness.region_note(variables, None)
    if note:
        result_dict["notes"].append(note)
    result = composer.compose(result_dict)

    history.append({"role": "assistant", "content": f"Produced chain result {result.result_id} ({result.path} path)."})
    session.variables = variables
    session.history = history
    db.add(session)
    db.commit()
    _record_result(db, session.session_id, result.model_dump())

    return ChatResponse(session_id=session.session_id, type="chain_result", result=result)


@app.post("/analyze", response_model=ChatResponse)
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    session = _get_or_create_session(db, req.session_id)

    geo_biome = None
    if req.geo and req.geo.lat is not None and req.geo.lon is not None:
        geo_biome = geo_lookup.lookup_biome(db, req.geo.lat, req.geo.lon)

    variables = _merge_variables(
        session.variables or {},
        {
            "deforestation": req.deforestation,
            "fragmentation": req.fragmentation,
            "temperature_trend": req.temperature_trend,
            "rainfall_trend": req.rainfall_trend,
            "region": req.region or (geo_biome["region_key"] if geo_biome else None),
            "biome": geo_biome["typical_biome"] if geo_biome else None,
        },
    )

    history = list(session.history or [])
    history.append({"role": "user", "content": req.model_dump()})

    clarifying = completeness.check_completeness(variables)
    if clarifying:
        history.append({"role": "assistant", "content": clarifying})
        session.variables = variables
        session.history = history
        db.add(session)
        db.commit()
        return ChatResponse(session_id=session.session_id, type="clarifying_question", message=clarifying)

    result_dict = chain_engine.run_chain_result(db, variables, session.session_id)
    note = completeness.region_note(variables, geo_biome)
    if note:
        result_dict["notes"].append(note)
    result = composer.compose(result_dict)

    history.append({"role": "assistant", "content": f"Produced chain result {result.result_id} ({result.path} path)."})
    session.variables = variables
    session.history = history
    db.add(session)
    db.commit()
    _record_result(db, session.session_id, result.model_dump())

    return ChatResponse(session_id=session.session_id, type="chain_result", result=result)


@app.get("/session/{session_id}", response_model=SessionStateResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(db_models.SessionRecord).filter_by(session_id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionStateResponse(
        session_id=session.session_id,
        variables=session.variables or {},
        history=session.history or [],
    )


@app.get("/chain-evidence/{result_id}", response_model=ChainEvidenceResponse)
def chain_evidence(result_id: str, db: Session = Depends(get_db)):
    record = db.query(db_models.ChainResultRecord).filter_by(result_id=result_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Chain result not found")

    payload = record.payload

    def _source_detail(source_id: str) -> dict:
        src = db.query(db_models.Source).filter_by(source_id=source_id).first()
        if not src:
            return {"source_id": source_id}
        return {
            "source_id": src.source_id,
            "title": src.title,
            "publisher": src.publisher,
            "year": src.year,
            "url": src.url,
        }

    chain_evidence_map = {
        node["node"]: [_source_detail(sid) for sid in node["evidence_source_ids"]]
        for node in payload["chain"]
    }
    recommendation_sources = {
        rec["what_to_do"]: [_source_detail(sid) for sid in rec["sources"]]
        for rec in payload["recommendations"]
    }

    return ChainEvidenceResponse(
        result_id=result_id,
        chain_evidence=chain_evidence_map,
        recommendation_sources=recommendation_sources,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
