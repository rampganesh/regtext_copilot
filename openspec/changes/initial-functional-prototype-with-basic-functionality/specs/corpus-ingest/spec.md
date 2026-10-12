# Spec Delta

## Purpose

Loads approved regulatory documents into a searchable, addressable corpus so the ask-answer capability can retrieve and cite exact passages.

## ADDED Requirements

### Requirement: Structured corpus ingestion
The system SHALL ingest an approved regulatory document into addressable chunks, each with a stable location identifier and its verbatim text stored as the source of truth.

#### Scenario: A document is ingested
- **WHEN** an approved document is loaded
- **THEN** its paragraphs and definitions become chunks with unique location identifiers and verbatim text preserved

### Requirement: Embedding of chunks
The system SHALL embed each chunk using a configured local embedding model and store the vector such that semantic search can retrieve it.

#### Scenario: A chunk is embedded and stored
- **WHEN** a chunk is created
- **THEN** a vector is computed and stored with the chunk in a searchable index

### Requirement: Approval gate
The system SHALL NOT make a source retrievable until a content owner explicitly approves it.

#### Scenario: Unapproved source is not retrievable
- **WHEN** a source has not been approved
- **THEN** retrieval never returns any chunk of that source

