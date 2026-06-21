# ruff: noqa: F403, F405, E501
"""Tests for cli-hub — registry, installer, analytics, and CLI."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import click.testing
import requests
from cli_hub import __version__
from cli_hub.registry import fetch_registry, fetch_all_clis, get_cli, search_clis, list_categories
from cli_hub.preview import (
    inspect_bundle,
    inspect_session,
    open_in_browser,
    render_html,
    render_inspect_text,
    render_live_html,
    render_session_text,
)
from cli_hub.installer import (
    install_cli,
    uninstall_cli,
    get_installed,
    _load_installed,
    _save_installed,
    _run_command,
    _install_strategy,
    _UV_INSTALL_HINT,
)
from cli_hub.analytics import _is_enabled, track_event, track_install, track_uninstall as analytics_track_uninstall, track_visit, track_first_run, _detect_is_agent, detect_invocation_context
from cli_hub.cli import main


SAMPLE_REGISTRY = {
    "meta": {"repo": "https://github.com/HKUDS/CLI-Anything", "description": "test"},
    "clis": [
        {
            "name": "gimp",
            "display_name": "GIMP",
            "version": "1.0.0",
            "description": "Image editing via GIMP",
            "requires": "gimp",
            "homepage": "https://gimp.org",
            "install_cmd": "pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=gimp/agent-harness",
            "entry_point": "cli-anything-gimp",
            "skill_md": "skills/cli-anything-gimp/SKILL.md",
            "category": "image",
            "contributor": "test-user",
            "contributor_url": "https://github.com/test-user",
        },
        {
            "name": "blender",
            "display_name": "Blender",
            "version": "1.0.0",
            "description": "3D modeling via Blender",
            "requires": "blender",
            "homepage": "https://blender.org",
            "install_cmd": "pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=blender/agent-harness",
            "entry_point": "cli-anything-blender",
            "skill_md": None,
            "category": "3d",
            "contributor": "test-user",
            "contributor_url": "https://github.com/test-user",
        },
        {
            "name": "audacity",
            "display_name": "Audacity",
            "version": "1.0.0",
            "description": "Audio editing and processing via sox",
            "requires": "sox",
            "homepage": "https://audacityteam.org",
            "install_cmd": "pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=audacity/agent-harness",
            "entry_point": "cli-anything-audacity",
            "skill_md": None,
            "category": "audio",
            "contributor": "test-user",
            "contributor_url": "https://github.com/test-user",
        },
    ],
}


GENERATE_VEO_CLI = {
    "name": "generate-veo-video",
    "display_name": "Generate Veo Video",
    "version": "0.2.5",
    "description": "CLI for generating videos with Google Veo 3.1",
    "category": "ai",
    "entry_point": "generate-veo",
    "_source": "public",
    "package_manager": "uv",
    "install_cmd": "uv tool install git+https://github.com/charles-forsyth/generate-veo-video.git",
    "uninstall_cmd": "uv tool uninstall generate-veo-video",
    "update_cmd": "uv tool upgrade generate-veo-video",
}


JIMENG_CLI = {
    "name": "jimeng",
    "display_name": "Jimeng / Dreamina CLI",
    "version": "latest",
    "description": "ByteDance AI image and video generation CLI",
    "category": "ai",
    "entry_point": "dreamina",
    "_source": "public",
    "install_strategy": "command",
    "package_manager": "script",
    "install_cmd": "curl -s https://jimeng.jianying.com/cli | bash",
}


# fmt: off
__all__ = ['GENERATE_VEO_CLI', 'JIMENG_CLI', 'MagicMock', 'Path', 'SAMPLE_REGISTRY', '_UV_INSTALL_HINT', '__version__', '_detect_is_agent', '_install_strategy', '_is_enabled', '_load_installed', '_run_command', '_save_installed', 'analytics_track_uninstall', 'click', 'detect_invocation_context', 'fetch_all_clis', 'fetch_registry', 'get_cli', 'get_installed', 'inspect_bundle', 'inspect_session', 'install_cli', 'json', 'list_categories', 'main', 'open_in_browser', 'os', 'patch', 'pytest', 'render_html', 'render_inspect_text', 'render_live_html', 'render_session_text', 'requests', 'search_clis', 'tempfile', 'track_event', 'track_first_run', 'track_install', 'track_visit', 'uninstall_cli']  # noqa: E501
# fmt: on
