# ruff: noqa: E501
from __future__ import annotations

import configparser
import os
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Optional


DATA_DIR_PREF = "extensions.zotero.dataDir"
USE_DATA_DIR_PREF = "extensions.zotero.useDataDir"
LOCAL_API_PREF = "extensions.zotero.httpServer.localAPI.enabled"
HTTP_PORT_PREF = "extensions.zotero.httpServer.port"

__all__ = [
    "DATA_DIR_PREF",
    "HTTP_PORT_PREF",
    "LOCAL_API_PREF",
    "Mapping",
    "Optional",
    "Path",
    "USE_DATA_DIR_PREF",
    "annotations",
    "asdict",
    "configparser",
    "dataclass",
    "os",
    "re",
    "shutil",
]
