# ruff: noqa: F403, F405, E501
from .nsight_graphics_cli_base import *  # noqa: F403

# fmt: off
from .nsight_graphics_cli_p1 import _common_kwargs, _handle_exc, _output, _print_gpu_trace_summary  # noqa: E402,E501
from .nsight_graphics_cli_p2 import cli  # noqa: E402,E501
from .nsight_graphics_cli_p4 import gpu_trace_group  # noqa: E402,E501
# fmt: on


@gpu_trace_group.command("capture")
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
    "--start-after-frames", type=int, default=None, help="Wait N frames before trace."
)
@click.option(
    "--start-after-submits", type=int, default=None, help="Wait N submits before trace."
)
@click.option(
    "--start-after-ms", type=int, default=None, help="Wait N milliseconds before trace."
)
@click.option(
    "--start-after-hotkey", is_flag=True, help="Wait for the target capture hotkey."
)
@click.option(
    "--max-duration-ms", type=int, default=None, help="Maximum trace duration."
)
@click.option(
    "--limit-to-frames", type=int, default=None, help="Trace at most N frames."
)
@click.option(
    "--limit-to-submits", type=int, default=None, help="Trace at most N submits."
)
@click.option("--auto-export", is_flag=True, help="Automatically export metrics data.")
@click.option("--architecture", default=None, help="Architecture name.")
@click.option(
    "--metric-set-id", default=None, help="Metric set id for the selected architecture."
)
@click.option("--multi-pass-metrics", is_flag=True, help="Enable multi-pass metrics.")
@click.option(
    "--real-time-shader-profiler",
    is_flag=True,
    help="Enable real-time shader profiler.",
)
@click.option(
    "--summarize",
    is_flag=True,
    help="Parse exported GPU Trace tables and include a summary.",
)
@click.option(
    "--summary-limit",
    type=int,
    default=10,
    show_default=True,
    help="Number of top GPU events to include in the summary.",
)
@click.pass_context
def gpu_trace_capture_cmd(
    ctx,
    exe_path,
    working_dir,
    program_args,
    envs,
    start_after_frames,
    start_after_submits,
    start_after_ms,
    start_after_hotkey,
    max_duration_ms,
    limit_to_frames,
    limit_to_submits,
    auto_export,
    architecture,
    metric_set_id,
    multi_pass_metrics,
    real_time_shader_profiler,
    summarize,
    summary_limit,
):
    """Run a GPU Trace capture."""
    try:
        data = gpu_trace.capture_trace(
            exe=exe_path,
            working_dir=working_dir,
            args=program_args,
            envs=envs,
            start_after_frames=start_after_frames,
            start_after_submits=start_after_submits,
            start_after_ms=start_after_ms,
            start_after_hotkey=start_after_hotkey,
            max_duration_ms=max_duration_ms,
            limit_to_frames=limit_to_frames,
            limit_to_submits=limit_to_submits,
            auto_export=auto_export,
            architecture=architecture,
            metric_set_id=metric_set_id,
            multi_pass_metrics=multi_pass_metrics,
            real_time_shader_profiler=real_time_shader_profiler,
            summarize=summarize,
            summary_limit=summary_limit,
            **_common_kwargs(ctx),
        )
        _output(
            ctx,
            data,
            lambda payload: (
                click.echo(f"Output dir: {payload.get('output_dir')}"),
                click.echo(f"Artifacts: {payload.get('artifact_count', 0)}"),
                _print_gpu_trace_summary(payload["summary"])
                if payload.get("summary")
                else None,
            ),
        )
    except Exception as exc:
        _handle_exc(ctx, exc)


@gpu_trace_group.command("summarize")
@click.option(
    "--input-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="GPU Trace export directory to summarize.",
)
@click.option(
    "--summary-limit",
    type=int,
    default=10,
    show_default=True,
    help="Number of top GPU events to include in the summary.",
)
@click.pass_context
def gpu_trace_summarize_cmd(ctx, input_dir, summary_limit):
    """Summarize an existing exported GPU Trace directory."""
    try:
        data = gpu_trace.summarize_export_dir(input_dir, top_n=summary_limit)
        _output(ctx, data, _print_gpu_trace_summary)
    except Exception as exc:
        _handle_exc(ctx, exc)


@cli.group("replay")
def replay_group():
    """Analyze existing Nsight capture files with ngfx-replay."""
