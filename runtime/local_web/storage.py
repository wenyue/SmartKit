"""Platform paths, confined namespaces, and atomic local state writes."""
from __future__ import annotations
import json
import os
import stat
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def _windows_is_appcontainer() -> bool:
    if os.name != "nt":
        return False
    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    security = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    security.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    security.GetTokenInformation.argtypes = [
        wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
    ]
    token_query = 0x0008
    token_is_appcontainer = 29
    token = wintypes.HANDLE()
    if not security.OpenProcessToken(kernel.GetCurrentProcess(), token_query, ctypes.byref(token)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        contained = wintypes.DWORD()
        size = wintypes.DWORD()
        if not security.GetTokenInformation(
            token, token_is_appcontainer, ctypes.byref(contained), ctypes.sizeof(contained), ctypes.byref(size)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return bool(contained.value)
    finally:
        kernel.CloseHandle(token)


def _windows_known_local_appdata() -> Path:
    import ctypes
    import uuid

    folder_id = (ctypes.c_ubyte * 16).from_buffer_copy(
        uuid.UUID("f1b32785-6fba-4fcf-9d55-7b8e7f157091").bytes_le
    )
    shell = ctypes.WinDLL("shell32")
    shell.SHGetKnownFolderPath.argtypes = [
        ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.POINTER(ctypes.c_wchar_p),
    ]
    shell.SHGetKnownFolderPath.restype = ctypes.c_long
    dont_verify = 0x4000
    value = ctypes.c_wchar_p()
    result = shell.SHGetKnownFolderPath(ctypes.byref(folder_id), dont_verify, None, ctypes.byref(value))
    if result:
        raise OSError(f"Unable to resolve LocalAppData known folder: 0x{result & 0xffffffff:08x}")
    try:
        if not value.value:
            raise OSError("LocalAppData known folder is empty")
        return Path(value.value)
    finally:
        memory = ctypes.WinDLL("ole32")
        memory.CoTaskMemFree.argtypes = [ctypes.c_void_p]
        memory.CoTaskMemFree(ctypes.cast(value, ctypes.c_void_p))


def _windows_user_local_appdata() -> Path:
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    ) as key:
        value, kind = winreg.QueryValueEx(key, "Local AppData")
    if not isinstance(value, str) or kind not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
        raise OSError("User LocalAppData registry value is invalid")
    return Path(os.path.expandvars(value) if kind == winreg.REG_EXPAND_SZ else value)


def _windows_local_appdata() -> Path:
    configured = Path(os.environ.get("LOCALAPPDATA", ""))
    if not configured.is_absolute():
        return Path.home() / "AppData/Local"
    try:
        if not _windows_is_appcontainer():
            return configured
        container = _windows_known_local_appdata()
        if configured.resolve() != container.resolve():
            return configured
        user = _windows_user_local_appdata()
        if not user.is_absolute() or user.resolve() == container.resolve():
            raise OSError("User LocalAppData does not identify a host directory")
        return user
    except OSError as error:
        # A missing host location must not be mistaken for an undecided preference.
        raise OSError(f"Unable to determine the current user's LocalAppData: {error}") from error


def user_cache_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library/Caches"
    if sys.platform == "win32":
        return _windows_local_appdata().resolve()
    configured = Path(os.environ.get("XDG_CACHE_HOME", ""))
    fallback = Path.home() / ".cache"
    return (configured if configured.is_absolute() else fallback).resolve()


def redirected(path: Path) -> bool:
    try:
        information = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(information.st_mode) or bool(
        getattr(information, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def cache_dir() -> Path:
    return user_cache_dir() / "smartkit/local-web"


def state_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library/Application Support"
    elif os.name == "nt":
        base = _windows_local_appdata()
    else:
        configured = Path(os.environ.get("XDG_STATE_HOME", ""))
        base = configured if configured.is_absolute() else Path.home() / ".local/state"
    return base.resolve() / "smartkit/local-web"


def safe_namespace(root: Path, base: Path) -> None:
    """Allow an explicitly relocated base, but reject redirects inside our namespace."""
    root.relative_to(base)
    current = base
    for part in root.relative_to(base).parts:
        current /= part
        if redirected(current):
            raise ValueError("web service namespace redirects through a link or reparse point: " + str(current))
        current.mkdir(mode=0o700, exist_ok=True)


def prepare_cache() -> Path:
    base = user_cache_dir()
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    safe_namespace(cache_dir(), base)
    return cache_dir()


def prepare_state() -> Path:
    root = state_dir()
    base = root.parent.parent
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    safe_namespace(root, base)
    return root


def read_json(path: Path) -> object:
    if redirected(path):
        raise ValueError("web service metadata must not redirect: " + str(path))
    return json.loads(path.read_bytes().decode("utf-8"))


def write_json(path: Path, value: object, *, create_only: bool = False) -> None:
    if redirected(path):
        raise ValueError("web service metadata must not redirect: " + str(path))
    descriptor, temporary = tempfile.mkstemp(prefix=".pending-", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(json.dumps(value, ensure_ascii=True, indent=2).encode("utf-8"))
        if create_only:
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
