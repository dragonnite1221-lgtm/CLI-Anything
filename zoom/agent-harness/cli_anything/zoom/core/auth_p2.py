# ruff: noqa: F403, F405, E501
from .auth_base import *  # noqa: F403


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
            result["name"] = (
                f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            )
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
