# Task 4 — Simulating an Assistant

This task is a small mock-interview coach called Ace. It uses a consistent persona and a sequence of prompts to ask questions, review answers, and adjust the next question based on the conversation.

## Project files

- `assistant/` contains the conversation logic and prompt text.
- `conversations/` contains sample conversations, including an ambiguous request.
- `results/` contains saved outputs from earlier versions.
- `report/assistant_report.md` explains the flow and observations.
- `report/consistency_metrics.md` compares selected behaviour across saved runs.
- `run_assistant.py` starts the assistant locally.
- `compare_logs.py` calculates simple metrics from the saved conversation logs.

## Run locally

Use Python 3.9 or newer. The assistant can run in its offline/demo mode without a live model; live responses require the local Ollama service and model described in the project methodology.

## Notes

The sample conversations are examples for reviewing the assistant's behaviour, not a guarantee that every possible interview answer will be handled correctly. One ambiguous/unsupported scenario remains a limitation documented in the report.
