# ruff: noqa: F403, F405, E501
from .anygen_cli_base import *  # noqa: F403

# fmt: off
from .anygen_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command("repl", hidden=True)
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.anygen.utils.repl_skin import ReplSkin

    skin = ReplSkin("anygen", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "task create": "Create a generation task",
        "task run": "Full workflow: create → poll → download",
        "task status <id>": "Check task status",
        "task poll <id>": "Poll until completion",
        "task download <id>": "Download generated file",
        "task list": "List local task history",
        "task prepare": "Multi-turn requirement analysis",
        "file upload <path>": "Upload a reference file",
        "config set <key> <val>": "Set configuration",
        "config get [key]": "Show configuration",
        "session history": "Show command history",
        "session undo": "Undo last command",
        "session redo": "Redo last undone command",
        "help": "Show this help",
        "quit / exit": "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="anygen")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line == "help":
            skin.help(commands)
            continue

        parts = line.split()
        try:
            cli.main(parts, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


@cli.group()
def task():
    """Task management — create, poll, download, and run tasks."""
    pass


@task.command("create")
@click.option(
    "--operation",
    "-o",
    required=True,
    type=click.Choice(VALID_OPERATIONS, case_sensitive=False),
    help="Operation type",
)
@click.option("--prompt", "-p", required=True, help="Content prompt")
@click.option("--language", "-l", default=None, help="Language (zh-CN, en-US)")
@click.option("--slide-count", "-c", type=int, default=None, help="Number of slides")
@click.option("--template", "-t", default=None, help="Slide template")
@click.option(
    "--ratio",
    "-r",
    type=click.Choice(["16:9", "4:3"]),
    default=None,
    help="Slide ratio",
)
@click.option("--export-format", "-f", default=None, help="Export format")
@click.option("--file-token", multiple=True, help="File token from upload (repeatable)")
@click.option("--style", "-s", default=None, help="Style preference")
@handle_error
def task_create(
    operation,
    prompt,
    language,
    slide_count,
    template,
    ratio,
    export_format,
    file_token,
    style,
):
    """Create a generation task."""
    sess = get_session()
    result = task_mod.create_task(
        _api_key,
        operation,
        prompt,
        language=language,
        slide_count=slide_count,
        template=template,
        ratio=ratio,
        export_format=export_format,
        file_tokens=list(file_token) if file_token else None,
        style=style,
    )
    sess.record("task create", {"operation": operation, "prompt": prompt}, result)
    output(result, f"✓ Task created: {result['task_id']}")


@task.command("status")
@click.argument("task_id")
@handle_error
def task_status(task_id):
    """Query task status (non-blocking)."""
    result = task_mod.query_task(_api_key, task_id)
    status = result.get("status")
    progress = result.get("progress", 0)
    out = {
        "task_id": task_id,
        "status": status,
        "progress": progress,
    }
    if status == "completed":
        o = result.get("output", {})
        if o.get("file_name"):
            out["file_name"] = o["file_name"]
        if o.get("task_url"):
            out["task_url"] = o["task_url"]
    output(out, f"Task {task_id}: {status} ({progress}%)")
