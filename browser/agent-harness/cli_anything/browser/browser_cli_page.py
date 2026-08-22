"""Page-navigation command registration for the browser CLI."""

from __future__ import annotations

import click

from cli_anything.browser.core import page as page_mod


def register_page_commands(root, get_session, output, handle_error) -> None:
    """Attach page commands without coupling them to CLI process state."""

    @root.group()
    def page():
        """Page navigation commands."""

    @page.command("open")
    @click.argument("url")
    @handle_error
    def page_open(url):
        """Open a URL in Chrome."""

        output(page_mod.open_page(get_session(), url), f"Opened: {url}")

    @page.command("reload")
    @handle_error
    def page_reload():
        """Reload the current page."""

        output(page_mod.reload_page(get_session()), "Page reloaded")

    @page.command("back")
    @handle_error
    def page_back():
        """Navigate back in history."""

        result = page_mod.go_back(get_session())
        output(result, result.get("error", "Navigated back"))

    @page.command("forward")
    @handle_error
    def page_forward():
        """Navigate forward in history."""

        result = page_mod.go_forward(get_session())
        output(result, result.get("error", "Navigated forward"))

    @page.command("info")
    @handle_error
    def page_info():
        """Show current page information."""

        output(page_mod.get_page_info(get_session()))
