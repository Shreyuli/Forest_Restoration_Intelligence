"""Causal-Chain Reasoning Engine.

Walks the fixed chain template(s) based on which input variables are
activated, binds retrieved evidence to every traversed edge, and matches
restoration recommendations to the most upstream broken link.
"""
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from . import chain_template, db_models, vectorstore
from .config import TOP_K

# Ordered upstream-to-downstream edge tags per path, used to find the most
# upstream link that has a matching intervention.
PRIMARY_EDGE_ORDER = [
    "deforestation_temp_rainfall->water_stress",
    "water_stress->vegetation_stress",
    "vegetation_stress->habitat_degradation",
    "habitat_degradation->biodiversity_decline",
]
SECONDARY_EDGE_ORDER = [
    "deforestation_agri->fragmentation",
    "fragmentation->habitat_degradation",
    "habitat_degradation->biodiversity_decline",
]


def _confidence_from_hits(n_hits: int) -> str:
    if n_hits >= 2:
        return "high"
    if n_hits == 1:
        return "medium"
    return "low"


def determine_path(variables: dict) -> str:
    fragmentation = bool(variables.get("fragmentation"))
    temp = variables.get("temperature_trend")
    rain = variables.get("rainfall_trend")
    climate_signal = temp in ("increasing", "decreasing") or rain in ("increasing", "decreasing")

    if fragmentation and not climate_signal:
        return "secondary"
    if climate_signal and fragmentation:
        return "combined"
    if climate_signal:
        return "primary"
    if fragmentation:
        return "secondary"
    # Completeness checker should have already blocked this case with a
    # clarifying question; primary is a safe default if reached anyway.
    return "primary"


def _build_chain_nodes(template: list[dict]) -> list[dict]:
    nodes = []
    for entry in template:
        hits = vectorstore.query_by_tag(entry["tag"], top_k=TOP_K)
        source_ids = sorted({h["source_id"] for h in hits})
        nodes.append(
            {
                "node": entry["node"],
                "label": entry["label"],
                "edge_tag": entry["tag"],
                "evidence_source_ids": source_ids,
                "confidence": _confidence_from_hits(len(source_ids)),
            }
        )
    return nodes


def build_chain(path: str) -> list[dict]:
    if path == "primary":
        return _build_chain_nodes(chain_template.PRIMARY_CHAIN)
    if path == "secondary":
        return _build_chain_nodes(chain_template.SECONDARY_CHAIN)
    if path == "combined":
        primary_nodes = _build_chain_nodes(chain_template.PRIMARY_CHAIN)
        # Insert the fragmentation node right after the trigger, before
        # water_stress, since both branches originate at the same
        # deforestation trigger and converge at habitat_degradation.
        frag_entry = chain_template.SECONDARY_CHAIN[1]  # "fragmentation" node
        frag_hits = vectorstore.query_by_tag(frag_entry["tag"], top_k=TOP_K)
        frag_node = {
            "node": frag_entry["node"],
            "label": frag_entry["label"],
            "edge_tag": frag_entry["tag"],
            "evidence_source_ids": sorted({h["source_id"] for h in frag_hits}),
            "confidence": _confidence_from_hits(len(frag_hits)),
        }
        return [primary_nodes[0], frag_node] + primary_nodes[1:]
    raise ValueError(f"Unknown path: {path}")


def _most_upstream_addressable_edge(path: str) -> Optional[str]:
    order = PRIMARY_EDGE_ORDER if path in ("primary", "combined") else SECONDARY_EDGE_ORDER
    addressable = {i["addresses_link"] for i in chain_template.INTERVENTIONS}
    for edge in order:
        if edge in addressable:
            return edge
    return None


def _get_evidence_coefficients(db: Session, addresses_link: str, biome: Optional[str]) -> list[db_models.EvidenceCoefficient]:
    rows = (
        db.query(db_models.EvidenceCoefficient)
        .filter(db_models.EvidenceCoefficient.addresses_link == addresses_link)
        .all()
    )
    if not rows:
        return []
    if biome:
        biome_matches = [r for r in rows if r.biome == biome]
        if biome_matches:
            return biome_matches
    return rows


def _build_recommendation(db: Session, intervention: dict, variables: dict, upstream: bool) -> dict:
    biome = variables.get("biome")
    coeff_rows = _get_evidence_coefficients(db, intervention["addresses_link"], biome)
    coeff_rows = [r for r in coeff_rows if r.intervention == intervention["what_to_do"]] or coeff_rows

    hits = (
        vectorstore.query_by_tag(intervention["retrieval_tag"], top_k=TOP_K)
        if intervention["retrieval_tag"]
        else []
    )
    source_ids = {h["source_id"] for h in hits}
    for r in coeff_rows:
        source_ids.add(r.source_id)

    impacted_metrics = [
        {"metric": r.effect_metric, "effect": f"{r.effect_size} ({r.effect_range})" if r.effect_range else r.effect_size}
        for r in coeff_rows
        if r.intervention == intervention["what_to_do"]
    ]
    if not impacted_metrics and coeff_rows:
        impacted_metrics = [
            {"metric": r.effect_metric, "effect": f"{r.effect_size} ({r.effect_range})" if r.effect_range else r.effect_size}
            for r in coeff_rows
        ]

    n_evidence = len(source_ids)
    confidence = _confidence_from_hits(n_evidence)
    if not upstream and confidence == "high":
        confidence = "medium"  # downstream/secondary recs are capped below upstream picks

    why = intervention["why_template"]
    if not upstream:
        why += " This addresses a downstream symptom rather than the most upstream broken link; the upstream intervention above is preferred where feasible."

    return {
        "what_to_do": intervention["what_to_do"],
        "why_it_works": why,
        "addresses_link": intervention["addresses_link"],
        "impacted_metrics": impacted_metrics or [{"metric": "qualitative_habitat_condition", "effect": "expected improvement; no quantified coefficient in corpus for this biome"}],
        "time_horizon": intervention["time_horizon"],
        "confidence": confidence if source_ids else "low",
        "sources": sorted(source_ids),
    }


def build_recommendations(db: Session, path: str, variables: dict) -> tuple[list[dict], list[str]]:
    notes = []
    upstream_edge = _most_upstream_addressable_edge(path)
    upstream_interventions = [
        i for i in chain_template.INTERVENTIONS if i["addresses_link"] == upstream_edge
    ]
    recommendations = [
        _build_recommendation(db, i, variables, upstream=True) for i in upstream_interventions
    ]
    notes.append(
        f"Recommendations prioritize the most upstream broken link ('{upstream_edge}') "
        "because interrupting the cause is more durable than treating downstream "
        "symptoms further down the chain."
    )

    # Include one complementary downstream recommendation (biodiversity-facing)
    # when it addresses a different edge than the upstream pick, for
    # completeness — clearly marked as secondary to the upstream fix.
    downstream_edge = "habitat_degradation->biodiversity_decline"
    if downstream_edge != upstream_edge:
        downstream_interventions = [
            i for i in chain_template.INTERVENTIONS if i["addresses_link"] == downstream_edge
        ]
        recommendations += [
            _build_recommendation(db, i, variables, upstream=False) for i in downstream_interventions
        ]

    return recommendations, notes


def run_chain_result(db: Session, variables: dict, session_id: Optional[str]) -> dict:
    path = determine_path(variables)
    chain = build_chain(path)
    recommendations, notes = build_recommendations(db, path, variables)

    return {
        "result_id": uuid.uuid4().hex[:12],
        "session_id": session_id,
        "path": path,
        "variables_used": variables,
        "chain": chain,
        "recommendations": recommendations,
        "notes": notes,
    }
