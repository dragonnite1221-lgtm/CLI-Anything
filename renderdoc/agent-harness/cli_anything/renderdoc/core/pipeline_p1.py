# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403


def _write_json(path: str, data: Any) -> None:
    """Write data as pretty-printed JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def get_depth_stencil_state(pipe) -> Optional[Dict[str, Any]]:
    """Extract depth-stencil state from a PipeState object."""
    try:
        d3d11 = getattr(pipe, "GetD3D11PipelineState", None)
        d3d12 = getattr(pipe, "GetD3D12PipelineState", None)
        gl = getattr(pipe, "GetGLPipelineState", None)
        vk = getattr(pipe, "GetVulkanPipelineState", None)

        def _stencil_face(s):
            return {
                "failOp": str(s.failOperation),
                "depthFailOp": str(s.depthFailOperation),
                "passOp": str(s.passOperation),
                "function": str(s.function),
            }

        if d3d11:
            ps = d3d11()
            ds = ps.outputMerger.depthStencilState
            return {
                "depthEnable": ds.depthEnable,
                "depthFunction": str(ds.depthFunction),
                "depthWrites": ds.depthWrites,
                "stencilEnable": ds.stencilEnable,
                "frontFace": _stencil_face(ds.frontFace),
                "backFace": _stencil_face(ds.backFace),
            }
        if d3d12:
            ps = d3d12()
            ds = ps.outputMerger.depthStencilState
            return {
                "depthEnable": ds.depthEnable,
                "depthFunction": str(ds.depthFunction),
                "depthWrites": ds.depthWrites,
                "stencilEnable": ds.stencilEnable,
                "frontFace": _stencil_face(ds.frontFace),
                "backFace": _stencil_face(ds.backFace),
            }
        if gl:
            ps = gl()
            ds = ps.depthState
            st = ps.stencilState
            return {
                "depthEnable": ds.depthEnable,
                "depthFunction": str(ds.depthFunction),
                "depthWrites": ds.depthWrites,
                "stencilEnable": st.stencilEnable,
                "frontFace": _stencil_face(st.frontFace),
                "backFace": _stencil_face(st.backFace),
            }
        if vk:
            ps = vk()
            ds = ps.depthStencil
            return {
                "depthTestEnable": ds.depthTestEnable,
                "depthWriteEnable": ds.depthWriteEnable,
                "depthFunction": str(ds.depthFunction),
                "depthBoundsEnable": ds.depthBoundsEnable,
                "stencilTestEnable": ds.stencilTestEnable,
                "frontFace": _stencil_face(ds.frontFace),
                "backFace": _stencil_face(ds.backFace),
            }
    except Exception as e:
        click.echo(f"Warning: {e}", err=True)
    return None
