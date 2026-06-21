# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403

# fmt: off
from .zotero_cli_p1 import _current_cli_config, current_runtime, current_session  # noqa: E402,E501
from .zotero_cli_p2 import _normalize_session_library, _persist_selected_collection  # noqa: E402,E501
from .zotero_cli_p4 import cli, run_repl  # noqa: E402,E501
from .zotero_cli_p5 import dispatch, emit  # noqa: E402,E501
# fmt: on


@cli.group()
def session() -> None:
    """Session and REPL context commands."""


@session.command("status")
@click.pass_context
def session_status(ctx: click.Context) -> int:
    emit(ctx, session_mod.build_session_payload(current_session()))
    return 0


@session.command("use-library")
@click.argument("library_ref")
@click.pass_context
def session_use_library(ctx: click.Context, library_ref: str) -> int:
    state = current_session()
    state["current_library"] = _normalize_session_library(
        current_runtime(ctx), library_ref
    )
    session_mod.save_session_state(state)
    session_mod.append_command_history(f"session use-library {library_ref}")
    emit(ctx, session_mod.build_session_payload(state))
    return 0


@session.command("use-collection")
@click.argument("collection_ref")
@click.pass_context
def session_use_collection(ctx: click.Context, collection_ref: str) -> int:
    state = current_session()
    state["current_collection"] = collection_ref
    session_mod.save_session_state(state)
    session_mod.append_command_history(f"session use-collection {collection_ref}")
    emit(ctx, session_mod.build_session_payload(state))
    return 0


@session.command("use-item")
@click.argument("item_ref")
@click.pass_context
def session_use_item(ctx: click.Context, item_ref: str) -> int:
    state = current_session()
    state["current_item"] = item_ref
    session_mod.save_session_state(state)
    session_mod.append_command_history(f"session use-item {item_ref}")
    emit(ctx, session_mod.build_session_payload(state))
    return 0


@session.command("use-selected")
@click.pass_context
def session_use_selected(ctx: click.Context) -> int:
    selected = catalog.use_selected_collection(current_runtime(ctx))
    state = _persist_selected_collection(selected)
    session_mod.append_command_history("session use-selected")
    emit(
        ctx, {"selected": selected, "session": session_mod.build_session_payload(state)}
    )
    return 0


@session.command("clear-library")
@click.pass_context
def session_clear_library(ctx: click.Context) -> int:
    state = current_session()
    state["current_library"] = None
    session_mod.save_session_state(state)
    session_mod.append_command_history("session clear-library")
    emit(ctx, session_mod.build_session_payload(state))
    return 0


@session.command("clear-collection")
@click.pass_context
def session_clear_collection(ctx: click.Context) -> int:
    state = current_session()
    state["current_collection"] = None
    session_mod.save_session_state(state)
    session_mod.append_command_history("session clear-collection")
    emit(ctx, session_mod.build_session_payload(state))
    return 0


@session.command("clear-item")
@click.pass_context
def session_clear_item(ctx: click.Context) -> int:
    state = current_session()
    state["current_item"] = None
    session_mod.save_session_state(state)
    session_mod.append_command_history("session clear-item")
    emit(ctx, session_mod.build_session_payload(state))
    return 0


@session.command("history")
@click.option("--limit", default=10, show_default=True, type=int)
@click.pass_context
def session_history(ctx: click.Context, limit: int) -> int:
    emit(ctx, {"history": current_session().get("command_history", [])[-limit:]})
    return 0


@cli.command("repl")
@click.pass_context
def repl_command(ctx: click.Context) -> int:
    """Start the interactive REPL."""
    return run_repl(_current_cli_config(ctx))


def entrypoint(argv: list[str] | None = None) -> int:
    return dispatch(argv, prog_name=sys.argv[0])
