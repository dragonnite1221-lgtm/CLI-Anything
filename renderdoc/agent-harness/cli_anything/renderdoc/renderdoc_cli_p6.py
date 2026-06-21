# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403

# fmt: off
from .renderdoc_cli_p1 import _get_handle, _output, cli  # noqa: E402,E501
from .renderdoc_cli_p4 import pipeline_group  # noqa: E402,E501
# fmt: on


@pipeline_group.command("cbuffer")
@click.argument("event_id", type=int)
@click.option("--stage", default="Fragment", help="Shader stage.")
@click.option("--index", "cbuffer_index", default=0, type=int, help="CBuffer index.")
@click.pass_context
def pipeline_cbuffer(ctx, event_id, stage, cbuffer_index):
    """Get constant buffer contents at a specific event."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.pipeline import get_cbuffer_contents

    data = get_cbuffer_contents(handle.controller, event_id, stage, cbuffer_index)
    _output(ctx, data)


@cli.group("resources")
def resources_group():
    """Resource (buffer/texture) listing and data reading."""
    pass


@resources_group.command("list")
@click.pass_context
def resources_list(ctx):
    """List all resources in the capture."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.resources import list_resources

    data = list_resources(handle.controller)

    def _human(resources):
        click.echo(f"Total resources: {len(resources)}")
        for r in resources:
            click.echo(f"  [{r['resourceId']}] {r['type']}: {r['name']}")

    _output(ctx, data, _human)


@resources_group.command("buffers")
@click.pass_context
def resources_buffers(ctx):
    """List all buffer resources."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.resources import list_buffers

    data = list_buffers(handle.controller)
    _output(ctx, data)


@resources_group.command("read-buffer")
@click.argument("resource_id")
@click.option("--offset", default=0, type=int, help="Byte offset.")
@click.option("--length", default=256, type=int, help="Number of bytes to read.")
@click.option(
    "--format", "fmt", default="hex", help="Output format: hex, float32, uint32, raw."
)
@click.pass_context
def resources_read_buffer(ctx, resource_id, offset, length, fmt):
    """Read raw buffer data."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.resources import get_buffer_data

    data = get_buffer_data(handle.controller, resource_id, offset, length, fmt)
    _output(ctx, data)


@cli.group("mesh")
def mesh_group():
    """Mesh data (vertex inputs/outputs) inspection."""
    pass


@mesh_group.command("inputs")
@click.argument("event_id", type=int)
@click.option("--max-vertices", default=100, type=int, help="Max vertices to decode.")
@click.pass_context
def mesh_inputs(ctx, event_id, max_vertices):
    """Get vertex shader inputs at a draw call."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.mesh import get_mesh_inputs

    data = get_mesh_inputs(handle.controller, event_id, max_vertices)
    _output(ctx, data)


@mesh_group.command("outputs")
@click.argument("event_id", type=int)
@click.option("--max-vertices", default=100, type=int, help="Max vertices to decode.")
@click.pass_context
def mesh_outputs(ctx, event_id, max_vertices):
    """Get post-vertex-shader outputs at a draw call."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.mesh import get_mesh_outputs

    data = get_mesh_outputs(handle.controller, event_id, max_vertices)
    _output(ctx, data)


@cli.group("counters")
def counters_group():
    """GPU performance counters."""
    pass


@counters_group.command("list")
@click.pass_context
def counters_list(ctx):
    """List all available GPU counters."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.counters import list_counters

    data = list_counters(handle.controller)

    def _human(counters):
        click.echo(f"Available GPU counters: {len(counters)}")
        for c in counters:
            click.echo(f"  [{c['counter']}] {c['name']}: {c['description']}")

    _output(ctx, data, _human)
