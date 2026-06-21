# ruff: noqa: F403, F405, E501
from .nsight_graphics_cli_base import *  # noqa: F403

# fmt: off
from .nsight_graphics_cli_p1 import _common_kwargs, _handle_exc, _output, _print_replay_analysis  # noqa: E402,E501
from .nsight_graphics_cli_p2 import cli  # noqa: E402,E501
from .nsight_graphics_cli_p5 import replay_group  # noqa: E402,E501
# fmt: on


@replay_group.command("analyze")
@click.option(
    "--capture-file",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Existing .ngfx-capture or .ngfx-gputrace file.",
)
@click.option(
    "--output-dir",
    required=True,
    type=click.Path(file_okay=False),
    help="Directory for replay analysis artifacts.",
)
@click.option(
    "--metadata",
    is_flag=True,
    help="Export metadata, function stream, and object metadata.",
)
@click.option(
    "--logs", is_flag=True, help="Export captured logs and captured error logs."
)
@click.option(
    "--screenshot", is_flag=True, help="Export the embedded metadata screenshot."
)
@click.option(
    "--perf-report", is_flag=True, help="Replay once and collect a performance report."
)
@click.pass_context
def replay_analyze_cmd(
    ctx, capture_file, output_dir, metadata, logs, screenshot, perf_report
):
    """Analyze an existing capture through ngfx-replay."""
    try:
        data = replay.analyze_capture(
            nsight_path=ctx.obj.get("nsight_path"),
            capture_file=capture_file,
            output_dir=output_dir,
            metadata=metadata,
            logs=logs,
            screenshot=screenshot,
            perf_report=perf_report,
        )
        _output(ctx, data, _print_replay_analysis)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("cpp")
def cpp_group():
    """Generate C++ Capture commands."""


@cpp_group.command("capture")
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
@click.option("--wait-hotkey", is_flag=True, help="Wait for the target capture hotkey.")
@click.pass_context
def cpp_capture_cmd(
    ctx, exe_path, working_dir, program_args, envs, wait_seconds, wait_hotkey
):
    """Run Generate C++ Capture."""
    try:
        data = cpp_capture.capture_cpp(
            exe=exe_path,
            working_dir=working_dir,
            args=program_args,
            envs=envs,
            wait_seconds=wait_seconds,
            wait_hotkey=wait_hotkey,
            **_common_kwargs(ctx),
        )
        _output(ctx, data)
    except Exception as exc:
        _handle_exc(ctx, exc)


def main():
    cli(obj={})
