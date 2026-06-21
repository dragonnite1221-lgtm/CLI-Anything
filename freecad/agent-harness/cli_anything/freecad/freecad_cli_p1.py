# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403


def get_session() -> Session:
    """Get or create the global session."""
    global _session
    if _session is None:
        _session = Session()
    return _session


def output(data: Any, message: str = "") -> None:
    """Print data as JSON or human-readable."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    click.echo(f"  {k}: {json.dumps(v, default=str)}")
                else:
                    click.echo(f"  {k}: {v}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    label = item.get("name", item.get("type", f"#{i}"))
                    click.echo(f"  [{i}] {label}")
                    for k, v in item.items():
                        if k != "name":
                            click.echo(f"      {k}: {v}")
                else:
                    click.echo(f"  [{i}] {item}")


def _spawn_live_viewer(session_dir: str, poll_ms: int) -> dict:
    """Launch cli-hub live preview watcher when available."""
    hub = shutil.which("cli-hub")
    command = [
        hub or "cli-hub",
        "previews",
        "watch",
        session_dir,
        "--open",
        "--poll-ms",
        str(int(poll_ms)),
    ]
    if hub is None:
        return {
            "launched": False,
            "command": command,
            "reason": "cli-hub not found on PATH",
        }
    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return {
        "launched": True,
        "pid": process.pid,
        "command": command,
    }


def _spawn_live_poller(session_dir: str) -> dict:
    """Launch the FreeCAD live preview poller in the background."""
    cli_path = shutil.which("cli-anything-freecad")
    if cli_path:
        command = [cli_path, "preview", "live", "monitor", "--session-dir", session_dir]
    else:
        command = [
            sys.executable,
            "-m",
            "cli_anything.freecad.freecad_cli",
            "preview",
            "live",
            "monitor",
            "--session-dir",
            session_dir,
        ]
    log_path = os.path.join(session_dir, "poller.log")
    log_fh = open(log_path, "ab")
    process = subprocess.Popen(
        command,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        close_fds=True,
    )
    log_fh.close()
    preview_mod.record_live_poller_spawn(
        session_dir,
        pid=process.pid,
        command=command,
        log_path=log_path,
    )
    return {
        "launched": True,
        "pid": process.pid,
        "command": command,
        "log_path": log_path,
    }
