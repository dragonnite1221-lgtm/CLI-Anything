# ruff: noqa: F403, F405, E501
from .rms_cli_base import *  # noqa: F403

# fmt: off
from .rms_cli_p1 import _get_token, cli, handle_error, output  # noqa: E402,E501
from .rms_cli_p3 import tags  # noqa: E402,E501
# fmt: on


@tags.command("update")
@click.argument("tag_id")
@click.option("--name", type=str, default=None)
@handle_error
def tags_update(tag_id, name):
    """Update tag."""
    from cli_anything.rms.core.tags import update_tag

    data = {}
    if name:
        data["name"] = name
    if not data:
        raise click.UsageError("No fields to update")
    result = update_tag(_get_token(), tag_id, data)
    output(result, f"Updated tag {tag_id}")


@tags.command("delete")
@click.argument("tag_id")
@handle_error
def tags_delete(tag_id):
    """Delete tag."""
    from cli_anything.rms.core.tags import delete_tag

    result = delete_tag(_get_token(), tag_id)
    output(result, f"Deleted tag {tag_id}")


@cli.group()
def alerts():
    """Alert management."""


@alerts.command("list")
@click.option(
    "--device", "device_id", type=str, default=None, help="Filter by device ID"
)
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def alerts_list(device_id, limit, offset):
    """List alerts."""
    from cli_anything.rms.core.alerts import list_alerts

    result = list_alerts(_get_token(), device_id=device_id, limit=limit, offset=offset)
    output(result, "Alerts")


@alerts.command("get")
@click.argument("alert_id")
@handle_error
def alerts_get(alert_id):
    """Get alert details."""
    from cli_anything.rms.core.alerts import get_alert

    result = get_alert(_get_token(), alert_id)
    output(result, f"Alert {alert_id}")


@alerts.command("delete")
@click.argument("alert_id")
@handle_error
def alerts_delete(alert_id):
    """Delete alert."""
    from cli_anything.rms.core.alerts import delete_alert

    result = delete_alert(_get_token(), alert_id)
    output(result, f"Deleted alert {alert_id}")


@alerts.group("configs")
def alert_configs():
    """Alert configuration management."""


@alert_configs.command("list")
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def alert_configs_list(limit, offset):
    """List alert configurations."""
    from cli_anything.rms.core.alerts import list_alert_configs

    result = list_alert_configs(_get_token(), limit=limit, offset=offset)
    output(result, "Alert configurations")


@alert_configs.command("get")
@click.argument("config_id")
@handle_error
def alert_configs_get(config_id):
    """Get alert configuration."""
    from cli_anything.rms.core.alerts import get_alert_config

    result = get_alert_config(_get_token(), config_id)
    output(result, f"Alert config {config_id}")


@alert_configs.command("create")
@click.option("--data", "data_json", required=True, help="JSON configuration data")
@handle_error
def alert_configs_create(data_json):
    """Create alert configuration."""
    from cli_anything.rms.core.alerts import create_alert_config

    data = json.loads(data_json)
    result = create_alert_config(_get_token(), data)
    output(result, "Created alert configuration")


@alert_configs.command("update")
@click.argument("config_id")
@click.option("--data", "data_json", required=True, help="JSON configuration data")
@handle_error
def alert_configs_update(config_id, data_json):
    """Update alert configuration."""
    from cli_anything.rms.core.alerts import update_alert_config

    data = json.loads(data_json)
    result = update_alert_config(_get_token(), config_id, data)
    output(result, f"Updated alert config {config_id}")


@alert_configs.command("delete")
@click.argument("config_id")
@handle_error
def alert_configs_delete(config_id):
    """Delete alert configuration."""
    from cli_anything.rms.core.alerts import delete_alert_config

    result = delete_alert_config(_get_token(), config_id)
    output(result, f"Deleted alert config {config_id}")


@cli.group()
def configs():
    """Device configuration management."""


@configs.command("list")
@click.option("--device", "device_id", type=str, default=None)
@click.option("--limit", type=int, default=25)
@click.option("--offset", type=int, default=0)
@handle_error
def configs_list(device_id, limit, offset):
    """List device configurations."""
    from cli_anything.rms.core.configs import list_configs

    result = list_configs(_get_token(), device_id=device_id, limit=limit, offset=offset)
    output(result, "Device configurations")


@configs.command("get")
@click.argument("config_id")
@handle_error
def configs_get(config_id):
    """Get device configuration."""
    from cli_anything.rms.core.configs import get_config

    result = get_config(_get_token(), config_id)
    output(result, f"Config {config_id}")


@configs.command("update")
@click.argument("config_id")
@click.option("--data", "data_json", required=True, help="JSON configuration data")
@handle_error
def configs_update(config_id, data_json):
    """Update device configuration."""
    from cli_anything.rms.core.configs import update_config

    data = json.loads(data_json)
    result = update_config(_get_token(), config_id, data)
    output(result, f"Updated config {config_id}")
