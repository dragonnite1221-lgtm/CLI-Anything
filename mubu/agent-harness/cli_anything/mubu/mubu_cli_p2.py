# ruff: noqa: F403, F405, E501
from .mubu_cli_base import *  # noqa: F403

# fmt: off
from .mubu_cli_p1 import append_command_history, emit_json, root_json_output, session_state_path  # noqa: E402,E501
# fmt: on


def expand_repl_aliases_with_state(
    argv: list[str], session: dict[str, object]
) -> list[str]:
    current_doc = session.get("current_doc")
    current_node = session.get("current_node")
    expanded: list[str] = []
    for token in argv:
        if token in {"@doc", "@current"} and isinstance(current_doc, str):
            expanded.append(current_doc)
        elif token == "@node" and isinstance(current_node, str):
            expanded.append(current_node)
        else:
            expanded.append(token)
    return expanded


def build_session_payload(session: dict[str, object]) -> dict[str, object]:
    history = list(session.get("command_history", []))
    return {
        "current_doc": session.get("current_doc"),
        "current_node": session.get("current_node"),
        "state_path": str(session_state_path()),
        "history_count": len(history),
    }


def emit_session_status(session: dict[str, object], json_output: bool) -> None:
    payload = build_session_payload(session)
    if json_output:
        emit_json(payload)
        return
    current_doc = payload["current_doc"] or "<unset>"
    current_node = payload["current_node"] or "<unset>"
    click.echo(f"Current doc: {current_doc}")
    click.echo(f"Current node: {current_node}")
    click.echo(f"State path: {payload['state_path']}")
    click.echo(f"History count: {payload['history_count']}")


def emit_session_history(
    session: dict[str, object], limit: int, json_output: bool
) -> None:
    history = list(session.get("command_history", []))[-limit:]
    if json_output:
        emit_json({"history": history})
        return
    if not history:
        click.echo("History: <empty>")
        return
    click.echo("History:")
    for index, entry in enumerate(history, start=max(1, len(history) - limit + 1)):
        click.echo(f"  {index}. {entry}")


def invoke_probe_command(
    ctx: click.Context | None, command_name: str, probe_args: Sequence[str]
) -> int:
    argv = [command_name, *list(probe_args)]
    if root_json_output(ctx) and "--json" not in argv:
        argv.append("--json")
    try:
        result = mubu_probe.main(argv)
    except SystemExit as exc:
        result = exc.code if isinstance(exc.code, int) else 1
    if result in (0, None) and "--help" not in argv and "-h" not in argv:
        append_command_history(" ".join(argv))
    return int(result or 0)
