# ruff: noqa: F403, F405, E501
from .wiremock_cli_base import *  # noqa: F403

# fmt: off
from .wiremock_cli_p1 import cli  # noqa: E402,E501
from .wiremock_cli_p3 import record  # noqa: E402,E501
# fmt: on


@record.command("start")
@click.argument("target_url")
@click.option("--match-header", multiple=True, help="Headers to capture (can repeat)")
@click.pass_context
def record_start(ctx, target_url, match_header):
    """Start recording traffic proxied to TARGET_URL."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = RecordingManager(client).start(target_url, list(match_header) or None)
        if json_mode:
            print_json(data)
        else:
            success(f"Recording started → {target_url}", data)
    except Exception as e:
        error(str(e), json_mode)


@record.command("stop")
@click.pass_context
def record_stop(ctx):
    """Stop recording and return captured stubs."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = RecordingManager(client).stop()
        if json_mode:
            print_json(data)
        else:
            count = len(data.get("mappings", []))
            success(f"Recording stopped. {count} stubs captured.", data)
    except Exception as e:
        error(str(e), json_mode)


@record.command("status")
@click.pass_context
def record_status(ctx):
    """Check recording status."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = RecordingManager(client).status()
        if json_mode:
            print_json(data)
        else:
            click.echo(f"Status: {data.get('status', 'unknown')}")
    except Exception as e:
        error(str(e), json_mode)


@record.command("snapshot")
@click.pass_context
def record_snapshot(ctx):
    """Take a snapshot of current traffic as stubs."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = RecordingManager(client).snapshot()
        if json_mode:
            print_json(data)
        else:
            count = len(data.get("mappings", []))
            success(f"Snapshot: {count} stubs captured", data)
    except Exception as e:
        error(str(e), json_mode)


@cli.group()
def settings():
    """Manage global WireMock settings."""


@settings.command("get")
@click.pass_context
def settings_get(ctx):
    """Get current global settings."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = SettingsManager(client).get()
        print_json(data)
    except Exception as e:
        error(str(e), json_mode)


@settings.command("version")
@click.pass_context
def settings_version(ctx):
    """Show WireMock server version."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = SettingsManager(client).get_version()
        if json_mode:
            print_json(data)
        else:
            click.echo(f"WireMock version: {data.get('version', 'unknown')}")
    except Exception as e:
        error(str(e), json_mode)


@cli.command("reset")
@click.pass_context
def reset_all(ctx):
    """Full reset: stubs + requests + scenarios."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        r = client.post("/reset")
        r.raise_for_status()
        if json_mode:
            print_json({"status": "ok"})
        else:
            success("Full reset complete")
    except Exception as e:
        error(str(e), json_mode)


@cli.command("shutdown")
@click.confirmation_option(prompt="Shutdown the WireMock server?")
@click.pass_context
def shutdown(ctx):
    """Shutdown the WireMock server."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        r = client.post("/shutdown")
        r.raise_for_status()
        if json_mode:
            print_json({"status": "ok", "message": "Shutdown signal sent"})
        else:
            click.echo("Shutdown signal sent")
    except (ConnectionError, requests.exceptions.ConnectionError):
        # Server drops connection on successful shutdown — this is expected
        if json_mode:
            print_json({"status": "ok", "message": "Shutdown signal sent"})
        else:
            click.echo("Shutdown signal sent (server connection closed)")
    except Exception as e:
        error(str(e), json_mode)
