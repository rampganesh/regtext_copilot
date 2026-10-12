# Design

## Context

The project has only planning artefacts and a frozen prototype UI; there is no running backend. This design describes how the minimal search-and-answer backend is built. See proposal.md for motivation. The local machine runs PostgreSQL 18 as a native service (no Docker), and Ollama serves a local embedding model (bge-base-en-v1.5, 768 dimensions) and a chat model (gemma4:12b).

## Goals / Non-Goals

Goals:
- A runnable end-to-end path: ingest one PDF, chunk it, embed it, store it, then ask a question and receive an evidence-led answer with verified citations.
- Keep the deterministic correctness core (verbatim verification, approval filter, five status labels) even in the minimal slice.
- A swappable provider adapter so Ollama can later be replaced by OpenRouter without code changes elsewhere.

Non-Goals:
- Full temporal/status resolution rules, graph expansion, conflict detection, and reporting-material structured citations (deferred vertical features).
- Authentication, shared hosting, and stale-answer marking.
- Any use of LangChain or LlamaIndex - libraries only.

## Decisions

1. Python FastAPI backend with Pydantic schemas. Alternative: Node or a split Python/Node stack. Rationale: Python has the strongest PDF tooling and match the existing planning decisions; the frontend is one static HTML file so there is no UI cost.

2. PyMuPDF for PDF text extraction. Alternative: pdfplumber. Rationale: PyMuPDF is the strongest parser with per-character geometry; pdfplumber is kept only as a cross-check. Note the AGPL licence is acceptable for internal use pending compliance sign-off.

3. PostgreSQL with the pgvector extension as the single store. Alternative: a separate vector database. Rationale: one store, no second runtime; the relationship edge table can live alongside chunks later.

4. Location-based chunking (one paragraph to one chunk, no overlap). Alternative: fixed-token sliding windows. Rationale: stable citation locations and verbatim verification require non-overlapping, addressable chunks.

5. A provider adapter exposing chat and embed methods, implemented first for Ollama. Alternative: call the model directly. Rationale: keeps the provider swappable and keeps model specifics out of retrieval and synthesis modules.

6. A deterministic verification gate that checks every quoted span against stored chunk text after ignoring whitespace. Alternative: trust the model output. Rationale: the no-fabrication invariant is the hard acceptance condition.

## Risks / Trade-offs

- pgvector may not yet be installed in the local PostgreSQL 18 instance. Mitigation: confirm and install it as the first environment setup step.
- The local embedding model has a 512-token context limit. Mitigation: keep chunks short (paragraph level) so no chunk exceeds the limit.
- Database credentials for the local PostgreSQL service are not recorded anywhere. Mitigation: capture them in an environment file before wiring the database layer.
- Quantised embedding quality may be below an online baseline. Mitigation: accept for the prototype and revisit if retrieval quality disappoints.

## Open Questions

- Whether to run a precise as-of-date status resolver now or defer it and apply only the approval and published-date filters first.

