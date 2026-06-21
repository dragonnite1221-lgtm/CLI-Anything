# ruff: noqa: F403, F405, E501
from .security_base import *  # noqa: F403


def get_allowed_schemes() -> set[str]:
    """Get the set of allowed URL schemes.

    Returns:
        Set of allowed schemes (e.g., {"http", "https"}).
    """
    return _ALLOWED_SCHEMES.copy()


def get_blocked_schemes() -> set[str]:
    """Get the set of blocked URL schemes.

    Returns:
        Set of blocked schemes (e.g., {"file", "javascript", "data"}).
    """
    return _BLOCKED_SCHEMES.copy()
