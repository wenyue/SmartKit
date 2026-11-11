"""Link project Agent configuration into a worktree, retaining copy origins."""
from __future__ import annotations

import argparse
import errno
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Sequence


RECORD = 'smartkit-worktree-configuration.json'
SKIP_NAMES = {'.git', '.hg', '.svn', '.codegraph', '__pycache__', '.pytest_cache',
              '.mypy_cache', '.ruff_cache', '.cache', '.venv', 'node_modules', '.DS_Store'}
LOCAL_STATE = {'.agents/project-config-sync.json', 'openwiki/.run.json'}
LINK_UNAVAILABLE = {errno.EPERM, errno.EACCES, errno.ENOSYS, errno.EOPNOTSUPP}
REPARSE_POINT = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)


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
    registered = {Path(part[len('worktree '):]).resolve()
                  for part in _git(project, 'worktree', 'list', '--porcelain', '-z').split('\0')
                  if part.startswith('worktree ')}
    if root not in registered:
        raise ValueError('project is not in a registered Git worktree')
    return root, directories[0], directories[1]


def _relative(value: str, *, project: bool = False) -> PurePosixPath:
    if not isinstance(value, str) or not value or any(char in value for char in '\\\0\r\n:'):
        raise ValueError('configuration paths must be nonempty relative POSIX paths')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value or (path == PurePosixPath('.') and not project):
        raise ValueError('invalid project-relative configuration path: ' + value)
    return path


def _ignored(path: PurePosixPath) -> bool:
    return any(part in SKIP_NAMES for part in path.parts) or str(path) in LOCAL_STATE


def _redirected(path: Path) -> bool:
    try:
        status = path.lstat()
    except FileNotFoundError:
        return False
    # Python 3.8 does not classify Windows junctions as symbolic links.
    return stat.S_ISLNK(status.st_mode) or bool(getattr(status, 'st_file_attributes', 0) & REPARSE_POINT)


def _reject_redirected(path: Path) -> None:
    for item in (path.absolute(), *path.absolute().parents):
        if _redirected(item):
            raise ValueError('configuration destination is redirected: ' + str(item))


def _destination(target: Path, relative: PurePosixPath) -> Path:
    result = target / relative
    for parent in relative.parents:
        directory = target / parent
        if _redirected(directory) or (directory.exists() and not directory.is_dir()):
            raise ValueError('target configuration parent is not a local directory: ' + str(directory))
    if _redirected(result) and not result.is_symlink():
        raise ValueError('target configuration is a reparse point: ' + str(result))
    return result


def _mode(project: Path) -> str:
    value = json.loads((project / '.agents/config.json').read_text(encoding='utf-8'))
    maintenance = value.get('maintenance') if isinstance(value, dict) else None
    mode = maintenance.get('mode') if isinstance(maintenance, dict) else None
    if mode not in {'local', 'local-only', 'repository'}:
        raise ValueError('source configuration needs a selected maintenance mode')
    return mode


def _read_record(path: Path) -> dict:
    _reject_redirected(path)
    if not path.exists():
        return {'projects': {}}
    if not path.is_file():
        raise ValueError('configuration origin record must be a regular file')
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or set(value) != {'projects'} or not isinstance(value['projects'], dict):
        raise ValueError('invalid configuration origin record')
    for relative, entry in value['projects'].items():
        _relative(relative, project=True)
        if (not isinstance(entry, dict) or set(entry) != {'source', 'paths'}
                or not isinstance(entry['source'], str) or not Path(entry['source']).is_absolute()
                or not isinstance(entry['paths'], dict)):
            raise ValueError('invalid project configuration origin')
        for item, method in entry['paths'].items():
            if _ignored(_relative(item)) or method not in {'link', 'copy'}:
                raise ValueError('invalid configuration origin path or method')
    return value


def _write_record(path: Path, value: dict) -> None:
    _reject_redirected(path)
    descriptor, temporary = tempfile.mkstemp(prefix=RECORD + '.', dir=str(path.parent))
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            json.dump(value, output, indent=2)
            output.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _source_tree(source: Path, relative: PurePosixPath) -> dict[str, tuple[Path, int]]:
    selected = source / relative
    anchor = selected.resolve(strict=True)
    entries = {}

    def visit(path: Path, name: PurePosixPath, ancestors: set[Path]) -> None:
        if _ignored(name):
            return
        physical = path.resolve(strict=True)
        if selected.is_dir() and physical != anchor and anchor not in physical.parents:
            raise ValueError('copy source link leaves the selected directory: ' + str(name))
        if path.is_dir():
            if physical in ancestors:
                raise ValueError('configuration directory contains a link cycle: ' + str(name))
            entries[str(name)] = (physical, stat.S_IMODE(physical.stat().st_mode) & 0o777)
            for child in sorted(path.iterdir()):
                visit(child, name / child.name, ancestors | {physical})
        elif path.is_file():
            entries[str(name)] = (physical, stat.S_IMODE(physical.stat().st_mode) & 0o777)
        else:
            raise ValueError('configuration source is not a regular file or directory: ' + str(name))

    visit(selected, relative, set())
    return entries


def _copy_missing(source: Path, target: Path, relative: PurePosixPath) -> None:
    entries = _source_tree(source, relative)
    for name, (original, mode) in entries.items():
        destination = _destination(target, PurePosixPath(name))
        if original.is_dir():
            if _redirected(destination) or (destination.exists() and (not destination.is_dir()
                    or (os.name == 'posix' and stat.S_IMODE(destination.stat().st_mode) & 0o777 != mode))):
                raise ValueError('configuration directory conflicts with existing target: ' + name)
            continue
        if _redirected(destination) or (destination.exists() and (
                not destination.is_file() or destination.read_bytes() != original.read_bytes()
                or (os.name == 'posix' and stat.S_IMODE(destination.stat().st_mode) & 0o777 != mode))):
            raise ValueError('configuration copy conflicts with existing target: ' + name)
    created_directories = []
    for name, (original, mode) in entries.items():
        destination = _destination(target, PurePosixPath(name))
        if original.is_dir():
            if not destination.exists():
                destination.mkdir(parents=True)
                created_directories.append((destination, mode))
            continue
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation preserves a file appearing after the comparison.
        with original.open('rb') as input_file, destination.open('xb') as output:
            shutil.copyfileobj(input_file, output)
            if os.name == 'posix':
                os.fchmod(output.fileno(), mode)
        if destination.read_bytes() != original.read_bytes():
            raise ValueError('source configuration changed while copying: ' + name)
    if os.name == 'posix':
        for directory, mode in reversed(created_directories):
            _reject_redirected(directory)
            directory.chmod(mode)


def _exclude(target: Path, root: Path, paths: Sequence[PurePosixPath]) -> None:
    relative_project = target.relative_to(root)
    ignore = Path(_git(target, 'rev-parse', '--git-path', 'info/exclude'))
    ignore = ignore if ignore.is_absolute() else target / ignore
    _reject_redirected(ignore)
    original = ignore.read_bytes() if ignore.exists() else b''
    patterns = []
    for path in paths:
        try:
            _git(target, 'check-ignore', '--quiet', '--no-index', '--', str(path))
            continue
        except subprocess.CalledProcessError as error:
            if error.returncode != 1:
                raise
        # A rule without a trailing slash also excludes a directory symlink node.
        name = (relative_project / str(path)).as_posix()
        pattern = '/' + ''.join('\\' + char if char in '\\*?[]!# ' else char for char in name)
        encoded = pattern.encode('utf-8')
        patterns.append(encoded)
    if patterns:
        ignore.parent.mkdir(parents=True, exist_ok=True)
        with ignore.open('ab') as output:
            if original and not original.endswith(b'\n'):
                output.write(b'\n')
            output.write(b'\n'.join(patterns) + b'\n')


def prepare(source: Path, target: Path, selections: Sequence[str], *, copy_only: bool = False) -> dict:
    """Prepare selected configuration; failures retain paths and their origin record."""
    source, target = source.resolve(strict=True), target.resolve(strict=True)
    source_root, common, _ = _identity(source)
    target_root, target_common, target_git = _identity(target)
    if source_root == target_root or common != target_common or target_git == target_common:
        raise ValueError('configuration preparation needs distinct same-repository checkouts and a linked target')
    project = source.relative_to(source_root).as_posix()
    if project != target.relative_to(target_root).as_posix():
        raise ValueError('source and target must name corresponding project directories')
    paths = [_relative(value) for value in selections]
    if not paths or len(set(paths)) != len(paths):
        raise ValueError('select distinct required configuration paths')
    for path in paths:
        if (_ignored(path) or any(path in PurePosixPath(state).parents for state in LOCAL_STATE)
                or any(path in other.parents for other in paths if path != other)):
            raise ValueError('select nonoverlapping configuration paths without worktree state: ' + str(path))
        if not (source / path).is_file() and not (source / path).is_dir():
            raise ValueError('required source configuration is missing: ' + str(path))
    mode = _mode(source)
    if _destination(target, PurePosixPath('.agents/config.json')).exists() and _mode(target) != mode:
        raise ValueError('source and target configuration modes differ')
    if mode == 'local':
        if any(not (target / path).exists() for path in paths):
            raise ValueError('Git-shared configuration is missing from the target; no configuration was transferred')
        return {'mode': mode, 'source': str(source), 'target': str(target), 'paths': {}, 'transferred': False}
    record_path = target_git / RECORD
    record = _read_record(record_path)
    entry = record['projects'].get(project, {'source': str(source), 'paths': {}})
    if entry['source'] != str(source):
        raise ValueError('target configuration already records a different source')
    for path in paths:
        name = str(path)
        destination = _destination(target, path)
        for known in entry['paths']:
            other = PurePosixPath(known)
            if path != other and (path in other.parents or other in path.parents):
                raise ValueError('selection overlaps an existing origin; reuse its recorded root: ' + known)
        if _git(target, '--literal-pathspecs', 'ls-files', '--', name):
            raise ValueError('preserve tracked configuration; narrow the selected scope: ' + name)
        if destination.exists() or destination.is_symlink():
            if name not in entry['paths']:
                raise ValueError('preserve existing target configuration; narrow the selected scope: ' + name)
            if destination.is_symlink():
                if destination.resolve() != (source / path).resolve():
                    raise ValueError('configuration link no longer matches its recorded source: ' + name)
            elif entry['paths'][name] == 'link':
                raise ValueError('recorded configuration link was replaced: ' + name)
    _exclude(target, target_root, paths)
    record['projects'][project] = entry
    for path in paths:
        name = str(path)
        destination = _destination(target, path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        method = 'copy' if copy_only or entry['paths'].get(name) == 'copy' else 'link'
        entry['paths'][name] = method
        _write_record(record_path, record)
        if method == 'link':
            if destination.is_symlink():
                continue
            try:
                destination.symlink_to(source / path, target_is_directory=(source / path).is_dir())
                continue
            except OSError as error:
                if error.errno not in LINK_UNAVAILABLE and getattr(error, 'winerror', None) != 1314:
                    raise
                # These failures leave no link; a regular copy preserves the same selected input.
                entry['paths'][name] = 'copy'
                _write_record(record_path, record)
        if destination.is_symlink():
            destination.unlink()
        _copy_missing(source, target, path)
    return {'mode': mode, 'source': str(source), 'target': str(target),
            'paths': {str(path): entry['paths'][str(path)] for path in paths}, 'transferred': True}


def inspect(target: Path) -> dict:
    """Read all project origins in the selected worktree, including missing sources."""
    root, common, git_dir = _identity(target.resolve(strict=True))
    record_path = git_dir / RECORD
    projects = []
    for relative, entry in _read_record(record_path)['projects'].items():
        source = Path(entry['source'])
        available = False
        try:
            source_root, source_common, _ = _identity(source)
            available = (source_root != root and source_common == common
                         and source.relative_to(source_root).as_posix() == relative)
        except (OSError, ValueError, subprocess.SubprocessError):
            # Inspection keeps the stored origin visible when its checkout is gone or unavailable.
            pass
        projects.append({'target': str(root / relative), 'source': str(source),
                         'source_available': available, 'paths': entry['paths']})
    return {'worktree': str(root), 'record': str(record_path), 'projects': projects}


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest='operation', required=True)
    command = commands.add_parser('prepare', help='Link selected configuration, copying when links are unavailable')
    command.add_argument('--source', type=Path, required=True)
    command.add_argument('--target', type=Path, required=True)
    command.add_argument('--path', action='append', required=True, help='Required project-relative file or directory; repeat')
    command.add_argument('--copy', action='store_true', help='Use after an observed host rejection of links; converts only recorded matching links')
    command = commands.add_parser('inspect', help='Read all configuration origins in a worktree without changing files')
    command.add_argument('--target', type=Path, required=True)
    args = parser.parse_args(arguments)
    try:
        if args.operation == 'prepare':
            result = prepare(args.source, args.target, args.path, copy_only=args.copy)
        else:
            result = inspect(args.target)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        if args.operation == 'prepare':
            print('Preparation incomplete. Preserve existing paths and inspect the origin record before retrying.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
