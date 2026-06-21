# ruff: noqa: E501
"""Instrument management — list, add, remove, reorder.

For listing, uses mscore --score-meta. For add/remove/reorder,
manipulates the MSCX XML directly.
"""

import logging
import os
from pathlib import Path

from cli_anything.musescore.utils import musescore_backend as backend

logger = logging.getLogger(__name__)
from cli_anything.musescore.utils import mscx_xml as xml_utils

__all__ = ["Path", "backend", "logger", "logging", "os", "xml_utils"]
