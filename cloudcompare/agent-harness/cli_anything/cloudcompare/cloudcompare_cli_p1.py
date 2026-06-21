# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p2 import project, repl  # noqa: E402,E501
# fmt: on


def _pretty(data, indent: int = 0) -> None:
    """Simple human-readable pretty printer for dicts/lists."""
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


def _out(ctx: click.Context, data: dict) -> None:
    """Print data as JSON or human-readable."""
    if ctx.obj and ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2))
    else:
        _pretty(data)


def _error(msg: str, json_mode: bool = False) -> None:
    if json_mode:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def _require_project(ctx: click.Context) -> tuple[Session, str]:
    """Get project path from context, raise UsageError if missing."""
    project_path = ctx.obj.get("project") if ctx.obj else None
    if not project_path:
        raise click.UsageError(
            "No project file specified. Use --project or create one with:\n"
            "  cli-anything-cloudcompare project new -o myproject.json"
        )
    return Session(project_path), project_path


@click.group(invoke_without_command=True)
@click.option(
    "--project",
    "-p",
    envvar="CC_PROJECT",
    default=None,
    help="Path to project JSON file.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Output results as JSON (for agent consumption).",
)
@click.pass_context
def cli(ctx: click.Context, project: Optional[str], json_output: bool) -> None:
    """cli-anything-cloudcompare: Agent-friendly CLI for CloudCompare.

    Run without a subcommand to enter the interactive REPL.
    Use --json for machine-readable output.

    CloudCompare must be installed:
      flatpak install flathub org.cloudcompare.CloudCompare
    """
    ctx.ensure_object(dict)
    ctx.obj["project"] = project
    ctx.obj["json"] = json_output

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
