# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403

# fmt: off
from .pipeline_p3 import _resolve_stage  # noqa: E402,E501
from .pipeline_p4 import _get_encoding_info, _get_encoding_str  # noqa: E402,E501
# fmt: on


def save_shader_raw(
    controller,
    event_id: int,
    stage_name: str = "Fragment",
    output_path: Optional[str] = None,
    default_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Save raw shader bytes to file, identical to RenderDoc UI Save.

    Parameters
    ----------
    default_dir : str or None
        Directory for auto-generated filename when output_path is None.
        If None, uses current working directory.
    """
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
    if not raw:
        return {"error": "Shader has no rawBytes data"}

    if output_path is None:
        rid_str = str(refl.resourceId).replace("::", "_")
        fname = "shader_%s_%s_eid%d%s" % (
            rid_str,
            stage_name,
            event_id,
            enc_info["file_ext"],
        )
        if default_dir:
            output_path = os.path.join(default_dir, fname)
        else:
            output_path = fname

    mode = "w" if enc_info["is_text"] else "wb"
    with open(
        output_path, mode, encoding="utf-8" if enc_info["is_text"] else None
    ) as f:
        if enc_info["is_text"]:
            f.write(raw.decode("utf-8", errors="replace"))
        else:
            f.write(raw)

    # Query available disassembly targets from RenderDoc runtime
    disasm_targets = []
    try:
        targets = controller.GetDisassemblyTargets(True)
        disasm_targets = [str(t) for t in targets]
    except Exception as e:
        click.echo(f"Warning: {e}", err=True)

    return {
        "eventId": event_id,
        "stage": stage_name,
        "resourceId": str(refl.resourceId),
        "encoding": enc_info["format"],
        "encoding_description": enc_info["description"],
        "is_text": enc_info["is_text"],
        "size_bytes": len(raw),
        "output_path": os.path.abspath(output_path),
        "disasm_targets": disasm_targets,
    }
