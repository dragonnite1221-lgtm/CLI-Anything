# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403
from .session_p0 import _locked_save_json  # noqa: F401,E501


class SessionMixin1:
    def save_project(self, path: Optional[str] = None) -> str:
        """Save the project. Returns the path saved to."""
        if self.data is None:
            raise RuntimeError("No project is open")
        save_path = path or self.project_path
        if not save_path:
            raise RuntimeError("No save path specified and project has no path")
        save_path = os.path.abspath(save_path)
        _locked_save_json(save_path, self.data, indent=2, sort_keys=False)
        self.project_path = save_path
        self._modified = False
        return save_path
    def save_session_state(self) -> str:
        """Persist session metadata to disk."""
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        state = {
            "session_id": self.session_id,
            "project_path": self.project_path,
            "modified": self._modified,
            "undo_depth": len(self._undo_stack),
            "redo_depth": len(self._redo_stack),
            "metadata": self._metadata,
            "timestamp": time.time(),
        }
        path = SESSION_DIR / f"{self.session_id}.json"
        _locked_save_json(path, state, indent=2, sort_keys=True)
        return str(path)
    @classmethod
    def load_session_state(cls, session_id: str) -> Optional[dict]:
        """Load session metadata from disk."""
        path = SESSION_DIR / f"{session_id}.json"
        if not path.is_file():
            return None
        with open(path) as f:
            return json.load(f)
    @classmethod
    def list_sessions(cls) -> list[dict]:
        """List all saved sessions."""
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        sessions = []
        for p in SESSION_DIR.glob("*.json"):
            try:
                with open(p) as f:
                    sessions.append(json.load(f))
            except (json.JSONDecodeError, OSError):
                continue
        sessions.sort(key=lambda s: s.get("timestamp", 0), reverse=True)
        return sessions
    def status(self) -> dict:
        """Get current session status."""
        result = {
            "session_id": self.session_id,
            "project_open": self.is_open,
            "project_path": self.project_path,
            "modified": self._modified,
            "undo_available": len(self._undo_stack),
            "redo_available": len(self._redo_stack),
        }
        if self.is_open:
            editor = self.editor
            result["zoom_region_count"] = len(editor.get("zoomRegions", []))
            result["speed_region_count"] = len(editor.get("speedRegions", []))
            result["trim_region_count"] = len(editor.get("trimRegions", []))
            result["annotation_count"] = len(editor.get("annotationRegions", []))
            result["aspect_ratio"] = editor.get("aspectRatio", "16:9")
            result["background"] = editor.get("wallpaper", "gradient_dark")
            result["padding"] = editor.get("padding", 50)
        return result
