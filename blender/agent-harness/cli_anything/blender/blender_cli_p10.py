# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403

# fmt: off
from .blender_cli_p1 import get_session, output  # noqa: E402,E501
from .blender_cli_p2 import cli, handle_error  # noqa: E402,E501
from .blender_cli_p9 import preview_live_group  # noqa: E402,E501
# fmt: on


@preview_live_group.command("push")
@click.option("--recipe", default="quick", help="Preview recipe name")
@click.option("--force", is_flag=True, help="Bypass preview cache")
@click.option("--root-dir", default=None, help="Override preview root directory")
@click.option(
    "--poll-ms",
    default=1500,
    show_default=True,
    help="Suggested viewer polling interval",
)
@handle_error
def preview_live_push(recipe, force, root_dir, poll_ms):
    """Publish a fresh bundle into the live preview session."""
    sess = get_session()
    result = preview_mod.live_push(
        sess,
        recipe=recipe,
        force=force,
        root_dir=root_dir,
        refresh_hint_ms=poll_ms,
        command=(
            f"cli-anything-blender --project {sess.project_path or ''} "
            f"preview live push --recipe {recipe}"
        ).strip(),
    )
    output(result, f"Updated live preview session: {result.get('_session_dir', '')}")


@preview_live_group.command("status")
@click.option("--recipe", default="quick", help="Preview recipe name")
@click.option("--root-dir", default=None, help="Override preview root directory")
@handle_error
def preview_live_status(recipe, root_dir):
    """Show live preview session metadata."""
    sess = get_session()
    result = preview_mod.live_status(sess, recipe=recipe, root_dir=root_dir)
    output(result, f"Live preview session: {result.get('_session_dir', '')}")


@preview_live_group.command("stop")
@click.option("--recipe", default="quick", help="Preview recipe name")
@click.option("--root-dir", default=None, help="Override preview root directory")
@handle_error
def preview_live_stop(recipe, root_dir):
    """Stop the live preview session without deleting artifacts."""
    sess = get_session()
    result = preview_mod.live_stop(sess, recipe=recipe, root_dir=root_dir)
    output(result, f"Stopped live preview session: {result.get('_session_dir', '')}")


@preview_live_group.command("monitor", hidden=True)
@click.option("--session-dir", required=True, help="Live session directory to monitor.")
@handle_error
def preview_live_monitor(session_dir):
    """Internal background poller for live preview sessions."""
    result = preview_mod.run_live_poller(session_dir)
    output(result, "")


@cli.group()
def session():
    """Session management commands."""
    pass


@session.command("status")
@handle_error
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    output({"undone": desc}, f"Undone: {desc}")


@session.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"redone": desc}, f"Redone: {desc}")


@session.command("history")
@handle_error
def session_history():
    """Show undo history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "Undo history:")


def main():
    cli()
