# ruff: noqa: E501
"""
Background LLDB session server for persistent non-REPL workflows.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import hmac
import json
import os
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from cli_anything.lldb.core.session import LLDBSession

MAX_MESSAGE_BYTES = 1024 * 1024

_ALLOWED_SESSION_METHODS = {
    "target_create",
    "target_info",
    "attach_pid",
    "attach_name",
    "launch",
    "detach",
    "breakpoint_set",
    "breakpoint_list",
    "breakpoint_delete",
    "breakpoint_enable",
    "step_over",
    "step_into",
    "step_out",
    "continue_exec",
    "interrupt",
    "interrupt_async",
    "backtrace",
    "locals",
    "local_values",
    "set_local_variable",
    "set_child_value",
    "evaluate",
    "threads",
    "thread_select",
    "frame_select",
    "frame_info",
    "read_memory",
    "find_memory",
    "disassemble",
    "loaded_sources",
    "modules",
    "load_core",
    "process_info",
}

__all__ = [
    "Any",
    "LLDBSession",
    "MAX_MESSAGE_BYTES",
    "Path",
    "_ALLOWED_SESSION_METHODS",
    "annotations",
    "argparse",
    "base64",
    "getpass",
    "hmac",
    "json",
    "os",
    "socket",
    "struct",
    "subprocess",
    "sys",
    "time",
]
