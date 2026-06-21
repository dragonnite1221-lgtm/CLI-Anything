# ruff: noqa: F403, F405, E501
from .mubu_cli_base import *  # noqa: F403

# fmt: off
from .mubu_cli_p1 import append_command_history, emit_json, load_session_state, resolve_current_daily_doc_ref, root_json_output, save_session_state, session_state_path  # noqa: E402,E501
from .mubu_cli_p2 import emit_session_history, emit_session_status, invoke_probe_command  # noqa: E402,E501
from .mubu_cli_p3 import run_repl  # noqa: E402,E501
from .mubu_cli_p4 import cli, dispatch, mutate, session  # noqa: E402,E501
# fmt: on


@mutate.command("delete-node", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def delete_node(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Build or execute one node deletion against the live Mubu API."""
    return invoke_probe_command(ctx, "delete-node", probe_args)


@mutate.command("update-text", context_settings=CONTEXT_SETTINGS, add_help_option=False)
@click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def update_text(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
    """Build or execute one text update against the live Mubu API."""
    return invoke_probe_command(ctx, "update-text", probe_args)


@session.command("status")
@click.option("--json", "json_output", is_flag=True, help="Emit session state as JSON.")
@click.pass_context
def session_status(ctx: click.Context, json_output: bool) -> int:
    """Show the current session state."""
    emit_session_status(
        load_session_state(), json_output=json_output or root_json_output(ctx)
    )
    return 0


@session.command("state-path")
@click.option(
    "--json", "json_output", is_flag=True, help="Emit the session state path as JSON."
)
@click.pass_context
def state_path_command(ctx: click.Context, json_output: bool) -> int:
    """Show the session state file path."""
    payload = {"state_path": str(session_state_path())}
    if json_output or root_json_output(ctx):
        emit_json(payload)
    else:
        click.echo(payload["state_path"])
    return 0


@session.command("use-doc")
@click.argument("doc_ref", nargs=-1)
def use_doc(doc_ref: tuple[str, ...]) -> int:
    """Persist the current document reference."""
    if not doc_ref:
        raise click.UsageError("use-doc requires a document reference.")
    value = " ".join(doc_ref)
    session_state = load_session_state()
    session_state["current_doc"] = value
    save_session_state(session_state)
    append_command_history(f"session use-doc {value}")
    click.echo(f"Current doc: {value}")
    return 0


@session.command("use-node")
@click.argument("node_ref", nargs=-1)
def use_node(node_ref: tuple[str, ...]) -> int:
    """Persist the current node reference."""
    if not node_ref:
        raise click.UsageError("use-node requires a node reference.")
    value = " ".join(node_ref)
    session_state = load_session_state()
    session_state["current_node"] = value
    save_session_state(session_state)
    append_command_history(f"session use-node {value}")
    click.echo(f"Current node: {value}")
    return 0


@session.command("use-daily")
@click.argument("folder_ref", nargs=-1)
def use_daily(folder_ref: tuple[str, ...]) -> int:
    """Resolve and persist the current daily document reference."""
    raw_value = " ".join(folder_ref).strip() if folder_ref else None
    try:
        resolved_folder_ref = mubu_probe.resolve_daily_folder_ref(raw_value)
        doc_ref = resolve_current_daily_doc_ref(resolved_folder_ref)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    session_state = load_session_state()
    session_state["current_doc"] = doc_ref
    save_session_state(session_state)
    append_command_history(f"session use-daily {resolved_folder_ref}")
    click.echo(f"Current doc: {doc_ref}")
    return 0


@session.command("clear-doc")
def clear_doc() -> int:
    """Clear the current document reference."""
    session_state = load_session_state()
    session_state["current_doc"] = None
    save_session_state(session_state)
    append_command_history("session clear-doc")
    click.echo("Current doc cleared.")
    return 0


@session.command("clear-node")
def clear_node() -> int:
    """Clear the current node reference."""
    session_state = load_session_state()
    session_state["current_node"] = None
    save_session_state(session_state)
    append_command_history("session clear-node")
    click.echo("Current node cleared.")
    return 0


@session.command("history")
@click.option(
    "--limit",
    default=10,
    show_default=True,
    type=int,
    help="How many recent entries to show.",
)
@click.option(
    "--json", "json_output", is_flag=True, help="Emit command history as JSON."
)
@click.pass_context
def history_command(ctx: click.Context, limit: int, json_output: bool) -> int:
    """Show recent command history stored in session state."""
    emit_session_history(
        load_session_state(),
        max(1, limit),
        json_output=json_output or root_json_output(ctx),
    )
    return 0


@cli.command("repl", help=REPL_COMMAND_HELP)
@click.pass_context
def repl_command(ctx: click.Context) -> int:
    """Interactive REPL for the Mubu CLI."""
    root = ctx.find_root()
    program_name = None
    if root is not None and root.obj is not None:
        program_name = root.obj.get("prog_name")
    return run_repl(program_name)


def create_legacy_command(command_name: str, help_text: str) -> click.Command:
    @click.command(
        name=command_name,
        help=help_text,
        context_settings=CONTEXT_SETTINGS,
        add_help_option=False,
    )
    @click.argument("probe_args", nargs=-1, type=click.UNPROCESSED)
    @click.pass_context
    def legacy(ctx: click.Context, probe_args: tuple[str, ...]) -> int:
        return invoke_probe_command(ctx, command_name, probe_args)

    return legacy


for _command_name, _help_text in LEGACY_COMMANDS.items():
    cli.add_command(create_legacy_command(_command_name, _help_text))


def entrypoint(argv: list[str] | None = None) -> int:
    return dispatch(argv, prog_name=sys.argv[0])
