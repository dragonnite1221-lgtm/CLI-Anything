# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class SessionMixin0:
    """Represents a stateful CLI editing session.

    Single-session architecture: there is always exactly one Session per process.
    - CLI one-shot mode: cli() creates one Session, runs one command, exits.
    - REPL mode: the REPL loop holds one Session. Running `new` or `open`
      replaces the current project inside that session — the old project is
      discarded. There is no way to have multiple concurrent sessions in one
      process, so cached node references (main_bin, main_tractor, _track_playlists,
      etc.) never become stale due to a different session's edits.

    This means global state like mlt_xml._parent_map (which tracks element
    parentage for the current tree) is inherently single-session and does not
    need per-session isolation.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self.project_path: Optional[str] = None
        self.root: Optional[ET.Element] = None
        self._undo_stack: list[bytes] = []
        self._redo_stack: list[bytes] = []
        self._modified = False
        self._metadata: dict = {}
        self.main_bin: Optional[ET.Element] = None
        self.main_tractor: Optional[ET.Element] = None
        self._track_playlists: list[ET.Element] = []
        self._bin_chains: dict[str, ET.Element] = {}
        self._timeline_insert_idx: int = 0
        self._bin_insert_idx: int = 0
        self._clip_id_counter: int = 0
        self._clip_ids: dict[str, str] = {}
        self._clip_resources: dict[str, str] = {}

    @property
    def is_open(self) -> bool:
        return self.root is not None

    @property
    def is_modified(self) -> bool:
        return self._modified

    def _snapshot(self) -> bytes:
        """Capture current state for undo."""
        if self.root is None:
            return b""
        return ET.tostring(self.root, xml_declaration=True, encoding="utf-8")

    def _push_undo(self) -> None:
        """Save current state to undo stack before a mutation."""
        snap = self._snapshot()
        if snap:
            self._undo_stack.append(snap)
            if len(self._undo_stack) > MAX_UNDO_DEPTH:
                self._undo_stack.pop(0)
            self._redo_stack.clear()

    def checkpoint(self) -> None:
        self._push_undo()
        self._modified = True

    def undo(self) -> bool:
        """Undo the last operation. Returns True if successful."""
        if not self._undo_stack:
            return False
        self._redo_stack.append(self._snapshot())
        prev = self._undo_stack.pop()
        mlt_xml._clear_parent_map()
        self.root = ET.fromstring(prev)
        mlt_xml._register_tree(self.root)
        self._resolve_refs()
        self._modified = bool(self._undo_stack)
        return True

    def redo(self) -> bool:
        """Redo the last undone operation. Returns True if successful."""
        if not self._redo_stack:
            return False
        self._undo_stack.append(self._snapshot())
        nxt = self._redo_stack.pop()
        mlt_xml._clear_parent_map()
        self.root = ET.fromstring(nxt)
        mlt_xml._register_tree(self.root)
        self._resolve_refs()
        self._modified = True
        return True

    def _resolve_refs(self) -> None:
        self.main_bin = mlt_xml.find_element_by_id(self.root, "main_bin")
        self.main_tractor = mlt_xml.get_main_tractor(self.root)
        self._track_playlists = []
        if self.main_tractor is not None:
            for track in mlt_xml.get_tractor_tracks(self.main_tractor):
                pid = track.get("producer")
                pl = mlt_xml.find_element_by_id(self.root, pid) if pid else None
                self._track_playlists.append(pl)
        self._bin_chains = {}
        self._clip_ids = {}
        self._clip_resources = {}
        self._clip_id_counter = 0
        if self.main_bin is not None:
            for entry in self.main_bin.findall("entry"):
                chain_id = entry.get("producer")
                if chain_id:
                    chain = mlt_xml.find_element_by_id(self.root, chain_id)
                    if chain is not None:
                        resource = mlt_xml.get_property(chain, "resource")
                        if resource:
                            clip_id = f"clip{self._clip_id_counter}"
                            self._clip_id_counter += 1
                            self._bin_chains[clip_id] = chain
                            self._clip_ids[clip_id] = resource
                            self._clip_resources[resource] = clip_id
        self._timeline_insert_idx = mlt_xml.find_insert_index_for_timeline_chain(
            self.root
        )
        self._bin_insert_idx = mlt_xml._find_insert_index_for_bin_chain(self.root)

    def new_project(self, profile: Optional[dict] = None) -> None:
        """Create a new blank project."""
        if profile is None:
            profile = {
                "width": "1920",
                "height": "1080",
                "frame_rate_num": "30000",
                "frame_rate_den": "1001",
                "sample_aspect_num": "1",
                "sample_aspect_den": "1",
                "display_aspect_num": "16",
                "display_aspect_den": "9",
                "progressive": "1",
                "colorspace": "709",
            }
        self.root = mlt_xml.create_blank_project(profile)
        self._resolve_refs()
        self.project_path = None
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._modified = False
