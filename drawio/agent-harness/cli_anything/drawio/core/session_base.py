# ruff: noqa: E501
"""Stateful session management for the Draw.io CLI.

A session tracks the currently open project, undo history, and working state.
Sessions persist to disk as JSON so they survive process restarts.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

from ..utils import drawio_xml

__all__ = ["ET", "Optional", "Path", "drawio_xml", "json", "os", "time"]
