"""OAuth2 authentication flow for Zoom API.

Handles:
- OAuth app setup (client_id, client_secret, redirect_uri)
- Browser-based authorization flow
- Token exchange and persistence
- Token refresh
- Auth status checking
"""

import secrets
from urllib.parse import urlparse

from cli_anything.zoom.core._oauth_callback import capture_oauth_callback
from cli_anything.zoom.utils.zoom_backend import (
    load_config, save_config, load_tokens, save_tokens,
    get_authorize_url, exchange_code, get_current_user,
    CONFIG_DIR,
)


def setup_oauth(client_id: str, client_secret: str,
                redirect_uri: str = "http://localhost:4199/callback") -> dict:
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

    # CSRF state: an unguessable token echoed back on the callback and verified
    # there, so an injected authorization code with the wrong state is rejected.
    state = secrets.token_urlsafe(32)
    auth_url = get_authorize_url(client_id, redirect_uri, state=state)

    # Open the browser and capture the callback (validates state, escapes errors).
    auth_code, auth_error = capture_oauth_callback(auth_url, port, expected_state=state)

    if auth_error:
        raise RuntimeError(f"Authorization failed: {auth_error}")

    if not auth_code:
        raise RuntimeError("Authorization timed out. Please try again.")

    # Exchange code for tokens
    tokens = exchange_code(client_id, client_secret, auth_code, redirect_uri)
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


def login_with_code(code: str) -> dict:
    """Complete login with a manually provided authorization code.

    Use this when the automatic callback server doesn't work.

    Args:
        code: The authorization code from the OAuth callback URL.

    Returns:
        Dict with login status.
    """
    config = load_config()
    if not config.get("client_id"):
        raise RuntimeError("OAuth app not configured. Run 'auth setup' first.")

    tokens = exchange_code(
        config["client_id"],
        config["client_secret"],
        code,
        config.get("redirect_uri", "http://localhost:4199/callback"),
    )
    save_tokens(tokens)

    try:
        user = get_current_user()
        return {
            "status": "logged_in",
            "user": user.get("email", "unknown"),
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        }
    except Exception:
        return {"status": "logged_in", "message": "Tokens saved."}


def get_auth_status() -> dict:
    """Check current authentication status.

    Returns:
        Dict with auth status, user info, and token expiry.
    """
    config = load_config()
    tokens = load_tokens()

    result = {
        "configured": bool(config.get("client_id")),
        "authenticated": bool(tokens.get("access_token")),
    }

    if config.get("client_id"):
        result["client_id"] = config["client_id"]
        result["redirect_uri"] = config.get("redirect_uri", "")

    if tokens.get("access_token"):
        try:
            user = get_current_user()
            result["user"] = user.get("email", "unknown")
            result["name"] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            result["token_valid"] = True
        except Exception as e:
            result["token_valid"] = False
            result["token_error"] = str(e)

    return result


def logout() -> dict:
    """Remove saved tokens (does not revoke on Zoom side).

    Returns:
        Dict confirming logout.
    """
    token_file = CONFIG_DIR / "tokens.json"
    if token_file.exists():
        token_file.unlink()
    return {"status": "logged_out", "message": "Local tokens removed."}
