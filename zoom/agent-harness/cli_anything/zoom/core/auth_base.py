# ruff: noqa: E501
"""OAuth2 authentication flow for Zoom API.

Handles:
- OAuth app setup (client_id, client_secret, redirect_uri)
- Browser-based authorization flow
- Token exchange and persistence
- Token refresh
- Auth status checking
"""

import webbrowser
import http.server
import threading
from urllib.parse import urlparse, parse_qs

from cli_anything.zoom.utils.zoom_backend import (
    load_config,
    save_config,
    load_tokens,
    save_tokens,
    get_authorize_url,
    exchange_code,
    get_current_user,
    CONFIG_DIR,
)

__all__ = [
    "CONFIG_DIR",
    "exchange_code",
    "get_authorize_url",
    "get_current_user",
    "http",
    "load_config",
    "load_tokens",
    "parse_qs",
    "save_config",
    "save_tokens",
    "threading",
    "urlparse",
    "webbrowser",
]
