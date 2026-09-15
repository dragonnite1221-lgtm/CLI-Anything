"""Guard against writing through a symlink that escapes an output directory.

Preview bundle and live-session directories can originate from untrusted
input (a shared bundle archive, an imported session). If one plants a
symlink at the well-known output filename (preview.html / live.html),
naively following it on write would let it clobber an arbitrary file the
current user can write, anywhere on disk.
"""

from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import IO


def safe_output_file(output_path: str) -> Path:
    """Resolve `output_path`, rejecting a pre-existing symlink whose real
    target falls outside the directory the caller asked to write into.

    Resolves via os.path.realpath and checks that the real target is the
    intended (non-symlink-following) directory itself or somewhere beneath
    it -- e.g. preview.html -> rendered/preview.html is a valid, contained
    redirect, not an escape. This is an early, friendly check only: the
    file may not exist yet, so there is nothing to resolve, and a symlink
    can still be planted afterward. Callers must still open the final path
    with `open_safe_output` to close that race.
    """
    raw = Path(output_path).expanduser()
    intended_dir = raw.parent.resolve()
    if raw.is_symlink():
        real_target = Path(os.path.realpath(raw))
        if real_target != intended_dir and intended_dir not in real_target.parents:
            raise ValueError(
                "Refusing to write preview output through a symlink that escapes "
                f"the intended output directory: {raw} -> {real_target}"
            )
        return real_target
    return intended_dir / raw.name


# os.O_NOFOLLOW/O_DIRECTORY and os.open(dir_fd=...) don't exist on native
# Windows (they do under WSL/Cygwin, where os.name == "posix"). Where
# they're missing, fall back to an immediately-before-open check: not
# atomic, so a narrower TOCTOU window remains on that platform
# specifically, but it is still checked, and creating filesystem symlinks
# on Windows normally requires elevated privileges or Developer Mode.
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_SUPPORTS_DIR_FD = bool(_NOFOLLOW and _O_DIRECTORY) and os.open in os.supports_dir_fd

# O_PATH (Linux) opens a directory purely for path resolution -- as the
# dir_fd for a later openat() -- without requiring read permission on it,
# unlike plain O_RDONLY. Without it (macOS, other POSIX), a write+execute
# but non-readable "dropbox" directory (mode 0333) that plain open(path,
# "w") could create files in would make this dir_fd open fail with EACCES;
# O_PATH avoids that regression on the platform where it's available.
_DIR_OPEN_FLAGS = getattr(os, "O_PATH", os.O_RDONLY) | _O_DIRECTORY

# Match plain open(path, "w")'s default create mode (0o666, narrowed by the
# process umask). os.open()'s own default is 0o777, which -- under a
# typical 022 umask -- would make newly created preview files executable.
_CREATE_MODE = 0o666


def _reraise_symlink_as_value_error(path: Path, error: OSError) -> None:
    if error.errno == errno.ELOOP:
        raise ValueError(f"Refusing to write preview output through a symlink: {path}") from error
    raise error


def open_safe_output(path: Path) -> IO[str]:
    """Open `path` for text writing, refusing to follow a symlink planted at
    that exact location -- or, where supported, anywhere in its parent
    chain -- after `safe_output_file` already checked it.

    `safe_output_file` only catches a symlink that already exists when it
    runs; the caller (HTML generation) can take a while after that check
    before it actually writes. A bare O_NOFOLLOW open only guards the final
    path component: another process could still swap out the *containing*
    directory itself for a symlink, and a plain os.open(full_path, ...)
    would re-resolve and follow it. Where dir_fd is supported, this opens
    the parent directory by descriptor first and creates the leaf relative
    to that descriptor with O_NOFOLLOW -- once the directory is open, its
    fd stays pinned to that inode no matter what later gets linked at its
    path, so a swap happening after this call starts can't redirect the
    leaf creation. A swap completed *before* this call starts (i.e.
    sometime during the HTML generation that runs between
    `safe_output_file`'s check and this open) is not covered: closing that
    fully would mean opening the directory once up front and holding it for
    the whole render, which would need a larger restructuring of
    render_html/render_live_html than this fix takes on. That residual
    window requires an attacker with concurrent write access to the
    directory's *parent*, at which point they already have unrestricted
    access to everything this process could ever write anyway. Where
    dir_fd isn't supported at all (native Windows), falls back to an
    O_NOFOLLOW (or, lacking even that, an immediately-before-open check) on
    the full path, which still closes the original, narrower "symlink at
    the leaf" race.
    """
    directory = os.path.dirname(os.fspath(path)) or "."
    name = os.path.basename(os.fspath(path))

    if _SUPPORTS_DIR_FD:
        dir_fd = os.open(directory, _DIR_OPEN_FLAGS)
        try:
            def _opener(_file: str, flags: int, _dir_fd: int = dir_fd) -> int:
                return os.open(name, flags | _NOFOLLOW, _CREATE_MODE, dir_fd=_dir_fd)

            try:
                return open(path, "w", encoding="utf-8", opener=_opener)
            except OSError as error:
                _reraise_symlink_as_value_error(path, error)
        finally:
            os.close(dir_fd)

    def _opener(file: str, flags: int) -> int:
        if _NOFOLLOW:
            return os.open(file, flags | _NOFOLLOW, _CREATE_MODE)
        if os.path.islink(file):
            raise OSError(errno.ELOOP, "symlink detected", file)
        return os.open(file, flags, _CREATE_MODE)

    try:
        return open(path, "w", encoding="utf-8", opener=_opener)
    except OSError as error:
        _reraise_symlink_as_value_error(path, error)
