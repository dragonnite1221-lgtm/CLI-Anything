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
import errno
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
    # Windows byte-range locks deny other handles read access too, so a
    # concurrent holder's read of this byte (to check emptiness, say) would
    # itself raise OSError while contended. Lock directly instead -- Windows
    # allows locking a byte range beyond the current end of file, so there
    # is no need to read or write the file before locking it.
    handle.seek(0)
    while True:
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            return
        except OSError as error:
            # LK_LOCK is documented (Microsoft CRT _locking reference) to
            # retry internally for ~10 seconds on contention, reporting
            # EACCES if it gives up quickly and EDEADLOCK once that longer
            # internal retry window itself times out -- both just mean
            # "still held by someone else," not a real failure, so both
            # are retried here. Anything else (EBADF, EINVAL, ...) is a
            # genuine failure that will never resolve by itself.
            if error.errno not in (errno.EACCES, errno.EDEADLOCK):
                raise


def _msvcrt_unlock(handle):
    handle.seek(0)
    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
