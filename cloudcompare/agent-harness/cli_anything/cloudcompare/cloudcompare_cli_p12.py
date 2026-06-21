# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project, cli  # noqa: E402,E501
from .cloudcompare_cli_p3 import cloud  # noqa: E402,E501
# fmt: on


@cloud.command("mesh-delaunay")
@click.argument("cloud_index", type=int)
@click.option(
    "--output", "-o", required=True, help="Output mesh file (.obj, .ply, .stl)."
)
@click.option(
    "--best-fit",
    is_flag=True,
    default=False,
    help="Use best-fit plane instead of axis-aligned XY.",
)
@click.option(
    "--max-edge-length",
    type=float,
    default=0.0,
    help="Remove triangles with edges longer than this (0=no limit).",
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_mesh_delaunay(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    best_fit: bool,
    max_edge_length: float,
    add_to_project: bool,
) -> None:
    """Build a 2.5-D Delaunay triangulation mesh from a cloud."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = delaunay_mesh(
            cloud_entry["path"],
            output,
            axis_aligned=not best_fit,
            max_edge_length=max_edge_length,
        )
        if result["returncode"] != 0:
            raise RuntimeError(f"Delaunay failed:\n{result['stderr'][:500]}")
        session.record(
            "delaunay_mesh",
            [cloud_entry["path"]],
            [output],
            {"axis_aligned": not best_fit, "max_edge_length": max_edge_length},
        )
        if add_to_project and result.get("exists"):
            session.add_mesh(output, f"{cloud_entry['label']}_mesh")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cloud.command("merge")
@click.option("--output", "-o", required=True, help="Output merged cloud file.")
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_merge(ctx: click.Context, output: str, add_to_project: bool) -> None:
    """Merge all clouds in the project into one."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        if session.cloud_count < 2:
            raise click.UsageError("Need at least 2 clouds to merge.")
        inputs = [session.get_cloud(i)["path"] for i in range(session.cloud_count)]
        result = merge_clouds(inputs, output)
        if result["returncode"] != 0:
            raise RuntimeError(f"Merge failed:\n{result['stderr'][:500]}")
        session.record("merge_clouds", inputs, [output], {})
        if add_to_project and result.get("exists"):
            session.add_cloud(output, "merged")
        session.save()
        _out(
            ctx,
            {
                "inputs": inputs,
                "output": output,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cloud.command("convert")
@click.argument("input_file")
@click.argument("output_file")
@click.pass_context
def cloud_convert(ctx: click.Context, input_file: str, output_file: str) -> None:
    """Convert a cloud from one format to another (format from extension)."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        result = convert_format(input_file, output_file)
        if result["returncode"] != 0:
            raise RuntimeError(f"Convert failed:\n{result['stderr'][:500]}")
        _out(
            ctx,
            {
                "input": input_file,
                "output": output_file,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cli.group()
def distance() -> None:
    """Distance computation between clouds and meshes."""
