# ruff: noqa: F403, F405, E501
from .mermaid_cli_base import *  # noqa: F403

# fmt: off
from .mermaid_cli_p1 import cli, diagram, emit, get_session, session  # noqa: E402,E501
# fmt: on


@diagram.command("show")
def diagram_show() -> None:
    result = diagram_mod.show_diagram(get_session())
    if _json_output:
        emit(result)
    else:
        click.echo(result["code"])


@cli.group()
def export() -> None:
    """Render and share commands."""


@export.command("render")
@click.argument("output_path")
@click.option("--format", "-f", "fmt", type=click.Choice(["svg", "png"]), default="svg")
@click.option("--overwrite", is_flag=True, help="Overwrite existing output")
def export_render(output_path: str, fmt: str, overwrite: bool) -> None:
    emit(
        export_mod.render(get_session(), output_path, fmt=fmt, overwrite=overwrite),
        "Rendered output",
    )


@export.command("share")
@click.option("--mode", type=click.Choice(["edit", "view"]), default="edit")
def export_share(mode: str) -> None:
    emit(export_mod.share(get_session(), mode=mode), "Generated share URL")


@session.command("status")
def session_status() -> None:
    emit(get_session().status(), "Session status")


@session.command("undo")
def session_undo() -> None:
    success = get_session().undo()
    emit(
        {"action": "undo", "success": success},
        "Undo complete" if success else "Nothing to undo",
    )


@session.command("redo")
def session_redo() -> None:
    success = get_session().redo()
    emit(
        {"action": "redo", "success": success},
        "Redo complete" if success else "Nothing to redo",
    )


def main() -> None:
    cli()
