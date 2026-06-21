# ruff: noqa: F403, F405, E501
from .kdenlive_cli_base import *  # noqa: F403

# fmt: off
from .kdenlive_cli_p1 import cli, get_session, handle_error, output  # noqa: E402,E501
from .kdenlive_cli_p4 import filter_group  # noqa: E402,E501
# fmt: on


@filter_group.command("set")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.argument("filter_index", type=int)
@click.argument("param_name")
@click.argument("value")
@handle_error
def filter_set(track_id, clip_index, filter_index, param_name, value):
    """Set a filter parameter."""
    try:
        value = float(value) if "." in str(value) else int(value)
    except ValueError:
        pass
    sess = get_session()
    sess.snapshot("Set filter param")
    result = filt_mod.set_filter_param(
        sess.get_project(), track_id, clip_index, filter_index, param_name, value
    )
    output(result, f"Set {param_name} = {value}")


@filter_group.command("list")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@handle_error
def filter_list(track_id, clip_index):
    """List filters on a clip."""
    sess = get_session()
    filters = filt_mod.list_filters(sess.get_project(), track_id, clip_index)
    output(filters, "Filters:")


@filter_group.command("available")
@click.option("--category", "-c", default=None, help="Filter by category")
@handle_error
def filter_available(category):
    """List all available filters."""
    filters = filt_mod.list_available(category)
    output(filters, "Available filters:")


@cli.group()
def transition():
    """Transition management commands."""
    pass


@transition.command("add")
@click.argument("transition_type")
@click.argument("track_a", type=int)
@click.argument("track_b", type=int)
@click.option("--position", "-p", type=float, default=0.0)
@click.option("--duration", "-d", type=float, default=1.0)
@click.option("--param", multiple=True, help="Parameter: key=value")
@handle_error
def transition_add(transition_type, track_a, track_b, position, duration, param):
    """Add a transition between tracks."""
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
    sess.snapshot(f"Add transition {transition_type}")
    result = trans_mod.add_transition(
        sess.get_project(),
        transition_type,
        track_a,
        track_b,
        position=position,
        duration=duration,
        params=params if params else None,
    )
    output(result, f"Added transition: {transition_type}")


@transition.command("remove")
@click.argument("transition_id", type=int)
@handle_error
def transition_remove(transition_id):
    """Remove a transition."""
    sess = get_session()
    sess.snapshot(f"Remove transition {transition_id}")
    removed = trans_mod.remove_transition(sess.get_project(), transition_id)
    output(removed, f"Removed transition {transition_id}")


@transition.command("set")
@click.argument("transition_id", type=int)
@click.argument("param_name")
@click.argument("value")
@handle_error
def transition_set(transition_id, param_name, value):
    """Set a transition parameter."""
    try:
        value = float(value) if "." in str(value) else int(value)
    except ValueError:
        pass
    sess = get_session()
    sess.snapshot("Set transition param")
    result = trans_mod.set_transition(
        sess.get_project(), transition_id, param_name, value
    )
    output(result, f"Set {param_name} = {value}")


@transition.command("list")
@handle_error
def transition_list():
    """List all transitions."""
    sess = get_session()
    transitions = trans_mod.list_transitions(sess.get_project())
    output(transitions, "Transitions:")


@cli.group()
def guide():
    """Guide/marker management commands."""
    pass
