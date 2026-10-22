# Task 3 — Prompting for Task Automation

**Brief (SkillCraft, PE Task 03):** apply prompting to semi-automate a real-world task. Design a
clear, consistent prompt that handles multiple inputs reliably. Submit the prompt, at least 3
input-output examples, and a short reflection on prompt iteration or debugging.

## What was built

A pipeline that turns meeting notes in any format (bullets, chat logs, emails, prose) into
one fixed **task-tracker JSON** schema:

```text
notes.txt ─► prompt_v3_rules ─► qwen2.5:3b (JSON mode, temp 0) ─► parse ─► fill missing keys with null
          ─► schema validation ─► (if invalid) one retry with the errors ─► result.json + scorecard
```

**Final result:** all 7 inputs are schema-valid, with **84%** field accuracy on the 5
development inputs and **88%** on 2 held-out inputs. None of the 28 extracted dates and
owners was invented.

## Files

| Path | Contents |
|---|---|
| [`prompts/prompt_v3_rules.txt`](prompts/prompt_v3_rules.txt) | **The final prompt** |
| [`prompts/`](prompts/) | All five prompt versions (v1 basic → v5 recap rule) |
| [`inputs/`](inputs/) | 7 fictional meeting notes (06 and 07 are held-out) |
| [`expected/`](expected/) | Hand-written answer keys used for scoring |
| [`results/prompt_v3_rules_json_retry_normalize/`](results/prompt_v3_rules_json_retry_normalize/) | **Final input → output examples**: `*.output.txt` (raw), `*.json` (validated), [`scorecard.md`](results/prompt_v3_rules_json_retry_normalize/scorecard.md), `run_log.json` |
| [`results/`](results/) | One folder per iteration, each with its own scorecard |
| [`automate.py`](automate.py) | The automation and scoring script |
| [`check_grounding.py`](check_grounding.py) | Checks that every extracted date and owner appears in the input |
| [`report/reflection.md`](report/reflection.md) | **Report and reflection**: iteration table, debugging lessons, limitations |

## Example (input 07, held-out)

Input ([`inputs/07_heldout_reversal.txt`](inputs/07_heldout_reversal.txt), excerpt):

```text
We first agreed to make an offer to candidate B. After Yuki shared reference feedback, we
changed our minds and agreed to invite candidate B for a second technical interview instead.
Marco will schedule the second interview next week.
Aisha to send the reference summary to HR by 2026-09-05.
```

Output ([`results/.../07_heldout_reversal.json`](results/prompt_v3_rules_json_retry_normalize/07_heldout_reversal.json)):
records only the final decision (a second interview, not the offer), Marco's task with
`"due_date": null` (because "next week" is not an exact date), and Aisha's task due
`2026-09-05`. It passed 11/11 checks.

## How to run

Requires [Ollama](https://ollama.com) and `ollama pull qwen2.5:3b`. Python standard library only.

```bash
# Final pipeline on all inputs, scored against expected/
python SCT_PE_3/automate.py --prompt prompts/prompt_v3_rules.txt \
    --json-mode --retry --normalize --tag json_retry_normalize

# Your own notes (no answer key, so no scoring)
python SCT_PE_3/automate.py --prompt prompts/prompt_v3_rules.txt \
    --json-mode --retry --normalize --tag my_run --input path/to/notes.txt

# Re-score saved runs without a model; check for invented values
python SCT_PE_3/automate.py --prompt prompts/prompt_v3_rules.txt --tag json_retry_normalize --rescore
python SCT_PE_3/check_grounding.py
```
