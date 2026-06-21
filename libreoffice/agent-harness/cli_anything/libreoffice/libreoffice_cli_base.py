# ruff: noqa: E501
#!/usr/bin/env python3
"""LibreOffice CLI -- A stateful command-line interface for document editing.

This CLI provides document creation and editing capabilities for Writer,
Calc, and Impress documents, with export to real ODF files (ZIP archives).

Usage:
    # One-shot commands
    python3 -m cli.libreoffice_cli document new --type writer --name "Report"
    python3 -m cli.libreoffice_cli writer add-paragraph --text "Hello world"
    python3 -m cli.libreoffice_cli export render output.odt --preset odt

    # Interactive REPL
    python3 -m cli.libreoffice_cli repl
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.libreoffice.core.session import Session
from cli_anything.libreoffice.core import document as doc_mod
from cli_anything.libreoffice.core import writer as writer_mod
from cli_anything.libreoffice.core import calc as calc_mod
from cli_anything.libreoffice.core import impress as impress_mod
from cli_anything.libreoffice.core import styles as styles_mod
from cli_anything.libreoffice.core import export as export_mod
from cli_anything.libreoffice.core import importer as import_mod

# Global session state
_session: Optional[Session] = None
_json_output = False
_repl_mode = False

__all__ = [
    "Optional",
    "Session",
    "_json_output",
    "_repl_mode",
    "_session",
    "calc_mod",
    "click",
    "doc_mod",
    "export_mod",
    "import_mod",
    "impress_mod",
    "json",
    "os",
    "shlex",
    "styles_mod",
    "sys",
    "writer_mod",
]
