# Spec Delta

## Purpose

Lets an analyst ask a regulatory question in plain language and receive a relevant, evidence-led answer with verifiable citations drawn only from the approved corpus.

## ADDED Requirements

### Requirement: Evidence-led answer with verified citations
The system SHALL accept a plain-language question and an as-of date and return an answer that cites authoritative sources, with every quoted passage verified verbatim against the stored corpus before it is returned.

#### Scenario: Question retrieves a prose paragraph
- **WHEN** an analyst submits a question about a requirement stated in a prose paragraph, and the as-of date is today
- **THEN** the system returns an answer citing the operative source with a status label, a status date, and the surrounding passage including any qualification

#### Scenario: The relevant sources indicate phrasing
- **WHEN** an answer is generated
- **THEN** its first sentence is evidence-led and it never states that a provision is the applicable requirement

### Requirement: No fabricated citations
The system SHALL ensure that no citation, quotation, or reference that does not appear verbatim in a stored chunk ever reaches the analyst.

#### Scenario: A passage altered in generation
- **WHEN** generated text quotes a passage that does not match a stored chunk after ignoring whitespace
- **THEN** the citation is dropped or fails loudly in development, never silently returned

### Requirement: No confidence scores
The system SHALL NOT present a confidence score, ranking percentage, or similar measure of model certainty anywhere in its output.

#### Scenario: No score in any answer
- **WHEN** any answer is returned
- **THEN** the response contains no numeric confidence value

