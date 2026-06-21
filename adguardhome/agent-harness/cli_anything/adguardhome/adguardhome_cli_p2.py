# ruff: noqa: F403, F405, E501
from .adguardhome_cli_base import *  # noqa: F403

# fmt: off
from .adguardhome_cli_p1 import cli, config, make_client, output  # noqa: E402,E501
# fmt: on


@config.command("show")
@click.pass_context
def config_show(ctx: click.Context):
    """Show current connection settings."""
    obj = ctx.obj
    data = {
        "host": obj["host"],
        "port": obj["port"],
        "username": obj["username"],
        "password": "***" if obj["password"] else "",
    }
    output(data, obj["as_json"])


@config.command("save")
@click.pass_context
def config_save(ctx: click.Context):
    """Save connection settings to config file."""
    obj = ctx.obj
    path = project.save_config(
        host=obj["host"],
        port=obj["port"],
        username=obj["username"],
        password=obj["password"],
        https=obj.get("use_https", False),
        config_path=obj.get("config_path"),
    )
    result = {"saved": str(path)}
    output(result, obj["as_json"])


@config.command("test")
@click.pass_context
def config_test(ctx: click.Context):
    """Test connection to AdGuardHome."""
    client = make_client(ctx)
    data = server_core.get_status(client)
    result = {
        "connected": True,
        "host": ctx.obj["host"],
        "port": ctx.obj["port"],
        **data,
    }
    output(result, ctx.obj["as_json"])


@cli.group("server")
@click.pass_context
def server_(ctx: click.Context):
    """Server management."""


@server_.command("status")
@click.pass_context
def server_status(ctx: click.Context):
    """Show server status."""
    client = make_client(ctx)
    data = server_core.get_status(client)
    output(data, ctx.obj["as_json"])


@server_.command("version")
@click.pass_context
def server_version(ctx: click.Context):
    """Show AdGuardHome version."""
    client = make_client(ctx)
    data = server_core.get_version(client)
    output(data, ctx.obj["as_json"])


@server_.command("restart")
@click.pass_context
def server_restart(ctx: click.Context):
    """Restart AdGuardHome."""
    client = make_client(ctx)
    data = server_core.restart(client)
    output(data or {"restarted": True}, ctx.obj["as_json"])


@cli.group("filter")
@click.pass_context
def filter_(ctx: click.Context):
    """Filtering rules management."""


@filter_.command("list")
@click.pass_context
def filter_list(ctx: click.Context):
    """List all filter subscriptions."""
    client = make_client(ctx)
    data = filtering_core.get_status(client)
    output(data, ctx.obj["as_json"])


@filter_.command("status")
@click.pass_context
def filter_status(ctx: click.Context):
    """Show filtering enabled/disabled state."""
    client = make_client(ctx)
    data = filtering_core.get_status(client)
    result = {
        "enabled": data.get("enabled"),
        "filters_count": len(data.get("filters", [])),
    }
    output(result, ctx.obj["as_json"])


@filter_.command("toggle")
@click.argument("state", type=click.Choice(["on", "off"]))
@click.pass_context
def filter_toggle(ctx: click.Context, state: str):
    """Enable or disable filtering globally."""
    client = make_client(ctx)
    data = filtering_core.set_enabled(client, state == "on")
    output(data or {"filtering_enabled": state == "on"}, ctx.obj["as_json"])


@filter_.command("add")
@click.option("--url", required=True, help="Filter list URL")
@click.option("--name", required=True, help="Filter name")
@click.option("--whitelist", is_flag=True, default=False)
@click.pass_context
def filter_add(ctx: click.Context, url: str, name: str, whitelist: bool):
    """Add a new filter subscription."""
    client = make_client(ctx)
    data = filtering_core.add_filter(client, url=url, name=name, whitelist=whitelist)
    output(data or {"added": True, "url": url, "name": name}, ctx.obj["as_json"])


@filter_.command("remove")
@click.option("--url", required=True, help="Filter list URL to remove")
@click.option("--whitelist", is_flag=True, default=False)
@click.pass_context
def filter_remove(ctx: click.Context, url: str, whitelist: bool):
    """Remove a filter subscription."""
    client = make_client(ctx)
    data = filtering_core.remove_filter(client, url=url, whitelist=whitelist)
    output(data or {"removed": True, "url": url}, ctx.obj["as_json"])
