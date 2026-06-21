# ruff: noqa: F403, F405, E501
from .macrocli_cli_base import *  # noqa: F403

# fmt: off
from .macrocli_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .macrocli_cli_p2 import macro  # noqa: E402,E501
# fmt: on


@macro.command("assist")
@click.argument("name")
@click.option(
    "--goal",
    "-g",
    required=True,
    help="Natural language goal (what the macro should do).",
)
@click.option(
    "--screenshot",
    default="current",
    help="'current' to take a screenshot now, or path to an image file.",
)
@click.option(
    "--output", "-o", default=None, help="Output YAML file path (default: <name>.yaml)."
)
@click.option(
    "--api-key",
    default=None,
    envvar="MACROCLI_API_KEY",
    help="API key (or set MACROCLI_API_KEY env var).",
)
@click.option(
    "--model", default=None, help="Model name (or set MACROCLI_MODEL env var)."
)
@handle_error
def macro_assist(name, goal, screenshot, output, api_key, model):
    """Generate a macro YAML from a screenshot using a vision model (optional).

    \b
    Takes a screenshot, sends it to the configured model with your goal, and
    generates a macro YAML. Steps that require visual templates will include
    instructions for which template images to capture.

    Requires: pip install openai mss Pillow

    \b
    Example:
      macro assist export_png \\
          --goal "Export the current diagram as PNG to /tmp/out.png" \\
          --api-key $MACROCLI_API_KEY
    """
    try:
        from cli_anything.macrocli.core.llm_assist import generate_macro
    except ImportError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if not _json_output:
        click.echo(
            f"Sending screenshot to model ({model or os.environ.get('MACROCLI_MODEL', 'unset')})..."
        )

    result = generate_macro(
        goal=goal,
        macro_name=name,
        screenshot_source=screenshot,
        api_key=api_key,
        model=model,
        output_path=output,
    )

    if _json_output:
        output(result)
    else:
        click.echo(f"✓ Generated {result['steps_count']} steps → {result['yaml_path']}")
        if result["warnings"]:
            for w in result["warnings"]:
                click.echo(f"  ⚠ {w}")
        if result.get("templates_to_capture"):
            click.echo("\n  Templates to capture (use 'macro capture-template'):")
            for t in result["templates_to_capture"]:
                click.echo(f"    {t['template_path']}: {t['description']}")


@macro.command("capture-template")
@click.argument("output_path")
@click.option("--x", type=int, required=True, help="Left edge of region.")
@click.option("--y", type=int, required=True, help="Top edge of region.")
@click.option("--width", type=int, required=True, help="Region width in pixels.")
@click.option("--height", type=int, required=True, help="Region height in pixels.")
@handle_error
def macro_capture_template(output_path, x, y, width, height):
    """Capture a screen region and save it as a template image.

    \b
    Use this to create the template PNG files that visual_anchor macros need.

    \b
    Example:
      macro capture-template templates/export_button.png \\
          --x 245 --y 110 --width 80 --height 30

    Requires: pip install mss Pillow
    """
    try:
        from cli_anything.macrocli.backends.visual_anchor import VisualAnchorBackend
        from cli_anything.macrocli.backends.base import BackendContext
        from cli_anything.macrocli.core.macro_model import MacroStep
    except ImportError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    va = VisualAnchorBackend()
    step = MacroStep(
        id="capture",
        backend="visual_anchor",
        action="capture_region",
        params={
            "output": output_path,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        },
    )
    ctx = BackendContext(params={})
    result = va.execute(step, {}, ctx)

    if _json_output:
        output(result.to_dict())
    else:
        if result.success:
            click.echo(f"✓ Template saved: {result.output.get('saved')}")
            click.echo(f"  Size: {result.output.get('file_size', 0)} bytes")
        else:
            click.echo(f"✗ {result.error}", err=True)
            if not _repl_mode:
                sys.exit(1)


@cli.group()
def session():
    """Session management and run history."""
