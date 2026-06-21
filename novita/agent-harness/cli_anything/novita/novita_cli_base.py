# ruff: noqa: E501
#!/usr/bin/env python3
"""Novita CLI — OpenAI-compatible AI API client.

Usage:
    # One-shot commands
    cli-anything-novita chat --prompt "Hello" --model deepseek/deepseek-v3.2

    # Interactive REPL
    cli-anything-novita
"""

from __future__ import annotations

import sys
import os
import json
import click
from pathlib import Path

from cli_anything.novita.core.session import ChatSession
from cli_anything.novita.utils.novita_backend import (
    get_api_key,
    load_config,
    save_config,
    chat_completion,
    chat_completion_stream,
    run_full_workflow,
    API_BASE,
    ENV_API_KEY,
    list_models,
)

_session = None
_json_output = False
_repl_mode = False

__all__ = [
    "API_BASE",
    "ChatSession",
    "ENV_API_KEY",
    "Path",
    "_json_output",
    "_repl_mode",
    "_session",
    "annotations",
    "chat_completion",
    "chat_completion_stream",
    "click",
    "get_api_key",
    "json",
    "list_models",
    "load_config",
    "os",
    "run_full_workflow",
    "save_config",
    "sys",
]
