# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project, cli  # noqa: E402,E501
from .cloudcompare_cli_p14 import mesh  # noqa: E402,E501
# fmt: on


@mesh.command("add")
@click.argument("mesh_file")
@click.option("--label", "-l", default=None)
@click.pass_context
def mesh_add(ctx: click.Context, mesh_file: str, label: Optional[str]) -> None:
    """Add a mesh file to the project."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        entry = session.add_mesh(mesh_file, label)
        session.save()
        _out(ctx, {"added": entry, "mesh_count": session.mesh_count})
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@mesh.command("list")
@click.pass_context
def mesh_list(ctx: click.Context) -> None:
    """List all meshes in the project."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        meshes = session.info()["meshes"]
        _out(ctx, {"meshes": meshes, "count": len(meshes)})
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@mesh.command("sample")
@click.argument("mesh_index", type=int)
@click.option("--output", "-o", required=True, help="Output sampled point cloud.")
@click.option(
    "--count",
    "-n",
    type=int,
    default=10000,
    help="Number of points to sample from the mesh surface.",
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def mesh_sample(
    ctx: click.Context,
    mesh_index: int,
    output: str,
    count: int,
    add_to_project: bool,
) -> None:
    """Sample a point cloud from a mesh surface."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        mesh_entry = session.get_mesh(mesh_index)
        result = sample_mesh(mesh_entry["path"], output, count)
        if result["returncode"] != 0:
            raise RuntimeError(f"Sample mesh failed:\n{result['stderr'][:500]}")
        session.record("sample_mesh", [mesh_entry["path"]], [output], {"count": count})
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{mesh_entry['label']}_sampled")
        session.save()
        _out(
            ctx,
            {
                "mesh": mesh_entry["path"],
                "output": output,
                "count": count,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cli.group()
def export() -> None:
    """Export clouds and meshes to various formats."""


@export.command("cloud")
@click.argument("cloud_index", type=int)
@click.argument("output_path")
@click.option(
    "--preset", "-f", default=None, help=f"Format preset: {', '.join(CLOUD_PRESETS)}."
)
@click.option("--overwrite", is_flag=True, default=False)
@click.pass_context
def export_cloud_cmd(
    ctx: click.Context,
    cloud_index: int,
    output_path: str,
    preset: Optional[str],
    overwrite: bool,
) -> None:
    """Export a cloud to a target format using CloudCompare."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = export_cloud(
            cloud_entry["path"], output_path, preset=preset, overwrite=overwrite
        )
        session.record(
            "export_cloud",
            [cloud_entry["path"]],
            [result["output"]],
            {
                "format": result["format"],
            },
        )
        session.save()
        _out(ctx, result)
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
