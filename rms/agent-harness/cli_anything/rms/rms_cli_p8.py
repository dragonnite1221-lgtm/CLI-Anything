# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403

# fmt: off
from .rms_cli_p1 import _get_session, _get_token, cli, handle_error, output  # noqa: E402,E501
from .rms_cli_p7 import smtp  # noqa: E402,E501
# fmt: on


@smtp.command("update")
@click.argument("config_id")
@click.option("--host", type=str, default=None)
@click.option("--port", type=int, default=None)
@click.option("--username", type=str, default=None)
@click.option("--password", type=str, default=None)
@click.option(
    "--password-stdin",
    is_flag=True,
    help="Read password from stdin (safer than --password)",
)
@handle_error
def smtp_update(config_id, host, port, username, password, password_stdin):
    """Update SMTP configuration."""
    import sys as _sys

    if password_stdin:
        password = _sys.stdin.readline().rstrip("\n")
        if not password:
            raise RuntimeError("No password provided on stdin")
    from cli_anything.rms.core.smtp import update_smtp_config

    data = {}
    if host:
        data["host"] = host
    if port:
        data["port"] = port
    if username:
        data["username"] = username
    if password:
        data["password"] = password
    if not data:
        raise click.UsageError("No fields to update")
    result = update_smtp_config(_get_token(), config_id, data)
    output(result, f"Updated SMTP config {config_id}")


@smtp.command("delete")
@click.argument("config_id")
@handle_error
def smtp_delete(config_id):
    """Delete SMTP configuration."""
    from cli_anything.rms.core.smtp import delete_smtp_config

    result = delete_smtp_config(_get_token(), config_id)
    output(result, f"Deleted SMTP config {config_id}")


@cli.group()
def auth():
    """Authentication management."""


@auth.command("test")
@handle_error
def auth_test():
    """Test API connectivity."""
    from cli_anything.rms.utils.rms_backend import api_get

    token = _get_token()
    result = api_get("/devices", params={"limit": 1}, token=token)
    if result.get("success"):
        output(
            {"status": "ok", "message": "API connection successful"},
            "RMS API test passed",
        )
    else:
        output(
            {"status": "error", "errors": result.get("errors", [])},
            "RMS API test failed",
        )


@auth.command("status")
@handle_error
def auth_status():
    """Show current auth info."""
    token = _get_token()
    if token:
        masked = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
        output({"authenticated": True, "token": masked}, f"Token: {masked}")
    else:
        output({"authenticated": False}, "No token configured")


@cli.group("config")
def config_group():
    """Local CLI configuration."""


@config_group.command("set")
@click.argument("key", type=click.Choice(["api_token", "default_limit"]))
@click.argument("value")
def config_set(key, value):
    """Set a configuration value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:10] + "..." if key == "api_token" and len(value) > 10 else value
    output({"key": key, "value": display}, f"Set {key} = {display}")


@config_group.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Get a configuration value (or show all)."""
    cfg = load_config()
    if key:
        val = cfg.get(key)
        if val:
            if key == "api_token" and len(val) > 10:
                val = val[:10] + "..."
            output({"key": key, "value": val}, f"{key} = {val}")
        else:
            output({"key": key, "value": None}, f"{key} is not set")
    else:
        masked = {}
        for k, v in cfg.items():
            masked[k] = (
                v[:10] + "..."
                if k == "api_token" and isinstance(v, str) and len(v) > 10
                else v
            )
        output(
            masked if masked else {},
            "Configuration" if masked else "No configuration set",
        )


@config_group.command("delete")
@click.argument("key")
def config_delete(key):
    """Delete a configuration value."""
    cfg = load_config()
    if key in cfg:
        del cfg[key]
        save_config(cfg)
        output({"deleted": key}, f"Deleted {key}")
    else:
        output({"error": f"{key} not found"}, f"{key} not found in config")


@config_group.command("path")
def config_path():
    """Show the config file path."""
    from cli_anything.rms.utils.rms_backend import CONFIG_FILE

    output({"path": str(CONFIG_FILE)}, f"Config file: {CONFIG_FILE}")


@cli.group("session")
def session_group():
    """Session management."""


@session_group.command("status")
@handle_error
def session_status():
    """Show session status."""
    s = _get_session()
    output(s.status(), "Session status")


@session_group.command("clear")
@handle_error
def session_clear():
    """Clear session."""
    s = _get_session()
    s.clear()
    output({"cleared": True}, "Session cleared")
