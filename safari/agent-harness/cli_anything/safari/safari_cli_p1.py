# ruff: noqa: F403, F405, E501
from .safari_cli_base import *  # noqa: F403


def _compute_url_validated_tools(registry) -> frozenset[str]:
    """Find every tool with a `url` param that takes a navigation target.

    Heuristic: a param whose MCP name is literally ``"url"`` (not
    ``urlPattern`` or similar) and type ``string`` is a navigation
    target. ``mock_route``'s ``urlPattern`` is a regex/substring
    pattern, not a target, and is correctly excluded.
    """
    result: set[str] = set()
    for tool in registry:
        for p in tool.params:
            if p.name == "url" and p.type == "string":
                result.add(tool.name)
                break
    return frozenset(result)


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str, ensure_ascii=False))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        elif data is not None:
            click.echo(str(data))


def _handle_error(e: Exception):
    """Uniform error reporting that respects --json and REPL mode."""
    err_type = type(e).__name__
    if _json_output:
        click.echo(json.dumps({"error": str(e), "type": err_type}))
    else:
        click.echo(f"Error: {e}", err=True)
    if not _repl_mode:
        sys.exit(1)


def handle_error(func):
    """Decorator that funnels exceptions through ``_handle_error``.

    Applied to ``tools``, ``raw``, and ``session`` commands so that any
    uncaught ``RuntimeError``, ``ValueError``, ``OSError``, or
    ``ClickException`` (the base class covering ``UsageError``,
    ``BadParameter``, ``BadOptionUsage``, ``MissingParameter``,
    ``FileError``, ``BadArgumentUsage``) is reported through the
    uniform error path (respects ``--json`` and REPL mode).

    The dynamically-built ``tool`` commands catch their own exceptions
    inline because they need per-parameter JSON-decode handling that a
    generic decorator cannot express.
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (
            RuntimeError,
            ValueError,
            IndexError,
            OSError,
            json.JSONDecodeError,
            click.exceptions.ClickException,
        ) as e:
            _handle_error(e)

    return wrapper


def _validate_url_or_exit(url: str) -> None:
    """Validate a URL and abort the current command if it's unsafe.

    In non-REPL mode this calls ``_handle_error`` which ``sys.exit(1)``s.
    In REPL mode it raises ``click.exceptions.UsageError`` so the REPL
    loop can report the error once and continue. The caller should
    propagate the raise — nothing downstream should run if the URL is
    bad.
    """
    ok, err = security_mod.validate_url(url)
    if ok:
        return
    if _repl_mode:
        raise click.exceptions.UsageError(err)
    _handle_error(click.exceptions.UsageError(err))
    return


_INTROSPECTION_SUBCOMMANDS = {"tools"}
