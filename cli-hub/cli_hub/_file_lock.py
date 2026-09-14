"""Cross-platform exclusive file lock for guarding a read-modify-write.

Several cli-hub commands load a JSON state file, mutate their own in-memory
copy, and write the whole file back. Without a lock spanning that entire
sequence, two concurrent cli-hub processes can both load the same snapshot
and then each write their own copy back -- whichever write lands last
silently discards the other process's change. `exclusive_lock` provides a
blocking, cross-process mutex (fcntl on POSIX, msvcrt on Windows) to wrap
such a sequence in.
"""

from __future__ import annotations

import contextlib
from pathlib import Path

try:
    import fcntl
except ImportError:  # Windows has no fcntl; fall back to msvcrt below.
    fcntl = None
    import msvcrt


@contextlib.contextmanager
def exclusive_lock(lock_path: Path):
    """Hold a blocking, exclusive lock on `lock_path` for the with-block.

    Safe to call from multiple processes racing on the same underlying
    state file; each caller blocks until the previous holder releases.
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+b") as lock_handle:
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        else:
            _msvcrt_lock(lock_handle)
            try:
                yield
            finally:
                _msvcrt_unlock(lock_handle)


def _msvcrt_lock(handle):
    handle.seek(0)
    if not handle.read(1):
        handle.write(b"0")
        handle.flush()
    handle.seek(0)
    while True:
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            return
        except OSError:
            continue


def _msvcrt_unlock(handle):
    handle.seek(0)
    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
