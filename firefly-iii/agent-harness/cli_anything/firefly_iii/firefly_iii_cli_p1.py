# ruff: noqa: F403, F405, E501
from .firefly_iii_cli_base import *  # noqa: F403

# fmt: off
from .firefly_iii_cli_p2 import repl  # noqa: E402,E501
# fmt: on


def get_backend() -> FireflyIIIBackend:
    """Get backend instance, raise error if not initialized"""
    if _backend is None:
        raise RuntimeError("Backend not initialized, please check configuration")
    return _backend


def output(data: Any):
    """Unified output format: JSON or human-readable"""
    if _json_output:
        try:
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        except UnicodeEncodeError:
            # If console does not support Unicode, use ASCII encoding
            click.echo(json.dumps(data, indent=2, ensure_ascii=True))
    else:
        # Human-readable format
        if isinstance(data, dict):
            if "data" in data:
                # Firefly III API standard response format
                items = data["data"]
                if isinstance(items, list):
                    for item in items:
                        attrs = item.get("attributes", {})
                        name = attrs.get("name", item.get("id"))
                        click.echo(f"  {item.get('id', 'N/A')}: {name}")
                else:
                    attrs = items.get("attributes", {})
                    for key, value in attrs.items():
                        click.echo(f"  {key}: {value}")
            elif "meta" in data:
                # Response with metadata
                click.echo(
                    f"  Total: {data.get('meta', {}).get('pagination', {}).get('total', 'N/A')}"
                )
            else:
                for key, value in data.items():
                    click.echo(f"  {key}: {value}")
        elif isinstance(data, list):
            for item in data:
                click.echo(f"  - {item}")
        else:
            click.echo(f"  {data}")


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option("--base-url", help="Firefly III base URL")
@click.option("--pat", help="Personal Access Token")
@click.option(
    "--preset",
    default="default",
    type=click.Choice(
        ["default", "full", "basic", "budget", "reporting", "admin", "automation"]
    ),
    help="Tool preset",
)
@click.pass_context
def cli(ctx, use_json, base_url, pat, preset):
    """Firefly III CLI - Personal finance management.

    Based on CLI-Anything spec, converted from MCP mode to stateless CLI mode,
    avoiding Node residual process issues.
    """
    global _json_output, _backend, _repl_skin

    _json_output = use_json

    # Get configuration from arguments and environment variables
    base_url = base_url or os.environ.get("FIREFLY_III_BASE_URL")
    pat = pat or os.environ.get("FIREFLY_III_PAT")

    if not base_url or not pat:
        click.echo(
            "Error: FIREFLY_III_BASE_URL and FIREFLY_III_PAT are required", err=True
        )
        click.echo("\nUsage:", err=True)
        click.echo("  cli-anything-firefly-iii --base-url URL --pat TOKEN", err=True)
        click.echo("\nOr set environment variables:", err=True)
        click.echo(
            "  export FIREFLY_III_BASE_URL=https://firefly.yourdomain.com", err=True
        )
        click.echo("  export FIREFLY_III_PAT=your-personal-access-token", err=True)
        ctx.exit(1)

    try:
        _backend = FireflyIIIBackend(base_url, pat)
        _repl_skin = ReplSkin("firefly-iii", "1.0.0")
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)

    # Enter REPL when no subcommand is provided
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
