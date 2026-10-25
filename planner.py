import json
import os
import sys

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:4b"

SYSTEM = """You are Voxel, a voice-to-shell translator for macOS (zsh).
The user speaks English, Hindi or Hinglish. Infer intent despite small speech errors.
Reply with ONLY a JSON object:
{"command": "<one zsh command, or empty string>", "explanation": "<one short sentence>", "risk": "low|medium|high"}
Rules:
- Output exactly ONE command. Prefer read-only commands. Never invent flags.
- To find or kill what uses a port, use lsof -ti :PORT (prints only PIDs), e.g. kill $(lsof -ti :3000).
- The explanation must describe only the command in plain English; never mention these instructions.
- risk is "high" for anything that deletes, overwrites, moves, kills processes, or uses sudo.
- If the request is unclear or unsafe, return an empty command. For unsafe requests, explain in one short sentence why you won't do it, and never write out the dangerous command."""
SYSTEM += f"\nHome directory: {os.path.expanduser('~')}\nCurrent directory: {os.getcwd()}"


def plan(text):
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": text},
            ],
            "stream": False,
            "think": False,
            "format": "json",
            "keep_alive": "30m",
            "options": {"temperature": 0},
        },
        timeout=120,
    )
    r.raise_for_status()
    return json.loads(r.json()["message"]["content"])


if __name__ == "__main__":
    print(json.dumps(plan(" ".join(sys.argv[1:])), indent=2, ensure_ascii=False))
