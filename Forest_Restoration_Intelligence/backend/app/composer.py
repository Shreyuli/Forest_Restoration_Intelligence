"""Response Composer: enforces the strict output schema and, when an LLM key
is configured, polishes recommendation prose without changing any structured
field, evidence source, or citation produced by the chain engine.
"""
from . import llm_client
from .schemas import ChainNode, ChainResult, ImpactedMetric, Recommendation


def compose(raw: dict) -> ChainResult:
    for rec in raw["recommendations"]:
        snippets = []
        # Pull a couple of the actual retrieved snippets as grounding context
        # for the LLM polish step, so it cannot drift from the evidence.
        for src in rec["sources"][:3]:
            snippets.append(src)
        rec["why_it_works"] = llm_client.polish_recommendation_text(
            rec["what_to_do"], rec["why_it_works"], snippets
        )

    chain = [
        ChainNode(
            node=n["node"],
            label=n["label"],
            evidence_source_ids=n["evidence_source_ids"],
            confidence=n["confidence"],
        )
        for n in raw["chain"]
    ]
    recommendations = [
        Recommendation(
            what_to_do=r["what_to_do"],
            why_it_works=r["why_it_works"],
            addresses_link=r["addresses_link"],
            impacted_metrics=[ImpactedMetric(**m) for m in r["impacted_metrics"]],
            time_horizon=r["time_horizon"],
            confidence=r["confidence"],
            sources=r["sources"],
        )
        for r in raw["recommendations"]
    ]

    return ChainResult(
        result_id=raw["result_id"],
        session_id=raw.get("session_id"),
        path=raw["path"],
        variables_used=raw["variables_used"],
        chain=chain,
        recommendations=recommendations,
        notes=raw.get("notes", []),
    )
