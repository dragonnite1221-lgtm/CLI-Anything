# ruff: noqa: E501
# ruff: noqa: F403, F405, E501
"""TCP listener that receives live NSLogger connections."""

from __future__ import annotations
import os
import base64
import json
import socket
import ssl
import struct
import subprocess
import sys
import tempfile
import threading
from importlib import resources
from typing import Callable, Optional
from .message import LogMessage
from .parser import _parse_message, ParseError


NSLOGGER_SERVICE_TYPE = "_nslogger._tcp.local."


NSLOGGER_SSL_SERVICE_TYPE = "_nslogger-ssl._tcp.local."

__all__ = [
    "Callable",
    "LogMessage",
    "NSLOGGER_SERVICE_TYPE",
    "NSLOGGER_SSL_SERVICE_TYPE",
    "Optional",
    "ParseError",
    "_parse_message",
    "annotations",
    "base64",
    "json",
    "os",
    "resources",
    "socket",
    "ssl",
    "struct",
    "subprocess",
    "sys",
    "tempfile",
    "threading",
]
