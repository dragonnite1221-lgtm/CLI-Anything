# ruff: noqa: F403, F405, E501
from .pipeline_base import *  # noqa: F403


def get_rasterizer_state(pipe) -> Optional[Dict[str, Any]]:
    """Extract rasterizer state from a PipeState object."""
    try:
        d3d11 = getattr(pipe, "GetD3D11PipelineState", None)
        d3d12 = getattr(pipe, "GetD3D12PipelineState", None)
        gl = getattr(pipe, "GetGLPipelineState", None)
        vk = getattr(pipe, "GetVulkanPipelineState", None)

        if d3d11:
            ps = d3d11()
            rs = ps.rasterizer.state
            return {
                "fillMode": str(rs.fillMode),
                "cullMode": str(rs.cullMode),
                "frontCCW": rs.frontCCW,
                "depthBias": rs.depthBias,
                "depthBiasClamp": rs.depthBiasClamp,
                "slopeScaledDepthBias": rs.slopeScaledDepthBias,
                "depthClip": rs.depthClip,
                "scissorEnable": rs.scissorEnable,
                "multisampleEnable": rs.multisampleEnable,
                "antialiasedLines": rs.antialiasedLines,
            }
        if d3d12:
            ps = d3d12()
            rs = ps.rasterizer.state
            return {
                "fillMode": str(rs.fillMode),
                "cullMode": str(rs.cullMode),
                "frontCCW": rs.frontCCW,
                "depthBias": rs.depthBias,
                "depthBiasClamp": rs.depthBiasClamp,
                "slopeScaledDepthBias": rs.slopeScaledDepthBias,
                "depthClip": rs.depthClip,
                "conservativeRasterization": str(rs.conservativeRasterization),
            }
        if gl:
            ps = gl()
            rs = ps.rasterizer.state
            return {
                "fillMode": str(rs.fillMode),
                "cullMode": str(rs.cullMode),
                "frontCCW": rs.frontCCW,
                "depthBias": rs.depthBias,
                "slopeScaledDepthBias": rs.slopeScaledDepthBias,
                "offsetClamp": rs.offsetClamp,
                "depthClamp": rs.depthClamp,
            }
        if vk:
            ps = vk()
            rs = ps.rasterizer
            return {
                "fillMode": str(rs.fillMode),
                "cullMode": str(rs.cullMode),
                "frontCCW": rs.frontCCW,
                "depthBiasEnable": rs.depthBiasEnable,
                "depthBias": rs.depthBias,
                "depthBiasClamp": rs.depthBiasClamp,
                "slopeScaledDepthBias": rs.slopeScaledDepthBias,
                "depthClampEnable": rs.depthClampEnable,
                "lineWidth": rs.lineWidth,
            }
    except Exception as e:
        click.echo(f"Warning: {e}", err=True)
    return None


def get_blend_state(pipe) -> Optional[Dict[str, Any]]:
    """Extract blend state from a PipeState object."""
    try:
        d3d11 = getattr(pipe, "GetD3D11PipelineState", None)
        d3d12 = getattr(pipe, "GetD3D12PipelineState", None)
        gl = getattr(pipe, "GetGLPipelineState", None)
        vk = getattr(pipe, "GetVulkanPipelineState", None)

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
            }

        if d3d11:
            ps = d3d11()
            om = ps.outputMerger
            return {
                "alphaToCoverage": om.blendState.alphaToCoverage,
                "independentBlend": om.blendState.independentBlend,
                "blends": [
                    dict(_blend_eq(b), index=i)
                    for i, b in enumerate(om.blendState.blends)
                ],
            }
        if d3d12:
            ps = d3d12()
            om = ps.outputMerger
            return {
                "alphaToCoverage": om.blendState.alphaToCoverage,
                "independentBlend": om.blendState.independentBlend,
                "blends": [
                    dict(_blend_eq(b), index=i)
                    for i, b in enumerate(om.blendState.blends)
                ],
            }
        if gl:
            ps = gl()
            fb = ps.framebuffer
            return {
                "blends": [
                    dict(_blend_eq(b), index=i)
                    for i, b in enumerate(fb.blendState.blends)
                ],
            }
        if vk:
            ps = vk()
            cb = ps.colorBlend
            return {
                "alphaToCoverage": cb.alphaToCoverageEnable,
                "blends": [
                    dict(_blend_eq(b), index=i) for i, b in enumerate(cb.blends)
                ],
            }
    except Exception as e:
        click.echo(f"Warning: {e}", err=True)
    return None
