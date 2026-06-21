# ruff: noqa: E501
#!/usr/bin/env python3
"""Ollama CLI — A command-line interface for local LLM inference and model management.

This CLI provides full access to the Ollama REST API for managing models,
generating text, chatting, and creating embeddings.

Usage:
    # One-shot commands
    cli-anything-ollama model list
    cli-anything-ollama generate text --model llama3.2 --prompt "Hello"
    cli-anything-ollama --json server status

    # Interactive REPL
    cli-anything-ollama
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

from cli_anything.ollama.utils.ollama_backend import DEFAULT_BASE_URL
from cli_anything.ollama.core import models as models_mod
from cli_anything.ollama.core import generate as gen_mod
from cli_anything.ollama.core import embeddings as embed_mod
from cli_anything.ollama.core import server as server_mod

# Global state
_json_output = False
_repl_mode = False
_host = DEFAULT_BASE_URL
_chat_history: list[dict] = []
_last_model: str = ""

__all__ = [
    "DEFAULT_BASE_URL",
    "Optional",
    "_chat_history",
    "_host",
    "_json_output",
    "_last_model",
    "_repl_mode",
    "click",
    "embed_mod",
    "gen_mod",
    "json",
    "models_mod",
    "os",
    "server_mod",
    "shlex",
    "sys",
]
