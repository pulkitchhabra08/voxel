import json
import os
import time

from rich import box
from rich.console import Console, Group
from rich.markup import escape
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

import guard
import planner
import runner

console = Console()
COLORS = {"allow": "green", "confirm": "yellow", "block": "red"}
LABELS = {"allow": "SAFE", "confirm": "CONFIRM FIRST", "block": "BLOCKED"}


def log(entry):
    os.makedirs("logs", exist_ok=True)
    with open("logs/runs.jsonl", "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def banner():
    title = Text("V O X E L", style="bold cyan", justify="center")
    sub = Text("say it · understand it · run it", style="dim", justify="center")
    meta = Text(f"{planner.MODEL} · whisper small · 100% offline", style="dim", justify="center")
    console.print(Panel(Group(title, sub, meta), box=box.ROUNDED, border_style="cyan", padding=(1, 4)))


def listen():
    import stt
    audio = stt.record()
    with console.status("[dim]transcribing…[/dim]", spinner="dots"):
        text, secs = stt.transcribe(audio)
    if not text:
        return "", 0.0
    console.print(f"  [bold cyan]heard[/] ❯ {escape(text)}  [dim]({secs:.1f}s)[/dim]")
    fix = console.input("  [dim]⏎ accept, or type a correction[/dim] ❯ ").strip()
    return (fix or text), secs


def handle(text, t_stt=0.0):
    t0 = time.time()
    with console.status("[dim]thinking…[/dim]", spinner="dots"):
        p = planner.plan(text)
    llm_s = round(time.time() - t0, 2)
    cmd = (p.get("command") or "").strip()
    explanation = (p.get("explanation") or "").strip()
    entry = {"input": text, "command": cmd, "risk": p.get("risk"), "stt_s": round(t_stt, 2), "llm_s": llm_s}

    if not cmd:
        console.print(Panel(Text(explanation or "I couldn't turn that into a command."),
                            title="[yellow]? need more info[/]", title_align="left",
                            border_style="yellow", box=box.ROUNDED, padding=(1, 2)))
        entry["outcome"] = "no_command"
        return log(entry)

    verdict, reason = guard.check(cmd, p.get("risk", "medium"))
    color = COLORS[verdict]
    body = Group(
        Syntax(cmd, "bash", theme="ansi_dark", background_color="default", word_wrap=True),
        Text(""),
        Text(explanation, style="dim"),
    )
    console.print(Panel(body, title=f"[bold {color}]{LABELS[verdict]}[/]", title_align="left",
                        subtitle=f"[{color}]{reason}[/]" if reason else None, subtitle_align="left",
                        border_style=color, box=box.ROUNDED, padding=(1, 2)))

    if verdict == "block":
        console.print("  [red]⛔ Not running this.[/]")
        entry["outcome"] = "blocked"
        return log(entry)

    if verdict == "confirm":
        ans = console.input("  [yellow]⚠ Run it?[/] [dim](y/N)[/dim] ❯ ").strip().lower()
        if ans != "y":
            console.print("  [dim]Skipped.[/dim]")
            entry["outcome"] = "declined"
            return log(entry)

    with console.status("[dim]running…[/dim]", spinner="dots"):
        code, out, run_s = runner.run(cmd)

    if out:
        console.print(Panel(Text(out), title="output", title_align="left",
                            border_style="dim", box=box.ROUNDED, padding=(0, 2)))
    elif code == 1:
        console.print("  [dim](no matches found)[/dim]")

    ok = code == 0 or (code == 1 and not out)
    mark = "[green]✓ done[/]" if ok else f"[red]✗ exit {code}[/]"
    total = t_stt + (time.time() - t0)
    console.print(f"  {mark}  [dim]stt {t_stt:.1f}s · llm {llm_s}s · run {run_s:.1f}s · total {total:.1f}s[/dim]")
    entry.update(outcome="ran", exit=code)
    log(entry)


def main():
    console.print()
    banner()
    while True:
        try:
            c = console.input("\n[bold cyan]❯[/] [dim]⏎ speak · t type · q quit[/dim] ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break
        if c == "q":
            break
        if c == "t":
            text, t_stt = console.input("  [bold cyan]type[/] ❯ ").strip(), 0.0
        else:
            text, t_stt = listen()
        if text:
            handle(text, t_stt)
        else:
            console.print("  [yellow]Didn't catch that. Try again.[/]")
    console.print("[dim]bye 👋[/dim]")


if __name__ == "__main__":
    main()
