# Task 2 — Prompting for Creativity

**Brief (SkillCraft, PE Task 02):** explore how prompt structure, tone, and examples influence
creative tasks. Use few-shot prompting to guide the model's style or persona. Run multiple
variants of a creative prompt and compare the results for tone, creativity, and detail.

## What was done

One creative challenge, *"generate a startup idea that solves a real-world problem"*, was
written as four prompt variants. Each variant isolates one technique:

| Variant | Technique |
|---|---|
| [v1](prompts/prompt_v1.txt) | Baseline |
| [v2](prompts/prompt_v2.txt) | Persona and tone |
| [v3](prompts/prompt_v3.txt) | Structured headings |
| [v4](prompts/prompt_v4.txt) | **Few-shot**: a mentor persona plus three example pitch cards |

Each variant was run 3 times (seeds 1–3, temperature 0.8) on `qwen2.5:3b`, giving
**12 genuine, unedited outputs**.

## Files

| Path | Contents |
|---|---|
| [`prompts/`](prompts/) | The four prompt variants |
| [`results/`](results/) | 12 outputs (`prompt_vN_seedS.md`) and [`run_log.json`](results/run_log.json) with settings and raw text |
| [`analyze_outputs.py`](analyze_outputs.py) | Objective metrics: words, required fields, startup names, numeric claims, overlap with the examples |
| [`report/automatic_metrics.md`](report/automatic_metrics.md) | Saved output of the metrics script |
| [`report/comparison_report.md`](report/comparison_report.md) | **Main report**: rubric, per-output scores, findings, recommendation |

## Key findings

| Variant | Tone | Creativity | Detail | In one line |
|---|---|---|---|---|
| v1 baseline | 2.0 | 2.0 | 4.0 | Long and detailed, generic voice, unsupported statistics |
| v2 persona | 4.0 | 3.3 | 3.0 | Lively founder voice; inconsistent structure |
| v3 structure | 2.0 | 2.0 | 3.7 | Always complete, but repeated safe ideas ("GreenThumb" twice) |
| v4 few-shot | 4.3 | 3.3 | 3.0 | Consistent format and playful voice; borrowed example ideas and had logic gaps |

Few-shot examples gave the strongest control over style and persona. They did not improve
the quality of the reasoning in a small model. The scores are rubric judgements; see the
report for how they were assigned.

## How to verify

```bash
python SCT_PE_2/analyze_outputs.py          # recompute the metrics from saved outputs

# Optional: regenerate outputs (needs Ollama and `ollama pull qwen2.5:3b`)
python tools/run_prompts.py --out SCT_PE_2/results --seeds 1 2 3 --temperature 0.8 \
    SCT_PE_2/prompts/prompt_v1.txt SCT_PE_2/prompts/prompt_v2.txt \
    SCT_PE_2/prompts/prompt_v3.txt SCT_PE_2/prompts/prompt_v4.txt
```
