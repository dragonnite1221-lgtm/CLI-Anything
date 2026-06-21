# ruff: noqa: F403, F405, E501
from .zotero_paths_base import *  # noqa: F403

# fmt: off
from .zotero_paths_p1 import _read_pref_file  # noqa: E402,E501
# fmt: on


def ensure_local_api_enabled(profile_dir: Path | None) -> Optional[Path]:
    if profile_dir is None:
        return None
    user_js = profile_dir / "user.js"
    existing = _read_pref_file(user_js)
    line = 'user_pref("extensions.zotero.httpServer.localAPI.enabled", true);'
    if line not in existing:
        content = existing.rstrip()
        if content:
            content += "\n"
        content += line + "\n"
        user_js.write_text(content, encoding="utf-8")
    return user_js
