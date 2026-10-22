# LinkedIn Post Drafts

The brief says that after each task it is mandatory to post on LinkedIn about the task and
what was learned. These are drafts to edit and post from your own account. Replace
`<repository link>` with the published URL. Every figure below comes from this
repository's reports.

---

## Task 1 — Writing Better Prompts

I've completed Task 1 of my Prompt Engineering internship at SkillCraft Technology.

I rewrote three vague prompts (an internship email, a binary-search explanation, and a
business social post) and compared the outputs from two models.

What I learned:
- Adding an audience, a role, and clear constraints turned generic or placeholder-filled
  output into targeted output.
- Models don't always follow constraints. Only 5 of 8 length and format checks passed, so I
  check them with a script.
- A precise prompt doesn't fix reasoning. A small model still traced binary search wrongly.

<repository link>

#PromptEngineering #SkillCraftTechnology #AI #LLM

---

## Task 2 — Prompting for Creativity

Task 2 is done: prompting for creativity.

I ran four versions of a startup-idea prompt (baseline, persona, structured headings, and
few-shot with three example pitch cards), with 3 runs each, and scored them for tone,
creativity, and detail.

Key takeaways:
- Few-shot examples gave the strongest control over voice and format.
- Structure alone made the output complete but not original: the same "GreenThumb" idea
  appeared three times.
- Few-shot has a cost. The model borrowed ideas from the examples, so they need to be
  chosen with care.

<repository link>

#PromptEngineering #FewShotPrompting #SkillCraftTechnology #GenerativeAI

---

## Task 3 — Prompting for Task Automation

Task 3 complete: I built a small pipeline that turns messy meeting notes (bullets, chat
logs, emails) into clean task-tracker JSON using a local LLM.

The iteration story:
- v1: 0% of checks passed. The model added chatty text and code fences around the JSON.
- v2: an exact schema raised that to 68%.
- v3: rules targeting the observed errors raised it to 82%.
- Final: JSON mode, a validation retry, and a small null-filling step gave valid JSON on
  7/7 inputs, 84% field accuracy, and 88% on held-out notes.

The surprise: adding a worked example made results worse, and measuring each version is how
I caught it.

<repository link>

#PromptEngineering #Automation #LLM #SkillCraftTechnology

---

## Task 4 — Simulating an Assistant

Final task done! I built "Ace", a mock-interview coach that chains six small prompts (role
extraction, intent routing, question generation, clarification, evaluation, and summary)
inside a simple state machine.

Ace scores each answer, adapts the difficulty, handles vague or out-of-scope requests, and
is covered by 18 unit tests.

Reading the conversation logs exposed consistency problems. The feedback talked about "the
candidate" instead of to the user, and the closing message contained a "[Candidate's Name]"
placeholder. Fixing the prompts and adding a code guard removed both.

<repository link>

#PromptEngineering #ConversationalAI #Chatbots #SkillCraftTechnology
