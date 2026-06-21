# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403


def _safe_filename(name: str) -> str:
    """Sanitize a string for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"[\s/\\]+", "_", name)
    return name[:60] or "workflow"


_INTERNAL_FIELDS = frozenset({"id", "createdAt", "updatedAt", "versionId", "shared"})


def _conn(ctx: click.Context) -> dict[str, str]:
    """Extract connection kwargs from Click context."""
    return {"base_url": ctx.obj["base_url"], "api_key": ctx.obj["api_key"]}


def _json_flag(ctx: click.Context) -> bool:
    return ctx.obj.get("as_json", False)


def _clean_for_api(data: dict[str, Any]) -> dict[str, Any]:
    """Remove n8n internal fields before sending to API."""
    return {k: v for k, v in data.items() if k not in _INTERNAL_FIELDS}


def _auto_snapshot(workflow_id: str, conn: dict[str, str], trigger: str) -> None:
    """Save a version snapshot before modifying a workflow."""
    try:
        wf_data = workflows.get_workflow(workflow_id, **conn)
        ver = versions.save_snapshot(workflow_id, wf_data, trigger)
        click.secho(f"  (snapshot v{ver} saved)", fg="bright_black")
    except (requests.exceptions.RequestException, OSError):
        warn("Could not save snapshot before this change")


def _load_json_arg(value: str) -> dict[str, Any]:
    """Parse a JSON string or read from file if prefixed with @. Must return dict."""
    if value.startswith("@"):
        filepath = Path(value[1:]).resolve()
        try:
            with open(filepath) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"File not found: {filepath}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")
    else:
        try:
            data = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    if not isinstance(data, dict):
        raise ValueError("JSON must be an object, not array or primitive")
    return data


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option("--url", default=None, envvar="N8N_BASE_URL", help="n8n instance URL")
@click.option("--api-key", default=None, envvar="N8N_API_KEY", help="n8n API key")
@click.option("--json", "as_json", is_flag=True, default=False, help="JSON output")
@click.version_option(version=VERSION, prog_name="cli-anything-n8n")
@click.pass_context
def cli(
    ctx: click.Context, url: str | None, api_key: str | None, as_json: bool
) -> None:
    """CLI harness for n8n workflow automation (API v1.1.1, n8n >= 1.0.0)."""
    ctx.ensure_object(dict)
    resolved_url, resolved_key = project.get_connection(url, api_key)
    ctx.obj["base_url"] = resolved_url
    ctx.obj["api_key"] = resolved_key
    ctx.obj["as_json"] = as_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command("repl", hidden=True)
@click.pass_context
def repl(ctx: click.Context) -> None:
    """Start interactive REPL."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import WordCompleter
        from prompt_toolkit.history import InMemoryHistory
    except ImportError:
        click.echo(
            "prompt-toolkit is required for REPL mode. Install: pip install prompt-toolkit"
        )
        sys.exit(1)

    base_url = ctx.obj["base_url"]
    print_banner(base_url or "(not configured)")

    # Build completer from all CLI commands
    words = ["help", "exit", "quit", "status"]
    for name, cmd in cli.commands.items():
        if getattr(cmd, "hidden", False):
            continue
        words.append(name)
        if hasattr(cmd, "commands"):
            for sub in cmd.commands:
                words.append(f"{name} {sub}")
    completer = WordCompleter(words, ignore_case=True)

    session = PromptSession(history=InMemoryHistory(), completer=completer)
    while True:
        try:
            line = session.prompt("n8n> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nBye!")
            break
        if not line:
            continue
        if line in ("exit", "quit", "q"):
            click.echo("Bye!")
            break
        if line == "help":
            click.echo(cli.get_help(ctx))
            continue
        try:
            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()
            cli.main(args, standalone_mode=False, obj=ctx.obj)
        except click.exceptions.UsageError as exc:
            error(str(exc))
        except SystemExit:
            pass
        except Exception as exc:
            error(str(exc))
