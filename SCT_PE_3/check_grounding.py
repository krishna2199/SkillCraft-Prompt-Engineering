"""Check that every non-null date and owner in a results folder appears in its input notes.

Usage:  python SCT_PE_3/check_grounding.py [results-folder-name]
Default: the final pipeline, prompt_v3_rules_json_retry_normalize.
A value that is not found in the input text was invented by the model.
"""

import json
import sys
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else "prompt_v3_rules_json_retry_normalize"
    checked, invented = 0, []
    for path in sorted((TASK_DIR / "results" / run).glob("*.json")):
        if path.name == "run_log.json":
            continue
        notes = (TASK_DIR / "inputs" / f"{path.stem}.txt").read_text(encoding="utf-8").lower()
        data = json.loads(path.read_text(encoding="utf-8"))
        values = [data["meeting_date"]]
        for item in data["action_items"]:
            values += [item["due_date"], item["owner"]]
        for value in values:
            if value is None:
                continue
            checked += 1
            if value.lower().lstrip("@") not in notes:
                invented.append(f"{path.stem}: {value!r}")
    print(f"{run}: {checked} non-null dates/owners checked, {len(invented)} not found in the input")
    for line in invented:
        print("  " + line)
    sys.exit(1 if invented else 0)


if __name__ == "__main__":
    main()
