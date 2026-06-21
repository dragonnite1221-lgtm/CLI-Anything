# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project  # noqa: E402,E501
from .cloudcompare_cli_p3 import cloud  # noqa: E402,E501
# fmt: on


@cloud.command("density")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option("--radius", "-r", type=float, default=0.1, help="Sphere radius.")
@click.option(
    "--type",
    "density_type",
    default="KNN",
    type=click.Choice(["KNN", "SURFACE", "VOLUME"], case_sensitive=False),
    help="Density type.",
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_density(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    radius: float,
    density_type: str,
    add_to_project: bool,
) -> None:
    """Compute point density scalar field."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = compute_density(cloud_entry["path"], output, radius, density_type)
        if result["returncode"] != 0:
            raise RuntimeError(f"Density failed:\n{result['stderr'][:500]}")
        session.record(
            "density",
            [cloud_entry["path"]],
            [output],
            {"radius": radius, "type": density_type},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_density")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "radius": radius,
                "type": density_type,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cloud.command("curvature")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option(
    "--type",
    "curv_type",
    default="MEAN",
    type=click.Choice(["MEAN", "GAUSS"], case_sensitive=False),
)
@click.option("--radius", "-r", type=float, default=0.1)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_curvature(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    curv_type: str,
    radius: float,
    add_to_project: bool,
) -> None:
    """Compute curvature scalar field (MEAN or GAUSS)."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = compute_curvature(cloud_entry["path"], output, curv_type, radius)
        if result["returncode"] != 0:
            raise RuntimeError(f"Curvature failed:\n{result['stderr'][:500]}")
        session.record(
            "curvature",
            [cloud_entry["path"]],
            [output],
            {"type": curv_type, "radius": radius},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_curv")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "type": curv_type,
                "radius": radius,
                "exists": result.get("exists", False),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
