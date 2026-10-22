# Task 4 — Assistant Design and Evaluation Report

## Objective

The SkillCraft brief asks for a persona-driven assistant that chains prompts or simulates a dialogue, adapts across turns, and documents the flow, conversation logs, and consistency improvements.

## Assistant: Ace, mock-interview coach

Ace helps a candidate practise for an intern or junior role. It asks for the role and level, asks three interview questions one at a time, evaluates answers, adjusts difficulty based on the previous score, and closes with a summary and average score.

## How the assistant flows

```text
Start
  ↓
Extract target role ── unclear ──► ask user to clarify
  ↓
Confirm level (intern/junior)
  ↓
Route user intent (answer/help/repeat/skip/quit/clarify/out-of-scope)
  ↓
Generate one interview question
  ↓
Receive answer → evaluate (score 1–5, strength, improvement tip)
  ↓
Update session state and difficulty
  ├─ fewer than 3 questions answered → next question
  └─ interview complete → personalised closing summary
```

The implementation is a Python state machine. Prompt templates live in `assistant/prompts.py`; orchestration, state, input handling, retries and fallbacks live in `assistant/engine.py`. The code keeps role, level, question count, scores, difficulty and transcript state between turns. It passes a compact state summary to each specialised prompt instead of asking one large prompt to do everything.

## Prompt chain

1. **Role extraction** — interpret the target job role and detect vague input.
2. **Intent routing** — classify commands and distinguish interview answers from unsupported requests.
3. **Question generation** — generate a single role- and level-appropriate question.
4. **Clarification** — restate or clarify the current question without advancing the interview.
5. **Answer evaluation** — return a bounded score, one strength, and one actionable tip.
6. **Final report** — summarise performance and calculate the average from session scores.

The engine validates model output and uses retries or deterministic fallbacks where needed. Commands include `help`, `repeat`, `skip`, and `quit`; empty input and unsupported requests are handled without incorrectly advancing the interview.

## Evidence and observed improvements

The repository contains scripted candidate inputs in `conversations/`, saved live-model transcripts in `results/`, offline tests in `tests/test_engine.py`, and generated metrics in `consistency_metrics.md`.

| Version | Scored answers | Turns with multiple questions | Turns referring to user as “the candidate” | Placeholder turns | Finished |
|---|---:|---:|---:|---:|---|
| v2.0 chained — happy path | 3/3 | 0 | 3 | 1 | Yes |
| v2.1 chained — happy path | 3/3 | 0 | 0 | 0 | Yes |
| v2.1 chained — ambiguous/unsupported | 1/2 | 0 | 0 | 0 | No |

The happy-path logs show improvements from v2.0 to v2.1: third-person references and bracket placeholders were removed while all three answers remained scored and the session finished. The ambiguous/unsupported sample did not finish and only one of two scripted answers received a numeric score; this is retained as a limitation rather than presented as a success.

## Testing

The offline unit-test suite contains 18 tests and passed in the validation run used for this portfolio. Tests use a fake backend with canned replies, so they validate state-machine behaviour, input handling, retries and fallbacks—not model quality. The saved conversation logs are live outputs from `qwen2.5:3b`; candidate turns in scripted runs are authored test inputs.

Run from the repository root:

```bash
python -m unittest discover -s SCT_PE_4/tests -v
python SCT_PE_4/compare_logs.py
```

## Improvements made for consistency

- Split the assistant into single-purpose prompts instead of a single broad prompt.
- Keep session state in code, reducing dependence on the model to remember earlier turns.
- Require one question per turn and validate generated questions.
- Validate evaluator output and constrain scores to the expected range.
- Add handling for vague roles, clarification, help, repeat, skip, quit, empty input and unsupported requests.
- Add retries and deterministic fallbacks for malformed or repetitive outputs.
- Compare versions using explicit transcript metrics and retain a failing/unfinished sample for honest evaluation.

## Limitations

The model is small and can still produce variable or incomplete responses. A successful unit-test run does not prove that every live model conversation will finish correctly. Only the saved runs listed in `results/` are evidence of live behaviour. The assistant is a practice tool, not a professional hiring assessment.
