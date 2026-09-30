"""Windows preview writer: pinned relative handles, no reparse traversal."""
from contextlib import ExitStack
import msvcrt
import os
from pathlib import Path
from . import _win_file_api as api


def open_windows_output(path):
    raw = Path(path)
    # Accept ordinary drive/UNC filesystem paths; refuse device namespaces,
    # alternate data streams and ambiguous Win32 dot/space components.
    if raw.anchor.startswith(('\\\\?\\', '\\\\.\\')):
        raise ValueError('Preview output requires an ordinary Windows filesystem path')
    for component in raw.parts:
        if component == raw.anchor or component in ('.', '..'):
            continue
        if ':' in component or component.endswith((' ', '.')) or '\x00' in component:
            raise ValueError('Ambiguous Windows output path component')
    absolute = Path(os.path.abspath(os.fspath(raw)))
    parts = absolute.parts
    if len(parts) < 2:
        raise ValueError('Preview output requires a file name')
    with ExitStack() as stack:
        parent = api.open_root(absolute.anchor)
        stack.callback(api.close, parent)
        for component in parts[1:-1]:
            parent = api.open_relative(parent, component)
            stack.callback(api.close, parent)
        handle = api.open_relative(parent, parts[-1], leaf=True)
        try:
            fd = msvcrt.open_osfhandle(handle, os.O_WRONLY | os.O_BINARY | os.O_NOINHERIT)
        except BaseException:
            api.close(handle)
            raise
        # open_osfhandle transfers ownership to the descriptor. Truncate
        # only after the pinned leaf has passed handle-based validation.
        try:
            os.ftruncate(fd, 0)
            return os.fdopen(fd, 'w', encoding='utf-8')
        except BaseException:
            os.close(fd)
            raise
