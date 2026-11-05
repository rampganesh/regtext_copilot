# Design

## Evidence

Benchmark harness: `backend/eval/bench.py` (frozen top-k=12 retrieval with the existing
bge embeddings, `think=false`, temperature 0, evidence-led prompt). 16 factual PS1/26 questions
with gold reference answers, manually scored.

Accuracy (correct / partial / wrong of 16) and warm first-token latency:

| Model | Correct | Partial | Wrong | warm TTFT mean |
|---|---|---|---|---|
| nemotron-3-nano:4b | 12 | 0 | 4 | ~2.0 s |
| ministral-3:3b | 11 | 1 | 4 | ~2.7 s |
| gemma4:12b (baseline) | 11 | 1 | 4 | ~8.8 s |
| granite4.2:3b | 10 | 2 | 4 | ~2.0 s (repetition loops) |
| phi3:3.8b | 9 | 2 | 5 | ~5.3 s |
| llama3.2:1b | 8 | 2 | 6 | ~0.5 s (largest hallucinations) |
| smollm2:1.7b | 8 | 0 | 8 | ~1.3 s |
| gemma:2b | 7 | 1 | 8 | ~0.9 s |

Full detail: `backend/eval/results/manual_scores.csv`, `manual_summary.csv`.

## Thinking-mode mechanism

`nemotron-3-nano:4b`, `gemma4:12b`, and `granite4.2:3b` are thinking-mode models in Ollama: by
default a streamed response emits reasoning in a `thinking` field while `content`/`response` stays
empty until reasoning completes; TTFT balloons (gemma4:12b ~50 s in the first benchmark run). The
Ollama API (`/api/generate` and `/api/chat`) accepts a top-level `think: false` boolean that skips
the thinking phase and returns only the final answer. Verified against Ollama 0.35.1 on
2026-11-01: `POST /api/generate` with `think: false` returns a non-empty `response` and
`thinking: null`.

## Decisions

- Keep the existing `/api/generate` provider path (adds `think: false`); switch to `/api/chat` only
  if the installed Ollama ever rejects the flag (it does not today).
- Embeddings unchanged (`bge-base-en-v1.5`, 768-dim) - retrieval is model-independent.
- Eval harness (`backend/eval/bench.py`) keeps `gemma4:12b` as the comparison baseline and
  `ministral-3:3b` as Ragas judge; it is a dev tool, not production config.

## Known follow-up (out of scope)

The output-floor question (x = 72.5%) was missed by every model; the fact lives in a dense formula
chunk that retrieval surfaces but models misread. Tracked in the memory bank as an open retrieval
issue.
