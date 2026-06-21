# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _clean_for_api, _conn, _load_json_arg  # noqa: E402,E501
from .n8n_cli_p2 import workflow_  # noqa: E402,E501
# fmt: on


@workflow_.command("restore-all")
@click.argument("backup_dir", type=click.Path(exists=True))
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be imported without doing it",
)
@click.pass_context
def workflow_restore_all(ctx: click.Context, backup_dir: str, dry_run: bool) -> None:
    """Restore workflows from a backup folder."""
    conn = _conn(ctx)
    backup_path = Path(backup_dir)
    backup_resolved = backup_path.resolve()
    json_files = sorted(backup_path.glob("*.json"))
    # Filter manifest and symlinks pointing outside backup dir
    json_files = [
        f
        for f in json_files
        if f.name != "_manifest.json" and f.resolve().is_relative_to(backup_resolved)
    ]

    if not json_files:
        warn(f"No JSON files found in {backup_dir}/")
        return

    click.echo(
        f"  {'[DRY RUN] ' if dry_run else ''}Restoring {len(json_files)} workflow(s) from {backup_dir}/\n"
    )
    ok, fail = 0, 0
    for f in json_files:
        try:
            data = json.loads(f.read_text())
            if not isinstance(data, dict):
                raise ValueError("Not a valid workflow JSON object")
            name = data.get("name", f.stem)
            if dry_run:
                click.echo(f"    Would import: {name}")
                ok += 1
                continue
            for field in ("id", "createdAt", "updatedAt", "versionId", "shared"):
                data.pop(field, None)
            data["active"] = False  # Never auto-activate restored workflows
            result = workflows.create_workflow(data, **conn)
            click.secho(f"    {result.get('id', '?')}  {name}", fg="green")
            ok += 1
        except Exception as exc:
            click.secho(f"    {f.name}  FAILED — {exc}", fg="red")
            fail += 1

    click.echo()
    if dry_run:
        success(f"Would restore {ok} workflows ({fail} would fail)")
    else:
        success(f"Restored {ok} workflows ({fail} failed)")


@workflow_.command("diff")
@click.argument("source")
@click.argument("target")
@click.pass_context
def workflow_diff(ctx: click.Context, source: str, target: str) -> None:
    """Compare two workflows. Use workflow IDs or @file.json paths.

    Examples: diff ABC123 DEF456, diff ABC123 @local.json, diff @a.json @b.json
    """
    import difflib

    conn = _conn(ctx)

    def _load(ref: str) -> dict:
        if ref.startswith("@"):
            return _load_json_arg(ref)
        return workflows.get_workflow(ref, **conn)

    def _clean(data: dict) -> dict:
        return _clean_for_api(data)

    src = _clean(_load(source))
    tgt = _clean(_load(target))

    src_lines = json.dumps(src, indent=2, sort_keys=True, default=str).splitlines(
        keepends=True
    )
    tgt_lines = json.dumps(tgt, indent=2, sort_keys=True, default=str).splitlines(
        keepends=True
    )

    src_label = source if source.startswith("@") else f"workflow:{source}"
    tgt_label = target if target.startswith("@") else f"workflow:{target}"

    diff = list(
        difflib.unified_diff(
            src_lines, tgt_lines, fromfile=src_label, tofile=tgt_label, lineterm=""
        )
    )

    if not diff:
        success("Workflows are identical")
        return

    for line in diff:
        if line.startswith("+++") or line.startswith("---"):
            click.secho(line, fg="cyan", bold=True)
        elif line.startswith("+"):
            click.secho(line, fg="green")
        elif line.startswith("-"):
            click.secho(line, fg="red")
        elif line.startswith("@@"):
            click.secho(line, fg="cyan")
        else:
            click.echo(line)
