"""Session-management command registration for the browser CLI."""

from __future__ import annotations


def register_session_commands(root, get_session, output, handle_error, backend) -> None:
    """Attach session and daemon controls to the root command group."""

    @root.group()
    def session():
        """Session management commands."""

    @session.command("status")
    @handle_error
    def session_status():
        """Show current session status."""

        output(get_session().status())

    @session.command("daemon-start")
    @handle_error
    def session_daemon_start():
        """Start persistent daemon mode."""

        try:
            backend.start_daemon()
            get_session().enable_daemon()
            output({"daemon": "started"}, "Daemon mode started")
        except RuntimeError as error:
            output({"error": str(error)}, str(error))

    @session.command("daemon-stop")
    @handle_error
    def session_daemon_stop():
        """Stop persistent daemon mode."""

        backend.stop_daemon()
        get_session().disable_daemon()
        output({"daemon": "stopped"}, "Daemon mode stopped")
