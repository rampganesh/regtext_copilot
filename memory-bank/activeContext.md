# Active Context — RegCopilot V1

## Current work focus (as of 2026-11-01)
**Model benchmark complete — chat-model selection decided.** The functional prototype backend is
built (see progress.md). This week the chat model for synthesis was evaluated empirically:
8 local Ollama models × 16 factual PS1/26 questions, fixed top-k=12 retrieval, `think=false`,
evidence-led prompt, temperature 0.

- Full details: `backend/eval/` (bench.py harness, eval_set.json, results/).
- Manual per-question judgements: `backend/eval/results/manual_scores.csv`;
  summary: `backend/eval/results/manual_summary.csv`.
- Outcome: **nemotron-3-nano:4b is the recommended synthesis model** — highest accuracy (12/16),
  stays grounded, ~4x faster TTFT (~2s) than the gemma4:12b baseline (~9s). Runner-up
  `ministral-3:3b` (11/16, ~2.7s).
- **gemma4:12b scored 11/16 but is 4x slower than Nemotron → no longer recommended for synthesis.**
- Open retrieval gap to fix: **no model could answer the output-floor question** (x=72.5% lives in a
  dense formula chunk that retrieval surfaces but models misread). Chunking/query handling for
  formula-heavy sections needs work.

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
- 2026-11-01: **Chat-model benchmark executed** (8 Ollama models × 16 PS1/26 factual questions,
  fixed top-k retrieval, judge-agnostic manual scoring). **Selected `nemotron-3-nano:4b`** as the
  synthesis model (best accuracy 12/16, ~2s TTFT). gemma4:12b (11/16, ~9s TTFT) superseded.
  Discovered that gemma4:12b/granite4.2/nemotron default to **thinking mode** (`think=false` needed
  via Ollama chat); without it they return `thinking` text with empty `content` and appear slow/
  unresponsive. Known open risk: output-floor numeric extraction (retrieval chunk quality).
- 2026-11-01: The OpenSpec change `initial-functional-prototype-with-basic-functionality` was built
  (backend scaffold + ingest + retrieval + synthesis + verify + FastAPI + tests); 17/17 tasks
  marked complete; one cached pytest failure to re-check. Ragas-based eval harness lives in
  `backend/eval/` (works; Ragas LLM-judge is slow — manual judging used for the decision).
