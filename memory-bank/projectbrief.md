# Project Brief — RegCopilot V1

## What this is
**RegCopilot** is an evidence-led Retrieval-Augmented Generation (RAG) research assistant over a
bounded, Content-Owner-gated corpus of UK Basel 3.1 capital regulatory material. It is built for
experienced regulatory reporting analysts on the UK capital reporting team who are preparing for
Basel 3.1 (secondary beneficiary: newer analysts learning the research path).

## Core problem
Producing a *verified*, evidence-backed answer to a Basel 3.1 regulatory question is slow because
analysts must find, status-check (current vs future vs superseded), cross-reference, and assemble
evidence manually. A "correct" answer built from the wrong document version is a real, observed
failure mode. The corpus is in a live transition period, so current/future and proposed/final
requirements coexist.

## The value hypothesis (epic)
**If we** provide an evidence-led research assistant that finds, connects and explains authoritative
UK capital regulatory evidence — with precise inspectable citations, visible source status and
effective dates, and explicit uncertainty/conflict signalling —
**for** experienced regulatory reporting analysts preparing for Basel 3.1,
**then we will** materially reduce the time required to produce a verified, evidence-backed answer
**without** reducing evidence quality or increasing unsafe answers.

## The defining differentiator
Correctness and trustworthiness are enforced by **deterministic systems, not model confidence**:
- Every citation, quotation and passage is **mechanically verified verbatim** against source text
  before it reaches the analyst (**hard gate: zero fabricated citations**).
- Source status is computed by a **pure, unit-tested rules function** relative to an analyst-chosen
  **as-of date** — the system never infers "latest = applicable".
- Conflicts between sources are surfaced **side-by-side and never silently resolved**; escalation to
  a human SME is the only resolution path.

## Five capabilities (each an independently testable sub-hypothesis)
1. **Evidence discovery & connection** (SH1) — NL questions return genuinely relevant authoritative
   sources plus related material.
2. **Provenance & citations** (SH2) — every answer carries source + document/version/status + precise
   location, including tables/rows/fields for reporting questions.
3. **Temporal & status awareness** (SH3) — five-label status taxonomy always shown on an explicit
   as-of-date basis.
4. **Conflict & uncertainty handling** (SH4) — conflicts exposed; insufficient evidence stated;
   evidence-backed escalation supported (tests the untested assumption A3).
5. **Corpus governance & staleness readiness** (SH5) — bounded curated corpus under Content-Owner
   governance, with amendment intake and version retention designed in from day one.

## Scope (V1)
- **In scope:** the vertical feature slices VF0 → VF1 → VF2 → VF3 → VF4 (see `systemPatterns.md`).
- **Local development only** for V1; no authentication/SSO.
- **Deferred (explicit):** STUB-1 stale-answer marking (gated on open question Q10), STUB-2 answer
  audit store, STUB-3 impact-tracing capture, STUB-4 newer-analyst learning path (needs a direct
  interview), STUB-5 structured feedback categories, auth/SSO, shared hosting, refresh SLA.

## Success criteria (epic validation — tested with real analysts)
Within 6 weeks of experiments starting, the hypothesis is valid if:
- Time to a verified, evidence-backed answer is reduced vs. the manual baseline (target % set once
  the baseline exists — the manual baseline is a required first experiment, not a build item).
- **0 fabricated citations/quotations across the difficult-case set — HARD GATE; one failure fails
  the experiment.**
- Citation correctness and completeness ≥ threshold agreed with SMEs on the difficult-case set.
- ≥ 8 of 10 answers judged faster to verify than the analyst's own assembly.
- Refusal/insufficient-evidence outcomes accepted as appropriate by both analysts (the A3 test).
- Both analysts state they would use the system for real recurring questions (the A1 test).

## Kill / pivot signals
- Analysts report the tool *adds* verification overhead → pivot the provenance/UX layer.
- Difficult-case citation correctness below threshold after iteration → pause build, fix
  retrieval/provenance.
- Concierge shows the workflow itself does not save time → re-examine the problem framing.

## Source artefacts (ground truth lives in `../artefacts/`)
- Epic: `2025-06-18_epic-hypothesis-regcopilot-v1.md`
- Features: `2025-06-18_epic-feature-breakdown-v3.md` (supersedes v2)
- Stories: `2025-06-18_user-story-backlog-v2.md` (supersedes v1)
- Tasks: `2026-10-03_user-story-tasks-regcopilot-v1.md`
- Solution intent: `2026-10-03_solution-intent-regcopilot-v1.md`
- UI/API contract: `regcopilot-prototype-integration-spec.md` + `regcopilot-prototype.html` (frozen)
- Prior versions are retained unchanged for audit.
