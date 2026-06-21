# ruff: noqa: F403, F405, E501
from .sbox_cli_base import *  # noqa: F403

# fmt: off
from .sbox_cli_p1 import _format_status_block, _output, _output_error, _resolve_project_path  # noqa: E402,E501
from .sbox_cli_p2 import cli  # noqa: E402,E501
from .sbox_cli_p22 import test_group  # noqa: E402,E501
# fmt: on


@test_group.command("run")
@click.option(
    "--strategies", default=None, help="Comma-separated strategies (default: all)"
)
@click.option("--sizes", default=None, help="Comma-separated sizes (default: all)")
@click.option("--seeds", default=None, help="Comma-separated seed values")
@click.option(
    "--seed-count", type=int, default=1, help="Number of random seeds per combo"
)
@click.option(
    "--timeout", type=float, default=60.0, help="Timeout per combo in seconds"
)
@click.pass_context
def test_run(ctx, strategies, sizes, seeds, seed_count, timeout):
    """Run map generation tests across strategy/size/seed combos."""
    try:
        sbox_install = sbox_backend.find_sbox_installation()
        sbproj = _resolve_project_path(ctx)
        if not sbproj:
            raise click.ClickException("No .sbproj found.")

        info = project_mod.get_project_info(sbproj)
        ident = info.get("ident", "hold_the_line")
        data_path = test_mod.resolve_data_path(sbox_install, ident)

        project_dir = os.path.dirname(sbproj)
        output_dir = os.path.join(project_dir, "test-results")
        os.makedirs(os.path.join(output_dir, "screenshots"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "reports"), exist_ok=True)

        parsed_strategies = strategies.split(",") if strategies else None
        parsed_sizes = sizes.split(",") if sizes else None
        parsed_seeds = [int(s) for s in seeds.split(",")] if seeds else None

        results = test_mod.run_test_pipeline(
            sbproj_path=sbproj,
            data_path=data_path,
            output_dir=output_dir,
            strategies=parsed_strategies,
            sizes=parsed_sizes,
            seeds=parsed_seeds,
            seed_count=seed_count,
            timeout=timeout,
        )

        succeeded = sum(1 for r in results if r["success"])
        failed = sum(1 for r in results if not r["success"])

        summary = {
            "total": len(results),
            "succeeded": succeeded,
            "failed": failed,
            "screenshots": [r["png_path"] for r in results if r.get("png_path")],
            "failures": [
                {"combo": r["combo"], "error": r["error"]}
                for r in results
                if not r["success"]
            ],
        }

        _output(ctx, summary, lambda d: _format_status_block(d, "Test Run Complete"))
        # Partial-failure: scripts/agents need a non-zero exit when any combo
        # fails, otherwise the summary is misleading (printed N failures, exit 0).
        if failed > 0 and not ctx.obj.get("repl"):
            sys.exit(1)
    except Exception as exc:
        _output_error(ctx, str(exc))


def main():
    """Main entry point for the CLI."""
    cli()
