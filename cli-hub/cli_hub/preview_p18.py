# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def open_in_browser(target: str) -> Dict[str, Any]:
    candidates = [
        ("chromium", ["chromium", f"--app={target}"]),
        ("google-chrome", ["google-chrome", f"--app={target}"]),
        ("google-chrome-stable", ["google-chrome-stable", f"--app={target}"]),
        ("microsoft-edge", ["microsoft-edge", f"--app={target}"]),
        ("firefox", ["firefox", "--new-window", target]),
        ("xdg-open", ["xdg-open", target]),
    ]
    for label, command in candidates:
        binary = shutil.which(command[0])
        if not binary:
            continue
        full_command = [binary] + command[1:]
        process = subprocess.Popen(
            full_command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return {
            "launched": True,
            "browser": label,
            "pid": process.pid,
            "command": full_command,
        }
    return {
        "launched": False,
        "browser": None,
        "command": [],
        "reason": "No supported browser launcher found on PATH",
    }
