# ruff: noqa: F403, F405, E501
from .pm2_backend_base import *  # noqa: F403

# fmt: off
from .pm2_backend_p1 import pm2_jlist, run_pm2  # noqa: E402,E501
# fmt: on


def pm2_describe(name: str) -> dict[str, Any] | None:
    """Get detailed info for a specific process.

    Uses pm2 jlist and filters by name/id, since pm2 describe
    does not produce JSON output.

    Args:
        name: Process name or ID.

    Returns:
        Process description dict, or None on failure.
    """
    processes = pm2_jlist()
    for p in processes:
        if p.get("name") == name or str(p.get("pm_id")) == str(name):
            return p
    return None


def pm2_action(action: str, name: str) -> dict[str, Any]:
    """Run a lifecycle action (restart, stop, delete) on a process.

    Args:
        action: One of "restart", "stop", "delete".
        name: Process name or ID.

    Returns:
        Result dict from run_pm2.
    """
    return run_pm2(action, str(name))


def pm2_start(script: str, name: str | None = None) -> dict[str, Any]:
    """Start a new PM2 process.

    Args:
        script: Path to script or ecosystem file.
        name: Optional process name.

    Returns:
        Result dict from run_pm2.
    """
    args = ["start", script]
    if name:
        args.extend(["--name", name])
    return run_pm2(*args)


def pm2_logs(name: str, lines: int = 20) -> dict[str, Any]:
    """Get recent logs for a process.

    Args:
        name: Process name or ID.
        lines: Number of log lines to retrieve.

    Returns:
        Result dict from run_pm2.
    """
    return run_pm2("logs", str(name), "--lines", str(lines), "--nostream")


def pm2_flush(name: str | None = None) -> dict[str, Any]:
    """Flush logs for a process or all processes.

    Args:
        name: Process name or ID. If None, flushes all.

    Returns:
        Result dict from run_pm2.
    """
    args = ["flush"]
    if name:
        args.append(str(name))
    return run_pm2(*args)


def pm2_save() -> dict[str, Any]:
    """Save the current PM2 process list."""
    return run_pm2("save")


def pm2_startup() -> dict[str, Any]:
    """Generate PM2 startup script."""
    return run_pm2("startup")


def pm2_version() -> str:
    """Get PM2 version string."""
    result = run_pm2("--version")
    if result["success"]:
        return result["stdout"].strip()
    return "unknown"
