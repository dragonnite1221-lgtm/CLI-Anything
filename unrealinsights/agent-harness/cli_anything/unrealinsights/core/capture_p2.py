# ruff: noqa: F403, F405, E501
from .capture_base import *  # noqa: F403

# fmt: off
from .capture_p1 import build_capture_command  # noqa: E402,E501
# fmt: on


def run_capture(
    target_exe: str,
    output_trace: str,
    channels: str = DEFAULT_CHANNELS,
    exec_cmds: Sequence[str] | None = None,
    target_args: Sequence[str] | None = None,
    wait: bool = False,
    timeout: float | None = None,
) -> dict[str, object]:
    """Launch a traced target executable."""
    backend.ensure_parent_dir(output_trace)
    command = build_capture_command(
        target_exe,
        output_trace=output_trace,
        channels=channels,
        exec_cmds=exec_cmds,
        target_args=target_args,
    )
    result = backend.run_process(command, timeout=timeout, wait=wait)

    trace_path = Path(output_trace).expanduser().resolve()
    trace_exists = trace_path.is_file()
    trace_size = trace_path.stat().st_size if trace_exists else None
    waited = bool(result.get("waited", wait))
    succeeded = True
    if waited:
        succeeded = (
            not bool(result.get("timed_out"))
            and result.get("exit_code") == 0
            and trace_exists
        )

    result.update(
        {
            "target_exe": str(Path(target_exe).expanduser().resolve()),
            "target_args": list(target_args or []),
            "trace_path": str(trace_path),
            "channels": channels,
            "trace_exists": trace_exists,
            "trace_size": trace_size,
            "succeeded": succeeded,
        }
    )
    return result


def capture_status(session) -> dict[str, object]:
    """Return the current tracked capture status."""
    info = session.capture_info()
    pid = info.get("pid")
    info["running"] = backend.is_process_running(pid) if pid else False
    return info


def stop_capture(
    session, force: bool = False, timeout: float | None = None
) -> dict[str, object]:
    """Stop the currently tracked capture process."""
    info = capture_status(session)
    pid = info.get("pid")
    if not pid:
        raise RuntimeError("No active capture session is being tracked.")

    termination = backend.terminate_process(int(pid), force=force, timeout=timeout)
    status = capture_status(session)
    result = {
        "termination": termination,
        "capture": status,
    }
    if termination.get("stopped"):
        session.clear_capture()
        result["capture"] = session.capture_info()
        if info.get("trace_path"):
            session.set_trace(info["trace_path"])
    return result


def snapshot_capture(session, output_trace: str | None = None) -> dict[str, object]:
    """Create a best-effort copy of the current trace file."""
    info = capture_status(session)
    source = info.get("trace_path")
    if not source:
        raise RuntimeError("No active capture trace is available to snapshot.")

    source_path = Path(source).expanduser().resolve()
    if not source_path.is_file():
        raise RuntimeError(f"Trace file not found: {source_path}")

    if output_trace:
        output_path = Path(output_trace).expanduser().resolve()
    else:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_path = source_path.with_name(
            f"{source_path.stem}-snapshot-{timestamp}{source_path.suffix}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, output_path)
    return {
        "source_trace": str(source_path),
        "snapshot_trace": str(output_path),
        "snapshot_exists": output_path.is_file(),
        "snapshot_size": output_path.stat().st_size if output_path.is_file() else None,
        "capture_running": info.get("running", False),
    }
