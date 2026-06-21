# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project  # noqa: E402,E501
from .cloudcompare_cli_p3 import cloud  # noqa: E402,E501
# fmt: on


@cloud.command("subsample")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option(
    "--method",
    "-m",
    default="SPATIAL",
    type=click.Choice(["RANDOM", "SPATIAL", "OCTREE"], case_sensitive=False),
    help="Subsampling method.",
)
@click.option(
    "--param",
    "-n",
    type=float,
    default=0.05,
    help="RANDOM: point count; SPATIAL: min distance; OCTREE: level.",
)
@click.option(
    "--add-to-project",
    is_flag=True,
    default=False,
    help="Add output cloud back to the project.",
)
@click.pass_context
def cloud_subsample(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    method: str,
    param: float,
    add_to_project: bool,
) -> None:
    """Subsample a cloud using RANDOM, SPATIAL, or OCTREE method."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = subsample(cloud_entry["path"], output, method.upper(), param)
        if result["returncode"] != 0:
            raise RuntimeError(f"Subsample failed:\n{result['stderr'][:500]}")
        session.record(
            "subsample",
            [cloud_entry["path"]],
            [output],
            {"method": method, "param": param},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_ss")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": result.get("output", output),
                "method": method,
                "param": param,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cloud.command("roughness")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option(
    "--radius",
    "-r",
    type=float,
    default=0.1,
    help="Sphere radius for roughness computation.",
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_roughness(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    radius: float,
    add_to_project: bool,
) -> None:
    """Compute roughness scalar field for a cloud."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = compute_roughness(cloud_entry["path"], output, radius)
        if result["returncode"] != 0:
            raise RuntimeError(f"Roughness failed:\n{result['stderr'][:500]}")
        session.record("roughness", [cloud_entry["path"]], [output], {"radius": radius})
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_rough")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "radius": radius,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
