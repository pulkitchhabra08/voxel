# Voxel

**Say it, understand it, run it.** An offline, voice-controlled terminal assistant for macOS. Speak in English, Hindi or Hinglish; Voxel turns your words into a shell command, explains it, checks it for danger, asks before anything risky, then runs it. Everything runs on your own laptop, with no hosted APIs.

**Track:** Narrow Agentic Tools (built to the local-inference rules) | **Team:** Pulkit Chhabra (solo) | **Event:** Hacktoberfest 26, Hack Day Jaipur, 25 Oct 2026


---

## Problem Statement & Target User

The terminal is powerful, but remembering exact commands and flags is slow and error-prone, especially for students and early developers who think in English, Hindi or Hinglish rather than in `lsof` and `du` flags. A plain script cannot turn *"Downloads ke sabse bade 5 files dikhao"* into a working command; this needs a language model.

Voxel is for developers and students who want to operate their Mac by speaking naturally, without sending their files, commands or voice to a cloud service. It does one job: **spoken request in, safe shell command out.**

## Approach, Architecture & Demo

**The one main task:** turn a spoken request into a single shell command, with a visible safety check before anything runs.

```
voice -> Whisper (stt.py) -> Qwen3 planner (planner.py) -> guard (guard.py) -> confirm -> runner (runner.py) -> output
```

| Module | Role |
|---|---|
| `stt.py` | Push-to-talk recording, then offline transcription with whisper.cpp (multilingual `small`). A hint prompt of terminal words (port, kill, zip, Downloads...) improves accuracy. |
| `planner.py` | Sends the sentence to Qwen3 4B via Ollama (`localhost:11434`) with temperature 0 and forced JSON output. Returns `{command, explanation, risk}`. |
| `guard.py` | Two independent safety layers: a regex **block list** (`sudo`, `dd`, `mkfs`, shutdown, pipe-to-shell, recursive deletes of broad paths such as `~` or `/`) and a **confirm list** (`rm`, `kill`, `mv`, overwrites, `chmod`, risky git). The model's own "high risk" label also triggers confirmation. |
| `runner.py` | Runs the approved command in zsh with a 30-second timeout and captures the output. |
| `main.py` | The loop and terminal UI (`rich`). The transcript is editable before it is sent, so a misheard word never causes a wrong action. Every run is logged to `logs/runs.jsonl`. |

**Guardrail and recovery path**

- Dangerous requests (for example "delete my entire home folder" or anything using `sudo`) are refused. The model declines in one sentence, and the guard blocks the command even if the model slips.
- Risky but legitimate commands (`kill`, `rm`) show a yellow **CONFIRM FIRST** panel and wait for `y`.
- Mis-heard speech is caught by the editable transcript. Typing mode (`t`) is a fallback if the microphone or room is bad.

**Terminal UI:** each command appears in a panel coloured green (safe), yellow (confirm first) or red (blocked), followed by the output and a timing footer (`stt`, `llm`, `run`, `total`).

## Model Details (name, size, licence, runtime, quantization, hardware)

| | Planner (reasoning) | Speech-to-text |
|---|---|---|
| **Model** | Qwen3 4B (`qwen3:4b`) | Whisper `small` (multilingual) |
| **Parameters** | 4B | 244M |
| **Licence** | Apache-2.0 | MIT (OpenAI Whisper weights) |
| **Runtime** | Ollama (local HTTP, `localhost:11434`) | whisper.cpp (`whisper-cli`) |
| **Quantization** | quantization        Q4_K_M | ggml format, `ggml-small.bin` |
| **Download size** | ~2.5 GB | ~466 MiB |

- **Hardware tested:** MacBook Air (Apple M5, 16 GB unified memory), macOS 26.6, Python 3.13. The planner runs 100% on the GPU (`ollama ps`: about 2.9 GB loaded).
- **External APIs:** none. All inference is local; the demo works with Wi-Fi off. The only network call is `localhost`.
- **Think mode:** Qwen3's reasoning mode is disabled (`"think": false` in the Ollama request), which cut planner latency from 100+ seconds to about 1 to 2 seconds.

## Setup Instructions

1. **Prerequisites:** macOS on Apple Silicon, [Homebrew](https://brew.sh), Python 3.10+.
2. **Install tools and dependencies:**
   ```bash
   brew install ollama whisper-cpp
   git clone https://github.com/pulkitchhabra08/voxel.git
   cd voxel
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Download the models:**
   ```bash
   ollama serve &            # skip if the Ollama app is already running
   ollama pull qwen3:4b
   # Whisper small (multilingual). Save it where model_path() in stt.py expects it:
   curl -L -C - --http1.1 -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin
   ```
4. **Start the app:**
   ```bash
   python main.py
   ```
   Press Enter to speak, `t` to type, `q` to quit. Pause half a second after pressing Enter before you start talking.
5. **Try example inputs:**
   - "what is using port 3000"
   - "Downloads ke sabse bade 5 files dikhao" (Hinglish)
   - "kill whatever is running on port 3000" (asks for confirmation)
   - "delete my entire home folder" (refused)

No API keys or secrets are needed. `.env.example` is included only as a placeholder.

## Results (screenshots / metrics from 3 runs)

Reproduce with `python bench.py` (3 repeated runs of a 12-prompt test set: 4 English, 4 Hinglish, 2 confirm-first, 2 refusals). A prompt only counts as a pass if the whole chain behaves correctly: the guard verdict is right, the command matches, and safe commands actually execute. Only commands the guard marks SAFE are ever executed by the benchmark. The run below was done with Wi-Fi off.



Raw data: [`results/bench_results.json`](results/bench_results.json). 

**Measured by hand (single runs):** Whisper small about 0.7 s for a short clip; end to end, from speaking to a command running, about 3 seconds.

**Known limitations**

- **Small-model errors.** A 4B model sometimes picks the wrong path or flag (for example listing the current directory instead of `~/Downloads`, or using GNU-only flags on macOS). The planner prompt now pins full paths, exact port numbers and macOS (BSD) flags; <<EDIT: list any case that still fails in the benchmark>>.
- **First spoken word can be dropped** by Whisper. The editable transcript is the safety net.
- **The guard is a safety net, not a sandbox.** It is regex-based and will not catch every dangerous command. Confirmation before risky actions is the real protection.
- **macOS only**, and `stt.py` calls `/opt/homebrew/bin/whisper-cli` by full path (Apple Silicon Homebrew default).
- **One command per request**, with no multi-step plans or follow-ups yet.

## Graphify Integration (link to graph) & Future Scope / Licence

**Graph:** [`graphify-out/graph.html`](graphify-out/graph.html) (screenshot below) | **Shared in Discord:** yes, https://discord.com/channels/1496114518160441345/1562682797460693075/1563822289558966363 | **Licence:** MIT

![Graphify codebase graph of Voxel](graph.png)

The graph (generated with `graphify extract . --code-only`) shows the pipeline as clusters: `stt.py` (`record`, `transcribe`), `planner.py` (`plan`), `guard.py` (`check`), `runner.py` (`run`) and `main.py` (`handle`).

**Future scope**

1. Self-healing: if a command fails, read the error, repair the command and retry once (through the guard again).
2. Speak the result back using macOS `say`.
3. Blast-radius preview before deletes ("this will remove 12 files, 84 MB").
4. Follow-up commands that remember the previous one.
5. Teach mode with longer explanations of each command.

## Third-party licences

- Qwen3: Apache-2.0 (Alibaba Qwen team), served via Ollama (MIT).
- Whisper model weights: MIT (OpenAI); whisper.cpp: MIT (ggml-org).
- Python libraries: `requests` (Apache-2.0), `rich` (MIT).

Voxel's own code is released under the MIT licence (see `LICENSE`).
