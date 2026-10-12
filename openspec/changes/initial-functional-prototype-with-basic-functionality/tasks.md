# Tasks

## 1. Environment and scaffold

- [x] 1.1 Create the backend project structure and dependency file, then verify the test runner collects tests in a clean run
- [x] 1.2 Record database and Ollama settings in an env file, then verify the env values load
- [x] 1.3 Install the pgvector extension into PostgreSQL and verify a query reports the extension is available
- [x] 1.4 Add a migration for the sources, source_versions, and chunks tables, then verify the migration applies and rolls back

## 2. Provider adapter

- [x] 2.1 Implement the llm.py adapter with chat and embed methods and verify both methods round-trip against Ollama
- [x] 2.2 Set temperature 0 and retry-once behaviour and verify a non-conforming response is retried then fails loudly

## 3. Ingestion

- [x] 3.1 Implement PyMuPDF text extraction and paragraph chunking, then verify a sample PDF produces non-empty chunks
- [x] 3.2 Implement location identifier assignment and verbatim text storage, then verify identifiers are unique per version
- [x] 3.3 Implement embedding and storage of chunks, then verify each chunk has a stored vector
- [x] 3.4 Implement the approval gate, then verify an unapproved source is never returned by retrieval

## 4. Retrieval and answer

- [x] 4.1 Implement vector retrieval with the approval and published-date filters, then verify a keyword question returns the expected chunk
- [x] 4.2 Implement the evidence-led synthesis prompt, then verify the answer starts with the relevant sources indicate phrasing
- [x] 4.3 Implement the verbatim verification gate, then verify an altered quote is dropped or fails loudly

## 5. API and UI wiring

- [x] 5.1 Implement the ask endpoint and schema, then verify the endpoint returns the frozen contract for a valid question
- [x] 5.2 Serve the prototype HTML and wire the ask action to the endpoint behind a demo flag, then verify a question shows an answer in the browser

## 6. Verification

- [x] 6.1 Write unit tests for the verbatim gate, sanitizer, and status labels, then verify the full test suite passes
- [x] 6.2 Run an end-to-end ask against the seed document and verify the answer has verified citations and no confidence score

