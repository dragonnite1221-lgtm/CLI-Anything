# ruff: noqa: F403, F405, E501
from .adguardhome_cli_base import *  # noqa: F403

# fmt: off
from .adguardhome_cli_p1 import cli, make_client, output  # noqa: E402,E501
from .adguardhome_cli_p3 import clients_  # noqa: E402,E501
# fmt: on


@clients_.command("list")
@click.pass_context
def clients_list(ctx: click.Context):
    client = make_client(ctx)
    output(clients_core.list_clients(client), ctx.obj["as_json"])


@clients_.command("add")
@click.option("--name", required=True)
@click.option("--ip", required=True, help="Client IP address")
@click.pass_context
def clients_add(ctx: click.Context, name: str, ip: str):
    c = make_client(ctx)
    output(
        clients_core.add_client(c, name=name, ids=[ip])
        or {"added": True, "name": name},
        ctx.obj["as_json"],
    )


@clients_.command("remove")
@click.option("--name", required=True)
@click.pass_context
def clients_remove(ctx: click.Context, name: str):
    c = make_client(ctx)
    output(
        clients_core.delete_client(c, name=name) or {"removed": True, "name": name},
        ctx.obj["as_json"],
    )


@clients_.command("show")
@click.option("--name", required=True)
@click.pass_context
def clients_show(ctx: click.Context, name: str):
    c = make_client(ctx)
    data = clients_core.list_clients(c)
    all_clients = data.get("clients", []) if isinstance(data, dict) else []
    found = next((cl for cl in all_clients if cl.get("name") == name), None)
    output(found or {"error": f"Client '{name}' not found"}, ctx.obj["as_json"])


@cli.group("stats")
@click.pass_context
def stats_(ctx: click.Context):
    """DNS query statistics."""


@stats_.command("show")
@click.pass_context
def stats_show(ctx: click.Context):
    client = make_client(ctx)
    output(stats_core.get_stats(client), ctx.obj["as_json"])


@stats_.command("reset")
@click.pass_context
def stats_reset(ctx: click.Context):
    client = make_client(ctx)
    output(stats_core.reset_stats(client) or {"reset": True}, ctx.obj["as_json"])


@stats_.command("config")
@click.option("--interval", type=int, default=None, help="Retention in days")
@click.pass_context
def stats_config(ctx: click.Context, interval):
    client = make_client(ctx)
    if interval is not None:
        output(stats_core.set_stats_config(client, interval), ctx.obj["as_json"])
    else:
        output(stats_core.get_stats_config(client), ctx.obj["as_json"])


@cli.group("log")
@click.pass_context
def log_(ctx: click.Context):
    """Query log management."""


@log_.command("show")
@click.option("--limit", default=50, type=int)
@click.option("--offset", default=0, type=int)
@click.pass_context
def log_show(ctx: click.Context, limit: int, offset: int):
    client = make_client(ctx)
    output(log_core.get_log(client, limit=limit, offset=offset), ctx.obj["as_json"])


@log_.command("config")
@click.option("--enabled/--disabled", default=None)
@click.option("--interval", type=int, default=None)
@click.pass_context
def log_config(ctx: click.Context, enabled, interval):
    client = make_client(ctx)
    if enabled is not None or interval is not None:
        current = log_core.get_log_config(client)
        effective_enabled = (
            enabled if enabled is not None else current.get("enabled", True)
        )
        effective_interval = (
            interval if interval is not None else current.get("interval", 90)
        )
        output(
            log_core.set_log_config(
                client, enabled=effective_enabled, interval=effective_interval
            ),
            ctx.obj["as_json"],
        )
    else:
        output(log_core.get_log_config(client), ctx.obj["as_json"])


@log_.command("clear")
@click.pass_context
def log_clear(ctx: click.Context):
    client = make_client(ctx)
    output(log_core.clear_log(client) or {"cleared": True}, ctx.obj["as_json"])


@cli.group("rewrite")
@click.pass_context
def rewrite_(ctx: click.Context):
    """DNS rewrite rules."""


@rewrite_.command("list")
@click.pass_context
def rewrite_list(ctx: click.Context):
    client = make_client(ctx)
    output(rewrite_core.list_rewrites(client), ctx.obj["as_json"])


@rewrite_.command("add")
@click.option("--domain", required=True)
@click.option("--answer", required=True)
@click.pass_context
def rewrite_add(ctx: click.Context, domain: str, answer: str):
    client = make_client(ctx)
    output(
        rewrite_core.add_rewrite(client, domain=domain, answer=answer)
        or {"added": True, "domain": domain, "answer": answer},
        ctx.obj["as_json"],
    )


@rewrite_.command("remove")
@click.option("--domain", required=True)
@click.option("--answer", required=True)
@click.pass_context
def rewrite_remove(ctx: click.Context, domain: str, answer: str):
    client = make_client(ctx)
    output(
        rewrite_core.delete_rewrite(client, domain=domain, answer=answer)
        or {"removed": True, "domain": domain},
        ctx.obj["as_json"],
    )
