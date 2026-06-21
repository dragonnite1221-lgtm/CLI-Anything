# ruff: noqa: F403, F405, E501
from .lldb_cli_base import *  # noqa: F403

# fmt: off
from .lldb_cli_p2 import repl  # noqa: E402,E501
# fmt: on


def _set_session_file(path: str | None):
    global _session, _session_file
    if _session_file != path:
        _session = None
        _session_file = path


def _shutdown_session():
    global _session
    if _session is not None:
        shutdown = getattr(_session, "shutdown", None)
        try:
            if callable(shutdown):
                shutdown()
            else:
                _session.destroy()
        finally:
            _session = None


def _parse_int(value: str) -> int:
    return int(value, 0)


def _get_session():
    global _session
    if _session is None:
        from cli_anything.lldb.utils.session_client import (
            RemoteLLDBSessionProxy,
            resolve_session_file,
        )

        _session = RemoteLLDBSessionProxy(resolve_session_file(_session_file))
    return _session


def _session_status(session):
    status_fn = getattr(session, "session_status", None)
    if callable(status_fn):
        status = status_fn()
        if isinstance(status, dict):
            return status
    return {
        "has_target": getattr(session, "target", None) is not None,
        "has_process": getattr(session, "process", None) is not None,
        "process_origin": None,
    }


def _require_target():
    s = _get_session()
    if not _session_status(s).get("has_target"):
        raise click.ClickException("No target. Run: target create --exe <path>")
    return s


def _require_process():
    s = _require_target()
    if not _session_status(s).get("has_process"):
        raise click.ClickException(
            "No process. Run: process launch/attach or core load"
        )
    return s


def _output(ctx: click.Context, data, human_fn=None):
    if ctx.obj.get("json_mode"):
        from cli_anything.lldb.utils.output import output_json

        output_json(data)
    elif human_fn:
        human_fn(data)
    else:
        from cli_anything.lldb.utils.output import output_json

        output_json(data)


def _handle_exc(ctx: click.Context, exc: Exception):
    from cli_anything.lldb.utils.errors import handle_error

    err = handle_error(exc, debug=ctx.obj.get("debug", False))
    if ctx.obj.get("json_mode"):
        from cli_anything.lldb.utils.output import output_json

        output_json(err)
        ctx.exit(1)
    raise click.ClickException(err["error"])


@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format.")
@click.option("--debug", is_flag=True, help="Show debug tracebacks on errors.")
@click.option(
    "--session-file",
    type=click.Path(dir_okay=False),
    default=None,
    help="Optional persistent session state file path.",
)
@click.version_option(package_name="cli-anything-lldb")
@click.pass_context
def cli(ctx, json_mode, debug, session_file):
    """LLDB CLI - stateful debugger harness with REPL and subcommands."""
    from cli_anything.lldb.utils.session_client import resolve_session_file

    ctx.ensure_object(dict)
    ctx.obj["json_mode"] = json_mode
    ctx.obj["debug"] = debug
    ctx.obj["session_file"] = str(resolve_session_file(session_file))
    ctx.obj.setdefault("close_session_on_exit", False)
    _set_session_file(ctx.obj["session_file"])
    if ctx.invoked_subcommand is None:
        ctx.obj["close_session_on_exit"] = True
        ctx.invoke(repl)
