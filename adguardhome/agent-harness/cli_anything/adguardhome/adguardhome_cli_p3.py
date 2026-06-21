# ruff: noqa: F403, F405, E501
from .adguardhome_cli_base import *  # noqa: F403

# fmt: off
from .adguardhome_cli_p1 import cli, make_client, output  # noqa: E402,E501
from .adguardhome_cli_p2 import filter_  # noqa: E402,E501
# fmt: on


@filter_.command("enable")
@click.option("--url", required=True)
@click.option("--name", required=True)
@click.option("--whitelist", is_flag=True, default=False)
@click.pass_context
def filter_enable(ctx: click.Context, url: str, name: str, whitelist: bool):
    """Enable a filter subscription."""
    client = make_client(ctx)
    data = filtering_core.set_filter_url(
        client, url=url, name=name, enabled=True, whitelist=whitelist
    )
    output(data or {"enabled": True, "url": url}, ctx.obj["as_json"])


@filter_.command("disable")
@click.option("--url", required=True)
@click.option("--name", required=True)
@click.option("--whitelist", is_flag=True, default=False)
@click.pass_context
def filter_disable(ctx: click.Context, url: str, name: str, whitelist: bool):
    """Disable a filter subscription."""
    client = make_client(ctx)
    data = filtering_core.set_filter_url(
        client, url=url, name=name, enabled=False, whitelist=whitelist
    )
    output(data or {"disabled": True, "url": url}, ctx.obj["as_json"])


@filter_.command("refresh")
@click.option("--whitelist", is_flag=True, default=False)
@click.pass_context
def filter_refresh(ctx: click.Context, whitelist: bool):
    """Trigger manual update of all filters."""
    client = make_client(ctx)
    data = filtering_core.refresh(client, whitelist=whitelist)
    output(data or {"refreshed": True}, ctx.obj["as_json"])


@cli.group()
@click.pass_context
def blocking(ctx: click.Context):
    """Parental, safebrowsing, safesearch controls."""


@blocking.group()
def parental():
    """Parental control."""


@parental.command("status")
@click.pass_context
def parental_status(ctx: click.Context):
    client = make_client(ctx)
    output(blocking_core.parental_status(client), ctx.obj["as_json"])


@parental.command("enable")
@click.pass_context
def parental_enable(ctx: click.Context):
    client = make_client(ctx)
    output(
        blocking_core.parental_enable(client) or {"enabled": True}, ctx.obj["as_json"]
    )


@parental.command("disable")
@click.pass_context
def parental_disable(ctx: click.Context):
    client = make_client(ctx)
    output(
        blocking_core.parental_disable(client) or {"disabled": True}, ctx.obj["as_json"]
    )


@blocking.group()
def safebrowsing():
    """Safe browsing control."""


@safebrowsing.command("status")
@click.pass_context
def safebrowsing_status(ctx: click.Context):
    client = make_client(ctx)
    output(blocking_core.safebrowsing_status(client), ctx.obj["as_json"])


@safebrowsing.command("enable")
@click.pass_context
def safebrowsing_enable(ctx: click.Context):
    client = make_client(ctx)
    output(
        blocking_core.safebrowsing_enable(client) or {"enabled": True},
        ctx.obj["as_json"],
    )


@safebrowsing.command("disable")
@click.pass_context
def safebrowsing_disable(ctx: click.Context):
    client = make_client(ctx)
    output(
        blocking_core.safebrowsing_disable(client) or {"disabled": True},
        ctx.obj["as_json"],
    )


@blocking.group()
def safesearch():
    """Safe search control."""


@safesearch.command("status")
@click.pass_context
def safesearch_status(ctx: click.Context):
    client = make_client(ctx)
    output(blocking_core.safesearch_status(client), ctx.obj["as_json"])


@safesearch.command("enable")
@click.pass_context
def safesearch_enable(ctx: click.Context):
    client = make_client(ctx)
    output(
        blocking_core.safesearch_enable(client) or {"enabled": True}, ctx.obj["as_json"]
    )


@safesearch.command("disable")
@click.pass_context
def safesearch_disable(ctx: click.Context):
    client = make_client(ctx)
    output(
        blocking_core.safesearch_disable(client) or {"disabled": True},
        ctx.obj["as_json"],
    )


@cli.group("blocked-services")
@click.pass_context
def blocked_services(ctx: click.Context):
    """Blocked service categories."""


@blocked_services.command("list")
@click.pass_context
def blocked_services_list(ctx: click.Context):
    client = make_client(ctx)
    output(blocking_core.blocked_services_get(client), ctx.obj["as_json"])


@blocked_services.command("set")
@click.argument("services", nargs=-1, required=True)
@click.pass_context
def blocked_services_set(ctx: click.Context, services: tuple):
    client = make_client(ctx)
    output(
        blocking_core.blocked_services_set(client, list(services))
        or {"set": list(services)},
        ctx.obj["as_json"],
    )


@cli.group("clients")
@click.pass_context
def clients_(ctx: click.Context):
    """Known client management."""
