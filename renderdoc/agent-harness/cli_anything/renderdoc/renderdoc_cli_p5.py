# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403

# fmt: off
from .renderdoc_cli_p1 import _get_export_dir, _get_handle, _output  # noqa: E402,E501
from .renderdoc_cli_p4 import pipeline_group  # noqa: E402,E501
# fmt: on


@pipeline_group.command("dump-shader-reflection", hidden=True)
@click.argument("event_id", type=int)
@click.option(
    "--stage", default="Fragment", help="Shader stage: Vertex, Fragment, Compute, etc."
)
@click.option(
    "-o", "--output", "output_dir", default=None, help="Output directory path."
)
@click.pass_context
def pipeline_dump_shader_reflection(ctx, event_id, stage, output_dir):
    """Export complete ShaderReflection for a shader stage to a folder.

    Creates a directory containing:

    \b
      reflection.json      Full ShaderReflection (signatures, cbuffer layouts,
                           resource declarations, debug info with source)
      bindings.json        Runtime GPU bindings (bound resource IDs, offsets)
      cbuffer_values.json  Runtime constant buffer variable values
      shader_raw.*         Raw shader bytes (e.g. .dxbc, .glsl)
      sources/             Debug source files (if compiled with debug info)

    \b
    Default output: <capture>_exported/shaders/<shader>_reflection/
    """
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.pipeline import export_shader_reflection

    if output_dir is None:
        # Build default output_dir under the capture's export directory.
        # We need the resourceId to name the folder, so do a quick probe first.
        import renderdoc as rd
        from cli_anything.renderdoc.core.pipeline import STAGE_MAP

        stage_enum = STAGE_MAP.get(stage.lower())
        if stage_enum is None:
            _output(ctx, {"error": "Unknown stage: %s" % stage})
            return
        handle.controller.SetFrameEvent(event_id, True)
        pipe = handle.controller.GetPipelineState()
        refl = pipe.GetShaderReflection(stage_enum)
        if refl is None:
            _output(
                ctx,
                {
                    "error": "No shader bound at stage %s for event %d"
                    % (stage, event_id)
                },
            )
            return
        rid_str = str(refl.resourceId).replace("::", "_")
        shader_dir = _get_export_dir(ctx, "shaders")
        output_dir = os.path.join(
            shader_dir,
            "shader_%s_%s_eid%d_reflection" % (rid_str, stage, event_id),
        )

    data = export_shader_reflection(
        handle.controller,
        event_id,
        stage,
        output_dir=output_dir,
    )

    def _human(d):
        if "error" in d:
            click.echo("Error: %s" % d["error"])
            return
        click.echo("Exported: %s" % d["output_dir"])
        click.echo("  Stage:       %s" % d["stage"])
        click.echo("  ResourceId:  %s" % d["resourceId"])
        click.echo("  EntryPoint:  %s" % d["entryPoint"])
        click.echo("  Encoding:    %s" % d["encoding"])
        click.echo("")
        click.echo("  Files:")
        for f in d.get("files", []):
            click.echo("    %s" % f)
        src_files = d.get("source_files", [])
        if src_files:
            click.echo("")
            click.echo("  Debug sources: %d files" % len(src_files))
            for sf in src_files:
                click.echo("    %s (%d bytes)" % (sf["original_path"], sf["size"]))
        click.echo("")
        click.echo(
            "  CBuffers: %d, ReadOnly: %d, ReadWrite: %d, Samplers: %d"
            % (
                d["constantBlocks_count"],
                d["readOnlyResources_count"],
                d["readWriteResources_count"],
                d["samplers_count"],
            )
        )

    _output(ctx, data, _human)


@pipeline_group.command("dump", hidden=True)
@click.argument("event_id", type=int)
@click.option(
    "-o", "--output", "output_path", default=None, help="Output JSON file path."
)
@click.pass_context
def pipeline_dump(ctx, event_id, output_path):
    """Dump full PipelineState + ShaderReflection at EVENT_ID to JSON.

    Exports the complete pipeline state, shader reflection metadata for all
    bound stages, and GPU runtime bindings. Intended for human debugging.

    \b
    Default output: <capture>_exported/pipeline_eid<EID>_dump.json
    """
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.pipeline import dump_pipeline

    data = dump_pipeline(handle.controller, event_id)

    if output_path is None:
        export_dir = _get_export_dir(ctx)
        output_path = os.path.join(export_dir, "pipeline_eid%d_dump.json" % event_id)

    output_path = os.path.abspath(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    if ctx.obj.get("json_mode"):
        _output(ctx, {"path": output_path})
    else:
        click.echo(output_path)
