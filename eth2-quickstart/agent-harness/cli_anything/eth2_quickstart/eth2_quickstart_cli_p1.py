# ruff: noqa: F403, F405, E501
from .eth2_quickstart_cli_base import *  # noqa: F403


def emit(data, as_json: bool) -> None:
    if as_json:
        click.echo(json.dumps(data, indent=2, default=str))
        return

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                click.echo(f"{key}: {json.dumps(value, default=str)}")
            else:
                click.echo(f"{key}: {value}")
        return

    click.echo(str(data))


def fail(message: str, as_json: bool) -> NoReturn:
    if as_json:
        click.echo(json.dumps({"error": message}))
    else:
        click.echo(message)
    raise click.exceptions.Exit(1)


def backend_from_context(ctx: click.Context) -> Eth2QuickStartBackend:
    try:
        return Eth2QuickStartBackend(ctx.obj["repo_root"])
    except RuntimeError as exc:
        fail(str(exc), ctx.obj["as_json"])


def require_confirm(ctx: click.Context, confirm: bool = False) -> None:
    if not (ctx.obj.get("confirm", False) or confirm):
        fail("This command requires --confirm", ctx.obj["as_json"])


def handle_backend_result(result: dict, as_json: bool) -> None:
    if result.get("ok"):
        emit(result, as_json)
        return

    payload = {
        "error": "Command failed",
        "result": result,
    }
    if as_json:
        click.echo(json.dumps(payload, indent=2))
    else:
        click.echo(f"ERROR {result.get('stderr') or result.get('stdout')}")
    raise click.exceptions.Exit(1)


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option("--repo-root", default=None, help="Path to an eth2-quickstart checkout")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON")
@click.option(
    "--confirm", is_flag=True, default=False, help="Confirm mutating operations"
)
@click.pass_context
def cli(ctx: click.Context, repo_root, as_json, confirm):
    """CLI harness for eth2-quickstart."""
    ctx.ensure_object(dict)
    ctx.obj["repo_root"] = repo_root
    ctx.obj["as_json"] = as_json
    ctx.obj["confirm"] = confirm

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command(hidden=True)
@click.pass_context
def repl(ctx: click.Context):
    """Interactive REPL mode."""
    from cli_anything.eth2_quickstart.utils.repl_skin import ReplSkin

    skin = ReplSkin("eth2-quickstart", version=__version__)
    skin.print_banner()
    pt_session = skin.create_prompt_session()

    while True:
        try:
            line = skin.get_input(pt_session, project_name="repo")
        except (EOFError, KeyboardInterrupt):
            break

        line = line.strip()
        if not line:
            continue
        if line in {"exit", "quit"}:
            break
        if line == "help":
            skin.help(
                {
                    "setup-node": "Run phase1, phase2, or ensure-driven orchestration",
                    "install-clients": "Install execution, consensus, and MEV clients",
                    "start-rpc": "Install and start nginx/caddy RPC exposure",
                    "configure-validator": "Update validator metadata and return import guidance",
                    "status": "Show aggregate status",
                    "health-check": "Run doctor --json",
                }
            )
            continue

        try:
            args = shlex.split(line)
            cli.main(args=args, obj=dict(ctx.obj), standalone_mode=False)
        except click.exceptions.Exit:
            pass
        except Exception as exc:  # pragma: no cover - REPL fallback
            skin.error(str(exc))

    skin.print_goodbye()
