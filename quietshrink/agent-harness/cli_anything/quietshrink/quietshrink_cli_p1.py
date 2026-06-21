# ruff: noqa: F403, F405, E501
from .quietshrink_cli_base import *  # noqa: F403


def find_bash_cli() -> Path:
    """Locate the quietshrink bash binary on $PATH.

    The harness is a thin Python wrapper around the standalone quietshrink bash
    CLI, which must be installed separately. See QUIETSHRINK.md for install.
    """
    in_path = shutil.which("quietshrink")
    if in_path:
        return Path(in_path)
    raise click.ClickException(
        "quietshrink bash CLI not found on $PATH. Install it with:\n"
        "  curl -fsSL https://raw.githubusercontent.com/achiya-automation/quietshrink/main/install.sh | bash\n"
        "Or download a release from https://github.com/achiya-automation/quietshrink/releases"
    )


def emit(data: dict, json_mode: bool) -> None:
    """Emit data as JSON or pretty-printed."""
    if json_mode:
        click.echo(json.dumps(data, indent=2))
    else:
        for k, v in data.items():
            click.echo(f"{k}: {v}")


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="cli-anything-quietshrink")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Agent-native CLI for quietshrink — Apple Silicon screen recording compressor.

    Designed for AI agents (Claude Code, OpenClaw, Cursor) — every command supports
    --json for machine-readable output and exits with proper error codes.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument(
    "input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.argument(
    "output_path", type=click.Path(dir_okay=False, path_type=Path), required=False
)
@click.option(
    "--quality",
    "-q",
    type=click.Choice(["tiny", "balanced", "transparent", "pristine"]),
    default="transparent",
    help="Quality preset",
)
@click.option("--gop", "-g", type=int, default=600, help="GOP size")
@click.option("--audio", "-a", default="96k", help="Audio bitrate")
@click.option(
    "--replace", is_flag=True, help="Replace input file with compressed version"
)
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
def compress(
    input_path: Path,
    output_path: Optional[Path],
    quality: str,
    gop: int,
    audio: str,
    replace: bool,
    json_mode: bool,
) -> None:
    """Compress a video file. Returns size statistics."""
    bash_cli = find_bash_cli()
    args = [
        str(bash_cli),
        "--quality",
        quality,
        "--gop",
        str(gop),
        "--audio",
        audio,
        "--json",
    ]
    if replace:
        args.append("--replace")
    args.append(str(input_path))
    if output_path:
        args.append(str(output_path))

    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        emit({"error": "compression_failed", "stderr": e.stderr.strip()}, json_mode)
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
        emit(data, json_mode)
    except json.JSONDecodeError as e:
        emit(
            {"error": "invalid_output", "raw": result.stdout, "detail": str(e)},
            json_mode,
        )
        sys.exit(1)


@cli.command()
@click.argument(
    "input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
def probe(input_path: Path, json_mode: bool) -> None:
    """Inspect a video file before compression. Returns codec, resolution, duration, size."""
    if not shutil.which("ffprobe"):
        emit({"error": "ffprobe not found", "hint": "brew install ffmpeg"}, json_mode)
        sys.exit(2)

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=codec_name,width,height,r_frame_rate",
        "-show_entries",
        "format=duration,bit_rate,size",
        "-of",
        "json",
        str(input_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_data = json.loads(result.stdout)
        size = input_path.stat().st_size
        video_stream = next(
            (
                s
                for s in probe_data.get("streams", [])
                if s.get("codec_name") not in ("aac", "mp3")
            ),
            {},
        )
        duration = float(probe_data.get("format", {}).get("duration", 0))

        info = {
            "path": str(input_path),
            "size_bytes": size,
            "size_mb": round(size / 1024 / 1024, 2),
            "codec": video_stream.get("codec_name"),
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
            "framerate": video_stream.get("r_frame_rate"),
            "duration_seconds": round(duration, 2),
        }
        emit(info, json_mode)
    except subprocess.CalledProcessError as e:
        emit({"error": "probe_failed", "stderr": e.stderr.strip()}, json_mode)
        sys.exit(1)
