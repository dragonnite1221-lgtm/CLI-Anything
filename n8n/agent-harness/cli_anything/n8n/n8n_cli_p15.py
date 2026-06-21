# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import _auto_snapshot, _clean_for_api, _conn, _json_flag  # noqa: E402,E501
from .n8n_cli_p14 import workflow_versions_  # noqa: E402,E501
# fmt: on


@workflow_versions_.command("rollback")
@click.argument("workflow_id")
@click.option(
    "--version",
    "ver_num",
    type=int,
    default=None,
    help="Version number to rollback to (default: previous)",
)
@click.pass_context
def versions_rollback(
    ctx: click.Context, workflow_id: str, ver_num: int | None
) -> None:
    """Rollback a workflow to a previous version."""
    conn = _conn(ctx)

    if ver_num is None:
        vers = versions.list_versions(workflow_id, limit=1)
        if not vers:
            error(f"No versions found for workflow {workflow_id}")
            return
        ver_num = vers[0].get("version_number")
        if not ver_num:
            error("Version data is corrupted")
            return

    snapshot = versions.get_snapshot(workflow_id, ver_num)
    if not snapshot:
        error(f"Version {ver_num} not found for workflow {workflow_id}")
        return

    # Save current state before rollback
    _auto_snapshot(workflow_id, conn, "pre-rollback")

    # Apply the rollback — deactivate first, then update
    try:
        workflows.deactivate_workflow(workflow_id, **conn)
    except requests.exceptions.HTTPError:
        pass  # May already be inactive
    update_data = _clean_for_api(snapshot)
    update_data.pop("active", None)
    workflows.update_workflow(workflow_id, update_data, **conn)
    success(
        f"Rolled back workflow {workflow_id} to version {ver_num} (deactivated — use activate to enable)"
    )


@workflow_versions_.command("show")
@click.argument("workflow_id")
@click.argument("version_number", type=int)
@click.pass_context
def versions_show(ctx: click.Context, workflow_id: str, version_number: int) -> None:
    """Show a specific version's snapshot."""
    snapshot = versions.get_snapshot(workflow_id, version_number)
    if not snapshot:
        error(f"Version {version_number} not found")
        return
    output(snapshot, _json_flag(ctx))


@workflow_versions_.command("diff")
@click.argument("workflow_id")
@click.argument("version_a", type=int)
@click.argument("version_b", type=int)
@click.pass_context
def versions_diff(
    ctx: click.Context, workflow_id: str, version_a: int, version_b: int
) -> None:
    """Compare two versions of a workflow."""
    if version_a == version_b:
        warn(f"Both versions are the same ({version_a}). Nothing to diff.")
        return
    import difflib

    snap_a = versions.get_snapshot(workflow_id, version_a)
    snap_b = versions.get_snapshot(workflow_id, version_b)
    if not snap_a:
        error(f"Version {version_a} not found")
        return
    if not snap_b:
        error(f"Version {version_b} not found")
        return

    def _clean(d: dict) -> str:
        clean = {
            k: v
            for k, v in d.items()
            if k not in ("id", "createdAt", "updatedAt", "versionId", "shared")
        }
        return json.dumps(clean, indent=2, sort_keys=True, default=str)

    lines_a = _clean(snap_a).splitlines(keepends=True)
    lines_b = _clean(snap_b).splitlines(keepends=True)
    diff = difflib.unified_diff(
        lines_a, lines_b, fromfile=f"v{version_a}", tofile=f"v{version_b}", lineterm=""
    )

    any_diff = False
    for line in diff:
        any_diff = True
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

    if not any_diff:
        success("Versions are identical")


@workflow_versions_.command("prune")
@click.argument("workflow_id")
@click.option("--keep", default=10, type=int, help="Number of recent versions to keep")
def versions_prune(workflow_id: str, keep: int) -> None:
    """Delete old versions, keeping the N most recent."""
    deleted = versions.prune_versions(workflow_id, keep=keep)
    success(f"Pruned {deleted} old version(s), kept {keep} most recent")
