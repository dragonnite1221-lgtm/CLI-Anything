# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import get_state, handle_iterm2_error, output  # noqa: E402,E501
from .iterm2_ctl_cli_p3 import app  # noqa: E402,E501
# fmt: on


@app.command("alert")
@click.argument("title")
@click.argument("subtitle")
@click.option(
    "--button",
    "buttons",
    multiple=True,
    help="Add a button label. Repeat for multiple buttons.",
)
@click.option("--window-id", default=None, help="Attach to a specific window.")
@handle_iterm2_error
def app_alert(title, subtitle, buttons, window_id):
    """Show a modal alert dialog with optional custom buttons.

    Returns the label of the button the user clicked.

    \b
      cli-anything-iterm2 app alert "Deploy?" "Push to production?"
      cli-anything-iterm2 app alert "Choose" "Pick one" --button Yes --button No
    """
    wid = window_id or get_state().window_id
    result = run_iterm2(
        dlg_mod.show_alert,
        title,
        subtitle,
        buttons=list(buttons) or None,
        window_id=wid,
    )
    output(result, f"Clicked: {result['button_label']}")


@app.command("text-input")
@click.argument("title")
@click.argument("subtitle")
@click.option("--placeholder", default="", help="Gray placeholder text.")
@click.option("--default", "default_value", default="", help="Pre-filled text.")
@click.option("--window-id", default=None)
@handle_iterm2_error
def app_text_input(title, subtitle, placeholder, default_value, window_id):
    """Show a modal alert with a text input field.

    Returns the text the user typed, or indicates cancellation.

    \b
      cli-anything-iterm2 app text-input "Rename" "Enter new name:" --default "myapp"
    """
    wid = window_id or get_state().window_id
    result = run_iterm2(
        dlg_mod.show_text_input,
        title,
        subtitle,
        placeholder=placeholder,
        default_value=default_value,
        window_id=wid,
    )
    if result["cancelled"]:
        output(result, "Cancelled.")
    else:
        output(result, f"Input: {result['text']}")


@app.command("file-panel")
@click.option("--title", default="Open", help="Panel message text.")
@click.option("--path", default=None, help="Initial directory.")
@click.option(
    "--ext",
    "extensions",
    multiple=True,
    help="Allowed extensions, e.g. --ext py --ext txt",
)
@click.option("--dirs", is_flag=True, default=False, help="Allow choosing directories.")
@click.option(
    "--multi", is_flag=True, default=False, help="Allow multiple file selection."
)
@handle_iterm2_error
def app_file_panel(title, path, extensions, dirs, multi):
    """Show a macOS Open File panel and return the chosen path(s).

    \b
      cli-anything-iterm2 app file-panel
      cli-anything-iterm2 app file-panel --path ~/Documents --ext py --ext txt
      cli-anything-iterm2 app file-panel --dirs --multi
    """
    result = run_iterm2(
        dlg_mod.show_open_panel,
        title,
        path=path,
        extensions=list(extensions) or None,
        can_choose_directories=dirs,
        allows_multiple=multi,
    )
    if result["cancelled"]:
        output(result, "Cancelled.")
    else:
        output(result, f"Selected: {', '.join(result['files'])}")


@app.command("save-panel")
@click.option("--title", default="Save", help="Panel message text.")
@click.option("--path", default=None, help="Initial directory.")
@click.option("--filename", default=None, help="Pre-filled filename.")
@handle_iterm2_error
def app_save_panel(title, path, filename):
    """Show a macOS Save File panel and return the chosen path.

    \b
      cli-anything-iterm2 app save-panel
      cli-anything-iterm2 app save-panel --path ~/Desktop --filename output.txt
    """
    result = run_iterm2(dlg_mod.show_save_panel, title, path=path, filename=filename)
    if result["cancelled"]:
        output(result, "Cancelled.")
    else:
        output(result, f"Save to: {result['file']}")


@app.command("snapshot")
@handle_iterm2_error
def app_snapshot():
    """Rich workspace snapshot: every session with path, process, role, and last output line.

    \b
    Use this to orient in an existing workspace without reading full screen contents
    for every pane. Returns name, current directory, foreground process, user.role
    label, and the last non-empty visible line for each session.

      cli-anything-iterm2 --json app snapshot
    """
    result = run_iterm2(sess_mod.workspace_snapshot)
    output(result, f"Workspace: {result['session_count']} session(s)")
    if not _json_output:
        for s in result["sessions"]:
            role_tag = f" [{s['role']}]" if s.get("role") else ""
            process_tag = f" ({s['process']})" if s.get("process") else ""
            path_tag = f"  {s['path']}" if s.get("path") else ""
            click.echo(
                f"  {s['session_id']}  {s['name']}{role_tag}{process_tag}{path_tag}"
            )
            if s.get("last_line"):
                click.echo(f"    > {s['last_line']}")
