# ruff: noqa: F403, F405, E501
from .zoom_backend_base import *  # noqa: F403

# fmt: off
from .zoom_backend_p1 import _get_valid_token  # noqa: E402,E501
# fmt: on


def api_request(
    method: str,
    endpoint: str,
    params: dict | None = None,
    json_data: dict | None = None,
    stream: bool = False,
) -> Any:
    """Make an authenticated request to the Zoom API.

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE).
        endpoint: API endpoint path (e.g., '/users/me/meetings').
        params: Query parameters.
        json_data: JSON request body.
        stream: Whether to stream the response (for downloads).

    Returns:
        Parsed JSON response, or raw Response if streaming.
    """
    token = _get_valid_token()
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    resp = requests.request(
        method,
        url,
        headers=headers,
        params=params,
        json=json_data,
        stream=stream,
        timeout=60,
    )

    if stream and resp.status_code == 200:
        return resp

    resp.raise_for_status()

    if resp.status_code == 204:
        return {"status": "success"}

    return resp.json()


def api_get(endpoint: str, params: dict | None = None) -> Any:
    """Shorthand for GET request."""
    return api_request("GET", endpoint, params=params)


def api_post(endpoint: str, data: dict | None = None) -> Any:
    """Shorthand for POST request."""
    return api_request("POST", endpoint, json_data=data)


def api_patch(endpoint: str, data: dict | None = None) -> Any:
    """Shorthand for PATCH request."""
    return api_request("PATCH", endpoint, json_data=data)


def api_delete(endpoint: str) -> Any:
    """Shorthand for DELETE request."""
    return api_request("DELETE", endpoint)


def get_current_user() -> dict:
    """Get the authenticated user's profile."""
    return api_get("/users/me")
