"""Obsidian Local REST API wrapper — the single module that makes network requests.

Obsidian Local REST API plugin runs an HTTPS server (default: https://localhost:27124).
Authentication is via Bearer token configured in the plugin settings.
Uses a self-signed certificate by default; TLS verification is skipped only for
loopback hosts (see _should_verify), and enforced for remote hosts.
"""

import os
import requests
import urllib3
from typing import Any
from urllib.parse import urlparse

# Suppress InsecureRequestWarning for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Default Obsidian Local REST API URL
DEFAULT_BASE_URL = "https://localhost:27124"

# Hosts whose self-signed certs we tolerate by default (the plugin ships one).
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _should_verify(base_url: str) -> bool:
    """Decide whether to verify TLS for a request.

    Local Obsidian instances use a self-signed cert, so verification is skipped
    for loopback hosts only. Remote hosts (via --host) are verified so the Bearer
    API key is not sent over an unauthenticated TLS channel. Override explicitly
    with OBSIDIAN_TLS_VERIFY=1/true (force on) or 0/false (force off).
    """
    override = os.environ.get("OBSIDIAN_TLS_VERIFY", "").strip().lower()
    if override in ("1", "true", "yes"):
        return True
    if override in ("0", "false", "no"):
        return False
    host = (urlparse(base_url).hostname or "").lower()
    return host not in _LOCAL_HOSTS


def _headers(api_key: str, accept: str = "application/json",
             content_type: str | None = None) -> dict:
    """Build request headers with Bearer auth."""
    h = {"Authorization": f"Bearer {api_key}", "Accept": accept}
    if content_type:
        h["Content-Type"] = content_type
    return h


def api_get(base_url: str, endpoint: str, api_key: str,
            params: dict | None = None, timeout: int = 30) -> Any:
    """Perform a GET request against the Obsidian REST API."""
    url = f"{base_url.rstrip('/')}{endpoint}"
    try:
        resp = requests.get(url, headers=_headers(api_key),
                           params=params, timeout=timeout, verify=_should_verify(base_url))
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return {"status": "ok"}
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            return resp.json()
        return {"content": resp.text}
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Cannot connect to Obsidian REST API at {base_url}. "
            "Is Obsidian running with the Local REST API plugin enabled?"
        ) from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"Obsidian API error {resp.status_code} on GET {endpoint}: {resp.text}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            f"Request to Obsidian timed out: GET {endpoint}"
        ) from e


def api_post(base_url: str, endpoint: str, api_key: str,
             data: dict | None = None, params: dict | None = None,
             timeout: int = 30) -> Any:
    """Perform a POST request against the Obsidian REST API."""
    url = f"{base_url.rstrip('/')}{endpoint}"
    try:
        resp = requests.post(url, headers=_headers(api_key),
                            json=data, params=params,
                            timeout=timeout, verify=_should_verify(base_url))
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return {"status": "ok"}
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            return resp.json()
        return {"content": resp.text}
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Cannot connect to Obsidian REST API at {base_url}. "
            "Is Obsidian running with the Local REST API plugin enabled?"
        ) from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"Obsidian API error {resp.status_code} on POST {endpoint}: {resp.text}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            f"Request to Obsidian timed out: POST {endpoint}"
        ) from e


def api_put(base_url: str, endpoint: str, api_key: str,
            content: str = "", content_type: str = "text/markdown",
            timeout: int = 30) -> Any:
    """Perform a PUT request (sends raw text, not JSON)."""
    url = f"{base_url.rstrip('/')}{endpoint}"
    try:
        headers = _headers(api_key, content_type=content_type)
        resp = requests.put(url, headers=headers, data=content.encode("utf-8"),
                           timeout=timeout, verify=_should_verify(base_url))
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return {"status": "ok"}
        ct = resp.headers.get("content-type", "")
        if "application/json" in ct:
            return resp.json()
        return {"status": "ok"}
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Cannot connect to Obsidian REST API at {base_url}. "
            "Is Obsidian running with the Local REST API plugin enabled?"
        ) from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"Obsidian API error {resp.status_code} on PUT {endpoint}: {resp.text}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            f"Request to Obsidian timed out: PUT {endpoint}"
        ) from e


def api_delete(base_url: str, endpoint: str, api_key: str,
               timeout: int = 30) -> Any:
    """Perform a DELETE request."""
    url = f"{base_url.rstrip('/')}{endpoint}"
    try:
        resp = requests.delete(url, headers=_headers(api_key),
                              timeout=timeout, verify=_should_verify(base_url))
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return {"status": "ok"}
        ct = resp.headers.get("content-type", "")
        if "application/json" in ct:
            return resp.json()
        return {"status": "ok"}
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Cannot connect to Obsidian REST API at {base_url}. "
            "Is Obsidian running with the Local REST API plugin enabled?"
        ) from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"Obsidian API error {resp.status_code} on DELETE {endpoint}: {resp.text}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            f"Request to Obsidian timed out: DELETE {endpoint}"
        ) from e


def is_available(api_key: str, base_url: str = DEFAULT_BASE_URL) -> bool:
    """Check if Obsidian REST API is reachable."""
    try:
        resp = requests.get(
            f"{base_url.rstrip('/')}/",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5,
            verify=_should_verify(base_url),
        )
        return resp.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False
