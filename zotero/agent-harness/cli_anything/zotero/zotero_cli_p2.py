# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403

# fmt: off
from .zotero_cli_p1 import RootCliConfig, _json_text, _safe_text_for_stdout, current_session  # noqa: E402,E501
# fmt: on


def repl_help_text() -> str:
    return """Interactive REPL for cli-anything-zotero

Builtins:
  help                    Show this help
  exit, quit              Leave the REPL
  current-library         Show the current library reference
  current-collection      Show the current collection reference
  current-item            Show the current item reference
  use-library <ref>       Persist current library
  use-collection <ref>    Persist current collection
  use-item <ref>          Persist current item
  use-selected            Read and persist the collection selected in Zotero
  clear-library           Clear current library
  clear-collection        Clear current collection
  clear-item              Clear current item
  status                  Show current session status
  history [limit]         Show recent command history
  state-path              Show the session state file path
"""


def _repl_echo(
    config: RootCliConfig, data: Any = None, *, text: str | None = None
) -> None:
    if config.json_output:
        click.echo(_json_text(data))
        return
    if text is not None:
        click.echo(_safe_text_for_stdout(text))
        return
    if isinstance(data, str):
        click.echo(_safe_text_for_stdout(data))
        return
    click.echo(_json_text(data))


def _normalize_session_library(
    runtime: discovery.RuntimeContext, library_ref: str
) -> int:
    try:
        library_id = catalog.resolve_library_id(runtime, library_ref)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    if library_id is None:
        raise click.ClickException("Library reference required")
    return library_id


def _persist_selected_collection(selected: dict[str, Any]) -> dict[str, Any]:
    state = current_session()
    state["current_library"] = selected.get("libraryID")
    state["current_collection"] = selected.get("id")
    session_mod.save_session_state(state)
    return state
