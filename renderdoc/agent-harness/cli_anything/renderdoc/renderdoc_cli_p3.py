# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403

# fmt: off
from .renderdoc_cli_p1 import _get_handle, _output, cli  # noqa: E402,E501
from .renderdoc_cli_p2 import actions_group  # noqa: E402,E501
# fmt: on


@actions_group.command("list")
@click.option("--flat/--no-flat", default=True, help="Flat list vs root-only.")
@click.option("--draws-only", is_flag=True, help="Only show actual draw calls.")
@click.pass_context
def actions_list(ctx, flat, draws_only):
    """List all actions (draw calls, clears, etc.) in the capture."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.actions import list_actions, get_drawcalls_only

    if draws_only:
        data = get_drawcalls_only(handle.controller)
    else:
        data = list_actions(handle.controller, flat=flat)

    def _human(actions):
        click.echo(f"Total actions: {len(actions)}")
        for a in actions:
            indent = "  " * a.get("depth", 0)
            flags = ",".join(a["flags"]) if a["flags"] else ""
            click.echo(f"{indent}[{a['eventId']:>5}] {a['name']:<50} {flags}")

    _output(ctx, data, _human)


@actions_group.command("summary")
@click.pass_context
def actions_summary(ctx):
    """Show action count summary by type."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.actions import action_summary

    data = action_summary(handle.controller)

    def _human(d):
        click.echo("Action Summary:")
        for k, v in d.items():
            click.echo(f"  {k}: {v}")

    _output(ctx, data, _human)


@actions_group.command("find")
@click.argument("pattern")
@click.pass_context
def actions_find(ctx, pattern):
    """Find actions by name pattern (case-insensitive)."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.actions import find_actions_by_name

    data = find_actions_by_name(handle.controller, pattern)
    _output(ctx, data)


@actions_group.command("get")
@click.argument("event_id", type=int)
@click.pass_context
def actions_get(ctx, event_id):
    """Get details of a single action by eventId."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.actions import find_action_by_event

    data = find_action_by_event(handle.controller, event_id)
    if data is None:
        data = {"error": f"No action found with eventId={event_id}"}
    _output(ctx, data)


@cli.group("textures")
def textures_group():
    """Texture inspection and export."""
    pass


@textures_group.command("list")
@click.pass_context
def textures_list(ctx):
    """List all textures in the capture."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.textures import list_textures

    data = list_textures(handle.controller)

    def _human(textures):
        click.echo(f"Total textures: {len(textures)}")
        for t in textures:
            click.echo(
                f"  [{t['resourceId']}] {t['width']}x{t['height']} "
                f"mips={t['mips']} fmt={t['format']}"
            )

    _output(ctx, data, _human)


@textures_group.command("get")
@click.argument("resource_id")
@click.pass_context
def textures_get(ctx, resource_id):
    """Get details of a single texture by resource ID."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.textures import get_texture

    data = get_texture(handle.controller, resource_id)
    if data is None:
        data = {"error": f"Texture {resource_id} not found"}
    _output(ctx, data)


@textures_group.command("save")
@click.argument("resource_id")
@click.option(
    "--output", "-o", required=True, type=click.Path(), help="Output file path."
)
@click.option(
    "--format",
    "fmt",
    default="png",
    help="Image format: png, jpg, bmp, tga, hdr, exr, dds.",
)
@click.option("--mip", default=0, type=int, help="Mip level (-1 for all, DDS only).")
@click.option(
    "--slice",
    "slice_idx",
    default=0,
    type=int,
    help="Array slice (-1 for all, DDS only).",
)
@click.option(
    "--alpha", default="preserve", help="Alpha: preserve, discard, blend_checkerboard."
)
@click.pass_context
def textures_save(ctx, resource_id, output, fmt, mip, slice_idx, alpha):
    """Save a texture to an image file."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.textures import save_texture

    data = save_texture(
        handle.controller, resource_id, output, fmt, mip, slice_idx, alpha
    )
    _output(ctx, data)
