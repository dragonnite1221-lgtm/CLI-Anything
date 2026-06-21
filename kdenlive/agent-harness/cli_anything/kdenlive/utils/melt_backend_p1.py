# ruff: noqa: F403, F405, E501
from .melt_backend_base import *  # noqa: F403


def _validate_codec(value: str, allowed: frozenset, label: str) -> str:
    """Validate that a codec name is in the allowlist."""
    if not value:
        return value
    if value not in allowed:
        raise ValueError(
            f"Unsupported {label}: '{value}'. Allowed values: {sorted(allowed)}"
        )
    return value


_BLOCKED_ARG_PREFIXES = ("vcodec=", "acodec=", "-consumer")


def _validate_extra_args(extra_args: list) -> list:
    """Reject extra_args that would bypass codec or consumer validation."""
    for arg in extra_args:
        for prefix in _BLOCKED_ARG_PREFIXES:
            if arg.startswith(prefix):
                raise ValueError(
                    f"extra_args cannot override '{prefix.rstrip('=')}'. "
                    f"Use the dedicated parameter instead."
                )
    return extra_args


def find_melt() -> str:
    """Find the melt executable. Raises RuntimeError if not found."""
    path = shutil.which("melt")
    if path:
        return path
    raise RuntimeError(
        "melt is not installed. Install it with:\n  apt install melt   # Debian/Ubuntu"
    )


def find_ffmpeg() -> str:
    """Find ffmpeg executable."""
    path = shutil.which("ffmpeg")
    if path:
        return path
    raise RuntimeError("ffmpeg is not installed. apt install ffmpeg")


def get_melt_version() -> str:
    """Get the installed melt version string."""
    melt = find_melt()
    result = subprocess.run(
        [melt, "--version"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    # melt outputs version info differently
    output = result.stdout.strip() or result.stderr.strip()
    return output.split("\n")[0] if output else "unknown"
