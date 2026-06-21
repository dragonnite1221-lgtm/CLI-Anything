# ruff: noqa: F403, F405, E501
from .update_registry_dates_base import *  # noqa: F403


REPO_ROOT = Path(__file__).resolve().parents[2]
USER_AGENT = "CLI-Anything registry date updater"
GITHUB_REPO_RE = re.compile(
    r"https://github\.com/([^/]+/[^/#?]+?)(?:\.git)?(?:[/?#].*)?$"
)
GIT_URL_RE = re.compile(r"https://github\.com/[^\s#]+")
SUBDIRECTORY_RE = re.compile(r"#subdirectory=([^\s]+)")


def _fetch_json(url: str) -> dict | None:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _fetch_last_modified(url: str) -> str | None:
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT}, method="HEAD"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            last_modified = resp.headers.get("Last-Modified")
            if not last_modified:
                return None
            return (
                parsedate_to_datetime(last_modified)
                .astimezone(timezone.utc)
                .strftime("%Y-%m-%d")
            )
    except Exception:
        return None


def _git_log_timestamp(
    target_path: Path, excluded_globs: tuple[str, ...] = ()
) -> int | None:
    try:
        relative_target = target_path.relative_to(REPO_ROOT).as_posix()
        cmd = ["git", "log", "-1", "--format=%ct", "--", relative_target]
        cmd.extend(f":(exclude,glob){pattern}" for pattern in excluded_globs)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_ROOT,
        )
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def get_last_modified(target_path: Path) -> str | None:
    """Get the most recent git commit date for CLI-specific files in a repo path."""
    relative_target = target_path.relative_to(REPO_ROOT).as_posix()
    shared_file_globs = (
        f"{relative_target}/cli_anything/**/utils/repl_skin.py",
        f"{relative_target}/cli_anything/**/skills/SKILL.md",
        f"{relative_target}/cli_anything/**/SKILL.md",
    )

    timestamp = _git_log_timestamp(target_path, excluded_globs=shared_file_globs)
    if timestamp is None:
        timestamp = _git_log_timestamp(target_path)
    if timestamp is None:
        return None

    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")
    except (OverflowError, OSError, ValueError):
        return None


def get_github_repo_date(source_url: str) -> str | None:
    """Get the last push date from a GitHub repo via the API."""
    match = GITHUB_REPO_RE.match(source_url)
    if not match:
        return None
    repo_slug = match.group(1)
    data = _fetch_json(f"https://api.github.com/repos/{repo_slug}")
    if not data:
        return None
    pushed_at = data.get("pushed_at")
    return pushed_at[:10] if pushed_at else None


def _extract_pypi_package(install_cmd: str) -> str | None:
    if not install_cmd:
        return None
    try:
        tokens = shlex.split(install_cmd)
    except ValueError:
        return None

    if not tokens:
        return None

    install_index = None
    if tokens[:3] == ["python3", "-m", "pip"]:
        install_index = 3
    elif tokens[0] in {"pip", "pip3"}:
        install_index = 1

    if (
        install_index is None
        or install_index >= len(tokens)
        or tokens[install_index] != "install"
    ):
        return None

    for token in tokens[install_index + 1 :]:
        if token.startswith("-"):
            continue
        if "://" in token or token.startswith("git+"):
            return None
        return token
    return None
