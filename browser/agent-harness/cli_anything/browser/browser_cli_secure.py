"""Secure-runtime command registration for the browser CLI."""

from __future__ import annotations


def register_secure_commands(root, output, handle_error, backend) -> None:
    """Attach non-secret secure-runtime lifecycle controls."""

    @root.group()
    def secure():
        """Inspect or control the private DNS-pinned browser runtime."""

    @secure.command("status")
    @handle_error
    def secure_status():
        """Show non-secret managed runtime state."""

        output(backend.secure_runtime_status())

    @secure.command("start")
    @handle_error
    def secure_start():
        """Start the managed browser and its DNS-pinning egress proxy."""

        available, message = backend.is_available()
        if not available:
            raise RuntimeError(message)
        output(backend.secure_runtime_status(), message)

    @secure.command("install")
    @handle_error
    def secure_install():
        """Install the lockfile-verified local DOMShell runtime."""

        output(backend.install_secure_runtime(), "Installed verified local DOMShell runtime")

    @secure.command("stop")
    @handle_error
    def secure_stop():
        """Stop the managed browser, DOMShell server, and egress proxy."""

        backend.stop_daemon()
        backend.stop_secure_runtime()
        output({"managed": False}, "Managed secure runtime stopped")
