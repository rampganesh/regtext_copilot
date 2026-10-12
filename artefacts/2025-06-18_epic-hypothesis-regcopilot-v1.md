# Epic Hypothesis: Basel 3.1 Regulatory Research Copilot - V1

Framed per `skills/epic-hypothesis` (template + examples read). Grounded in wiki evidence: decisions and problems cited inline; every claim traceable per the evidence-chain rule.

## If/Then Hypothesis

**If we** provide an evidence-led research assistant that finds, connects and explains authoritative UK capital regulatory evidence - with precise inspectable citations, visible source status and effective dates, and explicit uncertainty/conflict signalling
**for** experienced regulatory reporting analysts on the UK capital reporting team preparing for Basel 3.1 (secondary beneficiary: newer analysts learning the research path)
**Then we will** materially reduce the time required to produce a verified, evidence-backed answer **without** reducing evidence quality or increasing unsafe answers

*(North-star outcome per decision `wiki/decisions/2025-06-04_v1-balanced-scorecard.md`. Scope bounded by decision `wiki/decisions/2025-06-04_v1-scope-evidence-led-research.md`.)*

## Sub-hypotheses (each independently testable; user stories come later)

### SH1 - Evidence discovery & connection
**If** analysts can ask questions in natural language and receive the genuinely relevant authoritative sources plus related material (definitions, reporting instructions, related changes), **then** they will locate the right starting evidence faster and with fewer dead ends.
*Grounded in:* V1 scope decision; `wiki/problems/terminology-cross-referencing.md`; persona `experienced-analyst` ("jumps directly to likely sources").

### SH2 - Provenance & citations
**If** every answer carries provenance meeting the minimum standard (source + document/version/status + precise location, including tables/rows/fields/template references for reporting questions), **then** analysts will verify answers faster and extend per-answer trust to the tool.
*Grounded in:* decision `2025-06-04_minimum-provenance-standard`; `wiki/problems/citation-integrity.md` (confirmed); assumption A2 (validated, correlational).

### SH3 - Temporal & status awareness
**If** the system always shows source status (final/operative, future-effective, superseded/historical, proposed/consultation, explanatory/supporting) on an explicit as-of-date basis, **then** analysts will stop reaching operationally wrong answers built from technically correct sources.
*Grounded in:* decisions `2025-06-04_date-based-temporal-mode` and `2025-06-04_status-authority-labelling-ux`; `wiki/problems/source-validation-burden.md` (confirmed, 7 mentions); desk research timeline (CP16/22 -> PS1/26 -> CP9/26).

### SH4 - Conflict & uncertainty handling
**If** the system exposes conflicts, states insufficient evidence explicitly, and supports evidence-backed escalation, **then** refusal/escalation outcomes will be accepted as useful rather than seen as product failure - and trusted.
*Grounded in:* `wiki/problems/conflict-exposure.md` (confirmed); `wiki/problems/requirement-applicability-determination.md` (confirmed); **assumption A3 - still untested; this epic is its test**.

### SH5 - Corpus governance & staleness
**If** the corpus is curated under Content-Owner governance with an explicit staleness process (flag and link affected prior answers, preserve historical context), **then** analysts will rely on it as current without re-validating every answer manually.
*Grounded in:* decisions `2025-06-04_bounded-curated-corpus` and `2025-06-14_corpus-update-and-staleness-policy`; `wiki/problems/no-feedback-loop.md` (confirmed); Q10 residual risk (staleness window/threshold open).

## Tiny Acts of Discovery Experiments

*(Approach not yet decided by the team - both candidates run as open experiments; validation results decide which gates the build.)*

1. **Manual baseline first** (required by the scorecard decision): observe and time 5-10 real recent regulatory questions end-to-end, capturing the current effort split (search vs. validation vs. evidence assembly vs. presentation).
2. **Concierge / Wizard-of-Oz**: a researcher performs the intended workflow (search -> status-checked sources -> minimum-standard provenance -> uncertainty flags) for 5-10 real current questions, delivering answers in the intended UX format - measures the *workflow's* value with zero build.
3. **Thin prototype pilot**: minimal retrieval + citation UX evaluated against the SME's difficult historical questions - most-obvious-document-not-correct, current/future coexistence, superseded sources, similar terminology, insufficient-evidence cases (per Meeting 2 L133-137 and both analyst interviews, which converged on this list).
4. **A3 probe embedded in both**: present refusal/insufficient-evidence outcomes alongside substantive answers; observe whether trust rises or perceived usefulness falls.

## Validation Measures

**We know our hypothesis is valid if within 6 weeks of experiments starting** we observe:

- Time to a verified, evidence-backed answer reduced vs. baseline on comparable questions (quantitative; target % to be set once the manual baseline exists).
- **0 fabricated citations/quotations** across the difficult-case set (hard gate - one failure fails the experiment, per `wiki/problems/citation-integrity.md`).
- Citation correctness and completeness >= threshold agreed with SMEs on the difficult-case set (quantitative).
- >=8 of 10 answers judged faster to verify than the analyst's own assembly (qualitative; both analysts + one SME).
- Refusal/insufficient-evidence outcomes accepted as appropriate by both analysts (qualitative - the A3 test).
- Both analysts state they would use the system for real recurring questions (qualitative - the A1 behavioural test).

## Invalidation conditions (kill/pivot signals)

- Analysts report the tool **adds** verification overhead instead of removing it -> pivot the provenance/UX layer, not the core problem.
- Difficult-case citation correctness below threshold after iteration -> pause build; fix retrieval/provenance layer before continuing.
- Concierge shows the workflow itself does not save time -> the problem framing needs re-examination (this is a reversal condition on decision `2025-06-04_v1-scope-evidence-led-research`).

## Provenance

- Framing: `skills/epic-hypothesis` (Lean UX if/then hypothesis format).
- Evidence: `wiki/overview.md`, `wiki/decisions/` (8 active decisions), `wiki/problems/` (10 pages), `wiki/assumptions.md` (A1/A2 validated-correlational, A3 untested), `wiki/personas/` (experienced-analyst evidence-chained; newer-analyst second-hand).
- Drafted 2025-06-18; user stories intentionally deferred - epics are broad by design.
