# ruff: noqa: F403, F405, E501
from .runner_base import *  # noqa: F403

# fmt: off
from .runner_p1 import EvalContext, _build_summary, _iso_now, _report_to_markdown, _run_task, default_output_dir, discover_tasks  # noqa: E402,E501
# fmt: on


def _report_to_baseline(report: Dict[str, Any]) -> Dict[str, Any]:
    task_map = {}
    for task in report.get("tasks", []):
        task_map[task.get("id", "")] = {
            "status": task.get("status"),
            "metrics": task.get("metrics", {}),
        }
    return {
        "summary": report.get("summary", {}),
        "tasks": task_map,
    }


def load_baseline(path: str) -> Dict[str, Any]:
    baseline_path = Path(path)
    if not baseline_path.exists():
        raise FileNotFoundError(f"Baseline file not found: {path}")
    with baseline_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def compare_baseline(
    baseline: Dict[str, Any], report: Dict[str, Any]
) -> Dict[str, Any]:
    baseline_tasks = baseline.get("tasks", {}) or {}
    report_tasks = {t.get("id", ""): t for t in report.get("tasks", [])}

    regressions: List[Dict[str, Any]] = []

    for task_id, baseline_task in baseline_tasks.items():
        if baseline_task.get("status") != "pass":
            continue
        current = report_tasks.get(task_id)
        if current and current.get("status") == "fail":
            regressions.append(
                {
                    "task_id": task_id,
                    "reason": "pass_to_fail",
                }
            )

    baseline_rate = float(baseline.get("summary", {}).get("success_rate", 0.0))
    current_rate = float(report.get("summary", {}).get("success_rate", 0.0))
    rate_delta = round(current_rate - baseline_rate, 4)
    if rate_delta < 0:
        regressions.append(
            {
                "task_id": "__summary__",
                "reason": "success_rate_decrease",
                "delta": rate_delta,
            }
        )

    return {
        "success_rate_delta": rate_delta,
        "regressions": regressions,
        "regression": len(regressions) > 0,
    }


def run_eval(
    output_dir: Optional[str] = None,
    baseline_path: Optional[str] = None,
    update_baseline: bool = False,
) -> Dict[str, Any]:
    out_dir = Path(output_dir) if output_dir else default_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = out_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    tasks = discover_tasks()
    if not tasks:
        raise RuntimeError("No eval tasks discovered.")

    started_at = _iso_now()
    results: List[Dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        ctx = EvalContext(
            output_dir=out_dir,
            artifacts_dir=artifacts_dir,
            work_dir=Path(tmp_dir),
        )
        for task in tasks:
            results.append(_run_task(task, ctx))

    summary = _build_summary(results)
    report = {
        "schema_version": 1,
        "started_at": started_at,
        "summary": summary,
        "tasks": results,
    }

    comparison = None
    if baseline_path:
        baseline = load_baseline(baseline_path)
        comparison = compare_baseline(baseline, report)
        comparison["baseline_path"] = str(baseline_path)
        report["baseline_comparison"] = comparison

    report_json_path = out_dir / "eval_report.json"
    report_md_path = out_dir / "eval_report.md"

    safe_write_json(report_json_path, report, indent=2, default=str)
    report_md_path.write_text(_report_to_markdown(report), encoding="utf-8")

    baseline_written = None
    if update_baseline:
        baseline_out = (
            Path(baseline_path) if baseline_path else (out_dir / "baseline.json")
        )
        baseline_out.parent.mkdir(parents=True, exist_ok=True)
        baseline_data = _report_to_baseline(report)
        safe_write_json(baseline_out, baseline_data, indent=2, default=str)
        baseline_written = str(baseline_out)

    return {
        "report": report,
        "comparison": comparison,
        "paths": {
            "output_dir": str(out_dir),
            "report_json": str(report_json_path),
            "report_md": str(report_md_path),
            "baseline_written": baseline_written,
        },
    }
