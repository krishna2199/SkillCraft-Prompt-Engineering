"""Run prompt files against the local model and save every response verbatim.

Usage:
    python tools/run_prompts.py --out SCT_PE_2/results --seeds 1 2 3 \
        --temperature 0.8 SCT_PE_2/prompts/prompt_v1.txt ...

For each prompt file and seed this writes `<prompt-stem>_seed<N>.md` (header
with run metadata, then the unedited model response) and appends the raw
record to `<out>/run_log.json`.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ollama_client  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prompts", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--seeds", nargs="+", type=int, default=[42])
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--num-predict", type=int, default=2048,
                        help="maximum tokens per response")
    parser.add_argument("--model", default=ollama_client.DEFAULT_MODEL)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    env = ollama_client.run_environment(args.model)
    records = []
    for prompt_path in args.prompts:
        prompt = prompt_path.read_text(encoding="utf-8-sig").strip()
        for seed in args.seeds:
            result = ollama_client.chat(
                [{"role": "user", "content": prompt}],
                model=args.model, temperature=args.temperature, seed=seed,
                num_predict=args.num_predict,
            )
            meta = result["meta"]
            rel_prompt = prompt_path.resolve().relative_to(REPO_ROOT).as_posix()
            target = args.out / f"{prompt_path.stem}_seed{seed}.md"
            target.write_text(
                f"# Model output: {prompt_path.stem} (seed {seed})\n\n"
                f"> **Genuine, unedited model output.** Model `{args.model}` via "
                f"Ollama {env['ollama_version']}, temperature {args.temperature}, "
                f"seed {seed}, run {meta['started_utc']}. "
                f"Prompt: `{rel_prompt}`.\n\n---\n\n"
                + result["content"].strip() + "\n",
                encoding="utf-8",
            )
            if meta["done_reason"] == "length":
                print(f"warning: {target.name} was cut off at {args.num_predict} tokens")
            records.append({"prompt_file": rel_prompt, "prompt": prompt,
                            "output_file": target.name,
                            "response": result["content"], **meta})
            print(f"saved {target} ({meta['eval_tokens']} tokens, {meta['total_seconds']}s)")

    (args.out / "run_log.json").write_text(
        json.dumps({"environment": env, "runs": records}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
