import subprocess
import time


def run(cmd, timeout=30):
    """Returns (returncode, output, seconds)."""
    t0 = time.time()
    try:
        p = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, executable="/bin/zsh",
        )
        return p.returncode, (p.stdout + p.stderr).strip()[-4000:], time.time() - t0
    except subprocess.TimeoutExpired:
        return 124, "(timed out)", time.time() - t0
