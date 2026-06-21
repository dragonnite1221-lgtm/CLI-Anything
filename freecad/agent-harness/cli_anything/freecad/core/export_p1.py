# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def _validate_step(path: str) -> bool:
    """Check that *path* starts with the ISO-10303-21 header marker."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            header = fh.read(64)
        return header.strip().startswith("ISO-10303-21")
    except OSError:
        return False


def _validate_stl(path: str) -> bool:
    """Check for ASCII STL (``solid`` keyword) or valid binary STL header.

    A binary STL has an 80-byte header followed by a 4-byte little-endian
    triangle count.  An ASCII STL starts with the word ``solid``.
    """
    try:
        with open(path, "rb") as fh:
            head = fh.read(80)
        if not head:
            return False
        # ASCII STL check
        text_head = head.decode("ascii", errors="ignore").strip().lower()
        if text_head.startswith("solid"):
            return True
        # Binary STL: 80-byte header + 4-byte uint32 triangle count
        with open(path, "rb") as fh:
            fh.seek(80)
            count_bytes = fh.read(4)
            if len(count_bytes) == 4:
                _tri_count = struct.unpack("<I", count_bytes)[0]
                return True
        return False
    except OSError:
        return False


def _validate_iges(path: str) -> bool:
    """Check for IGES header markers in the first few lines.

    IGES files have fixed-width 80-column records.  The 73rd column of
    the first record should contain ``S`` (Start section).
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            first_line = fh.readline()
        if not first_line:
            return False
        # The 73rd character (index 72) should be 'S' for the start section
        if len(first_line) >= 73 and first_line[72] == "S":
            return True
        # Fallback: look for common IGES keywords
        upper = first_line.upper()
        return "IGES" in upper or "INITIAL GRAPHICS" in upper
    except OSError:
        return False


def _validate_dxf(path: str) -> bool:
    """Check that *path* contains DXF section markers."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            header = fh.read(256)
        return "0\nSECTION" in header or "AutoCAD" in header
    except OSError:
        return False


def _validate_svg(path: str) -> bool:
    """Check that *path* contains SVG or XML markers."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            header = fh.read(256)
        return "<svg" in header.lower() or "<?xml" in header.lower()
    except OSError:
        return False


def _validate_pdf(path: str) -> bool:
    """Check that *path* starts with the ``%PDF-`` header."""
    try:
        with open(path, "rb") as fh:
            header = fh.read(8)
        return header.startswith(b"%PDF-")
    except OSError:
        return False


def _validate_gltf(path: str) -> bool:
    """Check for glTF binary magic bytes or JSON with ``asset`` key."""
    try:
        with open(path, "rb") as fh:
            magic = fh.read(4)
        # Binary glTF magic: "glTF"
        if magic == b"glTF":
            return True
        # JSON-based glTF
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            header = fh.read(512)
        return '"asset"' in header
    except OSError:
        return False


def _validate_3mf(path: str) -> bool:
    """Check that *path* is a ZIP archive containing ``3D/3dmodel.model``."""
    try:
        if not zipfile.is_zipfile(path):
            return False
        with zipfile.ZipFile(path, "r") as zf:
            return "3D/3dmodel.model" in zf.namelist()
    except (OSError, zipfile.BadZipFile):
        return False


_FORMAT_VALIDATORS: Dict[str, Any] = {
    "step": _validate_step,
    "iges": _validate_iges,
    "stl": _validate_stl,
    "dxf": _validate_dxf,
    "svg": _validate_svg,
    "pdf": _validate_pdf,
    "gltf": _validate_gltf,
    "3mf": _validate_3mf,
}
