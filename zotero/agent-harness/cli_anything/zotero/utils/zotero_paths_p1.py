# ruff: noqa: F403, F405, E501
from .zotero_paths_base import *  # noqa: F403


@dataclass
class ZoteroEnvironment:
    executable: Optional[Path]
    executable_exists: bool
    install_dir: Optional[Path]
    version: str
    profile_root: Path
    profile_dir: Optional[Path]
    data_dir: Path
    data_dir_exists: bool
    sqlite_path: Path
    sqlite_exists: bool
    styles_dir: Path
    styles_exists: bool
    storage_dir: Path
    storage_exists: bool
    translators_dir: Path
    translators_exists: bool
    port: int
    local_api_enabled_configured: bool

    def to_dict(self) -> dict:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Path):
                data[key] = str(value)
        return data


def candidate_profile_roots(
    env: Mapping[str, str] | None = None, home: Path | None = None
) -> list[Path]:
    env = env or os.environ
    home = home or Path.home()
    candidates: list[Path] = []

    def add(path: Path | str | None) -> None:
        if not path:
            return
        candidate = Path(path).expanduser()
        if candidate not in candidates:
            candidates.append(candidate)

    appdata = env.get("APPDATA")
    if appdata:
        add(Path(appdata) / "Zotero" / "Zotero")
    add(home / "AppData" / "Roaming" / "Zotero" / "Zotero")
    add(home / "Library" / "Application Support" / "Zotero")
    add(home / ".zotero" / "zotero")
    return candidates


def find_profile_root(
    explicit_profile_dir: str | None = None, env: Mapping[str, str] | None = None
) -> Path:
    env = env or os.environ
    if explicit_profile_dir:
        explicit = Path(explicit_profile_dir).expanduser()
        if explicit.name == "profiles.ini":
            return explicit.parent
        if (explicit / "profiles.ini").exists():
            return explicit
        if (explicit.parent / "profiles.ini").exists():
            return explicit.parent
        return explicit

    env_profile = env.get("ZOTERO_PROFILE_DIR", "").strip()
    if env_profile:
        return find_profile_root(env_profile, env=env)

    for candidate in candidate_profile_roots(env=env):
        if (candidate / "profiles.ini").exists():
            return candidate
    return candidate_profile_roots(env=env)[0]


def read_profiles_ini(profile_root: Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    path = profile_root / "profiles.ini"
    if path.exists():
        config.read(path, encoding="utf-8")
    return config


def _profile_path_from_section(
    profile_root: Path, config: configparser.ConfigParser, section: str
) -> Optional[Path]:
    path_value = config.get(section, "Path", fallback="").strip()
    if not path_value:
        return None
    is_relative = config.get(section, "IsRelative", fallback="1").strip() == "1"
    return (
        (profile_root / path_value).resolve()
        if is_relative
        else Path(path_value).expanduser()
    )


def find_active_profile(profile_root: Path) -> Optional[Path]:
    config = read_profiles_ini(profile_root)
    ordered_sections = [
        section
        for section in config.sections()
        if section.lower().startswith("profile")
    ]
    for section in ordered_sections:
        if config.get(section, "Default", fallback="0").strip() != "1":
            continue
        return _profile_path_from_section(profile_root, config, section)
    for section in ordered_sections:
        candidate = _profile_path_from_section(profile_root, config, section)
        if candidate is not None:
            return candidate
    return None


def _read_pref_file(path: Path) -> str:
    if not path.exists():
        return ""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def _decode_pref_string(raw: str) -> str:
    return raw.replace("\\\\", "\\").replace('\\"', '"')


def read_pref(profile_dir: Path | None, pref_name: str) -> Optional[str]:
    if profile_dir is None:
        return None
    pattern = re.compile(rf'user_pref\("{re.escape(pref_name)}",\s*(.+?)\);')
    for filename in ("user.js", "prefs.js"):
        text = _read_pref_file(profile_dir / filename)
        for line in text.splitlines():
            match = pattern.search(line)
            if not match:
                continue
            raw = match.group(1).strip()
            if raw in {"true", "false"}:
                return raw
            if raw.startswith('"') and raw.endswith('"'):
                return _decode_pref_string(raw[1:-1])
            return raw
    return None
