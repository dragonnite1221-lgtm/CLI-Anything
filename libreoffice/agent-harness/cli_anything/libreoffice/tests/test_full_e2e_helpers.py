# ruff: noqa: F403, F405, E501
"""End-to-end tests for LibreOffice CLI with real ODF file validation
and real LibreOffice headless conversion.

These tests:
1. Create ODF files and validate their XML structure (native tests)
2. Convert ODF -> PDF/DOCX/XLSX/PPTX via LibreOffice headless (true E2E)
3. Verify output files exist, have correct format, and contain expected content
4. Print all generated artifact paths so users can inspect the output

Requires: libreoffice (system package) for the LibreOffice backend tests.
"""

import json
import os
import sys
import tempfile
import zipfile
import subprocess
import xml.etree.ElementTree as ET
import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from cli_anything.libreoffice.core.document import (
    create_document,
    save_document,
    open_document,
    get_document_info,
)
from cli_anything.libreoffice.core.writer import (
    add_paragraph,
    add_heading,
    add_list,
    add_table,
    add_page_break,
    list_content,
    remove_content,
)
from cli_anything.libreoffice.core.calc import (
    add_sheet,
    set_cell,
    get_cell,
    list_sheets,
    remove_sheet,
)
from cli_anything.libreoffice.core.impress import (
    add_slide,
    remove_slide,
    set_slide_content,
    add_slide_element,
    list_slides,
)
from cli_anything.libreoffice.core.styles import create_style, apply_style, list_styles
from cli_anything.libreoffice.core.export import (
    export,
    to_odt,
    to_ods,
    to_odp,
    to_html,
    to_text,
    list_presets,
)
from cli_anything.libreoffice.core import importer as importer_mod
from cli_anything.libreoffice.core.session import Session
from cli_anything.libreoffice.utils.odf_utils import (
    validate_odf,
    parse_odf,
    ODF_MIMETYPES,
)
from cli_anything.libreoffice.utils.lo_backend import (
    find_libreoffice,
    get_version,
    convert_odf_to,
)


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    import shutil

    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = (
        name.replace("cli-anything-", "cli_anything.")
        + "."
        + name.split("-")[-1]
        + "_cli"
    )
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


__all__ = [
    "ET",
    "ODF_MIMETYPES",
    "Session",
    "_resolve_cli",
    "add_heading",
    "add_list",
    "add_page_break",
    "add_paragraph",
    "add_sheet",
    "add_slide",
    "add_slide_element",
    "add_table",
    "apply_style",
    "convert_odf_to",
    "create_document",
    "create_style",
    "export",
    "find_libreoffice",
    "get_cell",
    "get_document_info",
    "get_version",
    "importer_mod",
    "json",
    "list_content",
    "list_presets",
    "list_sheets",
    "list_slides",
    "list_styles",
    "open_document",
    "os",
    "parse_odf",
    "pytest",
    "remove_content",
    "remove_sheet",
    "remove_slide",
    "save_document",
    "set_cell",
    "set_slide_content",
    "subprocess",
    "sys",
    "tempfile",
    "tmp_dir",
    "to_html",
    "to_odp",
    "to_ods",
    "to_odt",
    "to_text",
    "validate_odf",
    "zipfile",
]
