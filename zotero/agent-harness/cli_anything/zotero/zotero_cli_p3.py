# ruff: noqa: F403, F405, E501
from .zotero_cli_base import *  # noqa: F403

# fmt: off
from .zotero_cli_p1 import RootCliConfig, _build_runtime_from_config, current_session  # noqa: E402,E501
from .zotero_cli_p2 import _normalize_session_library, _persist_selected_collection, _repl_echo, repl_help_text  # noqa: E402,E501
# fmt: on


def _handle_repl_builtin(
    argv: list[str], skin: ReplSkin, config: RootCliConfig
) -> tuple[bool, int]:
    if not argv:
        return True, 0
    cmd = argv[0]
    state = current_session()
    if cmd in {"exit", "quit"}:
        return True, 1
    if cmd == "help":
        click.echo(repl_help_text())
        return True, 0
    if cmd == "current-library":
        _repl_echo(
            config,
            {"current_library": state.get("current_library")},
            text=f"Current library: {state.get('current_library') or '<unset>'}",
        )
        return True, 0
    if cmd == "current-collection":
        _repl_echo(
            config,
            {"current_collection": state.get("current_collection")},
            text=f"Current collection: {state.get('current_collection') or '<unset>'}",
        )
        return True, 0
    if cmd == "current-item":
        _repl_echo(
            config,
            {"current_item": state.get("current_item")},
            text=f"Current item: {state.get('current_item') or '<unset>'}",
        )
        return True, 0
    if cmd == "status":
        _repl_echo(config, session_mod.build_session_payload(state))
        return True, 0
    if cmd == "history":
        limit = 10
        if len(argv) > 1:
            try:
                limit = max(1, int(argv[1]))
            except ValueError:
                skin.warning(f"history limit must be an integer: {argv[1]}")
                return True, 0
        _repl_echo(config, {"history": state.get("command_history", [])[-limit:]})
        return True, 0
    if cmd == "state-path":
        _repl_echo(
            config,
            {"state_path": str(session_mod.session_state_path())},
            text=str(session_mod.session_state_path()),
        )
        return True, 0
    if cmd == "use-library" and len(argv) > 1:
        library_ref = " ".join(argv[1:])
        try:
            state["current_library"] = _normalize_session_library(
                _build_runtime_from_config(config), library_ref
            )
        except click.ClickException as exc:
            skin.error(exc.format_message())
            return True, 0
        session_mod.save_session_state(state)
        session_mod.append_command_history(f"use-library {library_ref}")
        _repl_echo(
            config,
            session_mod.build_session_payload(state),
            text=f"Current library: {state['current_library']}",
        )
        return True, 0
    if cmd == "use-collection" and len(argv) > 1:
        state["current_collection"] = " ".join(argv[1:])
        session_mod.save_session_state(state)
        session_mod.append_command_history(f"use-collection {' '.join(argv[1:])}")
        _repl_echo(
            config,
            session_mod.build_session_payload(state),
            text=f"Current collection: {state['current_collection']}",
        )
        return True, 0
    if cmd == "use-item" and len(argv) > 1:
        state["current_item"] = " ".join(argv[1:])
        session_mod.save_session_state(state)
        session_mod.append_command_history(f"use-item {' '.join(argv[1:])}")
        _repl_echo(
            config,
            session_mod.build_session_payload(state),
            text=f"Current item: {state['current_item']}",
        )
        return True, 0
    if cmd == "clear-library":
        state["current_library"] = None
        session_mod.save_session_state(state)
        _repl_echo(
            config,
            session_mod.build_session_payload(state),
            text="Current library cleared.",
        )
        return True, 0
    if cmd == "clear-collection":
        state["current_collection"] = None
        session_mod.save_session_state(state)
        _repl_echo(
            config,
            session_mod.build_session_payload(state),
            text="Current collection cleared.",
        )
        return True, 0
    if cmd == "clear-item":
        state["current_item"] = None
        session_mod.save_session_state(state)
        _repl_echo(
            config,
            session_mod.build_session_payload(state),
            text="Current item cleared.",
        )
        return True, 0
    if cmd == "use-selected":
        try:
            runtime = _build_runtime_from_config(config)
            selected = catalog.use_selected_collection(runtime)
        except Exception as exc:
            skin.error(str(exc))
            return True, 0
        persisted_state = _persist_selected_collection(selected)
        session_mod.append_command_history("use-selected")
        if config.json_output:
            _repl_echo(
                config,
                {
                    "selected": selected,
                    "session": session_mod.build_session_payload(persisted_state),
                },
            )
        else:
            _repl_echo(config, selected)
        return True, 0
    return False, 0
