# ruff: noqa: F403, F405, E501
from .anygen_backend_base import *  # noqa: F403

# fmt: off
from .anygen_backend_p1 import _make_auth_token, _require_api_key, encode_file  # noqa: E402,E501
# fmt: on


def prepare_task(
    api_key: str,
    messages: list[dict],
    file_tokens: list[str] | None = None,
    extra_headers: dict | None = None,
) -> dict:
    """Call the prepare API for multi-turn requirement analysis.

    Returns the full response dict including 'reply', 'status',
    'suggested_task_params', and 'messages'.
    """
    api_key = _require_api_key(api_key)
    auth_token = _make_auth_token(api_key)

    body: dict = {"auth_token": auth_token, "messages": messages}
    if file_tokens:
        body["file_tokens"] = file_tokens

    headers: dict = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    resp = requests.post(
        f"{API_BASE}/v1/openapi/tasks/prepare",
        json=body,
        headers=headers,
        timeout=120,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Prepare failed (HTTP {resp.status_code}): {resp.text[:300]}"
        )

    result = resp.json()
    if not result.get("success"):
        raise RuntimeError(f"Prepare failed: {result.get('error', 'Unknown error')}")
    return result


def create_task(
    api_key: str,
    operation: str,
    prompt: str,
    *,
    language: str | None = None,
    slide_count: int | None = None,
    template: str | None = None,
    ratio: str | None = None,
    export_format: str | None = None,
    file_tokens: list[str] | None = None,
    files: list[str] | None = None,
    style: str | None = None,
    extra_headers: dict | None = None,
) -> dict:
    """Create an async generation task.

    Returns {"task_id": ..., "task_url": ...}.
    """
    api_key = _require_api_key(api_key)
    if operation not in VALID_OPERATIONS:
        raise ValueError(
            f"Invalid operation '{operation}'. Valid: {', '.join(VALID_OPERATIONS)}"
        )

    final_prompt = prompt
    if style:
        final_prompt = f"{prompt}\n\nStyle requirement: {style}"

    body: dict = {
        "auth_token": _make_auth_token(api_key),
        "operation": operation,
        "prompt": final_prompt,
    }
    if language:
        body["language"] = language
    if operation == "slide":
        if slide_count:
            body["slide_count"] = slide_count
        if template:
            body["template"] = template
        if ratio:
            body["ratio"] = ratio
    if export_format:
        body["export_format"] = export_format
    if file_tokens:
        body["file_tokens"] = file_tokens

    if files:
        encoded = []
        for fp in files:
            encoded.append(encode_file(fp))
        body["files"] = encoded

    headers: dict = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    resp = requests.post(
        f"{API_BASE}/v1/openapi/tasks",
        json=body,
        headers=headers,
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Create task failed (HTTP {resp.status_code}): {resp.text[:300]}"
        )

    result = resp.json()
    if not result.get("success"):
        raise RuntimeError(
            f"Task creation failed: {result.get('error', 'Unknown error')}"
        )

    return {
        "task_id": result.get("task_id"),
        "task_url": result.get("task_url"),
    }
