# Task Breakdown — RegCopilot V1 User Stories (tasks & subtasks)

Companion to `2026-10-03_solution-intent-regcopilot-v1.md` and `2025-06-18_user-story-backlog-v2.md`. Stories keep their backlog IDs; tasks reflect the agreed technical decisions (Python/FastAPI, PyMuPDF, Postgres+pgvector with edge-table graph, OpenRouter adapter, frozen prototype UI, phased build VF0 → VF1 → VF2 → VF3 → VF4). Sizing is relative only (S/M/L) per PM direction — no day estimates.

---

## Foundation (Phase 0a — prerequisite for all stories)

| # | Task | Subtasks | Size |
|---|---|---|---|
| F1 | Repo scaffold & tooling | Python 3.12 project (`backend/`); uv/pip + requirements; ruff + mypy (strict); pytest; pre-commit; directory layout per plan (`api/ ingest/ retrieval/ status/ synthesis/ conflict/ verify/ db/`) | M |
| F2 | Local environment | `docker-compose.yml`: PostgreSQL 16 + pgvector extension; `.env` handling; README run instructions | S |
| F3 | DB migrations framework | Alembic setup; initial baseline migration (empty); naming/index conventions documented | S |
| F4 | Inference provider adapter | `llm.py` interface: `chat(messages, json_schema) -> str`, `embed(texts) -> vectors`; OpenRouter chat implementation; **embedding endpoint TBD by spike F6**; temperature-0 defaults; retry-once-on-nonconformance policy | M |
| F5 | PyMuPDF ingestion spike (gate for DI-4/DI-1) | Parse one real PRA prose PDF → section map extraction rate report (¶ IDs, chapter/section anchors, glossary list); reading-order QA on multi-column pages; **licensing confirmation of PyMuPDF AGPL for internal use** | M |
| F6 | Embedding model spike | Compare OpenAI text-embedding-3-small vs local BGE-class on ~20 regulatory passage pairs; pick; record dimensions in config | S |
| F7 | Static frontend serving | FastAPI serves `regcopilot-prototype.html`; CORS-free same-origin `fetch('/api/v1/ask')` wiring in `ask()` behind a demo flag | S |

---
## VF0 — Document & corpus foundation (Phase 0b unless noted)

### DI-1 — Curated corpus loading (Content-Owner gated) — parent VF0
| # | Task | Subtasks | Size |
|---|---|---|---|
| DI1-1 | Sources & versions schema | `sources` table (source_key, title, doc_type, subject_area, approval_state, content_owner, approved_at); `source_versions` (published_date, effective_from/to, version_label, pdf_path); unique constraints | M |
| DI1-2 | Ingest CLI entrypoint | `ingest <pdf> --source-key --doc-type --published --effective-from [--supersedes]`; staged workspace `corpus/<source_key>/<version>/` (`raw.json`, `chunks.json`, `edges.json`, `review.json`); idempotent re-ingest (transactional replace per version) | M |
| DI1-3 | Approval gate | `approve` CLI command flipping `approval_state='active'`; pending sources never retrievable (single query-level filter); exclusion criteria encoded as doc-type/subject checks at ingest | M |
| DI1-4 | Corpus manifest | Load the five real documents (CP16/22, PS17/23, PS9/24, PS1/26, CP9/26) + Rulebook parts + CRR007 template/instructions; metadata recorded per desk-research timeline | M |

### DI-2 — Source metadata capture — parent VF0
| # | Task | Subtasks | Size |
|---|---|---|---|
| DI2-1 | Metadata fields | publication date, effective date (distinct from publication), document type, subject area, version/status base facts stored per version | S |
| DI2-2 | Five-status vocabulary | Enum + DB check constraint limited to the five labels; mapping rules deferred to the resolver (ST-2), never inferred at ingest | S |

### DI-3 — Relationships and versioning — parent VF0
| # | Task | Subtasks | Size |
|---|---|---|---|
| DI3-1 | `source_relationships` table | from/to version ids; type `SUPERSEDES|AMENDS|REFERENCES`; acyclicity + effective-date-range consistency checks | S |
| DI3-2 | Relationship capture | Ingest flags (`--supersedes`) + front-matter boilerplate detector ("this Statement supersedes CP16/22") | S |
| DI3-3 | Template/instruction versioning | Templates and instructions ingested as first-class versions tied to their rule versions (Meeting 2 L115) | M |

### DI-4 — Structured content ingestion — parent VF0 (depends on spike F5)
| # | Task | Subtasks | Size |
|---|---|---|---|
| DI4-1 | Structure extraction | PyMuPDF pass: text items + coordinates → lines/paragraphs; strip repeated headers/footers; page → section mapping | L |
| DI4-2 | Location-ID detection | Anchors: numbered paragraphs (`SA-2.4`, `4.12`, `OF-1.2`, `ISA-3.1`), chapters/sections/appendices, template row codes (`0110`–`0130`), instruction IDs (`CRR007-INS2`), glossary term entries; build the per-document section map (resolver ground truth) | L |
| DI4-3 | Location-based chunker | 1 paragraph = 1 prose chunk (>600-word split on sentences with sub-IDs); table chunks + per-row chunks; template-row chunks with verbatim meaning text; definition chunks → glossary table; breadcrumb context prepended at embedding time; verbatim `content` stored (verification ground truth) | L |
| DI4-4 | `chunks` + `chunk_row_fields` tables | chunk_type, location_id (unique per version), page_ref, embedding vector; row fields: template_key, row_code, field_name, instruction_ref, definition_refs[] | M |
| DI4-5 | Template-row spike (gate) | Parse one CRR template PDF; row extraction rate + verbatim row-meaning capture; escalate to pdfplumber cross-check only if deficient | M |
| DI4-6 | Embedding indexer | Batch embed chunks → pgvector; full-text index on content | S |

### DI-5 — Amendment intake and validation gate — parent VF0
| # | Task | Subtasks | Size |
|---|---|---|---|
| DI5-1 | `watch` CLI (amendment detection) | Ingest new version of existing source → diff chunks by location ID (normalized string diff + embedding cosine); change report (added/changed/deleted paragraphs & rows) | M |
| DI5-2 | Candidate-update workflow states | New versions land as `pending` with diff attached; `approve`/`reject` CLI; detection output never auto-activates (staleness decision L6/L7/L12) | S |

### DI-6 — Version retention for audit — parent VF0
| # | Task | Subtasks | Size |
|---|---|---|---|
| DI6-1 | Historical version retention | All versions retained with effective-date ranges; as-of queryability of historical chunks (feeds S2.2 and future STUB-1/2/3); context preservation in staged raw outputs | M |

---
## VF1 — Core Copilot: ask, answer, verify (Phase 1)

### ST-0 — Shared retrieval infrastructure (enables S1.1; part of Phase 1)
| # | Task | Subtasks | Size |
|---|---|---|---|
| ST0-1 | Hybrid retrieval | pgvector cosine (top ~40) ∪ Postgres FTS (top ~40) → reciprocal-rank fusion; hard filters `approval_state='active'` AND `published_date ≤ asOfDate` | M |
| ST0-2 | Version dedup | If multiple versions of a source survive the as-of filter, keep the one operative at as-of; others may surface only as historical citations when the question warrants | S |
| ST0-3 | Relationship graph module | `chunk_edges` table (from/to, node_level, edge_type, context, reference_text, extraction_method, confidence, review_state) + indexes; `RelationshipGraph` interface (Postgres recursive-CTE implementation; Neo4j-swappable); ≤2-hop expansion; `QUALIFIES` edges always included; **point-in-time filter re-applied to every expanded node** | M |

### Story S1.1 — Natural-language search with regulatory-relevance ranking (Major Effort)
| # | Task | Subtasks | Size |
|---|---|---|---|
| S11-1 | Query handling | Accept free NL question (no operators); optional light LLM query rewrite for retrieval only (does not alter the echoed question) | S |
| S11-2 | Regulatory-relevance ranking | Rerank fused candidates blending term match, subject-area match, entity overlap (from ingest), and a mild authority/status prior — **ranking never selects "the applicable provision"**; none presented as such | M |
| S11-3 | Result assembly | Ranked source set with location IDs and resolved statuses, ready for citation/candidate use downstream | S |

### Story S2.1 — Status badges + effective dates on results and answers
| # | Task | Subtasks | Size |
|---|---|---|---|
| S21-1 | Status resolver (pure function, no LLM) | `(version, relationships, asOfDate) → {status, statusDate}` implementing the five-rule table; exhaustively unit-tested (rules × as-of boundaries; supersession timing; no retro-application; all five statuses derivable and nothing else) | L |
| S21-2 | Badges on results & answers | Every result and citation carries badge + statusDate; renderer contract supplies exactly the five labels | S |
| S21-3 | "Latest is not applicable" checks | Tests proving no query path surfaces a superseded source as current at any as-of date | S |

### Story S2.3 — Evidence-led answer phrasing
| # | Task | Subtasks | Size |
|---|---|---|---|
| S23-1 | Synthesis prompt & JSON output | Fresh generation from retrieved passages: opener "The relevant sources indicate…"; contrast authority levels; cite by location ID; flag divergence if present; never "the applicable requirement is…" | M |
| S23-2 | Insufficient-evidence path | When passages do not support an answer → explicit insufficient-evidence structure (pre-wire for S4.2), naming what was searched and what is missing | S |
| S23-3 | Phrasing enforcement test | Automated check: first sentence evidence-led; "applicable requirement" phrasing fails the build | S |

### Story S3.1 — Verifiable prose citations
| # | Task | Subtasks | Size |
|---|---|---|---|
| S31-1 | Citation builder | `source{id,title,type,publishedDate,status,statusDate}` + `location` chip + `passage` with `hl` (operative text) and `qual` (qualifications) spans + `definitions` keys | M |
| S31-2 | Verbatim verification gate | Every passage/quote/conflict text checked verbatim (whitespace-normalized) against chunk content; fabricated span → drop citation or loud dev failure; never silent | M |
| S31-3 | HTML sanitizer | Server-side strip of all HTML except `hl`/`qual` spans; hostile-input test cases | S |
| S31-4 | Context navigation payload | Surrounding-context data for citation expansion (the verify step, S3.3): parent section breadcrumb + adjacent paragraphs | S |

### Story S3.3 — Surrounding-context navigation from a citation
| # | Task | Subtasks | Size |
|---|---|---|---|
| S33-1 | Context endpoint/data | Context view carries the surrounding passage *with* qualifications preserved (rule 6); spot-check targets: scenario 1's 90-day/EUR 1m exception | M |
| S33-2 | Prototype wiring (frozen UI) | `toggleCit`/`toggleDef` handlers consume API data unchanged; only `ask()` edited; scenario chips deleted or demo-flagged; loading/error/empty states added minimally | S |

### Phase-1 API integration
| # | Task | Subtasks | Size |
|---|---|---|---|
| P1-1 | `POST /api/v1/ask` | Pydantic input/output schemas matching the frozen contract; as-of defaults to today; error & empty-result semantics (neutral empty state, no fabricated answer) | M |
| P1-2 | Golden-file harness | Record live LLM responses for scenarios 1 & 4; CI runs recorded mode; live-LLM run as separate manual gate | M |
| P1-3 | Scenario tests 1 & 4 green | Full assertions per acceptance spec (badges, exceptions preserved, point-in-time flip) | M |

---
## VF2 — Temporal navigation (Phase 2)

### Story S2.2 — As-of-date answers (current vs future vs superseded)
| # | Task | Subtasks | Size |
|---|---|---|---|
| S22-1 | Temporal coexistence in answers | Synthesis presents current & future-effective sources side by side when both bear on the question (e.g. PS17/23 near-final vs PS1/26 final), each with its own badge/dates | M |
| S22-2 | Difficult scenario (a): most-obvious-document-not-correct | Tests where the top-terminology match is not the operative provision at the given as-of; point-in-time filter + resolver handle it | M |
| S22-3 | Difficult scenario (b): current/future coexistence | Answer explicitly separates "what is in force" from "what takes effect later"; no merging of regimes | M |
| S22-4 | Superseded/historical handling | Historical citations carry `Superseded/Historical` + the superseder's effective date; superseder text never leaks into past as-of answers (graph-expansion invariant test) | M |
| S22-5 | Scenario 1 & 4 extended temporal assertions | Badge flips by as-of date across the whole result set, not just CP16/22 | S |

## VF3 — Reporting-material connection (Phase 3)

### Story S3.2 — Structured citations (template/table/row/field + definitions)
| # | Task | Subtasks | Size |
|---|---|---|---|
| S32-1 | Row/instruction-granularity retrieval | Retrieval over `template_row` and instruction chunks (CRR007 rows 0110/0120/0130, CRR007-INS2) across final (PS1/26) and near-final (PS9/24) versions | M |
| S32-2 | Structured citation format | `location` chips: `template CRR007, rows 0110–0130`; row meanings quoted verbatim; "blank where standardised-only" exception preserved in passage | M |
| S32-3 | Definitions population | Every `definitions` key referenced by a citation resolves to a glossary entry (build failure otherwise); inline expansion data supplied | M |

### Story S1.2 — Forward navigation: rule → reporting representation
| # | Task | Subtasks | Size |
|---|---|---|---|
| S12-1 | `REPORTS_AGAINST` edge extraction | Instruction-text patterns ("row NNNN reports…", "complete row NNNN in accordance with paragraph X") → rule-chunk ↔ row-chunk edges at ingest | M |
| S12-2 | Forward traversal | From a rule citation, follow edges to its reporting representation rows; surfaced in related context | M |

### Story S1.3 — Backward navigation: reporting field → underlying requirement
| # | Task | Subtasks | Size |
|---|---|---|---|
| S13-1 | Backward traversal | From a row/field citation, traverse inbound edges to the governing requirement(s) incl. dependent definitions (`DEFINES` edges) | M |
| S13-2 | Definition-dependency completeness | Row chunks' `definition_refs` all resolve (e.g. output floor, risk-weighted assets) | S |

### Story S1.4 — Related-material surfacing
| # | Task | Subtasks | Size |
|---|---|---|---|
| S14-1 | Related-context assembly | Graph expansion (≤2 hops) surfaces referenced/supporting/qualifying sections with roles; entity-overlap boost for related-material ranking | M |
| S14-2 | Difficult scenario (c): citation resolves to table/row/field | Tests that a prose citation resolving into template content lands on the right row with definitions attached | M |

### Phase-3 integration
| # | Task | Subtasks | Size |
|---|---|---|---|
| P3-1 | Scenario 3 green | Full acceptance assertions: row-level locations, verbatim row meanings, exception preserved, definitions populated, near-final vs final comparison | M |

## VF4 — Safe answers (Phase 4)

### Story S4.1 — Conflict exposure
| # | Task | Subtasks | Size |
|---|---|---|---|
| S41-1 | Conflict detection (LLM-assisted, experimental) | Second structured-output pass over candidate passages: "do these give materially divergent answers?" → `{headline, left, right, warning}`; left/right pulled verbatim from passages; deterministic rule candidates may be added and compared | L |
| S41-2 | Conflict object validation | Schema validation; both sides always present + warning; **never silently resolved**; escalation button data included | M |
| S41-3 | Scenario 2 test green | Side-by-side CP16/22 (`Superseded/Historical` at today) vs PS1/26 (`Future-Effective`); divergence flagged in answer text | M |
| S41-4 | Scenario 5 test green | Conflict between two `Future-Effective` sources (PS9/24 vs PS1/26) + CP9/26 `Proposed/Consultation` with "do not rely" qualification in context view; three-way authority layering | M |

### Story S4.2 — Insufficient-evidence statement
| # | Task | Subtasks | Size |
|---|---|---|---|
| S42-1 | Explicit insufficiency output | Names what was searched and what is missing; produced instead of low-support answers; outcome type recorded for instrumentation/A3 | M |
| S42-2 | Empty/neutral state | As-of date with no relevant sources → neutral empty state, no fabricated answer (checklist item) | S |

### Story S4.3 — Evidence-backed escalation package
| # | Task | Subtasks | Size |
|---|---|---|---|
| S43-1 | Escalation assembly | Bounded summary: question + evidence with citations/status + specific unresolved point (conflict headline + source ids when conflict present) | M |
| S43-2 | Escalation modal pre-fill | Frozen escalation modal consumes the package; submit flow unchanged | S |
| S43-3 | A3 instrumentation | Refusal/escalation appropriateness captured per outcome (feeds the A3 test and open question Q8) | S |

---
## Cross-cutting tasks (all phases)

| # | Task | Subtasks | Phase |
|---|---|---|---|
| X1 | Per-feature instrumentation | Capture time-to-answer, sources/citations used, outcome type (answer/refusal/escalation) for each feature's flows (dissolved F6/S6.2); feeds A3 test + Q8 | each phase |
| X2 | Dependency-extraction quality gate | Deterministic reference pass (regex over `¶ X.Y`, `row NNNN`, doc IDs, Appendix/Chapter forms) + LLM implicit-reference pass (temperature 0, JSON, validated); resolver maps targets via location index; unresolved → Content-Owner review queue (`review_state='pending'`); **precision measured on hand-labelled ~20-section sample before LLM edges trusted** | 0b |
| X3 | Entity extraction | `{name, type}` entities from the LLM pass → `entities` table (name, type, citing chunks); used for rerank boost + S1.4; glossary merge candidates | 0b |
| X4 | Ingestion structural QA | Unique location IDs; non-empty chunks with resolvable parents; definition_refs resolve; edges resolve or pending; supersession chains acyclic & date-consistent; random-chunk HTML spot-check vs PDF pages | 0b |
| X5 | Sanitizer + verification as shared library | Used by synthesis, conflict, and escalation paths; single source of truth for the no-fabrication gate | 1 |
| X6 | Five-scenario regression suite | Golden-file mode for CI; live-LLM manual gate; screenshot-diff against prototype for all five scenarios | 1→4 |
| X7 | §8 checklist automation | Automate the ten checklist items from the prototype integration spec as part of the suite | 4 |

## Deferred (explicitly out of V1 — recorded so nothing is silently dropped)

- **STUB-1** stale-answer marking — gated on Q10 (staleness window/threshold); builds on DI-5/DI-6
- **STUB-2** answer audit store — gated on data-retention/ownership/reliance decisions; builds on DI-6
- **STUB-3** impact-tracing capture — pairs with STUB-1/2; Neo4j swap candidate
- **STUB-4** newer-analyst learning path — blocked on direct newer-analyst interview
- **STUB-5** structured feedback categories — post-V1
- Auth/SSO, shared hosting, refresh SLA — revisit before any deployment beyond local dev

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

## Provenance

- Stories: `2025-06-18_user-story-backlog-v2.md` · Features: `2025-06-18_epic-feature-breakdown-v3.md` · Epic: `2025-06-18_epic-hypothesis-regcopilot-v1.md`
- Contract: `regcopilot-prototype-integration-spec.md` (frozen UI; input/output contract; §8 checklist)
- Agreed technical decisions (2026-10): Python/FastAPI + PyMuPDF; Postgres 16 + pgvector with edge-table graph & recursive CTEs (Neo4j-swappable); OpenRouter behind adapter; fresh-generation synthesis with mechanical verbatim verification; LLM-assisted conflict detection (experimental); location-based chunking; local dev only.
