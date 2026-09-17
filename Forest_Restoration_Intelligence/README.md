# Forest Restoration Intelligence

An AI system that reasons about forest degradation and recommends
evidence-backed restoration strategies — built for the Darukaa.Earth
Hackathon (Placement Track).

Given a description of a degraded forest area (free text, structured JSON,
or geo-coordinates), the system:

1. Extracts structured variables (deforestation, temperature trend, rainfall
   trend, fragmentation, region/biome).
2. Walks a fixed causal-chain template from disturbance to biodiversity
   decline, activating only the nodes/edges the input actually supports.
3. Retrieves real evidence (RAG over a curated forest-restoration corpus)
   for **every traversed edge**, not just the final answer.
4. Recommends specific restoration strategies, each mapped to the chain-link
   it addresses, with quantified impact, time horizon, confidence, and
   citations.

See [`docs/PRD_Forest_Restoration_Intelligence.md`](docs/PRD_Forest_Restoration_Intelligence.md)
and [`docs/TRD_Forest_Restoration_Intelligence.md`](docs/TRD_Forest_Restoration_Intelligence.md)
for the design docs, and [`docs/IMPLEMENTATION_NOTES.md`](docs/IMPLEMENTATION_NOTES.md)
for where the as-built system deliberately deviates from the original TRD
and why.

---

## Architecture

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

**Fixed causal-chain template**

```
Primary (climate-driven):
  deforestation + temperature_increase + rainfall_decrease
      → water_stress → vegetation_stress → habitat_degradation → biodiversity_decline

Secondary (fragmentation-driven, no climate signal required):
  deforestation / agricultural_expansion → fragmentation
      → habitat_degradation → biodiversity_decline
```

Only the path the input actually supports is activated — the engine picks
the primary path when a climate trend is present, the secondary path when
fragmentation is present without a climate trend, and a combined chain when
both are present (see `backend/app/chain_engine.py::determine_path`).

**Tech stack:** Python/FastAPI backend, SQLite for structured data, an
in-process TF-IDF vector index for retrieval (see
[`docs/IMPLEMENTATION_NOTES.md`](docs/IMPLEMENTATION_NOTES.md) for why this
replaced Chroma + hosted embeddings), optional Claude (Anthropic API) for
recommendation-prose polishing, and a minimal React (Vite) chat frontend.

---

## Database / schema

SQLite (`backend/app/db_models.py`):

| Table | Columns |
|---|---|
| `sources` | `source_id, title, publisher, year, url` |
| `chunks` | `chunk_id, source_id, text, chain_link_tag` |
| `evidence_coefficients` | `id, intervention, addresses_link, effect_metric, effect_size, effect_range, biome, source_id` |
| `geo_biome_lookup` | `region_key, lat_min, lat_max, lon_min, lon_max, typical_biome, baseline_rainfall, baseline_temp` |
| `sessions` | `session_id, created_at, variables (JSON), history (JSON)` |
| `chain_results` | `result_id, session_id, created_at, payload (JSON)` |

The vector index (`backend/store/vector_index.pkl`) holds per-chunk TF-IDF
vectors alongside `chunk_id`, `source_id`, and `chain_link_tag`, so retrieval
can be filtered to exactly the chunks tagged for a given causal-chain edge.

Both are populated by the ingestion pipeline (`backend/data/ingest.py`) from
the seed corpus in `backend/data/seed_sources.py` (16 real sources — FAO,
IPCC, peer-reviewed forest ecology literature), `evidence_coefficients.py`,
and `geo_biome.py`.

---

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/chat` | POST | Free-text turn → clarifying question or full chain result |
| `/analyze` | POST | Structured JSON input → clarifying question or full chain result |
| `/session/{id}` | GET | Retrieve session state/history |
| `/chain-evidence/{result_id}` | GET | Full per-edge and per-recommendation citation trail |
| `/health` | GET | Liveness check |

Example `/analyze` request (matches the brief's worked example):

```json
{
  "deforestation": true,
  "temperature_trend": "increasing",
  "rainfall_trend": "decreasing"
}
```

---

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python -m data.ingest          # populate SQLite + build the vector index
uvicorn app.main:app --reload  # serves on http://localhost:8000
```

Optional: copy `backend/.env.example` to `backend/.env` and set
`ANTHROPIC_API_KEY` to enable Claude-polished recommendation prose. The
system is fully functional without it — the chain, evidence, and citations
are always produced deterministically; the LLM only rewrites already-approved
text.

### Frontend

```bash
cd frontend
npm install
npm run dev   # serves on http://localhost:5173, talks to http://localhost:8000
```

Optional: copy `frontend/.env.example` to `frontend/.env` and set
`VITE_API_BASE_URL` if the backend isn't on `localhost:8000`.

### Running the two scenarios from the brief

**Primary scenario** (via curl, or paste into the chat UI):

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"deforestation": true, "temperature_trend": "increasing", "rainfall_trend": "decreasing"}'
```
→ 5-node primary chain (`trigger → water_stress → vegetation_stress → habitat_degradation → biodiversity_decline`),
every edge evidenced, recommendations mapped to `water_stress->vegetation_stress`.

**Secondary (fragmentation) scenario:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "A forest patch has been isolated by agricultural expansion. There has been no major change in rainfall or temperature."}'
```
→ routes through the secondary path (`trigger → fragmentation → habitat_degradation → biodiversity_decline`),
recommendation mapped to `fragmentation->habitat_degradation`.

**Incomplete input (clarifying question):**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Biodiversity in this area is declining."}'
```
→ returns a clarifying question instead of a chain.

---

## Tests

```bash
cd backend
pytest -v
```

18 tests across `backend/tests/`: completeness-checker gating, both chain
paths (primary/secondary/combined), resolvable-citation invariants for every
edge and recommendation, and full API scenarios including multi-turn
context carry-over. All run offline/deterministically (no API key needed).

---

## CI/CD

`.github/workflows/ci.yml` runs on every push/PR to `main`:
- **backend job:** `ruff check` + `pytest -v`
- **frontend job:** `npm run build`

Deployment configs are included but not wired to a live account (see
**Deployment** below):
- `backend/render.yaml`, `backend/Procfile` — Render / Railway
- `frontend/vercel.json` — Vercel

---

## Deployment

The app is designed to deploy in two pieces:

**Backend (Render, using `backend/render.yaml`):**
1. Push this repo to GitHub.
2. In Render, "New → Blueprint", point it at the repo — it reads `render.yaml`
   automatically (build: `pip install -r requirements.txt && python -m data.ingest`;
   start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
3. Optionally set `ANTHROPIC_API_KEY` in the Render dashboard to enable
   LLM-polished recommendation prose.

**Frontend (Vercel):**
1. Import the repo, set the root directory to `frontend/`.
2. Set the environment variable `VITE_API_BASE_URL` to the deployed backend
   URL from the step above.
3. Deploy — `vercel.json` handles the SPA rewrite.

> **Note:** this environment does not have Render/Vercel account credentials,
> so the live deploy step itself has not been executed here — only the
> configs and steps above. Local run is the documented fallback and is fully
> tested (see **Tests** above). If you'd like, share (or create) a
> Render/Vercel account and I can walk through the deploy with you, or you
> can run the two commands above yourself in a few minutes.

---

## Repository layout

```
backend/
  app/            FastAPI app, chain engine, retrieval, parser, schemas
  data/            seed corpus, evidence coefficients, geo-biome table, ingestion script
  tests/           pytest suite
frontend/
  src/             React chat UI (chain diagram + recommendation cards)
docs/              PRD, TRD, implementation-deviation notes
.github/workflows/ CI
```
