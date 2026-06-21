# ruff: noqa: F403, F405, E501
from .anygen_cli_base import *  # noqa: F403

# fmt: off
from .anygen_cli_p1 import get_session, handle_error, output  # noqa: E402,E501
from .anygen_cli_p2 import task  # noqa: E402,E501
# fmt: on


@task.command("poll")
@click.argument("task_id")
@click.option(
    "--output",
    "-o",
    "output_dir",
    default=None,
    help="Output directory for auto-download on completion",
)
@handle_error
def task_poll(task_id, output_dir):
    """Poll task until completion (blocking)."""

    def on_progress(status, pct):
        if not _json_output:
            click.echo(f"  ● {status}: {pct}%")

    result = task_mod.poll_task(_api_key, task_id, on_progress=on_progress)
    sess = get_session()
    sess.record("task poll", {"task_id": task_id}, {"status": result.get("status")})

    if output_dir and result.get("status") == "completed":
        dl = task_mod.download_file(_api_key, task_id, output_dir)
        output(dl, f"✓ Downloaded: {dl['local_path']} ({dl['file_size']:,} bytes)")
    else:
        output(result, f"✓ Task {task_id}: {result.get('status')}")


@task.command("download")
@click.argument("task_id")
@click.option("--output", "-o", "output_dir", required=True, help="Output directory")
@handle_error
def task_download(task_id, output_dir):
    """Download the generated file for a completed task."""
    dl = task_mod.download_file(_api_key, task_id, output_dir)
    sess = get_session()
    sess.record("task download", {"task_id": task_id}, dl)
    output(dl, f"✓ Downloaded: {dl['local_path']} ({dl['file_size']:,} bytes)")


@task.command("thumbnail")
@click.argument("task_id")
@click.option("--output", "-o", "output_dir", required=True, help="Output directory")
@handle_error
def task_thumbnail(task_id, output_dir):
    """Download thumbnail image for a completed task."""
    dl = task_mod.download_thumbnail(_api_key, task_id, output_dir)
    output(dl, f"✓ Thumbnail saved: {dl['local_path']}")


@task.command("run")
@click.option(
    "--operation",
    "-o",
    required=True,
    type=click.Choice(VALID_OPERATIONS, case_sensitive=False),
    help="Operation type",
)
@click.option("--prompt", "-p", required=True, help="Content prompt")
@click.option("--output", "output_dir", default=None, help="Output directory")
@click.option("--language", "-l", default=None, help="Language (zh-CN, en-US)")
@click.option("--slide-count", "-c", type=int, default=None, help="Number of slides")
@click.option("--template", "-t", default=None, help="Slide template")
@click.option("--ratio", "-r", type=click.Choice(["16:9", "4:3"]), default=None)
@click.option("--export-format", "-f", default=None, help="Export format")
@click.option("--file-token", multiple=True, help="File token (repeatable)")
@click.option("--style", "-s", default=None, help="Style preference")
@handle_error
def task_run(
    operation,
    prompt,
    output_dir,
    language,
    slide_count,
    template,
    ratio,
    export_format,
    file_token,
    style,
):
    """Full workflow: create → poll → download."""

    def on_progress(status, pct):
        if not _json_output:
            click.echo(f"  ● {status}: {pct}%")

    result = task_mod.run_full_workflow(
        _api_key,
        operation,
        prompt,
        output_dir,
        on_progress=on_progress,
        language=language,
        slide_count=slide_count,
        template=template,
        ratio=ratio,
        export_format=export_format,
        file_tokens=list(file_token) if file_token else None,
        style=style,
    )
    sess = get_session()
    sess.record("task run", {"operation": operation, "prompt": prompt}, result)

    if result.get("local_path"):
        output(
            result,
            f"✓ Completed! File: {result['local_path']} ({result.get('file_size', 0):,} bytes)",
        )
    else:
        output(result, f"✓ Completed! View at: {result.get('task_url', 'N/A')}")


@task.command("list")
@click.option("--limit", "-n", type=int, default=20, help="Max number of tasks")
@click.option("--status", "status_filter", default=None, help="Filter by status")
@handle_error
def task_list(limit, status_filter):
    """List locally cached task records."""
    records = task_mod.list_task_records(limit=limit, status_filter=status_filter)
    if not records:
        output([], "No tasks found.")
        return
    output(records, f"Found {len(records)} task(s):")
