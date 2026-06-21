# ruff: noqa: F403, F405, E501
from .auth_base import *  # noqa: F403


def setup_oauth(
    client_id: str,
    client_secret: str,
    redirect_uri: str = "http://localhost:4199/callback",
) -> dict:
    """Save OAuth app credentials.

    Args:
        client_id: Zoom OAuth app client ID.
        client_secret: Zoom OAuth app client secret.
        redirect_uri: OAuth redirect URI (must match app config).

    Returns:
        Saved configuration dict.
    """
    config = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }
    save_config(config)
    return {
        "status": "configured",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "config_path": str(CONFIG_DIR / "config.json"),
    }


def login() -> dict:
    """Run the OAuth2 authorization flow.

    Opens a browser for user authorization, starts a local HTTP server
    to capture the callback, exchanges the code for tokens, and saves them.

    Returns:
        Dict with login status and user info.
    """
    config = load_config()
    if not config.get("client_id") or not config.get("client_secret"):
        raise RuntimeError(
            "OAuth app not configured. Run 'auth setup' with your "
            "client_id and client_secret first."
        )

    client_id = config["client_id"]
    client_secret = config["client_secret"]
    redirect_uri = config.get("redirect_uri", "http://localhost:4199/callback")

    # Parse redirect URI to get port
    parsed = urlparse(redirect_uri)
    port = parsed.port or 4199

    auth_url = get_authorize_url(client_id, redirect_uri)

    # Capture authorization code via local HTTP server
    auth_code = [None]
    auth_error = [None]

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            query = parse_qs(urlparse(self.path).query)
            if "code" in query:
                auth_code[0] = query["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h2>Authorization successful!</h2>"
                    b"<p>You can close this window and return to the CLI.</p>"
                    b"</body></html>"
                )
            elif "error" in query:
                auth_error[0] = query.get("error_description", query["error"])[0]
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    f"<html><body><h2>Authorization failed: {auth_error[0]}</h2>".encode()
                )
            else:
                self.send_response(400)
                self.end_headers()

        def log_message(self, format, *args):
            pass  # Suppress server logs

    server = http.server.HTTPServer(("127.0.0.1", port), CallbackHandler)
    server.timeout = 120  # 2 minutes to complete auth

    # Open browser
    webbrowser.open(auth_url)

    # Wait for callback
    server.handle_request()
    server.server_close()

    if auth_error[0]:
        raise RuntimeError(f"Authorization failed: {auth_error[0]}")

    if not auth_code[0]:
        raise RuntimeError("Authorization timed out. Please try again.")

    # Exchange code for tokens
    tokens = exchange_code(client_id, client_secret, auth_code[0], redirect_uri)
    save_tokens(tokens)

    # Verify by getting user info
    try:
        user = get_current_user()
        return {
            "status": "logged_in",
            "user": user.get("email", "unknown"),
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
            "account_id": user.get("account_id", ""),
        }
    except Exception:
        return {
            "status": "logged_in",
            "message": "Tokens saved. Could not verify user info.",
        }
