# Proposal

## Why

The prototype's synthesis model, `gemma4:12b`, has a time-to-first-token of roughly 8-9 seconds, dominated by its thinking phase. The 2026-11-01 model benchmark (8 local Ollama chat models x 16 factual PS1/26 questions, frozen retrieval, manual scoring against gold reference answers) showed `nemotron-3-nano:4b` is MORE accurate (12/16 versus 11/16 for gemma4:12b), stays grounded, and answers about four times faster (~2 s first-token). Using it improves analyst experience without giving up correctness.

## What Changes

- Change the default synthesis chat model from `gemma4:12b` to `nemotron-3-nano:4b`.
- Invoke chat generation with thinking disabled (`think: false`) so thinking-mode models return only the final answer in the response text.
- Update the README stack note to reflect the model choice.

## Capabilities

### New Capabilities

- synthesis-model: the configured local chat model is invoked with thinking disabled so the returned answer contains only the final answer text.

### Modified Capabilities

(none - the ask-answer and corpus-ingest behaviours are unchanged; only the configured model and generation flag change)

## Impact

- `backend/config.py`: default `OLLAMA_CHAT_MODEL` becomes `nemotron-3-nano:4b` (still env-overridable).
- `backend/llm.py`: generation payload includes `think: false`.
- `README.md`: stack bullet updated.
- No database, schema, or corpus changes. Rollback is a one-line env override (`OLLAMA_CHAT_MODEL=gemma4:12b`).
