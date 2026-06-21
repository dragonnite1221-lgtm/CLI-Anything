# ruff: noqa: F403, F405, E501
"""Unit tests for LibreOffice CLI core modules.

Tests use synthetic data only -- no LibreOffice installation needed.
"""

import json
import os
import sys
import tempfile
import shutil
import zipfile
import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from cli_anything.libreoffice.core.document import (
    create_document,
    open_document,
    save_document,
    get_document_info,
    list_profiles,
    PROFILES,
)
from cli_anything.libreoffice.core.writer import (
    add_paragraph,
    add_heading,
    add_list,
    add_table,
    add_page_break,
    remove_content,
    list_content,
    get_content,
    set_content_text,
)
from cli_anything.libreoffice.core.calc import (
    add_sheet,
    remove_sheet,
    rename_sheet,
    set_cell,
    get_cell,
    clear_cell,
    list_sheets,
    get_sheet_data,
)
from cli_anything.libreoffice.core.impress import (
    add_slide,
    remove_slide,
    set_slide_content,
    add_slide_element,
    remove_slide_element,
    move_slide,
    duplicate_slide,
    list_slides,
    get_slide,
)
from cli_anything.libreoffice.core.styles import (
    create_style,
    modify_style,
    remove_style,
    list_styles,
    get_style,
    apply_style,
)
from cli_anything.libreoffice.core.session import Session
from cli_anything.libreoffice.core.export import to_odt, to_ods, to_odp
from cli_anything.libreoffice.core import importer as importer_mod
from cli_anything.libreoffice.utils.odf_utils import parse_odf


__all__ = [
    "PROFILES",
    "Session",
    "add_heading",
    "add_list",
    "add_page_break",
    "add_paragraph",
    "add_sheet",
    "add_slide",
    "add_slide_element",
    "add_table",
    "apply_style",
    "clear_cell",
    "create_document",
    "create_style",
    "duplicate_slide",
    "get_cell",
    "get_content",
    "get_document_info",
    "get_sheet_data",
    "get_slide",
    "get_style",
    "importer_mod",
    "json",
    "list_content",
    "list_profiles",
    "list_sheets",
    "list_slides",
    "list_styles",
    "modify_style",
    "move_slide",
    "open_document",
    "os",
    "parse_odf",
    "pytest",
    "remove_content",
    "remove_sheet",
    "remove_slide",
    "remove_slide_element",
    "remove_style",
    "rename_sheet",
    "save_document",
    "set_cell",
    "set_content_text",
    "set_slide_content",
    "shutil",
    "sys",
    "tempfile",
    "to_odp",
    "to_ods",
    "to_odt",
    "zipfile",
]
