# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class SessionMixin1:
    def open_project(self, path: str) -> None:
        """Open an existing MLT project file."""
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Project file not found: {path}")
        self.root = mlt_xml.parse_mlt(path)
        self._resolve_refs()
        self.project_path = path
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._modified = False

    def save_project(self, path: Optional[str] = None) -> str:
        """Save the project. Returns the path saved to."""
        if self.root is None:
            raise RuntimeError("No project is open")
        save_path = path or self.project_path
        if not save_path:
            raise RuntimeError("No save path specified and project has no path")
        save_path = os.path.abspath(save_path)
        mlt_xml.write_mlt(self.root, save_path)
        self.project_path = save_path
        self._modified = False
        return save_path

    def get_profile(self) -> dict:
        """Get the project's video profile as a dict."""
        if self.root is None:
            raise RuntimeError("No project is open")
        prof = self.root.find("profile")
        if prof is None:
            return {}
        return dict(prof.attrib)

    def get_main_tractor(self) -> ET.Element:
        """Get the main timeline tractor."""
        if self.root is None:
            raise RuntimeError("No project is open")
        tractor = mlt_xml.get_main_tractor(self.root)
        if tractor is None:
            raise RuntimeError("No main tractor found in project")
        return tractor

    def save_session_state(self) -> str:
        """Persist session metadata to disk (not the project, just session info)."""
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
            profile = self.get_profile()
            result["profile"] = profile
            try:
                tractor = self.get_main_tractor()
                tracks = mlt_xml.get_tractor_tracks(tractor)
                result["track_count"] = len(tracks)
            except RuntimeError:
                result["track_count"] = 0
        return result
