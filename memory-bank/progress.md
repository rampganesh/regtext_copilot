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
### Prototype (simple search-and-answer) — BUILT (2026-11-01)
- [x] Dependency install (fastapi, uvicorn, sqlalchemy, psycopg, pgvector, alembic, pytest, ...).
- [x] PostgreSQL 18 + pgvector 0.8.7 (`regcopilot` db) and Alembic migration.
- [x] `backend/` scaffold: `config.py`, `llm.py` (Ollama provider adapter), `db/models.py`,
  `ingest/` (extract/pipeline/cli), `retrieval/retrieve.py`, `synthesis/synthesize.py`,
  `verify/verify.py` (verbatim gate + sanitizer), `status/labels.py` (five labels),
  `api/main.py` (`POST /api/v1/ask` + serves the frozen prototype), `tests/`.
- [x] Seed ingest of `docs/ps126app1.pdf` — 1987 chunks embedded (bge-base-en-v1.5, 768-dim).
- [x] OpenSpec change tasks.md: 17/17 marked complete.
- [ ] Re-verify pytest suite green (one stale cached failure — `test_sanitizer_*` renamed during
  debugging); then the OpenSpec change can be archived.

### Chat-model selection — DECIDED (2026-11-01)
- 8 candidate Ollama chat models benchmarked on 16 factual PS1/26 questions (frozen top-k=12
  retrieval, `think=false`, temperature 0, evidence-led prompt). Scored manually against gold
  reference answers.
- **Adopt `nemotron-3-nano:4b`** as the synthesis model: 12/16 correct, grounded answers, ~2s mean
  TTFT. Outperforms + is ~4x faster than the prior default `gemma4:12b` (11/16, ~8.8s).
- Results: `backend/eval/results/manual_scores.csv` (128 per-question verdicts),
  `manual_summary.csv` (per-model), `bench.py` + `eval_set.json` (harness), `ragas_scores.csv`
  (partial LLM-judge output for completed runs).
- Open: **output-floor retrieval gap** — no model produced 72.5%; the fact sits in a formula chunk.
  Fix retrieval for numeric/formula sections, then re-run `bench.py` to confirm.

### Full V1 backlog (for reference — from the task breakdown)
- Phase 0a: F1–F7. Phase 0b: DI-1…DI-6, X2–X4. Phase 1: ST0-*, S1.1, S2.1, S2.3, S3.1, S3.3, P1-*.
  Phase 2: S2.2. Phase 3: S3.2, S1.2, S1.3, S1.4, P3-1. Phase 4: S4.1–S4.3, X7. All: X1.
- Deferred: STUB-1…STUB-5, auth/SSO, shared hosting, refresh SLA.

## Known issues / blockers
- **Thinking-mode models (2026-11-01):** `gemma4:12b`, `granite4.2:3b`, `nemotron-3-nano:4b` default
  to a `thinking` phase (`chunk.thinking` non-empty, `content` empty) on `ollama.chat`. Always pass
  `think=False` when timing/answer fields are needed (bench.py does this).
- **Ragas LLM-judge limitations (2026-11-01):** `ragas` collections metrics (`Faithfulness`,
  `AnswerCorrectness`, `AnswerRelevancy`) WORK with Ollama via `llm_factory` +
  `AsyncOpenAI(base_url='http://localhost:11434/v1')`. But (~a) ~10 judge calls/sample → slow
  (~25s/sample with ministral, so ~1h for 128 samples; gemma4:12b as judge would be ~4–10h),
  and (~b) the classic `ragas.evaluate` + `LangchainLLMWrapper(ChatOllama)` path **hangs** on
  Ollama — do not use it. ragas 0.4.3 also needs a site-packages shim for its stale
  `langchain_community.chat_models.vertexai` import (see `backend/eval/requirements-eval.txt`).
- **PyMuPDF AGPL** compliance sign-off pending (design open risk).
- **PowerShell `$variable` interpolation** is mangled by the command wrapper → use Python scripts or
  careful quoting for anything non-trivial in the shell.

## Status summary
- Project definition: **complete** (artefacts are thorough and internally consistent).
- Technical design: **reviewed** (satisfactory; improvement suggestions recorded in this session's
  conversation — tighter failure contracts, measurable ranking/glossary metrics).
- Implementation (prototype VF0-lite+VF1): **built and ingested**; unit tests to re-verify.
- Synthesis model: **selected (`nemotron-3-nano:4b`)** via empirical benchmark.
