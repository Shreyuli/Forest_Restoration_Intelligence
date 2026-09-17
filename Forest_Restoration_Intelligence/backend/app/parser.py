"""Rule-based free-text -> structured variable extraction.

Deterministic by design (no LLM call) so the reasoning pipeline is testable
offline/in CI without an API key. When USE_LLM is enabled, `llm_client` can
be used upstream to normalize messy input before this still runs as the
authoritative structured extractor — see composer.py for where the LLM is
actually used (prose polishing only, never fact extraction).
"""
import re
from typing import Optional

DEFORESTATION_PATTERNS = [
    r"deforestation", r"forest loss", r"clear[- ]?cut", r"logging",
    r"forest (has been|was) cleared", r"land[- ]?clearing", r"cleared for",
]

FRAGMENTATION_PATTERNS = [
    r"fragmentation", r"fragmented", r"isolated", r"agricultural expansion",
    r"agriculture expansion", r"surrounded by (cropland|farmland|agriculture)",
    r"forest patch", r"habitat patch",
]

TEMP_INCREASE_PATTERNS = [
    r"temperature (has |have )?increased", r"warmer", r"warming",
    r"rising temperature", r"average temperature has increased",
]
TEMP_DECREASE_PATTERNS = [
    r"temperature (has |have )?decreased", r"cooler", r"cooling",
]
TEMP_STABLE_KEYWORD = r"temperature"

RAIN_DECREASE_PATTERNS = [
    r"rainfall (has |have )?decreased", r"rainfall.*declin", r"drier", r"less rain",
    r"precipitation (has |have )?decreased",
]
RAIN_INCREASE_PATTERNS = [
    r"rainfall (has |have )?increased", r"wetter", r"more rain",
]
RAIN_STABLE_KEYWORD = r"rainfall|precipitation"

STABLE_TRIGGER_PATTERN = r"no (major |significant )?change|unchanged|remained stable|stayed (the )?same"

BIODIVERSITY_DECLINE_PATTERNS = [
    r"biodiversity.*declin", r"species.*declin", r"losing species", r"habitat loss",
]

REGION_HINT_PATTERN = re.compile(
    r"\bin (the )?([A-Z][A-Za-z\s]{2,40}?)(?:\.|,|$)"
)


def _any(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _detect_trend(
    text: str, increase_patterns: list[str], decrease_patterns: list[str], stable_keyword: str
) -> Optional[str]:
    if _any(increase_patterns, text):
        return "increasing"
    if _any(decrease_patterns, text):
        return "decreasing"
    if re.search(STABLE_TRIGGER_PATTERN, text, re.IGNORECASE) and re.search(
        stable_keyword, text, re.IGNORECASE
    ):
        return "stable"
    return None


def extract_variables(text: str) -> dict:
    """Best-effort deterministic extraction of the structured variable set."""
    t = text.strip()

    deforestation = True if _any(DEFORESTATION_PATTERNS, t) else None
    fragmentation = True if _any(FRAGMENTATION_PATTERNS, t) else None

    temperature_trend = _detect_trend(t, TEMP_INCREASE_PATTERNS, TEMP_DECREASE_PATTERNS, TEMP_STABLE_KEYWORD)
    rainfall_trend = _detect_trend(t, RAIN_INCREASE_PATTERNS, RAIN_DECREASE_PATTERNS, RAIN_STABLE_KEYWORD)

    biodiversity_decline_mentioned = _any(BIODIVERSITY_DECLINE_PATTERNS, t)

    region_match = REGION_HINT_PATTERN.search(t)
    region = region_match.group(2).strip() if region_match else None

    return {
        "deforestation": deforestation,
        "fragmentation": fragmentation,
        "temperature_trend": temperature_trend,
        "rainfall_trend": rainfall_trend,
        "region": region,
        "biodiversity_decline_mentioned": biodiversity_decline_mentioned,
        "raw_text": t,
    }
