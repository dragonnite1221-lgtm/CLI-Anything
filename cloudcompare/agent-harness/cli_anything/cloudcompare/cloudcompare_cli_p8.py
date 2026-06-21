# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project  # noqa: E402,E501
from .cloudcompare_cli_p3 import cloud  # noqa: E402,E501
# fmt: on


@cloud.command("filter-csf")
@click.argument("cloud_index", type=int)
@click.option("--ground", "-g", required=True, help="Output path for ground points.")
@click.option(
    "--offground",
    "-u",
    default=None,
    help="Output path for off-ground points (optional).",
)
@click.option(
    "--scene",
    default="RELIEF",
    type=click.Choice(["SLOPE", "RELIEF", "FLAT"], case_sensitive=False),
    help="Scene type: SLOPE (steep), RELIEF (general, default), FLAT (urban).",
)
@click.option(
    "--cloth-resolution",
    type=float,
    default=2.0,
    help="Cloth grid resolution in metres. Smaller = finer detail. Default: 2.0.",
)
@click.option(
    "--class-threshold",
    type=float,
    default=0.5,
    help="Max distance (m) from cloth to classify as ground. Default: 0.5.",
)
@click.option(
    "--max-iteration",
    type=int,
    default=500,
    help="Maximum cloth simulation iterations. Default: 500.",
)
@click.option(
    "--proc-slope",
    is_flag=True,
    default=False,
    help="Enable slope post-processing to smooth terrain artifacts.",
)
@click.option(
    "--add-to-project",
    is_flag=True,
    default=False,
    help="Add ground (and off-ground if exported) back to the project.",
)
@click.pass_context
def cloud_filter_csf(
    ctx: click.Context,
    cloud_index: int,
    ground: str,
    offground: Optional[str],
    scene: str,
    cloth_resolution: float,
    class_threshold: float,
    max_iteration: int,
    proc_slope: bool,
    add_to_project: bool,
) -> None:
    """Ground filtering using the Cloth Simulation Filter (CSF) algorithm.

    Separates a LiDAR scan into ground points and off-ground points
    (buildings, vegetation, etc.) by simulating a cloth draped over the
    inverted point cloud.

    Scene presets:
      SLOPE  — steep terrain (rigidness=1, looser cloth)
      RELIEF — mixed terrain (rigidness=2, default)
      FLAT   — flat/urban terrain (rigidness=3, stiffer cloth)

    Examples:

      # Extract ground only (outdoor LiDAR, mixed terrain)
      cloud filter-csf 0 --ground ground.las --scene RELIEF

      # Split ground + off-ground (urban scene)
      cloud filter-csf 0 --ground ground.las --offground buildings.las \\
          --scene FLAT --cloth-resolution 0.5 --class-threshold 0.3

      # Steep forested slope with slope post-processing
      cloud filter-csf 0 --ground ground.las --scene SLOPE --proc-slope
    """
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = csf_filter(
            cloud_entry["path"],
            ground_output=ground,
            offground_output=offground,
            scene=scene.upper(),
            cloth_resolution=cloth_resolution,
            class_threshold=class_threshold,
            max_iteration=max_iteration,
            proc_slope=proc_slope,
        )
        if result["returncode"] != 0:
            raise RuntimeError(f"CSF filter failed:\n{result['stderr'][:500]}")
        if not result.get("ground_exists"):
            raise RuntimeError(
                "CSF ran but ground output not found. "
                "Check that the CSF plugin is installed in CloudCompare."
            )
        params = {
            "scene": scene,
            "cloth_resolution": cloth_resolution,
            "class_threshold": class_threshold,
            "max_iteration": max_iteration,
            "proc_slope": proc_slope,
        }
        outputs = [ground]
        if offground:
            outputs.append(offground)
        session.record("csf_filter", [cloud_entry["path"]], outputs, params)
        if add_to_project:
            if result.get("ground_exists"):
                session.add_cloud(ground, f"{cloud_entry['label']}_ground")
            if offground and result.get("offground_exists"):
                session.add_cloud(offground, f"{cloud_entry['label']}_offground")
        session.save()
        out = {
            "input": cloud_entry["path"],
            "scene": scene,
            "cloth_resolution": cloth_resolution,
            "class_threshold": class_threshold,
            "ground": ground,
            "ground_exists": result.get("ground_exists", False),
            "ground_size": result.get("ground_size", 0),
        }
        if offground:
            out["offground"] = offground
            out["offground_exists"] = result.get("offground_exists", False)
            out["offground_size"] = result.get("offground_size", 0)
        _out(ctx, out)
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)
