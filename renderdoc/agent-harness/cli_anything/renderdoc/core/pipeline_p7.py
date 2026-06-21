# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403

# fmt: off
from .pipeline_p3 import _pso_for_stage, _resolve_stage  # noqa: E402,E501
from .pipeline_p6 import _runtime_var_to_dict  # noqa: E402,E501
# fmt: on


def get_cbuffer_contents(
    controller,
    event_id: int,
    stage_name: str = "Fragment",
    cbuffer_index: int = 0,
) -> Dict[str, Any]:
    """Get constant buffer variable contents at a specific event."""
    stage = _resolve_stage(stage_name)
    if stage is None:
        return {"error": f"Unknown stage: {stage_name}"}

    controller.SetFrameEvent(event_id, True)
    pipe = controller.GetPipelineState()
    refl = pipe.GetShaderReflection(stage)
    if refl is None:
        return {"error": f"No shader bound at stage {stage_name}"}

    if cbuffer_index >= len(refl.constantBlocks):
        return {
            "error": f"CBuffer index {cbuffer_index} out of range (max {len(refl.constantBlocks) - 1})"
        }

    pso = _pso_for_stage(pipe, stage)
    entry = pipe.GetShaderEntryPoint(stage)
    cb = pipe.GetConstantBlock(stage, cbuffer_index, 0)

    variables = controller.GetCBufferVariableContents(
        pso, refl.resourceId, stage, entry, cbuffer_index, cb.descriptor.resource, 0, 0
    )

    return {
        "eventId": event_id,
        "stage": stage_name,
        "cbuffer_index": cbuffer_index,
        "variables": [_runtime_var_to_dict(v) for v in variables],
    }


def _serialize_sig(sig) -> Dict[str, Any]:
    """Serialize a SigParameter to dict."""
    return {
        "varName": str(sig.varName),
        "semanticName": str(sig.semanticName),
        "semanticIndex": sig.semanticIndex,
        "regIndex": sig.regIndex,
        "systemValue": str(sig.systemValue),
        "varType": str(sig.varType),
        "compCount": sig.compCount,
    }


def _serialize_shader_type(t) -> Dict[str, Any]:
    """Serialize a ShaderVariableType to dict."""
    result = {}
    for attr in (
        "name",
        "rows",
        "columns",
        "elements",
        "arrayByteStride",
        "matrixByteStride",
        "pointerTypeID",
        "baseType",
    ):
        if hasattr(t, attr):
            val = getattr(t, attr)
            result[attr] = str(val) if not isinstance(val, (int, float, bool)) else val
    if hasattr(t, "members") and t.members:
        result["members"] = [_serialize_cbuffer_var(m) for m in t.members]
    return result


def _serialize_cbuffer_var(v) -> Dict[str, Any]:
    """Serialize a ShaderConstant (cbuffer variable) to dict."""
    d = {
        "name": str(v.name),
        "byteOffset": v.byteOffset,
    }
    if hasattr(v, "type"):
        d["type"] = _serialize_shader_type(v.type)
    if hasattr(v, "defaultValue"):
        d["defaultValue"] = v.defaultValue
    return d
