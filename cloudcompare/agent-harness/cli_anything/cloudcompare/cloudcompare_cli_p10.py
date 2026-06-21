# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project  # noqa: E402,E501
from .cloudcompare_cli_p3 import cloud  # noqa: E402,E501
# fmt: on


@cloud.command("sf-filter-z")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option(
    "--min",
    "min_val",
    type=float,
    default=None,
    help="Minimum Z height to keep (omit for no lower bound).",
)
@click.option(
    "--max",
    "max_val",
    type=float,
    default=None,
    help="Maximum Z height to keep (omit for no upper bound).",
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_sf_filter_z(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    min_val: Optional[float],
    max_val: Optional[float],
    add_to_project: bool,
) -> None:
    """Convert Z to scalar field and filter by height range in one step.

    Convenience command: combines sf-from-coord (Z) + filter-sf in a single
    CloudCompare call. Ideal for extracting a horizontal slice from a scan.

    Example — extract a 1-metre slice at z=5m to z=6m:
        cloud sf-filter-z 0 -o slice.las --min 5.0 --max 6.0
    """
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        if min_val is None and max_val is None:
            raise click.UsageError("Provide at least one of --min or --max.")
        result = coord_to_sf_and_filter(
            cloud_entry["path"],
            output,
            dimension="Z",
            min_val=min_val,
            max_val=max_val,
        )
        if result["returncode"] != 0:
            raise RuntimeError(f"sf-filter-z failed:\n{result['stderr'][:500]}")
        session.record(
            "sf_filter_z",
            [cloud_entry["path"]],
            [output],
            {"min": min_val, "max": max_val},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_zslice")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "z_min": min_val,
                "z_max": max_val,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cloud.command("sf-to-rgb")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud with RGB colours.")
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_sf_to_rgb(
    ctx: click.Context, cloud_index: int, output: str, add_to_project: bool
) -> None:
    """Convert the active scalar field to RGB colours."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = sf_to_rgb(cloud_entry["path"], output)
        if result["returncode"] != 0:
            raise RuntimeError(f"SF→RGB failed:\n{result['stderr'][:500]}")
        session.record("sf_to_rgb", [cloud_entry["path"]], [output], {})
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_rgb")
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


@cloud.command("rgb-to-sf")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud with SF from RGB.")
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_rgb_to_sf(
    ctx: click.Context, cloud_index: int, output: str, add_to_project: bool
) -> None:
    """Convert RGB colours to a scalar field (luminance)."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = rgb_to_sf(cloud_entry["path"], output)
        if result["returncode"] != 0:
            raise RuntimeError(f"RGB→SF failed:\n{result['stderr'][:500]}")
        session.record("rgb_to_sf", [cloud_entry["path"]], [output], {})
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_sf")
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
