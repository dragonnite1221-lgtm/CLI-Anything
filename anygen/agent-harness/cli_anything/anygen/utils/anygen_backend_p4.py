# ruff: noqa: F403, F405, E402, F401, E501
from .anygen_backend_base import *
from .anygen_backend_p2 import create_task
from .anygen_backend_p3 import download_file, poll_task, query_task

from . import anygen_backend_base as _coupbase  # noqa: E402


def download_thumbnail(
    api_key: str, task_id: str, output_dir: str, extra_headers: dict | None = None
) -> dict:
    """Download only the thumbnail image for a completed task."""
    task = _coupbase._COUP_GLOBALS["query_task"](api_key, task_id, extra_headers)
    if task.get("status") != "completed":
        raise RuntimeError(f"Task not completed (status={task.get('status')})")
    output = task.get("output", {})
    thumbnail_url = output.get("thumbnail_url")
    if not thumbnail_url:
        raise RuntimeError("No thumbnail available for this task")
    resp = requests.get(thumbnail_url, timeout=120)
    resp.raise_for_status()
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / f"thumbnail_{task_id}.png"
    with open(file_path, "wb") as f:
        f.write(resp.content)
    return {"local_path": str(file_path), "file_size": len(resp.content)}


def run_full_workflow(
    api_key: str,
    operation: str,
    prompt: str,
    output_dir: str | None = None,
    *,
    on_progress: Callable | None = None,
    **create_kwargs,
) -> dict:
    """Full workflow: create → poll → download.

    Returns dict with task info and local_path (if output_dir given).
    """
    result = create_task(api_key, operation, prompt, **create_kwargs)
    task_id = result["task_id"]
    task = poll_task(api_key, task_id, on_progress=on_progress)
    dl_info = {}
    if output_dir and operation in DOWNLOADABLE_OPERATIONS:
        dl_info = download_file(api_key, task_id, output_dir)
    return {
        "task_id": task_id,
        "task_url": result.get("task_url"),
        "status": task.get("status"),
        "output": task.get("output", {}),
        **dl_info,
    }
