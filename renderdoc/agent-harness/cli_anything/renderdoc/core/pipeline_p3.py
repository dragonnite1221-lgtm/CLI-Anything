# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403

# fmt: off
from .pipeline_p1 import get_depth_stencil_state  # noqa: E402,E501
from .pipeline_p2 import get_blend_state, get_rasterizer_state  # noqa: E402,E501
# fmt: on


def get_pipeline_state(controller, event_id: int) -> Dict[str, Any]:
    """Return a comprehensive pipeline state dict at the given event."""
    controller.SetFrameEvent(event_id, True)
    pipe = controller.GetPipelineState()

    result: Dict[str, Any] = {
        "eventId": event_id,
        "pipeline_type": str(controller.GetAPIProperties().pipelineType),
    }

    # Shader stages
    stages = [
        ("Vertex", rd.ShaderStage.Vertex),
        ("TessControl", rd.ShaderStage.Tess_Control),
        ("TessEval", rd.ShaderStage.Tess_Eval),
        ("Geometry", rd.ShaderStage.Geometry),
        ("Fragment", rd.ShaderStage.Fragment),
        ("Compute", rd.ShaderStage.Compute),
    ]
    shaders = {}
    for name, stage in stages:
        refl = pipe.GetShaderReflection(stage)
        if refl is not None:
            shaders[name] = {
                "bound": True,
                "resourceId": str(refl.resourceId),
                "entryPoint": str(refl.entryPoint),
                "debugInfo": str(refl.debugInfo.debuggable)
                if refl.debugInfo
                else "N/A",
                "numInputs": len(refl.inputSignature),
                "numOutputs": len(refl.outputSignature),
                "numCBuffers": len(refl.constantBlocks),
                "numReadOnly": len(refl.readOnlyResources),
                "numReadWrite": len(refl.readWriteResources),
            }
        else:
            shaders[name] = {"bound": False}
    result["shaders"] = shaders

    # Vertex inputs
    try:
        vinputs = pipe.GetVertexInputs()
        result["vertexInputs"] = [
            {
                "name": str(v.name),
                "vertexBuffer": v.vertexBuffer,
                "byteOffset": v.byteOffset,
                "perInstance": v.perInstance,
                "instanceRate": v.instanceRate,
                "format": str(v.format),
            }
            for v in vinputs
        ]
    except Exception as e:
        click.echo(f"Warning: failed to get vertexInputs: {e}", err=True)
        result["vertexInputs"] = []

    # Render targets
    try:
        targets = pipe.GetOutputTargets()
        result["renderTargets"] = [
            {"resourceId": str(t.resourceId), "index": i}
            for i, t in enumerate(targets)
            if t.resourceId != rd.ResourceId.Null()
        ]
    except Exception as e:
        click.echo(f"Warning: failed to get renderTargets: {e}", err=True)
        result["renderTargets"] = []

    # Depth target
    try:
        depth = pipe.GetDepthTarget()
        if depth.resourceId != rd.ResourceId.Null():
            result["depthTarget"] = {"resourceId": str(depth.resourceId)}
        else:
            result["depthTarget"] = None
    except Exception as e:
        click.echo(f"Warning: failed to get depthTarget: {e}", err=True)
        result["depthTarget"] = None

    # Viewports
    try:
        vp = pipe.GetViewport(0)
        result["viewport"] = {
            "x": vp.x,
            "y": vp.y,
            "width": vp.width,
            "height": vp.height,
            "minDepth": vp.minDepth,
            "maxDepth": vp.maxDepth,
        }
    except Exception as e:
        click.echo(f"Warning: failed to get viewport: {e}", err=True)
        result["viewport"] = None

    # Rasterizer state
    result["rasterizer"] = get_rasterizer_state(pipe)

    # Blend state
    result["blend"] = get_blend_state(pipe)

    # Depth-stencil state
    result["depthStencil"] = get_depth_stencil_state(pipe)

    return result


STAGE_MAP = {
    "vertex": rd.ShaderStage.Vertex if HAS_RD else None,
    "tesscontrol": rd.ShaderStage.Tess_Control if HAS_RD else None,
    "tesseval": rd.ShaderStage.Tess_Eval if HAS_RD else None,
    "geometry": rd.ShaderStage.Geometry if HAS_RD else None,
    "fragment": rd.ShaderStage.Fragment if HAS_RD else None,
    "pixel": rd.ShaderStage.Fragment if HAS_RD else None,
    "compute": rd.ShaderStage.Compute if HAS_RD else None,
}
STAGE_PAIRS = [
    ("Vertex", "vertex"),
    ("TessControl", "tesscontrol"),
    ("TessEval", "tesseval"),
    ("Geometry", "geometry"),
    ("Fragment", "fragment"),
    ("Compute", "compute"),
]


def _resolve_stage(stage_name: str):
    """Resolve a stage name string to rd.ShaderStage enum, or None."""
    return STAGE_MAP.get(stage_name.lower())


def _pso_for_stage(pipe, stage):
    """PSO handle for DisassembleShader / GetCBufferVariableContents (compute vs graphics)."""
    if HAS_RD and stage == rd.ShaderStage.Compute:
        return pipe.GetComputePipelineObject()
    return pipe.GetGraphicsPipelineObject()
