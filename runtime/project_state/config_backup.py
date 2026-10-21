"""Read complete configuration backups without running maintenance or Git."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

from .catalog import safe_relative
from .paths import confined_target, is_link_like

SYNC_PATH = PurePosixPath('.agents/project-config-sync.json')
DEFAULT_FILES = (
    'AGENTS.md', 'CLAUDE.md', '.agents/config.json', '.codex/config.toml',
    '.cursor/cli.json', '.cursor/mcp.json', '.mcp.json', '.qoder/mcp.json', '.vscode/mcp.json',
)
DEFAULT_DIRECTORIES = (
    '.agents/rules', '.agents/skills', '.agents/agents', '.codex/agents',
    '.codex/rules', '.cursor/rules', '.cursor/agents', '.github/agents', '.qoder/agents', '.qoder/rules',
)


def backup_path(value: str) -> PurePosixPath:
    path = safe_relative(value, 'configuration backup path')
    if (any(part in {'.git', '.codegraph', '__pycache__'} for part in path.parts)
            or path == SYNC_PATH):
        raise ValueError(f'not a configuration backup path: {path}')
    return path


def read_file(root: Path, path: PurePosixPath) -> bytes | None:
    destination = confined_target(root, path)
    if not destination.exists():
        return None
    if not destination.is_file():
        raise ValueError(f'configuration path is not a regular file: {path}')
    return destination.read_bytes()


def read_object(root: Path, path: PurePosixPath) -> dict:
    content = read_file(root, path)
    if content is None:
        raise ValueError(f'configuration document is missing: {path}')
    value = json.loads(content)
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain an object')
    return value


def manifest_paths(manifest: dict) -> tuple[list[str], list[str]]:
    if (set(manifest) != {'files', 'directories'}
            or not isinstance(manifest['files'], list) or not isinstance(manifest['directories'], list)):
        raise ValueError('invalid complete configuration backup manifest')
    files = [str(backup_path(value)) for value in manifest['files']]
    directories = [str(backup_path(value)) for value in manifest['directories']]
    paths = [*files, *directories]
    if len({path.casefold() for path in paths}) != len(paths):
        raise ValueError('duplicate or case-colliding backup paths')
    for directory in directories:
        root = PurePosixPath(directory)
        if root in SYNC_PATH.parents:
            raise ValueError('a backup directory cannot include its local synchronization record')
        if any(root in PurePosixPath(other).parents for other in paths if other != directory):
            raise ValueError('overlapping backup paths')
    return files, directories


def directory_files(root: Path, value: str) -> dict[str, bytes]:
    relative = backup_path(value)
    directory = confined_target(root, relative)
    if not directory.exists():
        return {}
    if not directory.is_dir():
        raise ValueError(f'backup directory is not a regular directory: {value}')
    files = {}
    for item in sorted(directory.rglob('*')):
        if is_link_like(item):
            raise ValueError(f'backup contains a symlink: {item}')
        if item.is_dir():
            continue
        path = backup_path((relative / item.relative_to(directory).as_posix()).as_posix())
        content = read_file(root, path)
        if content is None:
            raise ValueError(f'backup file disappeared while reading: {path}')
        files[str(path)] = content
    return files


def collect(root: Path, manifest: dict, *, required: bool = False) -> dict[str, bytes]:
    files, directories = manifest_paths(manifest)
    result = {}
    for value in files:
        content = read_file(root, backup_path(value))
        if content is None:
            if required:
                raise ValueError(f'source configuration file is missing: {value}')
        else:
            result[value] = content
    for value in directories:
        result.update(directory_files(root, value))
    if len({path.casefold() for path in result}) != len(result):
        raise ValueError('case-colliding backup files')
    return result


def fingerprint(manifest: dict, files: Mapping[str, bytes]) -> str:
    value = {'manifest': manifest, 'files': {
        path: hashlib.sha256(content).hexdigest() for path, content in sorted(files.items())}}
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def read_backup(entry: Path) -> tuple[dict, dict[str, bytes]]:
    manifest = read_object(entry, PurePosixPath('manifest.json'))
    return manifest, collect(entry / 'files', manifest, required=True)


def selected_manifest(target: Path, paths: Sequence[str]) -> dict:
    files, directories = [], []
    selections = paths or [*DEFAULT_FILES, *DEFAULT_DIRECTORIES]
    for value in selections:
        path = backup_path(value)
        destination = confined_target(target, path)
        if not destination.exists():
            if paths:
                raise ValueError(f'selected backup path does not exist: {path}')
            continue
        (directories if destination.is_dir() else files).append(str(path))
    manifest = {'files': sorted(files), 'directories': sorted(directories)}
    manifest_paths(manifest)
    return manifest


def read_receipt(target: Path, selected: dict) -> dict | None:
    if read_file(target, SYNC_PATH) is None:
        return None
    state = read_object(target, SYNC_PATH)
    if (set(state) != {'binding', 'source', 'sourceFingerprint', 'appliedPaths', 'automatic'}
            or state['binding'] != selected
            or not isinstance(state['source'], str) or not Path(state['source']).is_absolute()
            or not isinstance(state['automatic'], bool) or not isinstance(state['appliedPaths'], list)):
        raise ValueError('project configuration synchronization record is invalid or belongs to another binding')
    digest = state['sourceFingerprint']
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('invalid configuration source fingerprint')
    for value in state['appliedPaths']:
        backup_path(value)
    return state
