# ruff: noqa: E501
"""SVG XML helper functions for Inkscape CLI.

Provides namespace constants, SVG creation/parsing/serialization,
and style string helpers.
"""

import xml.etree.ElementTree as ET
import re
from typing import Dict, Optional, Any

# ── SVG Namespaces ──────────────────────────────────────────────

SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SODIPODI_NS = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
XLINK_NS = "http://www.w3.org/1999/xlink"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
CC_NS = "http://creativecommons.org/ns#"
DC_NS = "http://purl.org/dc/elements/1.1/"

NSMAP = {
    "svg": SVG_NS,
    "inkscape": INKSCAPE_NS,
    "sodipodi": SODIPODI_NS,
    "xlink": XLINK_NS,
    "rdf": RDF_NS,
    "cc": CC_NS,
    "dc": DC_NS,
}

# Register namespaces so ET doesn't generate ns0, ns1, etc.
for prefix, uri in NSMAP.items():
    ET.register_namespace(prefix, uri)
# Also register default namespace
ET.register_namespace("", SVG_NS)

__all__ = [
    "Any",
    "CC_NS",
    "DC_NS",
    "Dict",
    "ET",
    "INKSCAPE_NS",
    "NSMAP",
    "Optional",
    "RDF_NS",
    "SODIPODI_NS",
    "SVG_NS",
    "XLINK_NS",
    "re",
]
