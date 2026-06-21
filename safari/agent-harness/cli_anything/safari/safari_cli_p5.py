# ruff: noqa: F403, F405, E501
from .safari_cli_base import *  # noqa: F403

# fmt: off
from .safari_cli_p1 import _handle_error, _validate_url_or_exit, get_session, handle_error, output  # noqa: E402,E501
from .safari_cli_p2 import cli  # noqa: E402,E501
# fmt: on


@cli.command()
@click.argument("tool_name")
@click.option(
    "--json-args",
    default="{}",
    help="JSON string of arguments to pass to the MCP tool",
)
@handle_error
def raw(tool_name, json_args):
    """Call any safari-mcp tool directly by name.

    This bypasses the schema-driven 'tool' group — useful when you have
    a pre-built JSON args blob or when testing new tools.

    Example:
        cli-anything-safari raw safari_evaluate \\
            --json-args '{"script":"document.title"}'
    """
    try:
        args = json.loads(json_args)
    except json.JSONDecodeError as e:
        _handle_error(click.exceptions.UsageError(f"Invalid JSON for --json-args: {e}"))
        return

    if not isinstance(args, dict):
        _handle_error(
            click.exceptions.UsageError(
                f"--json-args must decode to a JSON object, got {type(args).__name__}"
            )
        )
        return

    # Even via raw, still run URL validation for navigation tools
    if tool_name in _URL_VALIDATED_TOOLS and args.get("url"):
        _validate_url_or_exit(args["url"])

    try:
        result = backend.call(tool_name, **args)
    except Exception as e:
        _handle_error(e)
        return
    output(result)


@cli.group()
def session():
    """Session state (last URL, current tab)."""


@session.command("status")
@handle_error
def session_status():
    """Show current session state."""
    output(get_session().status())


def main():
    cli()
