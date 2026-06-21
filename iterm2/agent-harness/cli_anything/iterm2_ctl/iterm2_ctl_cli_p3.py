# ruff: noqa: F403, F405, E501
from .iterm2_ctl_cli_base import *  # noqa: F403

# fmt: off
from .iterm2_ctl_cli_p1 import cli, get_state, handle_iterm2_error, output, save_state_now  # noqa: E402,E501
# fmt: on


@cli.group()
def app():
    """Application-level information and status."""


@app.command("status")
@handle_iterm2_error
def app_status():
    """Show current iTerm2 app status (windows, tabs, sessions)."""

    def _get_status(connection):
        import asyncio

        async def _inner(conn):
            import iterm2

            a = await iterm2.async_get_app(conn)
            windows = []
            for w in a.windows:
                tabs = []
                for t in w.tabs:
                    sessions = [
                        {"session_id": s.session_id, "name": s.name} for s in t.sessions
                    ]
                    tabs.append({"tab_id": t.tab_id, "sessions": sessions})
                windows.append({"window_id": w.window_id, "tabs": tabs})
            return {
                "window_count": len(a.windows),
                "windows": windows,
            }

        return _inner(connection)

    result = run_iterm2(_get_status)
    output(result, f"iTerm2: {result['window_count']} window(s)")


@app.command("current")
@handle_iterm2_error
def app_current():
    """Show the currently focused window/tab/session."""
    result = run_iterm2(win_mod.get_current_window)
    if result is None:
        output({"current": None}, "No window is currently focused.")
    else:
        state = get_state()
        state.window_id = result.get("window_id")
        state.tab_id = result.get("tab_id")
        state.session_id = result.get("session_id")
        save_state_now()
        output(
            result,
            f"Current: window={result.get('window_id')} "
            f"tab={result.get('tab_id')} session={result.get('session_id')}",
        )


@app.command("context")
def app_context():
    """Show the saved session context (current window/tab/session IDs)."""
    state = get_state()
    data = state.to_dict()
    output(data, f"Context: {state.summary()}")


@app.command("set-context")
@click.option("--window-id", default=None, help="Window ID to set as current.")
@click.option("--tab-id", default=None, help="Tab ID to set as current.")
@click.option("--session-id", default=None, help="Session ID to set as current.")
def app_set_context(window_id, tab_id, session_id):
    """Manually set the session context (window/tab/session IDs)."""
    state = get_state()
    if window_id:
        state.window_id = window_id
    if tab_id:
        state.tab_id = tab_id
    if session_id:
        state.session_id = session_id
    save_state_now()
    output(state.to_dict(), f"Context updated: {state.summary()}")


@app.command("clear-context")
def app_clear_context():
    """Clear the saved session context."""
    state = get_state()
    state.clear()
    save_state_now()
    output({}, "Context cleared.")


@app.command("get-var")
@click.argument("variable_name")
@handle_iterm2_error
def app_get_var(variable_name):
    """Get an app-level iTerm2 variable."""

    def _get(conn):
        async def _inner(c):
            import iterm2

            a = await iterm2.async_get_app(c)
            value = await a.async_get_variable(variable_name)
            return {"variable": variable_name, "value": value}

        return _inner(conn)

    result = run_iterm2(_get)
    output(result, f"{variable_name} = {result['value']}")


@app.command("set-var")
@click.argument("variable_name")
@click.argument("value")
@handle_iterm2_error
def app_set_var(variable_name, value):
    """Set an app-level iTerm2 variable (user.* namespace)."""

    def _set(conn):
        async def _inner(c):
            import iterm2

            a = await iterm2.async_get_app(c)
            await a.async_set_variable(variable_name, value)
            return {"variable": variable_name, "value": value, "set": True}

        return _inner(conn)

    result = run_iterm2(_set)
    output(result, f"Set {variable_name} = {value}")
