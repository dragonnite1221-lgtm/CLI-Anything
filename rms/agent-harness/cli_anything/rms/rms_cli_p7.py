# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403

# fmt: off
from .rms_cli_p1 import _get_token, cli, handle_error, output  # noqa: E402,E501
from .rms_cli_p6 import hotspots  # noqa: E402,E501
# fmt: on


@hotspots.command("list")
@click.option("--device", "device_id", type=str, default=None)
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def hotspots_list(device_id, limit, offset):
    """List hotspots."""
    from cli_anything.rms.core.hotspots import list_hotspots

    result = list_hotspots(
        _get_token(), device_id=device_id, limit=limit, offset=offset
    )
    output(result, "Hotspots")


@hotspots.command("get")
@click.argument("hotspot_id")
@handle_error
def hotspots_get(hotspot_id):
    """Get hotspot details."""
    from cli_anything.rms.core.hotspots import get_hotspot

    result = get_hotspot(_get_token(), hotspot_id)
    output(result, f"Hotspot {hotspot_id}")


@hotspots.command("create")
@click.option("--device", "device_id", required=True, help="Device ID")
@click.option("--name", required=True)
@handle_error
def hotspots_create(device_id, name):
    """Create hotspot."""
    from cli_anything.rms.core.hotspots import create_hotspot

    result = create_hotspot(_get_token(), {"device_id": device_id, "name": name})
    output(result, f"Created hotspot: {name}")


@hotspots.command("update")
@click.argument("hotspot_id")
@click.option("--name", type=str, default=None)
@handle_error
def hotspots_update(hotspot_id, name):
    """Update hotspot."""
    from cli_anything.rms.core.hotspots import update_hotspot

    data = {}
    if name:
        data["name"] = name
    if not data:
        raise click.UsageError("No fields to update")
    result = update_hotspot(_get_token(), hotspot_id, data)
    output(result, f"Updated hotspot {hotspot_id}")


@hotspots.command("delete")
@click.argument("hotspot_id")
@handle_error
def hotspots_delete(hotspot_id):
    """Delete hotspot."""
    from cli_anything.rms.core.hotspots import delete_hotspot

    result = delete_hotspot(_get_token(), hotspot_id)
    output(result, f"Deleted hotspot {hotspot_id}")


@cli.group()
def passwords():
    """Device password management."""


@passwords.command("get")
@click.argument("device_id")
@handle_error
def passwords_get(device_id):
    """Get device password."""
    from cli_anything.rms.core.passwords import get_password

    result = get_password(_get_token(), device_id)
    output(result, f"Password for device {device_id}")


@passwords.command("update")
@click.argument("device_id")
@click.option("--password", default=None, help="New password")
@click.option(
    "--password-stdin",
    is_flag=True,
    help="Read password from stdin (safer than --password)",
)
@handle_error
def passwords_update(device_id, password, password_stdin):
    """Update device password."""
    import sys

    if password_stdin:
        password = sys.stdin.readline().rstrip("\n")
        if not password:
            raise RuntimeError("No password provided on stdin")
    if not password:
        raise RuntimeError("Provide --password or --password-stdin")
    from cli_anything.rms.core.passwords import update_password

    result = update_password(_get_token(), device_id, {"password": password})
    output(result, f"Updated password for device {device_id}")


@cli.group()
def smtp():
    """SMTP configuration management."""


@smtp.command("list")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def smtp_list(limit, offset):
    """List SMTP configurations."""
    from cli_anything.rms.core.smtp import list_smtp_configs

    result = list_smtp_configs(_get_token(), limit=limit, offset=offset)
    output(result, "SMTP configurations")


@smtp.command("get")
@click.argument("config_id")
@handle_error
def smtp_get(config_id):
    """Get SMTP configuration."""
    from cli_anything.rms.core.smtp import get_smtp_config

    result = get_smtp_config(_get_token(), config_id)
    output(result, f"SMTP config {config_id}")


@smtp.command("create")
@click.option("--host", required=True)
@click.option("--port", type=int, default=None)
@click.option("--username", type=str, default=None)
@click.option("--password", type=str, default=None)
@click.option(
    "--password-stdin",
    is_flag=True,
    help="Read password from stdin (safer than --password)",
)
@handle_error
def smtp_create(host, port, username, password, password_stdin):
    """Create SMTP configuration."""
    import sys as _sys

    if password_stdin:
        password = _sys.stdin.readline().rstrip("\n")
        if not password:
            raise RuntimeError("No password provided on stdin")
    from cli_anything.rms.core.smtp import create_smtp_config

    data = {"host": host}
    if port:
        data["port"] = port
    if username:
        data["username"] = username
    if password:
        data["password"] = password
    result = create_smtp_config(_get_token(), data)
    output(result, f"Created SMTP config: {host}")
