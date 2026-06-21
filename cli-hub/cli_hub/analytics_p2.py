# ruff: noqa: F403, F405, E501
from .analytics_base import *  # noqa: F403

# fmt: off
from .analytics_p1 import ANALYTICS_ID_FILE, HOSTNAME, POSTHOG_API_HOST, POSTHOG_PROJECT_TOKEN, UMAMI_WEBSITE_ID, _AGENT_ENV_RULES, _PARENT_PROCESS_RULES, _analytics_dir, _parent_process_commands, _stdin_is_tty  # noqa: E402,E501
# fmt: on


def detect_invocation_context():
    """Classify the current cli-hub invocation as human, agent, or scripted."""
    signals = []

    for env_name, category, signal_id in _AGENT_ENV_RULES:
        if os.environ.get(env_name):
            signals.append({"id": signal_id, "category": category})

    for cmd in _parent_process_commands():
        for signal_id, category, pattern in _PARENT_PROCESS_RULES:
            if pattern.search(cmd):
                signals.append({"id": signal_id, "category": category})

    seen = set()
    unique_signals = []
    for signal in signals:
        if signal["id"] in seen:
            continue
        seen.add(signal["id"])
        unique_signals.append(signal)

    stdin_tty = _stdin_is_tty()
    if unique_signals:
        primary = unique_signals[0]
        return {
            "is_agent": True,
            "traffic_type": "agent",
            "category": primary["category"],
            "reason": primary["id"],
            "signals": [signal["id"] for signal in unique_signals],
            "stdin_tty": stdin_tty,
            "is_interactive": stdin_tty,
        }

    if not stdin_tty:
        return {
            "is_agent": True,
            "traffic_type": "agent",
            "category": "scripted_client",
            "reason": "stdin-not-tty",
            "signals": ["stdin-not-tty"],
            "stdin_tty": False,
            "is_interactive": False,
        }

    return {
        "is_agent": False,
        "traffic_type": "human",
        "category": "human",
        "reason": "human",
        "signals": [],
        "stdin_tty": True,
        "is_interactive": True,
    }


def _get_distinct_id():
    override = os.environ.get("CLI_HUB_ANALYTICS_DISTINCT_ID", "").strip()
    if override:
        return override

    marker = _analytics_dir() / ANALYTICS_ID_FILE
    try:
        if marker.exists():
            value = marker.read_text().strip()
            if value:
                return value
        marker.parent.mkdir(parents=True, exist_ok=True)
        value = str(uuid.uuid4())
        marker.write_text(value)
        return value
    except Exception:
        return f"cli-hub-anon-{uuid.uuid4()}"


def _posthog_capture_url():
    host = os.environ.get("CLI_HUB_POSTHOG_API_HOST", POSTHOG_API_HOST).rstrip("/")
    return f"{host}/capture/"


def _build_umami_payload(event_name, url, data):
    return {
        "type": "event",
        "payload": {
            "website": UMAMI_WEBSITE_ID,
            "hostname": HOSTNAME,
            "url": url,
            "name": event_name,
            "data": data,
        },
    }


def _build_posthog_payload(event_name, url, data):
    return {
        "api_key": os.environ.get(
            "CLI_HUB_POSTHOG_PROJECT_TOKEN", POSTHOG_PROJECT_TOKEN
        ),
        "event": event_name,
        "distinct_id": _get_distinct_id(),
        "properties": {
            "$current_url": f"https://{HOSTNAME}{url}",
            "hostname": HOSTNAME,
            "source": "cli",
            "channel": "cli-hub",
            "hub_version": __version__,
            **(data or {}),
        },
    }
