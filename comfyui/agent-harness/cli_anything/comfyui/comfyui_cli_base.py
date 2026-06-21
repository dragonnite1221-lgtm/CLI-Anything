# ruff: noqa: E501
#!/usr/bin/env python3
"""ComfyUI CLI — Manage AI image generation from the command line.

This CLI wraps the ComfyUI REST API. It covers the full generation lifecycle:
workflow management, queue operations, model discovery, and image retrieval.

Usage:
    # Check server status
    cli-anything-comfyui system stats

    # List available checkpoints
    cli-anything-comfyui models checkpoints

    # Queue a workflow
    cli-anything-comfyui queue prompt --workflow my_workflow.json

    # Check queue
    cli-anything-comfyui queue status

    # Download images
    cli-anything-comfyui images download --filename ComfyUI_00001_.png --output ./out.png

    # Interactive REPL
    cli-anything-comfyui repl
"""

import sys
import os
import json
import shlex
import click

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.comfyui.core import workflows as workflow_mod
from cli_anything.comfyui.core import queue as queue_mod
from cli_anything.comfyui.core import models as models_mod
from cli_anything.comfyui.core import images as images_mod
from cli_anything.comfyui.utils.comfyui_backend import api_get, DEFAULT_BASE_URL

# Global state
_json_output = False
_base_url = DEFAULT_BASE_URL

__all__ = [
    "DEFAULT_BASE_URL",
    "_base_url",
    "_json_output",
    "api_get",
    "click",
    "images_mod",
    "json",
    "models_mod",
    "os",
    "queue_mod",
    "shlex",
    "sys",
    "workflow_mod",
]
