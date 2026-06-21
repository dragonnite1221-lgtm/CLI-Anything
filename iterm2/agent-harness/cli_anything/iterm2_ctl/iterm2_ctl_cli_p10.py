# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import cli, get_state, handle_iterm2_error, output  # noqa: E402,E501
from .iterm2_ctl_cli_p5 import profile  # noqa: E402,E501
from .iterm2_ctl_cli_p6 import session  # noqa: E402,E501
# fmt: on


@session.command("wait-command-end")
@click.option("--session-id", default=None)
@click.option(
    "--timeout", "-t", type=float, default=30.0, help="Seconds to wait (default 30)."
)
@handle_iterm2_error
def session_wait_command_end(session_id, timeout):
    """Wait for the current command to finish (requires Shell Integration).

    Returns the exit status of the completed command.
    """
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(prompt_mod.wait_for_command_end, sid, timeout=timeout)
    if result.get("timed_out"):
        output(result, f"Timed out after {timeout}s.")
    else:
        output(result, f"Command ended, exit_status={result.get('exit_status')}")


@profile.command("list")
@click.option("--filter", "name_filter", default=None, help="Filter by name substring.")
@handle_iterm2_error
def profile_list(name_filter):
    """List all available profiles."""
    result = run_iterm2(profile_mod.list_profiles, name_filter=name_filter)
    output({"profiles": result}, f"{len(result)} profile(s)")
    if not _json_output and result:
        for p in result:
            click.echo(f"  {p['name']}  ({p['guid']})")


@profile.command("get")
@click.argument("guid")
@handle_iterm2_error
def profile_get(guid):
    """Get detailed settings for a profile by GUID.

    GUID: The profile GUID from `profile list`.

    \b
      cli-anything-iterm2 profile list          # find the GUID
      cli-anything-iterm2 profile get <guid>    # get details
    """
    result = run_iterm2(profile_mod.get_profile_detail, guid)
    output(result)
    if not _json_output:
        click.echo(f"  name:       {result['name']}")
        click.echo(f"  guid:       {result['guid']}")
        click.echo(f"  badge_text: {result.get('badge_text') or '(none)'}")


@profile.command("color-presets")
@handle_iterm2_error
def profile_color_presets():
    """List all available color presets."""
    result = run_iterm2(profile_mod.list_color_presets)
    output({"color_presets": result}, f"{len(result)} color preset(s)")
    if not _json_output and result:
        for p in result:
            click.echo(f"  {p}")


@profile.command("apply-preset")
@click.argument("preset_name")
@click.option("--session-id", default=None)
@handle_iterm2_error
def profile_apply_preset(preset_name, session_id):
    """Apply a color preset to a session."""
    sid = session_id or get_state().session_id
    if not sid:
        raise click.UsageError("No session ID specified.")
    result = run_iterm2(profile_mod.apply_color_preset, sid, preset_name)
    output(result, f"Applied preset '{preset_name}' to session {sid}")


@cli.group()
def arrangement():
    """Save and restore window arrangements."""


@arrangement.command("list")
@handle_iterm2_error
def arrangement_list():
    """List all saved arrangements."""
    result = run_iterm2(arr_mod.list_arrangements)
    output({"arrangements": result}, f"{len(result)} arrangement(s)")
    if not _json_output and result:
        for a in result:
            click.echo(f"  {a}")


@arrangement.command("save")
@click.argument("name")
@handle_iterm2_error
def arrangement_save(name):
    """Save all current windows as a named arrangement."""
    result = run_iterm2(arr_mod.save_arrangement, name)
    output(result, f"Saved arrangement '{name}'")


@arrangement.command("restore")
@click.argument("name")
@click.option(
    "--window-id",
    default=None,
    help="Restore into an existing window (default: open new windows).",
)
@handle_iterm2_error
def arrangement_restore(name, window_id):
    """Restore a saved arrangement."""
    wid = window_id or None
    result = run_iterm2(arr_mod.restore_arrangement, name, window_id=wid)
    output(result, f"Restored arrangement '{name}'")


@arrangement.command("save-window")
@click.argument("name")
@click.option("--window-id", default=None)
@handle_iterm2_error
def arrangement_save_window(name, window_id):
    """Save a single window as a named arrangement."""
    wid = window_id or get_state().window_id
    if not wid:
        raise click.UsageError("No window ID specified.")
    result = run_iterm2(arr_mod.save_window_arrangement, wid, name)
    output(result, f"Saved window {wid} as arrangement '{name}'")
