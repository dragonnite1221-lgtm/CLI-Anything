# ruff: noqa: E501
"""Meeting management — CRUD operations via Zoom API.

Covers:
- Create / update / delete meetings
- List meetings
- Get meeting details
- Meeting settings (recording, waiting room, etc.)
"""

from typing import Any
from cli_anything.zoom.utils.zoom_backend import (
    api_get,
    api_post,
    api_patch,
    api_delete,
)

__all__ = ["Any", "api_delete", "api_get", "api_patch", "api_post"]
