# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403

# fmt: off
from .renderdoc_cli_p1 import _get_export_dir, _get_handle, _output, cli  # noqa: E402,E501
from .renderdoc_cli_p3 import textures_group  # noqa: E402,E501
# fmt: on


@textures_group.command("save-outputs")
@click.argument("event_id", type=int)
@click.option(
    "--output-dir", "-o", required=True, type=click.Path(), help="Output directory."
)
@click.option("--format", "fmt", default="png", help="Image format.")
@click.pass_context
def textures_save_outputs(ctx, event_id, output_dir, fmt):
    """Save all render target outputs at a specific event."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.textures import save_action_outputs

    data = save_action_outputs(handle.controller, event_id, output_dir, fmt)
    _output(ctx, data)


@textures_group.command("pick")
@click.argument("resource_id")
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.option("--mip", default=0, type=int)
@click.option("--slice", "slice_idx", default=0, type=int)
@click.pass_context
def textures_pick(ctx, resource_id, x, y, mip, slice_idx):
    """Pick a pixel value from a texture."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.textures import pick_pixel

    data = pick_pixel(handle.controller, resource_id, x, y, mip, slice_idx)
    _output(ctx, data)


@cli.group("pipeline")
def pipeline_group():
    """Pipeline state inspection."""
    pass


@pipeline_group.command("state")
@click.argument("event_id", type=int)
@click.pass_context
def pipeline_state(ctx, event_id):
    """Show full pipeline state at a specific event."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.pipeline import get_pipeline_state

    data = get_pipeline_state(handle.controller, event_id)
    _output(ctx, data)


@pipeline_group.command("shader-export")
@click.argument("event_id", type=int)
@click.option(
    "--stage", default="Fragment", help="Shader stage: Vertex, Fragment, Compute, etc."
)
@click.option(
    "-o",
    "--output",
    "output_dir",
    default=None,
    help="Output directory. Default: <capture>_exported/shaders/",
)
@click.pass_context
def pipeline_shader_export(ctx, event_id, stage, output_dir):
    """Export shader source in human-readable form.

    For text shaders (GLSL, HLSL, Slang) the raw bytes are already
    readable — they are saved directly.

    For binary shaders (DXBC, SPIR-V, DXIL) the tool tries, in order:

    \b
      1. Embedded debug source (HLSL/GLSL compiled with /Zi)
      2. RenderDoc disassembly (bytecode asm)

    The raw binary is always saved alongside for completeness.

    \b
    Default output: <capture>_exported/shaders/
    """
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.pipeline import export_shader

    if output_dir is None:
        output_dir = _get_export_dir(ctx, "shaders")

    data = export_shader(handle.controller, event_id, stage, output_dir=output_dir)

    def _human(d):
        if "error" in d:
            click.echo("Error: %s" % d["error"])
            return
        click.echo("  Encoding:     %s" % d["encoding"])
        click.echo("  Raw:          %s" % d["raw_path"])
        rp = d.get("readable_path")
        if rp and rp != d["raw_path"]:
            label = "Source" if d.get("readable_kind") == "source" else "Disassembly"
            click.echo("  %s:  %s" % (label.ljust(12), rp))

    _output(ctx, data, _human)
