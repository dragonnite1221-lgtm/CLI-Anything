# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import cli, get_state  # noqa: E402,E501
# fmt: on


@cli.command("repl")
@click.pass_context
def repl(ctx):
    """Start the interactive REPL (default when no subcommand given)."""
    from cli_anything.iterm2_ctl.utils.repl_skin import ReplSkin

    skin = ReplSkin("iterm2_ctl", version="1.0.0")
    skin.print_banner()

    state = get_state()
    if state.summary() != "no context set":
        skin.info(f"Context: {state.summary()}")
        click.echo()

    skin.info("Type 'help' for commands, 'quit' to exit.")
    click.echo()

    pt_session = skin.create_prompt_session()

    _COMMANDS = {
        "app status": "Show iTerm2 status",
        "app current": "Get current window/tab/session",
        "app context": "Show saved context",
        "app set-context": "Set context IDs",
        "app clear-context": "Clear saved context",
        "app get-var <var>": "Get app-level variable",
        "app set-var <var> <val>": "Set app-level variable",
        "app alert <title> <subtitle>": "Show modal alert dialog",
        "app text-input <title> <subtitle>": "Show text input dialog",
        "app file-panel": "Show macOS open file picker",
        "app save-panel": "Show macOS save file picker",
        "window list": "List open windows",
        "window create": "Create a new window",
        "window close [id]": "Close a window",
        "window activate [id]": "Focus a window",
        "window set-title <title>": "Set window title",
        "window frame [id]": "Get window geometry",
        "window fullscreen <on|off|toggle|status>": "Control fullscreen",
        "tab list": "List tabs",
        "tab create": "Create a new tab",
        "tab close [id]": "Close a tab",
        "tab activate [id]": "Focus a tab",
        "tab select-pane <dir>": "Move focus to adjacent pane (left/right/above/below)",
        "session list": "List sessions",
        "session send <text>": "Send text to session",
        "session screen": "Read terminal screen",
        "session split": "Split pane",
        "session close [id]": "Close a session",
        "session set-name <name>": "Name a session",
        "session resize -c <cols> -r <rows>": "Resize terminal",
        "session inject <data>": "Inject raw bytes into session (use --hex for hex string)",
        "session get-prompt": "Get last shell prompt info (Shell Integration)",
        "session wait-prompt": "Wait for next shell prompt",
        "session wait-command-end": "Wait for command to finish",
        "session run-tmux-cmd <command>": "Run tmux cmd from gateway session",
        "profile list": "List profiles",
        "profile get <guid>": "Get profile details by GUID",
        "profile color-presets": "List color presets",
        "arrangement list": "List arrangements",
        "arrangement save <name>": "Save arrangement",
        "arrangement restore <name>": "Restore arrangement",
        "tmux list": "List active tmux -CC connections",
        "tmux bootstrap": "Start tmux -CC and wait for connection",
        "tmux send <command>": "Send tmux command (e.g. 'list-sessions')",
        "tmux create-window": "Create tmux window as iTerm2 tab",
        "tmux set-visible <id> on|off": "Show/hide a tmux window tab",
        "tmux tabs": "List tmux-backed tabs",
        "broadcast list": "List broadcast domains",
        "broadcast set <g1> [g2...]": "Set broadcast domains (comma-sep session IDs)",
        "broadcast add <s1> [s2...]": "Add sessions to a new broadcast domain",
        "broadcast clear": "Clear all broadcast domains",
        "broadcast all-panes": "Broadcast to all panes",
        "menu select <identifier>": "Invoke a menu item",
        "menu state <identifier>": "Get menu item state",
        "menu list-common": "List common menu identifiers",
        "pref list-keys": "List all valid preference key names",
        "pref get <key>": "Get a preference value",
        "pref set <key> <val>": "Set a preference value",
        "pref tmux-get": "Show all tmux preferences",
        "pref tmux-set <setting> <val>": "Set a tmux preference",
        "pref theme": "Show current theme tags",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            state = get_state()
            ctx_str = ""
            if state.session_id:
                ctx_str = state.session_id[:12]
            elif state.window_id:
                ctx_str = state.window_id[:12]

            line = skin.get_input(pt_session, context=ctx_str)
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue

        cmd = line.strip()

        if cmd in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        elif cmd == "help":
            skin.help(_COMMANDS)
            continue

        # Run the line through the Click CLI
        try:
            args = cmd.split()
            standalone = cli.main(
                args=args, standalone_mode=False, obj={"json": _json_output}
            )
        except SystemExit:
            pass
        except click.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))
