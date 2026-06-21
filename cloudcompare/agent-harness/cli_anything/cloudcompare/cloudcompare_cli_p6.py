# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project  # noqa: E402,E501
from .cloudcompare_cli_p3 import cloud  # noqa: E402,E501
# fmt: on


@cloud.command("normals")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option("--level", type=int, default=10, help="Octree level (1-10).")
@click.option(
    "--orientation",
    default="PLUS_Z",
    type=click.Choice(
        ["PLUS_X", "PLUS_Y", "PLUS_Z", "MINUS_X", "MINUS_Y", "MINUS_Z"],
        case_sensitive=False,
    ),
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_normals(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    level: int,
    orientation: str,
    add_to_project: bool,
) -> None:
    """Compute normals via octree method."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = compute_normals(cloud_entry["path"], output, level, orientation)
        if result["returncode"] != 0:
            raise RuntimeError(f"Normals failed:\n{result['stderr'][:500]}")
        session.record(
            "normals",
            [cloud_entry["path"]],
            [output],
            {"level": level, "orientation": orientation},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_normals")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "level": level,
                "orientation": orientation,
                "exists": result.get("exists", False),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cloud.command("filter-sor")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option("--nb-points", type=int, default=6, help="K nearest neighbors.")
@click.option("--std-ratio", type=float, default=1.0, help="Std deviation multiplier.")
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_filter_sor(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    nb_points: int,
    std_ratio: float,
    add_to_project: bool,
) -> None:
    """Statistical Outlier Removal (SOR) filter — removes noise points."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = sor_filter(cloud_entry["path"], output, nb_points, std_ratio)
        if result["returncode"] != 0:
            raise RuntimeError(f"SOR filter failed:\n{result['stderr'][:500]}")
        session.record(
            "sor_filter",
            [cloud_entry["path"]],
            [output],
            {"nb_points": nb_points, "std_ratio": std_ratio},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_sor")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "nb_points": nb_points,
                "std_ratio": std_ratio,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
