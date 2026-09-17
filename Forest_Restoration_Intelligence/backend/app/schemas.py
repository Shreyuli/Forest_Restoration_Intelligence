from typing import Literal, Optional

from pydantic import BaseModel, Field

Trend = Literal["increasing", "decreasing", "stable"]


class GeoCoord(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None


class AnalyzeRequest(BaseModel):
    """Structured input, matching the brief's worked JSON example."""

    deforestation: Optional[bool] = None
    deforestation_extent: Optional[str] = None
    temperature_trend: Optional[Trend] = None
    rainfall_trend: Optional[Trend] = None
    fragmentation: Optional[bool] = None
    region: Optional[str] = None
    geo: Optional[GeoCoord] = None
    session_id: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChainNode(BaseModel):
    node: str
    label: str
    evidence_source_ids: list[str] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"]


class ImpactedMetric(BaseModel):
    metric: str
    effect: str


class Recommendation(BaseModel):
    what_to_do: str
    why_it_works: str
    addresses_link: str
    impacted_metrics: list[ImpactedMetric]
    time_horizon: Literal["short", "medium", "long"]
    confidence: Literal["low", "medium", "high"]
    sources: list[str]


class ChainResult(BaseModel):
    result_id: str
    session_id: Optional[str] = None
    path: Literal["primary", "secondary", "combined"]
    variables_used: dict
    chain: list[ChainNode]
    recommendations: list[Recommendation]
    notes: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    session_id: str
    type: Literal["clarifying_question", "chain_result"]
    message: Optional[str] = None
    result: Optional[ChainResult] = None


class SessionStateResponse(BaseModel):
    session_id: str
    variables: dict
    history: list[dict]


class ChainEvidenceResponse(BaseModel):
    result_id: str
    chain_evidence: dict[str, list[dict]]
    recommendation_sources: dict[str, list[dict]]
