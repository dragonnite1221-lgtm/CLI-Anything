# ruff: noqa: F403, F405, E501
from .safari_cli_base import *  # noqa: F403

# fmt: off
from .safari_cli_p1 import _INTROSPECTION_SUBCOMMANDS, get_session  # noqa: E402,E501
# fmt: on


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Safari CLI — Browser automation on macOS via safari-mcp.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output, _session, _availability_cached
    _json_output = use_json

    # Click's --help support short-circuits before the group body runs,
    # so we only need to skip the availability probe for commands that
    # work off the bundled registry (tools list|describe|count).
    skip_probe = ctx.invoked_subcommand in _INTROSPECTION_SUBCOMMANDS

    if not skip_probe:
        if _availability_cached is None:
            _availability_cached = backend.is_available()
        available, msg = _availability_cached
        if not available:
            if _json_output:
                click.echo(json.dumps({"error": msg, "type": "dependency_error"}))
            else:
                click.echo(f"Error: {msg}", err=True)
                click.echo("\nDocs: https://github.com/achiya-automation/safari-mcp")
            sys.exit(1)

    _session = get_session()

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command()
def repl():
    """Start interactive REPL session."""
    from cli_anything.safari.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("safari", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    repl_commands = {
        "tool <name>": "Call any safari-mcp tool (use 'tools list' for names)",
        "tools list": "List all available tools",
        "tools describe <name>": "Show full schema for a tool",
        "raw <name>": "Call a tool via JSON args",
        "session status": "Show current session state",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            sess = get_session()
            context = ""
            if sess.last_url:
                url_display = (
                    sess.last_url[:40] + "..."
                    if len(sess.last_url) > 40
                    else sess.last_url
                )
                context = url_display
                if sess.current_tab_index is not None:
                    context = f"tab{sess.current_tab_index} {url_display}"

            line = skin.get_input(pt_session, context=context)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(repl_commands)
                continue

            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()

            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


@cli.group("tool")
def tool_group():
    """Call any of safari-mcp's 84 tools.

    Every MCP tool is exposed here with its full schema. Use
    ``cli-anything-safari tools list`` to see them, and
    ``cli-anything-safari tools describe <name>`` for full details.
    """


def _click_type_for_param(param: ToolParam):
    """Map a JSON Schema type to a Click ParamType."""
    base = {
        "string": click.STRING,
        "integer": click.INT,
        "number": click.FLOAT,
        "boolean": click.BOOL,
    }.get(param.type, click.STRING)
    if param.choices and param.type in ("string", "integer"):
        return click.Choice(param.choices, case_sensitive=False)
    return base


def _click_param_name(cli_name: str) -> str:
    """Click normalizes option names to underscores for the handler kwarg."""
    return cli_name.replace("-", "_")
