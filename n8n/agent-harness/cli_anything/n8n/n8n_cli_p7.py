# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag  # noqa: E402,E501
from .n8n_cli_p6 import execution_  # noqa: E402,E501
# fmt: on


@execution_.command("errors")
@click.option("--workflow-id", default=None, help="Filter by workflow ID")
@click.option("--limit", default=10, type=int, help="Number of errors to show")
@click.option(
    "--details", is_flag=True, default=False, help="Include error message details"
)
@click.pass_context
def execution_errors(
    ctx: click.Context, workflow_id: str | None, limit: int, details: bool
) -> None:
    """Show recent failed executions (shortcut for list --status error)."""
    conn = _conn(ctx)
    data = executions.list_executions(
        **conn,
        status="error",
        workflow_id=workflow_id,
        limit=limit,
        include_data=details,
    )
    err_list = data.get("data", []) if isinstance(data, dict) else data

    if _json_flag(ctx):
        output(data, True)
        return

    if not err_list:
        success("No errors found!")
        return

    click.secho(f"\n  {len(err_list)} recent error(s):\n", fg="red", bold=True)
    for e in err_list:
        eid = e.get("id", "?")
        wf_id = e.get("workflowId", "?")
        started = str(e.get("startedAt", ""))[:19].replace("T", " ")
        stopped = str(e.get("stoppedAt", ""))[:19].replace("T", " ")
        click.echo(
            f"    {click.style(eid, fg='red'):>12s}  wf:{wf_id:<16s}  {started} -> {stopped}"
        )

        if details and isinstance(e.get("data"), dict):
            run_data = e["data"].get("resultData", {})
            error_msg = run_data.get("error", {}).get("message", "")
            if error_msg:
                click.secho(f"              {error_msg[:120]}", fg="bright_black")
    click.echo()


@execution_.command("watch")
@click.option("--workflow-id", default=None, help="Filter by workflow ID")
@click.option(
    "--interval", default=5, type=int, help="Poll interval in seconds (default: 5)"
)
@click.option("--limit", default=5, type=int, help="Number of executions to show")
@click.pass_context
def execution_watch(
    ctx: click.Context, workflow_id: str | None, interval: int, limit: int
) -> None:
    """Watch executions in real-time (poll mode). Press Ctrl+C to stop."""
    import shutil

    if interval < 1:
        error("--interval must be at least 1 second")
        return
    conn = _conn(ctx)
    click.secho(
        f"  Watching executions (every {interval}s). Ctrl+C to stop.\n", fg="cyan"
    )
    seen: set[str] = set()
    try:
        while True:
            data = executions.list_executions(
                **conn, workflow_id=workflow_id, limit=limit
            )
            rows = data.get("data", []) if isinstance(data, dict) else data
            term_w = shutil.get_terminal_size().columns
            click.echo("\033[2J\033[H", nl=False)  # clear screen
            click.secho(
                f"  n8n executions — {time.strftime('%H:%M:%S')} (every {interval}s, Ctrl+C to stop)\n",
                fg="cyan",
            )
            if not rows:
                click.secho("  No executions found.", fg="bright_black")
            else:
                for row in rows:
                    eid = str(row.get("id", ""))
                    status = row.get("status", "?")
                    wf_id = row.get("workflowId", "?")
                    started = str(row.get("startedAt", ""))[:19].replace("T", " ")
                    is_new = eid not in seen
                    seen.add(eid)
                    color = {
                        "success": "green",
                        "error": "red",
                        "running": "yellow",
                        "waiting": "cyan",
                    }.get(status, "white")
                    marker = " *" if is_new else "  "
                    line = f"{marker} {eid:>8s}  {click.style(status.ljust(8), fg=color)}  wf:{wf_id:<16s}  {started}"
                    click.echo(line[:term_w])
            time.sleep(interval)
    except KeyboardInterrupt:
        click.echo("\n  Stopped.")
