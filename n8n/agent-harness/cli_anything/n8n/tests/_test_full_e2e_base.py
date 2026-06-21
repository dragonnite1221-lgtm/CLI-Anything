# ruff: noqa: F403, F405, E501
"""E2E tests — require a running n8n instance.

Set N8N_BASE_URL and N8N_API_KEY env vars to run these tests.
Verified against n8n 2.43.0 (API v1.1.1).
Skip with: pytest -m "not e2e"
"""
from __future__ import annotations
import os
import subprocess
import sys
import uuid
import pytest
import requests as req
from cli_anything.n8n.core import credentials, tags, variables, workflows


pytestmark = pytest.mark.e2e


N8N_URL = os.environ.get("N8N_BASE_URL", "")


N8N_KEY = os.environ.get("N8N_API_KEY", "")


# fmt: off
__all__ = ['N8N_KEY', 'N8N_URL', 'annotations', 'credentials', 'os', 'pytest', 'pytestmark', 'req', 'subprocess', 'sys', 'tags', 'uuid', 'variables', 'workflows']  # noqa: E501
# fmt: on
