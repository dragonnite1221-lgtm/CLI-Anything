# ruff: noqa: F403, F405, E501
from .krita_backend_base import *  # noqa: F403

# fmt: off
from .krita_backend_p3 import run_script  # noqa: E402,E501
# fmt: on


def create_new_image(
    width: int,
    height: int,
    output_path: str | Path,
    *,
    colorspace: str = "RGBA",
    depth: int = 8,
    background_color: str = "white",
    timeout: int = 300,
) -> Dict[str, Any]:
    """Create a new image of the given dimensions and save it.

    Because Krita's CLI does not expose a direct ``--new`` flag, this
    generates a small Python script and runs it with :func:`run_script`.

    Parameters:
        width: Image width in pixels.
        height: Image height in pixels.
        output_path: Where to save the resulting file.
        colorspace: Krita colour model name (``"RGBA"``, ``"GRAYA"``, etc.).
        depth: Bit depth per channel (8, 16, or 32).
        background_color: Fill colour name (``"white"``, ``"transparent"``,
            ``"black"``).
        timeout: Maximum seconds to wait.

    Returns:
        Result dict with ``output_path`` and ``output_exists`` keys.
    """
    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Map friendly depth values to Krita depth identifiers.
    depth_map = {
        8: "U8",
        16: "U16",
        32: "F32",
    }
    krita_depth = depth_map.get(depth, "U8")

    # Map background colour to RGBA tuples used in the InfoObject.
    bg_map = {
        "white": "(255, 255, 255, 255)",
        "black": "(0, 0, 0, 255)",
        "transparent": "(0, 0, 0, 0)",
    }
    bg_rgba = bg_map.get(background_color, "(255, 255, 255, 255)")

    script = textwrap.dedent(f"""\
        from krita import Krita
        import sys

        app = Krita.instance()
        doc = app.createDocument(
            {width},   # width
            {height},  # height
            "Untitled",
            "{colorspace}",
            "{krita_depth}",
            "",         # profile
            300.0,      # resolution
        )
        if doc is None:
            print("ERROR: failed to create document", file=sys.stderr)
            sys.exit(1)

        app.activeWindow().addView(doc)

        # Fill the background layer.
        root = doc.rootNode()
        first_layer = root.childNodes()[0] if root.childNodes() else None
        if first_layer is not None:
            color = app.createManagedColor("{colorspace}", "{krita_depth}", "")
            components = {bg_rgba}
            color.setComponents(list(components))
            sel = doc.selection()
            if sel is None:
                from krita import Selection
                sel = Selection()
                sel.select(0, 0, {width}, {height}, 255)
            first_layer.setPixelData(
                bytes([int(c) for c in components] * {width} * {height}),
                0, 0, {width}, {height},
            )

        doc.saveAs("{output_path.replace(chr(92), "/")}")
        doc.close()
        app.quit()
    """)

    result = run_script(script, timeout=timeout)
    result["output_path"] = output_path
    result["output_exists"] = os.path.isfile(output_path)
    return result
