"""Central configuration for the Forest Restoration Intelligence backend."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORE_DIR = BASE_DIR / "store"
STORE_DIR.mkdir(exist_ok=True)

SQLITE_PATH = os.getenv("SQLITE_PATH", str(STORE_DIR / "fri.db"))
DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
# When no API key is configured (or USE_LLM=0), the system falls back to a
# deterministic, template-based extractor/composer. This keeps the core
# reasoning pipeline (the part being judged) fully offline and testable in
# CI without secrets, while still using Claude to polish prose when a key
# is available.
USE_LLM = bool(ANTHROPIC_API_KEY) and os.getenv("USE_LLM", "1") != "0"

TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "3"))
