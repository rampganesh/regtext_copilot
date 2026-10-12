# RegCopilot V1 Prototype — Source Code Reading & RAG Integration Spec

**Audience:** development team building the V1 backend (RAG lookup, retrieval, synthesis).
**Reference implementation:** `artefacts/regcopilot-prototype.html` (single file, ~405 lines, vanilla HTML/CSS/JS, zero dependencies).
**Purpose:** explain how the prototype is structured, and define exactly which sections change — and which must **never** change — when the mock data layer is replaced by real RAG lookups. Includes the required data contract and a per-scenario input/output walkthrough.

---

## 1. Architecture at a glance

The prototype is a two-view single-page app with three logical layers:

```
[ VIEW LAYER ]  Ask page (lines 99–127) · Results page (lines 129–155) · Escalation modal (lines 157–159)
      |
[ PRESENTATION LAYER ]  CSS (lines 6–92) · render() + UI event handlers (lines 284–403)
      |
[ MOCK DATA LAYER ]  SOURCES registry (166–173) · SCENARIOS (186–263) · DEFS (267–275) · badgeFor() (175–183)
```

The **only layer the RAG integration touches is the Mock Data Layer** (plus one function, `ask()`, which currently dispatches locally). Everything in the View and Presentation layers is the frozen V1 UI contract — the whole point of the prototype was to validate that UX, so do not redesign it during backend integration.

### Line map (use as your reading guide)

| Lines | Section | Role | Changes for RAG? |
|---|---|---|---|
| 1–5 | Document head, title | Page metadata | No |
| 6–92 | `<style>` block | All visual design (badges, conflict panel, context view, escalation modal) | **No — frozen UI** |
| 94–97 | Header | Logo + authority disclaimer (governance requirement — never remove) | No |
| 99–127 | **View 1: Ask page** | Instructions box, question textarea, as-of date input, 5 scenario chips | Chips become optional; input wiring stays |
| 129–155 | **View 2: Results page** | Static shells: question box, answer box, citations list | No (rendered dynamically) |
| 157–159 | Escalation modal | SME escalation flow | No |
| 161–183 | `<script>` open · `SOURCES` · `badgeFor()` | Mock source registry + status computation | **REPLACE** with backend-provided status (see §4) |
| 186–263 | `SCENARIOS` | Five mock question/answer/citation sets | **REPLACE** — this is the mock RAG response corpus |
| 267–275 | `DEFS` | Mock definition dictionary (linked definitions in citations) | **REPLACE** — definitions come from retrieval |
| 277–282 | Date handling | as-of default (today) + change listener | No |
| 284–320 | `goAsk()`, `loadScenario()`, `ask()` | View switching + question dispatch | **EDIT `ask()`** — swap local lookup for API call (see §5) |
| 322–381 | `render(sc, asOf)` | Renders answer, citations, conflict panel from data | **Keep** — this is your render contract (see §4.3) |
| 383–403 | Event handlers: `toggleCit`, `toggleDef`, `openEsc`, `submitEsc`, `closeEsc` | Expand/collapse, definitions, escalation | No |

---

## 2. The product rules encoded in the code (do not break these)

These map 1:1 to compliance/stakeholder requirements and are enforced *in the presentation layer or data contract*. The RAG backend must respect them:

1. **No confidence scores, ever.** There is no score field anywhere and none may be added — trust comes from evidence chains only (see the answer-note injected at line ~348 and footer line ~160).
2. **Evidence-led phrasing.** Answers must begin “The relevant sources indicate…” and must never assert “The applicable requirement is…”. Enforce this in the synthesis prompt; the UI does not police it.
3. **Five status badges exactly** (line 17–21 CSS, `badgeFor()` line 175): `Final/Operative`, `Future-Effective`, `Superseded/Historical`, `Proposed/Consultation`, `Explanatory/Supporting` — plus an effective date on every cited source. No other statuses may be rendered.
4. **Conflicts are never auto-resolved.** A conflict arrives as a structured `conflict` object and is rendered side-by-side (lines 366–379). The UI never picks a source; the escalation button is the only resolution path.
5. **Effective dates are metadata, not applicability.** Statuses are computed relative to the user's **as-of date**; nothing in the UI claims a rule applies to the bank.
6. **Context views preserve qualifications/exceptions.** Passages carry inline `qual` segments (purple callouts) — retrieval must return the surrounding passage *with* its qualifications, not a stripped quote.
7. **Analyst owns the conclusion** — disclaimer in the header (line 96) and answer-note on every result.

---

## 3. Input contract (what the UI sends)

Produced in `ask()` (line 310) and `loadScenario()` (line 302):

```json
{
  "question": "string — free natural language, trimmed",
  "asOfDate": "YYYY-MM-DD — from the as-of control; defaults to today when empty"
}
```

Notes:
- **No search syntax is offered or supported** — the input is a plain textarea (line 106). Do not add operators unless the product decision is revisited.
- `asOfDate` is semantically load-bearing: every source status in the response is evaluated relative to it (scenario 4 proves this — same CP16/22 source renders as `Proposed/Consultation` when as-of = 2022-12-01 and `Superseded/Historical` when as-of = today).
- The five scenario chips (lines 116–121) are **demo-only scaffolding** — delete them (or hide behind a “demo mode” flag) once the API is live. They prefill the textarea and call `ask()`.

---

## 4. Output contract (what the RAG backend must return)

`render(sc, asOf)` (line 322) is the single consumer of the response. The backend must return a structure with exactly the shape of one SCENARIOS entry (lines 186–263), plus per-citation resolved status. Field-by-field:

```json
{
  "question": "echo of the user question",
  "answer": [
    { "text": "paragraph 1 — plain text or sanitized HTML" }
  ],
  "conflict": null
  | {
      "headline": "one-line description of the divergence",
      "left":  { "sourceKey": "CP16/22", "text": "passage A with <span class='hl'>highlight</span>", "meta": "status · dates · paragraph ref" },
      "right": { "sourceKey": "PS1/26",  "text": "passage B with <span class='hl'>highlight</span>", "meta": "status · dates · paragraph ref" },
      "warning": "explicit note that the UI does not pick a source"
    },
  "citations": [
    {
      "source": {
        "id": "PS17/23",
        "title": "Implementation of Basel standards — near-final rules",
        "type": "Policy Statement (near-final)",
        "publishedDate": "2023-07-20",
        "status": "future-effective",
        "statusDate": "2027-01-01"
      },
      "location": "PS17/23 · Credit risk (SA) · paragraph SA-2.4",
      "passage": "surrounding passage: operative text in <span class='hl'>…</span>, qualifications in <span class='qual'>…</span>",
      "definitions": [ "output floor", "risk weight" ]
    }
  ],
  "definitions": { "output floor": "definition text…", "IRB": "definition text…" }
}
```

### 4.1 Status resolution — where it moves to the backend

In the mock, `badgeFor(src, asOf)` (line 175) computes the badge from a hardcoded registry using exactly these rules. Reimplement server-side against real document metadata:

| Source base | asOf < effective date | asOf >= effective date | special cases |
|---|---|---|---|
| Final rules / near-final PS | `Future-Effective` | `Final/Operative` | near-final (PS17/23, PS9/24) treated as final-base; disclose “near-final” in `type` |
| Consultation CP | `Proposed/Consultation` | — | if `supersededBy` date exists and asOf >= it → `Superseded/Historical` |
| Explanatory content | `Explanatory/Supporting` always | — | effective date = publication date |

The date shown under the badge (`statusDate`) must always be present — “effective 1 Jan 2027”, “superseded 20 Jul 2023”, “published 27 Nov 2022”. Keep `badgeFor()` only as a fallback, or delete it once statuses come server-side.

### 4.2 Locations — prose vs reporting templates

`location` is a free-text string rendered as-is in a monospace chip (`.cit-loc`). Two mandatory formats:
- **Prose sources:** `<PS id> · <chapter/part> · paragraph <ref>` — e.g. `PS1/26 · Final rules · Credit risk (SA) · 2.11`.
- **Reporting sources:** the specific **template / table / row / field / instruction reference** — e.g. `PS1/26 · Reporting (C) · template CRR007, rows 0110–0130`, with `Instruction CRR007-INS2` quoted inside the passage. The retrieval index must be granular to row/instruction level, and `definitions` must list the field-level terms the rows depend on (scenario 3 is the acceptance test).

### 4.3 render() expectations (frozen)
- Iterates `answer` paragraphs; if `conflict` is non-null it injects the red conflict callout into the answer and renders the side-by-side panel at the top of the citation list with the Escalate button.
- Each citation renders: number, source id — title, type · published date, location chip, badge + statusDate; click expands the context passage and definition links.
- Definition links look up `definitions[key]`; a missing key renders “Definition not available” (acceptable degradation, but retrieval should always aim to populate).

---

## 5. Integration point: the one function you edit

`ask()` (line 310) currently does a local `SCENARIOS.find()` and falls back to scenario 1. Replace with:

```js
async function ask(){
  const q = document.getElementById('q').value.trim();
  if(!q) return;
  const asOf = document.getElementById('asof').value || TODAY;
  setLoading();
  const sc = await fetch('/api/v1/ask', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ question:q, asOfDate:asOf })
  }).then(r => { if(!r.ok) return showError(r.status); return r.json(); });
  current = sc; render(sc, asOf);
  document.getElementById('askView').classList.remove('active');
  document.getElementById('resView').classList.add('active');
  window.scrollTo(0,0);
}
```

Also add an error/empty-result state (currently impossible with mocks): render a neutral message such as “The relevant sources did not include an answer to this question” — with **no** confidence language — plus a suggestion to rephrase or escalate. Delete `SCENARIOS`, `DEFS` and (optionally) `SOURCES`/`badgeFor` once the backend supplies §4. Escaping: passages arrive pre-marked with `hl`/`qual` spans, so the backend must sanitize all other regulator/user text before placing it in `passage`/`text` fields.

---

## 6. Scenario-by-scenario input/output walkthrough (acceptance specification)

Each scenario in `SCENARIOS` (lines 186–263) is a concrete test case for the RAG pipeline. The table maps every scenario to what the backend must do and what the UI must show.

### Scenario 1 — Retail exposures under the standardised approach (lines 187–202)

| | |
|---|---|
| **Input** | `question` = retail SA question · `asOfDate` = today (2026-09-24) |
| **Backend behaviour** | Retrieve across three authority levels: near-final rules (PS17/23 ¶ SA-2.4, 75% weight), final rules (PS1/26 § 2.11, 45% for qualifying residential mortgages), explanatory overview. No conflict. Synthesis must *contrast* the two rule statements and note the differing authority levels. |
| **Output** | 3–4 answer paragraphs, evidence-led opening; 3 citations rendering as: PS17/23 → **Future-Effective** (eff. 1 Jan 2027), PS1/26 → **Future-Effective**, PRA overview → **Explanatory/Supporting**. Context views carry the 90-days-past-due / EUR 1m exceptions (PS17/23) and the LTV > 80% split-treatment exception (PS1/26). |
| **Tests** | Multi-status badge rendering; authority-level contrast in synthesis; exception preservation. |

### Scenario 2 — Output floor phase-in timetable (lines 203–214) — CONFLICT

| | |
|---|---|
| **Input** | `question` = output floor phase-in · `asOfDate` = today |
| **Backend behaviour** | Retrieve CP16/22 ¶ 4.12 (proposed 50% start, phased to 72.5% by 2030) alongside PS1/26 ¶ OF-1.2 (72.5% from 1 Jan 2027, no phase-in). **Conflict detection required** — these are semantically divergent answers to the same question. Do not resolve; do not rank as a proxy for choosing. |
| **Output** | Answer paragraphs explicitly flag the divergence; red conflict callout in the answer; side-by-side panel above the citations (left: CP16/22, `Superseded/Historical` at today's as-of; right: PS1/26, `Future-Effective`); warning text; **Escalate** button. |
| **Tests** | Conflict detection; side-by-side rendering; escalation path present. |

### Scenario 3 — Reporting template rows for the output floor (lines 223–231)

| | |
|---|---|
| **Input** | `question` = which template rows capture the output floor · `asOfDate` = today |
| **Backend behaviour** | Retrieval must operate at **row/instruction granularity**, not document level: template CRR007 rows 0110 (total RWA after floor), 0120 (RWA subject to floor), 0130 (floor ratio), instruction CRR007-INS2, from both PS1/26 (final) and PS9/24 (near-final draft). Must supply the dependent field definitions (`output floor`, `risk-weighted assets`) via `definitions`. |
| **Output** | Citations whose `location` chips are `template CRR007, rows 0110–0130`; context passages quote the row meanings verbatim with the “blank where standardised-only” exception preserved; definition links expand inline. |
| **Tests** | Template/row/field reference format; definitions linkage; near-final-vs-final comparison of template structure. |

### Scenario 4 — Original consultation as of 1 Dec 2022 (lines 233–243)

| | |
|---|---|
| **Input** | `question` = what was proposed in the original consultation · `asOfDate` = **2022-12-01** (chip sets this explicitly) |
| **Backend behaviour** | **Point-in-time retrieval**: only sources published on/before the as-of date may appear (here: CP16/22 only, as Proposed/Consultation). The explanatory overview (published 2026) must NOT be offered as if contemporaneous — if included at all, it must be statused Explanatory/Supporting with a published date that visibly post-dates the query (the mock does exactly this, with a note in the passage). |
| **Output** | Citations show CP16/22 as `Proposed/Consultation` (published 27 Nov 2022) — NOT `Superseded/Historical`, because the supersession happened after the as-of date. |
| **Tests** | As-of-driven status computation (same source = different badge on different as-of dates); no retro-application of later determinations. |

### Scenario 5 — ISAv model permission deadline (lines 244–263) — ESCALATION

| | |
|---|---|
| **Input** | `question` = ISAv permission application deadline · `asOfDate` = today |
| **Backend behaviour** | Retrieve PS9/24 ¶ 5.4 (31 Dec 2026 deadline, near-final) vs PS1/26 ¶ ISA-3.1 (deadline “to be specified”, final rules) and CP9/26 ¶ 2.8 (proposes confirming 31 Dec 2026). Conflict = divergence between a concrete date and a deferred date across authority levels. |
| **Output** | Conflict callout + side-by-side (PS9/24 vs PS1/26, both `Future-Effective` with their own statusDates) + CP9/26 citation as `Proposed/Consultation` with “do not rely on this” qualification in its context view; escalation modal pre-fills the summary with the conflict headline + both source ids + the question. |
| **Tests** | Conflict between two future-effective sources (status alone cannot disambiguate); escalation flow end-to-end; three-way authority layering. |

---

## 7. Change summary for the dev team

| Change type | Target | Detail |
|---|---|---|
| **DELETE** | `SCENARIOS` (186–263), `DEFS` (267–275), scenario chips (116–121) | Mock data layer and demo scaffolding |
| **DELETE or KEEP as fallback** | `SOURCES` (166–173), `badgeFor()` (175–183) | Only if status resolution is NOT moved server-side |
| **EDIT** | `ask()` (310) | Replace local lookup with `fetch('/api/v1/ask')`; add loading, error and empty states |
| **KEEP frozen** | All CSS (6–92), header disclaimer, both views, `render()` (322), `toggleCit`/`toggleDef`/escalation handlers (383–403) | The validated V1 UI contract |
| **ADD** | Loading spinner state; error/empty-result view; (optional) citation deep-link to source document for future V2 | Minimal, no redesign |

## 8. Integration test checklist

- [ ] All five scenarios produce identical UI states from API data as from mocks (screenshot diff against the prototype).
- [ ] Every citation has a status badge (one of exactly five) AND a status date — no citation renders without both.
- [ ] Changing as-of date to 2022-12-01 flips CP16/22 from `Superseded/Historical` to `Proposed/Consultation`.
- [ ] Conflict responses always include both sides + warning + escalation button; no response ever resolves a conflict silently.
- [ ] Every answer's first sentence is evidence-led (“The relevant sources indicate…”); a synthesis asserting “the applicable requirement is…” is a build failure.
- [ ] No confidence scores, ratings, or rankings are rendered anywhere in the UI.
- [ ] Reporting questions return row/instruction-level locations and populate every `definitions` key referenced.
- [ ] Context passages retain qualifications/exceptions (purple `qual` segments) — spot-check scenario 1 (90-day exception) and scenario 5 (transitional-arrangements exception).
- [ ] as-of date with no relevant sources → neutral empty state, no fabricated answer.
- [ ] HTML injection: passage/text fields are sanitized server-side; `hl`/`qual` are the only allowed inline tags.

---
*Source of truth: `artefacts/regcopilot-prototype.html` @ commit state of 2026-09-24. Line numbers refer to that file; re-verify after any edit.*
