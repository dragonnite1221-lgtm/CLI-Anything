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
    target directory differs from the directory the caller asked to write
    into.

    Resolves via os.path.realpath and compares the real target's parent
    directory against the (non-symlink-following) intended directory --
    the directory portion of `output_path` itself. This is an early,
    friendly check only: the file may not exist yet, so there is nothing to
    resolve, and a symlink can still be planted afterward. Callers must
    still open the final path with `open_safe_output` to close that race.
    """
    raw = Path(output_path).expanduser()
    intended_dir = raw.parent.resolve()
    if raw.is_symlink():
        real_target = Path(os.path.realpath(raw))
        if real_target.parent != intended_dir:
            raise ValueError(
                "Refusing to write preview output through a symlink that escapes "
                f"the intended output directory: {raw} -> {real_target}"
            )
        return real_target
    return intended_dir / raw.name


def open_safe_output(path: Path) -> IO[str]:
    """Open `path` for text writing, refusing to follow a symlink planted at
    that exact location.

    `safe_output_file` only catches a symlink that already exists when it
    runs; the caller (HTML generation) can take a while after that check
    before it actually writes. Opening with O_NOFOLLOW makes the write
    itself atomic against a symlink appearing there in between -- the kernel
    refuses the open outright instead of silently following it.
    """

    def _opener(file: str, flags: int) -> int:
        return os.open(file, flags | os.O_NOFOLLOW)

    try:
        return open(path, "w", encoding="utf-8", opener=_opener)
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise ValueError(f"Refusing to write preview output through a symlink: {path}") from error
        raise
