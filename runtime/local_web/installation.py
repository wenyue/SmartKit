"""Identify the loaded plugin and remember each installation seen by a session."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Optional

from .storage import read_json, redirected, state_dir, write_json


INSTALL_RECORD = ".codex-marketplace-install.json"
_REVISION = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_PAYLOAD = ("agents", "contexts", "hooks", "mcp", "rules", "runtime", "setup-assets", "skills", "vendor", "VERSION")


def _git_revision(root: Path) -> Optional[str]:
    try:
        record = read_json(root / INSTALL_RECORD)
    except FileNotFoundError:
        pass
    else:
        if isinstance(record, dict) and record.get("source_type") == "git":
            revision = record.get("revision")
            if not isinstance(revision, str) or _REVISION.fullmatch(revision) is None:
                raise ValueError("invalid installed SmartKit Git revision")
            return revision

    dot_git = root / ".git"
    git = shutil.which("git") if dot_git.exists() and not redirected(dot_git) else None
    if git is None:
        return None
    try:
        result = subprocess.run([git, "-C", str(root), "rev-parse", "--show-toplevel", "--verify", "HEAD^{commit}"],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=2)
    except subprocess.TimeoutExpired:
        return None
    if result.returncode != 0:
        return None
    lines = result.stdout.decode("utf-8", errors="replace").splitlines()
    if len(lines) != 2 or Path(lines[0]).resolve() != root or _REVISION.fullmatch(lines[1]) is None:
        return None
    return lines[1]


def installation_identity(root: Path) -> str:
    revision = _git_revision(root)
    if revision is not None:
        return "git:" + revision
    digest = hashlib.sha256()
    for name in _PAYLOAD:
        path = root / name
        if path.is_file() and not redirected(path):
            digest.update(_file_identity(root, path))
        elif path.is_dir() and not redirected(path):
            for directory, subdirs, files in os.walk(path, onerror=_walk_error):
                parent = Path(directory)
                subdirs[:] = sorted(item for item in subdirs
                                    if item not in (".git", "__pycache__") and not redirected(parent / item))
                for item in sorted(files):
                    file = parent / item
                    if not item.endswith((".pyc", ".pyo")) and not redirected(file) and file.is_file():
                        digest.update(_file_identity(root, file))
    return "content:" + digest.hexdigest()


def _walk_error(error: OSError) -> None:
    raise error


def _file_identity(root: Path, path: Path) -> bytes:
    return path.relative_to(root).as_posix().encode("utf-8") + bytes(1) + hashlib.sha256(path.read_bytes()).digest()


def identity_changed(previous: object, current: str) -> bool:
    # A different evidence format alone does not establish a plugin update.
    return isinstance(previous, str) and previous.split(":", 1)[0] == current.split(":", 1)[0] and previous != current


@dataclass(frozen=True)
class InstallationObservation:
    source: str
    identity: str
    observations: dict[str, str]

    @classmethod
    def read(cls, root: Path) -> InstallationObservation:
        try:
            value = read_json(state_dir() / "installation-observations.json")
        except FileNotFoundError:
            value = {}
        if not isinstance(value, dict) or not all(isinstance(item, str) for item in value.values()):
            raise ValueError("invalid SmartKit installation observations")
        return cls(os.path.normcase(str(root)), installation_identity(root), value)

    @property
    def previous(self) -> Optional[str]:
        return self.observations.get(self.source)

    def save(self) -> None:
        if self.previous != self.identity:
            write_json(state_dir() / "installation-observations.json",
                       {**self.observations, self.source: self.identity})
