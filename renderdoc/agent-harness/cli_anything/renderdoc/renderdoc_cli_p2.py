# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403

# fmt: off
from .renderdoc_cli_p1 import _close_all_captures, _get_handle, _output, cli  # noqa: E402,E501
# fmt: on


@cli.command()
@click.pass_context
def repl(ctx):
    """Start interactive REPL session."""
    from cli_anything.renderdoc.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("renderdoc", version="0.1.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "capture": "info|thumb|convert",
        "actions": "list|summary|find|get",
        "textures": "list|get|save|save-outputs|pick",
        "pipeline": "state|shader-export|cbuffer|diff",
        "preview": "recipes|capture|diff|latest",
        "resources": "list|buffers|read-buffer",
        "mesh": "inputs|outputs",
        "counters": "list|fetch",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    capture_path = ctx.obj.get("capture_path", "")
    context = os.path.basename(capture_path) if capture_path else ""

    try:
        while True:
            try:
                line = skin.get_input(pt_session, project_name=context, modified=False)
                if not line:
                    continue
                if line.lower() in ("quit", "exit", "q"):
                    skin.print_goodbye()
                    break
                if line.lower() == "help":
                    skin.help(_repl_commands)
                    continue

                args = line.split()
                try:
                    cli.main(args, standalone_mode=False, obj=ctx.obj)
                except SystemExit:
                    pass
                except click.exceptions.UsageError as e:
                    skin.warning("Usage error: %s" % e)
                except Exception as e:
                    skin.error("%s" % e)

            except (EOFError, KeyboardInterrupt):
                skin.print_goodbye()
                break
    finally:
        _close_all_captures()
        _repl_mode = False


@cli.group("capture")
def capture_group():
    """Capture file operations."""
    pass


@capture_group.command("info")
@click.pass_context
def capture_info(ctx):
    """Show capture file metadata and sections."""
    handle = _get_handle(ctx)
    meta = handle.metadata()
    meta["sections"] = handle.list_sections()

    def _human(data):
        click.echo(f"Capture: {data['path']}")
        click.echo(f"API:     {data['api']}")
        click.echo(f"Replay:  {'yes' if data['replay_supported'] else 'no'}")
        click.echo(f"\nSections ({len(data['sections'])}):")
        for s in data["sections"]:
            click.echo(
                f"  [{s['index']}] {s['name']} ({s['type']}) - {s['uncompressed_size']} bytes"
            )

    _output(ctx, meta, _human)


@capture_group.command("thumb")
@click.option(
    "--output", "-o", required=True, type=click.Path(), help="Output image path."
)
@click.option(
    "--max-dim", default=0, type=int, help="Max thumbnail dimension (0 = original)."
)
@click.pass_context
def capture_thumb(ctx, output, max_dim):
    """Extract capture thumbnail to an image file."""
    handle = _get_handle(ctx)
    result = handle.thumbnail(output, max_dim)
    _output(ctx, result)


@capture_group.command("convert")
@click.option(
    "--output", "-o", required=True, type=click.Path(), help="Output file path."
)
@click.option("--format", "fmt", default="", help="Target format (default: rdc).")
@click.pass_context
def capture_convert(ctx, output, fmt):
    """Convert capture to a different format."""
    handle = _get_handle(ctx)
    result = handle.convert(output, fmt)
    _output(ctx, result)


@cli.group("actions")
def actions_group():
    """Draw call / action inspection."""
    pass
