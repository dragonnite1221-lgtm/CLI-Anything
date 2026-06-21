# ruff: noqa: F403, F405, E501
from .gimp_backend_base import *  # noqa: F403


def _script_fu_escape(value: str) -> str:
    """Escape a Python string for safe use inside Script-Fu double quotes."""
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )


def find_gimp() -> str:
    """Find the GIMP executable. Raises RuntimeError if not found."""
    for name in ("gimp", "gimp-2.10", "gimp-2.99"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError(
        "GIMP is not installed. Install it with:\n  apt install gimp   # Debian/Ubuntu"
    )


def get_version() -> str:
    """Get the installed GIMP version string."""
    gimp = find_gimp()
    result = subprocess.run(
        [gimp, "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip()


def batch_script_fu(
    script: str,
    timeout: int = 120,
) -> dict:
    """Run a Script-Fu command in GIMP batch mode.

    Args:
        script: Script-Fu command string (single-quoted safe)
        timeout: Maximum seconds to wait

    Returns:
        Dict with stdout, stderr, return code
    """
    gimp = find_gimp()
    cmd = [gimp, "-i", "-b", script, "-b", "(gimp-quit 0)"]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    return {
        "command": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
