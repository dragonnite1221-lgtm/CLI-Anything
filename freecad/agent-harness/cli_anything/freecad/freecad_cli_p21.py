# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import _spawn_live_poller, _spawn_live_viewer, get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p20 import preview_live_group  # noqa: E402,E501
# fmt: on


@preview_live_group.command("start")
@click.option("--recipe", default="quick", help="Preview recipe name.")
@click.option("--force", is_flag=True, help="Bypass preview cache.")
@click.option("--root-dir", default=None, help="Override preview root directory.")
@click.option(
    "--poll-ms",
    default=1500,
    show_default=True,
    help="Suggested viewer polling interval.",
)
@click.option(
    "--mode",
    type=click.Choice(["poll", "manual"]),
    default="poll",
    show_default=True,
    help="Live preview mode. Poll mode auto-captures when the project file changes.",
)
@click.option(
    "--source-poll-ms",
    default=500,
    show_default=True,
    help="Polling interval for source project changes in poll mode.",
)
@click.option(
    "--open",
    "open_window",
    is_flag=True,
    help="Launch cli-hub live viewer in a separate window.",
)
@handle_error
def preview_live_start(
    recipe: str,
    force: bool,
    root_dir: Optional[str],
    poll_ms: int,
    mode: str,
    source_poll_ms: int,
    open_window: bool,
) -> None:
    """Start a live preview session and publish the latest bundle."""
    sess = get_session()
    result = preview_mod.live_start(
        sess,
        recipe=recipe,
        force=force,
        root_dir=root_dir,
        refresh_hint_ms=poll_ms,
        live_mode=mode,
        source_poll_ms=source_poll_ms,
        command=(
            f"cli-anything-freecad -p {sess.project_path or ''} "
            f"preview live start --recipe {recipe}"
        ).strip(),
    )
    if result.get("live_mode") == "poll" and not result.get("poller", {}).get(
        "running"
    ):
        result["poller"] = _spawn_live_poller(result["_session_dir"])
    if open_window:
        result["viewer"] = _spawn_live_viewer(result["_session_dir"], poll_ms)
    output_fn(result, f"Started live preview session: {result.get('_session_dir', '')}")


@preview_live_group.command("push")
@click.option("--recipe", default="quick", help="Preview recipe name.")
@click.option("--force", is_flag=True, help="Bypass preview cache.")
@click.option("--root-dir", default=None, help="Override preview root directory.")
@click.option(
    "--poll-ms",
    default=1500,
    show_default=True,
    help="Suggested viewer polling interval.",
)
@handle_error
def preview_live_push(
    recipe: str, force: bool, root_dir: Optional[str], poll_ms: int
) -> None:
    """Publish a fresh bundle into the live preview session."""
    sess = get_session()
    result = preview_mod.live_push(
        sess,
        recipe=recipe,
        force=force,
        root_dir=root_dir,
        refresh_hint_ms=poll_ms,
        source_poll_ms=preview_mod.DEFAULT_SOURCE_POLL_MS,
        command=(
            f"cli-anything-freecad -p {sess.project_path or ''} "
            f"preview live push --recipe {recipe}"
        ).strip(),
    )
    output_fn(result, f"Updated live preview session: {result.get('_session_dir', '')}")


@preview_live_group.command("status")
@click.option("--recipe", default="quick", help="Preview recipe name.")
@click.option("--root-dir", default=None, help="Override preview root directory.")
@handle_error
def preview_live_status(recipe: str, root_dir: Optional[str]) -> None:
    """Show live preview session metadata."""
    sess = get_session()
    result = preview_mod.live_status(sess, recipe=recipe, root_dir=root_dir)
    output_fn(result, f"Live preview session: {result.get('_session_dir', '')}")


@preview_live_group.command("stop")
@click.option("--recipe", default="quick", help="Preview recipe name.")
@click.option("--root-dir", default=None, help="Override preview root directory.")
@handle_error
def preview_live_stop(recipe: str, root_dir: Optional[str]) -> None:
    """Stop the live preview session without deleting artifacts."""
    sess = get_session()
    result = preview_mod.live_stop(sess, recipe=recipe, root_dir=root_dir)
    output_fn(result, f"Stopped live preview session: {result.get('_session_dir', '')}")


@preview_live_group.command("monitor", hidden=True)
@click.option("--session-dir", required=True, help="Live session directory to monitor.")
@handle_error
def preview_live_monitor(session_dir: str) -> None:
    """Internal background poller for live preview sessions."""
    result = preview_mod.run_live_poller(session_dir)
    output_fn(result, "")


@cli.group("motion")
def motion_group():
    """Motion sequencing and final showcase rendering commands."""
    pass
