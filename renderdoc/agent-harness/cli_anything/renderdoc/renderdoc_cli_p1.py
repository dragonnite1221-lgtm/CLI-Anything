# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403

# fmt: off
from .renderdoc_cli_p2 import repl  # noqa: E402,E501
# fmt: on


_capture_handle_b = None  # type: ignore
_capture_handle_b_path = None  # type: ignore


def _close_all_captures():
    global \
        _capture_handle, \
        _capture_handle_b, \
        _capture_handle_path, \
        _capture_handle_b_path
    if _capture_handle is not None:
        _capture_handle.close()
        _capture_handle = None
        _capture_handle_path = None
    if _capture_handle_b is not None:
        _capture_handle_b.close()
        _capture_handle_b = None
        _capture_handle_b_path = None


def _get_export_dir(ctx: click.Context, subfolder: str = "") -> str:
    """Return the default export directory for the current capture.

    Layout: <capture_dir>/<stem>_exported/<subfolder>/
    e.g.  tests/pc_exported/shaders/
    """
    capture_path = ctx.obj.get("capture_path", "capture")
    capture_dir = os.path.dirname(os.path.abspath(capture_path))
    stem = os.path.splitext(os.path.basename(capture_path))[0]
    export_dir = os.path.join(capture_dir, "%s_exported" % stem)
    if subfolder:
        export_dir = os.path.join(export_dir, subfolder)
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def _get_handle(ctx: click.Context):
    """Return the active CaptureHandle, opening it if needed."""
    global _capture_handle, _capture_handle_path
    path = ctx.obj.get("capture_path")
    if not path:
        click.echo("Error: No capture file specified. Use --capture <path>", err=True)
        ctx.exit(1)
    path_abs = os.path.abspath(path)
    if _capture_handle is not None:
        if _capture_handle_path == path_abs:
            return _capture_handle
        _capture_handle.close()
        _capture_handle = None
        _capture_handle_path = None
    from cli_anything.renderdoc.core.capture import CaptureHandle
    from cli_anything.renderdoc.utils.errors import handle_error

    try:
        _capture_handle = CaptureHandle(path)
        _capture_handle_path = path_abs
    except Exception as e:
        debug = ctx.obj.get("debug", False)
        err = handle_error(e, debug=debug)
        if ctx.obj.get("json_mode"):
            from cli_anything.renderdoc.utils.output import output_json

            output_json(err)
            ctx.exit(1)
        else:
            msg = "Failed to open capture: %s" % err["error"]
            if debug and "traceback" in err:
                msg += "\n" + err["traceback"]
            raise click.ClickException(msg)
    return _capture_handle


def _output(ctx: click.Context, data, human_fn=None):
    """Output data as JSON or human-readable."""
    if ctx.obj.get("json_mode"):
        from cli_anything.renderdoc.utils.output import output_json

        output_json(data)
    elif human_fn:
        human_fn(data)
    else:
        from cli_anything.renderdoc.utils.output import output_json

        output_json(data)


@click.group(invoke_without_command=True)
@click.option(
    "--capture",
    "-c",
    type=click.Path(exists=False),
    envvar="RENDERDOC_CAPTURE",
    help="Path to .rdc capture file.",
)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format.")
@click.option("--debug", is_flag=True, help="Show debug tracebacks on errors.")
@click.version_option(package_name="cli-anything-renderdoc")
@click.pass_context
def cli(ctx, capture, json_mode, debug):
    """RenderDoc CLI – headless capture analysis tool.

    Run without a subcommand to enter interactive REPL mode.
    """
    ctx.ensure_object(dict)
    # Preserve REPL session state: nested `cli.main(...)` omits global options, so
    # only overwrite capture when the user passed `-c` on that invocation.
    if capture is not None:
        ctx.obj["capture_path"] = capture
    ctx.obj["json_mode"] = json_mode
    ctx.obj["debug"] = debug

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
