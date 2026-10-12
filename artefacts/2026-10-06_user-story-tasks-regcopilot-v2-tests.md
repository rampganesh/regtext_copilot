# Test Specification — RegCopilot V1 User Stories v2 (tasks-linked, spec only)

Companion to `2026-10-06_user-story-tasks-regcopilot-v2.md`. Every test is keyed by the **task ID** it
verifies, so a test is found by its task. This is a **specification only** — it describes what each
test checks; it is not code.

**How to read each entry.** Every test lists: **Test name** · **Type** (unit or integration) ·
**What it checks** · **Inputs** · **Assertions (pass criteria)**. "Unit" means a plain function or
module tested in isolation; "integration" means it exercises the database, the retrieval pipeline, the
model adapter, or the API end to end.

**Framework note.** These tests are written to be run with `pytest` (the test runner chosen in task
DI1-1). Model-dependent tests run in **recorded mode** by default (previously recorded model
responses) so that Continuous Integration (CI) is deterministic; a **live mode** calls the real model
and is a separate manual gate (see task S33-4). Two global gates appear in most assertion sets:
**no fabricated quotation** (every quoted span exists verbatim in the source) and **no confidence
score** anywhere in the output.

**Global abbreviations:** Capital Requirements Regulation (CRR); Prudential Regulation Authority
(PRA); Retrieval-Augmented Generation (RAG); large language model (LLM); JavaScript Object Notation
(JSON); HyperText Markup Language (HTML); Application Programming Interface (API); Structured Query
Language (SQL).

---

## Global invariant tests (apply to every story)

These are cross-cutting and are referenced by, rather than repeated in, the per-task tests below.

| Test name | Type | What it checks | Assertions (pass criteria) |
|---|---|---|---|
| `invariant_no_fabrication_all_paths` | integration | No response path returns a quotation or reference not present verbatim in a stored chunk. | For every citation, conflict side and passage returned across all five scenarios, the quoted span exists in the source chunk after whitespace normalisation. **Zero exceptions.** |
| `invariant_no_confidence_score` | unit | No confidence score, rating or ranking percentage is ever rendered. | The response schema has no score field and the rendered output contains no numeric confidence value. |
| `invariant_five_status_labels_only` | unit | Only the five allowed status labels can ever be produced. | The status enum contains exactly the five labels and no code path can emit any other value. |
| `invariant_evidence_led_phrasing` | unit | Every answer opens evidence-led and never asserts applicability. | The first sentence matches the evidence-led pattern and the phrase "the applicable requirement is…" never appears. |

---

## VF0 — Document & corpus foundation

### DI-1 — Curated corpus loading

**DI1-1 — project scaffold**
- **Type:** unit. **Checks:** the empty project passes quality gates.
- **Assertions:** linting passes; strict type checking passes; the test runner runs and reports at
  least one collected test; the required package folders exist.

**DI1-2 — local environment and database**
- **Type:** integration. **Checks:** the database is reachable and the vector extension is present.
- **Assertions:** a connection succeeds using `.env` values; a query confirms the `vector` extension
  is installed; the README steps reproduce this on a clean checkout.

**DI1-3 — migration framework**
- **Type:** integration. **Checks:** migrations apply and reverse cleanly.
- **Assertions:** the baseline migration applies, then rolls back, leaving the schema unchanged.

**DI1-4 — sources and versions tables**
- **Type:** integration. **Checks:** the two tables and their constraints.
- **Assertions:** inserting the same version label twice for one source is rejected; a version of a
  different source with the same label is accepted; all dates store as plain dates.

**DI1-5 — ingest entry point**
- **Type:** integration. **Checks:** one command stages a document and is idempotent.
- **Assertions:** running the command creates `raw.json`, `chunks.json`, `edges.json` and
  `review.json`; running it twice for the same version leaves exactly one version (no duplicates).

**DI1-6 — approval gate**
- **Type:** integration. **Checks:** unapproved sources are never retrievable.
- **Assertions:** before `approve`, a retrieval query returns nothing for that source; after
  `approve`, it is retrievable; exclusion rules reject a disallowed document type at ingest.

**DI1-7 — real corpus manifest**
- **Type:** integration. **Checks:** the real documents are loaded with correct dates.
- **Assertions:** all five policy/consultation documents plus the Rulebook parts and CRR007 are
  present, each with a published date and an effective date matching the desk-research timeline.

**DI1-8 — inference provider adapter**
- **Type:** unit + integration. **Checks:** all model calls go through one swappable interface.
- **Assertions:** the adapter exposes `chat(messages, json_schema)` and `embed(texts)`; both provider
  implementations satisfy the interface and can be swapped by configuration; temperature defaults to
  0; a deliberately non-conforming model output is retried once and then fails loudly.

### DI-2 — Source metadata capture

**DI2-1 — metadata fields**
- **Type:** unit. **Checks:** publication and effective dates are independent.
- **Inputs:** a sample version where the two dates differ.
- **Assertions:** both dates are stored distinctly; no code derives "applicable" from "latest".

**DI2-2 — five-status vocabulary**
- **Type:** unit. **Checks:** the status set is closed and enforced by the database.
- **Assertions:** inserting a sixth label fails; the five labels insert successfully; ingest stores
  base facts only and does not compute status.

### DI-3 — Relationships and versioning

**DI3-1 — relationship table**
- **Type:** integration. **Assertions:** a supersession cycle is rejected; a relationship whose dates
  contradict the effective-date ranges is rejected.

**DI3-2 — relationship capture**
- **Type:** unit. **Assertions:** `--supersedes` records a link; the boilerplate detector matches
  "this Statement supersedes CP16/22" and records the link.

**DI3-3 — template and instruction versioning**
- **Type:** integration. **Assertions:** a CRR007 version links to its specific rule version and no
  current rule is ever returned with an outdated instruction.

**DI3-4 — explicit reference extraction**
- **Type:** unit. **Inputs:** text containing `¶ 5.22`, `4.12`, `SA-2.4`, `ISA-3.1`, `row 0110`, an
  Appendix reference and a Chapter reference. **Assertions:** each pattern is recognised and resolves
  to a chunk via the location index; the edge type is `REFERENCES`.

**DI3-5 — reference scoping disambiguation**
- **Type:** unit. **Inputs:** "Article 105" inside Trading Book (CRR) Part, and a bare "Article 108".
  **Assertions:** the qualified reference resolves to that Part's article; the bare reference resolves
  to the correct default scope; the scope used is the one in force at the citing chunk.

**DI3-6 — range expansion**
- **Type:** unit. **Inputs:** "Articles 192 to 239" and "Sections 3 to 5 of Chapter 3".
  **Assertions:** one edge per article and per section is produced; endpoints are inclusive; an
  unreasonably large range is capped and flagged.

**DI3-7 — continuation and dependence links**
- **Type:** unit. **Inputs:** a paragraph split across a two-column table and a page break; a chunk
  needing another for its meaning. **Assertions:** the split paragraph becomes one logical chunk via a
  `CONTINUES` link; a `DEPENDS_ON` link is created where meaning depends on another chunk.

**DI3-8 — implicit pass and coverage measure**
- **Type:** integration. **Inputs:** the hand-labelled ~20-section sample. **Assertions:** precision is
  computed and at or above the agreed threshold before edges are trusted; a coverage figure
  (found ÷ expected) is produced and recorded.

**DI3-9 — unresolved-reference queue**
- **Type:** integration. **Assertions:** an unresolved reference is written with
  `review_state='pending'` and appears in `review.json`; graph expansion treats a pending endpoint as
  unavailable and never blocks an answer.

### DI-4 — Structured content ingestion

**DI4-1 — PDF parsing spike**
- **Type:** integration. **Assertions:** the report states a section-map extraction rate for a real
  PDF; multi-column reading order is verified; the licence confirmation is recorded.

**DI4-2 — embedding model spike**
- **Type:** integration. **Assertions:** a comparison over about 20 passage pairs exists; a choice is
  recorded; the vector dimension is present in configuration.

**DI4-3 — structure extraction**
- **Type:** unit. **Assertions:** repeated headers/footers are removed; each page maps to a section;
  paragraph order matches the document.

**DI4-4 — location-ID detection**
- **Type:** unit. **Assertions:** paragraph, chapter/section/appendix, row code, instruction ID and
  glossary anchors each receive a unique per-version location ID; no duplicates exist.

**DI4-5 — paragraph chunker**
- **Type:** unit. **Assertions:** a paragraph over 600 words splits on sentence boundaries with
  sub-IDs; the verbatim content is stored; no chunk is empty.

**DI4-6 — table, template-row and glossary chunkers**
- **Type:** unit. **Assertions:** table and per-row chunks exist; template-row chunks carry the
  verbatim row meaning; definitions are collected into the glossary.

**DI4-7 — chunks and row-fields tables**
- **Type:** integration. **Assertions:** the location-ID-unique-per-version constraint holds; the
  embedding column is the vector type; `chunk_row_fields` stores the expected fields.

**DI4-8 — template-row spike**
- **Type:** integration. **Assertions:** the report states a row extraction rate; verbatim row
  meanings are confirmed; the cross-check decision is recorded.

**DI4-9 — entity extraction**
- **Type:** integration. **Assertions:** the pass writes `{name, type}` rows to the `entities` table,
  each linked to its citing chunk.

**DI4-10 — embedding indexer**
- **Type:** integration. **Assertions:** every chunk has a stored vector; a full-text index exists on
  chunk content; a sample keyword query returns the expected chunk.

**DI4-11 — ingestion structural checks**
- **Type:** integration. **Assertions:** unique location IDs; non-empty chunks with resolvable
  parents; all definition references resolve; edges resolve or are pending; supersession chains are
  acyclic and date consistent; a random chunk render matches its PDF page.

### DI-5 — Amendment intake

**DI5-1 — amendment detection**
- **Type:** integration. **Assertions:** the report lists added, changed and deleted paragraphs and
  rows, using normalised text difference and embedding similarity.

**DI5-2 — candidate-update workflow**
- **Type:** integration. **Assertions:** a detected version lands as `pending` with its diff;
  `approve`/`reject` move it out of `pending`; no detection output can become active without approval.

### DI-6 — Version retention

**DI6-1 — historical retention**
- **Type:** integration. **Assertions:** all versions are retained with date ranges; a past as-of
  query returns the historical chunk; staged context is preserved.

---

## VF1 — Core Copilot

### S1.1 — Natural-language search

**S11-1 — query handling**
- **Type:** unit. **Assertions:** a free question with no operators is accepted; an optional rewrite is
  applied for retrieval only; the displayed question is the original.

**S11-2 — hybrid retrieval**
- **Type:** integration. **Assertions:** semantic and keyword results are combined by reciprocal-rank
  fusion; the `active` and `published_date ≤ as-of` filters are applied; an unapproved or future
  document never appears.

**S11-3 — version de-duplication**
- **Type:** integration. **Assertions:** when several versions survive the filter, only the one
  operative at the as-of date is used by default; another version can surface as a historical citation
  when the question needs it.

**S11-4 — relationship graph module**
- **Type:** integration. **Assertions:** expansion stops at 2 hops; `QUALIFIES` edges are always
  included; the as-of filter is re-applied to every expanded node; a superseder's text never leaks into
  a past as-of answer.

**S11-5 — regulatory-relevance ranking**
- **Type:** unit. **Assertions:** ranking combines term, subject-area, entity-overlap and a mild
  authority prior; no result is labelled "the applicable provision".

**S11-6 — relevance-ranking spike**
- **Type:** integration. **Assertions:** the spike runs against the difficult-case set and its findings
  are recorded and linked to Open Question Q8.

**S11-7 — result assembly**
- **Type:** integration. **Assertions:** each ranked result carries a location ID and a resolved status.

### S2.1 — Status label and effective date

**S21-1 — status resolver**
- **Type:** unit. **Inputs:** the five-rule table with boundary as-of dates.
- **Assertions:** all five statuses are derivable and nothing else; supersession timing is correct; no
  retro-application; the function uses no model. This is the strongest unit-test target in the build
  and must cover every rule × boundary combination.

**S21-2 — badges on results and answers**
- **Type:** unit. **Assertions:** every result and citation carries a badge and a status date; the
  badge is one of exactly five labels.

**S21-3 — latest is not applicable**
- **Type:** integration. **Assertions:** at any as-of date, a superseded source is never surfaced as
  the current one.

### S2.3 — Evidence-led answer language

**S23-1 — synthesis prompt and JSON output**
- **Type:** integration. **Assertions:** the answer opens "The relevant sources indicate…"; authority
  levels are contrasted; citations are by location ID; the forbidden phrase never appears. (Covered
  also by the global `invariant_evidence_led_phrasing`.)

**S23-2 — insufficient-evidence path**
- **Type:** integration. **Assertions:** when passages do not support an answer, an explicit
  insufficient-evidence structure naming what was searched and what is missing is returned.

**S23-3 — phrasing enforcement**
- **Type:** unit. **Assertions:** an answer whose first sentence is not evidence-led, or that contains
  the forbidden phrase, fails the test.

### S3.1 — Verifiable citations

**S31-1 — citation builder**
- **Type:** unit. **Assertions:** the citation matches the frozen contract shape with source facts, a
  location chip, a passage with `hl`/`qual` spans and definition keys.

**S31-2 — verbatim verification gate (shared library)**
- **Type:** unit + integration. **Inputs:** a real passage, a paraphrased passage, a fabricated span.
- **Assertions:** the real passage passes; a fabricated span either drops the citation or fails loudly
  in development; behaviour is never silent. Shared by synthesis, conflict and escalation paths.

**S31-3 — HTML sanitizer**
- **Type:** unit. **Inputs:** hostile inputs containing script tags, event attributes and other HTML.
- **Assertions:** only `hl` and `qual` spans survive; all other HTML is stripped.

**S31-4 — context navigation payload**
- **Type:** unit. **Assertions:** the payload carries the parent breadcrumb and adjacent paragraphs.

### S3.3 — Surrounding-context navigation

**S33-1 — context view with qualifications**
- **Type:** integration. **Assertions:** the surrounding passage is returned with qualifications
  preserved; the scenario-1 exception (90-day / EUR 1m) is present.

**S33-2 — prototype wiring**
- **Type:** integration. **Assertions:** the frozen page is served; `ask()` calls the real endpoint on
  the same origin; the expand and definition handlers consume API data unchanged; loading, error and
  empty states exist.

**S33-3 — ask endpoint**
- **Type:** integration. **Assertions:** `POST /api/v1/ask` validates input and output with the schema
  models; the as-of date defaults to today; an empty result returns a neutral state with no fabricated
  answer.

**S33-4 — recorded-response harness**
- **Type:** integration. **Assertions:** scenarios 1 and 4 run in recorded mode in CI; a live run is a
  separate manual gate; results are identical to the recorded run.

**S33-5 — scenarios 1 and 4**
- **Type:** integration. **Assertions:** scenario 1 (prose citation with exception) and scenario 4
  (two-thousand-and-twenty-two as-of date flips CP16/22 to `proposed/consultation`) pass all
  assertions.

---

## VF2 — Temporal navigation

### S2.2 — As-of-date answers

**S22-1 — temporal coexistence**
- **Type:** integration. **Assertions:** current and future-effective sources are presented side by
  side, each with its own badge and dates.

**S22-2 — difficult case (a)**
- **Type:** integration. **Assertions:** when the top terminology match is not the operative provision
  at the as-of date, the point-in-time filter and resolver still return the correct result.

**S22-3 — difficult case (b)**
- **Type:** integration. **Assertions:** "in force now" and "takes effect later" are separated and never
  merged into one regime.

**S22-4 — superseded/historical handling**
- **Type:** integration. **Assertions:** a historical citation carries `superseded/historical` plus the
  superseder's effective date; the superseder's text never appears in a past as-of answer.

**S22-5 — extended temporal assertions**
- **Type:** integration. **Assertions:** the badge flips by as-of date across the whole result set, not
  only CP16/22.

---

## VF3 — Reporting-material connection

### S3.2 — Verifiable citation for reporting material

**S32-1 — row/instruction retrieval**
- **Type:** integration. **Assertions:** row and instruction chunks (CRR007 rows 0110/0120/0130,
  CRR007-INS2) are retrievable across both PS1/26 and PS9/24.

**S32-2 — structured citation format**
- **Type:** unit. **Assertions:** the location chip reads like `template CRR007, rows 0110–0130`; row
  meanings are verbatim; the "blank where standardised-only" exception is preserved.

**S32-3 — definitions population**
- **Type:** integration. **Assertions:** every `definitions` key resolves to a glossary entry; a missing
  one fails the build; inline expansion data is present.

**S32-4 — scenario 3**
- **Type:** integration. **Assertions:** row-level locations, verbatim row meanings, the exception,
  populated definitions and the near-final versus final comparison all pass.

### S1.2 — Forward navigation

**S12-1 — reporting-link extraction**
- **Type:** unit. **Inputs:** "row 0110 reports…", "complete row 0110 in accordance with paragraph X".
- **Assertions:** rule-to-row edges of type `REPORTS_AGAINST` are created.

**S12-2 — forward traversal**
- **Type:** integration. **Assertions:** from a rule citation, its reporting rows appear in the related
  context.

### S1.3 — Backward navigation

**S13-1 — backward traversal**
- **Type:** integration. **Assertions:** from a row/field citation, the governing requirement(s) and
  dependent definitions are surfaced.

**S13-2 — definition-dependency completeness**
- **Type:** integration. **Assertions:** every row chunk's `definition_refs` resolves (output floor,
  risk-weighted assets, and so on).

### S1.4 — Related-material surfacing

**S14-1 — related-context assembly**
- **Type:** integration. **Assertions:** expansion surfaces referenced, supporting and qualifying
  sections with roles; entity overlap boosts related-material ranking.

**S14-2 — difficult case (c)**
- **Type:** integration. **Assertions:** a prose citation resolving into template content lands on the
  right row with its definitions attached.

---

## VF4 — Safe answers

### S4.1 — Conflict exposure

**S41-1 — conflict detection**
- **Type:** integration. **Inputs:** two materially divergent passages. **Assertions:** the pass returns
  `{headline, left, right, warning}` with both sides pulled verbatim from the passages.

**S41-2 — conflict object validation**
- **Type:** unit. **Assertions:** the object is schema-valid; both sides and a warning are always
  present; the answer never auto-resolves; escalation data is attached.

**S41-3 — scenario 2**
- **Type:** integration. **Assertions:** CP16/22 (`superseded/historical` at today) and PS1/26
  (`future-effective`) render side by side with the divergence flagged.

**S41-4 — scenario 5**
- **Type:** integration. **Assertions:** the PS9/24 versus PS1/26 conflict plus CP9/26 as
  `proposed/consultation` renders with three-way authority layering and the "do not rely" qualification.

**S41-5 — five-scenario regression suite**
- **Type:** integration. **Assertions:** all five scenarios pass in recorded mode for CI; a live run is a
  separate manual gate; each scenario screenshot-matches the prototype.

**S41-6 — integration checklist automation**
- **Type:** integration. **Assertions:** the ten checklist items from the prototype integration spec run
  and pass as part of the suite.

### S4.2 — Insufficient-evidence statement

**S42-1 — insufficiency output**
- **Type:** integration. **Assertions:** an explicit statement naming what was searched and what is
  missing is returned instead of a low-support answer; the outcome type is recorded.

**S42-2 — empty/neutral state**
- **Type:** integration. **Assertions:** an as-of date with no relevant sources returns a neutral empty
  state and no fabricated answer.

**S42-3 — per-feature instrumentation**
- **Type:** integration. **Assertions:** for each feature's flows, time-to-answer, sources/citations
  used and outcome type are captured and available to the A3 test and Open Question Q8.

### S4.3 — Evidence-backed escalation package

**S43-1 — escalation assembly**
- **Type:** integration. **Assertions:** the summary contains the question, the evidence with citations
  and status, and the specific unresolved point (with the conflict headline and source IDs when a
  conflict is present).

**S43-2 — escalation modal pre-fill**
- **Type:** integration. **Assertions:** the frozen modal is pre-filled from the package; the submit
  flow is unchanged.

**S43-3 — A3 instrumentation**
- **Type:** integration. **Assertions:** the appropriateness of each refusal/escalation outcome is
  recorded and available to the A3 test and Open Question Q8.

---

## Coverage check

Every task in `2026-10-06_user-story-tasks-regcopilot-v2.md` has a matching test block above, keyed by
the same task ID. The four global invariant tests apply on top of the per-task tests and cover the
no-fabrication, no-confidence-score, five-labels and evidence-led-phrasing invariants across all
stories.

## Provenance

- Tasks: `2026-10-06_user-story-tasks-regcopilot-v2.md`
- Stories: `2025-06-18_user-story-backlog-v2.md` · Contract:
  `regcopilot-prototype-integration-spec.md` (§8 checklist) · Epic:
  `2025-06-18_epic-hypothesis-regcopilot-v1.md` (validation measures and hard gate).




