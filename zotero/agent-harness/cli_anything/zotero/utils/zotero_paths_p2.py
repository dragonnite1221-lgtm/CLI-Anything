# ruff: noqa: F403, F405, E501
from .zotero_paths_base import *  # noqa: F403

# fmt: off
from .zotero_paths_p1 import ZoteroEnvironment, _read_pref_file, find_active_profile, find_profile_root, read_pref  # noqa: E402,E501
# fmt: on


def find_data_dir(
    profile_dir: Path | None,
    explicit_data_dir: str | None = None,
    env: Mapping[str, str] | None = None,
) -> Path:
    env = env or os.environ
    if explicit_data_dir:
        return Path(explicit_data_dir).expanduser()

    env_data_dir = env.get("ZOTERO_DATA_DIR", "").strip()
    if env_data_dir:
        return Path(env_data_dir).expanduser()

    if profile_dir is not None:
        use_data_dir = read_pref(profile_dir, USE_DATA_DIR_PREF)
        pref_data_dir = read_pref(profile_dir, DATA_DIR_PREF)
        if use_data_dir == "true" and pref_data_dir:
            candidate = Path(pref_data_dir).expanduser()
            if candidate.exists():
                return candidate

    return Path.home() / "Zotero"


def find_executable(
    explicit_executable: str | None = None, env: Mapping[str, str] | None = None
) -> Optional[Path]:
    env = env or os.environ
    if explicit_executable:
        return Path(explicit_executable).expanduser()

    env_executable = env.get("ZOTERO_EXECUTABLE", "").strip()
    if env_executable:
        return Path(env_executable).expanduser()

    for name in ("zotero", "zotero.exe"):
        path = shutil.which(name)
        if path:
            return Path(path)

    candidates = [
        Path(r"C:\Program Files\Zotero\zotero.exe"),
        Path(r"C:\Program Files (x86)\Zotero\zotero.exe"),
        Path("/Applications/Zotero.app/Contents/MacOS/zotero"),
        Path("/usr/lib/zotero/zotero"),
        Path("/usr/local/bin/zotero"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_install_dir(executable: Optional[Path]) -> Optional[Path]:
    if executable is None:
        return None
    return executable.parent


def get_version(install_dir: Optional[Path]) -> str:
    if install_dir is None:
        return "unknown"
    candidates = [
        install_dir / "app" / "application.ini",
        install_dir / "application.ini",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        text = _read_pref_file(candidate)
        match = re.search(r"^Version=(.+)$", text, re.MULTILINE)
        if match:
            return match.group(1).strip()
    return "unknown"


def get_http_port(
    profile_dir: Path | None, env: Mapping[str, str] | None = None
) -> int:
    env = env or os.environ
    env_port = env.get("ZOTERO_HTTP_PORT", "").strip()
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            pass
    pref_port = read_pref(profile_dir, HTTP_PORT_PREF)
    if pref_port:
        try:
            return int(pref_port)
        except ValueError:
            pass
    return 23119


def is_local_api_enabled(profile_dir: Path | None) -> bool:
    return read_pref(profile_dir, LOCAL_API_PREF) == "true"


def build_environment(
    explicit_data_dir: str | None = None,
    explicit_profile_dir: str | None = None,
    explicit_executable: str | None = None,
    env: Mapping[str, str] | None = None,
) -> ZoteroEnvironment:
    env = env or os.environ
    profile_root = find_profile_root(explicit_profile_dir=explicit_profile_dir, env=env)
    env_profile_dir = env.get("ZOTERO_PROFILE_DIR", "").strip()
    explicit_or_env_profile = explicit_profile_dir or env_profile_dir or None
    profile_dir = (
        Path(explicit_or_env_profile).expanduser()
        if explicit_or_env_profile
        and (Path(explicit_or_env_profile) / "prefs.js").exists()
        else find_active_profile(profile_root)
    )
    executable = find_executable(explicit_executable=explicit_executable, env=env)
    install_dir = find_install_dir(executable)
    data_dir = find_data_dir(profile_dir, explicit_data_dir=explicit_data_dir, env=env)
    sqlite_path = data_dir / "zotero.sqlite"
    styles_dir = data_dir / "styles"
    storage_dir = data_dir / "storage"
    translators_dir = data_dir / "translators"
    return ZoteroEnvironment(
        executable=executable,
        executable_exists=bool(executable and executable.exists()),
        install_dir=install_dir,
        version=get_version(install_dir),
        profile_root=profile_root,
        profile_dir=profile_dir,
        data_dir=data_dir,
        data_dir_exists=data_dir.exists(),
        sqlite_path=sqlite_path,
        sqlite_exists=sqlite_path.exists(),
        styles_dir=styles_dir,
        styles_exists=styles_dir.exists(),
        storage_dir=storage_dir,
        storage_exists=storage_dir.exists(),
        translators_dir=translators_dir,
        translators_exists=translators_dir.exists(),
        port=get_http_port(profile_dir, env=env),
        local_api_enabled_configured=is_local_api_enabled(profile_dir),
    )
