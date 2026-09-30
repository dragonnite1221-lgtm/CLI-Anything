"""Small Windows file-handle bindings; imported only on native Windows."""
import ctypes
from ctypes import wintypes as w


class UnicodeString(ctypes.Structure):
    _fields_ = [('Length', w.USHORT), ('MaximumLength', w.USHORT), ('Buffer', w.LPWSTR)]


class ObjectAttributes(ctypes.Structure):
    _fields_ = [('Length', w.ULONG), ('RootDirectory', w.HANDLE),
                ('ObjectName', ctypes.POINTER(UnicodeString)), ('Attributes', w.ULONG),
                ('SecurityDescriptor', w.LPVOID), ('SecurityQualityOfService', w.LPVOID)]


class IoStatusBlock(ctypes.Structure):
    _fields_ = [('StatusOrPointer', w.LPVOID), ('Information', ctypes.c_size_t)]


kernel = ctypes.WinDLL('kernel32', use_last_error=True)
nt = ctypes.WinDLL('ntdll')
kernel.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, w.HANDLE]
kernel.CreateFileW.restype = w.HANDLE
kernel.CloseHandle.argtypes = [w.HANDLE]
kernel.CloseHandle.restype = w.BOOL
kernel.GetFileInformationByHandle.argtypes = [w.HANDLE, w.LPVOID]
kernel.GetFileInformationByHandle.restype = w.BOOL
nt.NtCreateFile.argtypes = [ctypes.POINTER(w.HANDLE), w.ULONG,
    ctypes.POINTER(ObjectAttributes), ctypes.POINTER(IoStatusBlock), w.LPVOID,
    w.ULONG, w.ULONG, w.ULONG, w.ULONG, w.LPVOID, w.ULONG]
nt.NtCreateFile.restype = w.LONG
nt.RtlNtStatusToDosError.argtypes = [w.LONG]
nt.RtlNtStatusToDosError.restype = w.ULONG

READ_ATTRIBUTES = 0x80
SYNCHRONIZE = 0x100000
TRAVERSE = 0x20
WRITE_DATA = 0x2
SHARE_READ_WRITE = 0x3  # Deliberately omit FILE_SHARE_DELETE.
OPEN_REPARSE_POINT = 0x200000
SYNCHRONOUS = 0x20
DIRECTORY = 0x1
NON_DIRECTORY = 0x40
REPARSE_ATTRIBUTE = 0x400


def close(handle):
    kernel.CloseHandle(handle)


def information(handle):
    # BY_HANDLE_FILE_INFORMATION consists of thirteen DWORDs, including
    # three FILETIMEs (two DWORDs each). No pathname is re-resolved here.
    info = (w.DWORD * 13)()
    if not kernel.GetFileInformationByHandle(handle, ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    return info[0], info[10]


def verify(handle, *, leaf=False):
    attributes, links = information(handle)
    if attributes & REPARSE_ATTRIBUTE:
        raise ValueError('Refusing preview output through a symlink/reparse point')
    if leaf and links != 1:
        raise ValueError('Refusing preview output through a multiply-linked file')


def open_root(anchor):
    handle = kernel.CreateFileW(anchor, TRAVERSE | READ_ATTRIBUTES | SYNCHRONIZE,
        SHARE_READ_WRITE, None, 3, 0x02000000 | OPEN_REPARSE_POINT, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        verify(handle)
        return handle
    except BaseException:
        close(handle)
        raise


def open_relative(parent, name, *, leaf=False):
    # One component relative to a held handle: no intermediate pathname
    # can be re-resolved, and reparse processing is bypassed for this name.
    length = len(name.encode('utf-16-le'))
    if length > 65532:
        raise ValueError('Output path component is too long')
    buffer = ctypes.create_unicode_buffer(name)
    text = UnicodeString(length, length + 2, ctypes.cast(buffer, w.LPWSTR))
    attrs = ObjectAttributes(ctypes.sizeof(ObjectAttributes), parent,
                             ctypes.pointer(text), 0x40, None, None)
    handle, status = w.HANDLE(), IoStatusBlock()
    access = READ_ATTRIBUTES | SYNCHRONIZE | (WRITE_DATA if leaf else TRAVERSE)
    options = OPEN_REPARSE_POINT | SYNCHRONOUS | (NON_DIRECTORY if leaf else DIRECTORY)
    result = nt.NtCreateFile(ctypes.byref(handle), access, ctypes.byref(attrs),
        ctypes.byref(status), None, 0x80, 1 if leaf else SHARE_READ_WRITE,
        3 if leaf else 1, options, None, 0)  # FILE_OPEN_IF / FILE_OPEN; never truncate yet.
    if result < 0:
        raise ctypes.WinError(nt.RtlNtStatusToDosError(result))
    try:
        verify(handle.value, leaf=leaf)
        return handle.value
    except BaseException:
        close(handle.value)
        raise
