# User Story Backlog v2 - RegCopilot V1 (vertical reorganization)

Supersedes `2025-06-18_user-story-backlog-v1.md` (retained unchanged for audit). Parent epic: `2025-06-18_epic-hypothesis-regcopilot-v1.md` | Features: `2025-06-18_epic-feature-breakdown-v3.md` (mapping table shows where every v1/v2 story went).
Persona: experienced regulatory reporting analyst (`wiki/personas/experienced-analyst.md`). Newer-analyst persona excluded (second-hand evidence - STUB-4).
Split method: `skills/user-story-splitting` (8 patterns in order) | Story format: `skills/user-story` (Cohn + Gherkin, one When/Then) | No day estimates (PM direction); sizing relative to siblings only.

**Invariant acceptance criterion (all stories touching citations or evidence):** the system must never fabricate citations, quotations or references (decision `2025-06-04_minimum-provenance-standard`; `wiki/problems/citation-integrity.md`; hard gate in the epic's validation measures).

**Build order: VF0 -> VF1 -> VF2 -> VF3 -> VF4.**

---

## VF0 - Document & corpus foundation (priority-0; prerequisite for all features)

Stories are Cohn gists - deliberately high-level to initiate database-design discussions. Ownership: Regulatory Content Owner governs inclusion/status/relationships; Technology owns ingestion/indexing (bounded-corpus decision row 5).

### DI-1 - Curated corpus loading (Content-Owner gated)
- **As a** Regulatory Content Owner
- **I want to** load only approved UK capital/Basel 3.1 material (Rulebook, policy/supervisory statements, reporting instructions/templates) into the corpus
- **so that** every answer draws exclusively from authoritative, approved sources
- **Capability requirements (database-design discussion starters):**
  - Inclusion/exclusion criteria operationalized: exclude unrelated domains, uncontrolled web content, unclear-provenance material, and sources mistakable for operative requirements when only explanatory/proposed (bounded-corpus decision row 5)
  - A Content Owner approval gate: nothing becomes active corpus without confirmation (row 5)
  - Support the real Basel 3.1 corpus: CP16/22, PS17/23, PS9/24, PS1/26, CP9/26 (desk research timeline)
- *Enables:* VF1 (S1.1 needs a corpus) | *Ground truth:* decision `2025-06-04_bounded-curated-corpus`; desk research (source: 2025_06_10_research_docversions.md, L6-9)

### DI-2 - Source metadata capture
- **As a** Regulatory Content Owner
- **I want to** every source stored with publication date, effective date, document type, subject area and version/status (five-label taxonomy)
- **so that** every result and citation can carry its status badge and date without inference
- **Capability requirements:**
  - The five statuses: final/operative, future-effective, superseded/historical, proposed/consultation, explanatory/supporting (labelling decision row 7)
  - Effective date distinct from publication date; "latest" is never derivable as applicable (date-based mode decision)
  - Version/status visible in both search and answers (labelling decision)
- *Enables:* S2.1, S2.3, S3.1 (all VF1); satisfies the corpus-metadata dependency flagged on S2.2 in v2 | *Ground truth:* rows 5, 7; decision `2025-06-04_status-authority-labelling-ux`; decision `2025-06-04_date-based-temporal-mode`

### DI-3 - Relationships and versioning
- **As a** Regulatory Content Owner
- **I want to** supersession, amendment and reference relationships recorded between sources, with templates and instructions versioned alongside their rules
- **so that** "which version applies when" is queryable and an analyst can never get a current rule with an outdated instruction
- **Capability requirements:**
  - Supersession/amendment/reference edges between sources (staleness decision L7 validation gate inputs)
  - Template/instruction versioning tied to regulatory material versions (Data/Reporting SME, Meeting 2 L115)
- *Enables:* S2.2, VF2 entirely | *Ground truth:* decision `2025-06-14_corpus-update-and-staleness-policy`; Meeting 2 L115

### DI-4 - Structured content ingestion
- **As a** Technology team member
- **I want to** tables, reporting templates, rows/fields and instructions ingested as structured, addressable content, including links to the definitions a field depends on
- **so that** citations can point at row/field level and navigation can run in both directions
- **Capability requirements:**
  - Addressable locations for template/table/row/field/instruction references (provenance decision row 4)
  - Definition-dependency links for reporting fields (non-prose problem)
- *Enables:* S3.2, S1.2, S1.3 (VF3) | *Ground truth:* `wiki/problems/non-prose-regulatory-content.md`; decision `2025-06-04_minimum-provenance-standard`; kickoff L15

### DI-5 - Amendment intake and validation gate (staleness precursor)
- **As a** Regulatory Content Owner
- **I want to** Technology to detect and flag new/changed source material, with nothing activated until I validate authority, status, effective date and relationships
- **so that** the corpus stays current without unvalidated content entering it
- **Capability requirements:**
  - Detection/flagging pipeline output distinct from authoritative corpus state (detection does not establish relevance or authority - staleness decision L6)
  - Validation-gate workflow states for each candidate update (staleness decision L7, L12)
- *Enables:* VF2 superseded handling; precursor to STUB-1 (stale marking), STUB-3 (impact tracing) | *Ground truth:* decision `2025-06-14_corpus-update-and-staleness-policy`

### DI-6 - Version retention for audit (stub precursor)
- **As a** Regulatory Content Owner
- **I want to** historical source versions retained with their effective-date ranges
- **so that** any answer could later be checked against the material current at the time
- **Capability requirements:**
  - Historical versions with effective-date ranges queryable as-of date (feeds VF2 and future audit features)
  - Sufficient context preservation for later reconstruction (Meeting 3 L91-93)
- *Precursor to:* STUB-1 (stale marking), STUB-2 (answer audit store), STUB-3 (impact tracing) | *Ground truth:* Meeting 3 L9, L91-93; Q10


## VF1 - Core Copilot: ask, answer, verify (ref: breakdown v3, VF1)

The basic functionality - one question in, one verified evidence-led answer out. Stories re-filed from backlog v1 with IDs preserved.

### Story S1.1 - Natural-language search with regulatory-relevance ranking (Major Effort core) [v1 F1]
- **As an** experienced regulatory reporting analyst
- **I want to** ask a question in normal language and receive genuinely relevant authoritative sources from the curated corpus
- **so that** I can start from likely sources instead of trial-and-error searching across multiple documents
- **Scenario:** the first plausible result is not the operative requirement
- **Given** the curated corpus is loaded (VF0 DI-1) **and Given** my question concerns a capital-reporting requirement **and Given** several documents contain semantically similar terminology but differ in exposure class or calculation approach
- **When** I submit my question in plain language
- **Then** I receive a ranked set of sources ranked by regulatory relevance (scope, status, applicability), not merely terminology similarity, and none is presented as "the applicable provision"
- *Ground truth:* digest row 1; Meeting 2 L43-47; interview A2 L10-21 (source: 2025_06_18_interview_analyst2prov.md); decisions `2025-06-04_v1-scope-evidence-led-research`, `2025-06-04_bounded-curated-corpus`

### Spike F1-TAD - Relevance-ranking feasibility (time-boxed; learning, not deliverable) [v1 F1]
- **Question:** can ranking reliably separate semantically similar from regulatorily applicable results? Evaluate against the difficult-case set before finalizing S1.1 acceptance criteria. Feeds Q8.
- *Ground truth:* Meeting 2 L45-47; SME evaluation spec L133-137; both analysts' difficult-case lists (interviews)

### Story S2.1 - Status label and effective date on every result and answer [v1 F2]
- **As an** experienced regulatory reporting analyst
- **I want to** see the source status (final/operative, future-effective, superseded/historical, proposed/consultation, explanatory/supporting) and effective date on every search result and answer
- **so that** I can immediately tell whether material is operative without manually checking the document
- **Scenario:** mixed-status results
- **Given** my search returns documents in different statuses (e.g., final rules PS1/26 and consultation CP9/26) **and Given** source metadata exists (VF0 DI-2)
- **When** I view the result list or an answer
- **Then** every source shown carries its status label and effective/publication date visibly - in both search and answers
- *Ground truth:* decisions `2025-06-04_status-authority-labelling-ux`, `2025-06-04_date-based-temporal-mode`; desk research L6-9 (source: 2025_06_10_research_docversions.md)

### Story S2.3 - Evidence-led answer language [v1 F2]
- **As an** experienced regulatory reporting analyst
- **I want to** answers phrased as "The relevant sources indicate..." with source status visible, never "The applicable requirement is..." unless applicability has been validated
- **so that** I never mistake a proposal, consultation or explanatory publication for the operative requirement
- **Scenario:** consultation-derived evidence
- **Given** the best-matching evidence for my question is a consultation paper or explanatory publication **and Given** status labels are displayed per S2.1
- **When** the answer is generated
- **Then** it uses cautious evidence-led phrasing, labels the material proposed/consultation or explanatory/supporting, and never states the requirement definitively
- *Ground truth:* digest row 7; Meeting 2 L39, L105; `wiki/problems/authority-overstatement-risk.md`; `wiki/problems/requirement-applicability-determination.md`

### Story S3.1 - Verifiable citation for textual requirements [v1 F3]
- **As an** experienced regulatory reporting analyst
- **I want to** every claim drawn from textual regulatory material to carry a citation I can navigate to - document, version/status, and the exact section or paragraph, with surrounding context preserved
- **so that** I can independently verify the claim against the wording in seconds instead of re-searching the document
- **Scenario:** verifying a rule-based claim
- **Given** an answer relies on a provision in a final rule
- **When** I follow its citation
- **Then** I land on the exact section/paragraph, and the cited context shows what the answer claimed - including any qualification or condition
- *Ground truth:* decision `2025-06-04_minimum-provenance-standard`; interview A1 L55-57, L61-65 (source: 2025_06_17_interview_analyst1exp.md); interview A2 L59 (source: 2025_06_18_interview_analyst2prov.md)

### Story S3.3 - Surrounding-context navigation from a citation [v1 F3]
- **As an** experienced regulatory reporting analyst
- **I want to** expand from a cited provision to its surrounding passage or table context
- **so that** I can check qualifications, exceptions and conditions without searching the document again
- **Scenario:** qualified provision
- **Given** an answer cites a provision containing a qualification or exception
- **When** I open the citation's context view
- **Then** I see the surrounding passage including the qualification/exception, without leaving the answer
- *Ground truth:* Meeting 2 L57-59; interview A2 L59 ("click or navigate directly to the exact supporting provision"); decision `2025-06-04_minimum-provenance-standard`

**Instrumentation task (from dissolved F6/S6.2):** capture time-to-answer, sources/citations used, and outcome type (answer/refusal/escalation) for this feature's flows (scorecard decision row 3).


## VF2 - Temporal navigation (ref: breakdown v3, VF2)

### Story S2.2 - As-of-date answers [v1 F2]
- **As an** experienced regulatory reporting analyst
- **I want to** ask a question relative to a specified date (current as-of a reference date, or future-effective)
- **so that** I get the requirement applicable at that date, not just the newest publication
- **Scenario:** future-effective requirement
- **Given** a requirement has a future effective date (e.g., Basel 3.1 from 1 Jan 2027) **and Given** the current requirement remains operative until then **and Given** source relationships and versioning exist (VF0 DI-3)
- **When** I ask for the requirement applicable as of a date before the effective date
- **Then** the answer presents the currently operative requirement, with the future-effective version available and clearly labelled - and vice versa for a post-date query
- *Ground truth:* decision `2025-06-04_date-based-temporal-mode`; Meeting 2 L17, L23; interview A2 L98 ("latest" inadequate)

**Instrumentation task (dissolved F6/S6.2):** capture time-to-answer, citations used, outcome type for as-of-date flows; track superseded-selection correctness (difficult scenarios a, b).

## VF3 - Reporting-material connection (ref: breakdown v3, VF3)

### Story S3.2 - Verifiable citation for reporting material (templates, tables, instructions) [v1 F3]
- **As an** experienced regulatory reporting analyst
- **I want to** answers about reporting fields and templates to identify the specific template, table, row/field or reporting instruction that carries the requirement - and the definitions the field's meaning depends on
- **so that** I can verify reporting answers even when no single prose paragraph states the requirement
- **Scenario:** reporting-field answer with dependent definitions
- **Given** a question about a reporting field **and Given** the field's meaning depends on a definition and a reporting instruction located elsewhere in the corpus (template instructions alone are insufficient) **and Given** structured content is addressable (VF0 DI-4)
- **When** I inspect the citation
- **Then** it identifies the specific template/table/row/field/instruction reference **and** links the definitions it depends on, preserving context so I can validate the claim without reconstructing the trail myself
- *Ground truth:* digest row 4; kickoff L15; `wiki/problems/non-prose-regulatory-content.md`; interview A2 L63-75; interview A1 L65 (source: 2025_06_17_interview_analyst1exp.md)

### Story S1.2 - Forward navigation: rule -> reporting representation [v1 F1]
- **As an** experienced regulatory reporting analyst
- **I want to** start from a prudential rule and see how it is represented in reporting instructions and templates
- **so that** I can answer "how does this requirement appear in reporting?" without manually following references
- **Scenario:** forward navigation from a rule
- **Given** I am viewing a rule requirement **and Given** reporting instructions/templates implement that requirement **and Given** source relationships exist (VF0 DI-3)
- **When** I request the reporting view of the requirement
- **Then** I see the linked reporting instructions/templates and any reporting treatment described elsewhere, each with source status shown
- *Ground truth:* Meeting 2 L63-65; kickoff L15; `wiki/problems/terminology-cross-referencing.md`

### Story S1.3 - Backward navigation: reporting field -> underlying requirement [v1 F1]
- **As an** experienced regulatory reporting analyst
- **I want to** start from a reporting field or template cell and trace back to the underlying regulatory requirement
- **so that** I can answer "where does this field come from / what does it mean?" from the primary source, not just the template instruction
- **Scenario:** backward navigation from a template field
- **Given** I am viewing a reporting template field **and Given** the field's meaning depends on definitions or instructions elsewhere in the corpus **and Given** structured content is addressable (VF0 DI-4)
- **When** I request the regulatory basis of the field
- **Then** I am shown the underlying requirement(s) and the definitions it depends on, each with source status
- *Ground truth:* kickoff L13-15; Meeting 2 L61, L63-65; `wiki/problems/non-prose-regulatory-content.md`

### Story S1.4 - Related-material surfacing [v1 F1]
- **As an** experienced regulatory reporting analyst
- **I want to** see related definitions, reporting instructions and relevant changes alongside a source I am viewing
- **so that** I discover connections without manually hunting every reference
- **Scenario:** related material for a reporting requirement
- **Given** I am viewing a source **and Given** the corpus contains definitions, related instructions and changes connected to it (VF0 DI-3 relationships)
- **When** I open the source
- **Then** I see its related material in a form I can scan without it overwhelming the answer
- *Ground truth:* kickoff L51; interview A1 L140 ("surface related material without overwhelming the user"); digest row 1

**Instrumentation task (dissolved F6/S6.2):** capture time-to-answer, citations used, outcome type for reporting-question flows; track citation-granularity correctness for structured references (difficult scenario c).


## VF4 - Safe answers (ref: breakdown v3, VF4)

### Story S4.1 - Conflict exposure [v1 F4]
- **As an** experienced regulatory reporting analyst
- **I want to** conflicting sources presented side-by-side with their status and dates
- **so that** I can understand why the conflict exists and decide which statement applies - instead of receiving a silently resolved answer
- **Scenario:** two sources, different conclusions
- **Given** the corpus contains sources that appear to conflict (different dates, scopes, populations or detail levels)
- **When** an answer draws on both
- **Then** the answer presents both sources with their status/dates and an explicit conflict warning - it does not pick one silently
- *Ground truth:* `wiki/problems/conflict-exposure.md` (confirmed); Meeting 2 L67-71; digest row 7

### Story S4.2 - Insufficient-evidence statement [v1 F4]
- **As an** experienced regulatory reporting analyst
- **I want to** the system to state clearly when the available evidence is insufficient, conflicting or ambiguous
- **so that** I never receive a plausible-looking answer without strong support
- **Scenario:** insufficient corpus evidence
- **Given** the corpus does not contain evidence sufficient to answer the question confidently
- **When** I ask the question
- **Then** the system says so explicitly - naming what was searched and what is missing - rather than producing a low-support answer
- *Ground truth:* kickoff L89; Meeting 2 L77; digest rows 1, 3; assumption A3 (this story is its test vehicle, alongside S4.3)

### Story S4.3 - Evidence-backed escalation package [v1 F4]
- **As an** experienced regulatory reporting analyst
- **I want to** assemble a well-bounded escalation - the question plus the assembled evidence package - to hand to a regulatory SME
- **so that** the SME can focus on the judgement that requires expertise rather than re-doing my research
- **Scenario:** unresolved point requiring judgement
- **Given** I have gathered the relevant sources but a specific point requires SME confirmation **and Given** I can state what is uncertain and what needs resolving
- **When** I request an escalation package
- **Then** I receive a bounded summary: the question, the evidence with citations and status, and the specific unresolved point
- *Ground truth:* interview A1 L78-82 (source: 2025_06_17_interview_analyst1exp.md); interview A2 L83-87 (source: 2025_06_18_interview_analyst2prov.md); assumption A3; `wiki/problems/requirement-applicability-determination.md`

**Instrumentation task (dissolved F6/S6.2):** capture time-to-answer, citations used, outcome type for edge-state flows; track refusal/escalation appropriateness (safe-behaviour measures; feeds A3 test).

## Deferred stubs (prioritized later - recorded so nothing is silently dropped; F5 and post-V1)

### STUB-1 - Stale-answer marking (F5) - gated on Q10; builds on VF0 DI-5/DI-6
- **As an** experienced regulatory reporting analyst
- **I want to** answers that relied on superseded or amended material flagged as potentially stale and linked to the updated source/version
- **so that** I never act on an answer that silently became outdated
- **Blocking open point:** Q10 - staleness window/threshold; proactive re-review vs. flag-on-use (`wiki/open-questions.md`; source: 2025_06_14_meeting_latedocuments.md, L13)
- *Ground truth:* decision `2025-06-14_corpus-update-and-staleness-policy`; Meeting 3 L8, L11; `wiki/problems/no-feedback-loop.md`

### STUB-2 - Answer audit store (F5) - gated on retention decisions; builds on VF0 DI-6
- **As an** experienced regulatory reporting analyst
- **I want to** answers stored with full audit context - question, answer, citations, evidence versions used, temporal context
- **so that** any answer can later be reconstructed and checked against the material current at the time
- **Blocking open point:** data retention/ownership/reliance considerations (Meeting 2 L151) - not assumed in initial design
- *Ground truth:* Meeting 3 L9, L91-93; `wiki/problems/no-feedback-loop.md`

### STUB-3 - Impact-tracing capture (F5) - pairs with STUB-1/2; builds on VF0 DI-5/DI-6
- **As an** experienced regulatory reporting analyst
- **I want to** the recipient and basis-version of each answer recorded at capture time
- **so that** when an interpretation is later found outdated, we can determine who received it and whether related questions were answered the same way
- *Ground truth:* interview A1 L88-93 (source: 2025_06_17_interview_analyst1exp.md); interview A2 L91-96 (source: 2025_06_18_interview_analyst2prov.md); Q10 evidence

### STUB-4 - Newer-analyst learning-path support - revisit after a direct newer-analyst interview
- **As a** newer regulatory reporting analyst
- **I want to** understand why one source should be trusted over another and follow a guided research path
- **so that** I reach competence faster without depending on colleague availability
- **Blocking open point:** persona evidence is entirely second-hand (interviews A1 L101-113, A2 L104-114; kickoff L81, L113); a direct newer-analyst interview is required before design (v3 breakdown, conscious exclusion 3)
- *Ground truth:* `wiki/personas/newer-analyst.md`; `wiki/problems/experience-dependency.md`

### STUB-5 - Structured feedback categories - post-V1 F6 extension
- **As an** experienced regulatory reporting analyst
- **I want to** report why an answer was poor - incorrect answer, insufficient evidence, incorrect source, outdated source, irrelevant source, or correct but poorly explained
- **so that** corrections can be tied to the question, evidence and source version, improving research quality beyond thumbs-up/down
- **Blocking open point:** not prioritized for V1 (F5-adjacent); SME feedback-mechanism design
- *Ground truth:* Meeting 2 L85-89; `wiki/problems/no-feedback-loop.md` (confirmed)

## Split evaluation and validation

- **Vertical-slice check:** VF1 delivers the complete workflow (ask -> results -> answer -> citations -> verify) in its simplest form; VF2-VF4 each add a step/variation to the same workflow (Humanizing Work workflow-steps pattern). VF0 is the data foundation prerequisite (PM direction).
- **Low-value work revealed:** S1.4 (related material) and S2.2 (as-of-date) can be deprioritized behind VF1's core set, which alone delivers a verifiable answer end-to-end.
- **Boundary statement:** VF1's S2.1 owns how status/date is displayed; S3.1/S3.2 own the citation reference itself. S2.3 references S2.1's labels as a Given.
- **INVEST re-check:** all stories single Scenario/one When/Then; distinct so-thats (verified for S3.1 vs S3.2); S1.1 acknowledged as Major Effort; VF0 stories are Cohn gists by design (database-design conversation starters).

## Completeness statement (ground truth check)

- **Decisions (8/8):** v1-scope (epic/VF1/VF4) | temporal-awareness (S2.1/S2.2) | scorecard (per-feature instrumentation tasks + baseline note) | bounded-corpus (VF0 DI-1/DI-2 + exclusion) | date-based mode (S2.2; "no latest" in S2.1/S2.3) | provenance standard (S3.1/S3.2/S3.3) | status/labelling (S2.1/S2.3) | corpus-update/staleness (VF0 DI-5/DI-6 + STUB-1/2/3 + exclusion)
- **Problems (10/10):** evidence-assembly (epic north star), source-validation (S2.1/S2.2), citation-integrity (S3.x + invariant), conflict-exposure (S4.1), requirement-applicability (S2.3/S4.3 boundary), no-feedback-loop (S6.2 + STUB-1/2/3/5), authority-overstatement (S2.3), terminology-cross-referencing (S1.1/S1.4), non-prose (S1.3/S3.2), experience-dependency (STUB-4 + persona exclusion)
- **Assumptions:** A1 (baseline note + per-feature instrumentation + S1.1) | A2 (S3.x) | A3 (S4.2/S4.3 as test vehicle)
- **Open questions:** Q8 fed by F1-TAD + instrumentation tasks | Q10 gates STUB-1
- **VF0 enablers mapped:** DI-1 -> VF1 | DI-2 -> S2.1/S2.3/S3.1 | DI-3 -> S2.2/S1.2/S1.4 | DI-4 -> S3.2/S1.3 | DI-5 -> STUB-1/STUB-3 | DI-6 -> STUB-1/2/3

## Provenance

- Skills: `skills/user-story-splitting` (8 patterns), `skills/user-story` (Cohn + Gherkin for S-stories; Cohn gists for DI-stories), tested via `skills/epic-breakdown-advisor` against `Epic breakdown.md` -> `2025-06-18_epic-feature-breakdown-v2.md` -> v3.
- Story-chain: `2025-06-18_epic-hypothesis-regcopilot-v1.md` -> `2025-06-18_epic-feature-breakdown-v3.md` -> this backlog. Prior versions retained unchanged for audit.
- Ground truth: `wiki/decisions/` (8 active), `wiki/problems/` (10 pages), `wiki/assumptions.md`, `wiki/open-questions.md` (Q8, Q10), `wiki/personas/`, `sources/` as cited per story.
