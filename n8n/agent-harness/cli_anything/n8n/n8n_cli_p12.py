# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _auto_snapshot, _clean_for_api, _conn, _json_flag, _load_json_arg  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
# fmt: on


@workflow_.command("autofix")
@click.argument("source")
@click.option(
    "--apply", is_flag=True, default=False, help="Apply fixes (default: preview only)"
)
@click.option(
    "--save",
    "save_path",
    default=None,
    help="Save fixed workflow to file instead of updating n8n",
)
@click.pass_context
def workflow_autofix(
    ctx: click.Context, source: str, apply: bool, save_path: str | None
) -> None:
    """Auto-fix common workflow issues. Preview by default, --apply to save.

    Fixes: expression format, webhook paths, broken connections, duplicate names,
    connection types, unused error outputs.
    """
    from cli_anything.n8n.core.fixers import autofix

    conn = _conn(ctx)
    if source.startswith("@"):
        wf_data = _load_json_arg(source)
        wf_id = None
    else:
        wf_data = workflows.get_workflow(source, **conn)
        wf_id = source

    import copy

    wf_copy = copy.deepcopy(wf_data)
    fixed_wf, fixes = autofix(wf_copy, apply=True)

    if _json_flag(ctx):
        output(
            {
                "fixes": [
                    {
                        "type": f.fix_type,
                        "description": f.description,
                        "confidence": f.confidence,
                        "node": f.node_name,
                    }
                    for f in fixes
                ],
                "total": len(fixes),
                "applied": apply or bool(save_path),
            },
            True,
        )
        return

    if not fixes:
        success("No issues found!")
        return

    click.secho(f"\n  Found {len(fixes)} issue(s):\n", fg="yellow", bold=True)
    for f in fixes:
        color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "bright_black"}.get(
            f.confidence, "white"
        )
        node_str = f" [{f.node_name}]" if f.node_name else ""
        click.echo(
            f"    {click.style(f.confidence, fg=color):>8s}  {f.fix_type:30s}{node_str}"
        )
        click.secho(f"             {f.description}", fg="bright_black")

    if save_path:
        Path(save_path).write_text(json.dumps(fixed_wf, indent=2, default=str))
        success(f"Fixed workflow saved to {save_path}")
    elif apply and wf_id:
        _auto_snapshot(wf_id, conn, "autofix")
        update_data = _clean_for_api(fixed_wf)
        workflows.update_workflow(wf_id, update_data, **conn)
        success(f"Applied {len(fixes)} fix(es) to workflow {wf_id}")
    elif apply and not wf_id:
        error("Cannot apply fixes to a file source. Use --save instead.")
    else:
        warn("Preview only. Use --apply to fix in n8n, or --save to save to file.")
    click.echo()
