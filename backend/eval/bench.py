"""Ragas model benchmark for RegCopilot answer synthesis.

Compares candidate local Ollama chat models against the baseline (gemma4:12b) on:
  - truthfulness-to-context  (Ragas `faithfulness`)
  - accuracy                 (Ragas `answer_correctness`)
  - relevance                (Ragas `answer_relevancy`)
  - cold/warm time-to-first-token and total response time (measured here)

Usage:
  python eval/bench.py --list-models
  python eval/bench.py --mode responses [--models gemma:2b --questions 0 1]
  python eval/bench.py --mode ragas
  python eval/bench.py --mode all

Retrieval is held fixed: the same bge-embedded pgvector contexts are used for every
model, so the chat model is the only variable.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import date
from pathlib import Path

import httpx
import ollama

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

EVAL_DIR = Path(__file__).resolve().parent
RESULTS_DIR = EVAL_DIR / "results"
EVAL_SET_PATH = EVAL_DIR / "eval_set.json"
RESPONSES_PATH = RESULTS_DIR / "responses.csv"
CONTEXTS_PATH = RESULTS_DIR / "contexts.json"
RAGAS_SCORES_PATH = RESULTS_DIR / "ragas_scores.csv"

OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest"
JUDGE_MODEL = "ministral-3:3b"
BASELINE = "gemma4:12b"
AS_OF_DATE = date(2027, 1, 1)
TOP_K = 12
WARM_RUNS = 3
NUM_PREDICT = 256

_OLLAMA = ollama.Client(host=OLLAMA_HOST, timeout=600)

# Family -> discovered tag. Auto-discovery via /api/tags reconciles this at runtime.
CANDIDATE_FAMILIES = {
    "phi": "phi3:3.8b",
    "smollm2": "smollm2:1.7b",
    "ministral": "ministral-3:3b",
    "nemotron-3-nano": "nemotron-3-nano:4b",
    "llama3.2": "llama3.2:1b",
    "granite": "granite4.2:3b",
    "gemma": "gemma:2b",
}


def list_ollama_tags() -> list[str]:
    r = httpx.get(OLLAMA_HOST + "/api/tags", timeout=300)
    r.raise_for_status()
    return [m["name"] for m in r.json().get("models", [])]


def resolve_models(include_baseline: bool) -> list[str]:
    """Return the exact candidate tags present locally, plus the baseline if requested."""
    available = list_ollama_tags()
    resolved = []
    for family, default_tag in CANDIDATE_FAMILIES.items():
        # prefer an exact tag that matches the family prefix, else the pinned default if present
        match = next(
            (t for t in available if t == default_tag or t.startswith(family)),
            None,
        )
        if match:
            resolved.append(match)
    if include_baseline and BASELINE in available:
        resolved.append(BASELINE)
    return resolved


def _stream_generate(model: str, prompt: str, keep_alive: str):
    """Stream one chat call via the ollama client; return (ttft_ms, total_ms, text, n_tokens)."""
    t0 = time.perf_counter()
    first = None
    parts = []
    stream = _OLLAMA.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        keep_alive=keep_alive,
        think=False,
        options={"temperature": 0, "num_predict": NUM_PREDICT},
    )
    for chunk in stream:
        tok = chunk["message"]["content"]
        if tok:
            if first is None:
                first = time.perf_counter()
            parts.append(tok)
    total = time.perf_counter()
    text = "".join(parts)
    ttft = (first - t0) * 1000 if first is not None else (total - t0) * 1000
    return ttft, (total - t0) * 1000, text, len(parts)


def _unload(model: str):
    """Load then immediately unload the model so a subsequent call is cold."""
    try:
        _OLLAMA.generate(model=model, prompt="ping", keep_alive=0, stream=False)
    except Exception:
        pass


def build_prompt(question: str, results: list[dict]) -> str:
    parts = []
    for i, r in enumerate(results):
        parts.append("[source %d] %s: %s" % (i + 1, r["title"], r["content"]))
    context = "\n".join(parts)
    return (
        "You are assisting a regulatory reporting analyst. "
        "Answer using only the sources below, phrased as evidence not certainty. "
        "Begin your answer with the exact words:\n The relevant sources indicate\n"
        "Never state that a provision is the applicable requirement. "
        "If the sources do not support an answer, say the evidence is insufficient.\n\n"
        "Sources:\n" + context + "\n\nQuestion: " + question
    )


def load_eval_set() -> list[dict]:
    return json.loads(EVAL_SET_PATH.read_text(encoding="utf-8"))


def retrieve_contexts(question: str) -> list[str]:
    from retrieval.retrieve import retrieve

    results = retrieve(question, AS_OF_DATE, top_k=TOP_K)
    return [r["content"] for r in results]


def run_responses(models: list[str], question_idx: list[int] | None):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    eval_set = load_eval_set()
    idx = question_idx if question_idx is not None else list(range(len(eval_set)))

    contexts_cache = {}
    if CONTEXTS_PATH.exists():
        contexts_cache = json.loads(CONTEXTS_PATH.read_text(encoding="utf-8"))

    rows = []
    for model in models:
        _unload(model)  # ensure a clean unloaded state before the first cold measurement

        warm_ttft = 0.0
        warm_total = 0.0
        response = ""
        n_tokens = 0
        cold_ttft, cold_total = 0.0, 0.0

        for i in idx:
            item = eval_set[i]
            question = item["question"]
            if question not in contexts_cache:
                contexts_cache[question] = retrieve_contexts(question)
            contexts = contexts_cache[question]

            # Use retrieve() output for the prompt (title + content), not raw contexts.
            prompt = build_prompt(question, [{"title": "source", "content": c} for c in contexts])

            warm_ttft, warm_total, text, nt = _stream_generate(model, prompt, keep_alive="5m")

            # first question is treated as cold; subsequent questions are warm
            if i == idx[0]:
                cold_ttft, cold_total = warm_ttft, warm_total
            else:
                cold_ttft, cold_total = 0.0, 0.0

            response = text
            n_tokens = nt

            opens = response.strip().startswith("The relevant sources indicate")
            rows.append({
                "model": model,
                "question": question,
                "cold_ttft_ms": round(cold_ttft, 1),
                "cold_total_ms": round(cold_total, 1),
                "warm_ttft_ms_mean": round(warm_ttft, 1),
                "warm_total_ms_mean": round(warm_total, 1),
                "n_tokens": n_tokens,
                "tokens_per_sec": round(n_tokens / (warm_total / 1000), 2) if warm_total else 0,
                "opens_with_required_phrase": opens,
                "response": response,
            })
            print(f"[{model}] q{i} cold_ttft={cold_ttft:.0f}ms warm_ttft={warm_ttft:.0f}ms "
                  f"warm_total={warm_total:.0f}ms nt={n_tokens}", flush=True)

    fieldnames = [
        "model", "question", "cold_ttft_ms", "cold_total_ms", "warm_ttft_ms_mean",
        "warm_total_ms_mean", "n_tokens", "tokens_per_sec", "opens_with_required_phrase",
        "response",
    ]

    # Preserve rows for models not being re-run, then overlay the new rows.
    merged = {}
    if RESPONSES_PATH.exists():
        with open(RESPONSES_PATH, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                merged[(r["model"], r["question"])] = r
    for r in rows:
        merged[(r["model"], r["question"])] = r

    question_order = {e["question"]: i for i, e in enumerate(eval_set)}
    model_order = list(CANDIDATE_FAMILIES.values()) + [BASELINE]

    def sort_key(r):
        m = model_order.index(r["model"]) if r["model"] in model_order else len(model_order)
        q = question_order.get(r["question"], len(eval_set))
        return (m, q)

    with open(RESPONSES_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in sorted(merged.values(), key=sort_key):
            w.writerow(r)

    CONTEXTS_PATH.write_text(json.dumps(contexts_cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(merged)} rows -> {RESPONSES_PATH}")


def run_ragas(judge_model: str = JUDGE_MODEL):
    import asyncio

    from openai import AsyncOpenAI
    from ragas.embeddings import OpenAIEmbeddings
    from ragas.llms import llm_factory
    from ragas.metrics.collections.answer_correctness import AnswerCorrectness
    from ragas.metrics.collections.answer_relevancy import AnswerRelevancy
    from ragas.metrics.collections.faithfulness import Faithfulness
    from ragas.run_config import RunConfig

    rows = list(csv.DictReader(open(RESPONSES_PATH, newline="", encoding="utf-8")))
    contexts = json.loads(CONTEXTS_PATH.read_text(encoding="utf-8"))
    references = {i["question"]: i["reference"] for i in load_eval_set()}

    client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=600)
    llm = llm_factory(judge_model, provider="openai", client=client, temperature=0)
    emb = OpenAIEmbeddings(client=client, model=EMBED_MODEL)
    rc = RunConfig(timeout=600, max_retries=1, max_workers=1)

    faith = Faithfulness(llm=llm, run_config=rc)
    corr = AnswerCorrectness(llm=llm, embeddings=emb, run_config=rc)
    rel = AnswerRelevancy(llm=llm, embeddings=emb, run_config=rc)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = ["model", "question", "faithfulness", "answer_correctness", "answer_relevancy"]
    f = open(RAGAS_SCORES_PATH, "w", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()

    async def _safe(metric, **kw):
        try:
            res = await metric.ascore(**kw)
            return float(res.value)
        except Exception as e:
            print(f"    !! {metric.__class__.__name__} error: {type(e).__name__}: {e}", flush=True)
            return None

    async def _one(r):
        q = r["question"]
        fv = await _safe(faith, user_input=q, response=r["response"], retrieved_contexts=contexts[q])
        cv = await _safe(corr, user_input=q, response=r["response"], reference=references[q])
        rv = await _safe(rel, user_input=q, response=r["response"])
        return {
            "model": r["model"],
            "question": q,
            "faithfulness": (round(fv, 4) if fv is not None else None),
            "answer_correctness": (round(cv, 4) if cv is not None else None),
            "answer_relevancy": (round(rv, 4) if rv is not None else None),
        }

    async def _run():
        for i, r in enumerate(rows):
            out = await _one(r)
            w.writerow(out)
            f.flush()
            print(f"[{i + 1}/{len(rows)}] {out['model']} :: {out['question'][:40]}", flush=True)

    asyncio.run(_run())
    f.close()
    print(f"Wrote Ragas scores -> {RAGAS_SCORES_PATH}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=["all", "responses", "ragas"], default="all")
    p.add_argument("--list-models", action="store_true", help="print resolved model tags and exit")
    p.add_argument("--models", nargs="*", help="override model tags (default: discover candidates + baseline)")
    p.add_argument("--questions", nargs="*", type=int, help="zero-based question indices to run")
    p.add_argument("--no-baseline", action="store_true", help="exclude gemma4:12b baseline from timing")
    p.add_argument("--judge", default=JUDGE_MODEL, help="judge model for Ragas scoring (default: ministral-3:3b)")
    args = p.parse_args()

    models = args.models if args.models else resolve_models(include_baseline=not args.no_baseline)

    if args.list_models:
        print("Resolved models:")
        for m in models:
            print("  " + m)
        return

    if not models:
        print("No candidate models found locally. Check `ollama list` / OLLAMA_HOST.")
        return

    print("Benchmarking models:")
    for m in models:
        print("  " + m)
    print()

    if args.mode in ("all", "responses"):
        run_responses(models, args.questions)
    if args.mode in ("all", "ragas"):
        run_ragas(args.judge)


if __name__ == "__main__":
    main()
