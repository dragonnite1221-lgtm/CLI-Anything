# ruff: noqa: F403, F405, E501
from .audacity_cli_base import *  # noqa: F403

# fmt: off
from .audacity_cli_p1 import cli, handle_error, output  # noqa: E402,E501
# fmt: on


@cli.command("eval")
@click.option(
    "--out", "out_dir", type=str, default=None, help="Output directory for eval reports"
)
@click.option(
    "--baseline",
    "baseline_path",
    type=str,
    default=None,
    help="Path to baseline JSON for regression comparison",
)
@click.option(
    "--update-baseline", is_flag=True, help="Write baseline JSON from this run"
)
@click.option(
    "--fail-on-regression",
    is_flag=True,
    help="Exit with code 2 if regression is detected",
)
@handle_error
def eval_cmd(out_dir, baseline_path, update_baseline, fail_on_regression):
    """Run evaluation tasks and generate reports."""
    from cli_anything.audacity.eval.runner import run_eval

    result = run_eval(
        output_dir=out_dir,
        baseline_path=baseline_path,
        update_baseline=update_baseline,
    )
    report = result.get("report", {})
    summary = report.get("summary", {})
    comparison = result.get("comparison")
    regression = bool(comparison.get("regression")) if comparison else False

    output_data = {
        "summary": summary,
        "output_dir": result.get("paths", {}).get("output_dir"),
        "report_json": result.get("paths", {}).get("report_json"),
        "report_md": result.get("paths", {}).get("report_md"),
        "baseline_written": result.get("paths", {}).get("baseline_written"),
        "regression": regression,
    }

    msg = f"Eval completed: {summary.get('passed', 0)}/{summary.get('total', 0)} passed"
    if regression:
        msg += " (regression detected)"
    output(output_data, msg)

    if regression and fail_on_regression:
        sys.exit(2)


def main():
    cli()
