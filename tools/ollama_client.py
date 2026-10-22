"""Minimal, dependency-free client for a local Ollama server.

Every call returns the model text together with the metadata needed to
reproduce it (model name, model digest, sampling options, timings), so that
each saved output in this repository can be traced to a real model run.
"""

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")


class OllamaUnavailable(RuntimeError):
    """Raised when the local Ollama server cannot be reached."""


def _request(path, payload=None, timeout=900):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        HOST + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise OllamaUnavailable(f"Cannot reach Ollama at {HOST}: {exc}") from exc


def server_version():
    return _request("/api/version")["version"]


def model_digest(model=DEFAULT_MODEL):
    for entry in _request("/api/tags").get("models", []):
        if entry["name"] == model:
            return entry["digest"]
    raise OllamaUnavailable(f"Model {model!r} is not pulled. Run: ollama pull {model}")


def chat(messages, *, model=DEFAULT_MODEL, temperature=0.7, seed=42,
         num_predict=1024, json_mode=False):
    """Send a chat request and return {"content": str, "meta": dict}."""
    options = {"temperature": temperature, "seed": seed, "num_predict": num_predict}
    payload = {"model": model, "messages": messages, "stream": False, "options": options}
    if json_mode:
        payload["format"] = "json"
    started = datetime.now(timezone.utc)
    resp = _request("/api/chat", payload)
    meta = {
        "model": model,
        "options": options,
        "json_mode": json_mode,
        "started_utc": started.isoformat(timespec="seconds"),
        "eval_tokens": resp.get("eval_count"),
        "prompt_tokens": resp.get("prompt_eval_count"),
        "total_seconds": round(resp.get("total_duration", 0) / 1e9, 2),
        "done_reason": resp.get("done_reason"),
    }
    return {"content": resp["message"]["content"], "meta": meta}


def run_environment(model=DEFAULT_MODEL):
    """Describe the runtime once per experiment for the run log."""
    return {
        "runtime": "Ollama (local)",
        "ollama_version": server_version(),
        "model": model,
        "model_digest": model_digest(model),
    }
