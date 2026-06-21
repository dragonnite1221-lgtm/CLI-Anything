# ruff: noqa: E501
"""MLT XML parsing and generation utilities.

This module handles all low-level MLT XML manipulation using
xml.etree.ElementTree from the Python standard library.
"""

import copy
import uuid
import xml.etree.ElementTree as ET
from typing import Optional

# Global parent mapping because ET.Element has no getparent().
# Safe for single-session architecture: only one Session/MLT tree exists per
# process. See Session class docstring in session.py for details.
_parent_map: dict[int, Optional[ET.Element]] = {}

__all__ = ["ET", "Optional", "_parent_map", "copy", "uuid"]
