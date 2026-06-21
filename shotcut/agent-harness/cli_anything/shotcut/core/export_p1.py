# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def list_presets() -> list[dict]:
    """List all available export presets."""
    result = []
    for name, preset in sorted(EXPORT_PRESETS.items()):
        result.append(
            {
                "name": name,
                "description": preset["description"],
                "format": preset.get("format", ""),
                "vcodec": preset.get("vcodec", ""),
                "acodec": preset.get("acodec", ""),
            }
        )
    return result


def get_preset_info(preset_name: str) -> dict:
    """Get detailed info about an export preset."""
    if preset_name not in EXPORT_PRESETS:
        available = ", ".join(sorted(EXPORT_PRESETS.keys()))
        raise ValueError(f"Unknown preset: {preset_name!r}. Available: {available}")
    info = dict(EXPORT_PRESETS[preset_name])
    info["name"] = preset_name
    return info


def _render_with_melt(
    session: Session,
    output_path: str,
    preset: dict,
    melt_path: str,
    width: Optional[int],
    height: Optional[int],
    extra_args: Optional[list[str]],
) -> dict:
    import tempfile

    root = session.root
    assert root is not None

    from .timeline import _update_tractor_out

    _update_tractor_out(session)

    old_producer = root.get("producer", "main_bin")
    tractor = mlt_xml.get_main_tractor(root)
    tractor_id = tractor.get("id", "tractor0") if tractor is not None else "tractor0"
    root.set("producer", tractor_id)

    try:
        with tempfile.NamedTemporaryFile(suffix=".mlt", delete=False, mode="w") as f:
            temp_mlt = f.name
            mlt_xml.write_mlt(root, temp_mlt)
    finally:
        root.set("producer", old_producer)

    try:
        cmd = [melt_path, temp_mlt, "-consumer"]

        consumer = f"avformat:{output_path}"
        cmd.append(consumer)

        vcodec = preset.get("vcodec", "")
        acodec = preset.get("acodec", "")
        if vcodec:
            cmd.extend(["vcodec=" + vcodec])
        if acodec:
            cmd.extend(["acodec=" + acodec])
        if preset.get("vb"):
            cmd.extend(["vb=" + preset["vb"]])
        if preset.get("crf"):
            cmd.extend(["crf=" + preset["crf"]])
        if preset.get("preset"):
            cmd.extend(["preset=" + preset["preset"]])
        if preset.get("ab"):
            cmd.extend(["ab=" + preset["ab"]])
        if preset.get("ar"):
            cmd.extend(["ar=" + preset["ar"]])

        if width and height:
            cmd.extend([f"width={width}", f"height={height}"])

        if extra_args:
            cmd.extend(extra_args)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

        if result.returncode != 0:
            raise RuntimeError(f"melt render failed: {result.stderr}")

        return {
            "action": "render",
            "output": output_path,
            "method": "melt",
            "success": True,
            "size_bytes": os.path.getsize(output_path)
            if os.path.exists(output_path)
            else 0,
        }
    finally:
        os.unlink(temp_mlt)
