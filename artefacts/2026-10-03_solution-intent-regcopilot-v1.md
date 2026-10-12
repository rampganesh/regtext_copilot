# Solution Intent: RegCopilot V1 — Evidence-Led Basel 3.1 Regulatory Research Assistant

*Derived from the Value Stream Epic `2025-06-18_epic-hypothesis-regcopilot-v1.md`. Solution intent status: **lean** — core elements are knowledge-confirmed via the validated prototype; a small set of elements remain explicitly speculative and are tagged throughout as **[FIXED]** or **[SPECULATIVE]**. Audience: technical and non-technical stakeholders assessing uniqueness and budget approval.*

---

## 1. Vision

**If we** provide an evidence-led research assistant that finds, connects and explains authoritative UK capital regulatory evidence — with precise inspectable citations, visible source status and effective dates, and explicit uncertainty/conflict signalling
**for** experienced regulatory reporting analysts on the UK capital reporting team preparing for Basel 3.1 (secondary beneficiary: newer analysts learning the research path)
**Then we will** materially reduce the time required to produce a verified, evidence-backed answer **without** reducing evidence quality or increasing unsafe answers.

The solution is a Retrieval-Augmented Generation (RAG) research assistant ("RegCopilot") over a bounded, Content-Owner-gated corpus of Basel 3.1 regulatory material. Its defining differentiator — the reason it is unique — is that correctness and trustworthiness are enforced by **deterministic systems, not model confidence**:

- Every citation, quotation and passage is mechanically verified verbatim against source text before it reaches the analyst (hard gate: zero fabricated citations).
- Source status is computed by a pure, unit-tested rules function relative to the analyst's chosen **as-of date** — the system never infers "latest = applicable".
- Conflicts between sources are surfaced side-by-side and never silently resolved; escalation to a human SME is the only resolution path.

Five capabilities, each an independently testable sub-hypothesis from the epic:

| # | Capability | Sub-hypothesis |
|---|---|---|
| 1 | Evidence discovery & connection | Natural-language questions return genuinely relevant authoritative sources plus related material — faster starting point, fewer dead ends (SH1) |
| 2 | Provenance & citations | Every answer carries source + document/version/status + precise location, including tables/rows/fields for reporting questions (SH2) |
| 3 | Temporal & status awareness | Source status (five-label taxonomy) always shown on an explicit as-of-date basis (SH3) |
| 4 | Conflict & uncertainty handling | Conflicts exposed; insufficient evidence stated explicitly; evidence-backed escalation supported (SH4 — tests the untested assumption A3) |
| 5 | Corpus governance & staleness readiness | Bounded curated corpus under Content-Owner governance, with amendment intake and version retention designed in from day one (SH5) |

---
## 2. Solution Context

The environment the solution operates in — summarised inline because stakeholders will read this document standalone. *(Full ground truth: `wiki/decisions/`, `wiki/problems/`, `wiki/assumptions.md`, `wiki/personas/` as cited in the story backlog.)*

### 2.1 Regulatory environment [FIXED]
- UK Basel 3.1 implementation is in a transition period: CP16/22 (consultation, 2022) → PS17/23 (near-final) → PS9/24 (near-final rules) → PS1/26 (final rules) → CP9/26 (current consultation). Current/future and proposed/final requirements **coexist** in the corpus — a "correct" answer built from the wrong document version is a real, observed failure mode (confirmed problem: source-validation burden, 7 mentions).
- The real corpus the V1 build must support: CP16/22, PS17/23, PS9/24, PS1/26, CP9/26, PRA Rulebook parts, reporting instructions/templates (e.g. CRR007), plus explanatory overviews. Approximate size: ≤ 1,500 pages, PDF format.

### 2.2 Users and workflow [FIXED]
- **Primary persona:** experienced regulatory reporting analyst (`wiki/personas/experienced-analyst.md`) — jumps directly to likely sources; needs to verify, not be told what applies. The analyst remains responsible for the conclusion (header disclaimer + answer note on every result).
- **Newer-analyst persona is excluded from V1** (second-hand evidence only — STUB-4; requires a direct interview before any design).
- Questions arrive as free natural language — no search operators (frozen UI decision).

### 2.3 Governance split [FIXED]
- **Regulatory Content Owner** governs corpus inclusion, source status and relationships; **Technology** owns ingestion, indexing and the retrieval pipeline (bounded-curated-corpus decision, row 5).
- Nothing enters the active corpus without Content Owner approval; Technology's amendment detection produces candidate updates that never auto-activate (staleness decision L6–L12).

### 2.4 Technical constraints and decisions [FIXED unless marked]
- Backend is **Python end-to-end: FastAPI + Pydantic**, PostgreSQL 16 + pgvector (single store, includes the relationship edge table), **PyMuPDF** for PDF parsing. *(AGPL licensing note for PyMuPDF: acceptable for internal, non-distributed tooling per our working assumption — to be confirmed with compliance before Phase 0a completes.)*
- LLM inference via **OpenRouter** behind a thin provider adapter, kept swappable (Azure OpenAI / direct providers later); embeddings endpoint chosen in the Phase 0a spike.
- **Local development only for V1**; no authentication/SSO in scope.
- Frontend is the **validated prototype UI, frozen**: `regcopilot-prototype.html`. Only `ask()` is edited to call the API; mock data layers deleted; loading/error/empty states added minimally.
- Conflict detection is **LLM-assisted with deterministic validation**, an explicit experiment: rule-based candidates may be added and results compared.

---

## 3. Specifications

### 3.1 The frozen UI/API contract [FIXED]

**Input contract** (`POST /api/v1/ask`, produced by `ask()`):

```json
{ "question": "string — free natural language, trimmed",
  "asOfDate": "YYYY-MM-DD — defaults to today when empty" }
```

**Output contract** (the single consumer is the prototype's `render(sc, asOf)`):

```json
{
  "question": "echo of the user question",
  "answer": [ { "text": "paragraph — plain text or sanitized HTML" } ],
  "conflict": null | {
      "headline": "one-line description of the divergence",
      "left":  { "sourceKey": "...", "text": "passage with <span class='hl'>…</span>", "meta": "status · dates · paragraph ref" },
      "right": { "sourceKey": "...", "text": "...", "meta": "..." },
      "warning": "explicit note that the UI does not pick a source" },
  "citations": [ {
      "source": { "id", "title", "type", "publishedDate", "status", "statusDate" },
      "location": "PS17/23 · Credit risk (SA) · paragraph SA-2.4",
      "passage": "operative text in <span class='hl'>…</span>, qualifications in <span class='qual'>…</span>",
      "definitions": [ "output floor", "risk weight" ] } ],
  "definitions": { "output floor": "definition text…", "IRB": "…" }
}
```

**Product rules encoded in the contract (compliance-relevant, non-negotiable):**

1. **No confidence scores, ever** — no score field exists anywhere and none may be added; trust comes from evidence chains only.
2. **Evidence-led phrasing** — answers begin "The relevant sources indicate…"; never "The applicable requirement is…". Enforced in the synthesis prompt; a violation is a build failure.
3. **Five status badges exactly:** `Final/Operative`, `Future-Effective`, `Superseded/Historical`, `Proposed/Consultation`, `Explanatory/Supporting` — plus a status date on every cited source. No other status may render.
4. **Conflicts are never auto-resolved** — structured conflict object, side-by-side rendering, escalation button as the only resolution path.
5. **Effective dates are metadata, not applicability** — statuses computed relative to the as-of date; nothing in the UI claims a rule applies to the bank.
6. **Context views preserve qualifications/exceptions** — retrieval returns the surrounding passage *with* its qualifications (`qual` spans), never a stripped quote.
7. **Analyst owns the conclusion** — disclaimer in the header; answer note on every result.
8. **No fabrication** — every citation passage, quote and conflict panel text is verified verbatim against source chunk content (whitespace-normalized) server-side; only `hl`/`qual` inline tags allowed, all other HTML sanitized away.
9. **Point-in-time retrieval** — nothing published after the as-of date may appear in any answer, including graph-expanded context.
10. **Definitions completeness** — every `definitions` key referenced by a citation must resolve to a glossary entry; a missing definition is a build failure.

---
### 3.2 Capability specifications (features)

- **VF0 — Document & corpus foundation (priority-0 prerequisite):** DI-1 curated corpus loading (Content-Owner gated); DI-2 source metadata capture (five-status taxonomy, publication vs effective date); DI-3 supersession/amendment/reference relationships; DI-4 structured content ingestion (tables, templates, rows/fields, definition links); DI-5 amendment intake and validation gate (detection ≠ activation); DI-6 version retention with effective-date ranges.
- **VF1 — Core Copilot (walking skeleton):** natural-language search with regulatory-relevance ranking (S1.1); status badges + effective dates (S2.1); evidence-led answer phrasing (S2.3); verifiable prose citations (S3.1); surrounding-context navigation from a citation (S3.3). One question in → one verified, evidence-led answer out.
- **VF2 — Temporal navigation:** as-of-date answers distinguishing current vs future vs superseded (S2.2); covers "most-obvious-document-not-correct" and "current/future coexistence" difficult scenarios.
- **VF3 — Reporting-material connection:** structured citations to template/table/row/field with dependent definitions (S3.2); forward navigation rule → reporting representation (S1.2); backward navigation field → underlying requirement (S1.3); related-material surfacing (S1.4).
- **VF4 — Safe answers:** conflict exposure side-by-side (S4.1); insufficient-evidence statement (S4.2); evidence-backed escalation package (S4.3 — the A3 test vehicle).

**Global invariants across all features:** no fabrication; five status labels only; evidence-led language; no confidence scores; analyst remains responsible.

**Deferred (recorded, not in V1 scope):** STUB-1 stale-answer marking (gated on open question Q10), STUB-2 answer audit store, STUB-3 impact-tracing capture, STUB-4 newer-analyst learning path, STUB-5 structured feedback categories.

---

## 4. Compliance

*Kept deliberately narrow: only considerations actually discussed and decided to date. This is not a regulatory compliance assessment; it is the list of governance and safety commitments the solution makes.*

**Fixed commitments:**

| Commitment | Source |
|---|---|
| **Bounded, curated corpus.** Only approved UK capital/Basel 3.1 material (Rulebook, policy/supervisory statements, reporting instructions/templates). Exclusions: unrelated domains, uncontrolled web content, unclear-provenance material, sources mistakable for operative requirements when only explanatory/proposed. | bounded-curated-corpus decision, row 5 |
| **Content Owner approval gate.** Nothing becomes active corpus without Content Owner confirmation; Technology detection of amendments is distinct from corpus authority state — detection does not establish relevance or authority. | bounded-corpus row 5; staleness decision L6–L7, L12 |
| **No fabricated citations/quotations/references.** Mechanically enforced (verbatim verification gate); the epic's validation measures make this a hard gate — one failure fails the experiment. | minimum-provenance-standard decision; citation-integrity problem (confirmed) |
| **No autonomous applicability determination.** The system never asserts which requirement applies to the bank; ranking never picks "the applicable provision"; the analyst owns the conclusion. Conscious exclusion of the V1 scope decision. | v1-scope decision; status-authority-labelling decision; requirement-applicability problem |
| **"Latest" is never derivable as applicable.** Status always computed on an explicit as-of-date basis; effective date distinct from publication date. | date-based-temporal-mode decision |
| **Explanatory material is visibly non-contemporaneous.** Explanatory/supporting sources carry their published date, which visibly post-dates the query when answering historical as-of questions. | scenario 4 acceptance specification |

**Variable / open (flagged, not assumed):**
- Data retention, ownership and reliance considerations for storing answers (Meeting 2 L151) — deferred to STUB-2 design; not assumed in initial build.
- Staleness window/threshold for stale-answer marking (open question Q10) — gates STUB-1.
- No authentication/SSO for V1 (local dev) — must be revisited before any shared/pilot deployment.

---
## 5. Architecture and Design

### 5.1 Critical architectural elements

```
┌───────────────────────── Frontend (existing, frozen) ─────────────────────────┐
│  regcopilot-prototype.html — ask() → POST /api/v1/ask;                       │
│  SCENARIOS/DEFS/chips deleted; loading + error + empty states added          │
└─────────────────────────────────────┬─────────────────────────────────────────┘
                                      │ {question, asOfDate}
┌─────────────────────────────────────▼─────────────────────────────────────────┐
│                    Python / FastAPI backend (Uvicorn)                          │
│  1. Input validation (Pydantic)                                                │
│  2. Hybrid retrieval: pgvector dense + Postgres full-text → RRF fusion         │
│  3. Graph expansion: edge table + recursive CTEs (≤2 hops)                     │
│  4. Status resolution: pure function, no LLM (correctness core)                │
│  5. Definition expansion: glossary lookup per citation                         │
│  6. Synthesis: LLM via OpenRouter adapter — fresh text with citations          │
│  7. Conflict detection: LLM-assisted, structured JSON, validated (S4.1)        │
│  8. Verbatim verification + HTML sanitization (hard gate)                      │
│  9. Response schema validation → frozen output contract                        │
│                                                                                │
│  Ingestion pipeline (separate CLI, staged intermediate outputs):               │
│    PDF → PyMuPDF parse → location-aware chunking → deterministic reference    │
│    extraction → LLM-assisted dependency extraction → resolver → review gate   │
│    → embedding → Content-Owner approval → active corpus                       │
└──────────┬──────────────────────────────┬─────────────────────────────────────┘
           │                              │
   PostgreSQL 16 + pgvector        OpenRouter (chat) + embeddings
   sources · source_versions ·     endpoint (via adapter; provider
   source_relationships · chunks · chosen in Phase 0a spike)
   chunk_edges · glossary · entities
```

**Design principles:**

1. **Deterministic core, LLM edges.** Status resolution, point-in-time filtering, and citation verification are pure code, exhaustively unit-tested. The LLM only synthesizes prose and assists conflict detection. Nothing correctness-critical depends on the LLM.
2. **The no-fabrication gate is mechanical.** Every passage and quote in the response is checked verbatim (whitespace-normalized) against a retrieved chunk before the response is returned; failure → citation dropped or loud failure in dev, never silent.
3. **Swappable inference.** All LLM/embedding calls go through a thin provider adapter (OpenRouter now; one-file swap later).
4. **Location-based chunking, not token windows.** Chunks are paragraphs, template rows and definitions with stable citation-grade location IDs (`PS17/23 · SA-2.4`, `CRR007 · row 0110`). No sliding-window overlap — duplicate citations would pollute verification. Chunk text is stored verbatim: it is the verification ground truth.
5. **Three-tier relationship model** (dependency-aware retrieval, per the graph-based retrieval research):
   - **Tier A — document level:** `SUPERSEDES` / `AMENDS` / `REFERENCES` edges between source versions (DI-3; drives the status resolver).
   - **Tier B — intra-document:** `REFERENCES` / `DEPENDS_ON` / `CONTINUES` / `QUALIFIES` edges between chunks. Regulatory cross-references are mostly explicit and patterned, so a **deterministic regex/rule pass resolves the majority**; an LLM pass (temperature 0, JSON output, validated) catches implicit references; unresolved targets go to a **Content-Owner review queue**, never silently dropped.
   - **Tier C — semantic/structural:** `REPORTS_AGAINST` (rule ↔ template row), `DEFINES` (row ↔ glossary), extracted entities. `QUALIFIES` edges are always followed during expansion — this is how qualifications/exceptions are preserved (product rule 6).
6. **Point-in-time discipline extends to graph expansion.** Every chunk pulled in via graph traversal must itself pass the `published_date ≤ asOfDate` filter — a superseding document's text must never leak into a historical as-of answer. *(An invariant the source research does not have; our corpus makes it mandatory.)*
7. **Confidence scores live only in the ingestion layer** — used for context-assembly ordering and review triage; never rendered (product rule 1).

**Status resolution rules table** (pure function `(version metadata, relationship graph, asOfDate) → {status, statusDate}`):

| Condition evaluated against asOfDate | Status |
|---|---|
| `effective_from ≤ asOf` and no later superseding/amending version in force at asOf | `Final/Operative` |
| `published ≤ asOf` and `effective_from > asOf` | `Future-Effective` |
| A superseding relationship's target is (or became) effective before asOf | `Superseded/Historical` (statusDate = superseder's effective_from) |
| Consultation (CP) document with no PS relationship recorded | `Proposed/Consultation` (statusDate = published_date) |
| Explanatory/supporting document types | `Explanatory/Supporting` (statusDate = published_date) |

Key proven property: the same source renders differently on different as-of dates (CP16/22 = `Proposed/Consultation` at as-of 2022-12-01; `Superseded/Historical` today) — **no retro-application of later determinations**.

---
### 5.2 Key use cases (the five acceptance scenarios)

Each prototype scenario is a concrete acceptance specification for the pipeline:

| # | Question / as-of | Required backend behaviour | Required output | What it proves |
|---|---|---|---|---|
| 1 | Retail exposures under the standardised approach; as-of today | Retrieve across three authority levels: PS17/23 ¶ SA-2.4 (near-final, 75%), PS1/26 § 2.11 (final, 45% qualifying residential), explanatory overview. No conflict. Synthesis contrasts the rule statements and notes differing authority levels. | 3–4 evidence-led paragraphs; citations: PS17/23 `Future-Effective` (eff. 1 Jan 2027), PS1/26 `Future-Effective`, overview `Explanatory/Supporting`; context views carry the 90-days-past-due / EUR 1m and LTV > 80% exceptions. | Multi-status badges; authority-level contrast; exception preservation |
| 2 | Output floor phase-in timetable; as-of today | Retrieve CP16/22 ¶ 4.12 (proposed 50% start, phased to 72.5% by 2030) alongside PS1/26 ¶ OF-1.2 (72.5% from 1 Jan 2027, no phase-in). **Conflict detection required.** Do not resolve; do not rank as a proxy for choosing. | Divergence flagged in answer; red conflict callout; side-by-side (CP16/22 `Superseded/Historical` at today's as-of vs PS1/26 `Future-Effective`); warning; **Escalate** button. | Conflict detection; side-by-side rendering; escalation path |
| 3 | Which template rows capture the output floor; as-of today | Row/instruction-granularity retrieval: CRR007 rows 0110 (total RWA after floor), 0120 (RWA subject to floor), 0130 (floor ratio), instruction CRR007-INS2, from PS1/26 (final) and PS9/24 (near-final). Supply dependent definitions. | Citations located at `template CRR007, rows 0110–0130`; row meanings quoted verbatim with the "blank where standardised-only" exception preserved; definition links expand inline. | Row-level citations; definitions linkage; near-final vs final comparison |
| 4 | What was proposed in the original consultation; **as-of 2022-12-01** | **Point-in-time retrieval**: only sources published on/before the as-of date may appear (CP16/22 only, as `Proposed/Consultation`). The 2026 explanatory overview must NOT appear as contemporaneous; if included at all, statused `Explanatory/Supporting` with visibly later published date. | CP16/22 cited as `Proposed/Consultation` (published 27 Nov 2022) — NOT `Superseded/Historical`, because supersession happened after the as-of date. | As-of-driven status computation; no retro-application |
| 5 | ISAv permission application deadline; as-of today | Retrieve PS9/24 ¶ 5.4 (31 Dec 2026 deadline, near-final) vs PS1/26 ¶ ISA-3.1 (deadline "to be specified", final) and CP9/26 ¶ 2.8 (proposes confirming 31 Dec 2026). Conflict = concrete date vs deferred date across authority levels. | Conflict callout + side-by-side (both `Future-Effective` with their own statusDates); CP9/26 cited `Proposed/Consultation` with "do not rely" qualification; escalation modal pre-filled with conflict headline + both source ids + question. | Conflict between two future-effective sources (status alone cannot disambiguate); three-way authority layering; escalation end-to-end |

---
### 5.3 Trade-offs and open decisions (for stakeholder vetting)

| Decision | Chosen | Alternative rejected | Rationale / risk |
|---|---|---|---|
| Backend language | **Python end-to-end** (FastAPI + PyMuPDF) | Node/TypeScript end-to-end; Python-ingest + Node-API split | Parsing (the biggest quality risk) gets the strongest toolset; frontend is a frozen static HTML file so there is zero UI cost; LLM/eval tooling is Python-native. Risk: none material identified. |
| PDF parsing library | **PyMuPDF** (primary); pdfplumber as occasional cross-check | pdfjs-dist native Node pass | PyMuPDF is the strongest parser (native speed, per-character geometry, table detection). Note: **AGPL licence** — acceptable for internal, non-distributed tooling per working assumption; **compliance confirmation pending before Phase 0a completes**. |
| Relationship storage | **Postgres edge table + recursive CTEs**, behind a swappable graph interface | Neo4j alongside Postgres | One store, no second runtime or sync problem; at ≤ ~1,500 pages / ~10k edges, 1–2 hop traversals are milliseconds. Neo4j remains a drop-in swap if V2 scale or STUB-3 impact tracing demands it. |
| Synthesis style | **Fresh generation with citations**, mechanically verbatim-verified | Extractive passage stitching | Better answer quality per backlog (evidence-led phrasing, authority contrast); fabrication risk mitigated by the verification gate rather than by restricting generation. Trade-off consciously taken. |
| Conflict detection | **LLM-assisted, structured output, deterministically validated**; rule-based candidates may be added and compared | Fully deterministic first | Acknowledged experiment ("explore to see which gives better results"); results compared on the 5-scenario suite. |
| Chunking | **Location-based** (paragraph/row/definition), no overlap | Token-window with overlap | Citation-grade locations and verbatim verification require it; overlap would create duplicate citations. Revisit only if retrieval recall disappoints. |
| RAG framework | **Libraries only** (PyMuPDF, pgvector, OpenAI-compatible SDK) | LangChain / LlamaIndex orchestration | Pipeline is deliberately non-generic (location chunking, deterministic reference extraction, status resolver, verification gate, no-scores invariant); framework abstractions would fight these. |
| Embedding provider | **Open** — chosen in Phase 0a spike (OpenAI text-embedding-3-small vs local BGE-class) | — | OpenRouter's embedding support is limited; adapter keeps it swappable. |
| Auth / hosting | **Local dev only for V1**, no SSO | Shared/pilot deployment | Explicit V1 scope decision; **must be revisited before any deployment beyond local**. |
| Deferred scope | STUB-1–5; newer-analyst mode; refresh SLA | Building them in V1 | Conscious exclusions per epic and breakdown; STUB-1 gated on open question Q10. |

### 5.4 Enablers / MVP sequencing

Build order is fixed: **VF0 → VF1 → VF2 → VF3 → VF4**, mapped to delivery phases 0a → 4 (see companion task breakdown `2026-10-03_user-story-tasks-regcopilot-v1.md`). Phase 0a contains two de-risking spikes before commitment: (1) real-PDF section-map extraction rate via PyMuPDF; (2) CRR template-table row extraction. Phase 0b measures dependency-extraction precision against a hand-labelled ~20-section sample before LLM extraction is trusted in the pipeline.

---
## 6. Tests

### 6.1 Verification — build criteria (we can prove the build works)

**The five-scenario integration suite** (§5.2) is the primary acceptance test: each scenario asserts its required output — badge set per as-of date, side-by-side conflict for scenario 2, row-level locations + populated definitions for scenario 3, the 2022 point-in-time flip for scenario 4, escalation pre-fill for scenario 5. Screenshot-diff against the prototype: all five scenarios must produce identical UI states from API data as from mocks.

**The §8 integration checklist from the prototype integration spec, verbatim:**

- [ ] All five scenarios produce identical UI states from API data as from mocks (screenshot diff against the prototype).
- [ ] Every citation has a status badge (one of exactly five) AND a status date — no citation renders without both.
- [ ] Changing as-of date to 2022-12-01 flips CP16/22 from `Superseded/Historical` to `Proposed/Consultation`.
- [ ] Conflict responses always include both sides + warning + escalation button; no response ever resolves a conflict silently.
- [ ] Every answer's first sentence is evidence-led ("The relevant sources indicate…"); a synthesis asserting "the applicable requirement is…" is a build failure.
- [ ] No confidence scores, ratings, or rankings are rendered anywhere in the UI.
- [ ] Reporting questions return row/instruction-level locations and populate every `definitions` key referenced.
- [ ] Context passages retain qualifications/exceptions (purple `qual` segments) — spot-check scenario 1 (90-day exception) and scenario 5 (transitional-arrangements exception).
- [ ] As-of date with no relevant sources → neutral empty state, no fabricated answer.
- [ ] HTML injection: passage/text fields are sanitized server-side; `hl`/`qual` are the only allowed inline tags.

**Unit / component test sets:**

- **Status resolver matrix** (highest-value suite): the §5.1 rules table × as-of-date boundaries — every rule, supersession timing cases, no-retro-application cases, all five statuses derivable and nothing else.
- **Verbatim verification gate:** fabricated spans, paraphrased quotes, and whitespace variants — all rejected or repaired before response.
- **Sanitizer:** only `hl`/`qual` inline tags survive; all other HTML stripped; hostile-input cases.
- **Schema validation:** Pydantic models for the frozen output contract; LLM outputs validated, retried once on non-conformance, then loud failure.
- **Retrieval filters:** `published_date ≤ asOfDate` and `approval_state = 'active'` enforced on primary results *and* graph-expanded context.
- **Ingestion QA:** unique location IDs; every chunk non-empty with resolvable parent; every `definition_refs` key resolves to glossary; reference edges resolve or sit in the review queue; supersession chains acyclic and consistent with effective-date ranges.
- **Determinism harness:** LLM-dependent assertions run in golden-file ("recorded") mode so CI is deterministic; live-LLM runs are a separate manual gate.

**Ingestion quality gates (Phase 0b):** dependency-extraction precision measured on a hand-labelled ~20-section sample from real PDFs, before LLM extraction is trusted; random-chunk HTML render spot-checks against PDF pages.

---
### 6.2 Validation — epic success criteria (the hypothesis, tested with real analysts)

Within 6 weeks of experiments starting, the hypothesis is valid if:

- Time to a verified, evidence-backed answer reduced vs. the manual baseline on comparable questions (quantitative; target % set once the baseline exists — manual baseline is a required first experiment, not a build item).
- **0 fabricated citations/quotations across the difficult-case set — hard gate; one failure fails the experiment** (citation-integrity problem).
- Citation correctness and completeness ≥ threshold agreed with SMEs on the difficult-case set (quantitative).
- ≥ 8 of 10 answers judged faster to verify than the analyst's own assembly (qualitative; both analysts + one SME).
- Refusal/insufficient-evidence outcomes accepted as appropriate by both analysts (qualitative — the A3 test, exercised via S4.2/S4.3).
- Both analysts state they would use the system for real recurring questions (qualitative — the A1 behavioural test).

**Kill/pivot signals** (from the epic): analysts report the tool *adds* verification overhead → pivot the provenance/UX layer; difficult-case citation correctness below threshold after iteration → pause build, fix retrieval/provenance; concierge shows the workflow itself does not save time → re-examine the problem framing.

**Instrumentation (dissolved F6/S6.2, attached to every feature):** capture time-to-answer, sources/citations used, and outcome type (answer/refusal/escalation) for the flows each feature introduces; track refusal/escalation appropriateness (feeds the A3 test and open question Q8).

---

## Provenance

- Epic: `2025-06-18_epic-hypothesis-regcopilot-v1.md` · Features: `2025-06-18_epic-feature-breakdown-v3.md` · Stories: `2025-06-18_user-story-backlog-v2.md`
- UI/UX contract: `regcopilot-prototype-integration-spec.md` + `regcopilot-prototype.html` (frozen)
- Technical decisions (discussed and agreed with the team, 2026-10): Python/FastAPI end-to-end; PyMuPDF; Postgres+pgvector edge-table graph with recursive CTEs; OpenRouter behind a swappable adapter; fresh-generation synthesis with mechanical verbatim verification; LLM-assisted conflict detection (experimental); local dev only; phased build VF0→VF4.
- Dependency-aware retrieval approach informed by: "Dependency-Aware Document Retrieval: Revolutionizing RAG with Graph Databases" (A. Mishra, 2025) — adapted with our point-in-time and no-confidence-score invariants.
