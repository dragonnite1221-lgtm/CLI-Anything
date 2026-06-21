# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403

# fmt: off
from .pipeline_p3 import _pso_for_stage, _resolve_stage  # noqa: E402,E501
from .pipeline_p4 import _get_encoding_info, _get_encoding_str  # noqa: E402,E501
from .pipeline_p6 import _runtime_var_to_dict  # noqa: E402,E501
from .pipeline_p11 import dump_pipeline  # noqa: E402,E501
# fmt: on


def dump_pipeline_for_diff(controller, event_id: int) -> Dict[str, Any]:
    """Build a complete pipeline snapshot suitable for ``diff_pipeline``.

    Calls :func:`dump_pipeline` for the base structure, then enriches every
    bound stage's ``bindings.constantBlocks[i]`` with a ``variables`` list
    containing runtime CBuffer values (via ``GetCBufferVariableContents``).
    """
    data = dump_pipeline(controller, event_id)
    ps = data.get("PipelineState", {})

    controller.SetFrameEvent(event_id, True)
    pipe = controller.GetPipelineState()

    stage_defs = [
        ("Vertex", rd.ShaderStage.Vertex),
        ("TessControl", rd.ShaderStage.Tess_Control),
        ("TessEval", rd.ShaderStage.Tess_Eval),
        ("Geometry", rd.ShaderStage.Geometry),
        ("Fragment", rd.ShaderStage.Fragment),
        ("Compute", rd.ShaderStage.Compute),
    ]

    for name, stage_enum in stage_defs:
        stage_data = ps.get("stages", {}).get(name)
        if stage_data is None:
            continue
        refl = pipe.GetShaderReflection(stage_enum)
        if refl is None:
            continue
        pso = _pso_for_stage(pipe, stage_enum)
        entry = pipe.GetShaderEntryPoint(stage_enum)
        cb_bindings = stage_data.get("bindings", {}).get("constantBlocks", [])
        for cb_entry in cb_bindings:
            idx = cb_entry.get("index")
            if idx is None or "error" in cb_entry:
                continue
            try:
                cb = pipe.GetConstantBlock(stage_enum, idx, 0)
                variables = controller.GetCBufferVariableContents(
                    pso,
                    refl.resourceId,
                    stage_enum,
                    entry,
                    idx,
                    cb.descriptor.resource,
                    0,
                    0,
                )
                cb_entry["variables"] = [_runtime_var_to_dict(v) for v in variables]
            except Exception as e:
                click.echo(f"Warning: failed to get variables: {e}", err=True)
                cb_entry["variables"] = []

    return data


def get_shader_raw(
    controller,
    event_id: int,
    stage_name: str = "Fragment",
) -> Dict[str, Any]:
    """Get raw shader encoding info. For text shaders includes source."""
    stage = _resolve_stage(stage_name)
    if stage is None:
        return {"error": "Unknown stage: %s" % stage_name}

    controller.SetFrameEvent(event_id, True)
    pipe = controller.GetPipelineState()
    refl = pipe.GetShaderReflection(stage)
    if refl is None:
        return {
            "error": "No shader bound at stage %s for event %d" % (stage_name, event_id)
        }

    enc_str = _get_encoding_str(refl)
    enc_info = _get_encoding_info(enc_str)
    raw = bytes(refl.rawBytes) if refl.rawBytes else b""

    result = {
        "encoding": enc_info["format"],
        "is_text": enc_info["is_text"],
        "size_bytes": len(raw),
    }
    if enc_info["is_text"] and raw:
        result["source"] = raw.decode("utf-8", errors="replace")

    return result
