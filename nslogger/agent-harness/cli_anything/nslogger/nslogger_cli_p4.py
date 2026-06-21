# ruff: noqa: F403, F405, E501
from .nslogger_cli_base import *  # noqa: F403
# fmt: off
from .nslogger_cli_p1 import _format_live_output_message, _json_option, _listen_waiting_message, _open_live_output_file, cli  # noqa: E402,E501
# fmt: on


@cli.command(short_help="Listen for live logs; use --output FILE to mirror them to disk.")
@click.option("--port", "-p", type=int, default=50000, show_default=True,
              help="TCP port to listen on")
@click.option("--timeout", "-t", type=float, default=None,
              help="Stop after N seconds (default: run until Ctrl-C)")
@click.option("--level", "-l", type=int, default=None,
              help="Maximum level to display while listening")
@click.option("--bonjour", "-b", is_flag=True, default=False,
              help="Advertise via Bonjour/mDNS (iOS app auto-discovers, no IP config needed)")
@click.option("--name", "-n", default=None,
              help="Bonjour service name (default: system-selected name)")
@click.option("--ssl", "force_ssl", is_flag=True,
              help="Use SSL/TLS for direct TCP mode; Bonjour uses SSL by default")
@click.option("--no-ssl", is_flag=True, help="Advertise/use the legacy non-SSL NSLogger Bonjour service")
@click.option("--bonjour-mode", type=click.Choice(["auto", "ssl", "raw"]), default="ssl", show_default=True,
              help="Bonjour service mode: ssl matches NSLogger GUI default, auto publishes raw+SSL, raw publishes legacy raw only")
@click.option("--bonjour-publisher", type=click.Choice(["native", "dns-sd", "zeroconf"]), default="native", show_default=True,
              help="Bonjour publisher backend")
@click.option("--advertise-host", default=None,
              help="IP address to publish when using --bonjour-publisher zeroconf")
@click.option("--filter-clients/--no-filter-clients", default=None,
              help="Advertise filterClients=1; defaults to on when --name is non-empty, matching NSLogger GUI")
@click.option("--output", "-o", type=click.Path(dir_okay=False, path_type=str),
              help="Write received live logs to this file while still printing to stdout")
@click.option("--output-format", type=click.Choice(["text", "jsonl"]), default="text", show_default=True,
              help="Format used for --output")
@click.option("--append", is_flag=True,
              help="Append to --output instead of replacing it at listener startup")
@click.option("--debug", is_flag=True, help="Print live frame diagnostics to stderr")
@_json_option()
def listen(
    port, timeout, level, bonjour, name, force_ssl, no_ssl, bonjour_mode,
    bonjour_publisher, advertise_host, filter_clients, output, output_format,
    append, debug, as_json
):
    """Listen for live NSLogger connections.

    \b
    TCP mode (default):
      cli-anything-nslogger listen --port 50000

    Bonjour mode (iOS auto-discovers on same WiFi):
      cli-anything-nslogger listen --bonjour --name bazinga
    """
    from .core.listener import NSLoggerListener

    collected = []
    output_file = _open_live_output_file(output, append) if output else None

    def on_message(msg):
        if level is not None and msg.level > level:
            return
        collected.append(msg)
        if output_file:
            output_file.write(_format_live_output_message(msg, output_format) + "\n")
        if as_json:
            click.echo(json.dumps(msg.to_dict(), default=str))
        else:
            click.echo(msg.to_text_line())

    def on_connect(host, p):
        click.echo(f"[+] Client connected: {host}:{p}", err=True)

    def on_disconnect(host, p):
        click.echo(f"[-] Client disconnected: {host}:{p}", err=True)

    def on_bonjour_ready(svc_name, svc_port):
        click.echo(f"[Bonjour] Advertising as '{svc_name}' on port {svc_port}", err=True)
        click.echo(f"[Bonjour] iOS app will auto-discover — no IP config needed", err=True)

    def on_parse_error(host, p, raw, exc):
        if not debug:
            return
        head = raw[:32].hex(" ")
        click.echo(
            f"[debug] Dropped frame from {host}:{p}: len={len(raw)} head={head} error={exc}",
            err=True,
        )

    def on_debug(message):
        if debug:
            click.echo(f"[debug] {message}", err=True)

    if no_ssl:
        bonjour_mode = "raw"
    use_ssl = force_ssl
    if bonjour:
        use_ssl = False if bonjour_mode == "raw" else None
    allow_plaintext = bonjour_mode != "ssl"

    listener = NSLoggerListener(
        port=port,
        timeout=timeout,
        on_message=on_message,
        on_connect=on_connect,
        on_disconnect=on_disconnect,
        on_bonjour_ready=on_bonjour_ready,
        on_parse_error=on_parse_error,
        on_debug=on_debug,
        use_ssl=use_ssl,
        allow_plaintext=allow_plaintext,
        bonjour=bonjour,
        bonjour_name=name,
        filter_clients=filter_clients,
        bonjour_publisher=bonjour_publisher,
        advertise_host=advertise_host,
    )

    if bonjour:
        click.echo(f"Starting Bonjour listener on port {port}…  (Ctrl-C to stop)", err=True)
    else:
        click.echo(f"Listening on TCP port {port}…  (Ctrl-C to stop)", err=True)
    click.echo(_listen_waiting_message(port, bonjour), err=True)
    if output:
        action = "Appending" if append else "Writing"
        click.echo(f"[output] {action} live logs to {output} ({output_format})", err=True)

    try:
        listener.listen()
    except KeyboardInterrupt:
        pass
    finally:
        if output_file:
            output_file.close()
    click.echo(f"\nCaptured {len(collected)} messages.", err=True)
