"""Conversation engines for Ace, the mock-interview coach.

`InterviewSession` (v2) keeps conversation state in code and chains small
prompts: role extraction -> intent routing -> question generation ->
answer evaluation -> final report. `SinglePromptSession` (v1) is the
baseline: one system prompt plus the whole transcript, with no code-side state.
"""

import json
import re
import sys
from pathlib import Path

from . import prompts as P

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import ollama_client  # noqa: E402

ENGINE_VERSION = "v2.1"
# Matches template placeholders such as "[Candidate's Name]" or "[Your Name]".
PLACEHOLDER_RE = re.compile(r"\[[^\]\n]{1,40}\]")

FOCUS_AREAS = [
    "motivation and background for this role",
    "a core skill or tool used in this role",
    "a problem-solving or teamwork scenario",
    "handling a mistake or tight deadline",
    "learning something new quickly",
]
FALLBACK_QUESTIONS = [
    "What attracted you to this role, and what have you done so far to prepare for it?",
    "Which skill or tool from this role are you most confident with, and how have you used it?",
    "Tell me about a time you solved a problem with a team. What was your part?",
    "Describe a time you made a mistake or missed a deadline. What did you change afterwards?",
    "How do you learn a new tool or topic quickly? Give a recent example.",
]
HELP_TEXT = ("Commands: 'repeat' shows the current question again, 'skip' moves to the next "
             "question, 'quit' ends the interview with a summary, 'help' shows this message.")
GREETING = ("Hi, I'm Ace, your mock-interview coach. I'll ask you a few interview questions, "
            "score each answer from 1 to 5, and adapt the difficulty as we go. "
            "Which job role would you like to practise for?")


class OllamaBackend:
    """Live backend. Structured (JSON) steps run at temperature 0 for consistency."""

    def __init__(self, model=ollama_client.DEFAULT_MODEL, temperature=0.7, seed=42):
        self.model, self.temperature, self.seed = model, temperature, seed

    def complete(self, purpose, messages, json_mode=False):
        result = ollama_client.chat(messages, model=self.model, seed=self.seed,
                                    temperature=0 if json_mode else self.temperature,
                                    num_predict=400, json_mode=json_mode)
        return result["content"]


def parse_level(text):
    """Return (level, note) parsed from free text, or (None, None) if unclear."""
    t = text.lower()
    if re.search(r"\bintern(ship)?\b", t):
        return "intern", None
    if re.search(r"\b(junior|entry|graduate|fresher|beginner|new grad)\b", t):
        return "junior", None
    if re.search(r"\b(mid|senior|lead|principal|manager|experienced)\b", t):
        return "junior", ("I focus on intern and junior interviews, so I'll pitch the "
                          "questions at junior level.")
    return None, None


def _clean_question(text):
    text = text.strip().strip('"').strip()
    text = re.sub(r"^(question\s*\d*\s*[:.-]|\d+[.)])\s*", "", text, flags=re.I)
    return " ".join(text.split())


class InterviewSession:
    def __init__(self, backend, max_questions=3):
        self.backend = backend
        self.max_questions = max_questions
        self.state = {"stage": "role", "role": None, "level": None, "difficulty": 1,
                      "question": None, "asked": [], "results": [], "role_attempts": 0,
                      "level_attempts": 0}
        self.trace = []

    # -- model helpers -------------------------------------------------------
    def _call(self, purpose, prompt, json_mode=False):
        raw = self.backend.complete(purpose, [{"role": "user", "content": prompt}], json_mode)
        self.trace.append({"step": purpose, "prompt": prompt, "raw_output": raw})
        return raw

    def _structured(self, purpose, prompt, validate, fallback):
        """Call a JSON step; retry once with the error, then use a safe fallback."""
        for attempt in range(2):
            raw = self._call(purpose, prompt, json_mode=True)
            try:
                return validate(json.loads(raw))
            except (ValueError, TypeError, KeyError) as exc:
                prompt += f"\n\nYour previous output was invalid ({exc}). Return only valid JSON."
        self.trace.append({"step": purpose, "fallback_used": fallback})
        return fallback

    # -- steps ---------------------------------------------------------------
    def _extract_role(self, message):
        def validate(data):
            role = data["role"]
            if role is None:
                return None
            if not isinstance(role, str) or not 0 < len(role.split()) <= 6:
                raise ValueError("role must be a short string or null")
            return role.strip()
        return self._structured("role_extraction", P.ROLE_EXTRACTION.format(message=message),
                                validate, None)

    def _route(self, message):
        def validate(data):
            if data["intent"] not in ("answer", "clarify", "unsupported"):
                raise ValueError(f"unknown intent {data['intent']!r}")
            return data["intent"]
        prompt = P.INTENT_ROUTER.format(question=self.state["question"], message=message)
        return self._structured("intent_router", prompt, validate, "answer")

    def _next_question(self):
        s = self.state
        number = len(s["asked"]) + 1
        prompt = P.QUESTION_GENERATOR.format(
            role=s["role"], level=s["level"], number=number, total=self.max_questions,
            difficulty=s["difficulty"], focus=FOCUS_AREAS[(number - 1) % len(FOCUS_AREAS)],
            asked="; ".join(s["asked"]) or "none")
        asked_norm = {q.lower() for q in s["asked"]}
        for _ in range(2):
            question = _clean_question(self._call("question_generator", prompt))
            problems = []
            if question.count("?") != 1 or not question.endswith("?"):
                problems.append("it must be exactly one question ending with '?'")
            if len(question.split()) > 40:
                problems.append("it is longer than 35 words")
            if question.lower() in asked_norm:
                problems.append("it repeats an earlier question")
            if not problems:
                break
            prompt += "\n\nYour previous attempt was rejected because " + "; ".join(problems) + "."
        else:
            question = FALLBACK_QUESTIONS[(number - 1) % len(FALLBACK_QUESTIONS)]
            self.trace.append({"step": "question_generator", "fallback_used": question})
        s["question"] = question
        s["asked"].append(question)
        return f"Question {number} of {self.max_questions}: {question}"

    def _evaluate(self, answer):
        def validate(data):
            score = data["score"]
            if isinstance(score, str) and score.strip().isdigit():
                score = int(score)
            if not isinstance(score, int) or not 1 <= score <= 5:
                raise ValueError("score must be an integer from 1 to 5")
            for key in ("strength", "improvement"):
                if not isinstance(data[key], str) or not data[key].strip():
                    raise ValueError(f"{key} must be a non-empty string")
            return {"score": score, "strength": data["strength"].strip(),
                    "improvement": data["improvement"].strip()}
        s = self.state
        prompt = P.EVALUATOR.format(level=s["level"], role=s["role"],
                                    question=s["question"], answer=answer)
        fallback = {"score": None, "strength": "Thanks for your answer.",
                    "improvement": "Try adding a specific example with a clear result."}
        return self._structured("evaluator", prompt, validate, fallback)

    def _adapt(self, score):
        if score is None:
            return
        if score >= 4:
            self.state["difficulty"] = min(3, self.state["difficulty"] + 1)
        elif score <= 2:
            self.state["difficulty"] = max(1, self.state["difficulty"] - 1)

    def _advance(self, prefix):
        if len(self.state["asked"]) >= self.max_questions:
            return prefix + self._finish()
        return prefix + self._next_question()

    def _finish(self):
        s = self.state
        s["stage"] = "done"
        scored = [r for r in s["results"] if r["score"] is not None]
        if not s["results"]:
            return "No questions were answered, so there is nothing to score. Good luck with your preparation!"
        lines = []
        for i, r in enumerate(s["results"], 1):
            if r["score"] is None:
                lines.append(f"Q{i}: skipped")
            else:
                lines.append(f"Q{i} (difficulty {r['difficulty']}): {r['score']}/5. "
                             f"Strength: {r['strength']} Improve: {r['improvement']}")
        prompt = P.FINAL_REPORT.format(level=s["level"], role=s["role"],
                                       results="\n".join(lines))
        closing = self._call("final_report", prompt).strip()
        if PLACEHOLDER_RE.search(closing):
            # v2.1: regenerate once with the problem named, then strip any that remain.
            closing = self._call("final_report", prompt + "\n\nYour previous message contained a "
                                 "placeholder in square brackets. Rewrite it without one.").strip()
            if PLACEHOLDER_RE.search(closing):
                closing = PLACEHOLDER_RE.sub("", closing)
                closing = re.sub(r",\s*,", ",", closing)            # "done, , keep" -> "done, keep"
                closing = re.sub(r"[ \t]+([,.!?])", r"\1", closing)  # "Thanks !" -> "Thanks!"
                closing = re.sub(r"[ \t]{2,}", " ", closing)
                self.trace.append({"step": "final_report", "placeholders_removed": True})
        if scored:
            avg = sum(r["score"] for r in scored) / len(scored)
            scores = ", ".join(str(r["score"]) if r["score"] is not None else "skipped"
                               for r in s["results"])
            closing += f"\n\nScores: {scores} (average {avg:.1f}/5)."
        return closing

    # -- public API ----------------------------------------------------------
    def start(self):
        return GREETING

    def handle(self, message):
        s = self.state
        msg = message.strip()
        cmd = msg.lower().rstrip(".!")
        if s["stage"] == "done":
            return "This interview is finished. Start a new session to practise again."
        if cmd in ("quit", "exit", "stop", "end"):
            return self._finish()
        if cmd == "help":
            return HELP_TEXT + (f"\n\nCurrent question: {s['question']}" if s["question"] else "")
        if not msg:
            return "I didn't catch anything. " + ("Please answer the question, or type 'help'."
                                                  if s["stage"] == "questioning"
                                                  else "Could you type that again?")

        if s["stage"] == "role":
            role = self._extract_role(msg)
            if role is None:
                s["role_attempts"] += 1
                return ("I couldn't identify a specific job role there. Which role should we "
                        "practise for? For example: data analyst, software developer, or "
                        "customer support associate.")
            s["role"], s["stage"] = role, "level"
            return (f"Great, we'll practise for a {role} role. What level are you aiming for: "
                    "intern or junior/entry-level?")

        if s["stage"] == "level":
            level, note = parse_level(msg)
            if level is None:
                s["level_attempts"] += 1
                if s["level_attempts"] < 2:
                    return "Sorry, which level is that: intern or junior/entry-level?"
                level, note = "junior", "I'll assume a junior/entry-level role."
            s["level"], s["stage"] = level, "questioning"
            intro = (note + " " if note else "") + (
                f"We'll do {self.max_questions} questions. Type 'help' at any time for commands.\n\n")
            return intro + self._next_question()

        # stage == "questioning"
        if cmd in ("repeat", "say again", "repeat the question"):
            return f"Sure. {s['question']}"
        if cmd == "skip":
            s["results"].append({"question": s["question"], "answer": None, "score": None,
                                 "difficulty": s["difficulty"], "strength": "", "improvement": ""})
            return self._advance("No problem, let's move on.\n\n")
        intent = self._route(msg)
        if intent == "clarify":
            clarification = self._call("clarify", P.CLARIFY.format(
                role=s["role"], level=s["level"], question=s["question"], message=msg)).strip()
            return f"{clarification}\n\nWhen you're ready: {s['question']}"
        if intent == "unsupported":
            return ("That's outside what I can help with here: I only run mock interviews and "
                    f"give feedback on your answers. Let's continue.\n\n{s['question']}")
        result = self._evaluate(msg)
        s["results"].append({"question": s["question"], "answer": msg,
                             "difficulty": s["difficulty"], **result})
        self._adapt(result["score"])
        score = f"{result['score']}/5" if result["score"] is not None else "not scored"
        feedback = (f"Score: {score}\nStrength: {result['strength']}\n"
                    f"To improve: {result['improvement']}\n\n")
        return self._advance(feedback)


class SinglePromptSession:
    """v1 baseline: one persona prompt and the full transcript, no code-side state."""

    def __init__(self, backend):
        self.backend = backend
        self.messages = [{"role": "system", "content": P.SINGLE_PROMPT_V1}]
        self.trace = []
        self.state = {"stage": "free-form (no code-side state)"}

    def _reply(self):
        raw = self.backend.complete("single_prompt", self.messages)
        self.messages.append({"role": "assistant", "content": raw})
        self.trace.append({"step": "single_prompt", "raw_output": raw})
        return raw.strip()

    def start(self):
        self.messages.append({"role": "user", "content": "Hello"})
        return self._reply()

    def handle(self, message):
        self.messages.append({"role": "user", "content": message})
        return self._reply()
