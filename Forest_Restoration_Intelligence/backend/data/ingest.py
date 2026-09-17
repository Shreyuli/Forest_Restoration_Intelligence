"""Ingestion pipeline: loads the seed corpus into SQLite (Source, Chunk,
EvidenceCoefficient, GeoBiomeLookup) and builds the Chroma vector index.

Run with:  python -m data.ingest   (from the backend/ directory)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import db_models, vectorstore  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from data.evidence_coefficients import EVIDENCE_COEFFICIENTS  # noqa: E402
from data.geo_biome import GEO_BIOME_LOOKUP  # noqa: E402
from data.seed_sources import SOURCES  # noqa: E402


def run():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    all_chunks = []
    try:
        for source in SOURCES:
            db.add(
                db_models.Source(
                    source_id=source["source_id"],
                    title=source["title"],
                    publisher=source["publisher"],
                    year=source["year"],
                    url=source["url"],
                )
            )
            for idx, (text, tag) in enumerate(source["chunks"]):
                chunk_id = f"{source['source_id']}_{idx}"
                db.add(
                    db_models.Chunk(
                        chunk_id=chunk_id,
                        source_id=source["source_id"],
                        text=text,
                        chain_link_tag=tag,
                    )
                )
                all_chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "source_id": source["source_id"],
                        "text": text,
                        "chain_link_tag": tag,
                    }
                )

        for coeff in EVIDENCE_COEFFICIENTS:
            db.add(db_models.EvidenceCoefficient(**coeff))

        for row in GEO_BIOME_LOOKUP:
            db.add(db_models.GeoBiomeLookup(**row))

        db.commit()
    finally:
        db.close()

    n_indexed = vectorstore.build_index(all_chunks)
    print(f"Ingested {len(SOURCES)} sources, {len(all_chunks)} chunks "
          f"({n_indexed} indexed in the vector store), "
          f"{len(EVIDENCE_COEFFICIENTS)} evidence coefficients, "
          f"{len(GEO_BIOME_LOOKUP)} geo-biome rows.")


if __name__ == "__main__":
    run()
