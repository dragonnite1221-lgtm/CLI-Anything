# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import cli, get_state, handle_iterm2_error, output  # noqa: E402,E501
# fmt: on


@cli.group()
def broadcast():
    """Control broadcast domains (sync keystrokes across panes)."""


@broadcast.command("list")
@handle_iterm2_error
def broadcast_list():
    """List current broadcast domains."""
    result = run_iterm2(bcast_mod.get_broadcast_domains)
    output(
        {"domains": result},
        f"{len(result)} broadcast domain(s)"
        if result
        else "No active broadcast domains.",
    )
    if not _json_output and result:
        for i, d in enumerate(result, 1):
            click.echo(f"  domain {i}: {', '.join(d['sessions'])}")


@broadcast.command("set")
@click.argument("groups", nargs=-1, required=True)
@handle_iterm2_error
def broadcast_set(groups):
    """Set broadcast domains from session ID groups.

    Each argument is a comma-separated list of session IDs forming one domain.

    \b
      cli-anything-iterm2 broadcast set "s1,s2" "s3,s4"
    """
    domain_groups = [g.split(",") for g in groups]
    result = run_iterm2(bcast_mod.set_broadcast_domains, domain_groups)
    output(result, f"Set {result['domain_count']} broadcast domain(s)")


@broadcast.command("add")
@click.argument("session_ids", nargs=-1, required=True)
@handle_iterm2_error
def broadcast_add(session_ids):
    """Add sessions to a new broadcast domain.

    SESSION_IDS: One or more session IDs to group into one domain.
    Existing domains are preserved.

    \b
      cli-anything-iterm2 broadcast add s1 s2
    """
    result = run_iterm2(bcast_mod.add_to_broadcast, list(session_ids))
    output(result, f"Added {len(session_ids)} session(s) to new broadcast domain")


@broadcast.command("clear")
@handle_iterm2_error
def broadcast_clear():
    """Clear all broadcast domains, stopping all input sync."""
    result = run_iterm2(bcast_mod.clear_broadcast)
    output(result, "All broadcast domains cleared.")


@broadcast.command("all-panes")
@click.option(
    "--window-id",
    default=None,
    help="Scope to a specific window (default: all windows).",
)
@handle_iterm2_error
def broadcast_all_panes(window_id):
    """Sync keystrokes across all panes in all windows (or one window)."""
    wid = window_id or get_state().window_id
    result = run_iterm2(bcast_mod.broadcast_all_panes, window_id=wid)
    output(result, f"Broadcasting to {result['session_count']} session(s)")


@cli.group()
def menu():
    """Invoke iTerm2 menu items programmatically."""


@menu.command("select")
@click.argument("identifier")
@handle_iterm2_error
def menu_select(identifier):
    """Invoke a menu item by its identifier string.

    IDENTIFIER: e.g. "Shell/Split Vertically with Current Profile"

    Run `menu list-common` to see available identifiers.
    """
    result = run_iterm2(menu_mod.select_menu_item, identifier)
    output(result, f"Invoked: {identifier}")


@menu.command("state")
@click.argument("identifier")
@handle_iterm2_error
def menu_state(identifier):
    """Get the checked/enabled state of a menu item."""
    result = run_iterm2(menu_mod.get_menu_item_state, identifier)
    output(
        result, f"{identifier}: checked={result['checked']} enabled={result['enabled']}"
    )


@menu.command("list-common")
@handle_iterm2_error
def menu_list_common():
    """List commonly useful menu item identifiers."""
    result = run_iterm2(menu_mod.list_common_menu_items)
    output({"menu_items": result}, f"{len(result)} common menu item(s)")
    if not _json_output and result:
        for item in result:
            click.echo(f"  {item['identifier']}")
            click.echo(f"    {item['description']}")


@cli.group()
def pref():
    """Read and write iTerm2 global preferences."""


@pref.command("get")
@click.argument("key")
@handle_iterm2_error
def pref_get(key):
    """Get a preference by key name (PreferenceKey enum name or raw string)."""
    result = run_iterm2(pref_mod.get_preference, key)
    output(result, f"{result['key']} = {result['value']}")


@pref.command("set")
@click.argument("key")
@click.argument("value")
@handle_iterm2_error
def pref_set(key, value):
    """Set a preference by key name."""
    result = run_iterm2(pref_mod.set_preference, key, value)
    output(result, f"Set {result['key']} = {result['value']}")
