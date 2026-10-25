import glob
import os
import subprocess
import tempfile
import time
import wave

import numpy as np
from rich.console import Console
import sounddevice as sd

WHISPER_BIN = "/opt/homebrew/bin/whisper-cli"
RATE = 16000
HINT = "terminal, port, kill, zip, folder, Downloads, files, disk, python, git, size, delete"


def model_path():
    found = sorted(glob.glob("models/ggml-small*.bin"))
    if not found:
        raise FileNotFoundError("No whisper model in models/")
    return found[0]


def record():
    """Caller has already pressed Enter to start; Enter again stops."""
    frames = []

    def cb(indata, n, t, status):
        frames.append(indata.copy())

    with sd.InputStream(samplerate=RATE, channels=1, dtype="int16", callback=cb):
        Console().input("  [bold red]●[/] listening…  [dim]press Enter to stop[/dim] ")
    return np.concatenate(frames) if frames else np.zeros((0, 1), dtype="int16")


def transcribe(audio):
    """Returns (text, seconds)."""
    t0 = time.time()
    if len(audio) < RATE * 0.3:
        return "", 0.0
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(audio.tobytes())
        out = subprocess.run(
            [WHISPER_BIN, "-m", model_path(), "-f", path, "-l", "auto",
             "-nt", "-np", "--prompt", HINT],
            capture_output=True, text=True,
        )
        text = " ".join(out.stdout.split())
        if not text and out.stderr:
            print(out.stderr[-500:])
    finally:
        os.unlink(path)
    return text, time.time() - t0


if __name__ == "__main__":
    input("Press Enter to start recording ")
    audio = record()
    text, secs = transcribe(audio)
    print(f"heard: {text!r}   ({secs:.1f}s)")
