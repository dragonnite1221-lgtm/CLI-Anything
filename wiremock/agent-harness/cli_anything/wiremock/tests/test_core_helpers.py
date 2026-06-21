# ruff: noqa: F403, F405, E501
"""Unit tests for cli_anything.wiremock core modules.

All tests use unittest.mock to intercept HTTP calls — no live server required.
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch


def _mock_response(status_code: int = 200, json_data: dict = None):
    """Return a mock requests.Response with configurable status and JSON."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {}
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        from requests.exceptions import HTTPError

        mock.raise_for_status.side_effect = HTTPError(f"{status_code}")
    return mock


__all__ = [
    "MagicMock",
    "_mock_response",
    "json",
    "os",
    "patch",
    "sys",
    "unittest",
]
