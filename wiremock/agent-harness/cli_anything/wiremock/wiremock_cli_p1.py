# ruff: noqa: F403, F405, E501
from .wiremock_cli_base import *  # noqa: F403


@click.group()
@click.option(
    "--host",
    default=None,
    envvar="WIREMOCK_HOST",
    help="WireMock host (default: localhost)",
)
@click.option(
    "--port",
    default=None,
    type=int,
    envvar="WIREMOCK_PORT",
    help="WireMock port (default: 8080)",
)
@click.option(
    "--scheme",
    default=None,
    envvar="WIREMOCK_SCHEME",
    help="http or https (default: http)",
)
@click.option(
    "--user", default=None, envvar="WIREMOCK_USER", help="Admin basic auth username"
)
@click.option(
    "--password",
    default=None,
    envvar="WIREMOCK_PASSWORD",
    help="Admin basic auth password",
)
@click.option(
    "--json",
    "json_mode",
    is_flag=True,
    envvar="WIREMOCK_JSON",
    help="Output as JSON",
)
@click.pass_context
def cli(ctx, host, port, scheme, user, password, json_mode):
    """WireMock CLI — manage stubs, requests, scenarios, and recordings."""
    session = Session.from_env()
    if host is not None:
        session.host = host
    if port is not None:
        session.port = port
    if scheme is not None:
        session.scheme = scheme
    if user is not None:
        session.username = user
    if password is not None:
        session.password = password
    client = WireMockClient(
        host=session.host,
        port=session.port,
        scheme=session.scheme,
        auth=session.auth(),
    )
    ctx.obj = client
    ctx.meta["json_mode"] = json_mode


@cli.group()
def stub():
    """Manage HTTP stub mappings."""


@stub.command("list")
@click.option("--limit", type=int, default=None)
@click.option("--offset", type=int, default=None)
@click.pass_context
def stub_list(ctx, limit, offset):
    """List all stub mappings."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    mgr = StubsManager(client)
    try:
        data = mgr.list(limit=limit, offset=offset)
        if json_mode:
            print_json(data)
        else:
            mappings = data.get("mappings", [])
            rows = [
                (
                    m.get("id", "")[:8] + "...",
                    m.get("name", ""),
                    m.get("request", {}).get("method", ""),
                    m.get("request", {}).get("url", ""),
                    m.get("response", {}).get("status", ""),
                )
                for m in mappings
            ]
            print_table(
                ["ID", "Name", "Method", "URL", "Status"],
                rows,
                title=f"Stubs ({data.get('total', 0)} total)",
            )
    except Exception as e:
        error(str(e), json_mode)


@stub.command("get")
@click.argument("stub_id")
@click.pass_context
def stub_get(ctx, stub_id):
    """Get a stub mapping by ID."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        data = StubsManager(client).get(stub_id)
        if json_mode:
            print_json(data)
        else:
            success(
                f"Stub {data.get('id', stub_id)[:8]}... "
                f"{data.get('request', {}).get('method', '')} "
                f"{data.get('request', {}).get('url', '')}",
                data,
            )
    except Exception as e:
        error(str(e), json_mode)


@stub.command("create")
@click.argument("mapping_json")
@click.pass_context
def stub_create(ctx, mapping_json):
    """Create a stub mapping from JSON string or @file."""
    client = ctx.obj
    json_mode = ctx.meta.get("json_mode", False)
    try:
        if mapping_json.startswith("@"):
            with open(mapping_json[1:], encoding="utf-8") as f:
                mapping = json.load(f)
        else:
            mapping = json.loads(mapping_json)
        data = StubsManager(client).create(mapping)
        if json_mode:
            print_json(data)
        else:
            success(f"Created stub {data.get('id')}", data)
    except Exception as e:
        error(str(e), json_mode)
