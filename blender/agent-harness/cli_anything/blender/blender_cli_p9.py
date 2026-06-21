# ruff: noqa: F403, F405, E501
from .blender_cli_base import *  # noqa: F403

# fmt: off
from .blender_cli_p1 import _spawn_live_poller, _spawn_live_viewer, get_session, output  # noqa: E402,E501
from .blender_cli_p2 import cli, handle_error  # noqa: E402,E501
from .blender_cli_p8 import render_group  # noqa: E402,E501
# fmt: on


@render_group.command("execute")
@click.argument("output_path")
@click.option("--frame", "-f", type=int, default=None, help="Specific frame to render")
@click.option("--animation", "-a", is_flag=True, help="Render full animation")
@click.option("--overwrite", is_flag=True, help="Overwrite existing file")
@handle_error
def render_execute(output_path, frame, animation, overwrite):
    """Render the scene (generates bpy script)."""
    sess = get_session()
    result = render_mod.render_scene(
        sess.get_project(),
        output_path,
        frame=frame,
        animation=animation,
        overwrite=overwrite,
    )
    output(result, f"Render script generated: {result['script_path']}")


@render_group.command("script")
@click.argument("output_path")
@click.option("--frame", "-f", type=int, default=None)
@click.option("--animation", "-a", is_flag=True)
@handle_error
def render_script(output_path, frame, animation):
    """Generate bpy script without rendering."""
    sess = get_session()
    script = render_mod.generate_bpy_script(
        sess.get_project(),
        output_path,
        frame=frame,
        animation=animation,
    )
    click.echo(script)


@cli.group("preview")
def preview_group():
    """Preview bundle capture and inspection."""
    pass


@preview_group.group("live")
def preview_live_group():
    """Live preview session management."""
    pass


@preview_group.command("recipes")
@handle_error
def preview_recipes():
    """List available preview recipes."""
    output(preview_mod.list_recipes(), "Preview recipes:")


@preview_group.command("capture")
@click.option("--recipe", default="quick", help="Preview recipe name")
@click.option("--force", is_flag=True, help="Bypass preview cache")
@click.option("--root-dir", default=None, help="Override preview bundle root directory")
@handle_error
def preview_capture(recipe, force, root_dir):
    """Capture a preview bundle for the active scene."""
    sess = get_session()
    result = preview_mod.capture(
        sess,
        recipe=recipe,
        force=force,
        root_dir=root_dir,
        command=f"cli-anything-blender --project {sess.project_path or ''} preview capture --recipe {recipe}".strip(),
    )
    bundle_dir = result.get("_bundle_dir", result.get("bundle_dir", ""))
    status = (
        "Reused preview bundle" if result.get("cached") else "Created preview bundle"
    )
    output(result, f"{status}: {bundle_dir}")


@preview_group.command("latest")
@click.option("--recipe", default=None, help="Filter by recipe name")
@click.option("--root-dir", default=None, help="Override preview bundle root directory")
@handle_error
def preview_latest(recipe, root_dir):
    """Show the latest preview bundle manifest."""
    sess = get_session()
    result = preview_mod.latest(
        project_path=sess.project_path, recipe=recipe, root_dir=root_dir
    )
    output(result, f"Latest preview bundle: {result.get('_bundle_dir', '')}")


@preview_live_group.command("start")
@click.option("--recipe", default="quick", help="Preview recipe name")
@click.option("--force", is_flag=True, help="Bypass preview cache")
@click.option("--root-dir", default=None, help="Override preview root directory")
@click.option(
    "--poll-ms",
    default=1500,
    show_default=True,
    help="Suggested viewer polling interval",
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
    recipe, force, root_dir, poll_ms, mode, source_poll_ms, open_window
):
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
            f"cli-anything-blender --project {sess.project_path or ''} "
            f"preview live start --recipe {recipe}"
        ).strip(),
    )
    if result.get("live_mode") == "poll" and not result.get("poller", {}).get(
        "running"
    ):
        result["poller"] = _spawn_live_poller(result["_session_dir"])
    if open_window:
        result["viewer"] = _spawn_live_viewer(result["_session_dir"], poll_ms)
    output(result, f"Started live preview session: {result.get('_session_dir', '')}")
