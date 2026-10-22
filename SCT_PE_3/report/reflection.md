# Task 3 — Prompting for Task Automation: Report and Reflection

## Objective (from the official brief)

> Apply prompting to semi-automate a useful real-world task such as summarizing notes,
> extracting structured data, or transforming formats. Design a clear, consistent prompt
> that can handle multiple inputs and produce reliable output. Submit your prompt, at least 3
> input-output examples, and a short reflection on prompt iteration or debugging.

## The task

**Meeting notes → task-tracker JSON.** Teams write meeting notes in many formats: bullet
lists, chat logs, emails, and prose. The pipeline turns any of them into one fixed JSON
schema (title, date, attendees, summary, decisions, action items with owner and due date,
and open questions). The output can then be loaded into a tracker without retyping.

| Deliverable | Where |
|---|---|
| **Final prompt** | [`prompts/prompt_v3_rules.txt`](../prompts/prompt_v3_rules.txt), run with JSON mode, one validation retry, and null-filling of missing keys |
| **Input → output examples (7)** | [`inputs/`](../inputs/) → [`results/prompt_v3_rules_json_retry_normalize/`](../results/prompt_v3_rules_json_retry_normalize/) (`*.output.txt` raw, `*.json` validated) |
| **Automation script** | [`automate.py`](../automate.py): prompt → model → parse → schema validation → retry → scoring |
| **Answer keys** | [`expected/`](../expected/): the owners, due dates, and counts a correct extraction must contain |
| **All iterations, with evidence** | One results folder per prompt version, each with a `scorecard.md` and a `run_log.json` |

The inputs are fictional notes written for this task. Inputs 06 and 07 were written **after
the last prompt was frozen** and were never used to tune any prompt, so they act as a
held-out test.

## Measuring "reliable output"

Two things are measured for every input:

1. **Schema-valid:** the response parses as JSON and has exactly the required keys and types.
   Dates must be `YYYY-MM-DD` or null, and the summary must be 40 words or fewer.
2. **Field accuracy:** checks against the answer key. These cover the meeting date, the number
   of action items, each expected item (found, correct owner, correct due date), the number
   of decisions and the specific details they must mention, and the number of open
   questions. There are 57 checks across inputs 01–05 and 25 across the held-out inputs 06–07.

All runs used `qwen2.5:3b` at temperature 0 with seed 42.

## Iteration results

| Version | What changed | Inputs | Schema-valid | Checks (01–05) | Held-out (06–07) |
|---|---|---|---|---|---|
| [v1 basic](../results/prompt_v1_basic/scorecard.md) | "Summarize these meeting notes as JSON" | 5 | 0/5 | 0/57 (0%) | — |
| [v2 schema](../results/prompt_v2_schema/scorecard.md) | Exact schema; "only JSON, no code fences" | 5 | 4/5 | 39/57 (68%) | — |
| [v3 rules](../results/prompt_v3_rules/scorecard.md) | 5 rules aimed at the observed failures | 5 | 4/5 | 47/57 (82%) | — |
| [v3 + JSON mode + retry](../results/prompt_v3_rules_json_retry/scorecard.md) | Ollama JSON mode; retry with validation errors | 5 | 4/5 | 48/57 (84%) | — |
| [v4 example](../results/prompt_v4_example/scorecard.md) | v3 plus one worked example (one-shot) | 5 | 5/5 | 43/57 (75%) | — |
| [v5 recap rule](../results/prompt_v5_recap_rule_json_retry_normalize/scorecard.md) | v4 plus a rule for "what we agreed" lists | 7 | 7/7 | 41/57 (72%) | 21/25 (84%) |
| [v4 full pipeline](../results/prompt_v4_example_json_retry_normalize/scorecard.md) | v4 + JSON mode + retry + normalize | 7 | 7/7 | 43/57 (75%) | 22/25 (88%) |
| **[v3 full pipeline (final)](../results/prompt_v3_rules_json_retry_normalize/scorecard.md)** | **v3 + JSON mode + retry + normalize** | 7 | **7/7** | **48/57 (84%)** | **22/25 (88%)** |

The final version was chosen on inputs 01–05 only. The held-out score is reported, not used
for selection. [`check_grounding.py`](../check_grounding.py) confirms that **every one of the
28 non-null dates and owners in the final outputs appears in its input text**. The pipeline
leaves a field empty rather than inventing a value.

## Reflection: what iteration and debugging taught me

**1. The first failure was the format, not the content.** v1 scored 0/57. The model extracted
the right facts, but every response started with "Here is the summarized information…" and
wrapped the JSON in Markdown fences, so nothing parsed. It also invented a different
structure for each input (`meetingDate` vs. nothing; `item`/`action`/`status` vs.
`description`/`details`). An exact schema and "return ONLY JSON, no code fences" (v2) fixed
both problems at once, raising the score from 0% to 68%.

**2. After that, I debugged by reading failures, not by guessing.** The v2 scorecard
showed four specific, repeated errors:
- Tasks with no owner were dropped (the FAQ page, telling the support team).
- Assignments were copied into `decisions`.
- In the email, the `due_date` key was missing and the date was left inside the task text.
- "Agreed NOT to change payment terms" lost the detail "30 days".

v3 added one rule for each error, and accuracy rose to 82%.

**3. Code is more reliable than prompting for mechanical rules.** One v3 output still left
out `due_date` for an unowned task. A retry that sent the validation error back to the
model did not fix it: the model returned the same object. A three-line `normalize` step that
adds a missing `owner` or `due_date` as `null` fixed it with certainty. It never invents a
value, and every key it adds is logged. The lesson is to let the prompt handle meaning and
let code enforce structure.

**4. A worked example made things worse.** I expected a one-shot example (v4) to help a small
model. It did fix the `"Grace: …"` owner format and the unowned FAQ task. However, on the
email (input 05) the model then put both assigned tasks under `decisions`. Comparing the
prompts alone, that input's score fell from 9/11 (v3) to 3/11 (v4). A follow-up rule about recap lists (v5) did not repair it,
and v5 lost another item on input 02. Each change was measured, so the regression was
caught rather than shipped. The final prompt is v3, without the example.

**5. Held-out inputs keep the result honest.** After five versions tuned on the same five
notes, there is a real risk of overfitting. The two notes written afterwards scored 88%,
close to the 84% on the development set. This suggests the rules generalise and were not
just memorised fixes.

## Known limitations of the final pipeline

- It sometimes **misses an owner** written as `Name: task` (input 04) and returns `null`
  rather than guessing. It also missed one unowned task ("tell the support team") and the
  first task in the Slack log.
- It can still **duplicate assignments into `decisions`** (inputs 01 and 05).
- Seven test inputs and one 3B model are a small sample. A larger model would probably score
  higher with the same prompt. Human review of the JSON is still needed, which is why this
  is *semi*-automation.
- Attendee names sometimes keep roles in brackets (for example `Omar (PM)`). The schema does
  not forbid this, and it is not scored.
