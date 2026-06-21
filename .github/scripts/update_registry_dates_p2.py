# ruff: noqa: F403, F405, E501
from .update_registry_dates_base import *  # noqa: F403

# fmt: off
from .update_registry_dates_p1 import GIT_URL_RE, SUBDIRECTORY_RE, _extract_pypi_package, _fetch_json, _fetch_last_modified, get_github_repo_date  # noqa: E402,E501
# fmt: on


def get_pypi_date(install_cmd: str) -> str | None:
    """Get the last release date from PyPI for a pip-installable package."""
    package = _extract_pypi_package(install_cmd)
    if not package:
        return None
    data = _fetch_json(f"https://pypi.org/pypi/{package}/json")
    if not data:
        return None
    latest = data.get("info", {}).get("version")
    releases = data.get("releases", {})
    release_files = releases.get(latest or "", [])
    if not release_files:
        return None
    upload_time = release_files[0].get("upload_time") or release_files[0].get(
        "upload_time_iso_8601"
    )
    return upload_time[:10] if upload_time else None


def _extract_npm_package(cli: dict) -> str | None:
    package = cli.get("npm_package")
    if package:
        return package

    install_cmd = cli.get("install_cmd", "")
    match = re.search(r"npm install -g (\S+)", install_cmd)
    return match.group(1) if match else None


def get_npm_date(cli: dict) -> str | None:
    """Get the latest publish date from the npm registry."""
    package = _extract_npm_package(cli)
    if not package:
        return None
    encoded = urllib.parse.quote(package, safe="")
    data = _fetch_json(f"https://registry.npmjs.org/{encoded}")
    if not data:
        return None
    latest = data.get("dist-tags", {}).get("latest")
    published = data.get("time", {}).get(latest or "")
    return published[:10] if published else None


def _extract_install_subdirectory(cli: dict) -> str | None:
    install_cmd = cli.get("install_cmd") or ""
    match = SUBDIRECTORY_RE.search(install_cmd)
    return match.group(1) if match else None


def _extract_skill_subdirectory(cli: dict) -> str | None:
    skill_md = cli.get("skill_md")
    if not skill_md or skill_md.startswith("http"):
        return None
    marker = "/agent-harness/"
    if marker not in skill_md:
        return None
    return skill_md.split(marker, 1)[0] + marker.rstrip("/")


def resolve_harness_path(cli: dict, repo_root: Path) -> Path | None:
    """Resolve the on-disk harness path for an in-repo CLI entry."""
    for relative in (
        _extract_install_subdirectory(cli),
        _extract_skill_subdirectory(cli),
    ):
        if relative:
            candidate = repo_root / relative
            if candidate.exists():
                return candidate

    candidate_dirs = []
    for name in (
        cli.get("name"),
        cli.get("name", "").replace("-", "_"),
        cli.get("name", "").replace("_", "-"),
    ):
        if name and name not in candidate_dirs:
            candidate_dirs.append(name)

    for directory in candidate_dirs:
        candidate = repo_root / directory / "agent-harness"
        if candidate.exists():
            return candidate
    return None


def extract_external_source_url(cli: dict) -> str | None:
    """Best-effort source URL discovery for third-party CLIs."""
    source_url = cli.get("source_url")
    if source_url:
        return source_url

    install_cmd = cli.get("install_cmd") or ""
    git_match = GIT_URL_RE.search(install_cmd)
    if git_match:
        return git_match.group(0).removesuffix(".git")

    for field in ("homepage", "docs_url"):
        value = cli.get(field)
        if value and "github.com/" in value:
            return value
    return None


def get_external_date(cli: dict) -> str | None:
    """Get a useful update date for external/public CLIs."""
    source_url = extract_external_source_url(cli)
    if source_url:
        date = get_github_repo_date(source_url)
        if date:
            return date

    package_manager = (cli.get("package_manager") or "").lower()
    if package_manager == "npm":
        date = get_npm_date(cli)
        if date:
            return date

    date = get_pypi_date(cli.get("install_cmd", ""))
    if date:
        return date

    for field in ("homepage", "docs_url"):
        url = cli.get(field)
        if url:
            date = _fetch_last_modified(url)
            if date:
                return date
    return None
