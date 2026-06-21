# ruff: noqa: F403, F405, E501
from .renderdoc_cli_base import *  # noqa: F403

# fmt: off
from .renderdoc_cli_p1 import _get_handle, _output, cli  # noqa: E402,E501
from .renderdoc_cli_p4 import pipeline_group  # noqa: E402,E501
from .renderdoc_cli_p7 import _get_handle_b  # noqa: E402,E501
# fmt: on


@pipeline_group.command("diff")
@click.argument("event_a", type=int)
@click.argument("event_b", type=int)
@click.option(
    "--capture-b",
    "-b",
    type=click.Path(exists=False),
    default=None,
    help="Path to second .rdc capture (default: same as --capture).",
)
@click.option(
    "--compact/--no-compact",
    default=True,
    help="Omit identical sections (default: compact).",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Output JSON path. Default: auto-generated next to capture.",
)
@click.pass_context
def pipeline_diff_cmd(ctx, event_a, event_b, capture_b, compact, output):
    """Compare pipeline state at EVENT_A vs EVENT_B.

    By default both events come from the same capture (--capture).
    Use --capture-b / -b to specify a second capture file.

    Results are written to a JSON file; only the path is printed to stdout.

    \b
    Examples:
      # Two events in different captures
      cli-anything-renderdoc -c a.rdc pipeline diff 100 200 -b b.rdc
      # Two events in the same capture
      cli-anything-renderdoc -c frame.rdc pipeline diff 100 200
      # Custom output path
      cli-anything-renderdoc -c a.rdc pipeline diff 100 200 -b b.rdc -o result.json
    """
    handle_a = _get_handle(ctx)
    if capture_b:
        handle_b = _get_handle_b(ctx, capture_b)
    else:
        handle_b = handle_a

    from cli_anything.renderdoc.core.diff import diff_pipeline

    data = diff_pipeline(
        handle_a.controller,
        event_a,
        handle_b.controller,
        event_b,
    )

    if compact:

        def _prune_same(obj):
            """Recursively remove 'SAME' markers and empty containers."""
            if isinstance(obj, dict):
                pruned = {}
                for k, v in obj.items():
                    if v == "SAME":
                        continue
                    cleaned = _prune_same(v)
                    if cleaned is not None:
                        pruned[k] = cleaned
                return pruned if pruned else None
            if isinstance(obj, list):
                pruned = [_prune_same(item) for item in obj if item != "SAME"]
                pruned = [item for item in pruned if item is not None]
                return pruned if pruned else None
            return obj

        data = _prune_same(data) or {}

    # Determine output file path
    if output is None:
        capture_a_path = ctx.obj.get("capture_path", "capture")
        base_dir = os.path.dirname(os.path.abspath(capture_a_path))
        stem_a = os.path.splitext(os.path.basename(capture_a_path))[0]
        if capture_b:
            stem_b = os.path.splitext(os.path.basename(capture_b))[0]
            output = os.path.join(
                base_dir,
                "diff_%s_eid%d_vs_%s_eid%d.json" % (stem_a, event_a, stem_b, event_b),
            )
        else:
            output = os.path.join(
                base_dir,
                "diff_%s_eid%d_vs_eid%d.json" % (stem_a, event_a, event_b),
            )

    output = os.path.abspath(output)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    if ctx.obj.get("json_mode"):
        _output(ctx, {"path": output})
    else:
        click.echo(output)


@cli.group("preview")
def preview_group():
    """Preview bundle capture and inspection."""
    pass


@preview_group.command("recipes")
@click.pass_context
def preview_recipes(ctx):
    """List available preview recipes."""
    from cli_anything.renderdoc.core.preview import list_recipes

    _output(ctx, list_recipes())
