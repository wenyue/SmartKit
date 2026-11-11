"""Copy explicitly selected local configuration into a linked worktree."""
from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Sequence

from project_state import config_backup as backup
from project_state.paths import _confined_root, confined_target

from . import project_configuration as configuration


def _git(root: Path, *arguments: str) -> str:
    environment = os.environ.copy()
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR', 'GIT_PREFIX',
                'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        environment.pop(key, None)
    result = subprocess.run(['git', '-C', str(root), *arguments], env=environment,
                            capture_output=True, text=True, check=True, timeout=30)
    return result.stdout[:-1] if result.stdout.endswith('\n') else result.stdout


def _identity(project: Path) -> tuple[Path, Path, Path]:
    root = Path(_git(project, 'rev-parse', '--show-toplevel')).resolve()
    directories = []
    for argument in ('--git-common-dir', '--git-dir'):
        directory = Path(_git(project, 'rev-parse', argument))
        directories.append((directory if directory.is_absolute() else project / directory).resolve())
    return root, directories[0], directories[1]


def _verify_worktrees(source: Path, target: Path) -> None:
    source_root, common, _ = _identity(source)
    target_root, target_common, target_git = _identity(target)
    if source_root == target_root or common != target_common or target_git == target_common:
        raise ValueError('configuration copy requires distinct checkouts of the same repository and a linked target')
    registered = {Path(record[len('worktree '):]).resolve()
                  for record in _git(source, 'worktree', 'list', '--porcelain', '-z').split('\0')
                  if record.startswith('worktree ')}
    if source_root not in registered or target_root not in registered:
        raise ValueError('configuration source and target must be registered Git worktrees')
    if source.relative_to(source_root) != target.relative_to(target_root):
        raise ValueError('configuration source and target must name corresponding project directories')


def _files(source: Path, manifest: dict) -> dict[str, tuple[bytes, int]]:
    return {path: (content, stat.S_IMODE(confined_target(source, PurePosixPath(path)).stat().st_mode) & 0o777)
            for path, content in backup.collect(source, manifest, required=True).items()}


def copy_worktree(source: Path, target: Path, paths: Sequence[str], *, check_only: bool = False) -> dict:
    """Copy missing local files without replacing target content or changing Git refs/indexes.

    Callers select the source and complete file scope and hold exclusive access while copying.
    A failure may retain completed files and a partially written current file; inspect those
    paths before retrying. This establishes selected file availability, not host readiness.
    """
    source, target = _confined_root(source), _confined_root(target)
    _verify_worktrees(source, target)
    selected = configuration.binding(source)
    if selected is None or selected.mode not in {'local', 'local-only'}:
        raise ValueError('copy-worktree needs a selected local or local-only source; repository mode uses restoration')
    if not paths:
        raise ValueError('copy-worktree requires explicit --file selections')
    manifest = backup.selected_manifest(source, paths)
    files = _files(source, manifest)
    current_binding = configuration.binding(target)
    if current_binding is None:
        if str(configuration.CONFIG) not in files:
            raise ValueError('select .agents/config.json to carry the source mode, or bind the target first')
    elif current_binding != selected:
        raise ValueError('target maintenance mode differs; preserve it and resolve the source choice before copying')

    missing, conflicts = [], []
    for path, (content, mode) in sorted(files.items()):
        relative = PurePosixPath(path)
        for parent in relative.parents:
            if parent == PurePosixPath('.'):
                continue
            directory = confined_target(target, parent)
            if directory.exists() and not directory.is_dir():
                raise ValueError('target configuration parent is not a directory: ' + str(parent))
        existing = backup.read_file(target, relative)
        if existing is None:
            missing.append(path)
        elif existing != content or (os.name == 'posix' and
                stat.S_IMODE(confined_target(target, relative).stat().st_mode) & 0o777 != mode):
            conflicts.append(path)
    report = {'mode': selected.mode, 'source': str(source), 'target': str(target),
              'scope': manifest, 'missing_paths': missing, 'conflicting_paths': conflicts,
              'copied_paths': [], 'check': 'drift' if missing or conflicts else 'clean'}
    if check_only:
        return report
    if conflicts:
        raise ValueError('configuration copy would replace existing target content or permissions; '
                         'review these paths and narrow or resolve the selected scope: ' + ', '.join(conflicts))
    if _files(source, manifest) != files:
        raise ValueError('source configuration changed before copying')
    _verify_worktrees(source, target)
    attempted = None
    try:
        for path in missing:
            attempted = path
            destination = confined_target(target, PurePosixPath(path))
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination = confined_target(target, PurePosixPath(path))
            content, mode = files[path]
            # Exclusive creation preserves files appearing after the preflight.
            with destination.open('xb') as output:
                output.write(content)
                output.flush()
                if os.name == 'posix':
                    os.fchmod(output.fileno(), mode)
            report['copied_paths'].append(path)
        _verify_worktrees(source, target)
        if _files(source, manifest) != files:
            raise ValueError('source configuration changed during copying')
        for path, (content, mode) in files.items():
            destination = confined_target(target, PurePosixPath(path))
            if (backup.read_file(target, PurePosixPath(path)) != content or
                    (os.name == 'posix' and stat.S_IMODE(destination.stat().st_mode) & 0o777 != mode)):
                raise ValueError('target configuration changed during copying: ' + path)
    except (OSError, ValueError, subprocess.SubprocessError):
        print('Configuration copy incomplete; retain and inspect copied paths '
              + repr(report['copied_paths']) + ' and the last attempted path ' + repr(attempted)
              + ' before retrying. No rollback or overwrite was performed.', file=sys.stderr)
        raise
    report['check'] = 'clean'
    return report
