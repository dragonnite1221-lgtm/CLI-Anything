# ruff: noqa: F403, F405, E402, F401, E501
from .anygen_backend_base import *
from .anygen_backend_p1 import _make_auth_token, _require_api_key

from . import anygen_backend_base as _coupbase  # noqa: E402


def query_task(api_key: str, task_id: str, extra_headers: dict | None = None) -> dict:
    """Single non-blocking query of task status. Returns full task dict."""
    api_key = _require_api_key(api_key)
    headers = {"Authorization": _make_auth_token(api_key)}
    if extra_headers:
        headers.update(extra_headers)
    resp = requests.get(
        f"{API_BASE}/v1/openapi/tasks/{task_id}", headers=headers, timeout=30
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Query failed (HTTP {resp.status_code}): {resp.text[:300]}")
    return resp.json()


def poll_task(
    api_key: str,
    task_id: str,
    *,
    max_time: int = MAX_POLL_TIME,
    interval: int = POLL_INTERVAL,
    extra_headers: dict | None = None,
    on_progress: Callable | None = None,
) -> dict:
    """Poll task until completed/failed. Returns final task dict.

    Args:
        on_progress: optional callback(status, progress_pct) called on each poll.
    """
    api_key = _require_api_key(api_key)
    start = time.time()
    last_progress = -1
    while True:
        elapsed = time.time() - start
        if elapsed > max_time:
            raise TimeoutError(f"Polling timeout after {max_time}s for task {task_id}")
        task = _coupbase._COUP_GLOBALS["query_task"](api_key, task_id, extra_headers)
        status = task.get("status")
        progress = task.get("progress", 0)
        if progress != last_progress and on_progress:
            on_progress(status, progress)
            last_progress = progress
        if status == "completed":
            return task
        if status == "failed":
            error = task.get("error", "Unknown error")
            raise RuntimeError(f"Task {task_id} failed: {error}")
        time.sleep(interval)


def download_file(
    api_key: str, task_id: str, output_dir: str, extra_headers: dict | None = None
) -> dict:
    """Download the generated file for a completed task.

    Returns {"local_path": ..., "file_name": ..., "file_size": ..., "task_url": ...}.
    """
    task = _coupbase._COUP_GLOBALS["query_task"](api_key, task_id, extra_headers)
    if task.get("status") != "completed":
        raise RuntimeError(f"Task not completed (status={task.get('status')})")
    output = task.get("output", {})
    file_url = output.get("file_url")
    file_name = output.get("file_name")
    task_url = output.get("task_url", f"{API_BASE}/task/{task_id}")
    if not file_url:
        raise RuntimeError("No download URL available for this task")
    resp = requests.get(file_url, timeout=120)
    resp.raise_for_status()
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / (file_name or "output")
    if file_path.exists():
        stem, suffix = (file_path.stem, file_path.suffix)
        counter = 1
        while file_path.exists():
            file_path = out_path / f"{stem}_{counter}{suffix}"
            counter += 1
    with open(file_path, "wb") as f:
        f.write(resp.content)
    return {
        "local_path": str(file_path),
        "file_name": file_name,
        "file_size": len(resp.content),
        "task_url": task_url,
    }
