"""Owned-directory junction mutation fixture; no symlink privilege needed."""
from contextlib import contextmanager
import ctypes
from ctypes import wintypes as w
import struct
from cli_hub import _win_file_api as api

api.kernel.DeviceIoControl.argtypes = [w.HANDLE, w.DWORD, w.LPVOID, w.DWORD,
    w.LPVOID, w.DWORD, ctypes.POINTER(w.DWORD), w.LPVOID]
api.kernel.DeviceIoControl.restype = w.BOOL


def control(handle, code, data):
    buffer, done = ctypes.create_string_buffer(data), w.DWORD()
    if not api.kernel.DeviceIoControl(handle, code, buffer, len(data),
                                     None, 0, ctypes.byref(done), None):
        raise ctypes.WinError(ctypes.get_last_error())


@contextmanager
def junction_in_place(parent, target):
    # Called only on an owned empty pytest directory. All shares permit the
    # candidate's already-open traversal handle; no privileges are changed.
    handle = api.kernel.CreateFileW(str(parent), 0x40000000, 7, None, 3, 0x02200000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    changed = False
    try:
        substitute = ('\\??\\' + str(target)).encode('utf-16-le')
        label = str(target).encode('utf-16-le')
        buffer = substitute + b'\0\0' + label + b'\0\0'
        data = struct.pack('<IHHHHHH', 0xA0000003, 8 + len(buffer), 0,
                           0, len(substitute), len(substitute) + 2, len(label)) + buffer
        control(handle, 0x900A4, data)  # FSCTL_SET_REPARSE_POINT, mount-point tag.
        changed = True
        yield
    finally:
        try:
            if changed:
                control(handle, 0x900AC, struct.pack('<IHH', 0xA0000003, 0, 0))
        finally:
            api.close(handle)
