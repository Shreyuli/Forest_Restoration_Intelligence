import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String, Text

from .db import Base


def _uuid() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"

    source_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    publisher = Column(String, nullable=False)
    year = Column(String, nullable=False)
    url = Column(String, nullable=False)


class Chunk(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey("sources.source_id"), nullable=False)
    text = Column(Text, nullable=False)
    chain_link_tag = Column(String, nullable=False, index=True)


class EvidenceCoefficient(Base):
    __tablename__ = "evidence_coefficients"

    id = Column(String, primary_key=True, default=_uuid)
    intervention = Column(String, nullable=False)
    addresses_link = Column(String, nullable=False, index=True)
    effect_metric = Column(String, nullable=False)
    effect_size = Column(String, nullable=False)
    effect_range = Column(String, nullable=True)
    biome = Column(String, nullable=False)
    source_id = Column(String, ForeignKey("sources.source_id"), nullable=False)


class GeoBiomeLookup(Base):
    __tablename__ = "geo_biome_lookup"

    region_key = Column(String, primary_key=True)
    lat_min = Column(Float, nullable=False)
    lat_max = Column(Float, nullable=False)
    lon_min = Column(Float, nullable=False)
    lon_max = Column(Float, nullable=False)
    typical_biome = Column(String, nullable=False)
    baseline_rainfall = Column(String, nullable=False)
    baseline_temp = Column(String, nullable=False)


class SessionRecord(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, default=_uuid)
    created_at = Column(DateTime, default=_now)
    variables = Column(JSON, default=dict)
    history = Column(JSON, default=list)


class ChainResultRecord(Base):
    __tablename__ = "chain_results"

    result_id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=True)
    created_at = Column(DateTime, default=_now)
    payload = Column(JSON, nullable=False)
