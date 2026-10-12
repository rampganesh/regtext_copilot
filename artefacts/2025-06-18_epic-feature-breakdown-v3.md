# Epic Feature Breakdown - v3 (vertical reorganization)

Supersedes `2025-06-18_epic-feature-breakdown-v2.md` (retained unchanged for audit). Parent epic unchanged: `2025-06-18_epic-hypothesis-regcopilot-v1.md`.

## Reorganization rationale

The v2 features were horizontal layers: F2/F3/F4 all sat on top of F1's retrieval and could not be delivered independently. This v3 applies the Humanizing Work workflow-steps pattern correctly: **VF1 delivers the complete analyst workflow in its simplest form (the copilot's basic functionality)**; VF2-VF4 each add a step or variation to that same workflow and are independently valuable and releasable. **VF0 is the foundational data feature** (PM direction): priority-0, builds the initial corpus database before other features.

**Build order: VF0 -> VF1 -> VF2 -> VF3 -> VF4.** Dependencies that remain (VF2-VF4 build on VF1) are the intended Humanizing Work kind - each feature delivers the full workflow with increasing sophistication, never a blocked half-layer.

---

## VF0 - Document & corpus foundation (priority-0; prerequisite for all)

Creates the initial corpus database. Ownership split per the bounded-corpus decision: the Regulatory Content Owner governs inclusion, status and relationships; Technology owns ingestion and indexing. Stories are Cohn gists - deliberately high-level to initiate database-design discussions (full gists in `2025-06-18_user-story-backlog-v2.md`).

- **DI-1 Curated corpus loading (Content-Owner gated)** - load only approved UK capital/Basel 3.1 material (Rulebook, policy/supervisory statements, reporting instructions/templates); nothing enters the active corpus without Content Owner confirmation. Enables VF1. (bounded-corpus decision row 5)
- **DI-2 Source metadata capture** - every source stored with publication date, effective date, document type, subject area and version/status (five-label taxonomy). Enables S2.1, S2.3, S3.1; satisfies the corpus-metadata dependency flagged on S2.2 in v2. (row 5; labelling decision)
- **DI-3 Relationships and versioning** - record supersession/amendment/reference relationships; version templates and instructions alongside their rules. Enables VF2 (S2.2). (Data/Reporting SME, Meeting 2 L115; staleness decision L7)
- **DI-4 Structured content ingestion** - ingest tables, templates, rows/fields and instructions as structured addressable content including links to dependent definitions. Enables S3.2, S1.2, S1.3. (non-prose problem; provenance decision row 4)
- **DI-5 Amendment intake and validation gate** - Technology detects and flags new/changed material; Content Owner validates authority, status, effective date, relationships before activation. Precursor to STUB-1 (stale marking) and STUB-3 (impact tracing). (staleness decision L6-7, L12)
- **DI-6 Version retention for audit** - retain historical source versions with effective-date ranges, so answers could later be checked against material current at the time. Precursor to STUB-1/2/3. (Meeting 3 L9, L91-93; Q10)

---

## VF1 - Core Copilot: ask, answer, verify (the basic functionality)

The walking skeleton: one question in -> one verified, evidence-led answer out. Simplest complete case: textual question, clear final/operative sources, no conflicts.
- **S1.1** Natural-language search with regulatory-relevance ranking (+ F1-TAD ranking spike) - from v2 F1
- **S2.1** Status badges + effective dates on results and answers - from v2 F2
- **S2.3** Evidence-led answer phrasing - from v2 F2 (kept in core per PM confirmation; phrasing is how answers avoid overstating authority)
- **S3.1** Verifiable prose citations (document, version/status, section/paragraph) - from v2 F3
- **S3.3** Surrounding-context navigation from a citation (the verify step) - from v2 F3 (kept in core per PM confirmation)

## VF2 - Temporal navigation (adds the as-of-date dimension)

The workflow extended to transition-period questions.
- **S2.2** As-of-date answers (current vs future vs superseded) - from v2 F2. Covers difficult scenarios (a) most-obvious-document-not-correct and (b) current/future coexistence.

## VF3 - Reporting-material connection (data variation: structured sources)

The workflow extended to reporting questions where no prose paragraph carries the answer.
- **S3.2** Structured citations (template/table/row/field + dependent definitions) - from v2 F3
- **S1.2** Forward navigation: rule -> reporting representation - from v2 F1
- **S1.3** Backward navigation: reporting field -> underlying requirement - from v2 F1
- **S1.4** Related-material surfacing - from v2 F1. Covers difficult scenario (c) citation resolves to a table/row/field.

## VF4 - Safe answers (edge states)
- **S4.1** Conflict exposure (side-by-side, never silently resolved) - from v2 F4
- **S4.2** Insufficient-evidence statement - from v2 F4
- **S4.3** Evidence-backed escalation package (A3 test vehicle) - from v2 F4. Covers difficult scenarios (d) conflicting sources and (e) insufficient evidence.

---

## Dissolved: F6 (evaluation signals)

Per PM rule, F6 was fully dependent on every other feature and is no longer a standalone feature. Its requirement (S6.2) becomes an **instrumentation task attached to every feature**: "For the flows this feature introduces, capture time-to-answer, sources/citations used, and outcome type (answer/refusal/escalation)" (scorecard decision row 3). The manual-baseline research note is unchanged (not a story).

## Unchanged from v2

- Invariants (no fabrication; five status labels; evidence-led language; no confidence scores; analyst remains responsible) - global across all features
- Deferred stubs STUB-1 to STUB-5 (now annotated with VF0 precursor links: STUB-1/2/3 build on DI-5/DI-6)
- Conscious exclusions (autonomous applicability; corpus governance operations; newer-analyst teaching mode; refresh SLA)

## v2 -> v3 mapping

| v2 | v3 |
|---|---|
| F1 S1.1, F1-TAD | VF1 |
| F1 S1.2, S1.3, S1.4 | VF3 |
| F2 S2.1, S2.3 | VF1 |
| F2 S2.2 | VF2 |
| F3 S3.1, S3.3 | VF1 |
| F3 S3.2 | VF3 |
| F4 S4.1-S4.3 | VF4 |
| F5 (deferred) | Deferred stubs STUB-1/2/3 (unchanged) |
| F6 / S6.2 | Dissolved - per-feature instrumentation tasks; manual baseline stays a research note |
| STUB-4, STUB-5 | Unchanged |
| (new) | VF0 DI-1 to DI-6 (Cohn gists; priority-0) |

## Coverage statement

All 10 problem pages, all 8 active decisions, all 3 assumptions and the Q8/Q10 linkages remain covered; nothing from v2 was dropped - only re-filed, with F6 dissolved into tasks and VF0 added as the foundational prerequisite. Full per-item detail in `2025-06-18_user-story-backlog-v2.md`.

## Provenance

Reorganized per `skills/epic-breakdown-advisor` Humanizing Work workflow-steps pattern (core + added steps, vertical slices); VF0 added per PM direction. Ground truth: wiki decisions, problems, assumptions, open questions, personas as cited per story in the backlog v2.
