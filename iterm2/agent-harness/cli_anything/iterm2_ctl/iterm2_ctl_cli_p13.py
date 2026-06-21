# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import cli, handle_iterm2_error, output  # noqa: E402,E501
from .iterm2_ctl_cli_p12 import pref  # noqa: E402,E501
# fmt: on


@pref.command("tmux-get")
@handle_iterm2_error
def pref_tmux_get():
    """Show all tmux-related preferences."""
    result = run_iterm2(pref_mod.get_tmux_preferences)
    output(result)
    if not _json_output:
        click.echo(
            f"  open_in:    {result['open_tmux_windows_in']} "
            f"({result['open_tmux_windows_in_label']})"
        )
        click.echo(f"  dash_limit: {result['tmux_dashboard_limit']}")
        click.echo(f"  auto_hide:  {result['auto_hide_tmux_client_session']}")
        click.echo(f"  use_profile:{result['use_tmux_profile']}")


@pref.command("tmux-set")
@click.argument(
    "setting",
    type=click.Choice(
        ["open_in", "dashboard_limit", "auto_hide_client", "use_profile"]
    ),
)
@click.argument("value")
@handle_iterm2_error
def pref_tmux_set(setting, value):
    """Set a tmux preference by name.

    \b
      open_in: 0=native_windows  1=new_window  2=tabs_in_existing
      dashboard_limit: integer
      auto_hide_client: true/false
      use_profile: true/false
    """
    result = run_iterm2(pref_mod.set_tmux_preference, setting, value)
    output(result, f"Set tmux.{setting} = {result['value']}")


@pref.command("list-keys")
@click.option(
    "--filter",
    "name_filter",
    default=None,
    help="Filter key names by substring (case-insensitive).",
)
def pref_list_keys(name_filter):
    """List all valid preference key names for use with `pref get/set`.

    \b
      cli-anything-iterm2 pref list-keys
      cli-anything-iterm2 pref list-keys --filter tmux
      cli-anything-iterm2 pref list-keys --filter font
    """
    from iterm2.preferences import PreferenceKey

    keys = sorted(k.name for k in PreferenceKey)
    if name_filter:
        keys = [k for k in keys if name_filter.lower() in k.lower()]
    data = {"keys": keys, "count": len(keys)}
    output(data, f"{len(keys)} preference key(s)")
    if not _json_output:
        for k in keys:
            click.echo(f"  {k}")


@pref.command("theme")
@handle_iterm2_error
def pref_theme():
    """Get the current iTerm2 theme tags."""
    result = run_iterm2(pref_mod.get_theme)
    output(result, f"Theme: {', '.join(result['tags'])}  dark={result['is_dark']}")


def main():
    cli()
