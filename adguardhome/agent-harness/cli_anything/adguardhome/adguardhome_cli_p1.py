# ruff: noqa: F403, F405, E501
from .adguardhome_cli_base import *  # noqa: F403


def make_client(ctx: click.Context) -> AdGuardHomeClient:
    obj = ctx.obj
    return AdGuardHomeClient(
        host=obj["host"],
        port=obj["port"],
        username=obj["username"],
        password=obj["password"],
        https=obj.get("use_https", False),
    )


def output(data, as_json: bool) -> None:
    if as_json:
        click.echo(json.dumps(data, indent=2, default=str))
    elif isinstance(data, dict):
        for k, v in data.items():
            click.echo(f"{k}: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                click.echo(json.dumps(item, default=str))
            else:
                click.echo(str(item))
    else:
        click.echo(str(data))


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option("--host", default=None, help="AdGuardHome hostname/IP")
@click.option("--port", default=None, type=int, help="AdGuardHome port (default 3000)")
@click.option("--username", default=None, help="Basic Auth username")
@click.option("--password", default=None, help="Basic Auth password")
@click.option(
    "--config",
    "config_path",
    default=None,
    type=click.Path(),
    help="Path to config file",
)
@click.option(
    "--https",
    "use_https",
    is_flag=True,
    default=False,
    help="Use HTTPS (auto-detected for port 443)",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON")
@click.pass_context
def cli(
    ctx: click.Context, host, port, username, password, config_path, use_https, as_json
):
    """cli-anything-adguardhome - control AdGuardHome from the command line."""
    ctx.ensure_object(dict)

    config_path_obj = Path(config_path) if config_path else None
    cfg = project.load_config(config_path_obj)
    ctx.obj["host"] = host or cfg["host"]
    ctx.obj["port"] = port or cfg["port"]
    ctx.obj["username"] = username or cfg["username"]
    ctx.obj["password"] = password or cfg["password"]
    ctx.obj["use_https"] = use_https or cfg.get("https", False)
    ctx.obj["as_json"] = as_json
    ctx.obj["config_path"] = config_path_obj

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command(hidden=True)
@click.pass_context
def repl(ctx: click.Context):
    """Interactive REPL mode."""
    skin = ReplSkin("adguardhome", version="1.0.0")
    skin.print_banner()

    host = ctx.obj["host"]
    port = ctx.obj["port"]
    skin.info(f"Connecting to {host}:{port}")

    pt_session = skin.create_prompt_session()

    while True:
        try:
            line = skin.get_input(pt_session, project_name=f"{host}:{port}")
        except (EOFError, KeyboardInterrupt):
            break

        line = line.strip()
        if not line:
            continue
        if line in ("exit", "quit"):
            break
        if line == "help":
            skin.help(
                {
                    "server status/version/restart": "Server management",
                    "filter list/add/remove/enable/disable/refresh/status/toggle": "Filtering",
                    "blocking parental/safebrowsing/safesearch status/enable/disable": "Blocking",
                    "blocked-services list/set": "Blocked services",
                    "clients list/add/remove/show": "Client management",
                    "stats show/reset/config": "Statistics",
                    "log show/config/clear": "Query log",
                    "rewrite list/add/remove": "DNS rewrites",
                    "dhcp status/leases/add-static/remove-static": "DHCP server",
                    "tls status": "TLS configuration",
                    "config show/save/test": "Connection config",
                }
            )
            continue

        try:
            args = shlex.split(line)
            cli.main(args=args, obj=dict(ctx.obj), standalone_mode=False)
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except RuntimeError as e:
            skin.error(str(e))
        except SystemExit:
            pass
        except Exception as e:
            skin.error(f"Unexpected error: {e}")

    skin.print_goodbye()


@cli.group()
@click.pass_context
def config(ctx: click.Context):
    """Connection configuration."""
