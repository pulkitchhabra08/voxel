import re

BLOCK = [
    (r"\bsudo\b", "uses sudo (admin rights)"),
    (r"\bmkfs\b|\bdiskutil\s+(erase|partition)", "can erase a disk"),
    (r"\bdd\b", "raw disk write"),
    (r":\(\)\s*\{", "fork bomb"),
    (r"\b(shutdown|reboot|halt)\b", "shuts down the machine"),
    (r"(curl|wget)[^|;]*\|\s*(sh|bash|zsh)", "pipes a download straight into a shell"),
]

CONFIRM = [
    (r"\brm\b", "deletes files"),
    (r"\b(kill|killall|pkill)\b", "kills a process"),
    (r"\bmv\b", "moves or overwrites files"),
    (r">", "writes or overwrites a file"),
    (r"\b(chmod|chown)\b", "changes permissions"),
    (r"\bgit\s+(reset|clean|push)", "changes git history or files"),
]

SAFE_REDIRECTS = re.compile(r"2>&1|2>\s*/dev/null|>\s*/dev/null")


def broad_rm(cmd):
    return (
        re.search(r"\brm\b", cmd)
        and re.search(r"\s-\w*[rf]", cmd)
        and re.search(r"(\s|^)(/|~|~/|\$HOME|\*|\.|\.\.)(\s|$)", cmd)
    )


def check(cmd, model_risk="medium"):
    """Returns (verdict, reason). Verdict is 'block', 'confirm' or 'allow'."""
    c = SAFE_REDIRECTS.sub("", cmd)
    if broad_rm(c):
        return "block", "recursive delete on a broad path"
    for pat, why in BLOCK:
        if re.search(pat, c):
            return "block", why
    for pat, why in CONFIRM:
        if re.search(pat, c):
            return "confirm", why
    if model_risk == "high":
        return "confirm", "the model flagged this as high risk"
    return "allow", ""
