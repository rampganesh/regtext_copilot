# Product Context — RegCopilot V1

## Why this exists
UK Basel 3.1 implementation is in a **transition period**, and the regulatory corpus reflects that.
The publication timeline the corpus must support:

| Doc | Role | Approx status |
|---|---|---|
| CP16/22 | Consultation Paper (2022) | Proposed/Consultation → later Superseded/Historical |
| PS17/23 | Policy Statement (near-final) | near-final base |
| PS9/24 | Policy Statement (near-final rules) | near-final base |
| PS1/26 | Policy Statement (final rules, effective 1 Jan 2027) | Future-Effective → Final/Operative |
| CP9/26 | Consultation Paper (current) | Proposed/Consultation |
| PRA Rulebook parts | Rulebook rules | per part |
| Reporting instructions/templates (e.g. CRR007) | Structured reporting material | per version |
| Explanatory overviews | Supporting material | Explanatory/Supporting |

**Current/future and proposed/final requirements coexist in the corpus.** A technically correct
answer built from the wrong document version is a real, observed failure mode (confirmed problem:
source-validation burden, 7 mentions). This is the single most important environmental fact and it
is the reason status + as-of-date logic is a *correctness core*, not a UI nicety.

Corpus size for V1: **≤ ~1,500 pages, PDF format.**

## Users
- **Primary persona — experienced regulatory reporting analyst** (`wiki/personas/experienced-analyst.md`):
  jumps directly to likely sources; needs to *verify*, not be told what applies. The analyst remains
  responsible for the conclusion (header disclaimer + answer note on every result).
- **Secondary — newer analysts learning the research path**: excluded from V1 design (evidence is
  second-hand only → STUB-4; requires a direct interview first).
- Questions arrive as **free natural language — no search operators** (frozen UI decision).

## Governance split (fixed)
- **Regulatory Content Owner** governs corpus inclusion, source status and relationships.
- **Technology** owns ingestion, indexing and the retrieval pipeline.
- Nothing enters the active corpus without Content Owner approval; Technology's amendment detection
  produces *candidate* updates that never auto-activate.

## Product rules encoded in the contract (compliance-relevant, NON-NEGOTIABLE)
1. **No confidence scores, ever** — no score field exists anywhere and none may be added; trust comes
   from evidence chains only.
2. **Evidence-led phrasing** — answers begin "The relevant sources indicate…"; never "The applicable
   requirement is…". Enforced in the synthesis prompt; a violation is a build failure.
3. **Five status badges exactly:** `Final/Operative`, `Future-Effective`, `Superseded/Historical`,
   `Proposed/Consultation`, `Explanatory/Supporting` — plus a **status date** on every cited source.
   No other status may render.
4. **Conflicts are never auto-resolved** — structured conflict object, side-by-side rendering,
   escalation button as the only resolution path.
5. **Effective dates are metadata, not applicability** — statuses computed relative to the as-of
   date; nothing in the UI claims a rule applies to the bank.
6. **Context views preserve qualifications/exceptions** — retrieval returns the surrounding passage
   *with* its qualifications (`qual` spans), never a stripped quote.
7. **Analyst owns the conclusion** — disclaimer in the header; answer note on every result.
8. **No fabrication** — every citation passage, quote and conflict panel text is verified verbatim
   against source chunk content (whitespace-normalized) server-side; only `hl`/`qual` inline tags
   allowed, all other HTML sanitized away.
9. **Point-in-time retrieval** — nothing published after the as-of date may appear in any answer,
   including graph-expanded context.
10. **Definitions completeness** — every `definitions` key referenced by a citation must resolve to a
   glossary entry; a missing definition is a build failure.

## The frozen UI/API contract
The prototype (`artefacts/regcopilot-prototype.html`) was validated and is **frozen**. Only the
mocked data layer and the single `ask()` function are edited during backend integration.

**Input contract** (`POST /api/v1/ask`, produced by `ask()`):
```json
{ "question": "string — free natural language, trimmed",
  "asOfDate": "YYYY-MM-DD — defaults to today when empty" }
```

**Output contract** (single consumer: the prototype's `render(sc, asOf)`):
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

## The five acceptance scenarios (integration suite is the primary acceptance test)
Inputs are `{question, asOfDate}`; each asserts a different behaviour:

1. **Prose citation with an exception** — retrieve the operative paragraph **plus** its qualification
   (e.g. the 90-day / EUR 1m exception), correct badge + status date.
2. **Conflict across supersession** — CP16/22 (`Superseded/Historical` at today) vs PS1/26
   (`Future-Effective`); side-by-side, never auto-resolved, divergence flagged in the answer.
3. **Reporting question, no prose paragraph** — row/instruction-level locations (e.g. CRR007 rows
   0110–0130, `CRR007-INS2`), verbatim row meanings, exception preserved, every `definitions` key
   populated, near-final vs final comparison.
4. **Point-in-time flip** — with `asOfDate = 2022-12-01`, CP16/22 renders `Proposed/Consultation`
   (published 27 Nov 2022), NOT `Superseded/Historical`, because supersession happened *after* the
   as-of date.
5. **Escalation** — ISAv permission deadline: PS9/24 ¶5.4 (concrete 31 Dec 2026) vs PS1/26 ¶ISA-3.1
   (deferred) vs CP9/26 ¶2.8 (proposes confirming); conflict callout + side-by-side + escalation
   modal pre-filled with headline + both source ids + question.

## Sample/seed corpus available in the repo
- `docs/ps126app1.pdf` (5.3 MB, real PRA PDF) and `docs/ps126app1-output.md` (≈10k lines, a
  PyMuPDF4LLM-style markdown extraction of it). Useful as the first real ingestion target and for
  parsing spike F5/DI4-5. Note the extraction contains OCR/encoding artefacts (e.g. `â€"`), so
  cleaning/verbatim-normalisation matters.
