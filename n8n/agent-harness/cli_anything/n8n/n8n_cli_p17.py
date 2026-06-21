# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag, cli  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
from .n8n_cli_p16 import node_  # noqa: E402,E501
# fmt: on


@node_.command("info")
@click.argument("package_name")
@click.pass_context
def node_info(ctx: click.Context, package_name: str) -> None:
    """Get detailed info about an n8n node package from npm."""
    data = nodes.get_node_info(package_name)

    if _json_flag(ctx):
        output(data, True)
        return

    click.secho(
        f"\n  {data.get('name', '?')} v{data.get('version', '?')}", fg="cyan", bold=True
    )
    click.echo(f"  {data.get('description', '')}")
    click.echo(f"  Author: {data.get('author', '?')}")
    click.echo(f"  License: {data.get('license', '?')}")
    if data.get("homepage"):
        click.echo(f"  Homepage: {data.get('homepage', '')}")
    click.echo(f"  npm: {data.get('npm_url', '')}")

    n8n_nodes = data.get("n8n_nodes", [])
    if n8n_nodes and isinstance(n8n_nodes, list):
        click.secho(f"\n  Nodes provided ({len(n8n_nodes)}):", fg="cyan")
        for n in n8n_nodes:
            click.echo(f"    - {n}")

    n8n_creds = data.get("n8n_credentials", [])
    if n8n_creds and isinstance(n8n_creds, list):
        click.secho("\n  Credentials:", fg="cyan")
        for c in n8n_creds:
            click.echo(f"    - {c}")

    click.secho("\n  Install:", fg="green")
    click.echo(f"    {data.get('install_cmd', 'N/A')}")
    click.echo()


@workflow_.command("scaffold")
@click.argument(
    "pattern",
    type=click.Choice(["webhook", "api", "database", "ai-agent", "scheduled"]),
)
@click.option("--name", default=None, help="Custom workflow name")
@click.option("--deploy", is_flag=True, default=False, help="Deploy directly to n8n")
@click.option("-o", "--output", "out_path", default=None, help="Save to file")
@click.pass_context
def workflow_scaffold(
    ctx: click.Context,
    pattern: str,
    name: str | None,
    deploy: bool,
    out_path: str | None,
) -> None:
    """Generate a workflow from a proven pattern.

    Patterns: webhook, api, database, ai-agent, scheduled.
    """
    wf = scaffolds.get_scaffold(pattern, name=name)

    if _json_flag(ctx) and not deploy and not out_path:
        output(wf, True)
        return

    if deploy:
        result = workflows.create_workflow(wf, **_conn(ctx))
        success(f"Deployed '{wf['name']}' as workflow {result.get('id', '?')}")
        output(result, _json_flag(ctx))
    elif out_path:
        Path(out_path).write_text(json.dumps(wf, indent=2, default=str))
        success(f"Saved scaffold to {out_path}")
    else:
        click.secho(f"\n  Pattern: {pattern}", fg="cyan", bold=True)
        click.echo(f"  Name: {wf.get('name', '?')}")
        click.echo(f"  Nodes: {len(wf.get('nodes', []))}")
        for n in wf.get("nodes", []):
            if not isinstance(n, dict):
                continue
            click.echo(f"    - {n.get('name', '?')} ({n.get('type', '?')})")
        click.echo(
            "\n  Use --deploy to create in n8n, --output to save to file, or --json to see full JSON"
        )
        click.echo()


@workflow_.command("patterns")
@click.pass_context
def workflow_patterns(ctx: click.Context) -> None:
    """List available scaffold patterns."""
    patterns = scaffolds.list_patterns()
    if _json_flag(ctx):
        output(patterns, True)
        return
    click.secho("\n  Available workflow patterns:\n", fg="cyan", bold=True)
    for p in patterns:
        click.echo(
            f"    {click.style(p.get('name', '?'), fg='cyan'):>20s}  {p.get('description', '')}"
        )
    click.echo("\n  Usage: cli-anything-n8n workflow scaffold <pattern> [--deploy]")
    click.echo()


@cli.command("expression")
@click.argument("expr")
@click.pass_context
def expression_validate(ctx: click.Context, expr: str) -> None:
    """Validate an n8n expression (e.g., '={{$json.name}}')."""
    result = expressions.validate_expression(expr)

    if _json_flag(ctx):
        output(
            {
                "valid": result.valid,
                "expression": result.expression,
                "issues": result.issues,
                "warnings": result.warnings,
            },
            True,
        )
        return

    if result.valid and not result.warnings:
        success(f"Expression is valid: {expr}")
        return

    if result.issues:
        click.secho("\n  INVALID expression:\n", fg="red", bold=True)
        for issue in result.issues:
            click.secho(f"    {issue}", fg="red")

    if result.warnings:
        click.secho("\n  Warnings:", fg="yellow")
        for w in result.warnings:
            click.secho(f"    {w}", fg="yellow")

    if result.valid:
        success("Expression is syntactically valid (with warnings)")
    click.echo()
