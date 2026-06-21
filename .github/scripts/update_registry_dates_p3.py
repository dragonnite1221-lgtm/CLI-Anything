# ruff: noqa: F403, F405, E501
from .update_registry_dates_base import *  # noqa: F403

# fmt: off
from .update_registry_dates_p1 import REPO_ROOT, get_last_modified  # noqa: E402,E501
from .update_registry_dates_p2 import get_external_date, resolve_harness_path  # noqa: E402,E501
# fmt: on


def get_cli_date(cli: dict, repo_root: Path) -> str | None:
    harness_path = resolve_harness_path(cli, repo_root)
    if harness_path:
        return get_last_modified(harness_path)
    return get_external_date(cli)


def _load_registry(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)["clis"]


def main() -> None:
    dates_path = REPO_ROOT / "docs" / "hub" / "registry-dates.json"
    all_clis = _load_registry(REPO_ROOT / "registry.json") + _load_registry(
        REPO_ROOT / "public_registry.json"
    )

    dates = {cli["name"]: get_cli_date(cli, REPO_ROOT) for cli in all_clis}

    with dates_path.open("w", encoding="utf-8") as f:
        json.dump(dates, f, indent=2)

    print(f"Updated dates for {len(dates)} CLI entries")
