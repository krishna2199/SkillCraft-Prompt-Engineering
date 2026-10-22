# Task 2 — Prompting for Creativity: Comparison Report

## Objective (from the official brief)

> Explore how prompt structure, tone, and examples influence creative tasks. Use few-shot
> prompting to guide the model's style or persona. Design a prompt that generates creative
> outputs, run multiple variants of your prompt, and compare the results for tone,
> creativity, and detail.

## Design

**Creative challenge (the same for every variant):** generate one startup idea that solves a
real-world problem.

| Variant | Technique isolated | Prompt |
|---|---|---|
| v1 | Baseline: no persona, structure, or examples | [`prompt_v1.txt`](../prompts/prompt_v1.txt) |
| v2 | **Persona and tone**: "imaginative startup founder", "engaging, optimistic tone" | [`prompt_v2.txt`](../prompts/prompt_v2.txt) |
| v3 | **Structure**: seven required headings, "specific, practical, and concise" | [`prompt_v3.txt`](../prompts/prompt_v3.txt) |
| v4 | **Few-shot persona and style**: a witty mentor persona ("Spark") plus **three example pitch cards**, with instructions to copy their style but not their ideas | [`prompt_v4.txt`](../prompts/prompt_v4.txt) |

**Runs:** each variant was run with 3 seeds (1, 2, 3) at temperature 0.8, giving 12 genuine
outputs from `qwen2.5:3b` via Ollama. The settings and raw text are in
[`../results/run_log.json`](../results/run_log.json). No output was edited.

> **Audit note:** the earlier draft of v4 had a single example, which is one-shot, not
> few-shot. The brief explicitly asks for few-shot prompting, so v4 was rewritten with three
> examples **before** any outputs were generated.

## Rubric

Each output was scored 1–5 on the brief's three criteria. The scorer was the AI assistant that
built this repository, not an independent panel (see the [methodology](../../docs/methodology.md)).
The anchors are:

| Score | Tone | Creativity | Detail |
|---|---|---|---|
| 1 | Flat or boilerplate | A common idea with a generic name | Vague; key parts missing |
| 3 | Pleasant but generic; little personality | A familiar idea with one fresh twist | Covers who, how, and money, but generically |
| 5 | A distinctive, consistent voice that fits the requested persona | An unusual problem or angle, with a memorable name and hook | Concrete, specific, internally consistent, and actionable |

Accuracy and coherence problems are listed separately as **flags** and are not hidden inside
the scores. Objective counts (length, required fields, name repetition, copying from the
examples, numeric claims) come from [`analyze_outputs.py`](../analyze_outputs.py). They are
saved in [`automatic_metrics.md`](automatic_metrics.md).

## Scores

| Output | Idea | Tone | Creativity | Detail | Flags |
|---|---|---|---|---|---|
| [v1 seed 1](../results/prompt_v1_seed1.md) | GreenThumb: sensor-based smart gardening | 2 | 2 | 4 | **Unsupported statistic:** "CAGR of 7% from 2020 to 2027" |
| [v1 seed 2](../results/prompt_v1_seed2.md) | FreshlyFed: matching surplus farm food with food banks | 2 | 2 | 4 | Uncited "one-third of all food" figure (widely reported, but no source given) |
| [v1 seed 3](../results/prompt_v1_seed3.md) | EcoCycle: recycling collection subscription | 2 | 2 | 4 | none |
| [v2 seed 1](../results/prompt_v2_seed1.md) | ChronoSync: AI time-management platform | 4 | 3 | 2 | No revenue model; features are abstract |
| [v2 seed 2](../results/prompt_v2_seed2.md) | EcoSnooze: nap-optimised seats in subscription EVs | 4 | 4 | 3 | **Unsupported claim:** "clinically-tested brainwave optimization"; unclear who drives while users nap |
| [v2 seed 3](../results/prompt_v2_seed3.md) | SmartSewer: IoT and AI wastewater monitoring | 4 | 3 | 4 | **Unsupported statistic:** "14 billion gallons … each day" |
| [v3 seed 1](../results/prompt_v3_seed1.md) | GreenThumb: produce subscription | 2 | 2 | 3 | **Contradiction:** the solution delivers produce, but the features are gardening kits |
| [v3 seed 2](../results/prompt_v3_seed2.md) | GreenThumb: hydroponic vertical gardens | 2 | 2 | 4 | "Soil moisture" sensors in a soil-free hydroponic system |
| [v3 seed 3](../results/prompt_v3_seed3.md) | EcoCycle: integrated urban waste platform | 2 | 2 | 4 | Unrealistic startup scope (building digestion and waste-to-energy plants) |
| [v4 seed 1](../results/prompt_v4_seed1.md) | WorryWise: anonymous worry support | 5 | 4 | 3 | Sensitive mental-health area with no safeguarding; odd "pricing by worry level" |
| [v4 seed 2](../results/prompt_v4_seed2.md) | PeakPeek: weekend gig matching | 4 | 3 | 3 | The problem and users don't match ("busy professionals" vs "freelancers"); borrows the "quick approval" idea from example ShiftSwap |
| [v4 seed 3](../results/prompt_v4_seed3.md) | NightCycle: e-bike charging reservations | 4 | 3 | 3 | The hook (phone charging) doesn't match the product; features mirror example RefillRoute ("real-time … alerts; price comparison") |

### Averages per variant

| Variant | Tone | Creativity | Detail | Mean words | Required fields | Distinct names (3 seeds) | Numeric claims without a source |
|---|---|---|---|---|---|---|---|
| v1 baseline | 2.0 | 2.0 | **4.0** | 418 | n/a | 3/3 | 2 |
| v2 persona and tone | 4.0 | **3.3** | 3.0 | 448 | n/a | 3/3 | 1 (+1 unsupported clinical claim) |
| v3 structure | 2.0 | 2.0 | 3.7 | 325 | 7/7 in all 3 | **2/3** (GreenThumb twice) | 0 |
| v4 few-shot | **4.3** | **3.3** | 3.0 | 139 | 8/8 in all 3 | 3/3 | 0 |

The word counts, field coverage, names, and numeric claims are automatic (see
[automatic_metrics.md](automatic_metrics.md)). The tone, creativity, and detail scores are the
rubric scores above.

## Findings

1. **Few-shot examples were the strongest control over style.** All three v4 outputs
   reproduced the pitch-card format with all 8 fields and a short quoted hook. They stayed
   short: 126–152 words, compared with 89–95 words in the examples and about 420–450 words
   for v1 and v2. The playful mentor voice came
   through in hooks such as *"Your worries are finally heard."* No other variant produced a
   consistent format and voice.
2. **A persona changed the tone, not the format.** v2 wrote in the first person with
   founder-style optimism ("Let's make every second count…"). Its structure, however, varied
   from seed to seed, and one output (ChronoSync) had no business model at all.
3. **Structure improved completeness but not originality.** v3 always produced all 7 headings.
   But its ideas fell back to the safest themes: **"GreenThumb" appeared twice in v3 and once
   in v1, and "EcoCycle" once in v1 and once in v3**. Asking for headings did not ask for
   novelty, and none was produced.
4. **The baseline was detailed but generic.** v1 wrote the longest responses, with many
   features and revenue streams, in a generic assistant voice ("Absolutely, here's…"). It
   also produced unsupported market statistics.
5. **Few-shot has a cost: content leakage and weaker reasoning.** The 4-gram overlap with the
   examples was low (1.4–2.1%), so v4 did not copy wording. It did copy **ideas**:
   NightCycle's features mirror RefillRoute's, and PeakPeek borrows ShiftSwap's approval flow.
   Two of the three v4 cards also have internal logic gaps. A 3B model imitates surface style
   more reliably than it reasons about a new idea.
6. **The format affected fabrication.** Unsupported statistics appeared only in the free-form
   variants (v1, v2), which included "market opportunity" or "why it matters" sections.
   Neither fixed format invited them. With 3 seeds per variant this is an observation, not a
   proven cause.

## Recommendation

Combine the techniques: use **few-shot examples for voice and format**, **an explicit field
list for completeness**, and a constraint such as *"do not include statistics unless the
user provides them"*. A follow-up experiment could test whether adding a "check your idea for
contradictions" step reduces the logic gaps seen in v4.

## Limitations

- 3 seeds per variant, one model (3B parameters), one creative challenge.
- One AI reviewer assigned the rubric scores. A second, independent rater would make them more
  reliable.
- Temperature 0.8 was chosen to allow creativity. Other settings could change the ranking.
