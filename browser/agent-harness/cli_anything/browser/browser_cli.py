#!/usr/bin/env python3
"""Browser CLI entry point for DOMShell-backed browser automation."""

from __future__ import annotations

import json
import sys
from typing import Optional

import click

from cli_anything.browser.browser_cli_act import register_act_commands
from cli_anything.browser.browser_cli_fs import register_fs_commands
from cli_anything.browser.browser_cli_page import register_page_commands
from cli_anything.browser.browser_cli_repl import register_repl_command
from cli_anything.browser.browser_cli_secure import register_secure_commands
from cli_anything.browser.browser_cli_session import register_session_commands
from cli_anything.browser.core.session import Session
from cli_anything.browser.utils import domshell_backend as backend


_session: Optional[Session] = None
_json_output = False
_repl_mode = False
_availability_cached: Optional[tuple[bool, str]] = None


def get_session() -> Session:
    """Return the process-local browser session."""

    global _session
    if _session is None:
        _session = Session()
    return _session


def output(data, message: str = ""):
    """Render command data in the selected human or JSON format."""

    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(data: dict, indent: int = 0):
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            click.echo(f"{prefix}{key}:")
            _print_dict(value, indent + 1)
        elif isinstance(value, list):
            click.echo(f"{prefix}{key}:")
            _print_list(value, indent + 1)
        else:
            click.echo(f"{prefix}{key}: {value}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for index, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{index}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    """Keep command errors compatible with JSON and REPL output modes."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as error:
            _report_error(error, "runtime_error")
        except (ValueError, IndexError) as error:
            _report_error(error, type(error).__name__)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def _report_error(error: Exception, error_type: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": str(error), "type": error_type}))
    else:
        click.echo(f"Error: {error}", err=True)
    if not _repl_mode:
        sys.exit(1)


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option("--daemon", "use_daemon", is_flag=True, help="Use persistent daemon mode")
@click.pass_context
def cli(ctx, use_json, use_daemon):
    """Browser CLI — filesystem-first browser automation via DOMShell."""

    global _json_output, _session, _availability_cached
    _json_output = use_json
    if "--help" not in sys.argv and "--version" not in sys.argv and ctx.invoked_subcommand != "secure":
        if _availability_cached is None:
            _availability_cached = backend.is_available()
        available, message = _availability_cached
        if not available:
            _report_dependency_error(message)
    _session = get_session()
    if use_daemon and ctx.invoked_subcommand != "secure":
        _enable_daemon_mode()
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


def _report_dependency_error(message: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": message, "type": "dependency_error"}))
    else:
        click.echo(f"Error: {message}", err=True)
        click.echo("\nSee `cli-anything-browser secure status` for secure-runtime setup.")
    sys.exit(1)


def _enable_daemon_mode() -> None:
    try:
        backend.start_daemon()
        get_session().enable_daemon()
        if not _json_output:
            click.echo("Daemon mode: persistent MCP connection active")
    except RuntimeError as error:
        if _json_output:
            click.echo(json.dumps({"error": str(error), "type": "daemon_error"}))
        else:
            click.echo(f"Daemon start failed: {error}", err=True)
            click.echo("Falling back to per-command mode", err=True)


def _set_repl_mode(enabled: bool) -> None:
    global _repl_mode
    _repl_mode = enabled


register_page_commands(cli, get_session, output, handle_error)
register_fs_commands(cli, get_session, output, handle_error, lambda: _json_output)
register_act_commands(cli, get_session, output, handle_error, backend)
register_session_commands(cli, get_session, output, handle_error, backend)
register_secure_commands(cli, output, handle_error, backend)
repl = register_repl_command(cli, get_session, lambda: _json_output, _set_repl_mode)


def main():
    """Run the browser CLI."""

    cli()


if __name__ == "__main__":
    main()
