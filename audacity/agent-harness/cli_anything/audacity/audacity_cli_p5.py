# ruff: noqa: F403, F405, E501
from .audacity_cli_base import *  # noqa: F403

# fmt: off
from .audacity_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .audacity_cli_p4 import effect_group  # noqa: E402,E501
# fmt: on


@effect_group.command("add")
@click.argument("name")
@click.option("--track", "-t", "track_index", type=int, default=0, help="Track index")
@click.option("--param", "-p", multiple=True, help="Parameter: key=value")
@handle_error
def effect_add(name, track_index, param):
    """Add an effect to a track."""
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
    sess.snapshot(f"Add effect {name} to track {track_index}")
    result = fx_mod.add_effect(sess.get_project(), name, track_index, params)
    output(result, f"Added effect: {name}")


@effect_group.command("remove")
@click.argument("effect_index", type=int)
@click.option("--track", "-t", "track_index", type=int, default=0)
@handle_error
def effect_remove(effect_index, track_index):
    """Remove an effect by index."""
    sess = get_session()
    sess.snapshot(f"Remove effect {effect_index} from track {track_index}")
    result = fx_mod.remove_effect(sess.get_project(), effect_index, track_index)
    output(result, f"Removed effect {effect_index}")


@effect_group.command("set")
@click.argument("effect_index", type=int)
@click.argument("param")
@click.argument("value")
@click.option("--track", "-t", "track_index", type=int, default=0)
@handle_error
def effect_set(effect_index, param, value, track_index):
    """Set an effect parameter."""
    try:
        value = float(value) if "." in str(value) else int(value)
    except ValueError:
        pass
    sess = get_session()
    sess.snapshot(f"Set effect {effect_index} {param}={value}")
    fx_mod.set_effect_param(sess.get_project(), effect_index, param, value, track_index)
    output(
        {"effect": effect_index, "param": param, "value": value},
        f"Set effect {effect_index} {param} = {value}",
    )


@effect_group.command("list")
@click.option("--track", "-t", "track_index", type=int, default=0)
@handle_error
def effect_list(track_index):
    """List effects on a track."""
    sess = get_session()
    effects = fx_mod.list_effects(sess.get_project(), track_index)
    output(effects, f"Effects on track {track_index}:")


@cli.group()
def selection():
    """Selection management commands."""
    pass


@selection.command("set")
@click.argument("start", type=float)
@click.argument("end", type=float)
@handle_error
def selection_set(start, end):
    """Set selection range."""
    sess = get_session()
    result = sel_mod.set_selection(sess.get_project(), start, end)
    output(result, f"Selection: {start}s - {end}s")


@selection.command("all")
@handle_error
def selection_all():
    """Select all (entire project duration)."""
    sess = get_session()
    result = sel_mod.select_all(sess.get_project())
    output(result, "Selected all")


@selection.command("none")
@handle_error
def selection_none():
    """Clear selection."""
    sess = get_session()
    result = sel_mod.select_none(sess.get_project())
    output(result, "Selection cleared")


@selection.command("info")
@handle_error
def selection_info():
    """Show current selection."""
    sess = get_session()
    result = sel_mod.get_selection(sess.get_project())
    output(result)


@cli.group()
def label():
    """Label/marker management commands."""
    pass


@label.command("add")
@click.argument("start", type=float)
@click.option(
    "--end", "-e", type=float, default=None, help="End time (for range labels)"
)
@click.option("--text", "-t", default="", help="Label text")
@handle_error
def label_add(start, end, text):
    """Add a label at a time position."""
    sess = get_session()
    sess.snapshot(f"Add label at {start}")
    result = label_mod.add_label(sess.get_project(), start, end, text)
    output(result, f"Added label: {text or f'at {start}s'}")
