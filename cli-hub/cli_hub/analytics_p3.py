# ruff: noqa: F403, F405, E501
from .analytics_base import *  # noqa: F403

# fmt: off
from .analytics_p1 import UMAMI_URL, USER_AGENT, _analytics_dir, _is_enabled, _lock, _pending_threads, _provider, _stdin_is_tty  # noqa: E402,E501
from .analytics_p2 import _build_posthog_payload, _build_umami_payload, _posthog_capture_url, detect_invocation_context  # noqa: E402,E501
# fmt: on


def _send_event(payload):
    """Send a single event payload. Blocking — callers should use threads."""
    try:
        if _provider() == "umami":
            return requests.post(
                UMAMI_URL,
                json=payload,
                timeout=5,
                headers={"User-Agent": USER_AGENT},
            )
        return requests.post(
            _posthog_capture_url(),
            json=payload,
            timeout=5,
            headers={"User-Agent": USER_AGENT},
        )
    except Exception:
        return None  # analytics must never break the user's workflow


def track_event(event_name, url="/cli-anything-hub", data=None):
    """Fire-and-forget event to the active provider. Non-blocking, never raises."""
    if not _is_enabled():
        return

    event_data = data or {}
    if _provider() == "umami":
        payload = _build_umami_payload(event_name, url, event_data)
    else:
        payload = _build_posthog_payload(event_name, url, event_data)

    t = threading.Thread(target=_send_event, args=(payload,), daemon=True)
    with _lock:
        _pending_threads.append(t)
    t.start()


def track_install(cli_name, version):
    """Track a CLI install event. CLI name goes in properties, not the event name,
    so the event catalog stays flat and dashboards can break down by properties.cli."""
    track_event(
        "cli-install",
        url=f"/cli-anything-hub/install/{cli_name}",
        data={
            "cli": cli_name,
            "version": version,
            "platform": platform.system().lower(),
        },
    )


def track_uninstall(cli_name):
    """Track a CLI uninstall event."""
    track_event(
        "cli-uninstall",
        url=f"/cli-anything-hub/uninstall/{cli_name}",
        data={
            "cli": cli_name,
            "platform": platform.system().lower(),
        },
    )


def track_launch(cli_name):
    """Track a CLI launch event — fires when a user runs `cli-hub launch <name>`.
    Distinct from install: this is actual usage signal."""
    track_event(
        "cli-launch",
        url=f"/cli-anything-hub/launch/{cli_name}",
        data={
            "cli": cli_name,
            "platform": platform.system().lower(),
        },
    )


def track_visit(is_agent=False, command="root", detection=None):
    """Track a cli-hub invocation using the new cli-hub call event."""
    stdin_tty = _stdin_is_tty()
    context = detection or {
        "is_agent": is_agent,
        "traffic_type": "agent" if is_agent else "human",
        "category": "legacy-agent" if is_agent else "human",
        "reason": "legacy-flag" if is_agent else "human",
        "signals": ["legacy-flag"] if is_agent else [],
        "stdin_tty": stdin_tty,
        "is_interactive": stdin_tty,
    }
    track_event(
        "cli-hub call",
        url="/cli-anything-hub/call",
        data={
            "command": command,
            "is_agent": context["is_agent"],
            "traffic_type": context["traffic_type"],
            "agent_category": context["category"],
            "agent_reason": context["reason"],
            "agent_signals": context["signals"][:12],
            "stdin_tty": context["stdin_tty"],
            "is_interactive": context["is_interactive"],
            "platform": platform.system().lower(),
        },
    )


def track_first_run():
    """Send a one-time 'cli-hub-installed' event on first invocation."""
    marker = _analytics_dir() / ".first_run_sent"
    if marker.exists():
        return
    track_event(
        "cli-anything-hub-installed",
        url="/cli-anything-hub/installed",
        data={
            "version": __version__,
            "platform": platform.system().lower(),
        },
    )
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(__version__)
    except Exception:
        pass


def _detect_is_agent():
    """Detect if cli-hub is likely being invoked by an AI agent."""
    return detect_invocation_context()["is_agent"]
