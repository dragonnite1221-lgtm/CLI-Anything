# ruff: noqa: F403, F405, E501
from .catalog_base import *  # noqa: F403

# fmt: off
from .catalog_p1 import _default_library, _require_sqlite, local_api_scope  # noqa: E402,E501
from .catalog_p2 import get_search  # noqa: E402,E501
# fmt: on


def search_items(
    runtime: RuntimeContext,
    ref: str | int | None,
    session: dict[str, Any] | None = None,
) -> Any:
    if not runtime.local_api_available:
        raise RuntimeError(
            "search items requires the Zotero Local API to be running and enabled"
        )
    search = get_search(runtime, ref, session=session)
    scope = local_api_scope(runtime, int(search["libraryID"]))
    return zotero_http.local_api_get_json(
        runtime.environment.port,
        f"{scope}/searches/{search['key']}/items",
        params={"format": "json"},
    )


def list_tags(
    runtime: RuntimeContext, session: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return zotero_sqlite.fetch_tags(
        _require_sqlite(runtime), library_id=_default_library(runtime, session)
    )


def tag_items(
    runtime: RuntimeContext, tag_ref: str | int, session: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return zotero_sqlite.fetch_tag_items(
        _require_sqlite(runtime), tag_ref, library_id=_default_library(runtime, session)
    )


def list_styles(runtime: RuntimeContext) -> list[dict[str, Any]]:
    styles_dir = runtime.environment.styles_dir
    if not styles_dir.exists():
        return []
    styles: list[dict[str, Any]] = []
    for path in sorted(styles_dir.glob("*.csl")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            styles.append(
                {"path": str(path), "id": None, "title": path.stem, "valid": False}
            )
            continue
        style_id = None
        title = None
        for element in root.iter():
            tag = element.tag.split("}", 1)[-1]
            if tag == "id" and style_id is None:
                style_id = (element.text or "").strip() or None
            if tag == "title" and title is None:
                title = (element.text or "").strip() or None
        styles.append(
            {
                "path": str(path),
                "id": style_id,
                "title": title or path.stem,
                "valid": True,
            }
        )
    return styles
