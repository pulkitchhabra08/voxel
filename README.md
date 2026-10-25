# Voxel
Speak to your terminal, fully offline. | **Track:** Narrow Agentic Tools

*Say it. Understand it. Run it.*

Push-to-talk -> whisper.cpp (Whisper small) -> Qwen3 4B via Ollama -> safety guard -> confirm -> run.
Runs 100% on-device (MacBook Air M5, 16 GB). No hosted APIs.

## Setup
1. `brew install ollama whisper-cpp && brew services start ollama`
2. `ollama pull qwen3:4b`
3. Download `ggml-small.bin` from the whisper.cpp Hugging Face repo into `models/`
4. `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
5. `python main.py`

## Licence
MIT
