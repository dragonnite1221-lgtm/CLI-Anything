# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403

# fmt: off
from .macrocli_cli_p1 import cli, get_runtime, get_session  # noqa: E402,E501
# fmt: on


@cli.command()
@click.pass_context
def repl(ctx):
    """Enter the interactive REPL (default when no command given)."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.macrocli.utils.repl_skin import ReplSkin

    skin = ReplSkin("macrocli", version="1.0.0")
    skin.print_banner()

    runtime = get_runtime()

    # Show quick summary on startup
    macros = runtime.registry.list_all()
    skin.info(f"{len(macros)} macros loaded. Type 'macro list' to see them.")
    skin.info("Type 'help' for commands, 'quit' to exit.\n")

    pt_session = skin.create_prompt_session()
    session_obj = get_session()

    while True:
        try:
            line = skin.get_input(
                pt_session,
                context=f"{session_obj.session_id[:12]}",
            )
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line.lower() in ("help", "?"):
            skin.help(
                {
                    "macro list": "List all available macros",
                    "macro info <name>": "Show macro schema",
                    "macro run <name> [--param k=v ...]": "Execute a macro",
                    "macro dry-run <name>": "Simulate without side effects",
                    "macro validate [name]": "Validate macro definitions",
                    "macro define <name>": "Scaffold a new macro YAML",
                    "session status": "Show session statistics",
                    "session history": "Show recent runs",
                    "backends": "Show backend availability",
                    "quit": "Exit the REPL",
                }
            )
            continue

        # Parse and dispatch via Click's standalone_mode=False
        import shlex

        try:
            args = shlex.split(line)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            ctx_obj = cli.make_context(
                "cli-anything-macrocli",
                args,
                standalone_mode=False,
                parent=ctx,
            )
            with ctx_obj:
                cli.invoke(ctx_obj)
        except SystemExit:
            pass
        except click.ClickException as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


@cli.group()
def macro():
    """Macro management and execution."""
