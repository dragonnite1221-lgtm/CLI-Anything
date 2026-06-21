# ruff: noqa: F403, F405, E501
from .nsight_graphics_cli_base import *  # noqa: F403

# fmt: off
from .nsight_graphics_cli_p1 import _common_kwargs, _handle_exc, _output  # noqa: E402,E501
from .nsight_graphics_cli_p2 import cli  # noqa: E402,E501
from .nsight_graphics_cli_p3 import frame_group  # noqa: E402,E501
# fmt: on


@frame_group.command("capture")
@click.option(
    "--activity",
    default=None,
    help="Nsight activity name. Defaults to Graphics Capture when available.",
)
@click.option(
    "--exe",
    "exe_path",
    type=click.Path(exists=False),
    default=None,
    help="Target executable path.",
)
@click.option(
    "--dir",
    "working_dir",
    type=click.Path(exists=False),
    default=None,
    help="Target working directory.",
)
@click.option(
    "--arg", "program_args", multiple=True, help="Target argument. Repeat for multiple."
)
@click.option("--env", "envs", multiple=True, help="Environment entry KEY=VALUE.")
@click.option(
    "--wait-seconds", type=int, default=None, help="Wait N seconds before capture."
)
@click.option(
    "--wait-frames", type=int, default=None, help="Wait N frames before capture."
)
@click.option("--wait-hotkey", is_flag=True, help="Wait for the target capture hotkey.")
@click.option(
    "--export-frame-perf-metrics",
    is_flag=True,
    help="Export whole-frame performance metrics.",
)
@click.option(
    "--export-range-perf-metrics",
    is_flag=True,
    help="Export per-range performance metrics.",
)
@click.pass_context
def frame_capture_cmd(
    ctx,
    activity,
    exe_path,
    working_dir,
    program_args,
    envs,
    wait_seconds,
    wait_frames,
    wait_hotkey,
    export_frame_perf_metrics,
    export_range_perf_metrics,
):
    """Run a Frame Debugger capture."""
    try:
        data = frame.capture_frame(
            exe=exe_path,
            working_dir=working_dir,
            args=program_args,
            envs=envs,
            activity=activity,
            wait_seconds=wait_seconds,
            wait_frames=wait_frames,
            wait_hotkey=wait_hotkey,
            export_frame_perf_metrics=export_frame_perf_metrics,
            export_range_perf_metrics=export_range_perf_metrics,
            **_common_kwargs(ctx),
        )
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("gpu-trace")
def gpu_trace_group():
    """GPU Trace capture commands."""
