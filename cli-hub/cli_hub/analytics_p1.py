# ruff: noqa: F403, F405, E501
from .analytics_base import *  # noqa: F403


ANALYTICS_PROVIDER = "posthog"
UMAMI_URL = "https://cloud.umami.is/api/send"
UMAMI_WEBSITE_ID = "a076c661-bed1-405c-a522-813794e688b4"
POSTHOG_API_HOST = "https://us.i.posthog.com"
POSTHOG_PROJECT_TOKEN = "phc_ovP8d5bmjpn8YZnTo7pb6rE3TikcAMgmNVt75o3Ywejz"
HOSTNAME = "clianything.cc"
USER_AGENT = f"Mozilla/5.0 (compatible; cli-anything-hub/{__version__})"
ANALYTICS_ID_FILE = ".analytics_id"
_pending_threads = []
_lock = threading.Lock()
_AGENT_ENV_RULES = (
    ("CLAUDE_CODE", "agent_tool", "claude-code-env"),
    ("CLAUDECODE", "agent_tool", "claude-code-env-alt"),
    ("CODEX", "agent_tool", "codex-env"),
    ("OPENAI_CODEX", "agent_tool", "codex-env-alt"),
    ("CURSOR_SESSION", "agent_tool", "cursor-session-env"),
    ("CURSOR_TRACE_ID", "agent_tool", "cursor-trace-env"),
    ("CLINE_SESSION", "agent_tool", "cline-session-env"),
    ("AIDER", "agent_tool", "aider-env"),
    ("AIDER_SESSION_ID", "agent_tool", "aider-session-env"),
    ("CONTINUE_SESSION", "agent_tool", "continue-session-env"),
    ("OPENHANDS_AGENT", "agent_tool", "openhands-agent-env"),
    ("OPENHANDS_RUNTIME", "agent_tool", "openhands-runtime-env"),
    ("BROWSER_USE", "agent_tool", "browser-use-env"),
    ("STAGEHAND", "agent_tool", "stagehand-env"),
    ("GOOSE_AGENT", "agent_tool", "goose-agent-env"),
    ("ROO_CODE", "agent_tool", "roo-code-env"),
    ("WINDSURF_AGENT", "agent_tool", "windsurf-agent-env"),
)
_PARENT_PROCESS_RULES = (
    (
        "claude-code-process",
        "agent_tool",
        re.compile(r"\bclaude(?:[ -]?code)?\b", re.IGNORECASE),
    ),
    ("codex-process", "agent_tool", re.compile(r"\bcodex(?:-cli)?\b", re.IGNORECASE)),
    (
        "copilot-process",
        "agent_tool",
        re.compile(r"\bcopilot(?:-cli)?\b", re.IGNORECASE),
    ),
    ("cursor-process", "agent_tool", re.compile(r"\bcursor\b", re.IGNORECASE)),
    ("cline-process", "agent_tool", re.compile(r"\bcline\b", re.IGNORECASE)),
    ("aider-process", "agent_tool", re.compile(r"\baider\b", re.IGNORECASE)),
    ("continue-process", "agent_tool", re.compile(r"\bcontinue\b", re.IGNORECASE)),
    ("gemini-process", "agent_tool", re.compile(r"\bgemini(?:-cli)?\b", re.IGNORECASE)),
    ("auggie-process", "agent_tool", re.compile(r"\bauggie(?:-cli)?\b", re.IGNORECASE)),
    (
        "augment-process",
        "agent_tool",
        re.compile(r"\baugment(?:[ -]?agent)?\b", re.IGNORECASE),
    ),
    ("amp-process", "agent_tool", re.compile(r"\bamp(?:code)?\b", re.IGNORECASE)),
    ("opencode-process", "agent_tool", re.compile(r"\bopencode\b", re.IGNORECASE)),
    ("kilo-process", "agent_tool", re.compile(r"\bkilo(?:code)?\b", re.IGNORECASE)),
    ("qodo-process", "agent_tool", re.compile(r"\bqodo\b", re.IGNORECASE)),
    ("kiro-process", "agent_tool", re.compile(r"\bkiro\b", re.IGNORECASE)),
    ("openhands-process", "agent_tool", re.compile(r"\bopenhands\b", re.IGNORECASE)),
    (
        "browser-use-process",
        "agent_tool",
        re.compile(r"\bbrowser[- ]use\b", re.IGNORECASE),
    ),
    ("stagehand-process", "agent_tool", re.compile(r"\bstagehand\b", re.IGNORECASE)),
    ("roo-process", "agent_tool", re.compile(r"\broo(?:-code)?\b", re.IGNORECASE)),
    ("windsurf-process", "agent_tool", re.compile(r"\bwindsurf\b", re.IGNORECASE)),
    ("goose-process", "agent_tool", re.compile(r"\bgoose\b", re.IGNORECASE)),
)


def _flush_pending():
    """Wait for in-flight analytics requests before process exit."""
    with _lock:
        threads = list(_pending_threads)
    for t in threads:
        t.join(timeout=3)


atexit.register(_flush_pending)


def _is_enabled():
    return os.environ.get("CLI_HUB_NO_ANALYTICS", "").strip() not in (
        "1",
        "true",
        "yes",
    )


def _provider():
    provider = (
        os.environ.get("CLI_HUB_ANALYTICS_PROVIDER", ANALYTICS_PROVIDER).strip().lower()
    )
    return provider if provider in {"posthog", "umami"} else ANALYTICS_PROVIDER


def _analytics_dir():
    return Path.home() / ".cli-hub"


def _stdin_is_tty():
    try:
        return sys.stdin.isatty()
    except Exception:
        return False


def _read_parent_pid(pid):
    status_path = Path("/proc") / str(pid) / "status"
    try:
        for line in status_path.read_text().splitlines():
            if line.startswith("PPid:"):
                parts = line.split()
                return int(parts[1]) if len(parts) > 1 else None
    except Exception:
        return None
    return None


def _read_process_cmdline(pid):
    cmdline_path = Path("/proc") / str(pid) / "cmdline"
    try:
        raw = cmdline_path.read_bytes()
    except Exception:
        return ""
    return raw.replace(b"\x00", b" ").decode("utf-8", errors="ignore").strip()


def _parent_process_commands(max_depth=4):
    commands = []
    pid = os.getpid()
    for _ in range(max_depth):
        pid = _read_parent_pid(pid)
        if not pid or pid <= 1:
            break
        cmd = _read_process_cmdline(pid)
        if cmd:
            commands.append(cmd)
    return commands
