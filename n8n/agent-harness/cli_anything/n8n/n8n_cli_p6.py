# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag, cli  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
# fmt: on


@workflow_.command("bulk-activate")
@click.option("--tag", default=None, help="Activate all workflows with this tag")
@click.option("--search", default=None, help="Activate all workflows matching name")
@click.pass_context
def workflow_bulk_activate(
    ctx: click.Context, tag: str | None, search: str | None
) -> None:
    """Activate multiple workflows by tag or name search."""
    if not tag and not search:
        error("Provide --tag or --search to select workflows")
        return
    conn = _conn(ctx)
    data = workflows.list_workflows(**conn, tags=tag, limit=200)
    wf_list = data.get("data", []) if isinstance(data, dict) else data
    if search:
        q = search.lower()
        wf_list = [w for w in wf_list if q in w.get("name", "").lower()]
    inactive = [w for w in wf_list if not w.get("active")]
    if not inactive:
        warn("No inactive workflows found matching criteria")
        return
    click.echo(f"  Activating {len(inactive)} workflow(s)...")
    ok, fail = 0, 0
    for w in inactive:
        try:
            workflows.activate_workflow(w.get("id", ""), **conn)
            click.secho(f"    {w.get('id', '?')}  {w.get('name', '?')}", fg="green")
            ok += 1
        except Exception as exc:
            click.secho(
                f"    {w.get('id', '?')}  {w.get('name', '?')} — {exc}", fg="red"
            )
            fail += 1
    success(f"Activated {ok}, failed {fail}")


@workflow_.command("bulk-deactivate")
@click.option("--tag", default=None, help="Deactivate all workflows with this tag")
@click.option("--search", default=None, help="Deactivate all workflows matching name")
@click.pass_context
def workflow_bulk_deactivate(
    ctx: click.Context, tag: str | None, search: str | None
) -> None:
    """Deactivate multiple workflows by tag or name search."""
    if not tag and not search:
        error("Provide --tag or --search to select workflows")
        return
    conn = _conn(ctx)
    data = workflows.list_workflows(**conn, tags=tag, limit=200)
    wf_list = data.get("data", []) if isinstance(data, dict) else data
    if search:
        q = search.lower()
        wf_list = [w for w in wf_list if q in w.get("name", "").lower()]
    active = [w for w in wf_list if w.get("active")]
    if not active:
        warn("No active workflows found matching criteria")
        return
    click.echo(f"  Deactivating {len(active)} workflow(s)...")
    ok, fail = 0, 0
    for w in active:
        try:
            workflows.deactivate_workflow(w.get("id", ""), **conn)
            click.secho(
                f"    {w.get('id', '?')}  {w.get('name', '?')}", fg="bright_black"
            )
            ok += 1
        except Exception as exc:
            click.secho(
                f"    {w.get('id', '?')}  {w.get('name', '?')} — {exc}", fg="red"
            )
            fail += 1
    success(f"Deactivated {ok}, failed {fail}")


@cli.group("execution")
def execution_() -> None:
    """Execution management."""


@execution_.command("list")
@click.option(
    "--status",
    type=click.Choice(["error", "success", "waiting", "running", "new"]),
    default=None,
)
@click.option("--workflow-id", default=None, help="Filter by workflow ID")
@click.option("--limit", default=20, type=int)
@click.option("--cursor", default=None)
@click.option(
    "--include-data", is_flag=True, default=False, help="Include execution data"
)
@click.pass_context
def execution_list(
    ctx: click.Context,
    status: str | None,
    workflow_id: str | None,
    limit: int,
    cursor: str | None,
    include_data: bool,
) -> None:
    """List executions."""
    data = executions.list_executions(
        **_conn(ctx),
        status=status,
        workflow_id=workflow_id,
        limit=limit,
        cursor=cursor,
        include_data=include_data,
    )
    output(data, _json_flag(ctx))


@execution_.command("get")
@click.argument("execution_id")
@click.option("--no-data", is_flag=True, default=False, help="Exclude execution data")
@click.pass_context
def execution_get(ctx: click.Context, execution_id: str, no_data: bool) -> None:
    """Get execution details."""
    data = executions.get_execution(
        execution_id, **_conn(ctx), include_data=not no_data
    )
    output(data, _json_flag(ctx))


@execution_.command("delete")
@click.argument("execution_id")
@click.pass_context
def execution_delete(ctx: click.Context, execution_id: str) -> None:
    """Delete an execution."""
    executions.delete_execution(execution_id, **_conn(ctx))
    success(f"Execution {execution_id} deleted")


@execution_.command("retry")
@click.argument("execution_id")
@click.pass_context
def execution_retry(ctx: click.Context, execution_id: str) -> None:
    """Retry a failed execution."""
    data = executions.retry_execution(execution_id, **_conn(ctx))
    output(data, _json_flag(ctx))
