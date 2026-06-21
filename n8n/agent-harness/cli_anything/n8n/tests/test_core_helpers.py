# ruff: noqa: F403, F405, E501
"""Unit tests — all HTTP calls mocked."""

from __future__ import annotations
import json
from unittest.mock import MagicMock, patch
import pytest
from cli_anything.n8n.core import (
    credentials,
    executions,
    project,
    tags,
    variables,
    workflows,
)
from cli_anything.n8n.utils import n8n_backend


def mock_response(
    status_code: int = 200, json_data: dict | list | None = None
) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = json.dumps(json_data or {})
    resp.raise_for_status = MagicMock()
    return resp


BASE = "https://n8n.example.com"
KEY = "test-api-key-1234"


__all__ = [
    "BASE",
    "KEY",
    "MagicMock",
    "annotations",
    "credentials",
    "executions",
    "json",
    "mock_response",
    "n8n_backend",
    "patch",
    "project",
    "pytest",
    "tags",
    "variables",
    "workflows",
]
