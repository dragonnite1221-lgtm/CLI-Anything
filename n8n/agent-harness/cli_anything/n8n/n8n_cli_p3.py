# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _auto_snapshot, _conn, _json_flag, _load_json_arg  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
# fmt: on


@workflow_.command("search")
@click.argument("query")
@click.option("--active/--inactive", default=None, help="Filter by active status")
@click.pass_context
def workflow_search(ctx: click.Context, query: str, active: bool | None) -> None:
    """Search workflows by name (case-insensitive)."""
    data = workflows.list_workflows(**_conn(ctx), limit=200, active=active)
    wf_list = data.get("data", []) if isinstance(data, dict) else data
    query_lower = query.lower()
    matches = [w for w in wf_list if query_lower in w.get("name", "").lower()]
    if _json_flag(ctx):
        output({"data": matches}, True)
    elif not matches:
        warn(f"No workflows matching '{query}'")
    else:
        click.secho(
            f"  Found {len(matches)} workflow(s) matching '{query}':\n", fg="cyan"
        )
        for w in matches:
            status_str = (
                click.style("active", fg="green")
                if w.get("active")
                else click.style("inactive", fg="bright_black")
            )
            click.echo(
                f"    {w.get('id', '?'):>16s}  {status_str}  {w.get('name', '?')}"
            )


@workflow_.command("get")
@click.argument("workflow_id")
@click.pass_context
def workflow_get(ctx: click.Context, workflow_id: str) -> None:
    """Get workflow details."""
    data = workflows.get_workflow(workflow_id, **_conn(ctx))
    output(data, _json_flag(ctx))


@workflow_.command("create")
@click.argument("json_data")
@click.pass_context
def workflow_create(ctx: click.Context, json_data: str) -> None:
    """Create a workflow from JSON (inline or @file.json). Workflows are created inactive."""
    payload = _load_json_arg(json_data)
    payload.pop("active", None)  # Never auto-activate on create
    data = workflows.create_workflow(payload, **_conn(ctx))
    output(data, _json_flag(ctx))


@workflow_.command("update")
@click.argument("workflow_id")
@click.argument("json_data")
@click.pass_context
def workflow_update(ctx: click.Context, workflow_id: str, json_data: str) -> None:
    """Update a workflow. Does not change active status — use activate/deactivate."""
    _auto_snapshot(workflow_id, _conn(ctx), "update")
    payload = _load_json_arg(json_data)
    payload.pop("active", None)  # Don't change active status via update
    data = workflows.update_workflow(workflow_id, payload, **_conn(ctx))
    output(data, _json_flag(ctx))


@workflow_.command("delete")
@click.argument("workflow_id")
@click.confirmation_option(prompt="Are you sure you want to delete this workflow?")
@click.pass_context
def workflow_delete(ctx: click.Context, workflow_id: str) -> None:
    """Delete a workflow."""
    workflows.delete_workflow(workflow_id, **_conn(ctx))
    success(f"Workflow {workflow_id} deleted")


@workflow_.command("activate")
@click.argument("workflow_id")
@click.pass_context
def workflow_activate(ctx: click.Context, workflow_id: str) -> None:
    """Activate a workflow."""
    data = workflows.activate_workflow(workflow_id, **_conn(ctx))
    output(data, _json_flag(ctx))


@workflow_.command("deactivate")
@click.argument("workflow_id")
@click.pass_context
def workflow_deactivate(ctx: click.Context, workflow_id: str) -> None:
    """Deactivate a workflow."""
    data = workflows.deactivate_workflow(workflow_id, **_conn(ctx))
    output(data, _json_flag(ctx))


@workflow_.command("tags")
@click.argument("workflow_id")
@click.pass_context
def workflow_tags(ctx: click.Context, workflow_id: str) -> None:
    """Get workflow tags."""
    data = workflows.get_workflow_tags(workflow_id, **_conn(ctx))
    output(data, _json_flag(ctx))


@workflow_.command("set-tags")
@click.argument("workflow_id")
@click.argument("json_data", metavar="TAG_IDS_JSON")
@click.pass_context
def workflow_set_tags(ctx: click.Context, workflow_id: str, json_data: str) -> None:
    """Set workflow tags (JSON array of {id} objects)."""
    try:
        tag_ids = json.loads(json_data)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if not isinstance(tag_ids, list):
        raise ValueError("JSON must be an array of {id} objects")
    data = workflows.update_workflow_tags(workflow_id, tag_ids, **_conn(ctx))
    output(data, _json_flag(ctx))


@workflow_.command("transfer")
@click.argument("workflow_id")
@click.argument("project_id")
@click.pass_context
def workflow_transfer(ctx: click.Context, workflow_id: str, project_id: str) -> None:
    """Transfer a workflow to another project."""
    workflows.transfer_workflow(workflow_id, project_id, **_conn(ctx))
    success(f"Workflow {workflow_id} transferred to project {project_id}")
