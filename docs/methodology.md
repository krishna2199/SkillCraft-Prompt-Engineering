# Methodology

This document explains how prompts were run, how outputs were recorded, and how they were
evaluated across all four tasks.

## 1. Model and runtime

| Item | Value |
|---|---|
| Runtime | [Ollama](https://ollama.com) running locally (no API key, no paid service) |
| Model | `qwen2.5:3b` (Qwen 2.5, 3B-parameter instruct model, Q4_K_M quantisation) |
| Hardware | Laptop CPU (AMD Ryzen 5 7520U, 16 GB RAM), no discrete GPU |
| Client | [`tools/ollama_client.py`](../tools/ollama_client.py) (Python standard library only) |

The exact Ollama version and model digest are written into each `run_log.json`.

**Why a small local model?** It is free, reproducible, and works offline. It also does not
need credentials, which keeps secrets out of a public repository. Its limits are part of the
findings: a 3B model makes mistakes that larger models may not. Those mistakes make the
effect of better prompts easier to see.

**Exception: Task 1's original outputs.** These were recorded before this repository used a
logged runtime. The model, date, and settings were not recorded. They are kept unchanged as
historical evidence. A fully logged rerun of the same six prompts with `qwen2.5:3b` sits
beside them in [`SCT_PE_1/results/rerun_qwen2.5-3b/`](../SCT_PE_1/results/rerun_qwen2.5-3b/).

## 2. Recording rules

1. **Outputs are never edited.** Every saved response is the raw model text. Generated files
   start with a short header that names the model, seed, temperature, and run time, followed
   by the unedited response. The raw text is also stored in the JSON run log.
2. **Settings are fixed and recorded.**

   | Task | Temperature | Seeds |
   |---|---|---|
   | Task 1 rerun | 0.7 | 42 |
   | Task 2 creative variants | 0.8 | 1, 2, 3 |
   | Task 3 extraction | 0 | 42 |
   | Task 4 assistant | 0 for JSON steps, 0.7 for free-text steps | 42 |

   Fixed seeds make runs *similar*, but **not guaranteed identical**. In this project, the same
   Task 1 prompt with seed 42 produced 128 tokens on one run and 117 on another, on the same
   machine. CPU threading can change the floating-point order. Different hardware or Ollama
   versions add more variation. The saved files are the record of what was actually produced.
3. **Authored inputs are labelled.** Task 3 meeting notes and Task 4 candidate turns were
   written by the author as fictional test inputs. They are stored as input files and are
   never presented as model output.
4. **Scores are separate from outputs.** Every score is either computed by a script or given
   by a human reviewer against a written rubric. Each score is labelled with which of the two
   it is.

## 3. Evaluation methods

| Task | What is measured | How |
|---|---|---|
| 1 | Compliance with each explicit constraint (word range, hashtags, subject line, placeholders, correctness of worked examples) | Automatic: [`SCT_PE_1/check_constraints.py`](../SCT_PE_1/check_constraints.py) |
| 1 | Relevance, clarity, structure, usefulness | Reviewer judgement with a written reason for each rating (see the Task 1 report) |
| 2 | Tone, creativity, detail (the three criteria named in the brief) | Reviewer rubric of 1–5 per criterion, each anchored to observable features; supported by automatic counts (words, headings, copying from the few-shot examples) |
| 3 | Valid JSON, schema compliance, field accuracy against a hand-written answer key | Automatic: [`SCT_PE_3/automate.py`](../SCT_PE_3/automate.py) |
| 4 | Engine correctness (state, routing, retries, fallbacks) | Automatic: 16 offline unit tests with a fake backend |
| 4 | Consistency of live conversations, v1 compared with v2 | Automatic turn metrics plus reviewer reading of the logs |

**About the reviewer scores.** The rubric scores in Tasks 1 and 2 were assigned by the AI
coding assistant that helped build this repository (Claude). They were not assigned by an
independent human panel. Each score cites the observable evidence behind it, so a reader can
check or change it.

## 4. What these experiments can and cannot show

- Task 2 uses 3 seeds per variant. Task 1 uses one response per prompt. These numbers are
  too small for statistical claims. The results show how one model behaved under recorded
  conditions. They are not general laws.
- Prompt quality and model quality interact. A prompt that helps a 3B model may matter less
  for a larger model.
- Automatic checks measure only what they test. For example, a correct due date does not
  prove that a summary is good. The scripts' definitions are documented so their limits are
  visible.
