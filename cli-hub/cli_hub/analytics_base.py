# ruff: noqa: E501
"""Lightweight, opt-out-able analytics with switchable providers."""

import atexit
import os
import platform
import re
import sys
import threading
import uuid
from pathlib import Path

import requests

from cli_hub import __version__

__all__ = [
    "Path",
    "__version__",
    "atexit",
    "os",
    "platform",
    "re",
    "requests",
    "sys",
    "threading",
    "uuid",
]
