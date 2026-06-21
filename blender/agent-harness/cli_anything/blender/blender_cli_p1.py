# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


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
    """Launch the Blender live preview poller in the background."""
    cli_path = shutil.which("cli-anything-blender")
    if cli_path:
        command = [cli_path, "preview", "live", "monitor", "--session-dir", session_dir]
    else:
        command = [
            sys.executable,
            "-m",
            "cli_anything.blender.blender_cli",
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
