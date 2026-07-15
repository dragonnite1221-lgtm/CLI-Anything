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


def _invocation_command(ctx, version):
    """Return a compact label for the current invocation."""
    argv = sys.argv[1:]
    if version:
        return "--version"
    if ctx.invoked_subcommand:
        return ctx.invoked_subcommand
    if any(arg in ("--help", "-h") for arg in argv):
        return "--help"
    if argv:
        return argv[0]
    return "root"


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version.")
@click.pass_context
def main(ctx, version):
    """cli-hub — Download and manage CLI-Anything harnesses and public CLIs."""
    # Resolve through the public facade at call time so existing
    # ``patch("cli_hub.cli.*")`` integrations continue to work after the split.
    from . import cli as facade

    facade.track_first_run()
    facade.track_visit(
        command=_invocation_command(ctx, version),
        detection=facade.detect_invocation_context(),
    )
    if version:
        click.echo(f"cli-hub {__version__}")
        return
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


__all__.extend(["_invocation_command", "main"])
