# Epic Feature Breakdown — v2 (revised per epic-breakdown-advisor test)

Revised from `Epic breakdown.md` after applying `skills/epic-breakdown-advisor` (Humanizing Work methodology) to the original five features. Every change traces to a wiki decision, problem page, or source line; the test findings are summarised inline per feature.

Parent epic: `2025-06-18_epic-hypothesis-regcopilot-v1.md`. User stories deliberately deferred — this document fixes **feature split and scope only**.

## Sequencing and dependency note

F2, F3 and F4 are quality layers on F1; the first valuable slice is **one question answered end-to-end spanning F1 + minimal F2 + minimal F3** (vertical slice, per the Humanizing Work principle). Features are independently *testable*, but the first slice is cross-feature. Recommended order: **F1 → F3 → F2 → F4 → F6; F5 deferred beyond V1.**

---

## F1 — Evidence search & connection (core, build first)

**Scope:**
- Natural-language search over the curated corpus (corpus per decision `2025-06-04_bounded-curated-corpus`; NL querying per decision `2025-06-04_v1-scope-evidence-led-research`)
- Results ranked by **regulatory relevance, not merely semantic similarity** — the first plausible result is never presented as the applicable provision (source: 2025_05_26_meeting_followup.md, L45-47)
- Bidirectional navigation: rule → reporting representation, and reporting field/template → underlying requirement; no assumed single starting point (source: 2025_05_26_meeting_followup.md, L63-65)
- Cross-referencing surfacing: definitions, related instructions, relevant changes — without overwhelming the user (source: 2025_06_17_interview_analyst1exp.md, L140)

**Changes from original 2.1:** added the semantic-similarity guard (test finding; was absent). Everything else retained.

---

## F2 — Status & temporal awareness (merged from original 2.2 — one capability, not three stories)

**Scope:**
- Every search result **and answer** displays source status (final/operative, future-effective, superseded/historical, proposed/consultation, explanatory/supporting) and effective date — visible in both search and answers (decision `2025-06-04_status-authority-labelling-ux`; decision `2025-06-04_date-based-temporal-mode`)
- Answers operate on an explicit **as-of-date basis**; publication date is never treated as applicability; "latest" is never a label
- Evidence-led language conventions enforced: "The relevant sources indicate…", "The cited PRA material states…"; **"The applicable requirement is…" reserved for validated applicability** (digest row 7) — this is the concrete expression of "never overstate authority" and carries the applicability boundary from `wiki/problems/requirement-applicability-determination.md`

**Changes from original 2.2:** 2.2.1/2.2.2/2.2.3 failed the INVEST Independence check (three facets of one capability) and are merged; adds search-side visibility and the language conventions (both were missing).

---

## F3 — Citations & provenance (original 2.4, scope aligned to the decision)

**Scope:**
- Provenance per the **full minimum standard** (decision `2025-06-04_minimum-provenance-standard`): source + document/version/status + precise location — section/paragraph for prose, and **table/row/field/instruction/template references for reporting questions** (closes the `wiki/problems/non-prose-regulatory-content.md` gap; source: 2025_06_18_interview_analyst2prov.md, L63-71)
- Excerpts **preserve the qualifications/exceptions needed to validate the claim** without forcing the analyst to re-search the document (source: 2025_05_26_meeting_followup.md, L57-59 — replaces the original "answer in entirety" wording, which conflicts with the context-vs-cumbersomeness trade-off)
- **"Never fabricate citations or quotations" is an invariant acceptance criterion on every story across F1–F4** — not a standalone story (fails INVEST Valuable alone); it is already the hard gate in the epic's validation measures

**Changes from original 2.4:** 2.4.1 aligned to the full standard (was narrower); 2.4.2 converted from story to invariant criterion; 2.4.3 reworded.

---

## F4 — Conflicts, uncertainty & escalation (original 2.3, plus escalation)

**Scope:**
- Present conflicting sources side-by-side, never silently resolved; conflict exposure as the first requirement (source: 2025_05_26_meeting_followup.md, L67)
- Explicit insufficient-evidence signalling ("I don't have sufficient evidence to answer this" is an acceptable outcome — digest row 1; source: 2025_05_26_meeting_followup.md, L77)
- **Evidence-backed escalation output**: assemble a well-bounded question + the assembled evidence package for SME review — the escalation pattern both analysts described as the accepted form (source: 2025_06_17_interview_analyst1exp.md, L78-82; source: 2025_06_18_interview_analyst2prov.md, L83-87). This is also the vehicle for testing assumption A3 (still untested).

**Changes from original 2.3:** added the escalation outcome (was missing).

---

## F5 — Answer history & staleness — DEFERRED BEYOND V1 (original 2.5, corrected scope)

**Scope as it would be built (decision-conformant):**
- Store answers with **full audit context**: question, answer, citations, evidence versions used, and temporal context (source: 2025_06_14_meeting_latedocuments.md, L9, L91-93)
- Stale flagging: affected answers flagged and **linked to the updated source/version**; historical answers preserved unmodified, never auto-rewritten (source: 2025_06_14_meeting_latedocuments.md, L8-9)
- Impact-tracing fields recorded at capture time (recipient, basis version) enabling later blast-radius analysis (source: 2025_06_17_interview_analyst1exp.md, L88-93; source: 2025_06_18_interview_analyst2prov.md, L91-96)

**Explicitly NOT in scope, per decisions:**
- Retrieval of past answers as an authoritative knowledge source (deferred — digest row 1)
- Retention of final answers for reuse (retention/ownership/reliance considerations not assumed in initial design — source: 2025_05_26_meeting_followup.md, L151)
- Auto-rewriting historical answers

**Status: NOT PRIORITIZED FOR V1** (PM direction). Revisit once Q10 (staleness window/threshold; proactive re-review vs. flag-on-use) is resolved.

---

## F6 — Evaluation signals (new — closes the ignored scorecard decision)

**Scope:**
- Capture the scorecard decision's measures on real usage: time-to-answer, citation correctness sampling, refusal/escalation occurrences, unsupported-answer rate, usage/repeat-usage (decision `2025-06-04_v1-balanced-scorecard`)
- Support the **manual baseline** capture the scorecard decision requires before experiments

**Rationale:** the epic's validation measures are untestable without this; it was the largest ignored decision in the test.

---

## Conscious exclusions (stated, not oversights)

1. **Autonomous applicability determination** — out of V1 (decision `2025-06-04_v1-scope-evidence-led-research`)
2. **Corpus governance/ingestion operations** — Content Owner + Technology process per decision `2025-06-04_bounded-curated-corpus`; operational workstream, not a product feature
3. **Newer-analyst teaching mode** — persona evidence is second-hand; revisit after a direct newer-analyst interview
4. **Refresh SLA/frequency** — explicitly out of system scope (decision `2025-06-14_corpus-update-and-staleness-policy`)

## Coverage statement (problems and decisions)

- **Problems:** all 10 problem pages are covered — the 6 confirmed problems map to F1–F5; `experience-dependency` covered by exclusion statement (3) and the epic's secondary beneficiary; `terminology-cross-referencing` and `non-prose-regulatory-content` covered by F1/F3.
- **Decisions:** all 8 active decisions are covered — v1 scope (epic), scorecard (F6), provenance (F3), labelling + temporal mode (F2), bounded corpus + staleness (F5 scope / exclusion 2), temporal awareness (F2), corpus update process (F5 scope + exclusion 4).

## Provenance

- Test method: `skills/epic-breakdown-advisor` (INVEST pre-split check, 9-pattern flowchart, split evaluation) applied to `Epic breakdown.md`.
- Original file retained unchanged for audit; this v2 supersedes its feature split.