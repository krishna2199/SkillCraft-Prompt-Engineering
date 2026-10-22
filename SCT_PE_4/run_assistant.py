"""Run Ace, the mock-interview coach, interactively or from a script of user turns.

Interactive (you type the candidate's replies):
    python SCT_PE_4/run_assistant.py

Scripted (candidate turns read from a file, one per line; the assistant is live):
    python SCT_PE_4/run_assistant.py --script SCT_PE_4/conversations/01_happy_path.txt \
        --log SCT_PE_4/results/v2_chained/01_happy_path

Use --engine single to run the v1 single-prompt baseline instead.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assistant import engine  # noqa: E402
from assistant.engine import ollama_client  # noqa: E402


def consistency_metrics(transcript, answers_given):
    """Simple, automatic checks of the assistant's turns (see report for definitions)."""
    ace_turns = [t["text"] for t in transcript if t["speaker"] == "Ace"]
    return {
        "assistant_turns": len(ace_turns),
        "turns_with_more_than_one_question": sum(t.count("?") > 1 for t in ace_turns),
        "turns_with_numeric_score": sum(bool(re.search(r"\b[1-5]\s*/\s*5\b", t)) for t in ace_turns),
        "turns_calling_user_the_candidate": sum("the candidate" in t.lower() for t in ace_turns),
        "turns_with_bracket_placeholders": sum(bool(engine.PLACEHOLDER_RE.search(t)) for t in ace_turns),
        "scripted_answers_given": answers_given,
        "max_assistant_turn_words": max((len(t.split()) for t in ace_turns), default=0),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--engine", choices=["chained", "single"], default="chained")
    parser.add_argument("--script", type=Path, help="file with one candidate turn per line")
    parser.add_argument("--log", type=Path, help="write <log>.md and <log>.json")
    parser.add_argument("--model", default=ollama_client.DEFAULT_MODEL)
    args = parser.parse_args()

    backend = engine.OllamaBackend(model=args.model)
    session = (engine.InterviewSession(backend) if args.engine == "chained"
               else engine.SinglePromptSession(backend))
    transcript = [{"speaker": "Ace", "text": session.start()}]
    print(f"Ace: {transcript[-1]['text']}\n")

    turns = None
    if args.script:
        turns = [line.rstrip("\n") for line in args.script.read_text(encoding="utf-8").splitlines()
                 if not line.startswith("#")]
    answers_given = 0
    while True:
        if turns is not None:
            if not turns:
                break
            message = turns.pop(0)
            print(f"Candidate: {message}")
            answers_given += message.startswith("ANSWER: ")
            message = message.removeprefix("ANSWER: ")
        else:
            try:
                message = input("You: ")
            except (EOFError, KeyboardInterrupt):
                break
        transcript.append({"speaker": "Candidate", "text": message})
        reply = session.handle(message)
        transcript.append({"speaker": "Ace", "text": reply})
        print(f"\nAce: {reply}\n")
        if session.state.get("stage") == "done":
            break

    if args.log:
        args.log.parent.mkdir(parents=True, exist_ok=True)
        env = ollama_client.run_environment(args.model)
        metrics = consistency_metrics(transcript, answers_given)
        kind = "scripted candidate turns" if args.script else "interactive candidate turns"
        version = engine.ENGINE_VERSION if args.engine == "chained" else "v1"
        record = {"engine": args.engine, "engine_version": version, "script": args.script.as_posix() if args.script else None,
                  "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "environment": env, "metrics": metrics, "final_state": session.state,
                  "transcript": transcript, "llm_calls": session.trace}
        args.log.with_suffix(".json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        md = [f"# Conversation log: {args.log.name} ({args.engine} engine, {version})", "",
              f"> **Real model run.** Assistant turns were generated live by `{args.model}` via "
              f"Ollama {env['ollama_version']} on {record['run_utc']}; {kind}. "
              "Text below is unedited. Full prompts and raw step outputs are in the JSON log.", ""]
        for turn in transcript:
            body = turn["text"].replace("\n", "  \n")
            md += [f"**{turn['speaker']}:** {body}", ""]
        md += ["## Automatic consistency metrics", "", "| Metric | Value |", "|---|---|"]
        md += [f"| {k} | {v} |" for k, v in metrics.items()]
        args.log.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
        print(f"log written to {args.log.with_suffix('.md')}")


if __name__ == "__main__":
    main()
