# Product Requirements Document (PRD)
## Forest Restoration Intelligence — Darukaa.Earth Hackathon

**Project codename:** Forest Restoration Intelligence (FRI)
**Prepared for:** Darukaa.Earth Hackathon Challenge — Placement Track
**Document owner:** Shreyuli
**Status:** Draft v1.0

---

## 1. Overview

Instead of building a general-purpose biodiversity advisor, this project narrows scope to one high-value, well-defined problem: **reasoning about forest degradation and recommending evidence-backed restoration strategies.** A focused scope is easier to make genuinely deep (rather than shallow-but-broad), which directly serves the brief's top-weighted criterion: Depth of Reasoning (30%).

The system takes a description of a degraded forest area (deforestation, rainfall/temperature changes, optionally geo-coordinates), reasons through the causal chain from disturbance to biodiversity decline, and recommends specific, evidence-backed restoration strategies — each tied to which part of the chain it interrupts or reverses.

---

## 2. Problem Statement

Forest restoration decisions are often made on intuition ("plant trees") without reasoning about *why* a forest is degrading or *which* intervention addresses the actual mechanism of decline. A forest losing biodiversity because of water stress (rainfall decline + temperature rise) needs a different intervention than one degrading primarily from fragmentation. There's no accessible tool that:
- Traces the causal mechanism from disturbance → biodiversity decline for a specific site
- Matches restoration strategies to the specific broken link in that chain
- Backs each strategy with quantified, cited evidence

---

## 3. Goals & Objectives

| Goal | Why it matters for scoring |
|---|---|
| Model the full causal chain: deforestation + temperature increase + reduced rainfall → water stress → vegetation stress → habitat degradation → biodiversity decline | Depth of Reasoning (30%), Multi-Metric Reasoning ("core differentiator") |
| Ground every restoration strategy in retrievable evidence | Scientific Grounding (25%) |
| Real RAG/vector retrieval over a curated forest-restoration evidence base | Knowledge System Design (20%) |
| Ask clarifying questions when inputs (deforestation extent, rainfall/temp change, region) are incomplete | Conversational Intelligence (15%) |
| Structured, consistent output per recommendation | Output Clarity (10%) |

---

## 4. Target Users

1. **Forest restoration NGOs / project designers** — need a specific, defensible intervention plan for a degraded site, backed by evidence they can show funders.
2. **Conservation / land-use planners** — need to understand which mechanism (water stress vs. fragmentation vs. soil loss) is driving decline on a given site before committing budget.
3. **Researchers / students** — want a tool that reasons transparently rather than giving generic advice.

---

## 5. Key Features

### 5.1 Knowledge System (Critical)
- Curated knowledge base focused on forest ecology and restoration: soil health under forest cover, canopy/water cycle interactions, temperature/rainfall effects on vegetation stress, habitat fragmentation, and species richness/habitat diversity in forest biomes.
- RAG over indexed sources: FAO forest restoration guidance, IPCC land-use/forest chapters, peer-reviewed forest ecology and reforestation studies.
- Every response shows its retrieval trail (source + snippet reference), so grounding is inspectable, not just claimed.

### 5.2 Conversational Intelligence
- Multi-turn memory: retains previously stated forest condition (deforestation extent, rainfall trend, temperature trend, region/biome) across a session.
- Clarifying questions when a required input for the causal chain is missing — e.g., if only "deforestation" is mentioned with no rainfall/temperature signal, the system asks before reasoning further.
- Follow-ups refine the existing analysis rather than restarting it (e.g., "what if we only address water stress and not fragmentation?").

### 5.3 Evidence-Backed Restoration Recommendations (Mandatory)
Each recommendation includes:
1. **What to do** (specific restoration action, e.g., "assisted natural regeneration with native pioneer species")
2. **Why it works** (mechanism — which link in the causal chain it addresses)
3. **Which metric improves, and by how much** (quantified where evidence supports it)
4. **Source** (study/report cited)

### 5.4 Multi-Metric Causal Reasoning (the core of this project)
The system must always construct and display the causal chain before recommending, e.g.:

```
Deforestation
      +
Temperature increase
      +
Reduced rainfall
      ↓
Water stress
      ↓
Vegetation stress
      ↓
Habitat degradation
      ↓
Biodiversity decline
```

- Each arrow in the chain is a claim that must be backed by retrieved evidence (not just asserted by the LLM).
- Recommendations are explicitly mapped to which link(s) in the chain they interrupt (e.g., "assisted regeneration → restores canopy cover → reduces water stress → breaks the vegetation-stress link").
- Minimum requirement carried over from the brief: reasoning must connect ≥3 environmental variables (here: deforestation extent, temperature trend, rainfall trend, at minimum).

### 5.5 Input Handling
- **Text (mandatory):** free-form description, e.g., "A forest area has experienced deforestation. Rainfall has decreased and average temperature has increased."
- **Structured input (mandatory):** JSON with deforestation extent/%, rainfall trend, temperature trend, region/biome.
- **Geo-coordinates (bonus, confirmed in scope):** optional lat/long used to pull regional climate/forest-biome priors (e.g., typical rainfall baseline, forest type) and to contextualize the causal chain and restoration strategy to the actual site instead of generic defaults.

### 5.6 Output Quality
Every response follows a fixed structure:
- Causal chain (the disturbance → decline pathway for this specific input)
- Recommendation(s), each with: what to do / why it works / impacted metric(s) / time horizon (short/medium/long) / confidence level
- Sources

---

## 6. Primary Demo Scenario (from the brief, used as the flagship example)

**Input (text):**
> "A forest area has experienced deforestation. Rainfall has decreased and average temperature has increased."

**System behavior:**
1. Extracts structured variables: deforestation = present, rainfall trend = decreasing, temperature trend = increasing.
2. Checks completeness — region/biome not specified, so either asks a clarifying question ("Which region or forest type is this?") or, if geo-coordinates are supplied, infers biome from location instead of asking.
3. Constructs the causal chain: deforestation + temperature increase + reduced rainfall → water stress → vegetation stress → habitat degradation → biodiversity decline.
4. Retrieves restoration evidence matched to breaking the water-stress/vegetation-stress link (e.g., assisted natural regeneration, native species reintroduction, canopy-cover restoration, water-retention measures).
5. Outputs restoration strategies, each tied explicitly to which link in the chain it addresses, quantified impact where evidence supports it, time horizon, confidence, and citations.

**Secondary scenario (to prove generality within the forest domain):** a fragmentation-driven case (e.g., forest patch isolated by agricultural expansion, no major rainfall/temperature change) — proves the system doesn't just pattern-match one chain, it reasons from the actual inputs given.

---

## 7. Success Metrics

| Criterion | Weight | Internal acceptance bar |
|---|---|---|
| Depth of Reasoning | 30% | Causal chain is always shown, always ≥3 linked variables, and recommendations are explicitly mapped to a specific link in the chain |
| Scientific Grounding | 25% | 100% of chain-links and recommendations carry a real citation from the indexed corpus |
| Knowledge System Design | 20% | RAG retrieval trace is inspectable in the demo/README, not just claimed |
| Conversational Intelligence | 15% | System correctly asks a clarifying question when region/biome or a chain-relevant variable is missing, demonstrated in at least one recorded demo turn |
| Output Clarity | 10% | 100% of responses include causal chain + all 4 recommendation fields |

---

## 8. Scope & Non-Goals

**In scope:**
- Forest degradation → restoration reasoning only (not a general biodiversity advisor across all land types)
- Text + structured JSON input; geo-coordinates as a working bonus feature (confirmed in scope per your note)
- Curated seed corpus (10–15 sources) specific to forest restoration ecology
- One primary demo scenario (matches the brief's worked example) + one secondary scenario (fragmentation case)

**Out of scope:**
- Agricultural/cropland recommendations (e.g., cover crops, monoculture-to-intercropping advice) — that's the general-advisor scope we deliberately dropped
- Live satellite/remote-sensing ingestion — geo-coordinates map to static regional reference data (climate zone, forest biome type), not real-time imagery
- Multi-tenant auth, production-grade accounts

---

## 9. Submission Checklist (per Darukaa's guidelines)

- [ ] GitHub repository link (public, or private with access granted to: ankita.dasgupta@darukaa.com, harsh.kumar@darukaa.com, utkarsh.gauniyal@darukaa.com, guneet.mutreja@darukaa.com)
- [ ] Live demo URL (where applicable)
- [ ] README.md covering architecture, database/schema, local setup, CI/CD
- [ ] Any additional credentials/notes needed to run the project
- [ ] All of the above compiled into **one Word (.docx) document** and submitted via the My Jobs / Applied Job page

---

## 10. Suggested Timeline

| Phase | Focus |
|---|---|
| Day 1 | Curate forest-restoration evidence corpus + ingestion pipeline + vector DB |
| Day 2 | Causal-chain reasoning engine (the deforestation→biodiversity-decline graph) + structured output schema |
| Day 3 | Conversational layer (memory, clarifying questions) + text/JSON/geo input handling |
| Day 4 | Polish primary + secondary demo scenarios, README + architecture doc, deploy |
| Day 5 (buffer) | Self-test against evaluation rubric, assemble submission doc |
