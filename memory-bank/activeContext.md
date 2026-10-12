# Active Context — RegCopilot V1

## Current work focus (as of 2026-10-05)
**Building the initial prototype + barebones project structure.** User instructions in this session:
> "Build the initial prototype (should do a simple search and answer) and the barebones structure of
> the project to build on. You can use a PostgreSQL database to store the embeddings as per the
> design. For the embedding, can use a local model served on Ollama. Give me a recommendation."

Deliverable shape agreed from context:
- A working **simple search-and-answer** endpoint (`POST /api/v1/ask`) — a minimal VF0-lite + VF1
  slice: ingest a PDF → chunk → embed → store in Postgres/pgvector → retrieve → synthesize an
  evidence-led answer with citations.
- Frozen prototype UI wired to the real API behind a demo flag (`ask()` → `fetch('/api/v1/ask')`).
- **Barebones but correct structure** laid out per task F1: `backend/` with
  `api/ ingest/ retrieval/ status/ synthesis/ conflict/ verify/ db/`.
- **Local embeddings via Ollama** recommended (see techContext.md recommendation).

## Embedding recommendation (delivered)
**Use `bge-base-en-v1.5` served by Ollama** (already installed:
`hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest`, 768-dim). Chat/synthesis via **`gemma4:12b`**
(already installed). Rationale and caveats are in `techContext.md`. This satisfies spike F6 with the
"local BGE-class" option the design named.

## Environment facts that change the plan (verify before coding)
1. **No docker** on this machine → use the native **PostgreSQL 18** service at `D:\DS\pgadmin`
   (`psql.exe` at `D:\DS\pgadmin\bin\psql.exe`), NOT docker-compose.
2. **pgvector must be installed** into PostgreSQL 18 (extension `vector`) — not yet confirmed.
3. **DB credentials unknown** — need the postgres password/user/db name. Must confirm before wiring
   `db/`.
4. **Missing Python deps** to install: `fastapi`, `uvicorn`, `psycopg[binary]`, `pgvector`,
   `sqlalchemy`, `alembic`, `pytest`, `ruff`, `mypy`. (pydantic, pymupdf, httpx, numpy already
   present.)
5. **Ollama embedding model has a 512-token context** → keep chunks ≤ ~512 tokens.

## Immediate next steps
1. Confirm DB connection + install/verify `pgvector` extension into PostgreSQL 18.
2. Install the missing Python dependencies into `.venv`.
3. Scaffold `backend/` package layout + `pyproject.toml`/requirements + `.env` + README run
   instructions (task F1–F3 lite).
4. Implement `db/` schema (sources, source_versions, chunks w/ vector, minimal glossary) + migration.
5. Implement `ingest/` minimal pipeline: PyMuPDF parse → location-based chunk → Ollama embed → store.
   Seed with `docs/ps126app1.pdf`.
6. Implement `retrieval/` (pgvector cosine top-k) + `status/` (pure status resolver stub) +
   `synthesis/` (Ollama chat, evidence-led prompt) + `verify/` (verbatim gate) — minimal.
7. Implement `api/` FastAPI app exposing `POST /api/v1/ask` matching the frozen contract; serve the
   prototype HTML.
8. Wire the prototype `ask()` to the API behind a demo flag; smoke-test end-to-end.

## Important constraints to respect while building
- **No fabrication** — even the minimal prototype must verbatim-verify quoted passage text against
  stored chunk content before returning it.
- **Evidence-led phrasing** — answers start "The relevant sources indicate…".
- **No confidence scores** anywhere.
- **Five status labels only.**
- **Point-in-time filter** (`published_date ≤ asOfDate`) — even if statuses are simplistic at first.
- **Read-only respect for the artefacts** — never modify files in `artefacts/` (audit trail).
- **Libraries only** — do NOT use LangChain/LlamaIndex.

## Open questions / risks
- PyMuPDF AGPL compliance sign-off (design-blocking for Phase 0a).
- pgvector install + DB credentials.
- Ollama batch-embedding behaviour and Q4 quant retrieval quality (F6 spike).

## Decisions log
- 2026-10-05: Initial memory bank created. Embedding stack recommended and verified
  (bge-base-en-v1.5 768d + gemma4:12b via Ollama). Environment divergences from design recorded.
