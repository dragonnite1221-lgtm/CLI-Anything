# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403

# fmt: off
from .rms_cli_p1 import _get_session, _get_token, cli, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command("repl", hidden=True)
@handle_error
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.rms.utils.repl_skin import ReplSkin

    skin = ReplSkin("rms", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "devices list [--status S]": "List devices",
        "devices get <id>": "Get device details",
        "companies list": "List companies",
        "users list": "List users",
        "tags list": "List tags",
        "alerts list [--device ID]": "List alerts",
        "configs list [--device ID]": "List device configurations",
        "remote-access list": "List remote access sessions",
        "logs list [--device ID]": "List device logs",
        "location get <device-id>": "Get device location",
        "credits list": "List credits",
        "files list": "List files",
        "reports list": "List reports",
        "hotspots list": "List hotspots",
        "passwords get <device-id>": "Get device password",
        "smtp list": "List SMTP configs",
        "auth test": "Test API connectivity",
        "config set <key> <val>": "Set configuration",
        "config get [key]": "Show configuration",
        "session status": "Show session status",
        "help": "Show this help",
        "quit / exit": "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="rms")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line == "help":
            skin.help(commands)
            continue

        try:
            parts = shlex.split(line)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            cli.main(parts, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


@cli.group()
def devices():
    """Device management."""


@devices.command("list")
@click.option("--status", type=click.Choice(["online", "offline"]), default=None)
@click.option("--tag", multiple=True, help="Filter by tag(s)")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@click.option("--sort", type=str, default=None, help="Sort field (prefix - for desc)")
@handle_error
def devices_list(status, tag, limit, offset, sort):
    """List devices."""
    from cli_anything.rms.core.devices import list_devices

    result = list_devices(
        _get_token(),
        status=status,
        tag=list(tag) if tag else None,
        limit=limit,
        offset=offset,
        sort=sort,
    )
    output(result, f"Devices ({result.get('meta', {}).get('total', '?')} total)")


@devices.command("get")
@click.argument("device_id")
@handle_error
def devices_get(device_id):
    """Get device details."""
    from cli_anything.rms.core.devices import get_device

    result = get_device(_get_token(), device_id)
    _get_session().set_last_device(device_id)
    output(result, f"Device {device_id}")


@devices.command("update")
@click.argument("device_id")
@click.option("--name", type=str, default=None)
@click.option("--tag", multiple=True)
@handle_error
def devices_update(device_id, name, tag):
    """Update device."""
    from cli_anything.rms.core.devices import update_device

    data = {}
    if name:
        data["name"] = name
    if tag:
        data["tags"] = list(tag)
    result = update_device(_get_token(), device_id, data)
    output(result, f"Updated device {device_id}")


@devices.command("delete")
@click.argument("device_id")
@handle_error
def devices_delete(device_id):
    """Delete device."""
    from cli_anything.rms.core.devices import delete_device

    result = delete_device(_get_token(), device_id)
    output(result, f"Deleted device {device_id}")


@cli.group()
def companies():
    """Company management."""


@companies.command("list")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def companies_list(limit, offset):
    """List companies."""
    from cli_anything.rms.core.companies import list_companies

    result = list_companies(_get_token(), limit=limit, offset=offset)
    output(result, "Companies")
