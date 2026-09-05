"""Windows 10/11 local-NTFS operations behind a small, injectable native-call boundary."""

from __future__ import annotations

import base64
import contextlib
import ctypes
import hashlib
import ntpath
import os
import re
import sys
from pathlib import Path, PureWindowsPath


class WindowsError(OSError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WindowsError(message)


def lexical(path: str) -> str:
    path = str(path).replace("/", "\\")
    drive, tail = ntpath.splitdrive(path)
    require(bool(re.fullmatch(r"[A-Za-z]:", drive)) and tail.startswith("\\"),
            "Windows transfer requires an absolute local drive path; UNC/device/relative paths are unsupported")
    require(len(path) < 240, "Windows transfer paths must be shorter than 240 characters")
    for part in tail.split("\\")[1:]:
        if not part:
            continue
        require(part not in (".", "..") and part == part.rstrip(" ."), "Windows path alias is unsupported")
        require(not any(character in part for character in ':<>"|?*~') and not any(ord(c) < 32 for c in part),
                "Windows ADS, short-name and special path aliases are unsupported")
        require(not re.fullmatch(r"(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\..*)?", part, re.I),
                "Windows DOS device names are unsupported")
    return drive.upper() + tail


def stable_metadata(value: dict) -> dict:
    return {key: value[key] for key in ("kind", "volume", "file_id", "links", "attributes", "security")}


class NativeAPI:
    """ctypes signatures stay here; the batch layer never interprets native partial success."""

    def __init__(self):
        require(os.name == "nt", "Windows native calls require a real Windows host")
        version = sys.getwindowsversion()
        require(version.major >= 10 and version.product_type == 1, "Windows transfer requires Windows 10/11 desktop")
        self.k = ctypes.WinDLL("kernel32", use_last_error=True)
        self.a = ctypes.WinDLL("advapi32", use_last_error=True)
        self.D = ctypes.c_uint32
        self.B = ctypes.c_int32
        self.H = ctypes.c_void_p
        self.P = ctypes.c_void_p
        self.W = ctypes.c_wchar_p
        self.invalid = ctypes.c_void_p(-1).value
        signatures = {
            "CreateFileW": (self.H, [self.W, self.D, self.D, self.P, self.D, self.D, self.H]),
            "CloseHandle": (self.B, [self.H]),
            "GetFinalPathNameByHandleW": (self.D, [self.H, self.W, self.D, self.D]),
            "GetFileInformationByHandle": (self.B, [self.H, self.P]),
            "GetVolumeInformationW": (self.B, [self.W, self.W, self.D, self.P, self.P, self.P, self.W, self.D]),
            "GetDriveTypeW": (self.D, [self.W]),
            "QueryDosDeviceW": (self.D, [self.W, self.W, self.D]),
            "FindFirstStreamW": (self.H, [self.W, ctypes.c_int, self.P, self.D]),
            "FindNextStreamW": (self.B, [self.H, self.P]),
            "FindClose": (self.B, [self.H]),
            "ReadFile": (self.B, [self.H, self.P, self.D, self.P, self.P]),
            "WriteFile": (self.B, [self.H, self.P, self.D, self.P, self.P]),
            "SetFilePointerEx": (self.B, [self.H, ctypes.c_int64, self.P, self.D]),
            "SetEndOfFile": (self.B, [self.H]),
            "FlushFileBuffers": (self.B, [self.H]),
            "SetFileInformationByHandle": (self.B, [self.H, ctypes.c_int, self.P, self.D]),
            "MoveFileExW": (self.B, [self.W, self.W, self.D]),
            "DeleteFileW": (self.B, [self.W]),
            "CreateDirectoryW": (self.B, [self.W, self.P]),
            "GetCurrentProcess": (self.H, []),
            "LocalFree": (self.H, [self.H]),
        }
        for name, (result, arguments) in signatures.items():
            function = getattr(self.k, name)
            function.restype, function.argtypes = result, arguments
        for name, result, arguments in (
            ("GetKernelObjectSecurity", self.B, [self.H, self.D, self.P, self.D, self.P]),
            ("OpenProcessToken", self.B, [self.H, self.D, self.P]),
            ("GetTokenInformation", self.B, [self.H, ctypes.c_int, self.P, self.D, self.P]),
            ("ConvertSidToStringSidW", self.B, [self.P, self.P]),
            ("ConvertStringSecurityDescriptorToSecurityDescriptorW", self.B, [self.W, self.D, self.P, self.P]),
        ):
            function = getattr(self.a, name)
            function.restype, function.argtypes = result, arguments

    def check(self, result, operation: str):
        if not result:
            raise ctypes.WinError(ctypes.get_last_error(), operation)
        return result

    def volume(self, path: str) -> None:
        root = lexical(path)[:3]
        require(self.k.GetDriveTypeW(root) == 3, "Windows transfer supports fixed local disks only")
        device = ctypes.create_unicode_buffer(1024)
        self.check(self.k.QueryDosDeviceW(root[:2], device, len(device)), "QueryDosDeviceW")
        require(device.value.startswith("\\Device\\HarddiskVolume"), "SUBST and device mappings are unsupported")
        filesystem = ctypes.create_unicode_buffer(64)
        self.check(self.k.GetVolumeInformationW(root, None, 0, None, None, None, filesystem, len(filesystem)),
                   "GetVolumeInformationW")
        require(filesystem.value == "NTFS", "Windows transfer requires local NTFS")

    @contextlib.contextmanager
    def open(self, path: str, access: str = "metadata", create: bool = False):
        rights = 0x20000 | 0x80  # READ_CONTROL and FILE_READ_ATTRIBUTES.
        sharing = 7
        if access == "data":
            rights |= 0x80000000 | 0x40000000
            sharing = 1  # Deny other writers and deleters while updating this object.
        handle = self.k.CreateFileW(path, rights, sharing, None, 1 if create else 3,
                                    0x02000000 | 0x00200000, None)
        if handle == self.invalid:
            raise ctypes.WinError(ctypes.get_last_error(), "CreateFileW")
        try:
            yield handle
        finally:
            self.check(self.k.CloseHandle(handle), "CloseHandle")

    def handle_metadata(self, handle) -> dict:
        D = self.D
        class Info(ctypes.Structure):
            _fields_ = [("attributes", D), ("creation_low", D), ("creation_high", D),
                        ("access_low", D), ("access_high", D), ("write_low", D), ("write_high", D),
                        ("volume", D), ("size_high", D), ("size_low", D), ("links", D),
                        ("id_high", D), ("id_low", D)]
        info = Info()
        self.check(self.k.GetFileInformationByHandle(handle, ctypes.byref(info)), "GetFileInformationByHandle")
        needed = D()
        self.a.GetKernelObjectSecurity(handle, 7, None, 0, ctypes.byref(needed))
        require(ctypes.get_last_error() == 122 and needed.value > 0, "security descriptor inspection failed")
        descriptor = ctypes.create_string_buffer(needed.value)
        self.check(self.a.GetKernelObjectSecurity(handle, 7, descriptor, needed, ctypes.byref(needed)),
                   "GetKernelObjectSecurity")
        final = ctypes.create_unicode_buffer(32768)
        length = self.k.GetFinalPathNameByHandleW(handle, final, len(final), 0)
        self.check(length, "GetFinalPathNameByHandleW")
        require(length < len(final), "native final path exceeds supported limit")
        name = final.value
        require(name.startswith("\\\\?\\") and not name.startswith("\\\\?\\UNC\\"), "nonlocal native path")
        return {"kind": "directory" if info.attributes & 0x10 else "file",
                "volume": info.volume, "file_id": (info.id_high << 32) | info.id_low,
                "links": info.links, "attributes": info.attributes,
                "security": base64.b64encode(descriptor.raw[:needed.value]).decode("ascii"),
                "path": name[4:]}

    def streams(self, path: str) -> list[str]:
        class Stream(ctypes.Structure):
            _fields_ = [("size", ctypes.c_int64), ("name", ctypes.c_wchar * 296)]
        value = Stream()
        handle = self.k.FindFirstStreamW(path, 0, ctypes.byref(value), 0)
        if handle == self.invalid:
            if ctypes.get_last_error() == 38:
                return []
            raise ctypes.WinError(ctypes.get_last_error(), "FindFirstStreamW")
        result = []
        try:
            while True:
                result.append(value.name)
                if not self.k.FindNextStreamW(handle, ctypes.byref(value)):
                    require(ctypes.get_last_error() == 38, "stream enumeration failed")
                    break
        finally:
            self.check(self.k.FindClose(handle), "FindClose")
        return result

    def read(self, handle):
        self.check(self.k.SetFilePointerEx(handle, 0, None, 0), "SetFilePointerEx")
        buffer = ctypes.create_string_buffer(1024 * 1024)
        length = self.D()
        while True:
            self.check(self.k.ReadFile(handle, buffer, len(buffer), ctypes.byref(length), None), "ReadFile")
            if not length.value:
                return
            yield buffer.raw[:length.value]

    def write(self, handle, chunks, attributes: int) -> None:
        self.check(self.k.SetFilePointerEx(handle, 0, None, 0), "SetFilePointerEx")
        for chunk in chunks:
            offset = 0
            while offset < len(chunk):
                buffer = ctypes.create_string_buffer(chunk[offset:])
                length = self.D()
                self.check(self.k.WriteFile(handle, buffer, len(chunk) - offset, ctypes.byref(length), None), "WriteFile")
                require(length.value > 0, "WriteFile made no progress")
                offset += length.value
        self.check(self.k.SetEndOfFile(handle), "SetEndOfFile")
        class Basic(ctypes.Structure):
            _fields_ = [("creation", ctypes.c_int64), ("access", ctypes.c_int64),
                        ("write", ctypes.c_int64), ("change", ctypes.c_int64), ("attributes", self.D)]
        basic = Basic(0, 0, 0, 0, attributes)
        self.check(self.k.SetFileInformationByHandle(handle, 0, ctypes.byref(basic), ctypes.sizeof(basic)),
                   "SetFileInformationByHandle")
        self.check(self.k.FlushFileBuffers(handle), "FlushFileBuffers")

    def move(self, source: str, destination: str) -> None:
        self.check(self.k.MoveFileExW(source, destination, 8), "MoveFileExW without overwrite")

    def delete(self, path: str) -> None:
        self.check(self.k.DeleteFileW(path), "DeleteFileW")

    def private_directory(self, path: str) -> None:
        token = self.H()
        self.check(self.a.OpenProcessToken(self.k.GetCurrentProcess(), 8, ctypes.byref(token)), "OpenProcessToken")
        try:
            needed = self.D()
            self.a.GetTokenInformation(token, 1, None, 0, ctypes.byref(needed))
            require(ctypes.get_last_error() == 122, "token user inspection failed")
            buffer = ctypes.create_string_buffer(needed.value)
            self.check(self.a.GetTokenInformation(token, 1, buffer, needed, ctypes.byref(needed)), "GetTokenInformation")
            sid = ctypes.cast(buffer, ctypes.POINTER(self.P))[0]
            sid_string = self.P()
            self.check(self.a.ConvertSidToStringSidW(sid, ctypes.byref(sid_string)), "ConvertSidToStringSidW")
            try:
                sid_text = ctypes.wstring_at(sid_string)
            finally:
                self.k.LocalFree(sid_string)
        finally:
            self.k.CloseHandle(token)
        descriptor = self.P()
        sddl = f"D:P(A;OICI;FA;;;{sid_text})(A;OICI;FA;;;SY)"
        self.check(self.a.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(descriptor), None),
                   "ConvertStringSecurityDescriptorToSecurityDescriptorW")
        class SecurityAttributes(ctypes.Structure):
            _fields_ = [("length", self.D), ("descriptor", self.P), ("inherit", self.B)]
        attributes = SecurityAttributes(ctypes.sizeof(SecurityAttributes), descriptor, 0)
        try:
            self.check(self.k.CreateDirectoryW(path, ctypes.byref(attributes)), "CreateDirectoryW")
        finally:
            self.k.LocalFree(descriptor)


class WindowsBackend:
    def __init__(self, api=None):
        self.api = api if api is not None else NativeAPI()

    def metadata(self, path) -> dict:
        name = lexical(str(path))
        self.api.volume(name)
        parts = PureWindowsPath(name)
        chain = list(reversed(parts.parents)) + [parts]
        value = None
        for item in chain:
            try:
                with self.api.open(str(item)) as handle:
                    observed = self.api.handle_metadata(handle)
            except FileNotFoundError:
                return {"kind": "absent"}
            require(ntpath.normcase(observed["path"]) == ntpath.normcase(str(item)),
                    "Windows physical path alias is unsupported")
            attributes = observed["attributes"]
            allowed = 0x10 | 0x20 | 0x80 | 0x2 | 0x4 | 0x2000 | (1 if observed["kind"] == "directory" else 0)
            require(attributes & ~allowed == 0,
                    "unsupported Windows readonly, reparse, sparse, compression, encryption or offline attributes")
            require(observed["kind"] == "directory" or observed["links"] == 1, "Windows hardlinks are unsupported")
            require(self.api.streams(str(item)) in ([], ["::$DATA"]), "Windows alternate streams are unsupported")
            value = observed
        return stable_metadata(value)

    def physical(self, path):
        self.metadata(path)
        return Path(lexical(str(path)))

    def guard(self, path, expected: dict) -> None:
        require(self.metadata(path) == expected, f"Windows native metadata drift: {path}")

    def private_directory(self, path) -> None:
        self.metadata(PureWindowsPath(str(path)).parent)
        self.api.private_directory(lexical(str(path)))
        require(self.metadata(path)["kind"] == "directory", "Windows operation directory was not created")

    def write(self, destination, incoming, expected: dict, before_data: dict, record) -> dict:
        name = lexical(str(destination))
        self.guard(destination, expected)
        create = expected["kind"] == "absent"
        with self.api.open(name, access="data", create=create) as handle:
            native = stable_metadata(self.api.handle_metadata(handle))
            if not create:
                require(native == expected, "Windows handle identity/security drift")
                hasher = hashlib.sha256()
                size = 0
                for chunk in self.api.read(handle):
                    hasher.update(chunk)
                    size += len(chunk)
                require(size == before_data["size"] and hasher.hexdigest() == before_data["sha256"],
                        "Windows locked-handle content drift")
            record(native)
            with Path(incoming).open("rb") as stream:
                self.api.write(handle, iter(lambda: stream.read(1024 * 1024), b""), native["attributes"])
            require(stable_metadata(self.api.handle_metadata(handle)) == native,
                    "Windows post-write security/attribute preservation failed")
        self.guard(destination, native)
        return native

    def move(self, source, destination, expected: dict) -> None:
        self.guard(source, expected)
        require(self.metadata(destination)["kind"] == "absent", "Windows move destination already exists")
        require(expected["volume"] == self.metadata(PureWindowsPath(str(destination)).parent)["volume"], "Windows cross-volume move is unsupported")
        self.api.move(lexical(str(source)), lexical(str(destination)))
        self.guard(destination, expected)
        require(self.metadata(source)["kind"] == "absent", "Windows move source remains")

    def delete(self, path, expected: dict) -> None:
        self.guard(path, expected)
        self.api.delete(lexical(str(path)))
        require(self.metadata(path)["kind"] == "absent", "Windows owned-file deletion is unproven")


_backend = None


def backend() -> WindowsBackend:
    global _backend
    if _backend is None:
        _backend = WindowsBackend()
    return _backend
