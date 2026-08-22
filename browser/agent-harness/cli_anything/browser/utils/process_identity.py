"""Linux process identities that remain stable across PID reuse."""

from __future__ import annotations

from pathlib import Path


def process_identity(pid: int) -> str | None:
    """Return the kernel start-time field for a live process, or ``None`` if unavailable."""

    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        closing = stat.rfind(")")
        fields = stat[closing + 2 :].split()
        return fields[19] if closing >= 0 and len(fields) > 19 else None
    except OSError:
        return None
