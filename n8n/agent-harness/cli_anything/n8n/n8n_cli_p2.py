# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _conn, _json_flag, cli  # noqa: E402,E501
# fmt: on


@cli.group("config")
def config_() -> None:
    """Configuration management."""


@config_.command("show")
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show current configuration (API key is always masked)."""
    cfg = project.load_config()
    masked = {**cfg}
    if masked.get("api_key"):
        masked["api_key"] = "****configured****"
    output(masked, _json_flag(ctx))


@config_.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set a config value (base_url, api_key)."""
    cfg = project.load_config()
    if key not in ("base_url", "api_key"):
        error(f"Unknown config key: {key}. Use: base_url, api_key")
        return
    if key == "base_url":
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            error(f"Invalid URL: {value} (must include http:// or https://)")
            return
    cfg[key] = value
    path = project.save_config(cfg)
    success(f"Saved {key} to {path}")


@config_.command("test")
@click.pass_context
def config_test(ctx: click.Context) -> None:
    """Test connection to your n8n instance."""
    conn = _conn(ctx)
    if not conn["base_url"]:
        error(
            "No URL configured. Run: cli-anything-n8n config set base_url https://..."
        )
        return
    if not conn["api_key"]:
        error(
            "No API key configured. Run: cli-anything-n8n config set api_key YOUR_KEY"
        )
        return
    try:
        workflows.list_workflows(**conn, limit=1)
        success(f"Connected to {conn['base_url']}")
        click.echo("    API is responding.")
    except requests.exceptions.ConnectionError:
        error(f"Cannot connect to {conn['base_url']}")
    except requests.exceptions.HTTPError as exc:
        status_code = exc.response.status_code
        if status_code == 401:
            error("API key is invalid or expired.")
        elif status_code == 403:
            error("API key does not have permission.")
        else:
            error(f"API returned {status_code}")


@cli.command("completions")
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
def install_completions(shell: str) -> None:
    """Generate shell completion script (bash, zsh, fish)."""
    import subprocess

    env_var = "_CLI_ANYTHING_N8N_COMPLETE"
    shell_map = {"bash": "bash_source", "zsh": "zsh_source", "fish": "fish_source"}
    import os

    result = subprocess.run(
        [sys.executable, "-m", "cli_anything.n8n"],
        capture_output=True,
        text=True,
        timeout=5,
        env={**os.environ, env_var: shell_map[shell]},
    )
    if result.stdout:
        click.echo(result.stdout)
        click.echo("\n# To install, run:", err=True)
        if shell == "bash":
            click.echo("# cli-anything-n8n completions bash >> ~/.bashrc", err=True)
        elif shell == "zsh":
            click.echo("# cli-anything-n8n completions zsh >> ~/.zshrc", err=True)
        elif shell == "fish":
            click.echo(
                "# cli-anything-n8n completions fish > ~/.config/fish/completions/cli-anything-n8n.fish",
                err=True,
            )
    else:
        success(
            f"Shell completions for {shell} generated. Paste output into your shell config."
        )


@cli.group("workflow")
def workflow_() -> None:
    """Workflow management."""


@workflow_.command("list")
@click.option("--active/--inactive", default=None, help="Filter by active status")
@click.option(
    "--tags", "tag_filter", default=None, help="Filter by tag names (comma-separated)"
)
@click.option("--name", default=None, help="Filter by name (contains)")
@click.option("--limit", default=50, type=int, help="Max results")
@click.option("--cursor", default=None, help="Pagination cursor")
@click.pass_context
def workflow_list(
    ctx: click.Context,
    active: bool | None,
    tag_filter: str | None,
    name: str | None,
    limit: int,
    cursor: str | None,
) -> None:
    """List workflows."""
    data = workflows.list_workflows(
        **_conn(ctx),
        active=active,
        tags=tag_filter,
        name=name,
        limit=limit,
        cursor=cursor,
    )
    output(data, _json_flag(ctx))
