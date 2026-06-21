# ruff: noqa: F403, F405, E501
from .layers_base import *  # noqa: F403

# fmt: off
from .layers_p1 import add_layer  # noqa: E402,E501
from .layers_p2 import _read_jpeg_dimensions, _read_tiff_dimensions, _read_webp_dimensions  # noqa: E402,E501
# fmt: on


def _read_image_dimensions(path: str) -> Optional[tuple]:
    """Read image width/height from file headers without external dependencies.

    Supports PNG, JPEG, GIF, BMP, WEBP, and TIFF.
    Returns (width, height) or None if the format is unrecognised.
    """
    try:
        with open(path, "rb") as f:
            header = f.read(32)

        if len(header) < 8:
            return None

        # PNG: 8-byte signature, then IHDR chunk with w/h at bytes 16-24
        if header[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", header[16:24])
            return (w, h)

        # GIF: signature + logical screen descriptor
        if header[:6] in (b"GIF87a", b"GIF89a"):
            w, h = struct.unpack("<HH", header[6:10])
            return (w, h)

        # BMP: 'BM' header, w/h as signed int32 at bytes 18-26
        if header[:2] == b"BM" and len(header) >= 26:
            w, h = struct.unpack("<ii", header[18:26])
            return (w, abs(h))

        # TIFF: byte-order mark then magic 42
        if header[:4] in (b"II\x2a\x00", b"MM\x00\x2a"):
            return _read_tiff_dimensions(path, header)

        # JPEG: starts with SOI marker 0xFFD8
        if header[:2] == b"\xff\xd8":
            return _read_jpeg_dimensions(path)

        # WEBP: RIFF container with 'WEBP' fourcc
        if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
            return _read_webp_dimensions(path)

    except (OSError, struct.error):
        pass
    return None


def add_from_file(
    project: Dict[str, Any],
    path: str,
    name: Optional[str] = None,
    position: Optional[int] = None,
    opacity: float = 1.0,
    blend_mode: str = "normal",
) -> Dict[str, Any]:
    """Add a layer from an image file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")

    layer_name = name or os.path.basename(path)

    dims = _read_image_dimensions(path)
    if dims:
        w, h = dims
    else:
        w = project["canvas"]["width"]
        h = project["canvas"]["height"]

    return add_layer(
        project,
        name=layer_name,
        layer_type="image",
        source=os.path.abspath(path),
        width=w,
        height=h,
        opacity=opacity,
        blend_mode=blend_mode,
        position=position,
    )


def remove_layer(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Remove a layer by index."""
    layers = project.get("layers", [])
    if not layers:
        raise ValueError("No layers to remove")
    if index < 0 or index >= len(layers):
        raise IndexError(f"Layer index {index} out of range (0-{len(layers) - 1})")
    removed = layers.pop(index)
    return removed


def duplicate_layer(project: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Duplicate a layer."""
    layers = project.get("layers", [])
    if index < 0 or index >= len(layers):
        raise IndexError(f"Layer index {index} out of range (0-{len(layers) - 1})")

    original = layers[index]
    dup = copy.deepcopy(original)
    existing_ids = [l.get("id", 0) for l in layers]
    dup["id"] = max(existing_ids, default=-1) + 1
    dup["name"] = f"{original['name']} copy"
    layers.insert(index, dup)
    return dup


def move_layer(project: Dict[str, Any], index: int, to: int) -> None:
    """Move a layer to a new position."""
    layers = project.get("layers", [])
    if index < 0 or index >= len(layers):
        raise IndexError(f"Source layer index {index} out of range")
    to = max(0, min(to, len(layers) - 1))
    layer = layers.pop(index)
    layers.insert(to, layer)
