# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


def resolve_cli() -> list[str]:
    force_installed = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    installed = shutil.which("cli-anything-zotero")
    if installed:
        return [installed]
    scripts_dir = Path(sysconfig.get_path("scripts"))
    for candidate in (scripts_dir / "cli-anything-zotero.exe", scripts_dir / "cli-anything-zotero"):
        if candidate.exists():
            return [str(candidate)]
    if force_installed:
        raise RuntimeError("cli-anything-zotero not found in PATH. Install it with: py -m pip install -e .")
    return [sys.executable, "-m", "cli_anything.zotero"]


def uses_module_fallback(cli_base: list[str]) -> bool:
    return len(cli_base) >= 3 and cli_base[1] == "-m"


def choose_regular_item() -> dict | None:
    if not HAS_LOCAL_DATA:
        return None
    items = zotero_sqlite.fetch_items(ENVIRONMENT.sqlite_path, library_id=zotero_sqlite.default_library_id(ENVIRONMENT.sqlite_path), limit=50)
    for item in items:
        if item["typeName"] not in {"attachment", "note"} and item.get("title"):
            return item
    return None


def choose_item_with_attachment() -> dict | None:
    if not HAS_LOCAL_DATA:
        return None
    library_id = zotero_sqlite.default_library_id(ENVIRONMENT.sqlite_path)
    items = zotero_sqlite.fetch_items(ENVIRONMENT.sqlite_path, library_id=library_id, limit=100)
    for item in items:
        if item["typeName"] in {"attachment", "note", "annotation"}:
            continue
        attachments = zotero_sqlite.fetch_item_attachments(ENVIRONMENT.sqlite_path, item["itemID"])
        if attachments:
            return item
    return None


def choose_item_with_note() -> dict | None:
    if not HAS_LOCAL_DATA:
        return None
    library_id = zotero_sqlite.default_library_id(ENVIRONMENT.sqlite_path)
    items = zotero_sqlite.fetch_items(ENVIRONMENT.sqlite_path, library_id=library_id, limit=100)
    for item in items:
        if item["typeName"] in {"attachment", "note", "annotation"}:
            continue
        notes = zotero_sqlite.fetch_item_notes(ENVIRONMENT.sqlite_path, item["itemID"])
        if notes:
            return item
    return None


def choose_collection() -> dict | None:
    if not HAS_LOCAL_DATA:
        return None
    collections = zotero_sqlite.fetch_collections(ENVIRONMENT.sqlite_path, library_id=zotero_sqlite.default_library_id(ENVIRONMENT.sqlite_path))
    return collections[0] if collections else None


def choose_tag_name() -> str | None:
    if not HAS_LOCAL_DATA:
        return None
    tags = zotero_sqlite.fetch_tags(ENVIRONMENT.sqlite_path, library_id=zotero_sqlite.default_library_id(ENVIRONMENT.sqlite_path))
    return tags[0]["name"] if tags else None
