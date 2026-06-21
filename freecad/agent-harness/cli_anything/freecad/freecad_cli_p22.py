# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session  # noqa: E402,E501
from .freecad_cli_p2 import _parse_vec3, handle_error, output_fn  # noqa: E402,E501
from .freecad_cli_p21 import motion_group  # noqa: E402,E501
# fmt: on


@motion_group.command("new")
@click.option("--name", default=None, help="Motion sequence name.")
@click.option("--duration", type=float, default=2.0, help="Motion duration in seconds.")
@click.option("--fps", type=int, default=24, help="Frames per second.")
@click.option(
    "--camera",
    type=click.Choice(sorted(motion_mod.CAMERA_PRESETS)),
    default="hero",
    help="Camera preset for rendering.",
)
@click.option("--width", type=int, default=1280, help="Output frame width.")
@click.option("--height", type=int, default=960, help="Output frame height.")
@click.option("--background", default="White", help="Viewport background color.")
@click.option(
    "--fit-mode",
    type=click.Choice(sorted(motion_mod.FIT_MODES)),
    default="initial",
    help="Whether to fit camera only once or on every frame.",
)
@handle_error
def motion_new(
    name: Optional[str],
    duration: float,
    fps: int,
    camera: str,
    width: int,
    height: int,
    background: str,
    fit_mode: str,
) -> None:
    """Create a new motion sequence."""
    sess = get_session()
    sess.snapshot("New motion sequence")
    proj = sess.get_project()
    result = motion_mod.create_motion(
        proj,
        name=name,
        duration=duration,
        fps=fps,
        camera=camera,
        width=width,
        height=height,
        background=background,
        fit_mode=fit_mode,
    )
    output_fn(result, f"Created motion: {result.get('name', '')}")


@motion_group.command("list")
@handle_error
def motion_list() -> None:
    """List motion sequences in the project."""
    sess = get_session()
    proj = sess.get_project()
    result = motion_mod.list_motions(proj)
    output_fn(result, f"{len(result)} motion sequence(s):")


@motion_group.command("get")
@click.argument("motion_index", type=int)
@handle_error
def motion_get(motion_index: int) -> None:
    """Show motion sequence details."""
    sess = get_session()
    proj = sess.get_project()
    result = motion_mod.get_motion(proj, motion_index)
    output_fn(result, f"Motion #{motion_index}")


@motion_group.command("delete")
@click.argument("motion_index", type=int)
@handle_error
def motion_delete(motion_index: int) -> None:
    """Delete a motion sequence."""
    sess = get_session()
    sess.snapshot(f"Delete motion #{motion_index}")
    proj = sess.get_project()
    result = motion_mod.delete_motion(proj, motion_index)
    output_fn(result, f"Deleted motion: {result.get('name', '')}")


@motion_group.command("keyframe")
@click.argument("motion_index", type=int)
@click.argument("target_kind", type=click.Choice(sorted(motion_mod.TARGET_KINDS)))
@click.argument("target_index", type=int)
@click.argument("time_value", type=float)
@click.option(
    "--position",
    default=None,
    help="Position as x,y,z. Defaults to the current placement.",
)
@click.option(
    "--rotation",
    default=None,
    help="Rotation as rx,ry,rz. Defaults to the current placement.",
)
@handle_error
def motion_keyframe(
    motion_index: int,
    target_kind: str,
    target_index: int,
    time_value: float,
    position: Optional[str],
    rotation: Optional[str],
) -> None:
    """Add or replace a motion keyframe for a target object."""
    sess = get_session()
    sess.snapshot(f"Motion keyframe on {target_kind} #{target_index}")
    proj = sess.get_project()
    result = motion_mod.add_keyframe(
        proj,
        motion_index,
        target_kind=target_kind,
        target_index=target_index,
        time_value=time_value,
        position=_parse_vec3(position) if position else None,
        rotation=_parse_vec3(rotation) if rotation else None,
    )
    output_fn(result, f"Updated motion #{motion_index}")


@motion_group.command("sample")
@click.argument("motion_index", type=int)
@click.argument("time_value", type=float)
@handle_error
def motion_sample(motion_index: int, time_value: float) -> None:
    """Sample interpolated motion placements at a given time."""
    sess = get_session()
    proj = sess.get_project()
    result = motion_mod.sample_motion(proj, motion_index, time_value)
    output_fn(result, f"Motion sample at t={result.get('time')}")
