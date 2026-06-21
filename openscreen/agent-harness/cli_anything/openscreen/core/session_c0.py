# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class SessionMixin0:
    """Represents a stateful CLI editing session."""
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self.project_path: Optional[str] = None
        self.data: Optional[dict] = None  # The full project JSON
        self._undo_stack: list[str] = []  # Serialized JSON snapshots
        self._redo_stack: list[str] = []
        self._modified = False
        self._metadata: dict = {}
    @property
    def is_open(self) -> bool:
        return self.data is not None
    @property
    def is_modified(self) -> bool:
        return self._modified
    @property
    def editor(self) -> dict:
        """Get the editor state dict. Raises if no project open."""
        if self.data is None:
            raise RuntimeError("No project is open")
        return self.data.get("editor", {})
    def _snapshot(self) -> str:
        """Capture current state for undo."""
        if self.data is None:
            return ""
        return json.dumps(self.data)
    def _push_undo(self) -> None:
        """Save current state to undo stack before a mutation."""
        snap = self._snapshot()
        if snap:
            self._undo_stack.append(snap)
            if len(self._undo_stack) > MAX_UNDO_DEPTH:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
    def checkpoint(self) -> None:
        """Create a checkpoint before performing a mutation.
        Call this before any operation that changes the project.
        """
        self._push_undo()
        self._modified = True
    def undo(self) -> bool:
        """Undo the last operation. Returns True if successful."""
        if not self._undo_stack:
            return False
        self._redo_stack.append(self._snapshot())
        prev = self._undo_stack.pop()
        self.data = json.loads(prev)
        self._modified = bool(self._undo_stack)
        return True
    def redo(self) -> bool:
        """Redo the last undone operation. Returns True if successful."""
        if not self._redo_stack:
            return False
        self._undo_stack.append(self._snapshot())
        nxt = self._redo_stack.pop()
        self.data = json.loads(nxt)
        self._modified = True
        return True
    def new_project(self, video_path: Optional[str] = None) -> None:
        """Create a new blank project."""
        self.data = {
            "version": 2,
            "editor": {
                "wallpaper": "gradient_dark",
                "shadowIntensity": 0,
                "showBlur": False,
                "motionBlurAmount": 0,
                "borderRadius": 12,
                "padding": 50,
                "cropRegion": {"x": 0, "y": 0, "width": 1, "height": 1},
                "zoomRegions": [],
                "trimRegions": [],
                "speedRegions": [],
                "annotationRegions": [],
                "aspectRatio": "16:9",
                "webcamLayoutPreset": "picture-in-picture",
                "webcamMaskShape": "rectangle",
                "webcamPosition": None,
                "exportQuality": "good",
                "exportFormat": "mp4",
                "gifFrameRate": 15,
                "gifLoop": True,
                "gifSizePreset": "medium",
            },
        }
        if video_path:
            self.data["media"] = {
                "screenVideoPath": os.path.abspath(video_path),
            }
        self.project_path = None
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._modified = False
    def open_project(self, path: str) -> None:
        """Open an existing .openscreen project file."""
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Project file not found: {path}")

        with open(path) as f:
            data = json.load(f)

        if not isinstance(data, dict) or "editor" not in data:
            raise ValueError(f"Invalid Openscreen project file: {path}")

        self.data = data
        self.project_path = path
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._modified = False
