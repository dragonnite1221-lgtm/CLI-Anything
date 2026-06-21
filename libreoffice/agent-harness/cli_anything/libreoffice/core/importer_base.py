# ruff: noqa: E501
"""Import existing Office/ODF files into the LibreOffice CLI project model."""

import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from cli_anything.libreoffice.core.document import create_document
from cli_anything.libreoffice.utils.lo_backend import convert
from cli_anything.libreoffice.utils.odf_utils import ODF_MIMETYPES, ODF_NS, parse_odf

__all__ = ['Any', 'Dict', 'ET', 'List', 'ODF_MIMETYPES', 'ODF_NS', 'Optional', 'Tuple', 'convert', 'create_document', 'datetime', 'os', 'parse_odf', 'tempfile', 'zipfile']

_COUP_GLOBALS = globals()
