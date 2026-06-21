# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403

# fmt: off
from .pipeline_p1 import get_depth_stencil_state  # noqa: E402,E501
from .pipeline_p2 import get_blend_state, get_rasterizer_state  # noqa: E402,E501
from .pipeline_p3 import _pso_for_stage  # noqa: E402,E501
from .pipeline_p8 import dump_shader_reflection  # noqa: E402,E501
from .pipeline_p9 import dump_stage_bindings  # noqa: E402,E501
# fmt: on


def dump_pipeline(controller, event_id: int) -> Dict[str, Any]:
    """Dump the complete pipeline state and shader reflections at an event.

    Produces a JSON-serializable dict with:
    - PipelineState: vertex inputs, render targets, viewport, rasterizer,
      blend, depth/stencil
    - For each bound shader stage: ShaderReflection + runtime bindings

    This is intended for human debugging, not for AI consumption.
    """
    controller.SetFrameEvent(event_id, True)
    pipe = controller.GetPipelineState()

    pipeline_type = str(controller.GetAPIProperties().pipelineType)

    ps = {
        "pipelineType": pipeline_type,
    }

    # Vertex inputs
    try:
        vinputs = pipe.GetVertexInputs()
        ps["vertexInputs"] = [
            {
                "name": str(v.name),
                "vertexBuffer": v.vertexBuffer,
                "byteOffset": v.byteOffset,
                "perInstance": v.perInstance,
                "instanceRate": v.instanceRate,
                "format": v.format.Name()
                if hasattr(v.format, "Name")
                else str(v.format),
            }
            for v in vinputs
        ]
    except Exception as e:
        click.echo(f"Warning: failed to get vertexInputs: {e}", err=True)
        ps["vertexInputs"] = []

    # Output targets
    try:
        targets = pipe.GetOutputTargets()
        ps["outputTargets"] = [
            {"resourceId": str(t.resourceId), "index": i}
            for i, t in enumerate(targets)
            if t.resourceId != rd.ResourceId.Null()
        ]
    except Exception as e:
        click.echo(f"Warning: failed to get outputTargets: {e}", err=True)
        ps["outputTargets"] = []

    # Depth target
    try:
        depth = pipe.GetDepthTarget()
        if depth.resourceId != rd.ResourceId.Null():
            ps["depthTarget"] = {"resourceId": str(depth.resourceId)}
        else:
            ps["depthTarget"] = None
    except Exception as e:
        click.echo(f"Warning: failed to get depthTarget: {e}", err=True)
        ps["depthTarget"] = None

    # Viewport
    try:
        vp = pipe.GetViewport(0)
        ps["viewport"] = {
            "x": vp.x,
            "y": vp.y,
            "width": vp.width,
            "height": vp.height,
            "minDepth": vp.minDepth,
            "maxDepth": vp.maxDepth,
        }
    except Exception as e:
        click.echo(f"Warning: failed to get viewport: {e}", err=True)
        ps["viewport"] = None

    # State blocks — use new unified PipeState API
    # Blend state
    try:
        color_blends = pipe.GetColorBlends()

        def _blend_eq(b):
            return {
                "enabled": b.enabled,
                "colorBlendSrc": str(b.colorBlend.source),
                "colorBlendDst": str(b.colorBlend.destination),
                "colorBlendOp": str(b.colorBlend.operation),
                "alphaBlendSrc": str(b.alphaBlend.source),
                "alphaBlendDst": str(b.alphaBlend.destination),
                "alphaBlendOp": str(b.alphaBlend.operation),
                "writeMask": int(b.writeMask),
                "logicOperationEnabled": b.logicOperationEnabled,
                "logicOperation": str(b.logicOperation),
            }

        ps["blend"] = {
            "independentBlend": pipe.IsIndependentBlendingEnabled(),
            "blends": [dict(_blend_eq(b), index=i) for i, b in enumerate(color_blends)],
        }
    except Exception as e:
        click.echo(f"Warning: failed to get blend: {e}", err=True)
        ps["blend"] = get_blend_state(pipe)

    # Depth-stencil state
    try:
        stencil_faces = pipe.GetStencilFaces()

        def _stencil_face(s):
            return {
                "failOp": str(s.failOperation),
                "depthFailOp": str(s.depthFailOperation),
                "passOp": str(s.passOperation),
                "function": str(s.function),
                "reference": s.reference,
                "compareMask": s.compareMask,
                "writeMask": s.writeMask,
            }

        ps["depthStencil"] = {
            "frontFace": _stencil_face(stencil_faces[0]),
            "backFace": _stencil_face(stencil_faces[1]),
        }
    except Exception as e:
        click.echo(f"Warning: failed to get depthStencil: {e}", err=True)
        ps["depthStencil"] = get_depth_stencil_state(pipe)

    # Rasterizer state
    try:
        ps["rasterizer"] = {
            "topology": str(pipe.GetPrimitiveTopology()),
        }
        sc = pipe.GetScissor(0)
        ps["rasterizer"]["scissor"] = {
            "enabled": sc.enabled,
            "x": sc.x,
            "y": sc.y,
            "width": sc.width,
            "height": sc.height,
        }
    except Exception as e:
        click.echo(f"Warning: failed to get rasterizer: {e}", err=True)
        ps["rasterizer"] = get_rasterizer_state(pipe)

    # Shader stages
    stages_dict = {}
    stage_defs = [
        ("Vertex", rd.ShaderStage.Vertex),
        ("TessControl", rd.ShaderStage.Tess_Control),
        ("TessEval", rd.ShaderStage.Tess_Eval),
        ("Geometry", rd.ShaderStage.Geometry),
        ("Fragment", rd.ShaderStage.Fragment),
        ("Compute", rd.ShaderStage.Compute),
    ]
    for name, stage_enum in stage_defs:
        refl = pipe.GetShaderReflection(stage_enum)
        if refl is None:
            continue
        pso = _pso_for_stage(pipe, stage_enum)
        stage_data = {
            "shader": str(refl.resourceId),
            "entryPoint": str(refl.entryPoint),
            "ShaderReflection": dump_shader_reflection(refl),
            "bindings": dump_stage_bindings(controller, pipe, pso, stage_enum, refl),
        }
        stages_dict[name] = stage_data
    ps["stages"] = stages_dict

    return {
        "eventId": event_id,
        "PipelineState": ps,
    }
