# ruff: noqa: F403, F405, E501
from .mubu_cli_base import *  # noqa: F403

# fmt: off
from .mubu_cli_p1 import normalize_program_name  # noqa: E402,E501
from .mubu_cli_p2 import expand_repl_aliases_with_state, invoke_probe_command  # noqa: E402,E501
from .mubu_cli_p3 import run_repl  # noqa: E402,E501
# fmt: on


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Emit JSON output for wrapped probe commands when supported.",
)
@click.pass_context
def cli(ctx: click.Context, json_output: bool) -> int:
    """Agent-native CLI for the Mubu desktop app with REPL and grouped command domains."""
    ctx.ensure_object(dict)
    ctx.obj["json_output"] = json_output
    ctx.obj["prog_name"] = normalize_program_name(ctx.info_name)
    if ctx.invoked_subcommand is None:
        return run_repl(ctx.obj["prog_name"])
    return 0


@cli.group(context_settings=CONTEXT_SETTINGS)
def discover() -> None:
    """Discovery commands for folders, documents, recency, and daily-document resolution."""


@discover.command("folders", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def folders(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """List folder metadata from local RxDB storage."""
    return invoke_probe_command(ctx, "folders", probe_args)


@cli.group()
def session() -> None:
    """Session and state commands for current document/node context and local command history."""


def dispatch(argv: list[str] | None = None, prog_name: str | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    normalized_prog_name = normalize_program_name(prog_name or sys.argv[0])
    try:
        result = cli.main(
            args=args, prog_name=normalized_prog_name, standalone_mode=False
        )
    except click.exceptions.Exit as exc:
        return int(exc.exit_code)
    except click.ClickException as exc:
        exc.show()
        return int(exc.exit_code)
    return int(result or 0)


def expand_repl_aliases(argv: list[str], current_doc: str | None) -> list[str]:
    return expand_repl_aliases_with_state(
        argv, {"current_doc": current_doc, "current_node": None}
    )


@discover.command("docs", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def discover_docs(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """List latest known document snapshots from local backups."""
    return invoke_probe_command(ctx, "docs", probe_args)


@discover.command(
    "folder-docs", context_settings=CONTEXT_SETTINGS, add_help_option=False
)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def folder_docs(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """List document metadata for one folder."""
    return invoke_probe_command(ctx, "folder-docs", probe_args)


@discover.command("path-docs", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def path_docs(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """List documents for one folder path or folder id."""
    return invoke_probe_command(ctx, "path-docs", probe_args)


@discover.command("recent", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def recent(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """List recently active documents using backups, metadata, and sync logs."""
    return invoke_probe_command(ctx, "recent", probe_args)


@discover.command("daily", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def daily(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Find Daily-style folders and list the documents inside them."""
    return invoke_probe_command(ctx, "daily", probe_args)


@discover.command(
    "daily-current", context_settings=CONTEXT_SETTINGS, add_help_option=False
)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def daily_current(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Resolve the current daily document from one Daily-style folder."""
    return invoke_probe_command(ctx, "daily-current", probe_args)


@cli.group(context_settings=CONTEXT_SETTINGS)
def inspect() -> None:
    """Inspection commands for tree views, search, links, sync events, and live node targeting."""


@inspect.command("show", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def show(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Show the latest backup tree for one document."""
    return invoke_probe_command(ctx, "show", probe_args)


@inspect.command("search", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def search(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Search latest backups for matching node text or note content."""
    return invoke_probe_command(ctx, "search", probe_args)


@inspect.command("changes", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def changes(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Parse recent client-sync change events from local logs."""
    return invoke_probe_command(ctx, "changes", probe_args)


@inspect.command("links", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def links(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Extract outbound Mubu document links from one document backup."""
    return invoke_probe_command(ctx, "links", probe_args)


@inspect.command("open-path", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def open_path(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Open one document by full path, suffix path, title, or doc id."""
    return invoke_probe_command(ctx, "open-path", probe_args)


@inspect.command("doc-nodes", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def doc_nodes(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """List live document nodes with node ids and update-target paths."""
    return invoke_probe_command(ctx, "doc-nodes", probe_args)


@inspect.command(
    "daily-nodes", context_settings=CONTEXT_SETTINGS, add_help_option=False
)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def daily_nodes(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """List live nodes from the current daily document in one step."""
    return invoke_probe_command(ctx, "daily-nodes", probe_args)


@cli.group(context_settings=CONTEXT_SETTINGS)
def mutate() -> None:
    """Mutation commands for dry-run-first atomic live edits against the Mubu API."""


@mutate.command(
    "create-child", context_settings=CONTEXT_SETTINGS, add_help_option=False
)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def create_child(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Build or execute one child-node creation against the live Mubu API."""
    return invoke_probe_command(ctx, "create-child", probe_args)
