# ruff: noqa: F403, F405, E501
from .safari_cli_base import *  # noqa: F403

# fmt: off
from .safari_cli_p1 import _compute_url_validated_tools, _handle_error, _validate_url_or_exit, get_session, output  # noqa: E402,E501
from .safari_cli_p2 import _click_param_name, _click_type_for_param, cli, tool_group  # noqa: E402,E501
# fmt: on


def _build_tool_command(tool: ToolSchema):
    """Build a Click command for a single MCP tool from its schema."""

    def run(**kwargs):
        # Convert kebab-case kwargs back to camelCase MCP names and coerce types.
        # Object/array params arrive as JSON strings and are decoded here;
        # a decode error is reported to the user via _handle_error rather
        # than bubbling up as an ugly traceback.
        args: dict[str, Any] = {}
        for param in tool.params:
            value = kwargs.get(_click_param_name(param.cli_name))
            if value is None:
                # Click's `required=True` covers most types, but boolean
                # flag pairs (--foo/--no-foo) cannot be marked required
                # at the Click level. We enforce here.
                if param.required and param.type == "boolean":
                    _handle_error(
                        click.exceptions.UsageError(
                            f"Missing required boolean flag: "
                            f"--{param.cli_name} or --no-{param.cli_name}"
                        )
                    )
                    return
                continue
            try:
                args[param.name] = coerce_arg_value(param, value)
            except json.JSONDecodeError as e:
                _handle_error(
                    click.exceptions.UsageError(
                        f"Invalid JSON for --{param.cli_name}: {e}"
                    )
                )
                return

        # URL safety for navigation tools. _validate_url_or_exit either
        # exits (non-REPL) or raises UsageError (REPL). Either way we
        # abort here before calling the MCP backend.
        if tool.name in _URL_VALIDATED_TOOLS and args.get("url"):
            _validate_url_or_exit(args["url"])

        try:
            result = backend.call(tool.name, **args)
        except Exception as e:
            _handle_error(e)
            return

        # Track URL for REPL context (only after a successful call).
        if tool.name in _URL_VALIDATED_TOOLS and args.get("url"):
            get_session().set_url(args["url"])

        output(result)

    # Apply Click options, in reverse so decorator order matches param order.
    decorated = run
    for param in reversed(tool.params):
        help_text = param.description or ""
        if param.default is not None:
            help_text = f"{help_text} (default: {param.default})".strip()
        if param.type == "boolean":
            # Required booleans need an explicit default (Click can't enforce
            # `required=True` on a boolean flag pair). For optional booleans
            # we use `default=None` so the arg is omitted from the MCP call
            # when the user doesn't pass --foo or --no-foo.
            bool_default = None
            if param.required:
                # No safe default for a required boolean — force the user
                # to pass --foo or --no-foo. Click doesn't have a "required
                # boolean flag" concept, so we approximate by leaving
                # default=None and validating in the runner below.
                bool_default = None
            decorated = click.option(
                f"--{param.cli_name}/--no-{param.cli_name}",
                default=bool_default,
                help=help_text,
            )(decorated)
        elif param.type in ("object", "array"):
            decorated = click.option(
                f"--{param.cli_name}",
                type=click.STRING,
                required=param.required,
                help=(
                    help_text + f" [JSON {param.type}]"
                    if help_text
                    else f"[JSON {param.type}]"
                ).strip(),
            )(decorated)
        else:
            decorated = click.option(
                f"--{param.cli_name}",
                type=_click_type_for_param(param),
                required=param.required,
                help=help_text,
            )(decorated)

    decorated.__doc__ = tool.description or f"Call {tool.name}."
    cmd = click.command(
        name=tool.short_name,
        help=tool.description or f"Call {tool.name}.",
    )(decorated)
    return cmd


def _register_all_tools():
    """Load the bundled registry and register every tool as a subcommand.

    Populates ``_URL_VALIDATED_TOOLS`` BEFORE registering any commands so
    no command can be invoked while the validation set is empty.
    """
    global _URL_VALIDATED_TOOLS
    try:
        registry = load_registry()
    except FileNotFoundError:
        click.echo(
            "Warning: bundled tool registry (resources/tools.json) is missing. "
            "Run: python scripts/extract_tools.py <safari-mcp>/index.js "
            "cli_anything/safari/resources/tools.json",
            err=True,
        )
        return

    # Compute the validation set first so any registered command sees it.
    _URL_VALIDATED_TOOLS = _compute_url_validated_tools(registry)
    for tool in registry:
        cmd = _build_tool_command(tool)
        tool_group.add_command(cmd)


_register_all_tools()


@cli.group("tools")
def tools_group():
    """Inspect the bundled safari-mcp tool registry."""
