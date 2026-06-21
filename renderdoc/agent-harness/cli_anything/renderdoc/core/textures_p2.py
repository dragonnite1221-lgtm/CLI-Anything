# ruff: noqa: F403, F405, E501
from .textures_base import *  # noqa: F403

# fmt: off
from .textures_p1 import _FORMAT_MAP  # noqa: E402,E501
# fmt: on


def save_texture(
    controller,
    resource_id_str: str,
    output_path: str,
    file_format: str = "png",
    mip: int = 0,
    slice_idx: int = 0,
    alpha: str = "preserve",
) -> Dict[str, Any]:
    """Save a texture to disk.

    Parameters
    ----------
    controller : ReplayController
    resource_id_str : str
        The resource ID as a string.
    output_path : str
        Destination file path.
    file_format : str
        One of: png, jpg, bmp, tga, hdr, exr, dds
    mip : int
        Mip level to save (-1 for all, DDS only).
    slice_idx : int
        Array slice to save (-1 for all, DDS only).
    alpha : str
        Alpha handling: 'preserve', 'discard', 'blend_checkerboard'
    """
    fmt_lower = file_format.lower()
    if fmt_lower not in _FORMAT_MAP:
        return {
            "error": f"Unsupported format: {file_format}. Use: {list(_FORMAT_MAP.keys())}"
        }

    tex_id = None
    for tex in controller.GetTextures():
        if str(tex.resourceId) == resource_id_str:
            tex_id = tex.resourceId
            break
    if tex_id is None:
        return {"error": f"Texture {resource_id_str} not found"}

    save = rd.TextureSave()
    save.resourceId = tex_id
    save.destType = _FORMAT_MAP[fmt_lower]
    save.mip = mip
    save.slice.sliceIndex = slice_idx

    alpha_lower = alpha.lower()
    if alpha_lower == "preserve":
        save.alpha = rd.AlphaMapping.Preserve
    elif alpha_lower == "discard":
        save.alpha = rd.AlphaMapping.Discard
    elif alpha_lower in ("blend", "blend_checkerboard", "checkerboard"):
        save.alpha = rd.AlphaMapping.BlendToCheckerboard
    else:
        save.alpha = rd.AlphaMapping.Preserve

    output_path = os.path.abspath(output_path)
    controller.SaveTexture(save, output_path)

    if os.path.isfile(output_path):
        return {
            "path": output_path,
            "format": fmt_lower,
            "size": os.path.getsize(output_path),
        }
    return {"error": "Failed to save texture (file not created)"}


def save_action_outputs(
    controller,
    event_id: int,
    output_dir: str,
    file_format: str = "png",
) -> List[Dict[str, Any]]:
    """Save all render target outputs at a specific event.

    Moves the replay to *event_id*, then saves each colour output and
    the depth output (if any) to *output_dir*.
    """
    controller.SetFrameEvent(event_id, True)
    state = controller.GetPipelineState()
    targets = state.GetOutputTargets()
    depth = state.GetDepthTarget()

    results = []
    os.makedirs(output_dir, exist_ok=True)

    for i, t in enumerate(targets):
        if t.resourceId == rd.ResourceId.Null():
            continue
        rid = str(t.resourceId)
        fname = f"event{event_id}_rt{i}.{file_format}"
        path = os.path.join(output_dir, fname)
        r = save_texture(controller, rid, path, file_format)
        r["label"] = f"RT{i}"
        results.append(r)

    if depth.resourceId != rd.ResourceId.Null():
        rid = str(depth.resourceId)
        fname = f"event{event_id}_depth.{file_format}"
        path = os.path.join(output_dir, fname)
        r = save_texture(controller, rid, path, file_format)
        r["label"] = "Depth"
        results.append(r)

    return results
