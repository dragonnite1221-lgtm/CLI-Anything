# ruff: noqa: E501
"""LibreOffice CLI - ODF XML helpers.

ODF (Open Document Format) files are ZIP archives containing XML files.
This module provides utilities for creating, parsing, and writing ODF documents.

Key ODF structure:
  mimetype          - MIME type (stored uncompressed, first entry)
  content.xml       - Document content
  styles.xml        - Document styles
  meta.xml          - Metadata
  META-INF/manifest.xml - Manifest of all files in the archive
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from datetime import datetime


# ODF XML Namespaces
ODF_NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "dc": "http://purl.org/dc/elements/1.1/",
    "manifest": "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0",
    "number": "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
}

# MIME types for ODF document types
ODF_MIMETYPES = {
    "writer": "application/vnd.oasis.opendocument.text",
    "calc": "application/vnd.oasis.opendocument.spreadsheet",
    "impress": "application/vnd.oasis.opendocument.presentation",
}

# File extensions for ODF document types
ODF_EXTENSIONS = {
    "writer": ".odt",
    "calc": ".ods",
    "impress": ".odp",
}

__all__ = [
    "Any",
    "Dict",
    "ET",
    "ODF_EXTENSIONS",
    "ODF_MIMETYPES",
    "ODF_NS",
    "Optional",
    "datetime",
    "os",
    "zipfile",
]
