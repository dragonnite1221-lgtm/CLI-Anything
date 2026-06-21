# ruff: noqa: F403, F405, E501
from .textures_base import *  # noqa: F403


def _tex_to_dict(tex) -> Dict[str, Any]:
    """Serialise TextureDescription to a plain dict."""
    return {
        "resourceId": str(tex.resourceId),
        "name": str(getattr(tex, "name", "")),
        "width": tex.width,
        "height": tex.height,
        "depth": tex.depth,
        "mips": tex.mips,
        "arraysize": tex.arraysize,
        "msQual": tex.msQual,
        "msSamp": tex.msSamp,
        "format": str(tex.format),
        "dimension": tex.dimension,
        "type": str(tex.type) if hasattr(tex, "type") else str(tex.dimension),
        "cubemap": getattr(tex, "cubemap", False),
        "byteSize": getattr(tex, "byteSize", 0),
        "creationFlags": int(getattr(tex, "creationFlags", 0)),
    }


def list_textures(controller) -> List[Dict[str, Any]]:
    """Return all textures in the capture."""
    textures = controller.GetTextures()
    return [_tex_to_dict(t) for t in textures]


def get_texture(controller, resource_id_str: str) -> Optional[Dict[str, Any]]:
    """Get a single texture by resource ID string."""
    for tex in controller.GetTextures():
        if str(tex.resourceId) == resource_id_str:
            return _tex_to_dict(tex)
    return None


def pick_pixel(
    controller,
    resource_id_str: str,
    x: int,
    y: int,
    mip: int = 0,
    slice_idx: int = 0,
    sample: int = 0,
) -> Dict[str, Any]:
    """Pick a pixel value from a texture.

    Returns dict with float, uint, and int value representations.
    """
    # Find the resource ID
    tex_id = None
    for tex in controller.GetTextures():
        if str(tex.resourceId) == resource_id_str:
            tex_id = tex.resourceId
            break
    if tex_id is None:
        return {"error": f"Texture {resource_id_str} not found"}

    sub = rd.Subresource(mip, slice_idx, sample)
    pix = controller.PickPixel(tex_id, x, y, sub, rd.CompType.Typeless)

    return {
        "x": x,
        "y": y,
        "resourceId": resource_id_str,
        "float": list(pix.floatValue),
        "uint": list(pix.uintValue),
        "int": list(pix.intValue),
    }


_FORMAT_MAP = {}
if HAS_RD and hasattr(rd, "FileType"):
    _FORMAT_MAP = {
        "png": rd.FileType.PNG,
        "jpg": rd.FileType.JPG,
        "jpeg": rd.FileType.JPG,
        "bmp": rd.FileType.BMP,
        "tga": rd.FileType.TGA,
        "hdr": rd.FileType.HDR,
        "exr": rd.FileType.EXR,
        "dds": rd.FileType.DDS,
    }
