# Task 1 — Writing Better Prompts

**Brief (SkillCraft, PE Task 01):** experiment with clarity, specificity, and tone. Take 3 vague
prompts, rewrite them into improved versions, and compare the outputs to understand how
prompt design affects LLM behaviour.

## Experiments

| # | Vague prompt | Improved prompt adds |
|---|---|---|
| 1 | "Write an email asking for an internship." | Role, HR audience, prompt-engineering focus, required parts, 120–160 words, no invented qualifications |
| 2 | "Explain binary search." | Beginner tutor persona, a sorted example array and target, steps, pseudocode, complexity, sorted-input requirement |
| 3 | "Make a social media post for my business." | LinkedIn, small-business audience, services, hook + 2 benefits + CTA, 100–140 words, ≤ 3 hashtags, no fabricated statistics |

## Files

| Path | Contents |
|---|---|
| [`prompts/`](prompts/) | The six prompts (`experimentN_original.txt`, `experimentN_improved.txt`) |
| [`results/`](results/) | The originally recorded responses (model and date not recorded; kept unedited) |
| [`results/rerun_qwen2.5-3b/`](results/rerun_qwen2.5-3b/) | A logged rerun of all six prompts with `qwen2.5:3b`, plus [`run_log.json`](results/rerun_qwen2.5-3b/run_log.json) |
| [`check_constraints.py`](check_constraints.py) | Automatic checks: word ranges, subject line, hashtags, placeholders, correctness of the binary-search examples, truncation |
| [`report/final_comparison_report.md`](report/final_comparison_report.md) | **Main report**: ratings, constraint results, findings, audit corrections |
| [`report/constraint_checks_recorded.md`](report/constraint_checks_recorded.md), [`report/constraint_checks_rerun.md`](report/constraint_checks_rerun.md) | Saved checker output |
| [`report/comparison_template.md`](report/comparison_template.md) | The blank template used to plan each comparison |

## Key findings

- The improved prompts produced on-topic responses for the intended audience in all six
  improved runs. The vague prompts produced generic text, a placeholder template, or (in the
  rerun) a clarifying question instead of a post.
- Only 5 of 8 length and format checks on the improved prompts passed. For example, the
  recorded email has no subject line, and the rerun post has 35 words instead of 100–140.
- A precise prompt did not prevent reasoning errors: the 3B model's binary-search traces loop
  incorrectly.
- The recorded chat outputs used personal and brand details that were not in the prompts, so
  hidden conversation context influenced them.

## How to verify

```bash
python SCT_PE_1/check_constraints.py                                 # recorded outputs
python SCT_PE_1/check_constraints.py SCT_PE_1/results/rerun_qwen2.5-3b

# Optional: reproduce the rerun (needs Ollama and `ollama pull qwen2.5:3b`)
python tools/run_prompts.py --out SCT_PE_1/results/rerun_qwen2.5-3b --seeds 42 \
    --temperature 0.7 SCT_PE_1/prompts/experiment{1,2,3}_{original,improved}.txt
```

Reruns on CPU can differ slightly even with the same seed. See the
[methodology](../docs/methodology.md).
