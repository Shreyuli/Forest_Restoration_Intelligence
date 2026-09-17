"""Thin wrapper around the Anthropic API, used only for prose polishing.

The chain/evidence/recommendation *facts* are always produced deterministically
by chain_engine.py — the LLM is never the source of truth for citations or
structured fields, only for rewriting already-approved text more naturally.
Any failure (no key, network error, timeout) falls back to the deterministic
text silently, so the pipeline never depends on the LLM being available.
"""
from .config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, USE_LLM

_client = None


def _get_client():
    global _client
    if _client is None:
        import anthropic

        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def polish_recommendation_text(what_to_do: str, why_it_works: str, evidence_snippets: list[str]) -> str:
    """Rewrite `why_it_works` in a more natural voice, grounded strictly in the
    given evidence snippets. Returns the original text on any failure."""
    if not USE_LLM:
        return why_it_works

    try:
        client = _get_client()
        snippets_block = "\n".join(f"- {s}" for s in evidence_snippets) or "(no additional evidence snippets)"
        message = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Rewrite the following restoration-recommendation rationale in one or two "
                        "clear sentences for a forest-restoration practitioner. Use ONLY the facts "
                        "already present in the rationale and evidence snippets below — do not add "
                        "new claims, numbers, or sources. Do not mention sources by name.\n\n"
                        f"Recommendation: {what_to_do}\n"
                        f"Current rationale: {why_it_works}\n"
                        f"Supporting evidence snippets:\n{snippets_block}\n\n"
                        "Rewritten rationale:"
                    ),
                }
            ],
        )
        text = "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        ).strip()
        return text or why_it_works
    except Exception:
        return why_it_works
