# Task Breakdown — RegCopilot V1 User Stories — v2 (every task under its story)

Supersedes `2026-10-03_user-story-tasks-regcopilot-v1.md` (retained unchanged for audit). Companion
to `2026-10-03_solution-intent-regcopilot-v1.md` and `2025-06-18_user-story-backlog-v2.md`.

**What changed from v1:** (a) every project-setup task (`F1`–`F7`), shared-retrieval task (`ST0-*`),
cross-cutting task (`X1`–`X7`) and phase-integration task (`P1-*`, `P3-*`) has been **moved under the
story that owns it** — there are no orphan tasks any more; (b) the cross-cutting tasks are now part of
the VF0 story subtasks they belong to (reference resolution, entity extraction, ingestion checks);
(c) three gaps found in review are now closed — intra-document reference scoping and range expansion,
`CONTINUES`/`DEPENDS_ON` edge extraction, and a recall (coverage) measure for reference resolution;
(d) tasks are rewritten in simple language, with every abbreviation expanded on first use; (e) every
task is written to be **SMART**; (f) each task links to a test in
`2026-10-06_user-story-tasks-regcopilot-v2-tests.md` by task ID (for example, task `DI3-4` is tested
by spec `DI3-4`).

Parent epic: `2025-06-18_epic-hypothesis-regcopilot-v1.md` · Features:
`2025-06-18_epic-feature-breakdown-v3.md` · Stories: `2025-06-18_user-story-backlog-v2.md`.

---

## How to read this document

**SMART note.** Every task is **Specific** (one clear outcome), **Measurable** (an explicit
"done when" condition), **Achievable** (small enough to finish), and **Relevant** (it serves the
named story and feature). **Time-bound is intentionally not applied** (per project management
direction — no day estimates). Instead each task carries a relative **Size**: **S** (small),
**M** (medium), **L** (large). Sizes are relative to sibling tasks only.

**Task ID convention.** `<story-or-area><sequence>` — for example `DI1-1`, `S31-2`, `S12-1`. Where a
task came from v1 it keeps a note of its old ID (for example "was F5") so reviews can trace the move.

**Every task sits under its story.** The sections below are the stories in build order
(`VF0 → VF1 → VF2 → VF3 → VF4`). Each story lists its tasks and subtasks. There is a traceability
matrix at the end mapping every task to its story, feature and epic sub-hypothesis.

**Test link.** Each task row ends with the test ID in the companion test specification. The test ID
equals the task ID (one or more named tests per task).

**Abbreviations expanded on first use:** Retrieval-Augmented Generation (RAG); natural-language (NL);
full-text search (FTS); reciprocal-rank fusion (RRF); common table expression (CTE); large language
model (LLM); subject-matter expert (SME); Product Manager (PM); Capital Requirements Regulation (CRR,
the United Kingdom on-shored version of the European Union regulation); Prudential Regulation
Authority (PRA); Financial Services and Markets Act 2000 (FSMA); single sign-on (SSO); Structured
Query Language (SQL); Portable Document Format (PDF); Application Programming Interface (API);
HyperText Markup Language (HTML); JavaScript Object Notation (JSON); Continuous Integration (CI).

---

## VF0 — Document & corpus foundation (priority-0; prerequisite for all features)

Ownership split per the bounded-corpus decision: the Regulatory Content Owner governs inclusion,
status and relationships; Technology owns ingestion and indexing.

### DI-1 — Curated corpus loading (Content-Owner gated)

Story: load only approved UK capital/Basel 3.1 material into the corpus, so every answer draws only
from authoritative, approved sources.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| DI1-1 | Project scaffold and tooling | A Python 3.12 project exists (`backend/`); dependencies install on a clean machine; linting, type checking, testing and pre-commit hooks run green. **Done when:** linting, strict type checking and the test runner all pass on an empty project and the folders `api/ ingest/ retrieval/ status/ synthesis/ conflict/ verify/ db/` exist. (was F1) | Create project; add dependency file; add linter and type checker; add test runner; add pre-commit; create package folders | M | DI1-1 |
| DI1-2 | Local environment and database | The project runs locally against a PostgreSQL 16+ server with the **pgvector** extension enabled. **Done when:** configuration is read from a `.env` file and a fresh developer can follow the README to reach a running database with the `vector` extension available. (was F2) | Document PostgreSQL 16+ and pgvector setup (no Docker on this machine); add `.env` template and loader; write README run steps | S | DI1-2 |
| DI1-3 | Database migration framework | Schema changes are applied through versioned migrations, not manual SQL. **Done when:** one baseline migration applies and rolls back cleanly and naming/index conventions are written down. (was F3) | Add migration tool; create baseline migration; document naming and index conventions | S | DI1-3 |
| DI1-4 | Sources and versions database tables | Two tables exist: `sources` (source_key, title, document type, subject area, approval state, content owner, approved-at) and `source_versions` (published date, effective-from, effective-to, version label, stored file path). **Done when:** a version cannot duplicate another version of the same source and all dates are stored as plain dates. | Create both tables; add unique constraints and indexes | M | DI1-4 |
| DI1-5 | Ingest command-line entry point | One command loads a PDF into a staged workspace and writes intermediate files. **Done when:** `ingest <pdf> --source-key --doc-type --published --effective-from [--supersedes]` creates `corpus/<source_key>/<version>/raw.json`, `chunks.json`, `edges.json`, `review.json`, and re-running the same command replaces that version in a single transaction without duplicates. | Build command-line parser; write staged workspace; make re-ingest idempotent | M | DI1-5 |
| DI1-6 | Content-Owner approval gate | Nothing joins the active corpus without explicit approval. **Done when:** an `approve` command sets `approval_state='active'`; a single query-time filter guarantees unapproved sources are never retrieved; inclusion/exclusion rules are enforced at ingest by document type and subject area. | Add `approve` command; implement active-only filter; encode inclusion/exclusion at ingest | M | DI1-6 |
| DI1-7 | Real corpus manifest | The real Basel 3.1 documents are loaded with correct metadata. **Done when:** CP16/22, PS17/23, PS9/24, PS1/26 and CP9/26, the relevant PRA Rulebook parts, and the CRR007 reporting template and instructions are present with correct published and effective dates per the desk-research timeline. | Collect documents; record metadata; load and approve | M | DI1-7 |
| DI1-8 | Inference provider adapter | One interface wraps all language-model and embedding calls, so the provider can be swapped. **Done when:** an adapter exposes `chat(messages, json_schema) -> str` and `embed(texts) -> vectors`; a local provider (Ollama) implementation and an alternative provider implementation both satisfy the interface; temperature defaults to 0; and a non-conforming model output is retried once before a loud failure. (was F4) | Define the adapter interface; implement the local provider first; keep the alternative provider swappable; set temperature 0 and retry-once behaviour | M | DI1-8 |

### DI-2 — Source metadata capture

Story: store every source with publication date, effective date, document type, subject area and
version/status, so every result and citation can show its status badge and dates without guessing.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| DI2-1 | Metadata fields captured per version | Publication date, effective date (kept clearly distinct from publication), document type, subject area and version/status base facts are stored for every version. **Done when:** a sample document shows publication and effective dates that differ and "latest" can never be derived as "applicable". | Add metadata columns; validate at ingest; test that publication and effective dates are independent | S | DI2-1 |
| DI2-2 | The five-status vocabulary | A fixed list of exactly five status labels is enforced by the database. **Done when:** `final/operative`, `future-effective`, `superseded/historical`, `proposed/consultation`, `explanatory/supporting` exist as an enum with a check constraint, and status is never chosen at ingest (that is the status resolver, task S21-1). | Define enum and check constraint; confirm ingest stores base facts only | S | DI2-2 |

### DI-3 — Relationships and versioning

Story: record supersession, amendment and reference relationships between sources, with templates and
instructions versioned alongside their rules, so "which version applies when" is queryable.

This story also owns the **cross-cutting concern of dependency/reference extraction** (the intra-
document cross-links — appendix, section, paragraph, article and table references). Tasks DI3-4 to
DI3-8 below close gaps found in review: distinguishing a bare reference from a Part/Chapter-qualified
one, expanding ranges, capturing continuation and dependence links, and measuring how much reference
coverage is achieved.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| DI3-1 | Cross-source relationship table | A `source_relationships` table records from-version, to-version and relationship type (`SUPERSEDES` / `AMENDS` / `REFERENCES`). **Done when:** the chain of supersessions is proven acyclic and consistent with the effective-date ranges. | Create table; add type constraint; add acyclicity and date-consistency check | S | DI3-1 |
| DI3-2 | Relationship capture at ingest | Relationships are recorded from the ingest command flag and from front-matter wording. **Done when:** `--supersedes` records a link and a boilerplate detector recognises wording such as "this Statement supersedes CP16/22". | Read the flag; add the boilerplate detector | S | DI3-2 |
| DI3-3 | Template and instruction versioning | Templates and instructions are ingested as first-class versions tied to the rule versions they belong to. **Done when:** a CRR007 template version is linked to the specific rule version it accompanies, so a current rule can never be shown with an outdated instruction. | Ingest templates/instructions as versions; link to rule versions | M | DI3-3 |
| DI3-4 | Intra-document reference extraction (explicit patterns) | Explicit, patterned intra-document references are found and resolved to a target chunk. **Done when:** a rule pass recognises paragraph forms (`¶ X.Y`, `4.12`, `SA-2.4`, `ISA-3.1`), table-row forms (`row NNNN`), document IDs, and Appendix/Chapter/Section forms, and each match resolves to a chunk via the location index (built in DI4-2). (was X2, part 1) | Write the pattern set; resolve each match against the location index; record edges of type `REFERENCES` | M | DI3-4 |
| DI3-5 | Reference scoping disambiguation | A bare reference is correctly resolved using its surrounding Part/Chapter scope. **Done when:** "Article 105" inside Trading Book (CRR) Part resolves to that Part's Article 105, while a bare "Article 108" resolves to the correct default scope; the scope in force at the citing chunk is used. (new — closes review gap 1) | Detect Part/Chapter context; carry scope into resolution; test qualified vs bare references | M | DI3-5 |
| DI3-6 | Reference range expansion | References expressed as a range become one edge per target. **Done when:** "Articles 192 to 239" produces an edge to each article in the range and "Sections 3 to 5 of Chapter 3" produces one edge per section; range endpoints are inclusive. (new — closes review gap 1) | Parse range expressions; expand to individual targets; cap unreasonable ranges | M | DI3-6 |
| DI3-7 | Continuation and dependence links | Two further link types are extracted: `CONTINUES` (a paragraph or table cell continued across a page or column break) and `DEPENDS_ON` (a chunk whose meaning needs another chunk). **Done when:** a paragraph split across a two-column table or page break becomes one logical chunk via a `CONTINUES` link, and a `DEPENDS_ON` link is created where a chunk refers to another for its meaning. (new — closes review gap 3) | Detect continuation across page/column breaks; detect dependence links; store both edge types | M | DI3-7 |
| DI3-8 | Implicit-reference pass and coverage measure | An LLM pass (temperature 0, JSON output, validated) finds references the pattern pass misses; the fraction of references found (recall/coverage) and the fraction that are correct (precision) are both measured. **Done when:** precision is measured on a hand-labelled ~20-section sample before LLM edges are trusted, **and** a coverage figure (references found divided by references expected) is reported for that sample. (was X2, part 2; recall added — closes review gap 2) | Run the LLM pass; validate output; compute precision and coverage on the sample | M | DI3-8 |
| DI3-9 | Unresolved-reference review queue | References that cannot be resolved are queued, never dropped. **Done when:** an unresolved reference is written to the review queue with `review_state='pending'` and appears in `review.json`; at query time, graph expansion treats a pending endpoint as unavailable context and never blocks the answer. (was X2, part 3; query-time behaviour added — closes review gap 2) | Write unresolved targets to the queue; define query-time handling of pending endpoints | S | DI3-9 |

### DI-4 — Structured content ingestion

Story: ingest tables, templates, rows/fields and instructions as structured, addressable content
including links to dependent definitions, so a citation can point at an exact row or field.

This story owns the **parsing and embedding spikes** (was F5 and F6), the **entity-extraction**
cross-cutting task (was X3) and the **ingestion structural checks** (was X4).

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| DI4-1 | PDF parsing spike (gate) | One real PRA prose PDF is parsed and the quality is measured before the parser is trusted. **Done when:** a report states the section-map extraction rate (paragraph IDs, chapter/section anchors, glossary entries) and reading order is checked on multi-column pages; the PyMuPDF AGPL licence is confirmed for internal use. (was F5) | Parse a real PDF; produce the extraction-rate report; check multi-column reading order; confirm licence | M | DI4-1 |
| DI4-2 | Embedding model spike (gate) | An embedding model is chosen and recorded before indexing. **Done when:** a short report compares the local BGE-class model with an online alternative on about 20 regulatory passage pairs, a choice is recorded, and the vector dimension is stored in configuration. (was F6) | Run the comparison; pick a model; record the dimension in config | S | DI4-2 |
| DI4-3 | Structure extraction | A parsing pass turns the PDF into ordered text with coordinates and a page-to-section map. **Done when:** text items and coordinates become lines and paragraphs, repeated headers/footers are removed, and each page is mapped to its section. (was DI4-1) | Extract text items with coordinates; build lines/paragraphs; strip headers/footers; build the page-to-section map | L | DI4-3 |
| DI4-4 | Location-ID detection | Every addressable location gets a stable identifier, forming the per-document section map used by the reference resolver. **Done when:** numbered paragraphs (`SA-2.4`, `4.12`, `OF-1.2`, `ISA-3.1`), chapters/sections/appendices, template row codes (`0110`–`0130`), instruction IDs (`CRR007-INS2`) and glossary term entries all receive a unique location ID per version. (was DI4-2) | Detect each anchor type; build the section map; assign unique location IDs | L | DI4-4 |
| DI4-5 | Paragraph chunker | Each numbered paragraph becomes exactly one chunk (no overlap), with breadcrumb context added for embedding. **Done when:** a paragraph over 600 words is split on sentence boundaries with sub-IDs, the verbatim `content` is stored as the verification ground truth, and no chunk is empty. (split from was DI4-3) | One paragraph to one chunk; split long paragraphs with sub-IDs; prepend breadcrumb for embedding; store verbatim content | L | DI4-5 |
| DI4-6 | Table, template-row and glossary chunkers | Tables, template rows and definitions each become addressable chunks. **Done when:** table chunks plus per-row chunks exist, template-row chunks carry the verbatim row meaning, and definition chunks are collected into a glossary table. (split from was DI4-3) | Table chunker; template-row chunker with verbatim meaning; definition-to-glossary chunker | L | DI4-6 |
| DI4-7 | Chunks and row-fields tables | Two tables exist: `chunks` (chunk type, location ID unique per version, page reference, embedding vector, verbatim content) and `chunk_row_fields` (template key, row code, field name, instruction reference, definition references). **Done when:** the unique-per-version location constraint holds and the embedding column uses the pgvector type. (was DI4-4) | Create `chunks`; create `chunk_row_fields`; add constraints and indexes | M | DI4-7 |
| DI4-8 | Template-row spike (gate) | One real reporting template is parsed and row quality is measured before template ingestion is trusted. **Done when:** a report states the row extraction rate and confirms verbatim row-meaning capture; a cross-check with a second parser is only added if the rate is too low. (was DI4-5) | Parse one CRR template; measure row extraction; confirm verbatim meanings; decide on cross-check | M | DI4-8 |
| DI4-9 | Entity extraction | Named entities are extracted to support ranking, related-material and glossary merging. **Done when:** the LLM pass produces entities as `{name, type}` pairs written to an `entities` table (name, type, citing chunk). (was X3) | Run the entity pass; write to `entities`; expose for later ranking use | M | DI4-9 |
| DI4-10 | Embedding indexer | Every chunk is embedded and searchable. **Done when:** chunks are embedded in batches into the pgvector column and a full-text index exists on the chunk content. (was DI4-6) | Batch-embed chunks; write vectors; create the full-text index | S | DI4-10 |
| DI4-11 | Ingestion structural checks | Ingestion is proven structurally sound before any chunk is retrievable. **Done when:** all location IDs are unique, every chunk is non-empty with a resolvable parent, every definition reference resolves, every reference edge resolves or sits in the review queue, supersession chains are acyclic and date-consistent, and a random-chunk HTML render is spot-checked against the PDF page. (was X4) | Run each check; fail ingestion loudly on any violation; spot-check rendering | M | DI4-11 |

### DI-5 — Amendment intake and validation gate

Story: detect and flag new or changed material, then let the Content Owner validate authority,
status, effective date and relationships before anything is activated.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| DI5-1 | Amendment detection command | A command compares a new version of an existing source with the current one and reports the differences. **Done when:** it diffs chunks by location ID using a normalised text difference plus embedding similarity, and produces a change report of added, changed and deleted paragraphs and rows. | Build the diff command; normalise text; add embedding similarity; produce the change report | M | DI5-1 |
| DI5-2 | Candidate-update workflow states | New versions wait for approval and never auto-activate. **Done when:** a detected version lands as `pending` with its diff attached, `approve`/`reject` commands move it out of `pending`, and no detection output can become active on its own. | Add `pending` state with diff; add approve/reject commands; prove no auto-activation | S | DI5-2 |

### DI-6 — Version retention for audit

Story: retain historical source versions with their effective-date ranges, so an answer could later be
checked against the material current at the time.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| DI6-1 | Historical version retention | Every version is kept and stays queryable by date. **Done when:** all versions are retained with effective-date ranges, historical chunks can be queried as-of a past date (feeding story S2.2 and future work), and original staged context is preserved. | Retain all versions with date ranges; add as-of queryability; preserve raw context | M | DI6-1 |

---

## VF1 — Core Copilot: ask, answer, verify (Phase 1)

### S1.1 — Natural-language search with regulatory-relevance ranking (Major Effort)

Story: ask a question in normal language and receive genuinely relevant authoritative sources, ranked
by regulatory relevance rather than similarity alone.

This story owns the **shared retrieval infrastructure** (was ST-0) and the **relevance-ranking spike**
(the backlog's "Spike F1-TAD").

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S11-1 | Query handling | A free natural-language question (no operators) is accepted and prepared for retrieval. **Done when:** the question is trimmed, an optional light query rewrite for retrieval is applied, and no search operators are required from the analyst. | Accept the question; add the optional rewrite; keep the original for display | S | S11-1 |
| S11-2 | Hybrid retrieval | Relevant chunks are found by combining semantic and keyword search. **Done when:** pgvector cosine similarity (top ~40) is combined with PostgreSQL full-text search (top ~40) using reciprocal-rank fusion, with hard filters `approval_state='active'` and `published_date ≤ as-of date`. (was ST0-1) | Run both searches; fuse with reciprocal-rank fusion; apply the two hard filters | M | S11-2 |
| S11-3 | Version de-duplication | Only the version in force at the as-of date is used by default. **Done when:** if several versions of a source survive the filter, the one operative at the as-of date is kept, and others surface only as historical citations when the question needs them. (was ST0-2) | Detect multiple versions; keep the operative one; allow historical surfacing | S | S11-3 |
| S11-4 | Relationship graph module | Cross-references can be followed to gather related chunks. **Done when:** a `chunk_edges` table (from/to, node level, edge type, context, reference text, extraction method, confidence, review state) exists with indexes; a `RelationshipGraph` interface with a PostgreSQL recursive-CTE implementation (and a stated path to swap in another graph store) expands up to 2 hops; `QUALIFIES` edges are always included; and the point-in-time filter is re-applied to every expanded node. (was ST0-3) | Build the edge table and indexes; implement the interface with recursive common table expressions; re-apply the as-of filter on each hop | M | S11-4 |
| S11-5 | Regulatory-relevance ranking | Results are ranked by regulatory relevance, not similarity alone. **Done when:** ranking blends term match, subject-area match, entity overlap and a mild authority/status prior, and **no result is ever presented as "the applicable provision"**. | Add the ranking signals; combine them; assert the no-applicable-provision rule | M | S11-5 |
| S11-6 | Relevance-ranking spike (learning task) | The team learns whether ranking can separate "looks similar" from "is applicable" before finalising acceptance. **Done when:** the spike is evaluated against the difficult-case set and its findings feed Open Question Q8. (was Spike F1-TAD) | Run the evaluation; record findings; link to Q8 | S | S11-6 |
| S11-7 | Result assembly | The ranked result set is ready for citation use. **Done when:** the ranked sources carry location IDs and resolved statuses for downstream steps. (was S11-3 v1) | Attach locations and statuses to each result | S | S11-7 |

### S2.1 — Status label and effective date on every result and answer

Story: see the source status and effective date on every search result and answer, so an analyst can
tell at a glance whether material is operative without checking the document by hand.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S21-1 | Status resolver (pure function, no LLM) | A plain function returns the status and its status date from the version, its relationships and the as-of date. **Done when:** it implements the five-rule table, is exhaustively unit-tested across rules and as-of boundaries (supersession timing, no retro-application, all five statuses derivable and nothing else), and uses no language model. (was S21-1; the resolver referenced as "ST-2" in DI2-2 is this task) | Implement the five-rule table; add boundary tests; confirm no LLM use | L | S21-1 |
| S21-2 | Badges on results and answers | Every result and citation carries a badge and a status date. **Done when:** the renderer contract supplies exactly the five labels and every item shows both a badge and a date. (was S21-2) | Attach badge and date to each result/citation; enforce the five-label set | S | S21-2 |
| S21-3 | "Latest is not applicable" checks | No query path ever shows a superseded source as current. **Done when:** tests prove that, at any as-of date, a superseded source is never surfaced as the current one. (was S21-3) | Write the proof tests across as-of dates | S | S21-3 |

### S2.3 — Evidence-led answer language

Story: answers are phrased as "The relevant sources indicate…" with source status visible, and never
as "The applicable requirement is…".

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S23-1 | Synthesis prompt and JSON output | An answer is freshly generated from retrieved passages in a fixed shape. **Done when:** the opening line is "The relevant sources indicate…", authority levels are contrasted, citations are by location ID, divergence is flagged if present, and the phrase "the applicable requirement is…" never appears. (was S23-1) | Write the prompt; enforce the JSON shape; add the required opening and forbidden phrase | M | S23-1 |
| S23-2 | Insufficient-evidence path | When the passages do not support an answer, the system says so. **Done when:** an explicit insufficient-evidence structure is returned, naming what was searched and what is missing (pre-wiring story S4.2). (was S23-2) | Add the insufficient-evidence structure; name searched sources and gaps | S | S23-2 |
| S23-3 | Phrasing enforcement test | The required phrasing is checked automatically. **Done when:** an automated test fails the build if the first sentence is not evidence-led or the forbidden phrase appears. (was S23-3) | Write the automated phrasing test | S | S23-3 |

### S3.1 — Verifiable citation for textual requirements

Story: every claim drawn from textual material carries a citation pointing to the exact section or
paragraph, with surrounding context preserved, so it can be verified in seconds.

This story owns the **shared sanitizer and verbatim verifier** cross-cutting task (was X5) — the
single source of truth for the no-fabrication gate.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S31-1 | Citation builder | A citation object is assembled with the source facts, a location chip, a passage with highlight and qualification spans, and its definition keys. **Done when:** the object matches the frozen contract: `source{id,title,type,publishedDate,status,statusDate}`, a `location` chip, a `passage` with `hl` (operative text) and `qual` (qualifications), and `definitions` keys. (was S31-1) | Build the object; add highlight and qualification spans; attach definition keys | M | S31-1 |
| S31-2 | Verbatim verification gate (shared library) | Every quoted span is proven to exist in the source before it is returned. **Done when:** each passage, quote and conflict text is checked verbatim (whitespace-normalised) against stored chunk content, and a fabricated span either drops the citation or fails loudly in development — never silently. Shared by the synthesis, conflict and escalation paths as one library. (was S31-2 + X5) | Build the verifier library; run it on every path; define drop-or-fail behaviour | M | S31-2 |
| S31-3 | HTML sanitizer | Only safe inline tags survive. **Done when:** all HTML is stripped except `hl` and `qual` spans, and hostile-input cases are tested. (was S31-3) | Build the sanitizer; add hostile-input tests | S | S31-3 |
| S31-4 | Context navigation payload | The data needed to expand a citation is supplied. **Done when:** the payload carries the parent section breadcrumb and adjacent paragraphs for the verify step (story S3.3). (was S31-4) | Build breadcrumb and adjacent-paragraph payload | S | S31-4 |

### S3.3 — Surrounding-context navigation from a citation

Story: expand from a cited provision to its surrounding passage or table context, so qualifications
and exceptions can be checked without re-searching.

This story owns the **static frontend serving** task (was F7) and the **API integration** tasks
(was P1-1, P1-2, P1-3).

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S33-1 | Context view with qualifications preserved | The context view shows the surrounding passage including its qualifications. **Done when:** the surrounding passage is returned with qualifications preserved (product rule 6) and the scenario-1 exception (the 90-day / EUR 1m case) is a verified spot-check target. (was S33-1) | Return the surrounding passage; preserve qualifications; verify the scenario-1 exception | M | S33-1 |
| S33-2 | Prototype wiring (frozen UI) | The frozen prototype consumes the real API without UI redesign. **Done when:** the frozen page is served by the backend, the `ask()` function calls the real endpoint on the same origin (no cross-origin setup), the expand/definition handlers consume API data unchanged, scenario chips are deleted or demo-flagged, and loading/error/empty states are added minimally. (was S33-2 + F7) | Serve the prototype; wire `ask()` to the endpoint behind a demo flag; add minimal loading/error/empty states | S | S33-2 |
| S33-3 | Ask endpoint | A single endpoint accepts the question and as-of date and returns the frozen contract. **Done when:** `POST /api/v1/ask` validates its input and output with the schema models, defaults the as-of date to today, and returns defined error and empty-result behaviour (a neutral empty state, no fabricated answer). (was P1-1) | Define request/response schemas; default the as-of date; define error and empty behaviour | M | S33-3 |
| S33-4 | Recorded-response test harness | CI runs deterministically without calling the live model. **Done when:** live model responses for scenarios 1 and 4 are recorded, CI runs in recorded mode, and a live run is a separate manual gate. (was P1-2) | Record responses; add recorded-mode run; add the manual live gate | M | S33-4 |
| S33-5 | Scenario tests 1 and 4 green | The first two acceptance scenarios pass end to end. **Done when:** scenario 1 (prose citation with exception) and scenario 4 (point-in-time flip of CP16/22) pass all assertions — correct badges, exceptions preserved, point-in-time flip. (was P1-3) | Write scenario tests 1 and 4; assert badges, exceptions and the flip | M | S33-5 |

---

## VF2 — Temporal navigation (Phase 2)

### S2.2 — As-of-date answers (current vs future vs superseded)

Story: ask a question relative to a specified date, so the answer reflects the requirement in force at
that date, not merely the newest publication.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S22-1 | Temporal coexistence in answers | When both a current and a future-effective source bear on a question, both are shown. **Done when:** the answer presents them side by side (for example PS17/23 near-final and PS1/26 final), each with its own badge and dates. | Present current and future sources side by side; attach each badge and dates | M | S22-1 |
| S22-2 | Difficult case (a): most-obvious document not correct | The answer is correct even when the top terminology match is not the operative provision. **Done when:** a test proves the point-in-time filter and the status resolver handle a case where the obvious document is wrong at the given as-of date. | Write the difficult-case test; verify filter and resolver behaviour | M | S22-2 |
| S22-3 | Difficult case (b): current/future coexistence | The answer clearly separates what is in force from what takes effect later. **Done when:** a test proves "in force now" and "takes effect later" are never merged into one regime. | Write the coexistence test; prove no regime merging | M | S22-3 |
| S22-4 | Superseded/historical handling | Historical citations are labelled correctly and later text never leaks backwards. **Done when:** a historical citation carries `superseded/historical` plus the superseder's effective date, and a test proves the superseder's text never appears in a past as-of answer (the graph-expansion invariant). | Label historical citations; add the no-leak graph-expansion test | M | S22-4 |
| S22-5 | Scenario 1 and 4 extended temporal assertions | The date-flip behaviour holds across the whole result set. **Done when:** the badge flips by as-of date across all results, not only CP16/22. | Extend assertions to the whole result set | S | S22-5 |

---

## VF3 — Reporting-material connection (Phase 3)

### S3.2 — Verifiable citation for reporting material (templates, tables, instructions)

Story: answers about reporting fields and templates identify the specific template, table, row/field
or instruction that carries the requirement, and the definitions the field depends on.

This story owns the **phase-3 integration acceptance** task (was P3-1).

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S32-1 | Row and instruction-granularity retrieval | Retrieval works at row and instruction granularity. **Done when:** retrieval covers `template_row` and instruction chunks (CRR007 rows 0110/0120/0130, CRR007-INS2) across both the final (PS1/26) and near-final (PS9/24) versions. | Index and retrieve row/instruction chunks; test both document versions | M | S32-1 |
| S32-2 | Structured citation format | Reporting citations point at the exact structured location. **Done when:** a `location` chip such as `template CRR007, rows 0110–0130` is produced, row meanings are quoted verbatim, and the "blank where standardised-only" exception is preserved in the passage. | Build the structured location chip; quote row meanings verbatim; preserve the exception | M | S32-2 |
| S32-3 | Definitions population | Every definition a citation depends on is present. **Done when:** every `definitions` key referenced by a citation resolves to a glossary entry (a missing one is a build failure) and inline expansion data is supplied. | Resolve every definition key; fail the build on a miss; supply inline expansion | M | S32-3 |
| S32-4 | Scenario 3 green | The reporting acceptance scenario passes end to end. **Done when:** scenario 3 passes all assertions — row-level locations, verbatim row meanings, exception preserved, definitions populated, near-final versus final comparison. (was P3-1) | Write scenario 3; assert all of the above | M | S32-4 |

### S1.2 — Forward navigation: rule to reporting representation

Story: start from a prudential rule and see how it appears in reporting instructions and templates,
without manually following references.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S12-1 | Reporting-link extraction (`REPORTS_AGAINST`) | Links from a rule to its reporting representation are created at ingest. **Done when:** instruction-text patterns such as "row NNNN reports…" and "complete row NNNN in accordance with paragraph X" produce edges between the rule chunk and the row chunk. | Write the instruction-pattern detector; create rule-to-row edges | M | S12-1 |
| S12-2 | Forward traversal | From a rule citation, its reporting rows can be followed. **Done when:** the reporting rows linked to a rule citation are surfaced in the related context. | Traverse forward from a rule; surface the reporting rows | M | S12-2 |

### S1.3 — Backward navigation: reporting field to underlying requirement

Story: start from a reporting field or template cell and trace back to the underlying regulatory
requirement and the definitions it depends on.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S13-1 | Backward traversal | From a row or field citation, the governing requirement can be traced back. **Done when:** inbound edges are traversed to the governing requirement(s), including dependent definitions via `DEFINES` edges. | Traverse backward from a row/field; include dependent definitions | M | S13-1 |
| S13-2 | Definition-dependency completeness | Row chunks have all their definition references resolved. **Done when:** every row chunk's `definition_refs` resolves (for example output floor and risk-weighted assets). | Resolve all row definition references; test completeness | S | S13-2 |

### S1.4 — Related-material surfacing

Story: see related definitions, reporting instructions and relevant changes alongside a source being
viewed, so connections are discovered without hunting every reference.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S14-1 | Related-context assembly | Related material is gathered and ranked. **Done when:** graph expansion (up to 2 hops) surfaces referenced, supporting and qualifying sections with their roles, and entity overlap boosts related-material ranking. | Expand the graph; label roles; add entity-overlap boost | M | S14-1 |
| S14-2 | Difficult case (c): citation resolves to table/row/field | A prose citation that resolves into template content lands correctly. **Done when:** a test proves a prose citation resolving into template content lands on the right row with its definitions attached. | Write the difficult-case test; verify row landing and definitions | M | S14-2 |

---

## VF4 — Safe answers (Phase 4)

### S4.1 — Conflict exposure

Story: conflicting sources are presented side-by-side with their status and dates, so the analyst can
decide which applies instead of receiving a silently resolved answer.

This story owns the **five-scenario regression suite** (was X6) and the **integration-checklist
automation** (was X7).

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S41-1 | Conflict detection (model-assisted, experimental) | Materially divergent passages are detected. **Done when:** a second structured pass asks "do these give materially divergent answers?" and returns `{headline, left, right, warning}` with left and right pulled verbatim from the passages; deterministic rule candidates may be added and compared. | Build the detection pass; pull sides verbatim; add rule candidates for comparison | L | S41-1 |
| S41-2 | Conflict object validation | A conflict is never silently resolved. **Done when:** the object is schema-validated, both sides and a warning are always present, the answer never auto-resolves, and data for the escalation button is included. | Validate the schema; require both sides and a warning; attach escalation data | M | S41-2 |
| S41-3 | Scenario 2 green | The supersession-conflict scenario passes end to end. **Done when:** CP16/22 (`superseded/historical` at today) versus PS1/26 (`future-effective`) render side by side and the divergence is flagged in the answer text. | Write scenario 2; assert side-by-side and flagged divergence | M | S41-3 |
| S41-4 | Scenario 5 green | The escalation scenario passes end to end. **Done when:** a conflict between two `future-effective` sources (PS9/24 versus PS1/26) plus CP9/26 as `proposed/consultation` with a "do not rely" qualification renders with three-way authority layering. | Write scenario 5; assert three-way layering and the qualification | M | S41-4 |
| S41-5 | Five-scenario regression suite | All five scenarios run in CI and via a live gate. **Done when:** the suite runs deterministically in recorded mode for CI, supports a separate live-model manual gate, and screenshot-diffs each scenario against the prototype. (was X6) | Assemble the suite; add recorded mode and the live gate; add screenshot diffing | M | S41-5 |
| S41-6 | Integration-checklist automation | The ten checklist items from the prototype integration spec are automated. **Done when:** the ten items run as part of the suite. (was X7) | Automate the ten checklist items; wire into the suite | M | S41-6 |

### S4.2 — Insufficient-evidence statement

Story: the system states clearly when the evidence is insufficient, conflicting or ambiguous, so the
analyst never receives a plausible-looking but weakly supported answer.

This story owns the **per-feature instrumentation** cross-cutting task (was X1).

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S42-1 | Explicit insufficiency output | The system says when it cannot answer well. **Done when:** an explicit statement names what was searched and what is missing and is produced instead of a low-support answer, with the outcome type recorded. | Build the statement; name searched sources and gaps; record the outcome type | M | S42-1 |
| S42-2 | Empty/neutral state | A date with no relevant sources returns a neutral state. **Done when:** an as-of date with no relevant sources returns a neutral empty state with no fabricated answer (a checklist item). | Return the neutral empty state; assert no fabrication | S | S42-2 |
| S42-3 | Per-feature instrumentation | Every feature's flows are measured. **Done when:** for each feature's flows, time-to-answer, sources/citations used and outcome type (answer, refusal, escalation) are captured; this feeds the A3 test and Open Question Q8 and runs in every phase. (was X1) | Add the capture points per feature; report to the A3 test and Q8 | S | S42-3 |

### S4.3 — Evidence-backed escalation package

Story: assemble a well-bounded escalation (the question plus the evidence package) to hand to an SME,
so the SME focuses on the judgement rather than redoing the research.

| # | Task | What "done" looks like (SMART) | Subtasks | Size | Test |
|---|---|---|---|---|---|
| S43-1 | Escalation assembly | A bounded escalation summary is produced. **Done when:** it contains the question, the evidence with citations and status, and the specific unresolved point (the conflict headline plus source IDs when a conflict is present). | Assemble the summary; include citations, status and the unresolved point | M | S43-1 |
| S43-2 | Escalation modal pre-fill | The frozen escalation modal consumes the package. **Done when:** the frozen modal is pre-filled from the package and the submit flow is unchanged. | Pre-fill the modal; keep the submit flow unchanged | S | S43-2 |
| S43-3 | A3 instrumentation | Refusal/escalation appropriateness is captured. **Done when:** the appropriateness of each refusal/escalation outcome is recorded, feeding the A3 test and Open Question Q8. | Capture appropriateness per outcome | S | S43-3 |

---

## Deferred (explicitly out of V1 — recorded so nothing is silently dropped)

These remain stories in the backlog but carry no V1 tasks. They are retained here for traceability.

- **STUB-1** stale-answer marking — waiting on Open Question Q10 (staleness window/threshold); builds
  on DI-5 and DI-6.
- **STUB-2** answer audit store — waiting on data-retention, ownership and reliance decisions;
  builds on DI-6.
- **STUB-3** impact-tracing capture — pairs with STUB-1 and STUB-2; a candidate for a graph-store swap.
- **STUB-4** newer-analyst learning path — blocked on a direct newer-analyst interview.
- **STUB-5** structured feedback categories — after V1.
- Sign-on (SSO), shared hosting and a refresh service-level agreement — revisit before any deployment
  beyond local development.

---

## Traceability matrix (task → story → feature → epic sub-hypothesis)

Epic sub-hypotheses: SH1 evidence discovery and connection; SH2 provenance and citations; SH3 temporal
and status awareness; SH4 conflict and uncertainty handling; SH5 corpus governance and staleness.

| Story | Feature | Epic sub-hypothesis | Tasks |
|---|---|---|---|
| DI-1 | VF0 | SH5 | DI1-1 … DI1-8 |
| DI-2 | VF0 | SH3, SH5 | DI2-1, DI2-2 |
| DI-3 | VF0 | SH1, SH5 | DI3-1 … DI3-9 |
| DI-4 | VF0 | SH1, SH5 | DI4-1 … DI4-11 |
| DI-5 | VF0 | SH5 | DI5-1, DI5-2 |
| DI-6 | VF0 | SH5 | DI6-1 |
| S1.1 | VF1 | SH1 | S11-1 … S11-7 |
| S2.1 | VF1 | SH3 | S21-1 … S21-3 |
| S2.3 | VF1 | SH2 | S23-1 … S23-3 |
| S3.1 | VF1 | SH2 | S31-1 … S31-4 |
| S3.3 | VF1 | SH2 | S33-1 … S33-5 |
| S2.2 | VF2 | SH3 | S22-1 … S22-5 |
| S3.2 | VF3 | SH2 | S32-1 … S32-4 |
| S1.2 | VF3 | SH1 | S12-1, S12-2 |
| S1.3 | VF3 | SH1 | S13-1, S13-2 |
| S1.4 | VF3 | SH1 | S14-1, S14-2 |
| S4.1 | VF4 | SH4 | S41-1 … S41-6 |
| S4.2 | VF4 | SH4 | S42-1 … S42-3 |
| S4.3 | VF4 | SH4 | S43-1 … S43-3 |

**Orphan check:** every task above sits under a story. The former `F1–F7` tasks now sit under DI-1
(F1, F2, F3, F4), DI-4 (F5, F6) and S3.3 (F7). The former `ST0-1/2/3` sit under S1.1 (S11-2, S11-3,
S11-4). The former `X1–X7` sit under S4.2 (X1), DI-3 (X2), DI-4 (X3, X4), S3.1 (X5), S4.1 (X6, X7).
The former `P1-1/2/3` sit under S3.3 (S33-3, S33-4, S33-5) and `P3-1` under S3.2 (S32-4). No task
remains outside a story.

## Provenance

- Stories: `2025-06-18_user-story-backlog-v2.md` · Features: `2025-06-18_epic-feature-breakdown-v3.md`
  · Epic: `2025-06-18_epic-hypothesis-regcopilot-v1.md`
- Contract: `regcopilot-prototype-integration-spec.md` (frozen UI; input/output contract; §8 checklist)
- Supersedes `2026-10-03_user-story-tasks-regcopilot-v1.md` (retained unchanged for audit).
- Tests: `2026-10-06_user-story-tasks-regcopilot-v2-tests.md` (keyed by task ID).










