# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403
from .session_p0 import _empty_session_data  # noqa: F401,E501


class SessionMixin0:
    """Manages CLI session state with undo/redo support.

    Session file is stored at ~/.cli-anything-sbox/session.json by default.

    Tracks:
    - Current project path
    - Current scene path
    - Operation history (undo/redo stacks)
    - Modified flag
    """
    def __init__( self, session_path: Optional[str] = None ) -> None:
        """Initialize or load an existing session.

        Args:
            session_path: Path to the session JSON file.
                          Defaults to ~/.cli-anything-sbox/session.json
        """
        self._session_path: str = session_path or _DEFAULT_SESSION_FILE
        self._data: Dict[str, Any] = _empty_session_data()

        if os.path.isfile( self._session_path ):
            self.load()
    def load( self ) -> None:
        """Load session from disk.

        If the file does not exist or is malformed, resets to empty state. A
        malformed file is preserved as ``<path>.corrupt`` so the user's undo
        history is not silently destroyed.
        """
        try:
            with open( self._session_path, "r", encoding="utf-8" ) as f:
                raw = json.load( f )
            if isinstance( raw, dict ):
                merged = _empty_session_data()
                merged.update( raw )
                self._data = merged
            else:
                self._data = _empty_session_data()
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            # Preserve the malformed file before resetting so the user can
            # recover state if needed; emit a stderr warning so the reset is
            # not silent. Use a timestamp suffix so a second corruption does
            # not silently overwrite the first preserved copy.
            backup = f"{self._session_path}.corrupt.{int( time.time() )}"
            preserved = False
            try:
                if os.path.isfile( self._session_path ):
                    os.replace( self._session_path, backup )
                    preserved = True
            except OSError as backup_exc:
                # Couldn't move the file - still warn the user that the
                # session is being reset, just note the preservation failed.
                try:
                    sys.stderr.write(
                        f"warning: session file at {self._session_path} could not be "
                        f"read ({exc}) and preservation failed ({backup_exc}); "
                        f"resetting to empty state\n"
                    )
                except (OSError, ValueError):
                    pass
            else:
                try:
                    location = backup if preserved else self._session_path
                    sys.stderr.write(
                        f"warning: session file at {self._session_path} could not be read "
                        f"({exc}); preserved as {location} and reset to empty state\n"
                    )
                except (OSError, ValueError):
                    pass
            self._data = _empty_session_data()
    def save( self ) -> None:
        """Save session to disk.

        Creates parent directories if needed. Writes atomically by
        writing to a temporary file first, then renaming.
        """
        self._data["updated_at"] = time.time()

        session_dir = os.path.dirname( self._session_path )
        os.makedirs( session_dir, exist_ok=True )

        tmp_path = self._session_path + ".tmp"
        try:
            with open( tmp_path, "w", encoding="utf-8" ) as f:
                json.dump( self._data, f, indent=2, ensure_ascii=False )
                f.write( "\n" )
                f.flush()
                os.fsync( f.fileno() )

            # Atomic rename (on Windows, need to remove target first)
            if os.path.exists( self._session_path ):
                os.replace( tmp_path, self._session_path )
            else:
                os.rename( tmp_path, self._session_path )
        except OSError:
            # Clean up temp file on failure
            if os.path.exists( tmp_path ):
                try:
                    os.remove( tmp_path )
                except OSError:
                    pass
            raise
    def set_project( self, sbproj_path: str ) -> None:
        """Set the active project.

        Args:
            sbproj_path: Path to the .sbproj file.
        """
        self._data["project_path"] = os.path.abspath( sbproj_path )
        self._data["modified"] = True
        self.save()
    def set_scene( self, scene_path: str ) -> None:
        """Set the active scene.

        Args:
            scene_path: Path to the .scene file.
        """
        self._data["scene_path"] = os.path.abspath( scene_path )
        self._data["modified"] = True
        self.save()
