# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project  # noqa: E402,E501
from .cloudcompare_cli_p3 import cloud  # noqa: E402,E501
# fmt: on


@cloud.command("noise-filter")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output filtered cloud.")
@click.option(
    "--knn", type=int, default=6, help="Number of nearest neighbours (default 6)."
)
@click.option(
    "--noisiness", type=float, default=1.0, help="Noise threshold multiplier."
)
@click.option(
    "--radius", type=float, default=0.1, help="Search radius (when --use-radius)."
)
@click.option(
    "--use-radius", is_flag=True, default=False, help="Use radius mode instead of KNN."
)
@click.option(
    "--absolute", is_flag=True, default=False, help="Use absolute noise threshold."
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_noise_filter(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    knn: int,
    noisiness: float,
    radius: float,
    use_radius: bool,
    absolute: bool,
    add_to_project: bool,
) -> None:
    """Remove noisy points using the PCL noise filter (-NOISE KNN/RADIUS REL/ABS)."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = noise_filter(
            cloud_entry["path"],
            output,
            knn=knn,
            noisiness=noisiness,
            use_radius=use_radius,
            radius=radius,
            absolute=absolute,
        )
        if result["returncode"] != 0:
            raise RuntimeError(f"Noise filter failed:\n{result['stderr'][:500]}")
        session.record(
            "noise_filter",
            [cloud_entry["path"]],
            [output],
            {"knn": knn, "noisiness": noisiness, "use_radius": use_radius},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_denoised")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output": output,
                "knn": knn,
                "noisiness": noisiness,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cloud.command("invert-normals")
@click.argument("cloud_index", type=int)
@click.option(
    "--output", "-o", required=True, help="Output cloud with inverted normals."
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def cloud_invert_normals(
    ctx: click.Context, cloud_index: int, output: str, add_to_project: bool
) -> None:
    """Invert (flip) all normals in the cloud."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = invert_normals(cloud_entry["path"], output)
        if result["returncode"] != 0:
            raise RuntimeError(f"Invert normals failed:\n{result['stderr'][:500]}")
        session.record("invert_normals", [cloud_entry["path"]], [output], {})
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_inv")
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


@cloud.command("segment-cc")
@click.argument("cloud_index", type=int)
@click.option(
    "--output-dir", "-o", required=True, help="Directory to save component clouds."
)
@click.option("--octree-level", type=int, default=8, help="Octree level (1-10).")
@click.option(
    "--min-points", type=int, default=100, help="Minimum points per component."
)
@click.option(
    "--fmt", default="xyz", help="Output format extension (xyz, las, ply, etc.)."
)
@click.pass_context
def cloud_segment_cc(
    ctx: click.Context,
    cloud_index: int,
    output_dir: str,
    octree_level: int,
    min_points: int,
    fmt: str,
) -> None:
    """Segment cloud into connected components (clusters).

    Each component is saved as a separate file in OUTPUT_DIR.
    """
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = extract_connected_components(
            cloud_entry["path"], output_dir, octree_level, min_points, fmt
        )
        session.record(
            "segment_cc",
            [cloud_entry["path"]],
            result["components"],
            {"octree_level": octree_level, "min_points": min_points},
        )
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "output_dir": output_dir,
                "octree_level": octree_level,
                "min_points": min_points,
                "component_count": result["component_count"],
                "components": result["components"],
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
