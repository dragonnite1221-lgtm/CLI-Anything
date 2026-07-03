"""Local OAuth2 callback capture for the Zoom browser-login flow.

Split out of ``auth.py`` so the login flow stays within the file-size limit.
Adds two hardening measures over the previous inline handler (code review M-4):

* CSRF ``state`` validation — a callback whose ``state`` does not match the
  value we generated is rejected, so an attacker who reaches the local
  callback during the ~2-minute window cannot inject their own auth code.
* ``html.escape`` on the reflected ``error_description`` — the error page no
  longer interpolates raw query text into HTML (reflected-XSS defense).
"""

from __future__ import annotations

import html
import http.server
import webbrowser
from urllib.parse import parse_qs, urlparse


def capture_oauth_callback(
    auth_url: str, port: int, expected_state: str, timeout: int = 120
) -> tuple[str | None, str | None]:
    """Open the browser and capture the OAuth callback on 127.0.0.1:``port``.

    Returns ``(auth_code, error_message)`` — exactly one is non-None on a
    completed callback; both are None on timeout.
    """
    result: dict[str, str | None] = {"code": None, "error": None}

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - http.server API name
            query = parse_qs(urlparse(self.path).query)
            # Reject any callback whose state doesn't match (CSRF / code injection).
            state = query.get("state", [None])[0]
            if state != expected_state:
                self._respond(400, "<h2>Authorization failed: invalid state</h2>")
                result["error"] = "invalid state parameter (possible CSRF)"
            elif "code" in query:
                result["code"] = query["code"][0]
                self._respond(
                    200,
                    "<h2>Authorization successful!</h2>"
                    "<p>You can close this window and return to the CLI.</p>",
                )
            elif "error" in query:
                detail = query.get("error_description", query["error"])[0]
                result["error"] = detail
                self._respond(400, f"<h2>Authorization failed: {html.escape(detail)}</h2>")
            else:
                self.send_response(400)
                self.end_headers()

        def _respond(self, status: int, body_html: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body>{body_html}</body></html>".encode())

        def log_message(self, format, *args):  # noqa: A002 - http.server API name
            pass  # Suppress server logs

    server = http.server.HTTPServer(("127.0.0.1", port), CallbackHandler)
    server.timeout = timeout
    webbrowser.open(auth_url)
    server.handle_request()
    server.server_close()
    return result["code"], result["error"]
