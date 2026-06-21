# ruff: noqa: F403, F405, E501
from .cloudanalyzer_cli_base import *  # noqa: F403


def _pretty(data, indent: int = 0) -> None:
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{k}:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{prefix}{k}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{prefix}[{i}]")
                _pretty(item, indent + 1)
            else:
                click.echo(f"{prefix}  {item}")
    else:
        click.echo(f"{prefix}{data}")


def _out(ctx: click.Context, data: dict | list) -> None:
    """Print data as JSON or human-readable."""
    if ctx.obj and ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        _pretty(data)


def _error(msg: str, json_mode: bool = False) -> None:
    if json_mode:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


@click.group(invoke_without_command=True)
@click.option("-p", "--project", default=None, help="Path to project JSON file")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.version_option(VERSION, prog_name="cli-anything-cloudanalyzer")
@click.pass_context
def cli(ctx: click.Context, project: Optional[str], json_mode: bool) -> None:
    """CloudAnalyzer — Agent-friendly QA platform for point cloud outputs."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_mode
    ctx.obj["project"] = project
    if ctx.invoked_subcommand is None:
        _start_repl(ctx)


def _start_repl(ctx: click.Context) -> None:
    """Launch interactive REPL."""
    if not ca_backend.is_available():
        click.echo(
            "Error: CloudAnalyzer is not installed. Run: pip install cloudanalyzer"
        )
        ctx.exit(1)
        return

    skin = ReplSkin("cloudanalyzer", version=VERSION)
    skin.print_banner()

    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory

        repl_session = PromptSession(history=FileHistory(".ca_repl_history"))
    except ImportError:
        repl_session = None

    while True:
        try:
            if repl_session:
                line = repl_session.prompt(skin.prompt())
            else:
                line = input(skin.prompt())
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        line = line.strip()
        if not line:
            continue
        if line in ("exit", "quit", "q"):
            skin.print_goodbye()
            break

        try:
            args = shlex.split(line)
            cli.main(args, standalone_mode=False, obj=ctx.obj)
        except SystemExit:
            pass
        except ValueError as e:
            _error(f"Invalid input: {e}", ctx.obj.get("json", False))
        except Exception as e:
            _error(str(e), ctx.obj.get("json", False))


@cli.group()
@click.pass_context
def evaluate(ctx: click.Context) -> None:
    """Point cloud evaluation commands."""


@evaluate.command("run")
@click.argument("source")
@click.argument("reference")
@click.option("--plot", default=None, help="Save F1 curve plot")
@click.option("--threshold", type=float, default=None)
@click.pass_context
def evaluate_run(
    ctx: click.Context,
    source: str,
    reference: str,
    plot: Optional[str],
    threshold: Optional[float],
) -> None:
    """Evaluate a point cloud against a reference."""
    try:
        kwargs = {}
        if threshold is not None:
            kwargs["thresholds"] = [threshold]
        if plot:
            kwargs["plot"] = plot
        result = ca_backend.evaluate(source, reference, **kwargs)
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@evaluate.command("compare")
@click.argument("source")
@click.argument("target")
@click.option("--register", default="gicp", help="Registration method")
@click.pass_context
def evaluate_compare(
    ctx: click.Context, source: str, target: str, register: str
) -> None:
    """Compare two point clouds with optional registration."""
    try:
        result = ca_backend.compare(source, target, method=register)
        _out(ctx, result)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)
