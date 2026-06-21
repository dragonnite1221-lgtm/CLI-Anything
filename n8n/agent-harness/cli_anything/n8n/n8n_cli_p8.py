# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag, _load_json_arg, cli  # noqa: E402,E501
# fmt: on


@cli.command("status")
@click.pass_context
def status_dashboard(ctx: click.Context) -> None:
    """Show a quick overview of your n8n instance."""
    conn = _conn(ctx)
    as_json = _json_flag(ctx)

    wf_data = workflows.list_workflows(**conn, limit=200)
    wf_list = wf_data.get("data", []) if isinstance(wf_data, dict) else wf_data
    active_wfs = [w for w in wf_list if w.get("active")]
    inactive_wfs = [w for w in wf_list if not w.get("active")]

    exec_data = executions.list_executions(**conn, limit=10)
    exec_list = exec_data.get("data", []) if isinstance(exec_data, dict) else exec_data
    errors = [e for e in exec_list if e.get("status") == "error"]

    if as_json:
        output(
            {
                "workflows": {
                    "total": len(wf_list),
                    "active": len(active_wfs),
                    "inactive": len(inactive_wfs),
                },
                "recent_executions": len(exec_list),
                "recent_errors": len(errors),
                "last_error": errors[0] if errors else None,
            },
            True,
        )
        return

    click.echo()
    click.secho("  n8n Status Dashboard", fg="cyan", bold=True)
    click.secho("  " + "=" * 40, fg="cyan")
    click.echo()

    click.secho("  Workflows", fg="cyan", bold=True)
    click.echo(f"    Total:    {len(wf_list)}")
    click.secho(f"    Active:   {len(active_wfs)}", fg="green")
    click.echo(f"    Inactive: {len(inactive_wfs)}")
    click.echo()

    click.secho("  Recent Executions (last 10)", fg="cyan", bold=True)
    if not exec_list:
        click.secho("    No executions found.", fg="bright_black")
    else:
        for e in exec_list:
            status = e.get("status", "?")
            color = {
                "success": "green",
                "error": "red",
                "running": "yellow",
                "waiting": "cyan",
            }.get(status, "white")
            started = str(e.get("startedAt", ""))[:19].replace("T", " ")
            click.echo(
                f"    {e.get('id', '?'):>8s}  {click.style(status.ljust(8), fg=color)}  wf:{e.get('workflowId', '?'):<16s}  {started}"
            )
    click.echo()

    if errors:
        click.secho(
            f"  Errors: {len(errors)} in last 10 executions", fg="red", bold=True
        )
        last = errors[0]
        click.echo(
            f"    Last error: execution {last.get('id')} (wf:{last.get('workflowId')}) at {str(last.get('startedAt', ''))[:19]}"
        )
    else:
        click.secho("  No errors in recent executions", fg="green")
    click.echo()


@cli.group("credential")
def credential_() -> None:
    """Credential management (limited by n8n API — no list/update)."""


@credential_.command("create")
@click.argument("json_data")
@click.pass_context
def credential_create(ctx: click.Context, json_data: str) -> None:
    """Create a credential from JSON."""
    data = credentials.create_credential(_load_json_arg(json_data), **_conn(ctx))
    output(data, _json_flag(ctx))


@credential_.command("delete")
@click.argument("credential_id")
@click.confirmation_option(prompt="Are you sure you want to delete this credential?")
@click.pass_context
def credential_delete(ctx: click.Context, credential_id: str) -> None:
    """Delete a credential."""
    credentials.delete_credential(credential_id, **_conn(ctx))
    success(f"Credential {credential_id} deleted")


@credential_.command("schema")
@click.argument("credential_type")
@click.pass_context
def credential_schema(ctx: click.Context, credential_type: str) -> None:
    """Get credential schema for a type."""
    data = credentials.get_credential_schema(credential_type, **_conn(ctx))
    output(data, _json_flag(ctx))


@credential_.command("transfer")
@click.argument("credential_id")
@click.argument("project_id")
@click.pass_context
def credential_transfer(
    ctx: click.Context, credential_id: str, project_id: str
) -> None:
    """Transfer a credential to another project."""
    credentials.transfer_credential(credential_id, project_id, **_conn(ctx))
    success(f"Credential {credential_id} transferred to project {project_id}")


@cli.group("variable")
def variable_() -> None:
    """Variable management."""


@variable_.command("list")
@click.pass_context
def variable_list(ctx: click.Context) -> None:
    """List all variables."""
    data = variables.list_variables(**_conn(ctx))
    output(data, _json_flag(ctx))


@variable_.command("create")
@click.argument("key")
@click.argument("value")
@click.pass_context
def variable_create(ctx: click.Context, key: str, value: str) -> None:
    """Create a variable."""
    data = variables.create_variable(key, value, **_conn(ctx))
    output(data, _json_flag(ctx))
