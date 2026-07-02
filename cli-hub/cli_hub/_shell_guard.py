"""Consent gate for registry install commands that execute a shell.

Registry entries may ship shell-operator commands (``curl … | bash``) that
download and run remote code. The registry is fetched over the network, so a
compromised or spoofed registry would otherwise get silent code execution on
``cli-hub install``. This gate forces informed consent before any such command
runs: an interactive ``y`` confirmation, or an explicit
``CLI_HUB_ALLOW_SHELL_INSTALL=1`` opt-in for CI / non-interactive use.

Plain commands (no shell operators, run via ``shlex.split`` without a shell)
are unaffected — they cannot invoke a shell interpreter.
"""

from __future__ import annotations

import os
import sys

SHELL_METACHARACTERS = ("|", "&&", "||", ";", "$(", "`", ">", "<")

ALLOW_ENV = "CLI_HUB_ALLOW_SHELL_INSTALL"


def has_shell_operator(cmd: str) -> bool:
    """True if the command string contains a shell operator/redirection."""
    return any(token in cmd for token in SHELL_METACHARACTERS)


def confirm_shell_command(cmd: str) -> bool:
    """Return True only if the shell command is allowed to run.

    Order: explicit env opt-in wins; otherwise require an interactive ``y``.
    Non-interactive without the opt-in is refused (fail closed).
    """
    if os.environ.get(ALLOW_ENV) == "1":
        return True
    if not sys.stdin.isatty():
        return False
    sys.stderr.write(
        "\n⚠  This install runs a shell command from the registry that can "
        "execute remote code:\n\n    " + cmd + "\n\n"
        "Only continue if you trust this source. Proceed? [y/N] "
    )
    sys.stderr.flush()
    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer in ("y", "yes")
