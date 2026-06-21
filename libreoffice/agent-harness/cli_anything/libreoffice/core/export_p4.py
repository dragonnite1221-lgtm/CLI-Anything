# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _export_odf  # noqa: E402,E501
from .export_p2 import to_html  # noqa: E402,E501
from .export_p3 import to_text  # noqa: E402,E501
# fmt: on


def _export_via_libreoffice(
    project: Dict[str, Any],
    output_path: str,
    preset_cfg: Dict[str, Any],
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Export by generating an ODF intermediate then converting via LibreOffice.

    This is the key integration point: we generate a valid ODF file using our
    own XML builder, then hand it to LibreOffice headless for conversion to
    PDF/DOCX/XLSX/PPTX/CSV. LibreOffice does the real rendering.
    """
    target_format = preset_cfg["format"]
    source_odf_type = preset_cfg.get("source_odf", "writer")
    doc_type = project.get("type", "writer")

    # Determine correct ODF intermediate format based on document type
    odf_ext = {
        "writer": ".odt",
        "calc": ".ods",
        "impress": ".odp",
    }.get(doc_type, ".odt")

    # Generate the ODF intermediate in a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        odf_path = os.path.join(tmpdir, f"intermediate{odf_ext}")
        write_odf(odf_path, doc_type, project)

        result = convert_odf_to(
            odf_path,
            output_format=target_format,
            output_path=output_path,
            overwrite=overwrite,
        )

    result["preset"] = target_format
    result["source_type"] = doc_type
    return result


def export(
    project: Dict[str, Any],
    output_path: str,
    preset: str = "odt",
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Export using a named preset.

    Native presets (odt, ods, odp, html, text) produce files directly.
    LibreOffice presets (pdf, docx, xlsx, pptx, csv) first generate an
    ODF intermediate file, then convert it using `libreoffice --headless`.
    """
    if preset not in EXPORT_PRESETS:
        raise ValueError(
            f"Unknown preset: {preset}. Available: {', '.join(EXPORT_PRESETS.keys())}"
        )

    preset_cfg = EXPORT_PRESETS[preset]
    fmt = preset_cfg["format"]
    method = preset_cfg.get("method", "native")

    if method == "lo_convert":
        return _export_via_libreoffice(project, output_path, preset_cfg, overwrite)
    elif fmt == "html":
        return to_html(project, output_path, overwrite)
    elif fmt == "text":
        return to_text(project, output_path, overwrite)
    elif fmt in _FORMAT_TO_DOCTYPE:
        doc_type = _FORMAT_TO_DOCTYPE[fmt]
        return _export_odf(project, output_path, doc_type, overwrite)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
