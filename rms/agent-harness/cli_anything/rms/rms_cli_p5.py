# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403

# fmt: off
from .rms_cli_p1 import _get_token, cli, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.group("remote-access")
def remote_access():
    """Remote access session management."""


@remote_access.command("list")
@click.option("--device", "device_id", type=str, default=None)
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def remote_access_list(device_id, limit, offset):
    """List remote access sessions."""
    from cli_anything.rms.core.remote_access import list_sessions

    result = list_sessions(
        _get_token(), device_id=device_id, limit=limit, offset=offset
    )
    output(result, "Remote access sessions")


@remote_access.command("get")
@click.argument("session_id")
@handle_error
def remote_access_get(session_id):
    """Get remote access session."""
    from cli_anything.rms.core.remote_access import get_session

    result = get_session(_get_token(), session_id)
    output(result, f"Session {session_id}")


@remote_access.command("create")
@click.option("--device", "device_id", required=True, help="Device ID")
@click.option("--protocol", type=str, default=None)
@click.option("--port", type=int, default=None)
@handle_error
def remote_access_create(device_id, protocol, port):
    """Create remote access session."""
    from cli_anything.rms.core.remote_access import create_session

    data = {"device_id": device_id}
    if protocol:
        data["protocol"] = protocol
    if port:
        data["port"] = port
    result = create_session(_get_token(), data)
    output(result, "Created remote access session")


@remote_access.command("delete")
@click.argument("session_id")
@handle_error
def remote_access_delete(session_id):
    """Delete remote access session."""
    from cli_anything.rms.core.remote_access import delete_session

    result = delete_session(_get_token(), session_id)
    output(result, f"Deleted session {session_id}")


@cli.group()
def logs():
    """Device log management."""


@logs.command("list")
@click.option("--device", "device_id", type=str, default=None)
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def logs_list(device_id, limit, offset):
    """List device logs."""
    from cli_anything.rms.core.logs import list_logs

    result = list_logs(_get_token(), device_id=device_id, limit=limit, offset=offset)
    output(result, "Device logs")


@logs.command("get")
@click.argument("log_id")
@handle_error
def logs_get(log_id):
    """Get log details."""
    from cli_anything.rms.core.logs import get_log

    result = get_log(_get_token(), log_id)
    output(result, f"Log {log_id}")


@logs.command("delete")
@click.argument("log_id")
@handle_error
def logs_delete(log_id):
    """Delete log."""
    from cli_anything.rms.core.logs import delete_log

    result = delete_log(_get_token(), log_id)
    output(result, f"Deleted log {log_id}")


@cli.group()
def location():
    """Device location."""


@location.command("get")
@click.argument("device_id")
@handle_error
def location_get(device_id):
    """Get device location."""
    from cli_anything.rms.core.location import get_location

    result = get_location(_get_token(), device_id)
    output(result, f"Location for device {device_id}")


@location.command("history")
@click.argument("device_id")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def location_history(device_id, limit, offset):
    """Get device location history."""
    from cli_anything.rms.core.location import list_location_history

    result = list_location_history(_get_token(), device_id, limit=limit, offset=offset)
    output(result, f"Location history for device {device_id}")


@cli.group()
def credits():
    """Credit management."""


@credits.command("list")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def credits_list(limit, offset):
    """List credits."""
    from cli_anything.rms.core.credits import list_credits

    result = list_credits(_get_token(), limit=limit, offset=offset)
    output(result, "Credits")


@credits.command("transfer")
@click.option("--code", required=True, help="Transfer code")
@handle_error
def credits_transfer(code):
    """Transfer credits using a code."""
    from cli_anything.rms.core.credits import transfer_credits

    result = transfer_credits(_get_token(), {"code": code})
    output(result, "Credit transfer")


@credits.command("codes")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def credits_codes(limit, offset):
    """List credit transfer codes."""
    from cli_anything.rms.core.credits import list_transfer_codes

    result = list_transfer_codes(_get_token(), limit=limit, offset=offset)
    output(result, "Transfer codes")


@cli.group()
def files():
    """File management."""
