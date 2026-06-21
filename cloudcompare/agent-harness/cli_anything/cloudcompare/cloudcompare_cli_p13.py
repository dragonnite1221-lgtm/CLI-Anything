# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project, cli  # noqa: E402,E501
from .cloudcompare_cli_p12 import distance  # noqa: E402,E501
# fmt: on


@distance.command("c2c")
@click.option(
    "--compare", required=True, help="Index of cloud to compare (gets distance SF)."
)
@click.option("--reference", required=True, help="Index of reference cloud.")
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option(
    "--split-xyz", is_flag=True, default=False, help="Split into X/Y/Z components."
)
@click.option(
    "--octree-level", type=int, default=10, help="Octree level for computation."
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def distance_c2c(
    ctx: click.Context,
    compare: str,
    reference: str,
    output: str,
    split_xyz: bool,
    octree_level: int,
    add_to_project: bool,
) -> None:
    """Compute cloud-to-cloud distances. Adds distance SF to compared cloud."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        compare_entry = session.get_cloud(int(compare))
        ref_entry = session.get_cloud(int(reference))
        result = compute_c2c_distances(
            compare_entry["path"], ref_entry["path"], output, split_xyz, octree_level
        )
        if result["returncode"] != 0:
            raise RuntimeError(f"C2C distance failed:\n{result['stderr'][:500]}")
        session.record(
            "c2c_dist",
            [compare_entry["path"], ref_entry["path"]],
            [output],
            {
                "split_xyz": split_xyz,
                "octree_level": octree_level,
            },
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{compare_entry['label']}_c2c")
        session.save()
        _out(
            ctx,
            {
                "compare": compare_entry["path"],
                "reference": ref_entry["path"],
                "output": output,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@distance.command("c2m")
@click.option("--cloud", "cloud_idx", type=int, required=True, help="Cloud index.")
@click.option("--mesh", "mesh_idx", type=int, required=True, help="Mesh index.")
@click.option("--output", "-o", required=True, help="Output cloud file path.")
@click.option("--flip-normals", is_flag=True, default=False)
@click.option("--unsigned", is_flag=True, default=False)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def distance_c2m(
    ctx: click.Context,
    cloud_idx: int,
    mesh_idx: int,
    output: str,
    flip_normals: bool,
    unsigned: bool,
    add_to_project: bool,
) -> None:
    """Compute cloud-to-mesh distances. Adds distance SF to the cloud."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_idx)
        mesh_entry = session.get_mesh(mesh_idx)
        result = compute_c2m_distances(
            cloud_entry["path"], mesh_entry["path"], output, flip_normals, unsigned
        )
        if result["returncode"] != 0:
            raise RuntimeError(f"C2M distance failed:\n{result['stderr'][:500]}")
        session.record(
            "c2m_dist",
            [cloud_entry["path"], mesh_entry["path"]],
            [output],
            {
                "flip_normals": flip_normals,
                "unsigned": unsigned,
            },
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_c2m")
        session.save()
        _out(
            ctx,
            {
                "cloud": cloud_entry["path"],
                "mesh": mesh_entry["path"],
                "output": output,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cli.group()
def transform() -> None:
    """Transformations and registration (ICP, match-centers)."""
