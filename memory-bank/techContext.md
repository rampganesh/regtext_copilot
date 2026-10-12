# Tech Context — RegCopilot V1

## Agreed technical decisions (discussed and agreed with the team, 2026-10)
- **Backend:** Python 3.12 end-to-end — **FastAPI + Pydantic** (Uvicorn server).
- **PDF parsing:** **PyMuPDF** (primary), pdfplumber as occasional cross-check.
  ⚠️ **AGPL licence** — acceptable for internal, non-distributed tooling per working assumption;
  **compliance confirmation still pending before Phase 0a completes** (open risk).
- **Datastore:** **PostgreSQL 16 + pgvector** — single store, including the relationship edge table.
  Graph traversals via **recursive CTEs** behind a swappable `RelationshipGraph` interface
  (Neo4j remains a drop-in swap if V2 scale or STUB-3 impact tracing demands it).
- **LLM inference:** via a thin, swappable provider adapter. The design specifies **OpenRouter**
  for chat; embeddings endpoint was deferred to spike F6.
- **Synthesis:** fresh generation with citations, **mechanically verbatim-verified** (not extractive
  stitching).
- **Conflict detection:** LLM-assisted, structured output, deterministically validated
  (**explicit experiment**; rule-based candidates may be added and compared).
- **Chunking:** **location-based** (paragraph / row / definition), **no overlap**.
- **RAG framework:** **libraries only** (PyMuPDF, pgvector, OpenAI-compatible SDK) — **LangChain /
  LlamaIndex explicitly REJECTED** (the pipeline is deliberately non-generic: location chunking,
  deterministic reference extraction, status resolver, verification gate, no-scores invariant).
- **Auth/hosting:** **local development only for V1**, no SSO. Must be revisited before any
  deployment beyond local.
- **Build order (fixed):** **VF0 → VF1 → VF2 → VF3 → VF4**, mapped to phases 0a → 4.

## ⚠️ Environment reality vs. design (IMPORTANT — verified this session)
The local environment differs from the design in ways that must be reconciled:

### Python environment
- Active venv: `d:\DS\CG\regtext_copilot\.venv` (Python 3.12.10, pip 25.0.1).
- **Already installed:** `pydantic` 2.13.5, `httpx` 0.28.1, `numpy` 2.5.3, `pymupdf` 1.28.2,
  `pymupdf4llm` 1.28.2, `requests` 2.34.2, `langchain` 1.4.3 (present but *to be avoided* per the
  libraries-only decision), `networkx`, `tabulate`, `tenacity`.
- **NOT installed (required by design):** `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg`/`psycopg2`,
  `pgvector`, `alembic`, `pytest`, `ruff`, `mypy`. Install these before building the API/DB layers.

### Database — actual local setup
- **PostgreSQL 18** is running as a Windows service: `postgresql-x64-18` (Status: Running).
- Install directory: **`D:\DS\pgadmin`** (registry `HKLM\SOFTWARE\PostgreSQL\Installations\
  postgresql-x64-18`, Base Directory = `D:\DS\pgadmin`).
- `psql.exe` lives at **`D:\DS\pgadmin\bin\psql.exe`** (NOT on PATH — call it by full path).
- **docker is NOT available** on this machine → the planned `docker-compose.yml` cannot be used
  locally. Use the native PostgreSQL 18 service instead.
  - **pgvector availability unconfirmed** — the `vector` extension must be installed into
    PostgreSQL 18 before embeddings can be stored. Setup prerequisite.
  - **Connection details (user/password/db) still to be confirmed** — interactive `psql -U postgres`
    prompts for a password and could not be tested non-interactively.

### Ollama (local model serving) — RECOMMENDED STACK (verified working)
Ollama 0.35.1 is running on `http://localhost:11434`. Verified this session:

- **Embeddings:** `hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest` → **768-dim** vector.
  - Endpoint: `POST http://localhost:11434/api/embeddings` with `{"model": "...", "prompt": "..."}`
    (returns `{"embedding": [768 floats]}`). Confirmed working.
  - Model facts: BERT architecture, 109M params, context length 512, embedding length 768,
    quant Q4_K_M.
  - ⚠️ **512-token context limit** — chunks must be kept ≤ ~512 tokens for embedding; reinforces
    paragraph-level location chunking (DI4-3).
- **Chat/synthesis:** `gemma4:12b` (7.6 GB) — confirmed responding via
  `POST /api/generate` with `{"model": "gemma4:12b", "prompt": "...", "stream": false}`.
  - Chosen over `deepseek-r1:8b` (reasoning model — slow/unpredictable for strict JSON output) and
    `Llama-3.2-1B` (too weak for synthesis quality).
- Other available models: `deepseek-r1:8b`, `hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest`.

### Ollama embedding recommendation rationale
- **Use `bge-base-en-v1.5` — already installed and the right class of model for retrieval**
  (BGE is purpose-built for retrieval; 768 dims suits pgvector well).
- It satisfies design task **F6 (embedding model spike)**: this *is* the "local BGE-class" option the
  solution intent named as the alternative to OpenAI `text-embedding-3-small`. Choosing it keeps the
  whole stack local, private, and cost-free — appropriate for a local-dev-only V1.
- **Caveat to verify during F6:** Ollama's batch-embedding behaviour for many chunks, and whether Q4
  quantisation measurably hurts retrieval vs. the OpenAI baseline on the ~20 passage-pair spike.

### Shell note (this environment)
- Commands run through PowerShell, but `$variable` interpolation in inline commands gets mangled by
  the wrapper. **Prefer writing small Python scripts / using the venv Python** for anything involving
  variables, loops, or non-trivial scripting. Call tools by absolute path, e.g.
  `& 'd:\DS\CG\regtext_copilot\.venv\Scripts\python.exe'`.

## Providers in the design vs. this environment
| Concern | Design says | This environment |
|---|---|---|
| Chat LLM | OpenRouter (swappable adapter) | Ollama `gemma4:12b` locally — use behind the same adapter |
| Embeddings | Spike F6: OpenAI 3-small vs local BGE | Ollama `bge-base-en-v1.5` (768d) — the local BGE option |
| DB | PostgreSQL 16 + pgvector via docker-compose | PostgreSQL **18** native service at `D:\DS\pgadmin` (no docker) |
| Secrets | `.env` | `.env` (Ollama needs no key; no OpenRouter key required if local) |

**Design intent preserved:** the provider abstraction (`llm.py`: `chat(messages, json_schema) -> str`,
`embed(texts) -> vectors`) makes swapping Ollama ↔ OpenRouter a config/implementation detail.
Implement the Ollama provider first (local, free), keep the OpenRouter provider as the documented
alternative.


