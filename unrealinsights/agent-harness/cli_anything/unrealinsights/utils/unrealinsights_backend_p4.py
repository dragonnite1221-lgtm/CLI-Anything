# ruff: noqa: F403, F405, E501
from .unrealinsights_backend_base import *  # noqa: F403

# fmt: off
from .unrealinsights_backend_p3 import run_process  # noqa: E402,E501
# fmt: on


def is_process_running(pid: int | None) -> bool:
    """Check whether a process is still running."""
    if not pid or pid <= 0:
        return False

    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        stdout = result.stdout.strip()
        return (
            bool(stdout)
            and "No tasks are running" not in stdout
            and "INFO:" not in stdout
        )

    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def terminate_process(
    pid: int, force: bool = False, timeout: float | None = None
) -> dict[str, object]:
    """Terminate a process tree and report whether it stopped."""
    if pid <= 0:
        raise RuntimeError(f"Invalid PID: {pid}")

    if os.name == "nt":
        command = ["taskkill", "/PID", str(pid), "/T"]
        if force:
            command.append("/F")
        result = run_process(command, timeout=timeout, wait=True)
    else:
        sig = signal.SIGKILL if force else signal.SIGTERM
        signal_arg = f"-{sig.name}"
        try:
            os.kill(pid, sig)
            result = {
                "command": ["kill", signal_arg, str(pid)],
                "waited": True,
                "timed_out": False,
                "exit_code": 0,
                "stdout": "",
                "stderr": "",
                "pid": None,
            }
        except OSError as exc:
            result = {
                "command": ["kill", signal_arg, str(pid)],
                "waited": True,
                "timed_out": False,
                "exit_code": 1,
                "stdout": "",
                "stderr": str(exc),
                "pid": None,
            }

    deadline = time.time() + (timeout or 10)
    while time.time() < deadline and is_process_running(pid):
        time.sleep(0.25)

    result["stopped"] = not is_process_running(pid)
    result["requested_pid"] = pid
    result["force"] = force
    return result


def parse_unreal_log(log_path: str | Path) -> dict[str, object]:
    """Extract warning and error lines from an Unreal log file."""
    path = Path(log_path).expanduser().resolve()
    if not path.is_file():
        return {
            "path": str(path),
            "exists": False,
            "warnings": [],
            "errors": [],
            "tail": [],
        }

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    warnings = [line for line in lines if "Warning:" in line]
    errors = [line for line in lines if "Error:" in line]
    return {
        "path": str(path),
        "exists": True,
        "warnings": warnings,
        "errors": errors,
        "tail": lines[-20:],
    }
