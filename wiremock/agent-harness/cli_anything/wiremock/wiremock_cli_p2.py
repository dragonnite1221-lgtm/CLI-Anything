# ruff: noqa: F403, F405, E501
from .wiremock_cli_base import *  # noqa: F403

# fmt: off
from .wiremock_cli_p1 import cli, stub  # noqa: E402,E501
# fmt: on


@cli.command()
@click.pass_context
def status(ctx):
    """Check if WireMock server is running."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    alive = client.is_alive()
    if json_mode:
        print_json(
            {
                "status": "running" if alive else "stopped",
                "host": client.host,
                "port": client.port,
            }
        )
    else:
        icon = "✓" if alive else "✗"
        state = "running" if alive else "stopped"
        click.echo(f"{icon} WireMock at {client.host}:{client.port} is {state}")


@stub.command("quick")
@click.argument("method")
@click.argument("url")
@click.argument("status", type=int)
@click.option("--body", default=None, help="Response body")
@click.option("--content-type", default="application/json")
@click.pass_context
def stub_quick(ctx, method, url, status, body, content_type):
    """Quickly create a stub: METHOD URL STATUS [--body TEXT]."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = StubsManager(client).quick_stub(method, url, status, body, content_type)
        if json_mode:
            print_json(data)
        else:
            success(f"Created stub {data.get('id')}", data)
    except Exception as e:
        error(str(e), json_mode)


@stub.command("delete")
@click.argument("stub_id")
@click.pass_context
def stub_delete(ctx, stub_id):
    """Delete a stub mapping by ID."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        StubsManager(client).delete(stub_id)
        if json_mode:
            print_json({"status": "ok"})
        else:
            success(f"Deleted stub {stub_id}")
    except Exception as e:
        error(str(e), json_mode)


@stub.command("reset")
@click.pass_context
def stub_reset(ctx):
    """Reset all stubs to defaults."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        StubsManager(client).reset()
        if json_mode:
            print_json({"status": "ok"})
        else:
            success("Stubs reset to default mappings")
    except Exception as e:
        error(str(e), json_mode)


@stub.command("save")
@click.pass_context
def stub_save(ctx):
    """Persist stubs to disk."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        StubsManager(client).save()
        if json_mode:
            print_json({"status": "ok"})
        else:
            success("Mappings saved to disk")
    except Exception as e:
        error(str(e), json_mode)


@stub.command("import")
@click.argument("file_path")
@click.pass_context
def stub_import(ctx, file_path):
    """Import stubs from a JSON file."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        result = StubsManager(client).import_stubs(data)
        if json_mode:
            print_json(result)
        else:
            success("Stubs imported", result)
    except Exception as e:
        error(str(e), json_mode)


@cli.group()
def request():
    """Inspect and verify served requests."""


@request.command("list")
@click.option("--limit", type=int, default=None)
@click.pass_context
def request_list(ctx, limit):
    """List recent served requests."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = RequestsLog(client).list(limit=limit)
        if json_mode:
            print_json(data)
        else:
            events = data.get("serveEvents", [])
            rows = [
                (
                    e.get("id", "")[:8] + "...",
                    e.get("request", {}).get("method", ""),
                    e.get("request", {}).get("url", ""),
                    e.get("responseDefinition", {}).get("status", ""),
                    e.get("wasMatched", ""),
                )
                for e in events
            ]
            print_table(
                ["ID", "Method", "URL", "Status", "Matched"],
                rows,
                title=f"Requests ({data.get('total', 0)} total)",
            )
    except Exception as e:
        error(str(e), json_mode)
