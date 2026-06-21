# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403

# fmt: off
from .pipeline_p3 import _pso_for_stage, _resolve_stage  # noqa: E402,E501
# fmt: on


def _get_encoding_str(refl) -> str:
    """Extract encoding name string from ShaderReflection."""
    enc = str(refl.encoding)
    if "." in enc:
        enc = enc.split(".")[-1]
    return enc


_ENCODING_INFO = {
    "DXBC": {
        "format": "DXBC",
        "description": "Direct3D 11 bytecode container (binary)",
        "is_text": False,
        "file_ext": ".dxbc",
        "disasm_ext": ".dxbc.asm",
    },
    "DXIL": {
        "format": "DXIL",
        "description": "Direct3D 12 DXIL bytecode (binary)",
        "is_text": False,
        "file_ext": ".dxil",
        "disasm_ext": ".dxil.asm",
    },
    "GLSL": {
        "format": "GLSL",
        "description": "OpenGL/ES GLSL source code (text, already human-readable)",
        "is_text": True,
        "file_ext": ".glsl",
        "disasm_ext": ".glsl",
    },
    "SPIRV": {
        "format": "SPIR-V",
        "description": "Vulkan SPIR-V binary module (binary)",
        "is_text": False,
        "file_ext": ".spv",
        "disasm_ext": ".spv.asm",
    },
    "OpenGLSPIRV": {
        "format": "OpenGL SPIR-V",
        "description": "OpenGL variant of SPIR-V binary (binary)",
        "is_text": False,
        "file_ext": ".spv",
        "disasm_ext": ".spv.asm",
    },
    "HLSL": {
        "format": "HLSL",
        "description": "High Level Shading Language source (text, already human-readable)",
        "is_text": True,
        "file_ext": ".hlsl",
        "disasm_ext": ".hlsl",
    },
    "Slang": {
        "format": "Slang",
        "description": "Slang shader source (text, already human-readable)",
        "is_text": True,
        "file_ext": ".slang",
        "disasm_ext": ".slang",
    },
}


def _get_encoding_info(enc_str: str) -> Dict[str, Any]:
    return _ENCODING_INFO.get(
        enc_str,
        {
            "format": enc_str,
            "description": "Unknown shader encoding",
            "is_text": False,
            "file_ext": ".bin",
            "disasm_ext": ".asm",
        },
    )


def get_shader_disasm(
    controller,
    event_id: int,
    stage_name: str = "Fragment",
    disasm_target_index: int = 0,
) -> Dict[str, Any]:
    """Get only the disassembly text from RenderDoc.

    Returns a lightweight dict with encoding info and the disassembly string,
    without gathering signatures, cbuffer values, or debug source files.
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
    enc_str = _get_encoding_str(refl)
    enc_info = _get_encoding_info(enc_str)
    raw = bytes(refl.rawBytes) if refl.rawBytes else b""

    result = {
        "eventId": event_id,
        "stage": stage_name,
        "resourceId": str(refl.resourceId),
        "entryPoint": str(refl.entryPoint),
        "encoding": enc_info["format"],
        "encoding_description": enc_info["description"],
        "is_text": enc_info["is_text"],
        "disasm_ext": enc_info["disasm_ext"],
        "rawBytes_size": len(raw),
    }

    # Disassembly
    targets = controller.GetDisassemblyTargets(True)
    result["disasmTargets"] = [str(t) for t in targets]
    if targets:
        tidx = min(disasm_target_index, len(targets) - 1)
        disasm = controller.DisassembleShader(pso, refl, targets[tidx])
        result["disasmTarget"] = str(targets[tidx])
        result["disassembly"] = disasm
    else:
        result["disassembly"] = None

    # Fallback: for text encodings, if disasm failed use raw source
    disasm = result.get("disassembly", "")
    if disasm and ("failed" in disasm.lower()[:100] or "error" in disasm.lower()[:200]):
        if enc_info["is_text"] and raw:
            result["disassembly"] = raw.decode("utf-8", errors="replace")
            result["disasmTarget"] = enc_info["format"] + " (raw source fallback)"

    return result
