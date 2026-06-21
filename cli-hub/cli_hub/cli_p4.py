# ruff: noqa: F403, F405, E501
from .cli_base import *  # noqa: F403

# fmt: off
from .cli_p1 import _invocation_command  # noqa: E402,E501
from .cli_p3 import previews  # noqa: E402,E501
# fmt: on


def _serve_live_session(session_ref, poll_ms, auto_open, port):
    session_dir, session = load_session(session_ref)
    output_path = Path(session_dir) / "live.html"
    render_live_html(session_ref, str(output_path), poll_ms=poll_ms)
    server, base_url = start_static_server(str(session_dir), port=port)
    live_url = f"{base_url}/live.html"
    click.echo(f"Live preview URL: {live_url}")
    if auto_open:
        launched = open_in_browser(live_url)
        if launched.get("launched"):
            click.echo(f"Opened in {launched['browser']}: pid {launched['pid']}")
        else:
            click.echo(
                "Browser launch unavailable. Open this manually:\n"
                f"  {live_url}\n"
                f"  Suggested command: {session.get('watch_command') or f'cli-hub previews watch {session_dir} --open'}"
            )
    click.echo("Press Ctrl-C to stop the live preview server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        click.echo("\nStopped live preview server.")
    finally:
        server.server_close()


@previews.command("watch")
@click.argument("session_ref")
@click.option(
    "--poll-ms",
    default=1500,
    show_default=True,
    help="Polling interval for the live page.",
)
@click.option(
    "--port",
    default=0,
    show_default=True,
    help="Preferred localhost port. Use 0 for auto.",
)
@click.option(
    "--open/--no-open",
    "auto_open",
    default=False,
    help="Open a separate browser window.",
)
def preview_watch(session_ref, poll_ms, port, auto_open):
    """Serve and watch a live preview session."""
    _serve_live_session(session_ref, poll_ms=poll_ms, auto_open=auto_open, port=port)


@previews.command("open")
@click.argument("preview_ref")
@click.option(
    "--output",
    "-o",
    "output_path",
    default=None,
    help="Override the generated HTML path.",
)
@click.option(
    "--poll-ms",
    default=1500,
    show_default=True,
    help="Polling interval when opening a live session.",
)
@click.option(
    "--port",
    default=0,
    show_default=True,
    help="Preferred localhost port for live sessions.",
)
def preview_open(preview_ref, output_path, poll_ms, port):
    """Open a preview bundle or live session in a browser window."""
    if is_live_session_ref(preview_ref):
        _serve_live_session(preview_ref, poll_ms=poll_ms, auto_open=True, port=port)
        return
    if output_path is None:
        payload = inspect_bundle(preview_ref)
        output_path = os.path.join(payload["bundle_dir"], "preview.html")
    rendered = render_html(preview_ref, output_path)
    launched = open_in_browser(Path(rendered).resolve().as_uri())
    click.echo(rendered)
    if launched.get("launched"):
        click.echo(f"Opened in {launched['browser']}: pid {launched['pid']}")
    else:
        click.echo(f"Open this file manually: {rendered}")


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version.")
@click.pass_context
def main(ctx, version):
    """cli-hub — Download and manage CLI-Anything harnesses and public CLIs."""
    track_first_run()
    track_visit(
        command=_invocation_command(ctx, version), detection=detect_invocation_context()
    )
    if version:
        click.echo(f"cli-hub {__version__}")
        return
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
