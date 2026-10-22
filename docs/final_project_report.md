# SkillCraft Prompt Engineering — Final Project Report

## Executive summary

This portfolio implements the four tasks shown in the SkillCraft Technology Prompt Engineering brief (slides 57–60): writing better prompts, prompting for creativity, prompting for task automation, and simulating an assistant. The work includes prompts, outputs, evaluation reports, scripts, and validation evidence.

## Task outcomes

### Task 1 — Writing Better Prompts
Three vague prompts were rewritten with clearer roles, audience, output requirements, tone and constraints. Original and improved outputs are retained, with a comparison report and constraint checks. A logged rerun with `qwen2.5:3b` provides reproducible evidence for the rerun, while the provenance of the earlier recorded outputs is explicitly described as unknown.

### Task 2 — Prompting for Creativity
Four prompt variants isolate a baseline, persona/tone, structured output, and few-shot style guidance. Each variant has three outputs from `qwen2.5:3b` at temperature 0.8 (12 outputs total). The report compares tone, creativity and detail, with automatic output metrics and a note that rubric scores were assigned by the project reviewer rather than an independent panel.

### Task 3 — Prompting for Task Automation
The pipeline converts fictional meeting notes in multiple formats into a fixed JSON task-tracker schema. Five development inputs and two held-out inputs are scored against authored answer keys. The final recorded pipeline output is schema-valid for 7/7 inputs; field checks pass 48/57 on development data (84%) and 22/25 on held-out data (88%). The combined score is 70/82 (about 85%). A grounding check found that all 28 non-null dates and owners checked appeared in their source input. These are results on a small, fictional dataset and should not be interpreted as a general accuracy guarantee.

### Task 4 — Simulating an Assistant
Ace is a persona-driven mock-interview coach implemented as a state machine with specialised prompts. It adapts question difficulty based on scores and supports common user commands and unsupported requests. Eighteen offline unit tests passed. Saved live-model logs show that v2.1 improved the happy-path transcript metrics compared with v2.0, while an ambiguous/unsupported scenario remains unfinished; this limitation is documented.

## Reproducibility and tools

- Python 3.9+ is the documented baseline; code was syntax-compiled in the validation environment.
- Tasks 1–3 use Ollama with `qwen2.5:3b` for saved live outputs.
- Task 4's unit tests use a fake backend and do not require the model.
- See `docs/methodology.md` for evaluation choices and limitations, `docs/requirements_checklist.md` for a brief-aligned checklist, and each task README for commands.

## Submission checklist

- [x] Four task folders with prompts and evidence.
- [x] Reports, methodology, official brief transcription and checklist.
- [x] Offline Task 4 unit tests pass (18 tests).
- [x] Task 3 grounding check passes (28 date/owner checks).
- [x] Python files compile.
- [ ] Publish the repository to the user's GitHub account.
- [ ] Review and publish the required LinkedIn post after each task.

The final two actions require the user's own account and approval; this archive does not claim they have been completed.
