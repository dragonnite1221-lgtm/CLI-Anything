"""Interactive REPL command registration for the browser CLI."""

from __future__ import annotations

import shlex

import click

from cli_anything.browser.utils.repl_skin import ReplSkin


REPL_COMMANDS = {
    "page": "open|reload|back|forward|info",
    "fs": "ls|cd|cat|grep|pwd",
    "act": "click|type",
    "session": "status|daemon-start|daemon-stop",
    "secure": "status|start|stop",
    "help": "Show this help",
    "quit": "Exit REPL",
}


def register_repl_command(root, get_session, is_json_output, set_repl_mode):
    """Register and return the root CLI's interactive REPL command."""

    @root.command()
    def repl():
        """Start an interactive REPL session."""

        set_repl_mode(True)
        skin = ReplSkin("browser", version="1.0.0")
        skin.print_banner()
        prompt_session = skin.create_prompt_session()
        try:
            while True:
                context = _prompt_context(get_session())
                line = skin.get_input(prompt_session, context=context)
                if not line:
                    continue
                if line.lower() in {"quit", "exit", "q"}:
                    skin.print_goodbye()
                    return
                if line.lower() == "help":
                    skin.help(REPL_COMMANDS)
                    continue
                _run_line(root, line, is_json_output, skin)
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
        finally:
            set_repl_mode(False)

    return repl


def _prompt_context(session) -> str:
    context = session.working_dir or "/"
    if session.current_url:
        url = session.current_url
        context = f"{url[:40] + '...' if len(url) > 40 else url} {context}"
    return context


def _run_line(root, line: str, is_json_output, skin) -> None:
    try:
        arguments = shlex.split(line)
    except ValueError:
        arguments = line.split()
    if is_json_output() and "--json" not in arguments and not any(arg.startswith("--json") for arg in arguments):
        arguments = ["--json", *arguments]
    try:
        root.main(arguments, standalone_mode=False)
    except SystemExit:
        pass
    except click.exceptions.UsageError as error:
        skin.warning(f"Usage error: {error}")
    except Exception as error:
        skin.error(str(error))
