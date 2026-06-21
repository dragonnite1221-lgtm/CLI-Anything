# ruff: noqa: F403, F405, E501
from .nslogger_cli_base import *  # noqa: F403
# fmt: off
from .nslogger_cli_p1 import _json_option, _level_option, cli  # noqa: E402,E501
from .nslogger_cli_p2 import _run_repl  # noqa: E402,E501
# fmt: on


@cli.command()
@click.argument("output", type=click.Path())
@click.option("--count", "-n", type=int, default=20, show_default=True,
              help="Number of log messages to generate")
def generate(output, count):
    """Generate a sample .rawnsloggerdata file for testing."""
    from .utils.generate import generate_sample_file
    generate_sample_file(output, count=count)
    click.echo(f"Generated {count} messages → {output}")
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--count", "-n", type=int, default=20, show_default=True,
              help="Number of messages from the end to show")
@_level_option()
@click.option("--tag", "-t", multiple=True, help="Filter by tag before tailing")
@_json_option()
def tail(file, count, level, tag, as_json):
    """Show the last N messages from a file (reverse of --limit in read)."""
    msgs = parse_file(file)
    msgs = filter_messages(
        msgs,
        max_level=level,
        tags=list(tag) if tag else None,
    )
    all_msgs = list(msgs)
    result = all_msgs[-count:]
    if as_json:
        click.echo(json.dumps([m.to_dict() for m in result], indent=2, default=str))
    else:
        for m in result:
            click.echo(m.to_text_line())
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@_json_option()
def clients(file, as_json):
    """List all client connections recorded in a NSLogger file."""
    from .core.blocks import extract_clients
    msgs = parse_file(file)
    client_list = extract_clients(msgs)
    if as_json:
        click.echo(json.dumps(client_list, indent=2, default=str))
    else:
        if not client_list:
            click.echo("No client_info messages found.")
            return
        for c in client_list:
            ts = c.get("timestamp") or "?"
            name = c.get("client_name") or "unknown"
            ver = c.get("client_version") or ""
            os_ = f"{c.get('os_name', '')} {c.get('os_version', '')}".strip()
            machine = c.get("machine") or ""
            click.echo(f"[{ts}] {name} {ver}  {os_}  {machine}".strip())
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--indent", type=int, default=2, show_default=True,
              help="Spaces per indent level")
@_json_option()
def blocks(file, indent, as_json):
    """Show the block start/end structure from a NSLogger file as an indented tree."""
    from .core.blocks import iter_block_tree
    msgs = parse_file(file)
    entries = list(iter_block_tree(msgs))
    if as_json:
        result = [
            {"depth": depth, **m.to_dict()}
            for depth, m in entries
        ]
        click.echo(json.dumps(result, indent=2, default=str))
    else:
        for depth, m in entries:
            prefix = " " * (depth * indent)
            click.echo(f"{prefix}{m.to_text_line()}")
@cli.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write merged output to file (default: stdout)")
@click.option("--format", "-f", "fmt",
              type=click.Choice(["text", "json", "csv"]), default="text",
              show_default=True)
@_level_option()
def merge(files, output, fmt, level):
    """Merge multiple NSLogger files, sorted by timestamp."""
    from .core.blocks import merge_files
    all_msgs = merge_files(list(files))
    if level is not None:
        all_msgs = [m for m in all_msgs if m.level <= level]
    from .core.exporter import export_messages
    result_str = export_messages(iter(all_msgs), fmt=fmt)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result_str)
        click.echo(f"Merged {len(files)} files → {output}", err=True)
    else:
        click.echo(result_str, nl=False)
@cli.command()
@click.argument("file", type=click.Path(exists=True), required=False)
@click.pass_context
def repl(ctx, file):
    """Start an interactive command REPL for NSLogger files."""
    _run_repl(ctx, file=file)
def main():
    cli()
