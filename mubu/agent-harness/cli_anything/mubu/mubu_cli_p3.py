# ruff: noqa: F403, F405, E501
from .mubu_cli_base import *  # noqa: F403

# fmt: off
from .mubu_cli_p1 import append_command_history, load_session_state, parse_history_limit, print_repl_banner, print_repl_help, resolve_current_daily_doc_ref, save_session_state, session_state_dir, session_state_path  # noqa: E402,E501
from .mubu_cli_p2 import emit_session_history, emit_session_status, expand_repl_aliases_with_state  # noqa: E402,E501
from .mubu_cli_p4 import dispatch  # noqa: E402,E501
# fmt: on


def handle_repl_builtin(
    argv: list[str],
    session: dict[str, object],
    program_name: str | None = None,
) -> tuple[bool, int]:
    if not argv:
        return True, 0

    command = argv[0]
    if command in {"exit", "quit"}:
        return True, 1
    if command == "help":
        print_repl_help(program_name)
        return True, 0
    if command == "current-doc":
        current_doc = session.get("current_doc")
        click.echo(
            f"Current doc: {current_doc}" if current_doc else "Current doc: <unset>"
        )
        return True, 0
    if command == "current-node":
        current_node = session.get("current_node")
        click.echo(
            f"Current node: {current_node}" if current_node else "Current node: <unset>"
        )
        return True, 0
    if command == "status":
        emit_session_status(session, json_output=False)
        return True, 0
    if command == "history":
        try:
            limit = parse_history_limit(argv)
        except RuntimeError as exc:
            click.echo(str(exc), err=True)
            return True, 0
        emit_session_history(session, limit, json_output=False)
        return True, 0
    if command == "state-path":
        click.echo(f"State path: {session_state_path()}")
        return True, 0
    if command == "clear-doc":
        session["current_doc"] = None
        save_session_state(session)
        append_command_history("clear-doc")
        click.echo("Current doc cleared.")
        return True, 0
    if command == "clear-node":
        session["current_node"] = None
        save_session_state(session)
        append_command_history("clear-node")
        click.echo("Current node cleared.")
        return True, 0
    if command == "use-doc":
        if len(argv) < 2:
            click.echo("use-doc requires a document reference.", err=True)
            return True, 0
        doc_ref = " ".join(argv[1:])
        session["current_doc"] = doc_ref
        save_session_state(session)
        append_command_history(f"use-doc {doc_ref}")
        click.echo(f"Current doc: {doc_ref}")
        return True, 0
    if command == "use-node":
        if len(argv) < 2:
            click.echo("use-node requires a node reference.", err=True)
            return True, 0
        node_ref = " ".join(argv[1:])
        session["current_node"] = node_ref
        save_session_state(session)
        append_command_history(f"use-node {node_ref}")
        click.echo(f"Current node: {node_ref}")
        return True, 0
    if command == "use-daily":
        folder_ref = " ".join(argv[1:]).strip() if len(argv) > 1 else None
        try:
            resolved_folder_ref = mubu_probe.resolve_daily_folder_ref(folder_ref)
            doc_ref = resolve_current_daily_doc_ref(resolved_folder_ref)
        except RuntimeError as exc:
            click.echo(str(exc), err=True)
            return True, 0
        session["current_doc"] = doc_ref
        save_session_state(session)
        append_command_history(f"use-daily {resolved_folder_ref}")
        click.echo(f"Current doc: {doc_ref}")
        return True, 0

    return False, 0


def run_repl(program_name: str | None = None) -> int:
    session = load_session_state()
    skin = ReplSkin(
        "mubu",
        version=__version__,
        history_file=str(session_state_dir() / "history.txt"),
    )
    prompt_session = skin.create_prompt_session()
    print_repl_banner(skin, program_name)
    if session.get("current_doc"):
        click.echo(f"Current doc: {session['current_doc']}")
    if session.get("current_node"):
        click.echo(f"Current node: {session['current_node']}")
    while True:
        try:
            line = skin.get_input(prompt_session)
        except EOFError:
            click.echo()
            skin.print_goodbye()
            return 0
        except KeyboardInterrupt:
            click.echo()
            continue

        line = line.strip()
        if not line:
            continue

        try:
            argv = shlex.split(line)
        except ValueError as exc:
            click.echo(f"parse error: {exc}", err=True)
            continue

        handled, control = handle_repl_builtin(argv, session, program_name)
        if handled:
            if control == 1:
                skin.print_goodbye()
                return 0
            session = load_session_state()
            continue

        argv = expand_repl_aliases_with_state(argv, session)
        result = dispatch(argv)
        if result not in (0, None):
            click.echo(f"command exited with status {result}", err=True)
        session = load_session_state()
