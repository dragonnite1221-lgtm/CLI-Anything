# ruff: noqa: F403, F405, E501
from .mubu_probe_base import *  # noqa: F403


def candidate_appdata_roots(
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    mount_root: Path = Path("/mnt/c/Users"),
) -> list[Path]:
    env = env or os.environ
    home = home or Path.home()
    candidates: list[Path] = []

    def add(path: str | Path | None) -> None:
        if not path:
            return
        candidate = Path(path).expanduser()
        if candidate not in candidates:
            candidates.append(candidate)

    add(env.get("APPDATA"))
    userprofile = env.get("USERPROFILE")
    if userprofile:
        add(Path(userprofile) / "AppData" / "Roaming")

    for username in (home.name, env.get("USER")):
        if username:
            add(mount_root / username / "AppData" / "Roaming")

    if mount_root.exists():
        for child in sorted(mount_root.iterdir()):
            if child.is_dir():
                add(child / "AppData" / "Roaming")

    return candidates
def default_mubu_data_root(
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    mount_root: Path = Path("/mnt/c/Users"),
) -> Path:
    env = env or os.environ
    home = home or Path.home()
    for candidate in candidate_appdata_roots(env=env, home=home, mount_root=mount_root):
        if candidate.exists():
            return candidate / "Mubu" / "mubu_app_data" / "mubu_data"
    return home / ".config" / "mubu" / "mubu_data"
DEFAULT_MUBU_DATA_ROOT = Path(os.environ.get("MUBU_DATA_ROOT", str(default_mubu_data_root())))
DEFAULT_BACKUP_ROOT = Path(os.environ.get("MUBU_BACKUP_ROOT", str(DEFAULT_MUBU_DATA_ROOT / "backup")))
DEFAULT_LOG_ROOT = Path(os.environ.get("MUBU_LOG_ROOT", str(DEFAULT_MUBU_DATA_ROOT / "log")))
DEFAULT_STORAGE_ROOT = Path(os.environ.get("MUBU_STORAGE_ROOT", str(DEFAULT_MUBU_DATA_ROOT / ".storage")))
DEFAULT_API_HOST = os.environ.get("MUBU_API_HOST", "https://api2.mubu.com")
DEFAULT_PLATFORM = os.environ.get("MUBU_PLATFORM", "windows")
DEFAULT_PLATFORM_VERSION = os.environ.get("MUBU_PLATFORM_VERSION", "10.0.26100")
TAG_RE = re.compile(r"<[^>]+>")
ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")
TIMESTAMP_RE = re.compile(r"^\[(?P<timestamp>[^\]]+)\]")
NET_REQUEST_RE = re.compile(r"Net request \d+ (?P<payload>\{.*\})$")
STORE_SET_RE = re.compile(r"Store set start (?P<doc_id>\S+) (?P<payload>\{.*\})$")
ANCHOR_RE = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<label>.*?)</a>", re.IGNORECASE | re.DOTALL)
TOKEN_ATTR_RE = re.compile(r'data-token="(?P<token>[^"]+)"')
HREF_DOC_RE = re.compile(r'href="https://mubu\.com/doc(?P<token>[^"?#/]+)"', re.IGNORECASE)
NODE_ID_ALPHABET = string.ascii_letters + string.digits
DAILY_TITLE_PATTERNS = (
    re.compile(r"^\d{2}\.\d{1,2}\.\d{1,2}(?:-\d{1,2}(?:\.\d{1,2})?)?$"),
    re.compile(r"^\d{4}[./-]\d{1,2}[./-]\d{1,2}$"),
    re.compile(r"^\d{4}年\d{1,2}月\d{1,2}日$"),
    re.compile(r"^\d{1,2}[./-]\d{1,2}$"),
    re.compile(r"^\d{1,2}月\d{1,2}日$"),
)
DEFAULT_DAILY_EXCLUDE_KEYWORDS = ("模板", "template")
DEFAULT_DAILY_FOLDER_KEYWORDS = ("daily", "diary", "journal", "日记", "日志", "每日", "每天", "日常")
def configured_daily_folder_ref(env: Mapping[str, str] | None = None) -> str | None:
    env = env or os.environ
    value = env.get("MUBU_DAILY_FOLDER", "")
    if not isinstance(value, str):
        return None
    resolved = value.strip()
    return resolved or None
def resolve_daily_folder_ref(
    folder_ref: str | None,
    env: Mapping[str, str] | None = None,
) -> str:
    value = (folder_ref or "").strip()
    if value:
        return value
    configured = configured_daily_folder_ref(env=env)
    if configured:
        return configured
    raise RuntimeError(
        "daily folder reference required; pass <folder_ref> explicitly "
        "or set MUBU_DAILY_FOLDER"
    )
def extract_plain_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                parts.append(extract_plain_text(item.get("text", "")))
            else:
                parts.append(extract_plain_text(item))
        return "".join(parts).strip()
    if isinstance(value, dict):
        if "text" in value:
            return extract_plain_text(value.get("text"))
        return ""

    text = str(value)
    text = html.unescape(text)
    text = TAG_RE.sub("", text)
    text = ZERO_WIDTH_RE.sub("", text)
    return " ".join(text.split()).strip()
def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(errors="replace"))
