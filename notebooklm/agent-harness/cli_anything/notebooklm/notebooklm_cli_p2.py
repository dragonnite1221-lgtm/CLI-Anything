# ruff: noqa: F403, F405, E501
from .notebooklm_cli_base import *  # noqa: F403

# fmt: off
from .notebooklm_cli_p1 import chat, cli, emit, handle_error, resolve_notebook_id  # noqa: E402,E501
# fmt: on


@chat.command("ask")
@click.argument("prompt")
@click.option("--notebook", "notebook_id", default=None, help="Notebook ID")
@handle_error
def chat_ask(prompt, notebook_id):
    """Ask a question against a notebook."""
    emit(
        run_notebooklm(
            ["ask", prompt],
            notebook_id=resolve_notebook_id(notebook_id),
            json_output=_json_output,
        )
    )


@chat.command("history")
@click.option("--notebook", "notebook_id", default=None, help="Notebook ID")
@handle_error
def chat_history(notebook_id):
    """Show chat history."""
    emit(
        run_notebooklm(
            ["history"],
            notebook_id=resolve_notebook_id(notebook_id),
            json_output=_json_output,
        )
    )


@cli.group()
def artifact():
    """Artifact generation and inspection commands."""


@artifact.command("list")
@click.option("--notebook", "notebook_id", default=None, help="Notebook ID")
@handle_error
def artifact_list(notebook_id):
    """List notebook artifacts."""
    emit(
        run_notebooklm(
            ["artifact", "list"],
            notebook_id=resolve_notebook_id(notebook_id),
            json_output=_json_output,
        )
    )


@artifact.command("generate-report")
@click.option("--notebook", "notebook_id", default=None, help="Notebook ID")
@handle_error
def artifact_generate_report(notebook_id):
    """Generate a report artifact."""
    emit(
        run_notebooklm(
            ["generate", "report", "--wait"],
            notebook_id=resolve_notebook_id(notebook_id),
            json_output=_json_output,
        )
    )


@cli.group()
def download():
    """Artifact download helpers."""


@download.command("report")
@click.argument("output_path")
@click.option("--notebook", "notebook_id", default=None, help="Notebook ID")
@handle_error
def download_report(output_path, notebook_id):
    """Download the latest report artifact."""
    emit(
        run_notebooklm(
            ["download", "report", output_path],
            notebook_id=resolve_notebook_id(notebook_id),
            json_output=_json_output,
        )
    )


@cli.group()
def share():
    """Sharing and access control commands."""


@share.command("status")
@click.option("--notebook", "notebook_id", default=None, help="Notebook ID")
@handle_error
def share_status(notebook_id):
    """Inspect notebook sharing state."""
    emit(
        run_notebooklm(
            ["share", "status"],
            notebook_id=resolve_notebook_id(notebook_id),
            json_output=_json_output,
        )
    )


def main():
    cli()
