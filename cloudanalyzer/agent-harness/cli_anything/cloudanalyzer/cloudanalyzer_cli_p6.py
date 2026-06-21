# ruff: noqa: F403, F405, E501
from .cloudanalyzer_cli_base import *  # noqa: F403

# fmt: off
from .cloudanalyzer_cli_p1 import _error, _out, cli  # noqa: E402,E501
from .cloudanalyzer_cli_p5 import session  # noqa: E402,E501
# fmt: on


@session.command("new")
@click.option("-o", "--output", required=True, help="Project file path")
@click.option("-n", "--name", default="untitled")
@click.pass_context
def session_new(ctx: click.Context, output: str, name: str) -> None:
    """Create a new project file."""
    try:
        create_project(output, name=name)
        _out(ctx, {"created": output, "name": name})
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


@session.command("history")
@click.option("-n", "--last", type=int, default=10)
@click.pass_context
def session_history(ctx: click.Context, last: int) -> None:
    """Show recent operation history."""
    project_path = ctx.obj.get("project")
    if not project_path:
        _error("No project specified. Use --project.", ctx.obj.get("json", False))
        ctx.exit(1)
        return
    try:
        sess = Session(project_path)
        history = sess.history[-last:]
        _out(ctx, history)
    except Exception as e:
        _error(str(e), ctx.obj.get("json", False))
        ctx.exit(1)


def main() -> None:
    cli(obj={})
