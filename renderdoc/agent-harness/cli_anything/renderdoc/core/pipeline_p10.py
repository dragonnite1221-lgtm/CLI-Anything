# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403

# fmt: off
from .pipeline_p1 import _write_json  # noqa: E402,E501
from .pipeline_p3 import _pso_for_stage, _resolve_stage  # noqa: E402,E501
from .pipeline_p4 import _get_encoding_info, _get_encoding_str  # noqa: E402,E501
from .pipeline_p6 import _runtime_var_to_dict  # noqa: E402,E501
from .pipeline_p8 import dump_shader_reflection  # noqa: E402,E501
from .pipeline_p9 import dump_stage_bindings  # noqa: E402,E501
# fmt: on


def export_shader_reflection(
    controller,
    event_id: int,
    stage_name: str = "Fragment",
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Export complete ShaderReflection for a shader stage to a folder.

    Creates:
      <output_dir>/
        reflection.json        — full ShaderReflection (with debugInfo file contents)
        bindings.json          — runtime GPU bindings (bound resources, cbuffers, samplers)
        cbuffer_values.json    — runtime constant buffer variable values
        sources/               — individual debug source files (if available)
          <filename>

    Returns a summary dict with paths and metadata.
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

    pso = _pso_for_stage(pipe, stage)
    entry = pipe.GetShaderEntryPoint(stage)

    # Build output directory
    if output_dir is None:
        rid_str = str(refl.resourceId).replace("::", "_")
        output_dir = "shader_%s_%s_eid%d_reflection" % (rid_str, stage_name, event_id)
    os.makedirs(output_dir, exist_ok=True)

    files_written = []

    # 1. reflection.json — full ShaderReflection including source contents
    refl_data = dump_shader_reflection(refl, include_file_contents=True)
    refl_path = os.path.join(output_dir, "reflection.json")
    _write_json(refl_path, refl_data)
    files_written.append("reflection.json")

    # 2. bindings.json — runtime GPU bindings
    bindings_data = dump_stage_bindings(controller, pipe, pso, stage, refl)
    bindings_path = os.path.join(output_dir, "bindings.json")
    _write_json(bindings_path, bindings_data)
    files_written.append("bindings.json")

    # 3. cbuffer_values.json — runtime constant buffer variable values
    cbuffer_values = []
    for idx in range(len(refl.constantBlocks)):
        cb_block = refl.constantBlocks[idx]
        entry_dict: Dict[str, Any] = {
            "index": idx,
            "name": str(cb_block.name),
        }
        try:
            cb = pipe.GetConstantBlock(stage, idx, 0)
            variables = controller.GetCBufferVariableContents(
                pso,
                refl.resourceId,
                stage,
                entry,
                idx,
                cb.descriptor.resource,
                0,
                0,
            )
            entry_dict["variables"] = [_runtime_var_to_dict(v) for v in variables]
        except Exception as e:
            entry_dict["variables"] = []
            entry_dict["error"] = str(e)
        cbuffer_values.append(entry_dict)
    cbuf_path = os.path.join(output_dir, "cbuffer_values.json")
    _write_json(cbuf_path, cbuffer_values)
    files_written.append("cbuffer_values.json")

    # 4. sources/ — individual debug source files
    source_files = []
    if refl.debugInfo and refl.debugInfo.files:
        sources_dir = os.path.join(output_dir, "sources")
        os.makedirs(sources_dir, exist_ok=True)
        for f in refl.debugInfo.files:
            fname = str(f.filename)
            contents = str(f.contents)
            if not contents:
                continue
            safe_name = fname.replace("\\", "/").replace("/", "_").replace(":", "_")
            if not safe_name:
                safe_name = "unnamed_source"
            src_path = os.path.join(sources_dir, safe_name)
            with open(src_path, "w", encoding="utf-8") as fh:
                fh.write(contents)
            source_files.append(
                {
                    "original_path": fname,
                    "saved_as": safe_name,
                    "size": len(contents),
                }
            )
            files_written.append("sources/%s" % safe_name)

    # 5. raw shader bytes
    raw = bytes(refl.rawBytes) if refl.rawBytes else b""
    if raw:
        enc_str = _get_encoding_str(refl)
        enc_info = _get_encoding_info(enc_str)
        raw_ext = enc_info.get("file_ext", ".bin")
        raw_name = "shader_raw%s" % raw_ext
        raw_path = os.path.join(output_dir, raw_name)
        mode = "w" if enc_info["is_text"] else "wb"
        with open(
            raw_path, mode, encoding="utf-8" if enc_info["is_text"] else None
        ) as fh:
            if enc_info["is_text"]:
                fh.write(raw.decode("utf-8", errors="replace"))
            else:
                fh.write(raw)
        files_written.append(raw_name)

    return {
        "eventId": event_id,
        "stage": stage_name,
        "resourceId": str(refl.resourceId),
        "entryPoint": str(refl.entryPoint),
        "encoding": _get_encoding_str(refl),
        "output_dir": os.path.abspath(output_dir),
        "files": files_written,
        "source_files": source_files,
        "constantBlocks_count": len(refl.constantBlocks),
        "readOnlyResources_count": len(refl.readOnlyResources),
        "readWriteResources_count": len(refl.readWriteResources),
        "samplers_count": len(refl.samplers),
    }
