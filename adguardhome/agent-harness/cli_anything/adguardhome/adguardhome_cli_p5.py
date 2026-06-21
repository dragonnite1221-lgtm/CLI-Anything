# ruff: noqa: F403, F405, E501
from .adguardhome_cli_base import *  # noqa: F403

# fmt: off
from .adguardhome_cli_p1 import cli, make_client, output  # noqa: E402,E501
# fmt: on


@cli.group("dhcp")
@click.pass_context
def dhcp_(ctx: click.Context):
    """DHCP server management."""


@dhcp_.command("status")
@click.pass_context
def dhcp_status(ctx: click.Context):
    client = make_client(ctx)
    output(dhcp_core.get_status(client), ctx.obj["as_json"])


@dhcp_.command("leases")
@click.pass_context
def dhcp_leases(ctx: click.Context):
    client = make_client(ctx)
    output(dhcp_core.get_leases(client), ctx.obj["as_json"])


@dhcp_.command("add-static")
@click.option("--mac", required=True)
@click.option("--ip", required=True)
@click.option("--hostname", default="")
@click.pass_context
def dhcp_add_static(ctx: click.Context, mac: str, ip: str, hostname: str):
    client = make_client(ctx)
    output(
        dhcp_core.add_static_lease(client, mac=mac, ip=ip, hostname=hostname)
        or {"added": True, "mac": mac, "ip": ip},
        ctx.obj["as_json"],
    )


@dhcp_.command("remove-static")
@click.option("--mac", required=True)
@click.option("--ip", required=True)
@click.option("--hostname", default="")
@click.pass_context
def dhcp_remove_static(ctx: click.Context, mac: str, ip: str, hostname: str):
    client = make_client(ctx)
    output(
        dhcp_core.remove_static_lease(client, mac=mac, ip=ip, hostname=hostname)
        or {"removed": True, "mac": mac},
        ctx.obj["as_json"],
    )


@cli.group("tls")
@click.pass_context
def tls_(ctx: click.Context):
    """TLS/HTTPS configuration."""


@tls_.command("status")
@click.pass_context
def tls_status(ctx: click.Context):
    client = make_client(ctx)
    output(server_core.get_tls_status(client), ctx.obj["as_json"])


def main():
    cli(obj={})
