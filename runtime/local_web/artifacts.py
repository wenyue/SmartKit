#!/usr/bin/env python
"""Cache disposable files privately; publish selected files through the web owner.

Creation copies a complete group, fixes its deadline, and cleans recognized expired
groups first. Native OSError/ValueError failures propagate with confirmed cleanup
effects; failed publication never rolls back already completed cache creation.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path, PurePosixPath
from typing import Dict, Mapping, Optional, Sequence, Tuple

from .storage import redirected, user_cache_dir, cache_dir, prepare_cache


SCHEMA = "smartkit.local-artifact/v1"
DEFAULT_RETENTION = timedelta(days=7)
ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,79}")
METADATA_NAME = ".artifact.json"


@dataclass(frozen=True)
class CachedFile:
    path: Path
    sha256: str
    public: bool


@dataclass(frozen=True)
class CachedArtifact:
    id: str
    created_at: float
    expires_at: float
    files: Mapping[str, CachedFile]
    published: bool


def cache_root() -> Path:
    return cache_dir() / "artifacts"


def checked_path(path: Path) -> Path:
    """Constrain reads and cleanup to regular files beneath the selected user cache."""
    base = user_cache_dir()
    relative = path.absolute().relative_to(base)
    if ".." in relative.parts:
        raise ValueError("artifact path escapes the user cache")
    current = base
    for part in relative.parts:
        current /= part
        if redirected(current):
            raise ValueError("artifact path redirects through a link or reparse point: " + str(current))
    return current


def filename(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or any(ord(c) < 32 for c in value):
        raise ValueError("invalid artifact filename")
    if PurePosixPath(value).is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("artifact filenames must be confined relative paths")
    if value.split("/")[0] == METADATA_NAME:
        raise ValueError("artifact filename is reserved for metadata")
    return value


def _unique_object(pairs: Sequence[Tuple[str, object]]) -> Dict[str, object]:
    result = {}  # type: Dict[str, object]
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field: " + key)
        result[key] = value
    return result


def _number(value: object) -> bool:
    try:
        return type(value) in (int, float) and math.isfinite(value) and value > 0
    except OverflowError:
        return False


def _prepare_root() -> Path:
    prepare_cache()
    root = checked_path(cache_root())
    root.mkdir(mode=0o700, exist_ok=True)
    return root


def load_artifact(identity: str) -> Optional[CachedArtifact]:
    """Read metadata without maintenance; malformed or redirected records fail visibly."""
    if not isinstance(identity, str) or ID_PATTERN.fullmatch(identity) is None:
        return None
    folder = checked_path(cache_root() / identity / "files")
    metadata = folder / METADATA_NAME
    checked_path(metadata)
    try:
        record = json.loads(metadata.read_bytes().decode("utf-8"), object_pairs_hook=_unique_object)
    except FileNotFoundError:
        return None
    if (not isinstance(record, dict) or set(record) != {"schema", "id", "created_at", "expires_at", "files", "published"}
            or record["schema"] != SCHEMA or record["id"] != identity
            or not _number(record["created_at"]) or not _number(record["expires_at"])
            or record["expires_at"] <= record["created_at"]
            or not isinstance(record["files"], dict) or not record["files"]
            or type(record["published"]) is not bool):
        raise ValueError("invalid cached artifact metadata: " + str(metadata))
    entries = {}  # type: Dict[str, CachedFile]
    for name, value in record["files"].items():
        filename(name)
        if (not isinstance(value, dict) or set(value) != {"sha256", "public"}
                or not isinstance(value["sha256"], str)
                or re.fullmatch(r"[0-9a-f]{64}", value["sha256"]) is None
                or type(value["public"]) is not bool):
            raise ValueError("invalid cached artifact file metadata: " + str(metadata))
        entries[name] = CachedFile(folder / name, value["sha256"], value["public"])
    return CachedArtifact(identity, record["created_at"], record["expires_at"], entries, record["published"])


def read_file(entry: CachedFile) -> bytes:
    path = checked_path(entry.path)
    if not path.is_file():
        raise ValueError("cached artifact is not a regular file: " + str(path))
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != entry.sha256:
        raise ValueError("cached artifact content changed: " + str(path))
    return content


def _owned_group(artifact: CachedArtifact) -> bool:
    """Unknown children, altered files, and redirects retain the entire group."""
    group = checked_path(cache_root() / artifact.id)
    if {child.name for child in group.iterdir()} != {"files"}:
        return False
    expected_files = {METADATA_NAME} | set(artifact.files)
    expected_dirs = set()
    for name, entry in artifact.files.items():
        read_file(entry)
        parent = PurePosixPath(name).parent
        while str(parent) != ".":
            expected_dirs.add(str(parent))
            parent = parent.parent
    found_files, found_dirs = set(), set()
    pending = [group / "files"]
    while pending:
        directory = pending.pop()
        for child in directory.iterdir():
            checked_path(child)
            name = child.relative_to(group / "files").as_posix()
            if child.is_dir():
                found_dirs.add(name)
                pending.append(child)
            elif child.is_file():
                found_files.add(name)
            else:
                return False
    return found_files == expected_files and found_dirs == expected_dirs


def cleanup_expired(now: Optional[float] = None) -> None:
    """Delete only recognized expired groups and preserve evidence of partial failure."""
    moment = time.time() if now is None else now
    if not _number(moment):
        raise ValueError("cleanup time must be finite and positive")
    root = checked_path(cache_root())
    if root.exists():
        for group in sorted(root.iterdir()):
            if group.name.startswith(".pending-"):
                continue
            artifact = None
            try:
                artifact = load_artifact(group.name)
                owned = artifact is not None and artifact.expires_at <= moment and _owned_group(artifact)
            except (OSError, ValueError):
                owned = False
            if not owned:
                if artifact is None or artifact.expires_at <= moment:
                    print("Preserved unrecognized or unsafe cache: " + str(group), file=sys.stderr)
                continue
            try:
                shutil.rmtree(group)
            except OSError as error:
                if not group.exists():
                    continue
                raise OSError("expired cache cleanup failed at %s; some files may already be deleted: %s"
                              % (group, error)) from error
            print("Expired cache removed: " + str(group), file=sys.stderr)


def create_artifact(files: Mapping[str, bytes], *, public_files: Sequence[str] = (),
                    retention: timedelta = DEFAULT_RETENTION) -> CachedArtifact:
    """Copy one fixed group; private files are retained but never implicitly published.

    The positive finite duration starts after all payload files are written. Cleanup
    can have lasting effects before a later write fails; publication is a separate
    operation and cannot renew this deadline.
    """
    seconds = retention.total_seconds() if isinstance(retention, timedelta) else 0
    if not _number(seconds) or not files:
        raise ValueError("artifact needs files and a positive finite retention duration")
    names = set()
    for name, content in files.items():
        filename(name)
        normalized = os.path.normcase(name)
        if normalized in names or not isinstance(content, bytes):
            raise ValueError("artifact files need distinct names and captured bytes")
        names.add(normalized)
    for name in files:
        if any(os.path.normcase(str(parent)) in names for parent in PurePosixPath(name).parents if str(parent) != "."):
            raise ValueError("artifact filenames cannot overlap file and directory paths")
    public = set(public_files)
    if public - set(files):
        raise ValueError("public files must belong to the captured artifact")
    root = _prepare_root()
    cleanup_expired()
    identity = "artifact-" + uuid.uuid4().hex
    output = root / identity
    with tempfile.TemporaryDirectory(prefix=".pending-", dir=str(root)) as temporary:
        staged = Path(temporary) / "files"
        staged.mkdir(mode=0o700)
        entries = {}
        for name, content in files.items():
            path = staged / name
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            path.write_bytes(content)
            entries[name] = {"sha256": hashlib.sha256(content).hexdigest(), "public": name in public}
        created = time.time()
        expires = created + seconds
        if not _number(created) or not _number(expires) or expires <= created:
            raise ValueError("artifact retention produced an invalid deadline")
        record = {"schema": SCHEMA, "id": identity, "created_at": created, "expires_at": expires,
                  "files": entries, "published": False}
        (staged / METADATA_NAME).write_bytes(json.dumps(record, ensure_ascii=True).encode("utf-8"))
        # Reserve the identity before atomic publication; Unix rename can replace an empty directory.
        output.mkdir(mode=0o700)
        try:
            staged.rename(output / "files")
        except OSError as error:
            try:
                output.rmdir()
            except OSError as cleanup_error:
                raise OSError("artifact publication failed (%s); reserved directory cleanup failed at %s (%s)"
                              % (error, output, cleanup_error)) from error
            raise
    return CachedArtifact(identity, created, expires,
                          {name: CachedFile(output / "files" / name, item["sha256"], item["public"])
                           for name, item in entries.items()}, False)


def mark_published(identity: str) -> CachedArtifact:
    """Enable only declared public files, preserving captured content and deadline."""
    artifact = load_artifact(identity)
    if artifact is None or artifact.expires_at <= time.time():
        raise ValueError("cached artifact is unavailable or expired")
    public = [entry for entry in artifact.files.values() if entry.public]
    if not public:
        raise ValueError("cached artifact has no declared public files")
    for entry in public:
        read_file(entry)
    if not artifact.published:
        metadata = checked_path(cache_root() / identity / "files" / METADATA_NAME)
        record = json.loads(metadata.read_bytes().decode("utf-8"), object_pairs_hook=_unique_object)
        record["published"] = True
        descriptor, temporary = tempfile.mkstemp(prefix=".pending-", dir=str(metadata.parent))
        try:
            with os.fdopen(descriptor, "wb") as output:
                output.write(json.dumps(record, ensure_ascii=True).encode("utf-8"))
            os.replace(temporary, metadata)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
    return CachedArtifact(artifact.id, artifact.created_at, artifact.expires_at, artifact.files, True)


def has_unexpired_artifacts(now: float) -> bool:
    root = checked_path(cache_root())
    if not root.exists():
        return False
    for group in root.iterdir():
        if group.name.startswith(".pending-"):
            continue
        try:
            artifact = load_artifact(group.name)
        except (OSError, ValueError):
            continue
        if artifact is not None and artifact.published and artifact.expires_at > now:
            return True
    return False
