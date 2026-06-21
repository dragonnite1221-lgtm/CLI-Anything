# ruff: noqa: F403, F405, E501
from ._test_cli_entrypoint_base import *  # noqa: F403


def detect_daily_folder_ref() -> str | None:
    if not HAS_LOCAL_DATA:
        return None

    metas = load_document_metas(DEFAULT_STORAGE_ROOT)
    folders = load_folders(DEFAULT_STORAGE_ROOT)
    _, folder_paths = build_folder_indexes(folders)
    docs_by_folder: dict[str, list[dict[str, object]]] = {}
    for meta in metas:
        folder_id = meta.get("folder_id")
        if isinstance(folder_id, str):
            docs_by_folder.setdefault(folder_id, []).append(meta)

    best_path: str | None = None
    best_score = -1
    for folder in folders:
        folder_id = folder.get("folder_id")
        if not isinstance(folder_id, str):
            continue
        _, candidates = choose_current_daily_document(docs_by_folder.get(folder_id, []))
        if not candidates:
            continue
        folder_path = folder_paths.get(folder_id, "")
        if not folder_path:
            continue
        score = max(
            max(item.get("updated_at") or 0, item.get("created_at") or 0)
            for item in candidates
        )
        if score > best_score:
            best_score = score
            best_path = folder_path
    return best_path


def resolve_cli() -> list[str]:
    installed = shutil.which("cli-anything-mubu")
    if installed:
        return [installed]
    return [sys.executable, "-m", "cli_anything.mubu"]
