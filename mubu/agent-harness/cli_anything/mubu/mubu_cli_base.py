# ruff: noqa: E501
from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path
from typing import Iterable, Sequence

import click

import mubu_probe
from cli_anything.mubu import __version__
from cli_anything.mubu.utils import ReplSkin


CONTEXT_SETTINGS = {"ignore_unknown_options": True, "allow_extra_args": True}
COMMAND_HISTORY_LIMIT = 50
PUBLIC_PROGRAM_NAME = "mubu-cli"
COMPAT_PROGRAM_NAME = "cli-anything-mubu"
DISCOVER_COMMANDS = {
    "docs": "List latest known document snapshots from local backups.",
    "folders": "List folder metadata from local RxDB storage.",
    "folder-docs": "List document metadata for one folder.",
    "path-docs": "List documents for one folder path or folder id.",
    "recent": "List recently active documents using backups, metadata, and sync logs.",
    "daily": "Find Daily-style folders and list the documents inside them.",
    "daily-current": "Resolve the current daily document from one Daily-style folder.",
}
INSPECT_COMMANDS = {
    "show": "Show the latest backup tree for one document.",
    "search": "Search latest backups for matching node text or note content.",
    "changes": "Parse recent client-sync change events from local logs.",
    "links": "Extract outbound Mubu document links from one document backup.",
    "open-path": "Open one document by full path, suffix path, title, or doc id.",
    "doc-nodes": "List live document nodes with node ids and update-target paths.",
    "daily-nodes": "List live nodes from the current daily document in one step.",
}
MUTATE_COMMANDS = {
    "create-child": "Build or execute one child-node creation against the live Mubu API.",
    "delete-node": "Build or execute one node deletion against the live Mubu API.",
    "update-text": "Build or execute one text update against the live Mubu API.",
}
LEGACY_COMMANDS = {}
LEGACY_COMMANDS.update(DISCOVER_COMMANDS)
LEGACY_COMMANDS.update(INSPECT_COMMANDS)
LEGACY_COMMANDS.update(MUTATE_COMMANDS)

REPL_HELP_TEMPLATE = """Interactive REPL for {program_name}

Builtins:
  help              Show this REPL help
  exit, quit        Leave the REPL
  use-doc <ref>     Set the current document reference for this REPL session
  use-node <id>     Set the current node reference for this REPL session
  use-daily [ref]   Resolve and set the current daily document
  current-doc       Show the current document reference
  current-node      Show the current node reference
  clear-doc         Clear the current document reference
  clear-node        Clear the current node reference
  status            Show the current session status
  history [limit]   Show recent command history from session state
  state-path        Show the session state file path

Examples:
  recent --limit 5 --json
  discover daily-current '<daily-folder-ref>'
  discover daily-current --json '<daily-folder-ref>'
  inspect daily-nodes '<daily-folder-ref>' --query '<anchor>' --json
  session use-doc '<doc-ref>'
  mutate create-child @doc --parent-node-id <node-id> --text 'scratch child' --json
  mutate delete-node @doc --node-id @node --json
  update-text '<doc-ref>' --node-id <node-id> --text 'new text' --json

If you prefer no-argument daily helpers, set MUBU_DAILY_FOLDER='<daily-folder-ref>'.
"""
REPL_COMMAND_HELP = REPL_HELP_TEMPLATE.format(program_name="the Mubu CLI")

__all__ = [
    "COMMAND_HISTORY_LIMIT",
    "COMPAT_PROGRAM_NAME",
    "CONTEXT_SETTINGS",
    "DISCOVER_COMMANDS",
    "INSPECT_COMMANDS",
    "Iterable",
    "LEGACY_COMMANDS",
    "MUTATE_COMMANDS",
    "PUBLIC_PROGRAM_NAME",
    "Path",
    "REPL_COMMAND_HELP",
    "REPL_HELP_TEMPLATE",
    "ReplSkin",
    "Sequence",
    "__version__",
    "annotations",
    "click",
    "json",
    "mubu_probe",
    "os",
    "shlex",
    "sys",
]
