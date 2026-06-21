# ruff: noqa: E501
"""cli-hub — CLI entry point."""

import os
import shutil
import sys
import json as json_mod
from pathlib import Path

import click

from cli_hub import __version__
from cli_hub.registry import fetch_all_clis, get_cli, search_clis, list_categories
from cli_hub.installer import install_cli, uninstall_cli, get_installed, update_cli
from cli_hub.analytics import (
    detect_invocation_context,
    track_first_run,
    track_install,
    track_launch,
    track_uninstall,
    track_visit,
)
from cli_hub.preview import (
    inspect_bundle,
    inspect_session,
    is_live_session_ref,
    load_session,
    open_in_browser,
    render_html,
    render_inspect_text,
    render_live_html,
    render_session_text,
    start_static_server,
)

__all__ = [
    "Path",
    "__version__",
    "click",
    "detect_invocation_context",
    "fetch_all_clis",
    "get_cli",
    "get_installed",
    "inspect_bundle",
    "inspect_session",
    "install_cli",
    "is_live_session_ref",
    "json_mod",
    "list_categories",
    "load_session",
    "open_in_browser",
    "os",
    "render_html",
    "render_inspect_text",
    "render_live_html",
    "render_session_text",
    "search_clis",
    "shutil",
    "start_static_server",
    "sys",
    "track_first_run",
    "track_install",
    "track_launch",
    "track_uninstall",
    "track_visit",
    "uninstall_cli",
    "update_cli",
]
