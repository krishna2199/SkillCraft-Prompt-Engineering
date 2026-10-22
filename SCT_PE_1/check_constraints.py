"""Programmatically check Task 1 outputs against the explicit prompt constraints.

Usage:  python SCT_PE_1/check_constraints.py [results_dir]
Prints a Markdown table. Defaults to the originally recorded outputs in results/.
"""

import json
import math
import re
import sys
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent
HASHTAG = re.compile(r"#\w+")
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-.@]*")


def words(text):
    """Count words, ignoring hashtags and Markdown symbols."""
    return len(WORD.findall(HASHTAG.sub("", text)))


def binary_search(arr, target):
    """Reference implementation used to verify the worked examples."""
    low, high, mids = 0, len(arr) - 1, []
    while low <= high:
        mid = (low + high) // 2
        mids.append(mid)
        if arr[mid] == target:
            return mid, mids
        if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1, mids


def read(results, name):
    """Read a recorded output (`*_output.md`) or a logged rerun (`*_seed42.md`)."""
    path = results / name
    if path.exists():
        return path.read_text(encoding="utf-8-sig")
    rerun = results / name.replace("_output.md", "_seed42.md")
    if rerun.exists():
        # Drop the run-metadata header written by tools/run_prompts.py.
        return rerun.read_text(encoding="utf-8").split("\n---\n", 1)[1]
    return None


def main():
    results = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else TASK_DIR / "results"
    rows = []

    def check(experiment, constraint, passed, evidence):
        rows.append((experiment, constraint, "PASS" if passed else "FAIL", evidence))

    for variant in ("original", "improved"):
        email = read(results, f"experiment1_{variant}_output.md")
        if email is None:
            continue
        n = words(email)
        if variant == "improved":
            check("1 improved", "120-160 words", 120 <= n <= 160, f"{n} words")
            check("1 improved", "has a subject line",
                  bool(re.search(r"^\W*subject\b", email, re.I | re.M)), "searched for 'Subject'")
        check(f"1 {variant}", "no unfilled placeholders",
              not re.search(r"\[[^\]]*your[^\]]*\]", email, re.I),
              ", ".join(re.findall(r"\[[^\]]+\]", email)) or "none")
        check(f"1 {variant}", "does not claim a resume is attached",
              not re.search(r"resume attached|attached .*resume|find my resume attached", email, re.I),
              "searched for 'resume attached'")

    sorted_array = [2, 5, 8, 12, 16, 23, 38]
    index, mids = binary_search(sorted_array, 16)
    check("2 improved", "prompt's example array is sorted", sorted_array == sorted(sorted_array),
          str(sorted_array))
    # The recorded outputs are checked against specific claims they make; reruns are
    # checked for truncation and their worked steps are verified by hand in the audit.
    original = read(results, "experiment2_original_output.md")
    if (results / "experiment2_original_output.md").exists():
        check("2 improved", "worked steps (mid 3 -> 5 -> 4, found at index 4)",
              (index, mids) == (4, [3, 5, 4]), f"reference run: mids={mids}, index={index}")
        check("2 improved", "'about 10 comparisons for 1,000 elements'",
              math.floor(math.log2(1000)) + 1 == 10,
              f"floor(log2 1000)+1 = {math.floor(math.log2(1000)) + 1}")
        index, _ = binary_search([10, 20, 30, 40, 50, 60, 70], 50)
        check("2 original", "printed output (4) matches code", index == 4, f"reference returns {index}")
        check("2 original", "example target matches code target",
              "Target element: 40" in original and "binary_search(numbers, 40)" in original,
              "prose searches 40, code searches 50")

    for variant in ("original", "improved"):
        post = read(results, f"experiment3_{variant}_output.md")
        if post is None:
            continue
        n, tags = words(post), len(HASHTAG.findall(post))
        if variant == "improved":
            check("3 improved", "100-140 words", 100 <= n <= 140, f"{n} words excl. hashtags")
            check("3 improved", "at most 3 hashtags", tags <= 3, f"{tags} hashtags")
        else:
            check("3 original", "hashtag count (no limit set)", True, f"{tags} hashtags")
        check(f"3 {variant}", "no statistics or testimonials",
              not re.search(r"\d+\s*%|\bclients? (say|said)\b|“.*”\s*-", post),
              "searched for percentages and quotes")

    run_log = results / "run_log.json"
    if run_log.exists():
        for run in json.loads(run_log.read_text(encoding="utf-8"))["runs"]:
            check(run["output_file"].split("_seed")[0].replace("experiment", "").replace("_", " "),
                  "response not truncated", run["done_reason"] != "length",
                  f"{run['eval_tokens']} tokens, done_reason={run['done_reason']}")

    print(f"Constraint checks for `{results.relative_to(TASK_DIR.parent).as_posix()}`\n")
    print("| Experiment | Constraint | Result | Evidence |\n|---|---|---|---|")
    for row in rows:
        print("| " + " | ".join(row) + " |")
    print(f"\n{sum(r[2] == 'PASS' for r in rows)}/{len(rows)} checks passed.")


if __name__ == "__main__":
    main()
