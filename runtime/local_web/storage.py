"""Platform paths, confined namespaces, and atomic local state writes."""
from __future__ import annotations
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

def user_cache_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library/Caches"
    windows = sys.platform == "win32"
    configured = Path(os.environ.get("LOCALAPPDATA" if windows else "XDG_CACHE_HOME", ""))
    fallback = Path.home() / ("AppData/Local" if windows else ".cache")
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
    else:
        configured = Path(os.environ.get("LOCALAPPDATA" if os.name == "nt" else "XDG_STATE_HOME", ""))
        base = configured if configured.is_absolute() else Path.home() / ("AppData/Local" if os.name == "nt" else ".local/state")
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
