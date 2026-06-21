# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403

# fmt: off
from .renderdoc_cli_p1 import _capture_handle_b, _capture_handle_b_path, _get_handle, _output  # noqa: E402,E501
from .renderdoc_cli_p6 import counters_group  # noqa: E402,E501
# fmt: on


@counters_group.command("fetch")
@click.option(
    "--ids", default=None, help="Comma-separated counter IDs (default: SamplesPassed)."
)
@click.pass_context
def counters_fetch(ctx, ids):
    """Fetch GPU counter results."""
    handle = _get_handle(ctx)
    from cli_anything.renderdoc.core.counters import fetch_counters

    counter_ids = None
    if ids:
        counter_ids = [int(i.strip()) for i in ids.split(",")]

    data = fetch_counters(handle.controller, counter_ids)
    _output(ctx, data)


def _get_handle_b(ctx: click.Context, path: str):
    """Open a second capture file for the B-side of a diff."""
    global _capture_handle_b, _capture_handle_b_path
    path_abs = os.path.abspath(path)
    if _capture_handle_b is not None:
        if _capture_handle_b_path == path_abs:
            return _capture_handle_b
        _capture_handle_b.close()
        _capture_handle_b = None
        _capture_handle_b_path = None
    from cli_anything.renderdoc.core.capture import CaptureHandle
    from cli_anything.renderdoc.utils.errors import handle_error

    try:
        _capture_handle_b = CaptureHandle(path)
        _capture_handle_b_path = path_abs
    except Exception as e:
        debug = ctx.obj.get("debug", False)
        err = handle_error(e, debug=debug)
        if ctx.obj.get("json_mode"):
            from cli_anything.renderdoc.utils.output import output_json

            output_json(err)
            ctx.exit(1)
        else:
            msg = "Failed to open capture-b: %s" % err["error"]
            if debug and "traceback" in err:
                msg += "\n" + err["traceback"]
            raise click.ClickException(msg)
    return _capture_handle_b
