# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _clean_for_api, _conn, _json_flag, _safe_filename  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
# fmt: on


@workflow_.command("export")
@click.argument("workflow_id")
@click.option(
    "-o",
    "--output",
    "out_path",
    default=None,
    help="Output file (default: <name>.json)",
)
@click.pass_context
def workflow_export(ctx: click.Context, workflow_id: str, out_path: str | None) -> None:
    """Export a workflow to a JSON file."""
    data = workflows.get_workflow(workflow_id, **_conn(ctx))
    if not out_path:
        name = _safe_filename(data.get("name", workflow_id))
        out_path = f"{name}.json"
    # Remove server-specific fields for portability
    export_data = _clean_for_api(data)
    out = Path(out_path)
    if out.exists():
        warn(f"File {out_path} already exists — overwriting")
    out.write_text(json.dumps(export_data, indent=2, default=str))
    success(f"Exported to {out_path}")


@workflow_.command("import")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--name", default=None, help="Override workflow name")
@click.pass_context
def workflow_import(ctx: click.Context, file_path: str, name: str | None) -> None:
    """Import a workflow from a JSON file."""
    with open(file_path) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        error("Invalid workflow format: must be a JSON object, not array or string")
        return
    # Remove fields that would conflict on import
    for field in ("id", "createdAt", "updatedAt", "versionId", "shared"):
        data.pop(field, None)
    data["active"] = False  # Never auto-activate imported workflows
    if name:
        data["name"] = name
    result = workflows.create_workflow(data, **_conn(ctx))
    success(f"Imported as workflow {result.get('id', '?')} — {result.get('name', '?')}")
    output(result, _json_flag(ctx))


@workflow_.command("backup-all")
@click.option(
    "-d",
    "--dir",
    "out_dir",
    default="n8n-backup",
    help="Output directory (default: n8n-backup)",
)
@click.option(
    "--active-only", is_flag=True, default=False, help="Only backup active workflows"
)
@click.pass_context
def workflow_backup_all(ctx: click.Context, out_dir: str, active_only: bool) -> None:
    """Backup ALL workflows to a folder (one JSON per workflow)."""
    conn = _conn(ctx)
    # Paginate to get ALL workflows, not just first page
    wf_list: list[dict] = []
    cursor = None
    seen_cursors: set[str] = set()
    for _ in range(100):  # Max 100 pages (10,000 workflows)
        data = workflows.list_workflows(
            **conn, limit=100, cursor=cursor, active=True if active_only else None
        )
        page = data.get("data", []) if isinstance(data, dict) else data
        wf_list.extend(page)
        cursor = data.get("nextCursor") if isinstance(data, dict) else None
        if not cursor or not page or cursor in seen_cursors:
            break
        seen_cursors.add(cursor)

    if not wf_list:
        warn("No workflows found")
        return

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    click.echo(f"  Backing up {len(wf_list)} workflow(s) to {out_dir}/\n")
    ok, fail = 0, 0
    for w in wf_list:
        wf_id = w.get("id", "unknown")
        try:
            full = workflows.get_workflow(wf_id, **conn)
            export_data = _clean_for_api(full)
            name_safe = _safe_filename(full.get("name", wf_id))
            filename = f"{wf_id}_{name_safe}.json"
            (out_path / filename).write_text(
                json.dumps(export_data, indent=2, default=str)
            )
            click.secho(f"    {wf_id}  {full.get('name', '?')}", fg="green")
            ok += 1
        except Exception as exc:
            click.secho(f"    {wf_id}  FAILED — {exc}", fg="red")
            fail += 1

    # Write manifest
    manifest = {
        "backup_date": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "count": ok,
        "failed": fail,
        "workflows": [w.get("id") for w in wf_list],
    }
    (out_path / "_manifest.json").write_text(json.dumps(manifest, indent=2))

    click.echo()
    success(f"Backed up {ok} workflows to {out_dir}/ ({fail} failed)")
