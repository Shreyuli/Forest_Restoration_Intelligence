# Technical Requirements Document (TRD)
## Forest Restoration Intelligence — Darukaa.Earth Hackathon

**Companion document to:** PRD_Forest_Restoration_Intelligence.md
**Status:** Draft v1.0 (see `docs/IMPLEMENTATION_NOTES.md` for the as-built deviations)

---

## 1. Architecture Overview

```
Client (React chat UI: text / structured JSON / geo)
        │ REST
Conversation Orchestrator (FastAPI: session store, parser, completeness checker)
        │
        ├── Retrieval Layer (RAG): TF-IDF vector index over the forest-restoration corpus,
        │     chunks tagged by chain-link, filtered retrieval per edge
        │
        └── Causal-Chain Reasoning Engine: walks the fixed chain template based on
              activated variables, binds evidence per edge, matches recommendations
              to the most upstream broken link
                │
        Response Composer: enforces the output schema, optional Claude prose polish
                │
        Client renders the causal chain as a flow diagram + recommendation cards
```

---

## 2. Tech Stack (as built — see IMPLEMENTATION_NOTES.md for why it differs from the original draft below)

| Layer | Original plan | As built |
|---|---|---|
| LLM | Claude (Sonnet-class) via Anthropic API | Same — used only for optional recommendation-prose polishing |
| Embeddings | `text-embedding-3-small` / `voyage-2` | Local TF-IDF (no external embedding API — offline, deterministic, no key required) |
| Vector DB | Chroma (local/dev) → Pinecone/Weaviate (hosted) | In-process TF-IDF cosine-similarity index (numpy), persisted to disk |
| Backend | Python, FastAPI | Same |
| Structured data store | PostgreSQL or SQLite | SQLite |
| Frontend | Minimal React chat UI | Same (Vite + React) |
| Deployment | Render/Railway (backend) + Vercel (frontend) | Same, config included; live URL depends on the account owner deploying |
| CI/CD | GitHub Actions | Same |

---

## 3. Knowledge Layer Design

### 3.1 Data Sources (seed corpus)
16 real, citable sources: FAO State of the World's Forests 2020, IPCC AR6 WG2 Ch.2, and peer-reviewed forest ecology literature covering canopy loss/water-stress, drought-driven tree mortality, fragmentation and species richness, and forest restoration outcomes (natural regeneration, active planting, native species reintroduction, connectivity restoration). Full list with URLs in `backend/data/seed_sources.py`.

### 3.2 Ingestion Pipeline
`backend/data/ingest.py`:
1. Loads `SOURCES` (source metadata + chunk text + chain-link tag per chunk) from `seed_sources.py`.
2. Writes `Source` and `Chunk` rows to SQLite.
3. Writes `EvidenceCoefficient` and `GeoBiomeLookup` seed rows.
4. Builds the TF-IDF vector index over all chunks and persists it (`backend/store/vector_index.pkl`).

### 3.3 Retrieval Strategy
- The causal-chain engine determines which edges are activated for the given input.
- For each activated edge, `vectorstore.query_by_tag(tag, top_k=3)` retrieves the top-k chunks whose `chain_link_tag` exactly matches that edge, ranked by TF-IDF cosine similarity.
- For recommendations, the same mechanism retrieves chunks tagged with the specific intervention's `retrieval_tag`.

### 3.4 Retrieval Transparency
- `GET /chain-evidence/{result_id}` returns the full per-edge and per-recommendation citation trail (title, publisher, year, URL) — the auditable proof of grounding.

---

## 4. Causal-Chain Reasoning Engine

- **Chain template** (`backend/app/chain_template.py`): fixed directed graph —
  Primary: `deforestation + temperature_increase + rainfall_decrease → water_stress → vegetation_stress → habitat_degradation → biodiversity_decline`
  Secondary: `deforestation / agricultural_expansion → fragmentation → habitat_degradation → biodiversity_decline`
- **Activation logic** (`chain_engine.determine_path`): a climate signal (temperature or rainfall trend) routes to the primary path; fragmentation without a climate signal routes to the secondary path; both present routes to a combined chain.
- **Evidence binding**: every traversed edge is resolved against the vector index; confidence is `high`/`medium`/`low` based on how many distinct sources were retrieved. No edge is asserted without a resolvable source_id.
- **Recommendation matching**: interventions are matched to the most upstream edge (in traversal order) that has a defined intervention, with an explicit note stating why upstream fixes are preferred. A complementary downstream (biodiversity-facing) recommendation is included when applicable, marked as secondary to the upstream fix.

---

## 5. Conversational Engine

- **Session memory**: `SessionRecord` (SQLite) stores merged variables and full turn history, keyed by `session_id`.
- **Completeness checker** (`app/completeness.py`): requires a land-cover signal (deforestation or fragmentation) AND at least one driver (a climate trend, or fragmentation itself as the driver). Region/geo is a soft requirement — missing region does not block reasoning, it falls back to general/global evidence coefficients and appends a note (this is a deliberate, documented deviation from a hard region gate — see IMPLEMENTATION_NOTES.md).
- **Context carry-over**: each `/chat` turn merges newly extracted variables into the session's existing variables (only overwriting fields the new message actually specifies), then re-runs completeness + the chain engine.

---

## 6. Data Schema

Implemented in `backend/app/db_models.py` (SQLAlchemy / SQLite):

```
Source(source_id, title, publisher, year, url)
Chunk(chunk_id, source_id, text, chain_link_tag)
EvidenceCoefficient(id, intervention, addresses_link, effect_metric, effect_size, effect_range, biome, source_id)
GeoBiomeLookup(region_key, lat_min, lat_max, lon_min, lon_max, typical_biome, baseline_rainfall, baseline_temp)
SessionRecord(session_id, created_at, variables JSON, history JSON)
ChainResultRecord(result_id, session_id, created_at, payload JSON)
```

`ChainResult` (the API response object) is a Pydantic schema in `app/schemas.py`: `chain: [{node, label, evidence_source_ids, confidence}]`, `recommendations: [{what_to_do, why_it_works, addresses_link, impacted_metrics, time_horizon, confidence, sources}]`.

---

## 7. API Design

| Endpoint | Method | Purpose |
|---|---|---|
| `/chat` | POST | Free-text turn → clarifying question or full ChainResult, wrapped in a `ChatResponse` |
| `/analyze` | POST | Structured JSON input → clarifying question or full ChainResult (same `ChatResponse` shape, so incomplete JSON input also asks rather than erroring, per PRD §8) |
| `/session/{id}` | GET | Retrieve session state/history |
| `/chain-evidence/{result_id}` | GET | Full per-link + per-recommendation citation trail |

---

## 8. Input Handling Details

- **Text**: `app/parser.py` — deterministic regex/keyword extraction (deforestation, fragmentation, temperature/rainfall trend, region hint). Deliberately rule-based rather than LLM-based, so extraction is reproducible in CI without an API key; see IMPLEMENTATION_NOTES.md.
- **JSON**: validated via Pydantic (`AnalyzeRequest`); missing required fields route through the same completeness checker as `/chat`.
- **Geo-coordinates (bonus)**: `app/geo_lookup.py` looks up `GeoBiomeLookup` by lat/lon range to infer biome + baseline rainfall/temperature, covering 8 representative forest regions.

---

## 9. Deployment & CI/CD

- **Repo structure**: `/backend`, `/frontend`, `/docs`, `/.github/workflows`.
- **CI (GitHub Actions, `.github/workflows/ci.yml`)**: ruff lint + pytest (backend), `npm run build` (frontend), on every push/PR to `main`.
- **CD**: `backend/render.yaml` (Render) and `backend/Procfile` (Railway/Heroku-style) for the API; `frontend/vercel.json` for the SPA. Actual deployment requires the account owner's credentials — see the top-level README for the exact steps.

---

## 10. Testing & Evaluation Plan (implemented in `backend/tests/`)

| Test | Validates |
|---|---|
| `test_chat_primary_scenario_matches_brief_example` / `test_primary_path_full_chain` | Exact brief input → 5-node primary chain, all edges evidenced, water-stress-linked recommendation present |
| `test_chat_fragmentation_scenario` / `test_secondary_path_routes_through_fragmentation` | Fragmentation-only input routes through the secondary path, not water-stress |
| `test_chat_incomplete_input_triggers_clarifying_question` | Input with no disturbance/driver signal triggers a clarifying question, not a chain |
| `test_every_edge_and_recommendation_has_resolvable_sources` | Every chain edge and recommendation resolves to a real `Source` row |
| `test_chain_evidence_endpoint_returns_citation_trail` | `/chain-evidence/{id}` returns real source metadata |
| `test_session_state_persists_and_context_carries_over` | Multi-turn session merges variables and re-runs reasoning |

---

## 11. Risks & Mitigations (as built)

| Risk | Mitigation |
|---|---|
| Corpus too narrow → chain edges lack evidence | 16 sources deliberately chosen to cover every tag in the chain template at least once (most with 2–3) |
| LLM cites a source that doesn't exist | The LLM is never the source of citations — `chain_engine.py` binds sources deterministically from the vector index/coefficient table; the LLM only rewrites already-approved prose |
| Fixed chain template feels rigid | Recommendation matching (which link to prioritize, which intervention, quantified effect) is where the reasoning depth lives, per the original plan |
| Geo lookup table too sparse | Scoped to 8 representative regions, documented as a bonus feature, not global coverage |
| Compiled-dependency install risk (chromadb/scikit-learn) on an unknown grader machine | Replaced with a pure numpy TF-IDF index — no C compiler or model download required at install time |
