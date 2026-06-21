# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project  # noqa: E402,E501
from .cloudcompare_cli_p3 import cloud  # noqa: E402,E501
# fmt: on


@cloud.command("sf-from-coord")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option(
    "--dim",
    "dimension",
    default="Z",
    type=click.Choice(["X", "Y", "Z"], case_sensitive=False),
    help="Coordinate axis to convert to scalar field. Default: Z (height).",
)
@click.option(
    "--sf-index", type=int, default=0, help="Index to set as active SF after creation."
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_sf_from_coord(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    dimension: str,
    sf_index: int,
    add_to_project: bool,
) -> None:
    """Convert a coordinate axis (X/Y/Z) to a scalar field.

    Most commonly used to create a height (Z) scalar field for
    elevation-based analysis and visualization.

    Example:
        cloud sf-from-coord 0 -o with_z_sf.las --dim Z
    """
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = coord_to_sf(cloud_entry["path"], output, dimension, sf_index)
        if result["returncode"] != 0:
            raise RuntimeError(f"coord_to_sf failed:\n{result['stderr'][:500]}")
        session.record(
            "coord_to_sf",
            [cloud_entry["path"]],
            [output],
            {"dimension": dimension, "sf_index": sf_index},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_sf{dimension}")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "dimension": dimension,
                "sf_index": sf_index,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cloud.command("filter-sf")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option(
    "--min",
    "min_val",
    type=float,
    required=True,
    help="Minimum scalar field value to keep.",
)
@click.option(
    "--max",
    "max_val",
    type=float,
    required=True,
    help="Maximum scalar field value to keep.",
)
@click.option(
    "--sf-index",
    type=int,
    default=None,
    help="Set this SF index as active before filtering.",
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_filter_sf(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    min_val: float,
    max_val: float,
    sf_index: Optional[int],
    add_to_project: bool,
) -> None:
    """Filter a cloud by scalar field value range.

    Keeps only points whose active scalar field value is in [min, max].
    Typically used after sf-from-coord to filter by height range.

    Example — keep points between z=10m and z=20m:
        cloud sf-from-coord 0 -o with_z.las --dim Z --add-to-project
        cloud filter-sf 1 -o slice.las --min 10.0 --max 20.0
    """
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = filter_sf_by_value(
            cloud_entry["path"], output, min_val, max_val, sf_index
        )
        if result["returncode"] != 0:
            raise RuntimeError(f"filter_sf failed:\n{result['stderr'][:500]}")
        session.record(
            "filter_sf",
            [cloud_entry["path"]],
            [output],
            {"min": min_val, "max": max_val, "sf_index": sf_index},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_sffilter")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "min": min_val,
                "max": max_val,
                "sf_index": sf_index,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
