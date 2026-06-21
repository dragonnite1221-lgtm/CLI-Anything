# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403

# fmt: off
from .pipeline_p3 import _resolve_stage  # noqa: E402,E501
from .pipeline_p4 import _get_encoding_info, _get_encoding_str, get_shader_disasm  # noqa: E402,E501
from .pipeline_p5 import _extract_debug_source  # noqa: E402,E501
# fmt: on


def export_shader(
    controller,
    event_id: int,
    stage_name: str = "Fragment",
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Export a shader in human-readable form, plus the raw binary.

    Saves two files into *output_dir*:

    1. **Raw shader** — the original bytes (e.g. ``.dxbc``, ``.glsl``)
    2. **Readable shader** (only if raw is binary) — tried in order:
       a. Embedded debug source (HLSL/GLSL compiled with ``/Zi``)
       b. RenderDoc disassembly (bytecode asm)

    For text encodings (GLSL, HLSL, Slang) the raw file *is* the readable
    file, so only one file is produced.

    Returns a summary dict with ``saved_files``, ``readable_path``,
    ``readable_kind`` (``"source"`` | ``"disasm"`` | ``None``).
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

    rid_str = str(refl.resourceId).replace("::", "_")
    if output_dir is None:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    # --- Save raw ---
    raw_ext = enc_info.get("file_ext", ".bin")
    raw_name = "shader_%s_%s_eid%d%s" % (rid_str, stage_name, event_id, raw_ext)
    raw_path = os.path.join(output_dir, raw_name)
    mode = "w" if enc_info["is_text"] else "wb"
    with open(raw_path, mode, encoding="utf-8" if enc_info["is_text"] else None) as f:
        if enc_info["is_text"]:
            f.write(raw.decode("utf-8", errors="replace"))
        else:
            f.write(raw)
    raw_path = os.path.abspath(raw_path)

    saved_files = [raw_path]
    readable_path = None
    readable_kind = None

    if enc_info["is_text"]:
        # Raw is already human-readable
        readable_path = raw_path
        readable_kind = "source"
    else:
        # Binary — try embedded debug source first
        source_text, source_ext = _extract_debug_source(refl, enc_str)

        if source_text:
            src_name = "shader_%s_%s_eid%d%s" % (
                rid_str,
                stage_name,
                event_id,
                source_ext,
            )
            readable_path = os.path.abspath(os.path.join(output_dir, src_name))
            with open(readable_path, "w", encoding="utf-8") as f:
                f.write(source_text)
            readable_kind = "source"
            saved_files.append(readable_path)
        else:
            # Fallback: disassembly
            disasm_data = get_shader_disasm(controller, event_id, stage_name, 0)
            disasm_text = disasm_data.get("disassembly") or ""
            if disasm_text:
                disasm_ext = enc_info.get("disasm_ext", ".asm")
                asm_name = "shader_%s_%s_eid%d%s" % (
                    rid_str,
                    stage_name,
                    event_id,
                    disasm_ext,
                )
                readable_path = os.path.abspath(os.path.join(output_dir, asm_name))
                with open(readable_path, "w", encoding="utf-8") as f:
                    f.write(disasm_text)
                readable_kind = "disasm"
                saved_files.append(readable_path)

    return {
        "eventId": event_id,
        "stage": stage_name,
        "resourceId": str(refl.resourceId),
        "entryPoint": str(refl.entryPoint),
        "encoding": enc_info["format"],
        "encoding_description": enc_info["description"],
        "is_text": enc_info["is_text"],
        "size_bytes": len(raw),
        "raw_path": raw_path,
        "saved_files": saved_files,
        "readable_path": readable_path,
        "readable_kind": readable_kind,
    }


def _runtime_var_to_dict(v) -> Dict[str, Any]:
    """Serialize a runtime CBuffer variable (ShaderVariable) to dict.

    This is the module-level equivalent of the nested ``_var_to_dict``
    formerly duplicated as nested ``_var_to_dict`` in several functions.
    """
    d: Dict[str, Any] = {"name": v.name, "rows": v.rows, "columns": v.columns}
    if len(v.members) == 0:
        vals = []
        for r in range(v.rows):
            for c in range(v.columns):
                vals.append(v.value.f32v[r * v.columns + c])
        d["values"] = vals
    else:
        d["members"] = [_runtime_var_to_dict(m) for m in v.members]
    return d
