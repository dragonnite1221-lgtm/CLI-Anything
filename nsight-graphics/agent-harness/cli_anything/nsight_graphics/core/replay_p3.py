# ruff: noqa: F403, F405, E501
from .replay_base import *  # noqa: F403
# fmt: off
from .replay_p1 import _read_text, _write_stdout  # noqa: E402,E501
from .replay_p2 import _compact_result  # noqa: E402,E501
# fmt: on


def _run_stdout_export(
    binaries: dict[str, str | None],
    *,
    capture_file: str,
    output_file: Path,
    kind: str,
    replay_flag: str,
    timeout: int = 300,
) -> dict[str, Any]:
    """Run a metadata-style replay command and save stdout."""
    command = backend.build_replay_command(
        binaries,
        capture_file=capture_file,
        extra_args=[replay_flag],
    )
    result = backend.run_command(command, timeout=timeout)
    _write_stdout(output_file, result.get("stdout") or "")
    return _compact_result(kind, result, stdout_file=output_file)
def _read_error_summary(path: Path, limit: int = 10) -> list[str]:
    """Read a compact captured-log error summary."""
    if not path.is_file():
        return []
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    return [line for line in lines if line][:limit]
def _is_no_error_line(line: str) -> bool:
    """Return whether ngfx-replay is explicitly reporting an empty error set."""
    return line.strip().lower().startswith("no log messages found")
def _summarize_logs(log_file: Path | None, errors_file: Path | None, limit: int = 10) -> dict[str, Any]:
    """Summarize captured replay logs and separate no-error markers from errors."""
    log_lines = [line.strip() for line in _read_text(log_file).splitlines() if line.strip()] if log_file else []
    raw_error_lines = [line.strip() for line in _read_text(errors_file).splitlines() if line.strip()] if errors_file else []
    if raw_error_lines and all(_is_no_error_line(line) for line in raw_error_lines):
        error_lines: list[str] = []
        status = "no_errors"
    elif raw_error_lines:
        error_lines = raw_error_lines
        status = "errors_present"
    else:
        error_lines = []
        status = "no_error_artifact" if errors_file else "not_requested"

    return {
        "log_line_count": len(log_lines),
        "error_line_count": len(error_lines),
        "error_summary": error_lines[:limit],
        "raw_error_summary": raw_error_lines[:limit],
        "status": status,
    }
def _has_files(path: Path) -> bool:
    """Return whether a directory contains at least one non-empty file."""
    if not path.is_dir():
        return False
    for child in path.rglob("*"):
        if child.is_file() and child.stat().st_size > 0:
            return True
    return False
