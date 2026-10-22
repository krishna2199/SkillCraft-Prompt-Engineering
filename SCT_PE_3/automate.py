"""Semi-automate meeting-notes -> structured JSON extraction with a local LLM.

Usage (final pipeline):
    python SCT_PE_3/automate.py --prompt prompts/prompt_v3_rules.txt \
        --json-mode --retry --normalize --tag json_retry_normalize
    python SCT_PE_3/automate.py --prompt prompts/prompt_v3_rules.txt \
        --json-mode --retry --normalize --tag my_run --input path/to/my_notes.txt

Without --input, every file in inputs/ is processed and scored against the
answer key in expected/. Results are written to results/<prompt-stem>[_<tag>]/.
Add --rescore to re-score a saved run without calling the model.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_DIR.parent / "tools"))
import ollama_client  # noqa: E402

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SCHEMA_KEYS = {"meeting_title", "meeting_date", "attendees", "summary",
               "decisions", "action_items", "open_questions"}
ACTION_KEYS = {"task", "owner", "due_date"}


def parse_json(text):
    """Strictly parse the model response; return (data, error)."""
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc.msg} (line {exc.lineno})"


def validate_schema(data):
    """Return a list of schema violations (empty list means valid)."""
    if not isinstance(data, dict):
        return ["top level is not an object"]
    errors = []
    missing, extra = SCHEMA_KEYS - data.keys(), data.keys() - SCHEMA_KEYS
    if missing:
        errors.append(f"missing keys: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected keys: {sorted(extra)}")
    if not isinstance(data.get("meeting_title"), str):
        errors.append("meeting_title must be a string")
    date = data.get("meeting_date")
    if date is not None and not (isinstance(date, str) and DATE_RE.match(date)):
        errors.append(f"meeting_date must be YYYY-MM-DD or null, got {date!r}")
    summary = data.get("summary")
    if not isinstance(summary, str):
        errors.append("summary must be a string")
    elif len(summary.split()) > 40:
        errors.append(f"summary has {len(summary.split())} words (max 40)")
    for key in ("attendees", "decisions", "open_questions"):
        value = data.get(key)
        if not (isinstance(value, list) and all(isinstance(v, str) for v in value)):
            errors.append(f"{key} must be a list of strings")
    items = data.get("action_items")
    if not isinstance(items, list):
        errors.append("action_items must be a list")
        return errors
    for i, item in enumerate(items):
        if not isinstance(item, dict) or set(item) != ACTION_KEYS:
            errors.append(f"action_items[{i}] must have exactly keys {sorted(ACTION_KEYS)}")
            continue
        if not isinstance(item["task"], str) or not item["task"].strip():
            errors.append(f"action_items[{i}].task must be a non-empty string")
        if item["owner"] is not None and not isinstance(item["owner"], str):
            errors.append(f"action_items[{i}].owner must be a string or null")
        due = item["due_date"]
        if due is not None and not (isinstance(due, str) and DATE_RE.match(due)):
            errors.append(f"action_items[{i}].due_date must be YYYY-MM-DD or null, got {due!r}")
    return errors


def _norm(value):
    """Compare names case-insensitively, ignoring a leading chat-handle '@'."""
    return value.strip().lstrip("@").lower() if isinstance(value, str) else value


def score(data, expected):
    """Compare extracted data with the answer key; return a list of (check, passed, detail)."""
    checks = [("meeting_date", data.get("meeting_date") == expected["meeting_date"],
               f"got {data.get('meeting_date')!r}")]
    items = data.get("action_items") or []
    checks.append(("action_item_count", len(items) == len(expected["action_items"]),
                   f"got {len(items)}, expected {len(expected['action_items'])}"))
    for exp in expected["action_items"]:
        match = next((it for it in items if isinstance(it, dict)
                      and exp["keyword"].lower() in str(it.get("task", "")).lower()), None)
        label = f"action '{exp['keyword']}'"
        if match is None:
            # A missing item fails its owner and due-date checks too, so every run of the
            # same input has the same number of checks.
            checks.append((f"{label} found", False, "no task mentions keyword"))
            checks.append((f"{label} owner", False, "item missing"))
            checks.append((f"{label} due_date", False, "item missing"))
            continue
        checks.append((f"{label} found", True, ""))
        checks.append((f"{label} owner", _norm(match.get("owner")) == _norm(exp["owner"]),
                       f"got {match.get('owner')!r}"))
        checks.append((f"{label} due_date", match.get("due_date") in exp["due_date"],
                       f"got {match.get('due_date')!r}"))
    decisions = data.get("decisions") or []
    rng = expected["decisions"]
    checks.append(("decision_count", rng["min"] <= len(decisions) <= rng["max"],
                   f"got {len(decisions)}, expected {rng['min']}-{rng['max']}"))
    for needle in rng["must_mention"]:
        checks.append((f"decision mentions '{needle}'",
                       any(needle.lower() in str(d).lower() for d in decisions), ""))
    questions = data.get("open_questions") or []
    rng = expected["open_questions"]
    checks.append(("open_question_count", rng["min"] <= len(questions) <= rng["max"],
                   f"got {len(questions)}, expected {rng['min']}-{rng['max']}"))
    return checks


def normalize(data):
    """Add missing optional action-item keys as null. Never invents a value.

    Returns the list of keys that were added, so every change is logged.
    """
    added = []
    for i, item in enumerate(data.get("action_items") or [] if isinstance(data, dict) else []):
        if isinstance(item, dict):
            for key in ("owner", "due_date"):
                if key not in item:
                    item[key] = None
                    added.append(f"action_items[{i}].{key}")
    return added


def extract(template, notes, *, json_mode, retry, model, fix_missing=False):
    """Run the prompt; optionally retry once with the validation errors fed back."""
    messages = [{"role": "user", "content": template.replace("{notes}", notes.strip())}]
    attempts = []
    for _ in range(2 if retry else 1):
        result = ollama_client.chat(messages, model=model, temperature=0, seed=42,
                                    json_mode=json_mode)
        data, error = parse_json(result["content"])
        added = normalize(data) if fix_missing and not error else []
        errors = [error] if error else validate_schema(data)
        attempts.append({"response": result["content"], "errors": errors,
                         "normalized_keys": added, "meta": result["meta"]})
        if not errors:
            return data, attempts
        messages += [
            {"role": "assistant", "content": result["content"]},
            {"role": "user", "content": "Your previous answer failed validation:\n- "
             + "\n- ".join(errors) + "\nReturn only the corrected JSON object."},
        ]
    return data, attempts


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--input", type=Path, nargs="*")
    parser.add_argument("--json-mode", action="store_true",
                        help="ask Ollama to constrain output to valid JSON")
    parser.add_argument("--retry", action="store_true",
                        help="retry once, feeding validation errors back to the model")
    parser.add_argument("--normalize", action="store_true",
                        help="add missing action-item owner/due_date keys as null")
    parser.add_argument("--tag", default="",
                        help="suffix for the results folder, e.g. 'prompt_only'")
    parser.add_argument("--rescore", action="store_true",
                        help="re-score the saved run_log.json instead of calling the model")
    parser.add_argument("--model", default=ollama_client.DEFAULT_MODEL)
    args = parser.parse_args()

    prompt_path = args.prompt if args.prompt.is_absolute() else TASK_DIR / args.prompt
    template = prompt_path.read_text(encoding="utf-8")
    inputs = args.input or sorted((TASK_DIR / "inputs").glob("*.txt"))
    run_name = prompt_path.stem + (f"_{args.tag}" if args.tag else "")
    out_dir = TASK_DIR / "results" / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.rescore:
        # Re-score saved responses (for example after changing the answer key or scorer)
        # without calling the model again.
        log = json.loads((out_dir / "run_log.json").read_text(encoding="utf-8"))
        args.json_mode, args.retry = log["json_mode"], log["retry"]
        args.normalize = log.get("normalize", False)
    else:
        log = {"environment": ollama_client.run_environment(args.model),
               "prompt_file": f"prompts/{prompt_path.name}",
               "json_mode": args.json_mode, "retry": args.retry,
               "normalize": args.normalize, "runs": []}
        for path in inputs:
            data, attempts = extract(template, path.read_text(encoding="utf-8"),
                                     json_mode=args.json_mode, retry=args.retry,
                                     model=args.model, fix_missing=args.normalize)
            final = attempts[-1]
            (out_dir / f"{path.stem}.output.txt").write_text(final["response"], encoding="utf-8")
            if not final["errors"]:
                (out_dir / f"{path.stem}.json").write_text(
                    json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            log["runs"].append({"input": path.name, "attempts": attempts})
            print(f"{path.name}: valid={not final['errors']} attempts={len(attempts)}")

    rows, total_pass, total_checks = [], 0, 0
    for run in log["runs"]:
        final = run["attempts"][-1]
        expected_path = TASK_DIR / "expected" / f"{Path(run['input']).stem}.json"
        if not expected_path.exists():
            continue
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        data, _ = parse_json(final["response"])
        if args.normalize:
            normalize(data)
        # An unparsable response fails every check for that input.
        checks = score(data, expected) if isinstance(data, dict) else             [(c, False, "unparsable response") for c, _, _ in score({}, expected)]
        passed = sum(ok for _, ok, _ in checks)
        run["checks"] = [{"check": c, "passed": ok, "detail": d} for c, ok, d in checks]
        total_pass, total_checks = total_pass + passed, total_checks + len(checks)
        rows.append((run["input"], len(run["attempts"]),
                     ", ".join(final.get("normalized_keys", [])) or "-",
                     not final["errors"], f"{passed}/{len(checks)}",
                     "; ".join(final["errors"]) or "-",
                     "; ".join(f"{c} ({d})" if d else c for c, ok, d in checks if not ok) or "-"))

    (out_dir / "run_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    if rows:
        lines = [f"# Scorecard: {run_name}", "",
                 f"Generated by `automate.py` from a real run of `{args.model}` "
                 f"(temperature 0, seed 42, JSON mode {'on' if args.json_mode else 'off'}, "
                 f"retry {'on' if args.retry else 'off'}, "
                 f"normalize {'on' if args.normalize else 'off'}). Raw responses are in "
                 "`*.output.txt`; validated, parsed results are in `*.json`.", "",
                 f"**Overall: {total_pass}/{total_checks} checks passed "
                 f"({100 * total_pass / total_checks:.0f}%).**", "",
                 "| Input | Attempts | Keys added by normalize | Schema-valid | Checks passed | Validation errors | Failed checks |",
                 "|---|---|---|---|---|---|---|"]
        lines += [f"| {a} | {b} | {g} | {'yes' if c else 'no'} | {d} | {e} | {f} |".replace("\n", " ")
                  for a, b, g, c, d, e, f in rows]
        (out_dir / "scorecard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"overall {total_pass}/{total_checks}")


if __name__ == "__main__":
    main()
