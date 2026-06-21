# ruff: noqa: F403, F405, E501
from .gpu_trace_base import *  # noqa: F403


def _find_export_dir(
    output_dir: str,
    *,
    artifact_paths: Sequence[str] | None = None,
) -> tuple[str, dict[str, str]]:
    """Pick the newest export directory containing a complete GPU Trace export."""
    output_root = Path(output_dir).resolve()
    artifact_path_set = None
    if artifact_paths is not None:
        artifact_path_set = {str(Path(path).resolve()) for path in artifact_paths}

    matches_by_name = {
        name: sorted(output_root.rglob(name))
        for name in (*REQUIRED_EXPORT_FILES, "GPUTRACE_REGIMES.xls")
    }

    candidate_dirs = {
        path.parent for name in REQUIRED_EXPORT_FILES for path in matches_by_name[name]
    }
    complete_candidates: list[tuple[int, Path, dict[str, str]]] = []
    for directory in candidate_dirs:
        required_paths = [directory / name for name in REQUIRED_EXPORT_FILES]
        if not all(path.is_file() for path in required_paths):
            continue
        if artifact_path_set is not None and not all(
            str(path.resolve()) in artifact_path_set for path in required_paths
        ):
            continue
        newest_required_mtime = max(path.stat().st_mtime_ns for path in required_paths)
        files = {
            "frame": str(directory / "FRAME.xls"),
            "trace_frame": str(directory / "GPUTRACE_FRAME.xls"),
            "events": str(directory / "D3DPERF_EVENTS.xls"),
            "regimes": None,
        }
        regimes_path = directory / "GPUTRACE_REGIMES.xls"
        if regimes_path.is_file():
            files["regimes"] = str(regimes_path)
        complete_candidates.append((newest_required_mtime, directory, files))

    if complete_candidates:
        _, export_dir, files = max(
            complete_candidates,
            key=lambda item: (item[0], str(item[1])),
        )
        return str(export_dir), files

    if artifact_path_set is not None:
        raise RuntimeError(
            "GPU Trace capture finished without a complete newly exported table set "
            "(FRAME.xls, GPUTRACE_FRAME.xls, D3DPERF_EVENTS.xls). Refusing to "
            "summarize stale export data."
        )

    missing = [name for name in REQUIRED_EXPORT_FILES if not matches_by_name[name]]
    if missing:
        raise RuntimeError(
            "GPU Trace export summary requires exported tables. Missing: "
            + ", ".join(missing)
        )
    raise RuntimeError(
        "GPU Trace export summary requires FRAME.xls, GPUTRACE_FRAME.xls, and "
        "D3DPERF_EVENTS.xls to exist under the same export directory."
    )


def _read_kv_file(path: str) -> dict[str, str]:
    """Read a simple tab-separated key/value file."""
    data: dict[str, str] = {}
    with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or "\t" not in line:
                continue
            key, value = line.split("\t", 1)
            data[key.strip()] = value.strip()
    return data


def _read_event_rows(path: str) -> list[dict[str, str]]:
    """Read D3DPERF event rows from the exported TSV."""
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = []
        for row in reader:
            event_text = (row.get("event_text") or "").rstrip()
            time_ms = (row.get("time_ms") or "").strip()
            if not event_text or not time_ms:
                continue
            rows.append({"event_text": event_text, "time_ms": time_ms})
        return rows


def _read_table_rows(path: str | None) -> tuple[list[str], list[dict[str, str]]]:
    """Read a generic tab-separated table."""
    if not path:
        return [], []
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = [
            {
                str(key): (value or "").strip()
                for key, value in row.items()
                if key is not None
            }
            for row in reader
        ]
        return list(reader.fieldnames or []), rows


def _safe_float(value: str | None) -> float | None:
    """Convert a string to float when possible."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: float | None) -> int | None:
    """Convert a float to int when available."""
    if value is None:
        return None
    return int(round(value))


def _metric_unit(metric_name: str) -> str:
    """Classify a metric suffix into a compact unit family."""
    lowered = metric_name.lower()
    if lowered.endswith(".avg.pct_of_peak_sustained_elapsed"):
        return "pct_of_peak"
    if lowered.endswith(".pct"):
        return "percent"
    if lowered.endswith(".sum.per_second"):
        return "per_second"
    if lowered.endswith(".sum"):
        return "count"
    if lowered.endswith(".avg.per_cycle_elapsed"):
        return "per_cycle"
    if lowered.endswith(".avg.peak_sustained"):
        return "peak_sustained"
    if ".avg." in lowered:
        return "average"
    return "other"
