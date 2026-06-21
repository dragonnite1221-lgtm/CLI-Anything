# ruff: noqa: F403, F405, E501
from .obs_studio_cli_base import *  # noqa: F403

# fmt: off
from .obs_studio_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.group("filter")
def filter_group():
    """Filter management commands."""
    pass


@filter_group.command("add")
@click.argument("filter_type", type=click.Choice(sorted(filt_mod.FILTER_TYPES.keys())))
@click.option(
    "--source", "-S", "source_index", type=int, default=0, help="Source index"
)
@click.option("--scene", "-s", "scene_index", type=int, default=0, help="Scene index")
@click.option("--name", "-n", default=None, help="Filter name")
@click.option("--param", "-p", multiple=True, help="Parameter: key=value")
@handle_error
def filter_add(filter_type, source_index, scene_index, name, param):
    """Add a filter to a source."""
    params = {}
    for p in param:
        if "=" not in p:
            raise ValueError(f"Invalid param format: '{p}'. Use key=value.")
        k, v = p.split("=", 1)
        try:
            v = float(v) if "." in v else int(v)
        except ValueError:
            pass
        params[k] = v

    sess = get_session()
    sess.snapshot(f"Add filter: {filter_type}")
    filt = filt_mod.add_filter(
        sess.get_project(),
        filter_type,
        source_index,
        scene_index,
        name=name,
        params=params if params else None,
    )
    output(filt, f"Added filter: {filt['name']}")


@filter_group.command("remove")
@click.argument("filter_index", type=int)
@click.option("--source", "-S", "source_index", type=int, default=0)
@click.option("--scene", "-s", "scene_index", type=int, default=0)
@handle_error
def filter_remove(filter_index, source_index, scene_index):
    """Remove a filter from a source."""
    sess = get_session()
    sess.snapshot(f"Remove filter {filter_index}")
    removed = filt_mod.remove_filter(
        sess.get_project(), filter_index, source_index, scene_index
    )
    output(removed, f"Removed filter: {removed['name']}")


@filter_group.command("set")
@click.argument("filter_index", type=int)
@click.argument("param")
@click.argument("value")
@click.option("--source", "-S", "source_index", type=int, default=0)
@click.option("--scene", "-s", "scene_index", type=int, default=0)
@handle_error
def filter_set(filter_index, param, value, source_index, scene_index):
    """Set a filter parameter."""
    try:
        value = float(value) if "." in str(value) else int(value)
    except ValueError:
        pass
    sess = get_session()
    sess.snapshot(f"Set filter {filter_index} {param}={value}")
    filt_mod.set_filter_param(
        sess.get_project(),
        filter_index,
        param,
        value,
        source_index,
        scene_index,
    )
    output(
        {"filter": filter_index, "param": param, "value": value},
        f"Set filter {filter_index} {param} = {value}",
    )


@filter_group.command("list")
@click.option("--source", "-S", "source_index", type=int, default=0)
@click.option("--scene", "-s", "scene_index", type=int, default=0)
@handle_error
def filter_list(source_index, scene_index):
    """List all filters on a source."""
    sess = get_session()
    filters = filt_mod.list_filters(sess.get_project(), source_index, scene_index)
    output(filters, "Filters:")


@filter_group.command("list-available")
@click.option(
    "--category", "-c", type=str, default=None, help="Filter by category: video, audio"
)
@handle_error
def filter_list_available(category):
    """List all available filter types."""
    filters = filt_mod.list_available_filters(category)
    output(filters, "Available filters:")


@cli.group("audio")
def audio_group():
    """Audio management commands."""
    pass


@audio_group.command("add")
@click.option("--name", "-n", default="Audio", help="Audio source name")
@click.option(
    "--type", "audio_type", type=click.Choice(["input", "output"]), default="input"
)
@click.option("--device", "-d", default="", help="Device identifier")
@click.option("--volume", "-v", type=float, default=1.0, help="Volume (0.0-3.0)")
@handle_error
def audio_add(name, audio_type, device, volume):
    """Add a global audio source."""
    sess = get_session()
    sess.snapshot(f"Add audio: {name}")
    src = audio_mod.add_audio_source(
        sess.get_project(),
        name=name,
        audio_type=audio_type,
        device=device,
        volume=volume,
    )
    output(src, f"Added audio source: {src['name']}")


@audio_group.command("remove")
@click.argument("index", type=int)
@handle_error
def audio_remove(index):
    """Remove a global audio source."""
    sess = get_session()
    sess.snapshot(f"Remove audio {index}")
    removed = audio_mod.remove_audio_source(sess.get_project(), index)
    output(removed, f"Removed audio: {removed['name']}")
