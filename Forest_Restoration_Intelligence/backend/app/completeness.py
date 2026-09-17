"""Completeness checker: decides whether we have enough signal to reason,
or need to ask a clarifying question first.

Minimum bar (per PRD): a land-cover disturbance signal (deforestation or
fragmentation) PLUS at least one driver (a climate trend, or fragmentation
itself when it is the stated driver). Region/geo is treated as a soft
requirement: when missing we proceed using generic/global evidence
coefficients and note the reduced precision, rather than blocking — this
keeps the two worked scenarios from the brief (neither of which states a
region) answerable without an unnecessary extra turn, while still gating on
the cases that genuinely lack a reasoning starting point.
"""
from typing import Optional


def check_completeness(variables: dict) -> Optional[str]:
    land_cover_signal = bool(variables.get("deforestation") or variables.get("fragmentation"))
    driver_signal = bool(
        variables.get("temperature_trend") in ("increasing", "decreasing")
        or variables.get("rainfall_trend") in ("increasing", "decreasing")
        or variables.get("fragmentation")
    )

    if not land_cover_signal:
        return (
            "I need a starting signal to reason about degradation here. Has this "
            "forest area experienced deforestation, or is habitat fragmentation "
            "(e.g. isolation caused by agricultural expansion) part of the "
            "picture?"
        )

    if not driver_signal:
        return (
            "You've mentioned land-cover change, but I need at least one driver "
            "to trace the causal chain: has rainfall or average temperature "
            "changed in this area, or is the decline primarily due to "
            "fragmentation (e.g. agricultural expansion isolating the forest)?"
        )

    return None


def region_note(variables: dict, geo_biome: Optional[dict]) -> Optional[str]:
    if variables.get("region") or geo_biome:
        return None
    return (
        "No region, biome, or geo-coordinates were provided, so biome-specific "
        "quantified effect sizes could not be applied — general/global "
        "coefficients were used instead. Provide a region or lat/lon for a "
        "more site-specific recommendation."
    )
