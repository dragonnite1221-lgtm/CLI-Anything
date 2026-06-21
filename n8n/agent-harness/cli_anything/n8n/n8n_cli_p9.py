# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag, cli  # noqa: E402,E501
from .n8n_cli_p8 import variable_  # noqa: E402,E501
# fmt: on


@variable_.command("update")
@click.argument("variable_id")
@click.argument("key")
@click.argument("value")
@click.pass_context
def variable_update(ctx: click.Context, variable_id: str, key: str, value: str) -> None:
    """Update a variable."""
    data = variables.update_variable(variable_id, key, value, **_conn(ctx))
    output(data, _json_flag(ctx))


@variable_.command("delete")
@click.argument("variable_id")
@click.pass_context
def variable_delete(ctx: click.Context, variable_id: str) -> None:
    """Delete a variable."""
    variables.delete_variable(variable_id, **_conn(ctx))
    success(f"Variable {variable_id} deleted")


@cli.group("tag")
def tag_() -> None:
    """Tag management."""


@tag_.command("list")
@click.option("--limit", default=50, type=int)
@click.pass_context
def tag_list(ctx: click.Context, limit: int) -> None:
    """List all tags."""
    data = tags.list_tags(**_conn(ctx), limit=limit)
    output(data, _json_flag(ctx))


@tag_.command("get")
@click.argument("tag_id")
@click.pass_context
def tag_get(ctx: click.Context, tag_id: str) -> None:
    """Get tag details."""
    data = tags.get_tag(tag_id, **_conn(ctx))
    output(data, _json_flag(ctx))


@tag_.command("create")
@click.argument("name")
@click.pass_context
def tag_create(ctx: click.Context, name: str) -> None:
    """Create a tag."""
    data = tags.create_tag(name, **_conn(ctx))
    output(data, _json_flag(ctx))


@tag_.command("update")
@click.argument("tag_id")
@click.argument("name")
@click.pass_context
def tag_update(ctx: click.Context, tag_id: str, name: str) -> None:
    """Update a tag name."""
    data = tags.update_tag(tag_id, name, **_conn(ctx))
    output(data, _json_flag(ctx))


@tag_.command("delete")
@click.argument("tag_id")
@click.pass_context
def tag_delete(ctx: click.Context, tag_id: str) -> None:
    """Delete a tag."""
    tags.delete_tag(tag_id, **_conn(ctx))
    success(f"Tag {tag_id} deleted")


@cli.group("template")
def template_() -> None:
    """Browse and deploy templates from n8n.io (2,700+ templates)."""


@template_.command("search")
@click.argument("query")
@click.option("--limit", default=10, type=int, help="Max results")
@click.pass_context
def template_search(ctx: click.Context, query: str, limit: int) -> None:
    """Search templates on n8n.io by keyword."""
    data = templates.search_templates(query, limit=limit)
    wfs = data.get("workflows", [])

    if _json_flag(ctx):
        output(data, True)
        return

    total = data.get("totalWorkflows", 0)
    click.secho(
        f"\n  {total} templates found for '{query}' (showing {len(wfs)}):\n", fg="cyan"
    )
    for w in wfs:
        views = w.get("totalViews", 0)
        click.echo(
            f"    {click.style(str(w.get('id', '?')), fg='cyan'):>8s}  {w.get('name', '?')[:60]}"
        )
        click.secho(
            f"             {views:,} views  by {w.get('user', {}).get('username', '?')}",
            fg="bright_black",
        )
    click.echo()


@template_.command("get")
@click.argument("template_id", type=int)
@click.pass_context
def template_get(ctx: click.Context, template_id: int) -> None:
    """Get template details from n8n.io."""
    data = templates.get_template(template_id)
    wf = data.get("workflow", {})
    if _json_flag(ctx):
        output(data, True)
        return
    click.secho(
        f"\n  Template #{template_id}: {wf.get('name', '?')}", fg="cyan", bold=True
    )
    click.echo(f"  Nodes: {len(wf.get('nodes', []))}")
    click.echo(f"  Views: {wf.get('totalViews', 0):,}")
    desc = data.get("description", "")
    if desc:
        click.echo(f"  Description: {desc[:200]}")
    click.echo()
