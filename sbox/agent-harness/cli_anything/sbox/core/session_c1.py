# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class SessionMixin1:
    def snapshot(
        self,
        op_type: str,
        description: str,
        before_state: Optional[Any] = None,
        after_state: Optional[Any] = None,
        file_path: Optional[str] = None,
    ) -> None:
        """Alias for ``record_operation`` matching HARNESS naming convention.

        Records a snapshot of an operation onto the undo stack. See
        :meth:`record_operation` for full documentation.
        """
        self.record_operation(
            op_type=op_type,
            description=description,
            before_state=before_state,
            after_state=after_state,
            file_path=file_path,
        )
    def record_operation(
        self,
        op_type: str,
        description: str,
        before_state: Optional[Any] = None,
        after_state: Optional[Any] = None,
        file_path: Optional[str] = None,
    ) -> None:
        """Record an operation for undo/redo.

        Args:
            op_type: One of 'scene_modify', 'project_modify', 'input_modify',
                     'collision_modify', 'file_create', 'codegen'.
            description: Human-readable description of what was done.
            before_state: Serializable state before the operation (for undo).
            after_state: Serializable state after the operation (for redo).
            file_path: The file that was modified.

        Raises:
            ValueError: If op_type is not a recognised operation type.
        """
        if op_type not in VALID_OP_TYPES:
            raise ValueError(
                f"Invalid op_type '{op_type}'. "
                f"Must be one of: {', '.join( sorted( VALID_OP_TYPES ) )}"
            )

        entry: Dict[str, Any] = {
            "op_type": op_type,
            "description": description,
            "timestamp": time.time(),
            "file_path": os.path.abspath( file_path ) if file_path else None,
            "before_state": copy.deepcopy( before_state ),
            "after_state": copy.deepcopy( after_state ),
        }

        self._data["undo_stack"].append( entry )
        # Recording a new operation clears the redo stack
        self._data["redo_stack"].clear()
        self._data["modified"] = True
        self.save()
    def undo( self ) -> Optional[Dict[str, Any]]:
        """Undo the last operation.

        If the operation has a before_state and file_path, the caller is
        responsible for actually restoring the file contents. This method
        manages the stack bookkeeping.

        Returns:
            Dict describing what was undone (the operation entry), or None
            if the undo stack is empty.
        """
        undo_stack: List[Dict[str, Any]] = self._data["undo_stack"]
        if not undo_stack:
            return None

        entry = undo_stack.pop()
        self._data["redo_stack"].append( copy.deepcopy( entry ) )
        self._data["modified"] = True
        self.save()

        return {
            "undone": True,
            "op_type": entry["op_type"],
            "description": entry["description"],
            "file_path": entry.get( "file_path" ),
            "before_state": entry.get( "before_state" ),
            "after_state": entry.get( "after_state" ),
        }
