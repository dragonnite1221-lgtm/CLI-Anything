# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import cli, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p21 import motion_group  # noqa: E402,E501
# fmt: on


@motion_group.command("render-frames")
@click.argument("motion_index", type=int)
@click.argument("output_dir", type=click.Path())
@click.option("--overwrite", is_flag=True, help="Replace an existing output directory.")
@click.option(
    "--camera",
    type=click.Choice(sorted(motion_mod.CAMERA_PRESETS)),
    default=None,
    help="Override the motion camera preset.",
)
@click.option("--width", type=int, default=None, help="Override the frame width.")
@click.option("--height", type=int, default=None, help="Override the frame height.")
@click.option("--background", default=None, help="Override the viewport background.")
@click.option(
    "--fit-mode",
    type=click.Choice(sorted(motion_mod.FIT_MODES)),
    default=None,
    help="Override the camera fit mode.",
)
@handle_error
def motion_render_frames(
    motion_index: int,
    output_dir: str,
    overwrite: bool,
    camera: Optional[str],
    width: Optional[int],
    height: Optional[int],
    background: Optional[str],
    fit_mode: Optional[str],
) -> None:
    """Render a motion sequence to real FreeCAD frame images."""
    sess = get_session()
    proj = sess.get_project()
    result = motion_mod.render_frames(
        proj,
        motion_index,
        output_dir,
        overwrite=overwrite,
        camera=camera,
        width=width,
        height=height,
        background=background,
        fit_mode=fit_mode,
    )
    output_fn(result, f"Rendered {result.get('frame_count', 0)} motion frame(s)")


@motion_group.command("render-video")
@click.argument("motion_index", type=int)
@click.argument("output_path", type=click.Path())
@click.option("--overwrite", is_flag=True, help="Replace an existing output file.")
@click.option(
    "--frames-dir",
    default=None,
    type=click.Path(),
    help="Persist rendered frame images to this directory.",
)
@click.option(
    "--keep-frames",
    is_flag=True,
    help="Keep rendered frames even when --frames-dir is not specified.",
)
@click.option(
    "--camera",
    type=click.Choice(sorted(motion_mod.CAMERA_PRESETS)),
    default=None,
    help="Override the motion camera preset.",
)
@click.option("--width", type=int, default=None, help="Override the frame width.")
@click.option("--height", type=int, default=None, help="Override the frame height.")
@click.option("--background", default=None, help="Override the viewport background.")
@click.option(
    "--fit-mode",
    type=click.Choice(sorted(motion_mod.FIT_MODES)),
    default=None,
    help="Override the camera fit mode.",
)
@handle_error
def motion_render_video(
    motion_index: int,
    output_path: str,
    overwrite: bool,
    frames_dir: Optional[str],
    keep_frames: bool,
    camera: Optional[str],
    width: Optional[int],
    height: Optional[int],
    background: Optional[str],
    fit_mode: Optional[str],
) -> None:
    """Render a motion sequence to a final showcase video."""
    sess = get_session()
    proj = sess.get_project()
    result = motion_mod.render_video(
        proj,
        motion_index,
        output_path,
        overwrite=overwrite,
        frames_dir=frames_dir,
        keep_frames=keep_frames,
        camera=camera,
        width=width,
        height=height,
        background=background,
        fit_mode=fit_mode,
    )
    output_fn(result, f"Rendered motion video: {result.get('output', '')}")


@cli.group("session")
def session_group():
    """Session management commands."""
    pass


@session_group.command("undo")
@handle_error
def session_undo() -> None:
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    if desc:
        result = {"undone": desc}
        output_fn(result, f"Undone: {desc}")
    else:
        output_fn({"message": "Nothing to undo"}, "Nothing to undo")


@session_group.command("redo")
@handle_error
def session_redo() -> None:
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    if desc:
        result = {"redone": desc}
        output_fn(result, f"Redone: {desc}")
    else:
        output_fn({"message": "Nothing to redo"}, "Nothing to redo")
