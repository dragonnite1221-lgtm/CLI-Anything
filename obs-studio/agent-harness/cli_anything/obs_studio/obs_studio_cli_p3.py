# ruff: noqa: F403, F405, E501
from .obs_studio_cli_base import *  # noqa: F403

# fmt: off
from .obs_studio_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .obs_studio_cli_p2 import project  # noqa: E402,E501
# fmt: on


@project.command("open")
@click.argument("path")
@handle_error
def project_open(path):
    """Open an existing project."""
    proj = proj_mod.open_project(path)
    sess = get_session()
    sess.set_project(proj, path)
    info = proj_mod.get_project_info(proj)
    globals()["output"](info, f"Opened: {path}")


@project.command("save")
@click.argument("path", required=False)
@handle_error
def project_save(path):
    """Save the current project."""
    sess = get_session()
    saved = sess.save_session(path)
    globals()["output"]({"saved": saved}, f"Saved to: {saved}")


@project.command("info")
@handle_error
def project_info():
    """Show project information."""
    sess = get_session()
    info = proj_mod.get_project_info(sess.get_project())
    globals()["output"](info)


@project.command("json")
@handle_error
def project_json():
    """Print raw project JSON."""
    sess = get_session()
    click.echo(json.dumps(sess.get_project(), indent=2, default=str))


@cli.group("scene")
def scene_group():
    """Scene management commands."""
    pass


@scene_group.command("add")
@click.option("--name", "-n", default="Scene", help="Scene name")
@handle_error
def scene_add(name):
    """Add a new scene."""
    sess = get_session()
    sess.snapshot(f"Add scene: {name}")
    scene = scene_mod.add_scene(sess.get_project(), name=name)
    output(scene, f"Added scene: {scene['name']}")


@scene_group.command("remove")
@click.argument("index", type=int)
@handle_error
def scene_remove(index):
    """Remove a scene by index."""
    sess = get_session()
    sess.snapshot(f"Remove scene {index}")
    removed = scene_mod.remove_scene(sess.get_project(), index)
    output(removed, f"Removed scene: {removed['name']}")


@scene_group.command("duplicate")
@click.argument("index", type=int)
@handle_error
def scene_duplicate(index):
    """Duplicate a scene."""
    sess = get_session()
    sess.snapshot(f"Duplicate scene {index}")
    dup = scene_mod.duplicate_scene(sess.get_project(), index)
    output(dup, f"Duplicated scene: {dup['name']}")


@scene_group.command("set-active")
@click.argument("index", type=int)
@handle_error
def scene_set_active(index):
    """Set the active scene."""
    sess = get_session()
    sess.snapshot(f"Set active scene {index}")
    result = scene_mod.set_active_scene(sess.get_project(), index)
    output(result, f"Active scene: {result['active_scene']}")


@scene_group.command("list")
@handle_error
def scene_list():
    """List all scenes."""
    sess = get_session()
    scenes = scene_mod.list_scenes(sess.get_project())
    output(scenes, "Scenes:")


@cli.group("source")
def source_group():
    """Source management commands."""
    pass
