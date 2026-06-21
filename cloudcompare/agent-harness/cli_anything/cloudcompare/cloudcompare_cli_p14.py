# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403

# fmt: off
from .cloudcompare_cli_p1 import _error, _out, _require_project, cli  # noqa: E402,E501
from .cloudcompare_cli_p13 import transform  # noqa: E402,E501
# fmt: on


@transform.command("icp")
@click.option("--aligned", type=int, required=True, help="Index of cloud to align.")
@click.option("--reference", type=int, required=True, help="Index of reference cloud.")
@click.option("--output", "-o", required=True, help="Output aligned cloud path.")
@click.option("--max-iter", type=int, default=100, help="Maximum ICP iterations.")
@click.option("--min-error-diff", type=float, default=1e-6)
@click.option(
    "--overlap", type=float, default=100.0, help="Overlap percentage (0-100)."
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def transform_icp(
    ctx: click.Context,
    aligned: int,
    reference: int,
    output: str,
    max_iter: int,
    min_error_diff: float,
    overlap: float,
    add_to_project: bool,
) -> None:
    """Run ICP registration to align one cloud to another."""
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        aligned_entry = session.get_cloud(aligned)
        ref_entry = session.get_cloud(reference)
        result = run_icp(
            aligned_entry["path"],
            ref_entry["path"],
            output,
            max_iter,
            min_error_diff,
            overlap,
        )
        if result["returncode"] != 0:
            raise RuntimeError(f"ICP failed:\n{result['stderr'][:500]}")
        session.record(
            "icp",
            [aligned_entry["path"], ref_entry["path"]],
            [output],
            {
                "max_iter": max_iter,
                "overlap": overlap,
            },
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{aligned_entry['label']}_icp")
        session.save()
        _out(
            ctx,
            {
                "aligned": aligned_entry["path"],
                "reference": ref_entry["path"],
                "output": output,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@transform.command("apply")
@click.argument("cloud_index", type=int)
@click.option("--output", "-o", required=True, help="Output transformed cloud.")
@click.option(
    "--matrix", "-m", required=True, help="Path to 4×4 transformation matrix text file."
)
@click.option(
    "--inverse", is_flag=True, default=False, help="Apply the inverse of the matrix."
)
@click.option("--add-to-project", is_flag=True, default=False)
@click.pass_context
def transform_apply(
    ctx: click.Context,
    cloud_index: int,
    output: str,
    matrix: str,
    inverse: bool,
    add_to_project: bool,
) -> None:
    """Apply a 4×4 rigid-body transformation matrix to a cloud.

    The matrix file must contain 4 rows of 4 space-separated values.

    Example identity matrix file::

        1 0 0 0
        0 1 0 0
        0 0 1 0
        0 0 0 1
    """
    json_mode = ctx.obj.get("json", False) if ctx.obj else False
    try:
        session, path = _require_project(ctx)
        cloud_entry = session.get_cloud(cloud_index)
        result = apply_transform(cloud_entry["path"], output, matrix, inverse)
        if result["returncode"] != 0:
            raise RuntimeError(f"Apply transform failed:\n{result['stderr'][:500]}")
        session.record(
            "apply_transform",
            [cloud_entry["path"]],
            [output],
            {"matrix": matrix, "inverse": inverse},
        )
        if add_to_project and result.get("exists"):
            session.add_cloud(output, f"{cloud_entry['label']}_transformed")
        session.save()
        _out(
            ctx,
            {
                "input": cloud_entry["path"],
                "matrix": matrix,
                "inverse": inverse,
                "output": output,
                "exists": result.get("exists", False),
                "file_size": result.get("file_size", 0),
            },
        )
    except Exception as e:
        _error(str(e), json_mode)
        sys.exit(1)


@cli.group()
def mesh() -> None:
    """Mesh operations (add, convert, export)."""
