# User Story Backlog - RegCopilot V1

Parent epic: `2025-06-18_epic-hypothesis-regcopilot-v1.md` | Feature references: `2025-06-18_epic-feature-breakdown-v2.md`
Persona: experienced regulatory reporting analyst (evidence-chained, `wiki/personas/experienced-analyst.md`). Newer-analyst persona excluded (second-hand evidence - stub below).
Split method: `skills/user-story-splitting` (8 patterns in order) | Story format: `skills/user-story` (Cohn + Gherkin, one When/Then) | No day estimates (PM direction); sizing relative to siblings only.

**Invariant acceptance criterion (all stories touching citations or evidence):** the system must never fabricate citations, quotations or references (decision `2025-06-04_minimum-provenance-standard`; `wiki/problems/citation-integrity.md`; hard gate in the epic's validation measures).

---

## F1 - Evidence search & connection (ref: breakdown v2, F1)

### Story S1.1 - Natural-language search with regulatory-relevance ranking (Major Effort core)
- **As an** experienced regulatory reporting analyst
- **I want to** ask a question in normal language and receive genuinely relevant authoritative sources from the curated corpus
- **so that** I can start from likely sources instead of trial-and-error searching across multiple documents
- **Scenario:** the first plausible result is not the operative requirement
- **Given** the curated corpus is loaded **and Given** my question concerns a capital-reporting requirement **and Given** several documents contain semantically similar terminology but differ in exposure class or calculation approach
- **When** I submit my question in plain language
- **Then** I receive a ranked set of sources ranked by regulatory relevance (scope, status, applicability), not merely terminology similarity, and none is presented as "the applicable provision"
- *Ground truth:* digest row 1 (source: 2025_06_04_digest_clarifications.md); Meeting 2 L43-47 (source: 2025_05_26_meeting_followup.md); interview A2 L10-21 (source: 2025_06_18_interview_analyst2prov.md); decisions `2025-06-04_v1-scope-evidence-led-research`, `2025-06-04_bounded-curated-corpus`

### Story S1.2 - Forward navigation: rule -> reporting representation
- **As an** experienced regulatory reporting analyst
- **I want to** start from a prudential rule and see how it is represented in reporting instructions and templates
- **so that** I can answer "how does this requirement appear in reporting?" without manually following references
- **Scenario:** forward navigation from a rule
- **Given** I am viewing a rule requirement **and Given** reporting instructions/templates implement that requirement
- **When** I request the reporting view of the requirement
- **Then** I see the linked reporting instructions/templates and any reporting treatment described elsewhere, each with source status shown
- *Ground truth:* Meeting 2 L63-65 (bidirectional navigation, no single starting point); kickoff L15 (template-field example); `wiki/problems/terminology-cross-referencing.md`

### Story S1.3 - Backward navigation: reporting field -> underlying requirement
- **As an** experienced regulatory reporting analyst
- **I want to** start from a reporting field or template cell and trace back to the underlying regulatory requirement
- **so that** I can answer "where does this field come from / what does it mean?" from the primary source, not just the template instruction
- **Scenario:** backward navigation from a template field
- **Given** I am viewing a reporting template field **and Given** the field's meaning depends on definitions or instructions elsewhere in the corpus
- **When** I request the regulatory basis of the field
- **Then** I am shown the underlying requirement(s) and the definitions it depends on, each with source status
- *Ground truth:* kickoff L13-15; Meeting 2 L61, L63-65; `wiki/problems/non-prose-regulatory-content.md`

### Story S1.4 - Related-material surfacing
- **As an** experienced regulatory reporting analyst
- **I want to** see related definitions, reporting instructions and relevant changes alongside a source I am viewing
- **so that** I discover connections without manually hunting every reference
- **Scenario:** related material for a reporting requirement
- **Given** I am viewing a source **and Given** the corpus contains definitions, related instructions and changes connected to it
- **When** I open the source
- **Then** I see its related material in a form I can scan without it overwhelming the answer
- *Ground truth:* kickoff L51; interview A1 L140 ("surface related material without overwhelming the user"); digest row 1

### Spike F1-TAD - Relevance-ranking feasibility (time-boxed; learning, not deliverable)
- **Question:** can ranking reliably separate semantically similar from regulatorily applicable results? Evaluate against the difficult-case set (most-obvious-document-not-correct, similar terminology) before finalizing S1.1's acceptance criteria. Feeds Q8 (evaluation design, `wiki/open-questions.md`).
- *Ground truth:* Meeting 2 L45-47; SME evaluation spec L133-137; both analysts' difficult-case lists (interviews)


## F2 - Status & temporal awareness (ref: breakdown v2, F2; unchanged per PM direction)

### Story S2.1 - Status label and effective date on every result and answer
- **As an** experienced regulatory reporting analyst
- **I want to** see the source status (final/operative, future-effective, superseded/historical, proposed/consultation, explanatory/supporting) and effective date on every search result and answer
- **so that** I can immediately tell whether material is operative without manually checking the document
- **Scenario:** mixed-status results
- **Given** my search returns documents in different statuses (e.g., final rules PS1/26 and consultation CP9/26)
- **When** I view the result list or an answer
- **Then** every source shown carries its status label and effective/publication date visibly - in both search and answers
- *Ground truth:* decisions `2025-06-04_status-authority-labelling-ux`, `2025-06-04_date-based-temporal-mode`; desk research L6-9 (source: 2025_06_10_research_docversions.md)

### Story S2.2 - As-of-date answers
- **As an** experienced regulatory reporting analyst
- **I want to** ask a question relative to a specified date (current as-of a reference date, or future-effective)
- **so that** I get the requirement applicable at that date, not just the newest publication
- **Scenario:** future-effective requirement
- **Given** a requirement has a future effective date (e.g., Basel 3.1 from 1 Jan 2027) **and Given** the current requirement remains operative until then
- **When** I ask for the requirement applicable as of a date before the effective date
- **Then** the answer presents the currently operative requirement, with the future-effective version available and clearly labelled - and vice versa for a post-date query
- **Dependency flag:** requires corpus metadata (effective dates, status) from the bounded-corpus ingestion workstream (decision `2025-06-04_bounded-curated-corpus`)
- *Ground truth:* decision `2025-06-04_date-based-temporal-mode`; Meeting 2 L17, L23; interview A2 L98 ("latest" inadequate)

### Story S2.3 - Evidence-led answer language
- **As an** experienced regulatory reporting analyst
- **I want to** answers phrased as "The relevant sources indicate..." with source status visible, never "The applicable requirement is..." unless applicability has been validated
- **so that** I never mistake a proposal, consultation or explanatory publication for the operative requirement
- **Scenario:** consultation-derived evidence
- **Given** the best-matching evidence for my question is a consultation paper or explanatory publication **and Given** status labels are displayed per S2.1
- **When** the answer is generated
- **Then** it uses cautious evidence-led phrasing, labels the material proposed/consultation or explanatory/supporting, and never states the requirement definitively
- *Ground truth:* digest row 7; Meeting 2 L39, L105; `wiki/problems/authority-overstatement-risk.md`; `wiki/problems/requirement-applicability-determination.md`

## F3 - Citations & provenance (ref: breakdown v2, F3)

### Story S3.1 - Verifiable citation for textual requirements
- **As an** experienced regulatory reporting analyst
- **I want to** every claim drawn from textual regulatory material to carry a citation I can navigate to - document, version/status, and the exact section or paragraph, with surrounding context preserved
- **so that** I can independently verify the claim against the wording in seconds instead of re-searching the document
- **Scenario:** verifying a rule-based claim
- **Given** an answer relies on a provision in a final rule
- **When** I follow its citation
- **Then** I land on the exact section/paragraph, and the cited context shows what the answer claimed - including any qualification or condition
- *Ground truth:* decision `2025-06-04_minimum-provenance-standard`; interview A1 L55-57, L61-65 (source: 2025_06_17_interview_analyst1exp.md); interview A2 L59 (source: 2025_06_18_interview_analyst2prov.md)

### Story S3.2 - Verifiable citation for reporting material (templates, tables, instructions)
- **As an** experienced regulatory reporting analyst
- **I want to** answers about reporting fields and templates to identify the specific template, table, row/field or reporting instruction that carries the requirement - and the definitions the field's meaning depends on
- **so that** I can verify reporting answers even when no single prose paragraph states the requirement
- **Scenario:** reporting-field answer with dependent definitions
- **Given** a question about a reporting field **and Given** the field's meaning depends on a definition and a reporting instruction located elsewhere in the corpus (template instructions alone are insufficient)
- **When** I inspect the citation
- **Then** it identifies the specific template/table/row/field/instruction reference **and** links the definitions it depends on, preserving context so I can validate the claim without reconstructing the trail myself
- *Ground truth:* digest row 4; kickoff L15; `wiki/problems/non-prose-regulatory-content.md`; interview A2 L63-75; interview A1 L65 (source: 2025_06_17_interview_analyst1exp.md)

### Story S3.3 - Surrounding-context navigation from a citation
- **As an** experienced regulatory reporting analyst
- **I want to** expand from a cited provision to its surrounding passage or table context
- **so that** I can check qualifications, exceptions and conditions without searching the document again
- **Scenario:** qualified provision
- **Given** an answer cites a provision containing a qualification or exception
- **When** I open the citation's context view
- **Then** I see the surrounding passage including the qualification/exception, without leaving the answer
- *Ground truth:* Meeting 2 L57-59 (context-vs-cumbersomeness trade-off); interview A2 L59 ("click or navigate directly to the exact supporting provision"); decision `2025-06-04_minimum-provenance-standard`


## F4 - Conflicts, uncertainty & escalation (ref: breakdown v2, F4)

### Story S4.1 - Conflict exposure
- **As an** experienced regulatory reporting analyst
- **I want to** conflicting sources presented side-by-side with their status and dates
- **so that** I can understand why the conflict exists and decide which statement applies - instead of receiving a silently resolved answer
- **Scenario:** two sources, different conclusions
- **Given** the corpus contains sources that appear to conflict (different dates, scopes, populations or detail levels)
- **When** an answer draws on both
- **Then** the answer presents both sources with their status/dates and an explicit conflict warning - it does not pick one silently
- *Ground truth:* `wiki/problems/conflict-exposure.md` (confirmed); Meeting 2 L67-71; digest row 7

### Story S4.2 - Insufficient-evidence statement
- **As an** experienced regulatory reporting analyst
- **I want to** the system to state clearly when the available evidence is insufficient, conflicting or ambiguous
- **so that** I never receive a plausible-looking answer without strong support
- **Scenario:** insufficient corpus evidence
- **Given** the corpus does not contain evidence sufficient to answer the question confidently
- **When** I ask the question
- **Then** the system says so explicitly - naming what was searched and what is missing - rather than producing a low-support answer
- *Ground truth:* kickoff L89; Meeting 2 L77; digest rows 1, 3; assumption A3 (this story is its test vehicle, alongside S4.3)

### Story S4.3 - Evidence-backed escalation package
- **As an** experienced regulatory reporting analyst
- **I want to** assemble a well-bounded escalation - the question plus the assembled evidence package - to hand to a regulatory SME
- **so that** the SME can focus on the judgement that requires expertise rather than re-doing my research
- **Scenario:** unresolved point requiring judgement
- **Given** I have gathered the relevant sources but a specific point requires SME confirmation **and Given** I can state what is uncertain and what needs resolving
- **When** I request an escalation package
- **Then** I receive a bounded summary: the question, the evidence with citations and status, and the specific unresolved point
- *Ground truth:* interview A1 L78-82; interview A2 L83-87; assumption A3; `wiki/problems/requirement-applicability-determination.md` (gathering info is not making the determination)

## F6 - Evaluation signals (ref: breakdown v2, F6)

### Story S6.2 - Tool-assisted answer measurement
- **As an** experienced regulatory reporting analyst
- **I want to** tool-assisted answers to automatically capture time-to-answer, citations used, and whether the outcome was an answer, refusal or escalation
- **so that** productivity, safety and citation-correctness can be measured against the manual baseline without manual logging
- **Scenario:** instrumented answer
- **Given** I answered a question using the tool
- **When** the answer is produced
- **Then** the system records time-to-answer, sources/citations used, and the outcome type (answer / refusal / escalation)
- *Ground truth:* decision `2025-06-04_v1-balanced-scorecard` (row 3 measures); `wiki/problems/no-feedback-loop.md` (interview evidence); feeds Q8

### Research note - Manual baseline protocol (NOT a backlog story; replaces the original S6.1)
The manual-process baseline (decision `2025-06-04_v1-balanced-scorecard`: "a manual-process baseline should be established first") measures today's process **before the tool exists** - it is a research activity, not system functionality. Protocol: a structured observation template (question type; time split across search / validation / evidence assembly / presentation; sources used; outcome) run over 5-10 real recent questions. It feeds the epic's validation measures ("target % to be set once the manual baseline exists") - see experiment 1 in `2025-06-18_epic-hypothesis-regcopilot-v1.md`.


## Deferred stubs (prioritized later - recorded so nothing is silently dropped)

### STUB-1 - Stale-answer marking (F5) - gated on Q10
- **As an** experienced regulatory reporting analyst
- **I want to** answers that relied on superseded or amended material flagged as potentially stale and linked to the updated source/version
- **so that** I never act on an answer that silently became outdated
- **Blocking open point:** Q10 - staleness window/threshold; proactive re-review vs. flag-on-use (`wiki/open-questions.md`; source: 2025_06_14_meeting_latedocuments.md, L13)
- *Ground truth:* decision `2025-06-14_corpus-update-and-staleness-policy`; Meeting 3 L8, L11; `wiki/problems/no-feedback-loop.md`

### STUB-2 - Answer audit store (F5) - gated on retention decisions
- **As an** experienced regulatory reporting analyst
- **I want to** answers stored with full audit context - question, answer, citations, evidence versions used, temporal context
- **so that** any answer can later be reconstructed and checked against the material current at the time
- **Blocking open point:** data retention/ownership/reliance considerations (Meeting 2 L151) - not assumed in initial design
- *Ground truth:* Meeting 3 L9, L91-93; `wiki/problems/no-feedback-loop.md`

### STUB-3 - Impact-tracing capture (F5) - pairs with STUB-1/2
- **As an** experienced regulatory reporting analyst
- **I want to** the recipient and basis-version of each answer recorded at capture time
- **so that** when an interpretation is later found outdated, we can determine who received it and whether related questions were answered the same way
- *Ground truth:* interview A1 L88-93 (source: 2025_06_17_interview_analyst1exp.md); interview A2 L91-96 (source: 2025_06_18_interview_analyst2prov.md); Q10 evidence

### STUB-4 - Newer-analyst learning-path support - revisit after a direct newer-analyst interview
- **As a** newer regulatory reporting analyst
- **I want to** understand why one source should be trusted over another and follow a guided research path
- **so that** I reach competence faster without depending on colleague availability
- **Blocking open point:** persona evidence is entirely second-hand (interviews A1 L101-113, A2 L104-114; kickoff L81, L113); a direct newer-analyst interview is required before design (v2 breakdown, conscious exclusion 3)
- *Ground truth:* `wiki/personas/newer-analyst.md`; `wiki/problems/experience-dependency.md`

### STUB-5 - Structured feedback categories - post-V1 F6 extension
- **As an** experienced regulatory reporting analyst
- **I want to** report why an answer was poor - incorrect answer, insufficient evidence, incorrect source, outdated source, irrelevant source, or correct but poorly explained
- **so that** corrections can be tied to the question, evidence and source version, improving research quality beyond thumbs-up/down
- **Blocking open point:** not prioritized for V1 (F5-adjacent); SME feedback-mechanism design
- *Ground truth:* Meeting 2 L85-89; `wiki/problems/no-feedback-loop.md` (confirmed)

## Split evaluation and validation

- **Pattern route:** F1 = Pattern 6 (Major Effort) + Pattern 3/4 (navigation directions, related-material data variations) + Pattern 8/TAD (ranking spike). F2 = Pattern 7 (Simple/Complex: core label, as-of behaviour, language variations). F3 = Pattern 4 (data variations: prose vs. structured references) + context navigation. F4 = Pattern 3 (three business-rule variations). F6 = single story + research note.
- **Low-value work revealed:** S1.4 (related material) and S2.2 (as-of-date) can be deprioritized behind S1.1 + S2.1 + S3.1, which alone deliver a verifiable answer end-to-end.
- **Boundary statement:** F2 owns how status/date is displayed; F3 owns the citation reference itself. S2.3 references S2.1's labels as a Given.
- **INVEST re-check:** all stories single Scenario/one When/Then; distinct so-thats (verified explicitly for S3.1 vs S3.2); S1.1 acknowledged as Major Effort (heavier by design); F5-related work absent from V1 stories (stubbed instead).

## Completeness statement (ground truth check)

- **Decisions (8/8):** v1-scope (epic/F1/F4) | temporal-awareness (S2.1/S2.2) | scorecard (S6.2 + baseline note) | bounded-corpus (S2.2 dependency flag + exclusion) | date-based mode (S2.2; "no latest" in S2.1/S2.3) | provenance standard (S3.1/S3.2/S3.3) | status/labelling (S2.1/S2.3) | corpus-update/staleness (STUB-1/2/3 + exclusion)
- **Problems (10/10):** evidence-assembly (epic north star), source-validation (S2.1/S2.2), citation-integrity (S3.x + invariant), conflict-exposure (S4.1), requirement-applicability (S2.3/S4.3 boundary), no-feedback-loop (S6.2 + STUB-1/2/3/5), authority-overstatement (S2.3), terminology-cross-referencing (S1.1/S1.4), non-prose (S1.3/S3.2), experience-dependency (STUB-4 + persona exclusion)
- **Assumptions:** A1 (baseline note + S6.2 + S1.1) | A2 (S3.x) | A3 (S4.2/S4.3 as test vehicle)
- **Open questions:** Q8 fed by F1-TAD + S6.2 | Q10 gates STUB-1

## Provenance

- Skills: `skills/user-story-splitting` (8 patterns), `skills/user-story` (Cohn + Gherkin template), tested via `skills/epic-breakdown-advisor` against `Epic breakdown.md` -> `2025-06-18_epic-feature-breakdown-v2.md`.
- Ground truth: `wiki/decisions/` (8 active), `wiki/problems/` (10 pages), `wiki/assumptions.md`, `wiki/open-questions.md` (Q8, Q10), `wiki/personas/`, sources `sources/` as cited per story.
