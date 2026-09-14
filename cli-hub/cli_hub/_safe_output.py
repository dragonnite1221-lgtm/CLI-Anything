"""Guard against writing through a symlink that escapes an output directory.

Preview bundle and live-session directories can originate from untrusted
input (a shared bundle archive, an imported session). If one plants a
symlink at the well-known output filename (preview.html / live.html),
naively following it on write would let it clobber an arbitrary file the
current user can write, anywhere on disk.
"""

from __future__ import annotations

import os
from pathlib import Path


def safe_output_file(output_path: str) -> Path:
    """Resolve `output_path`, rejecting a pre-existing symlink whose real
    target directory differs from the directory the caller asked to write
    into.

    Resolves via os.path.realpath and compares the real target's parent
    directory against the (non-symlink-following) intended directory --
    the directory portion of `output_path` itself.
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
