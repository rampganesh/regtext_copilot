# System Patterns — RegCopilot V1

## Architecture (target)
```
             Browser (frozen prototype UI, static regcopilot-prototype.html)
                                      │ {question, asOfDate}
                                      ▼
                 Python / FastAPI backend (Uvicorn)
   1. Input validation (Pydantic)
   2. Hybrid retrieval: pgvector dense + Postgres full-text → RRF fusion
   3. Graph expansion: edge table + recursive CTEs (≤2 hops)
   4. Status resolution: pure function, no LLM (correctness core)
   5. Synthesis: LLM fresh generation from retrieved passages (structured fields)
   6. Verbatim verification gate + HTML sanitizer (deterministic, no LLM)
   7. Conflict detection: LLM-assisted + deterministic validation (experiment)
                                      │
              ┌───────────────────────┴────────────────────────┐
   PostgreSQL 16/18 + pgvector                 LLM provider adapter
   sources · source_versions ·                 (Ollama locally; OpenRouter
   source_relationships · chunks ·             chat + embeddings endpoint)
   chunk_edges · entities · glossary)
```

## Planned directory layout (from task F1)
`backend/` with sub-packages:
`api/  ingest/  retrieval/  status/  synthesis/  conflict/  verify/  db/`

## Vertical feature slices (build order: VF0 → VF1 → VF2 → VF3 → VF4)
- **VF0 — Document & corpus foundation (priority-0, prerequisite for all).** DI-1 curated corpus
  loading (Content-Owner gated), DI-2 source metadata capture (five-status taxonomy; publication vs
  effective date), DI-3 relationships & versioning (supersession/amendment/reference), DI-4 structured
  content ingestion (tables/templates/rows/fields + definition links), DI-5 amendment intake &
  validation gate (detection ≠ activation), DI-6 version retention for audit.
- **VF1 — Core Copilot (walking skeleton):** S1.1 NL search w/ regulatory-relevance ranking; S2.1
  status badges + effective dates; S2.3 evidence-led phrasing; S3.1 verifiable prose citations; S3.3
  surrounding-context navigation. One question in → one verified, evidence-led answer out.
- **VF2 — Temporal navigation:** S2.2 as-of-date answers (current vs future vs superseded).
- **VF3 — Reporting-material connection:** S3.2 structured citations (template/table/row/field +
  definitions); S1.2 forward navigation (rule → reporting representation); S1.3 backward navigation
  (field → requirement); S1.4 related-material surfacing.
- **VF4 — Safe answers:** S4.1 conflict exposure (side-by-side, never silently resolved); S4.2
  insufficient-evidence statement; S4.3 evidence-backed escalation package (the A3 test vehicle).

**F6 (evaluation signals) was DISSOLVED** into a per-feature instrumentation task (X1): capture
time-to-answer, sources/citations used, and outcome type (answer/refusal/escalation).

## Key design patterns
- **Deterministic correctness layer separated from the generative layer.** Status resolver, verbatim
  verification gate, sanitizer, retrieval filters, and point-in-time filters are all deterministic
  (no LLM). Only synthesis and conflict-detection candidates are generative.
- **Provider adapter (ports & adapters).** `llm.py` interface: `chat(messages, json_schema) -> str`
  and `embed(texts) -> vectors`. Implementations: Ollama (local) first; OpenRouter as the documented
  alternative. Temperature-0 defaults; retry-once-on-nonconformance then loud failure.
- **Swappable graph interface.** `RelationshipGraph` with a Postgres recursive-CTE implementation
  (`chunk_edges` edge table); Neo4j-swappable. ≤2-hop expansion; `QUALIFIES` edges always included;
  point-in-time filter re-applied to every expanded node.
- **Location-based chunking (no overlap).** 1 paragraph = 1 prose chunk (>600 words split on
  sentences with sub-IDs); table chunks + per-row chunks; template-row chunks with verbatim meaning
  text; definition chunks → glossary table. Breadcrumb context prepended at *embedding time*; verbatim
  `content` stored (verification ground truth). Unique `location_id` per version.
- **Golden-file ("recorded") determinism harness for CI.** LLM-dependent assertions run against
  recorded responses; live-LLM runs are a separate manual gate. Screenshot-diff against the prototype.
- **Verbatim verification as the central gate.** Every passage/quote/conflict text checked verbatim
  (whitespace-normalized) against stored chunk content; fabricated span → drop citation or loud
  failure (never silent).

## Data model (planned tables)
- `sources` (source_key, title, doc_type, subject_area, approval_state, content_owner, approved_at)
- `source_versions` (published_date, effective_from/to, version_label, pdf_path)
- `source_relationships` (from/to version ids; type `SUPERSEDES|AMENDS|REFERENCES`; acyclicity +
  effective-date-range consistency checks)
- `chunks` (chunk_type, location_id unique-per-version, page_ref, embedding vector, verbatim content)
- `chunk_row_fields` (template_key, row_code, field_name, instruction_ref, definition_refs[])
- `chunk_edges` (from/to, node_level, edge_type, context, reference_text, extraction_method,
  confidence, review_state)
- `entities` (name, type, citing chunks) — for rerank boost + S1.4 + glossary merge candidates
- glossary table (definition term → definition chunk)

## Cross-cutting tasks (X1–X7)
- **X1** per-feature instrumentation (dissolved F6/S6.2) — each phase.
- **X2** dependency-extraction quality gate — deterministic reference pass (regex over `¶ X.Y`,
  `row NNNN`, doc IDs, Appendix/Chapter forms) + LLM implicit-reference pass; precision measured on a
  hand-labelled ~20-section sample before LLM edges are trusted.
- **X3** entity extraction (`{name, type}` → `entities` table; rerank boost + S1.4 + glossary merge).
- **X4** ingestion structural QA (unique location IDs; non-empty chunks w/ resolvable parents;
  definition_refs resolve; edges resolve or pending; supersession chains acyclic & date-consistent).
- **X5** sanitizer + verification as a shared library (single source of truth for the no-fabrication
  gate).
- **X6** five-scenario regression suite (golden-file CI + live-LLM manual gate + screenshot-diff).
- **X7** §8 checklist automation (the ten items from the prototype integration spec).

## Phase → story coverage map
| Phase | Contents |
|---|---|
| 0a | F1–F7 (scaffold, env, migrations, adapter, parsing + embedding spikes, frontend serving) |
| 0b | DI-1 … DI-6 (+ X2–X4 ingest quality tasks) |
| 1 | ST0-*, S1.1, S2.1, S2.3, S3.1, S3.3, P1-* (scenarios 1 & 4 green) |
| 2 | S2.2 (temporal coexistence; largely enabled by S21-1) |
| 3 | S3.2, S1.2, S1.3, S1.4, P3-1 (scenario 3 green) |
| 4 | S4.1–S4.3, X7 (scenarios 2 & 5 green; full checklist) |
| all | X1 instrumentation per feature |

## Invariants (global across all features)
No fabrication · five status labels only · evidence-led language · no confidence scores · analyst
remains responsible for the conclusion.


