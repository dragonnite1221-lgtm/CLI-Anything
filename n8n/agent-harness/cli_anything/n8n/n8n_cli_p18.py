# ruff: noqa: F403, F405, E501
from .n8n_cli_base import *  # noqa: F403

# fmt: off
from .n8n_cli_p1 import cli  # noqa: E402,E501
# fmt: on


def main() -> None:
    try:
        cli(obj={})
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code
        try:
            body = exc.response.json()
            msg = str(body.get("message", "Request failed"))[:200]
        except (ValueError, AttributeError):
            msg = "Request failed"
        error(f"{status} — {msg}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        error("Cannot connect to n8n. Check your URL and network.")
        sys.exit(1)
    except ValueError as exc:
        error(str(exc))
        sys.exit(1)
    except OSError as exc:
        error(f"File error: {exc}")
        sys.exit(1)
