# Progress — RegCopilot V1

## What works (current state)
- **Discovery complete.** Read and consolidated all five key artefacts (epic hypothesis, feature
  breakdown v3, story backlog v2, task breakdown, solution intent) plus the prototype integration
  spec.
- **Memory bank initialised** (this folder) — project brief, product context, tech context, system
  patterns, active context, progress.
- **Environment verified:**
  - Python 3.12.10 venv at `.venv` (pydantic 2, pymupdf, pymupdf4llm, httpx, numpy present;
    fastapi/uvicorn/psycopg/pgvector/sqlalchemy/alembic/pytest/ruff/mypy **missing**).
  - PostgreSQL **18** service `postgresql-x64-18` running; install dir `D:\DS\pgadmin`.
  - **No docker.**
  - **Ollama 0.35.1** running; embedding + chat endpoints confirmed working.
- **Embedding/LLM recommendation delivered and verified:**
  - Embeddings: `hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest` → 768-dim (confirmed).
  - Chat: `gemma4:12b` (confirmed responding).
- **Seed corpus identified:** `docs/ps126app1.pdf` + `docs/ps126app1-output.md` (≈10k lines).

## What's left to build (from the requested deliverable)
### Prototype (simple search-and-answer) — NOT YET STARTED as code
- [ ] Confirm DB connection; install/verify pgvector extension into PostgreSQL 18.
- [ ] Install missing Python deps (fastapi, uvicorn, psycopg, pgvector, sqlalchemy, pytest, ruff, mypy).
- [ ] Scaffold `backend/` layout + tooling (requirements/pyproject, `.env`, README).
- [ ] DB schema + migration (sources, source_versions, chunks w/ vector, glossary).
- [ ] Minimal ingest pipeline (PyMuPDF → chunk → Ollama embed → store), seed with `ps126app1.pdf`.
- [ ] Retrieval (pgvector top-k) + status resolver stub + synthesis (evidence-led) + verbatim gate.
- [ ] FastAPI `POST /api/v1/ask` matching frozen contract + serve prototype HTML.
- [ ] Wire prototype `ask()` to API behind demo flag; end-to-end smoke test.

### Full V1 backlog (for reference — from the task breakdown)
- Phase 0a: F1–F7. Phase 0b: DI-1…DI-6, X2–X4. Phase 1: ST0-*, S1.1, S2.1, S2.3, S3.1, S3.3, P1-*.
  Phase 2: S2.2. Phase 3: S3.2, S1.2, S1.3, S1.4, P3-1. Phase 4: S4.1–S4.3, X7. All: X1.
- Deferred: STUB-1…STUB-5, auth/SSO, shared hosting, refresh SLA.

## Known issues / blockers
- **DB credentials** for PostgreSQL 18 unknown (interactive password prompt untestable
  non-interactively).
- **pgvector extension** not yet confirmed installed in PostgreSQL 18.
- **PyMuPDF AGPL** compliance sign-off pending (design open risk).
- **PowerShell `$variable` interpolation** is mangled by the command wrapper → use Python scripts or
  careful quoting for anything non-trivial in the shell.

## Status summary
- Project definition: **complete** (artefacts are thorough and internally consistent).
- Technical design: **reviewed** (satisfactory; improvement suggestions recorded in this session's
  conversation — tighter failure contracts, measurable ranking/glossary metrics).
- Implementation: **not started** — next action is to scaffold the project and build the minimal
  search-and-answer prototype against PostgreSQL + pgvector + Ollama.
