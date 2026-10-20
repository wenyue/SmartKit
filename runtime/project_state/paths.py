"""Reject redirected project paths before reading configuration state."""
from __future__ import annotations

import stat
from pathlib import Path, PurePosixPath


_FILE_ATTRIBUTE_REPARSE_POINT = getattr(
    stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400,
)


def is_link_like(path: Path) -> bool:
    """Return whether a path redirects through a symlink or Windows reparse point."""
    try:
        status = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(status.st_mode) or bool(
        getattr(status, 'st_file_attributes', 0) & _FILE_ATTRIBUTE_REPARSE_POINT
    )

class ProjectError(ValueError):
    """Raised when a target project cannot be inspected safely."""


def _confined_root(root: Path) -> Path:
    candidate = Path(root).absolute()
    current = Path(candidate.anchor)
    for part in candidate.parts[1:]:
        current /= part
        if is_link_like(current):
            raise ProjectError(f'target path contains symlink: {current}')
    return candidate


def confined_target(root: Path, relative: PurePosixPath) -> Path:
    """Return a target path only when every existing component is non-symlinked."""
    if not isinstance(relative, PurePosixPath):
        raise ProjectError('target path must be a relative POSIX path')
    if relative.is_absolute() or not relative.parts or '..' in relative.parts:
        raise ProjectError('target path must be relative and cannot contain ..')

    confined_root = _confined_root(root)
    target = confined_root.joinpath(*relative.parts)
    current = confined_root
    for part in relative.parts:
        current /= part
        if is_link_like(current):
            raise ProjectError(f'target path contains symlink: {current}')
    return target
