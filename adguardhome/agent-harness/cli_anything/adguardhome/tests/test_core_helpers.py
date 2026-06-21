# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-adguardhome core modules.

No real AdGuardHome instance needed - all HTTP calls are mocked.
"""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import requests
from cli_anything.adguardhome.utils.adguardhome_backend import AdGuardHomeClient
from cli_anything.adguardhome.core import project, filtering, blocking, clients, rewrite


def mock_response(data=None, status=200, text=""):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status
    if data is not None:
        resp.json.return_value = data
        resp.content = json.dumps(data).encode()
        resp.text = json.dumps(data)
    else:
        resp.json.side_effect = ValueError("no json")
        resp.content = text.encode() if text else b""
        resp.text = text
    resp.raise_for_status = MagicMock()
    return resp


def make_client(host="localhost", port=3000, username="admin", password="secret"):
    return AdGuardHomeClient(host=host, port=port, username=username, password=password)


__all__ = [
    "AdGuardHomeClient",
    "MagicMock",
    "Path",
    "blocking",
    "clients",
    "filtering",
    "json",
    "make_client",
    "mock_response",
    "os",
    "patch",
    "project",
    "pytest",
    "requests",
    "rewrite",
]
