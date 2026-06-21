# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403

# fmt: off
from .renderdoc_cli_p1 import _close_all_captures, _get_handle, _output, cli  # noqa: E402,E501
from .renderdoc_cli_p7 import _get_handle_b  # noqa: E402,E501
from .renderdoc_cli_p8 import preview_group  # noqa: E402,E501
# fmt: on


@preview_group.command("capture")
@click.option("--recipe", default="quick", help="Preview recipe name.")
@click.option("--event-id", type=int, default=None, help="Specific event to inspect.")
@click.option("--force", is_flag=True, help="Bypass preview cache.")
@click.option(
    "--root-dir", default=None, help="Override preview bundle root directory."
)
@click.pass_context
def preview_capture_cmd(ctx, recipe, event_id, force, root_dir):
    """Capture a preview bundle for the active RenderDoc capture."""
    from cli_anything.renderdoc.core.preview import capture

    handle = _get_handle(ctx)
    capture_path = ctx.obj.get("capture_path")
    result = capture(
        handle,
        capture_path,
        recipe=recipe,
        event_id=event_id,
        force=force,
        root_dir=root_dir,
        command=f"cli-anything-renderdoc -c {capture_path} preview capture --recipe {recipe}",
    )
    _output(ctx, result)


@preview_group.command("diff")
@click.argument("event_a", type=int)
@click.argument("event_b", type=int)
@click.option(
    "--capture-b",
    "-b",
    type=click.Path(exists=False),
    default=None,
    help="Path to second .rdc capture (default: same as --capture).",
)
@click.option("--compact/--no-compact", default=True, help="Prune identical sections.")
@click.option("--force", is_flag=True, help="Bypass preview cache.")
@click.option(
    "--root-dir", default=None, help="Override preview bundle root directory."
)
@click.pass_context
def preview_diff_cmd(ctx, event_a, event_b, capture_b, compact, force, root_dir):
    """Capture a diff preview bundle for two RenderDoc events."""
    from cli_anything.renderdoc.core.preview import diff

    handle_a = _get_handle(ctx)
    capture_path_a = ctx.obj.get("capture_path")
    if capture_b:
        handle_b = _get_handle_b(ctx, capture_b)
        capture_path_b = capture_b
    else:
        handle_b = handle_a
        capture_path_b = capture_path_a

    result = diff(
        handle_a,
        capture_path_a,
        event_a,
        handle_b,
        capture_path_b,
        event_b,
        compact=compact,
        force=force,
        root_dir=root_dir,
        command=(
            f"cli-anything-renderdoc -c {capture_path_a} preview diff {event_a} {event_b}"
            + (f" --capture-b {capture_path_b}" if capture_b else "")
        ),
    )
    _output(ctx, result)


@preview_group.command("latest")
@click.option("--recipe", default=None, help="Filter by recipe name.")
@click.option(
    "--kind", "bundle_kind", type=click.Choice(["capture", "diff"]), default=None
)
@click.option(
    "--root-dir", default=None, help="Override preview bundle root directory."
)
@click.pass_context
def preview_latest_cmd(ctx, recipe, bundle_kind, root_dir):
    """Show the latest preview bundle manifest."""
    from cli_anything.renderdoc.core.preview import latest

    result = latest(
        project_path=ctx.obj.get("capture_path"),
        recipe=recipe,
        bundle_kind=bundle_kind,
        root_dir=root_dir,
    )
    _output(ctx, result)


@cli.result_callback()
@click.pass_context
def cleanup(ctx, *args, **kwargs):
    global _repl_mode
    # REPL invokes cli.main() per line; keep captures open until repl() exits.
    if _repl_mode:
        return
    _close_all_captures()


def main():
    cli(obj={})
