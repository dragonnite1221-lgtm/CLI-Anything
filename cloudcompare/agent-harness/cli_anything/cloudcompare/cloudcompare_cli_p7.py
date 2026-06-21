# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project  # noqa: E402,E501
from .cloudcompare_cli_p3 import cloud  # noqa: E402,E501
# fmt: on


@cloud.command("crop")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option("--xmin", type=float, required=True)
@click.option("--ymin", type=float, required=True)
@click.option("--zmin", type=float, required=True)
@click.option("--xmax", type=float, required=True)
@click.option("--ymax", type=float, required=True)
@click.option("--zmax", type=float, required=True)
@click.option(
    "--outside", is_flag=True, default=False, help="Keep points outside the box."
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_crop(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    xmin: float,
    ymin: float,
    zmin: float,
    xmax: float,
    ymax: float,
    zmax: float,
    outside: bool,
    add_to_project: bool,
) -> None:
    """Crop a cloud to an axis-aligned bounding box."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = crop_cloud(
            cloud_entry["path"], output, xmin, ymin, zmin, xmax, ymax, zmax, outside
        )
        if result["returncode"] != 0:
            raise RuntimeError(f"Crop failed:\n{result['stderr'][:500]}")
        session.record(
            "crop",
            [cloud_entry["path"]],
            [output],
            {
                "bbox": [xmin, ymin, zmin, xmax, ymax, zmax],
                "outside": outside,
            },
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_crop")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "bbox": [xmin, ymin, zmin, xmax, ymax, zmax],
                "outside": outside,
                "exists": result.get("exists", False),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
