# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403
from .session_p0 import _empty_session_data  # noqa: F401,E501


class SessionMixin2:
    def redo( self ) -> Optional[Dict[str, Any]]:
        """Redo the last undone operation.

        Returns:
            Dict describing what was redone (the operation entry), or None
            if the redo stack is empty.
        """
        redo_stack: List[Dict[str, Any]] = self._data["redo_stack"]
        if not redo_stack:
            return None

        entry = redo_stack.pop()
        self._data["undo_stack"].append( copy.deepcopy( entry ) )
        self._data["modified"] = True
        self.save()

        return {
            "redone": True,
            "op_type": entry["op_type"],
            "description": entry["description"],
            "file_path": entry.get( "file_path" ),
            "before_state": entry.get( "before_state" ),
            "after_state": entry.get( "after_state" ),
        }
    def get_status( self ) -> Dict[str, Any]:
        """Return a dict with current session status.

        Returns:
            Dict with keys: project_path, scene_path, modified,
            undo_count, redo_count, created_at, updated_at.
        """
        return {
            "project_path": self._data.get( "project_path" ),
            "scene_path": self._data.get( "scene_path" ),
            "modified": self._data.get( "modified", False ),
            "undo_count": len( self._data.get( "undo_stack", [] ) ),
            "redo_count": len( self._data.get( "redo_stack", [] ) ),
            "created_at": self._data.get( "created_at" ),
            "updated_at": self._data.get( "updated_at" ),
            "session_file": self._session_path,
        }
    def clear( self ) -> None:
        """Clear session state and save to disk."""
        self._data = _empty_session_data()
        self.save()
    @property
    def project_path( self ) -> Optional[str]:
        """Current project .sbproj path."""
        return self._data.get( "project_path" )
    @property
    def scene_path( self ) -> Optional[str]:
        """Current scene path."""
        return self._data.get( "scene_path" )
    @property
    def is_modified( self ) -> bool:
        """Whether there are unsaved changes."""
        return bool( self._data.get( "modified", False ) )
