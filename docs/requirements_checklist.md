# Requirements Compliance Checklist

Each requirement below is quoted or closely paraphrased from the official brief
([transcript and screenshots](brief/official_brief.md)). Status key: ✅ met, with linked
evidence · ⚠️ partly met or needs action by the intern · ❌ not met.

## General instructions (brief pages 2–4)

| # | Requirement | Status | Evidence / note |
|---|---|---|---|
| G1 | Complete at least 2 tasks for the certificate; all 4 for a Letter of Recommendation | ✅ | All four tasks are implemented: [SCT_PE_1](../SCT_PE_1/), [SCT_PE_2](../SCT_PE_2/), [SCT_PE_3](../SCT_PE_3/), [SCT_PE_4](../SCT_PE_4/) |
| G2 | Host the work and submit a link. *"For Prompt Engineering … you are not required to use Github. You can use any platform to host your work."* | ⚠️ | The repository is ready to publish, but **pushing it needs the intern's approval and GitHub account**. See the [QA report](qa_report.md#github-readiness). |
| G3 | If GitHub is used for other tracks: public repo named `SCT_TrackCode_TaskNumber` | ⚠️ (not mandatory for PE) | This is one repository with folders named `SCT_PE_1` … `SCT_PE_4`. That is acceptable because the PE track does not require GitHub. If one repository per task is preferred, each folder can be published separately as `SCT_PE_N`. |
| G4 | *"Following the completion of each task, it is MANDATORY that you create a post on LinkedIn"* | ⚠️ needs the intern | Draft posts are in [linkedin_posts.md](linkedin_posts.md). Posting needs the intern's own LinkedIn account. |
| G5 | Any language or framework may be used | ✅ | Python standard library plus a local Ollama model |

## Task 01 — Writing Better Prompts (page 57)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1.1 | Experiment with clarity, specificity, and tone | ✅ | [Report: how the prompts were improved](../SCT_PE_1/report/final_comparison_report.md#how-the-prompts-were-improved) |
| 1.2 | Take **3** vague or ineffective prompts | ✅ | [`experiment{1,2,3}_original.txt`](../SCT_PE_1/prompts/) |
| 1.3 | Rewrite them into improved versions | ✅ | [`experiment{1,2,3}_improved.txt`](../SCT_PE_1/prompts/) |
| 1.4 | Compare and analyze the outputs | ✅ | Recorded and rerun outputs; [comparison report](../SCT_PE_1/report/final_comparison_report.md); automatic [constraint checks](../SCT_PE_1/report/constraint_checks_recorded.md) |
| 1.5 | Understand how prompt design affects LLM behaviour | ✅ | [Overall conclusions](../SCT_PE_1/report/final_comparison_report.md#overall-conclusions) |

## Task 02 — Prompting for Creativity (page 58)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 2.1 | Explore how prompt structure, tone, and examples influence creative tasks | ✅ | Variants v1–v4 each isolate one factor ([design](../SCT_PE_2/report/comparison_report.md#design)) |
| 2.2 | **Use few-shot prompting** to guide style or persona | ✅ | [`prompt_v4.txt`](../SCT_PE_2/prompts/prompt_v4.txt): a persona plus 3 example pitch cards (rewritten from a one-shot draft) |
| 2.3 | Design a prompt that generates creative outputs | ✅ | Startup-idea challenge |
| 2.4 | Run multiple variants of the prompt | ✅ | 4 variants × 3 seeds = [12 outputs](../SCT_PE_2/results/) |
| 2.5 | Compare results for **tone, creativity, and detail** | ✅ | [Rubric and scores](../SCT_PE_2/report/comparison_report.md#scores), [automatic metrics](../SCT_PE_2/report/automatic_metrics.md) |

## Task 03 — Prompting for Task Automation (page 59)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 3.1 | Semi-automate a useful real-world task (summarising notes, extracting structured data, transforming formats) | ✅ | Meeting notes → task-tracker JSON ([`automate.py`](../SCT_PE_3/automate.py)) |
| 3.2 | A clear, consistent prompt that handles **multiple inputs** | ✅ | [`prompt_v3_rules.txt`](../SCT_PE_3/prompts/prompt_v3_rules.txt), tested on 7 inputs in 4 formats |
| 3.3 | Produces **reliable** output | ✅ | All 7 schema-valid; 84% field accuracy (development) and 88% (held-out); 0 invented values ([scorecard](../SCT_PE_3/results/prompt_v3_rules_json_retry_normalize/scorecard.md)) |
| 3.4 | Submit the prompt | ✅ | [`prompts/`](../SCT_PE_3/prompts/) |
| 3.5 | **At least 3** input-output examples | ✅ | 7 examples: [`inputs/`](../SCT_PE_3/inputs/) → [final outputs](../SCT_PE_3/results/prompt_v3_rules_json_retry_normalize/) |
| 3.6 | A short reflection on prompt iteration or debugging | ✅ | [reflection.md](../SCT_PE_3/report/reflection.md) |

## Task 04 — Simulating an Assistant (page 60)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 4.1 | Build a simple assistant by **chaining multiple prompts** or simulating dialogue | ✅ | [`assistant/engine.py`](../SCT_PE_4/assistant/engine.py): 6 chained prompt steps run by a state machine |
| 4.2 | A **persona-driven** interaction (for example, a job interview bot) | ✅ | "Ace", a mock-interview coach ([`prompts.py`](../SCT_PE_4/assistant/prompts.py)) |
| 4.3 | **Adapts across turns** using structured prompt sequences | ✅ | Difficulty rises or falls with each score; re-asks after vague input; handles clarification and out-of-scope requests ([report](../SCT_PE_4/report/assistant_report.md)) |
| 4.4 | Document how the assistant flows (step-by-step or diagram) | ✅ | [Flow diagram and steps](../SCT_PE_4/report/assistant_report.md#how-the-assistant-flows) |
| 4.5 | Sample conversation logs | ✅ | [`results/`](../SCT_PE_4/results/): saved live-model logs for the tested conversations; one ambiguous scenario remains unfinished |
| 4.6 | Improvements made to get consistent responses | ✅ | [v1 → v2.0 → v2.1 comparison](../SCT_PE_4/report/assistant_report.md#improvements-for-consistent-responses) with [metrics](../SCT_PE_4/report/consistency_metrics.md) |

## What the brief does not specify

The brief gives no grading rubric, length limits, required model, file formats, or
deadline. Evaluation criteria beyond those quoted above were chosen by the author. They are
documented in the [methodology](methodology.md) and should not be read as official
SkillCraft criteria.
