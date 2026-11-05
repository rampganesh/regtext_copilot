# Tasks

## 1. Change scaffolding

- [x] 1.1 Create the OpenSpec change scaffold (proposal, design, tasks, spec delta)

## 2. Code

- [x] 2.1 Confirm `/api/generate` accepts `think: false` for nemotron-3-nano:4b and returns non-empty response text with no thinking content
- [x] 2.2 Change the default synthesis chat model to `nemotron-3-nano:4b` in `backend/config.py` (env override retained)
- [x] 2.3 Add `think: false` to the generation payload in `backend/llm.py`; keep temperature 0 and non-streamed response

## 3. Documentation

- [x] 3.1 Update the README Ollama stack note to name `nemotron-3-nano:4b` (chat, thinking disabled)

## 4. Verification

- [x] 4.1 Run `openspec validate switch-synthesis-model-nemotron --strict` and confirm it is clean
- [x] 4.2 Run the backend test suite and confirm all tests pass
- [x] 4.3 Smoke-test the real endpoint with two benchmark questions and confirm: evidence-led opener, non-empty answer, verified citations, no thinking text, visibly faster first token
- [x] 4.4 Repeat one question twice and confirm the answer is identical (determinism)

## 5. Finalise

- [ ] 5.1 Archive the change per the repo archive workflow

