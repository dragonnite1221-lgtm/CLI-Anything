# ruff: noqa: E501
#!/usr/bin/env python3
"""Obsidian CLI — Knowledge management and note-taking via Obsidian Local REST API.

This CLI provides full access to the Obsidian REST API for managing notes,
searching the vault, and executing Obsidian commands.

Usage:
    # One-shot commands
    cli-anything-obsidian --api-key YOUR_KEY vault list
    cli-anything-obsidian --api-key YOUR_KEY vault read "My Note.md"
    cli-anything-obsidian --api-key YOUR_KEY --json search query "tag:#project"

    # Interactive REPL
    cli-anything-obsidian --api-key YOUR_KEY
"""

import sys
import os
import json
import shlex
import click
from cli_anything.obsidian.utils.obsidian_backend import DEFAULT_BASE_URL
from cli_anything.obsidian.core import vault as vault_mod
from cli_anything.obsidian.core import search as search_mod
from cli_anything.obsidian.core import note as note_mod
from cli_anything.obsidian.core import command as cmd_mod
from cli_anything.obsidian.core import server as server_mod

# Global state
_json_output = False
_repl_mode = False
_host = DEFAULT_BASE_URL
_api_key = ""
_last_path: str = ""

__all__ = [
    "DEFAULT_BASE_URL",
    "_api_key",
    "_host",
    "_json_output",
    "_last_path",
    "_repl_mode",
    "click",
    "cmd_mod",
    "json",
    "note_mod",
    "os",
    "search_mod",
    "server_mod",
    "shlex",
    "sys",
    "vault_mod",
]
