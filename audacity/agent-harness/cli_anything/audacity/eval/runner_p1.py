# ruff: noqa: F403, F405, E501
from .runner_base import *  # noqa: F403


@dataclass
class TaskSpec:
    task_id: str
    name: str
    description: str
    run: Callable[["EvalContext"], Dict[str, Any]]


@dataclass
class EvalContext:
    output_dir: Path
    artifacts_dir: Path
    work_dir: Path
    task_id: str = ""

    def task_work_dir(self) -> Path:
        path = self.work_dir / self.task_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def task_artifacts_dir(self) -> Path:
        path = self.artifacts_dir / self.task_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def task_artifact_path(self, filename: str) -> Path:
        return self.task_artifacts_dir() / filename


def _iso_now() -> str:
    return datetime.now().isoformat()


def default_output_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("eval_results") / stamp


def discover_tasks() -> List[TaskSpec]:
    tasks_pkg = importlib.import_module("cli_anything.audacity.eval.tasks")
    task_specs: List[TaskSpec] = []
    seen_ids = set()

    for mod in pkgutil.iter_modules(tasks_pkg.__path__):
        if mod.ispkg:
            continue
        module_name = f"{tasks_pkg.__name__}.{mod.name}"
        module = importlib.import_module(module_name)
        task_meta = getattr(module, "TASK", None)
        run_fn = getattr(module, "run", None)
        if not isinstance(task_meta, dict) or not callable(run_fn):
            continue

        task_id = str(task_meta.get("id") or mod.name)
        if task_id in seen_ids:
            raise ValueError(f"Duplicate task id: {task_id}")
        seen_ids.add(task_id)

        task_specs.append(
            TaskSpec(
                task_id=task_id,
                name=str(task_meta.get("name", task_id)),
                description=str(task_meta.get("description", "")),
                run=run_fn,
            )
        )

    task_specs.sort(key=lambda t: t.task_id)
    return task_specs


def _run_task(task: TaskSpec, ctx: EvalContext) -> Dict[str, Any]:
    ctx.task_id = task.task_id
    ctx.task_work_dir()
    ctx.task_artifacts_dir()

    started = time.time()
    ok = False
    metrics: Dict[str, Any] = {}
    artifacts: List[str] = []
    notes = ""
    error = ""

    try:
        result = task.run(ctx) or {}
        ok = bool(result.get("ok", False))
        metrics = result.get("metrics", {}) or {}
        artifacts = result.get("artifacts", []) or []
        notes = result.get("notes", "") or ""
    except Exception as exc:  # pylint: disable=broad-except
        error = f"{type(exc).__name__}: {exc}"

    duration_ms = int((time.time() - started) * 1000)
    status = "pass" if ok else "fail"

    return {
        "id": task.task_id,
        "name": task.name,
        "description": task.description,
        "status": status,
        "duration_ms": duration_ms,
        "metrics": metrics,
        "artifacts": artifacts,
        "notes": notes,
        "error": error,
    }


def _build_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "pass")
    failed = total - passed
    success_rate = float(passed) / float(total) if total else 0.0
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": round(success_rate, 4),
    }


def _report_to_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Audacity Eval Report")
    lines.append("")
    lines.append(f"Run at: {report.get('started_at', '')}")
    lines.append("")
    summary = report.get("summary", {})
    lines.append(
        f"Summary: {summary.get('passed', 0)}/{summary.get('total', 0)} passed "
        f"({summary.get('success_rate', 0.0):.2%})"
    )
    lines.append("")
    lines.append("| Task | Status | Duration (ms) |")
    lines.append("| --- | --- | --- |")
    for task in report.get("tasks", []):
        status = str(task.get("status", "")).upper()
        lines.append(
            f"| {task.get('id', '')} | {status} | {task.get('duration_ms', 0)} |"
        )

    comparison = report.get("baseline_comparison")
    if comparison:
        lines.append("")
        lines.append("## Baseline Comparison")
        lines.append("")
        lines.append(f"Baseline: {comparison.get('baseline_path', '')}")
        lines.append(
            f"Success rate delta: {comparison.get('success_rate_delta', 0.0):.4f}"
        )
        if comparison.get("regressions"):
            lines.append("")
            lines.append("Regressions:")
            for reg in comparison.get("regressions", []):
                lines.append(f"- {reg.get('task_id', '')}: {reg.get('reason', '')}")
        else:
            lines.append("")
            lines.append("Regressions: none")

    lines.append("")
    return "\n".join(lines)
