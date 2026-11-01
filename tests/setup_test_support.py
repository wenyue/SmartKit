"""Build isolated setup sources without repeatedly committing the whole checkout."""
from __future__ import annotations

import atexit
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def copy_plugin_source(destination: Path) -> None:
    shutil.copytree(
        REPO_ROOT,
        destination,
        ignore=shutil.ignore_patterns(
            '.git', '.worktrees', '.venv', '.playwright-mcp', '.superpowers',
            '.idea', '.vscode', '__pycache__', '*.pyc', '*.log',
        ),
    )


def _git(directory: Path, *arguments: str) -> None:
    subprocess.run(
        ('git', '-C', str(directory), *arguments),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


@lru_cache(maxsize=1)
def _source_repository() -> Path:
    temporary = tempfile.TemporaryDirectory(prefix='smartkit-setup-source-')
    atexit.register(temporary.cleanup)
    source = Path(temporary.name) / 'source'
    copy_plugin_source(source)
    _git(source, 'init', '--quiet')
    _git(source, 'checkout', '--quiet', '-b', 'master')
    _git(source, 'config', 'user.email', 'test@example.invalid')
    _git(source, 'config', 'user.name', 'Setup Test')
    _git(source, 'add', '.')
    _git(source, 'commit', '--quiet', '-m', 'setup test source')
    # Pack once so Windows clones copy a few files instead of every loose object.
    _git(source, 'repack', '-a', '-d', '-q')
    return source


def make_origin(root: Path) -> tuple[Path, Path]:
    """Give each case independent Git objects, refs, and mutable source files."""
    origin = root / 'origin.git'
    work = root / 'origin-work'
    source = _source_repository()
    _git(root, 'clone', '--bare', '--quiet', '--no-hardlinks', str(source), str(origin))
    _git(root, 'clone', '--quiet', '--no-hardlinks', str(origin), str(work))
    _git(work, 'remote', 'set-url', 'origin', origin.as_uri())
    _git(work, 'config', 'user.email', 'test@example.invalid')
    _git(work, 'config', 'user.name', 'Setup Test')
    return origin, work
