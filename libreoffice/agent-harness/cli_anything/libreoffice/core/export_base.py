# ruff: noqa: E501
"""LibreOffice CLI - Export module.

Exports project JSON to ODF files (real ZIP archives), HTML, plain text,
and via LibreOffice headless to PDF, DOCX, XLSX, PPTX, and other formats.
"""

import os
import html as html_module
import tempfile
from typing import Dict, Any, Optional, List

from cli_anything.libreoffice.utils.odf_utils import write_odf, ODF_EXTENSIONS
from cli_anything.libreoffice.utils.lo_backend import convert_odf_to


# Export presets
# "native" presets produce ODF/HTML/text directly (no LibreOffice needed)
# "lo_convert" presets use LibreOffice headless to convert from ODF
EXPORT_PRESETS = {
    # Native ODF
    "odt": {
        "format": "odt",
        "ext": ".odt",
        "description": "ODF Writer document",
        "method": "native",
    },
    "ods": {
        "format": "ods",
        "ext": ".ods",
        "description": "ODF Calc spreadsheet",
        "method": "native",
    },
    "odp": {
        "format": "odp",
        "ext": ".odp",
        "description": "ODF Impress presentation",
        "method": "native",
    },
    "html": {
        "format": "html",
        "ext": ".html",
        "description": "HTML document",
        "method": "native",
    },
    "text": {
        "format": "text",
        "ext": ".txt",
        "description": "Plain text",
        "method": "native",
    },
    # LibreOffice headless conversions
    "pdf": {
        "format": "pdf",
        "ext": ".pdf",
        "description": "PDF document (via LibreOffice)",
        "method": "lo_convert",
        "source_odf": "writer",
    },
    "docx": {
        "format": "docx",
        "ext": ".docx",
        "description": "MS Word DOCX (via LibreOffice)",
        "method": "lo_convert",
        "source_odf": "writer",
    },
    "xlsx": {
        "format": "xlsx",
        "ext": ".xlsx",
        "description": "MS Excel XLSX (via LibreOffice)",
        "method": "lo_convert",
        "source_odf": "calc",
    },
    "pptx": {
        "format": "pptx",
        "ext": ".pptx",
        "description": "MS PowerPoint PPTX (via LibreOffice)",
        "method": "lo_convert",
        "source_odf": "impress",
    },
    "csv": {
        "format": "csv",
        "ext": ".csv",
        "description": "CSV spreadsheet (via LibreOffice)",
        "method": "lo_convert",
        "source_odf": "calc",
    },
}

# Map format to doc type
_FORMAT_TO_DOCTYPE = {
    "odt": "writer",
    "ods": "calc",
    "odp": "impress",
}

__all__ = [
    "Any",
    "Dict",
    "EXPORT_PRESETS",
    "List",
    "ODF_EXTENSIONS",
    "Optional",
    "_FORMAT_TO_DOCTYPE",
    "convert_odf_to",
    "html_module",
    "os",
    "tempfile",
    "write_odf",
]
