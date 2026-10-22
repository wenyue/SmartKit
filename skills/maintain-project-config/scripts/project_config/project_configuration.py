"""Back up and restore complete project configuration files.

Repository scope is authoritative; setup rendering keeps its own checks.
"""
from __future__ import annotations

import difflib
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

from project_state import config_backup as backup
from project_state.paths import confined_target

from . import repository
from .catalog import parse_maintenance
from .models import ChangeKind, DesiredFile, MaintenanceConfig, Plan
from .planner import build_plan
from .transaction import TransactionError, apply_plan

CONFIG = PurePosixPath('.agents/config.json')
STATE = backup.SYNC_PATH


@dataclass(frozen=True)
class _BackupUpdate:
    root: Path
    plan: Plan
    original: DesiredFile


@dataclass(frozen=True)
class ConfigurationUpdate:
    """Frozen final config and receipt writes, with an optional backed-up config.

    The caller keeps exclusive access through apply and recovery. Handled failures
    restore owned writes; TransactionError retains failed rollback diagnostics and
    third-party changes. Earlier generated-source writes are outside this update.
    """
    target: Path
    plan: Plan
    source_fingerprint: str | None
    backup_update: _BackupUpdate | None

    def apply(self) -> list[str]:
        restore_plan: Plan | None = None
        source_committed = False
        source_error: TransactionError | None = None

        def verify() -> None:
            if require_converged(self.target) != self.source_fingerprint:
                raise ValueError('configuration source changed during final configuration update')

        def commit_backup() -> None:
            nonlocal restore_plan, source_committed, source_error
            if self.backup_update is None:
                verify()
                return
            update = self.backup_update

            def source_postcondition() -> None:
                nonlocal restore_plan
                verify()
                # Capture the owned postimage before the source transaction verifies it.
                restore_plan = build_plan(update.root, [update.original])

            try:
                apply_plan(update.root, update.plan, postcondition=source_postcondition)
            except TransactionError as error:
                source_error = error
                raise
            source_committed = True

        try:
            apply_plan(self.target, self.plan, postcondition=commit_backup)
        except TransactionError as error:
            # The outer transaction unwraps nested errors; retain source rollback failures.
            rollback_errors = [*(source_error.rollback_errors if source_error else ()), *error.rollback_errors]
            if source_committed:
                assert self.backup_update is not None and restore_plan is not None
                try:
                    apply_plan(self.backup_update.root, restore_plan)
                except TransactionError as rollback_error:
                    rollback_errors.append(rollback_error)
            if rollback_errors:
                raise TransactionError(error.original_error, tuple(rollback_errors)) from error
            raise
        return [str(change.path) for change in self.plan.changes if change.kind is not ChangeKind.UNCHANGED]


def prepare_config_update(target: Path, content: bytes) -> ConfigurationUpdate:
    """Freeze a config update and its backup/receipt without changing storage."""
    desired = [DesiredFile(CONFIG, content)]
    source_fingerprint: str | None = None
    backup_update: _BackupUpdate | None = None
    selected = binding(target)
    if selected is not None and selected.mode == 'repository':
        entry, files, state, report = _observe(target)
        if report['changes']:
            raise ValueError('configuration source or target changed before final configuration update')
        if str(CONFIG) in files:
            source_path = PurePosixPath('files') / CONFIG
            original = DesiredFile(source_path, files[str(CONFIG)])
            if original.content != content:
                backup_update = _BackupUpdate(entry, build_plan(entry, [DesiredFile(source_path, content)]), original)
            files[str(CONFIG)] = content
        manifest = report['scope']
        source_fingerprint = backup.fingerprint(manifest, files)
        desired.append(_state_file(target, entry, manifest, files, automatic=state['automatic']))
    return ConfigurationUpdate(target, build_plan(target, desired), source_fingerprint, backup_update)


def _json(content: object) -> bytes:
    return (json.dumps(content, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')


def _document(root: Path, relative: PurePosixPath, *, missing: bool = False) -> dict:
    if missing and _read(root, relative) is None:
        return {}
    return backup.read_object(root, relative)


def binding(target: Path) -> MaintenanceConfig | None:
    return parse_maintenance(_document(target, CONFIG, missing=True).get('maintenance'))


def binding_document(value: MaintenanceConfig) -> dict:
    return {key: item for key, item in asdict(value).items() if item is not None}


def entry_root(target: Path) -> Path:
    value = binding(target)
    if value is None or value.mode != 'repository':
        raise ValueError('project has no repository maintenance binding; bind the selected source first')
    return confined_target(repository.open_checkout(value.repository, value.branch), PurePosixPath('projects') / value.entry)


def _source_path(value: str) -> PurePosixPath:
    return backup.backup_path(value)


def _read(root: Path, path: PurePosixPath) -> bytes | None:
    return backup.read_file(root, path)


def _digest(content: bytes | None) -> str | None:
    return hashlib.sha256(content).hexdigest() if content is not None else None


def _state(target: Path) -> dict:
    selected = binding_document(binding(target))
    state = backup.read_receipt(target, selected)
    if state is not None:
        return state
    return {'binding': selected, 'source': str(entry_root(target)),
            'sourceFingerprint': None, 'appliedPaths': [], 'automatic': False}


def _state_file(target: Path, entry: Path, manifest: dict, files: Mapping[str, bytes],
                *, automatic: bool = False) -> DesiredFile:
    selected = binding_document(binding(target))
    if str(CONFIG) in files:
        selected = json.loads(files[str(CONFIG)])['maintenance']
    return DesiredFile(STATE, _json({'binding': selected,
        'source': str(entry), 'sourceFingerprint': backup.fingerprint(manifest, files),
        'appliedPaths': sorted(files), 'automatic': automatic}))


def initialize_entry(target: Path, entry: Path, paths: Sequence[str], *,
                     config_content: bytes | None = None) -> None:
    """Capture selected files/directories, or existing default configuration paths."""
    if any(entry.iterdir()):
        raise ValueError('configuration entry is not empty; inspect and connect the existing entry')
    selections = [path for path in paths if not (path == str(CONFIG) and config_content is not None)]
    manifest = (backup.selected_manifest(target, selections) if selections or not paths
                else {'files': [], 'directories': []})
    files = backup.collect(target, manifest, required=True)
    if config_content is not None and (not paths or str(CONFIG) in paths):
        files[str(CONFIG)] = config_content
        if str(CONFIG) not in manifest['files']:
            manifest['files'].append(str(CONFIG))
            manifest['files'].sort()
    desired = [DesiredFile(PurePosixPath('files') / path, content) for path, content in files.items()]
    desired.append(DesiredFile(PurePosixPath('manifest.json'), _json(manifest)))
    apply_plan(entry, build_plan(entry, desired), postcondition=lambda: backup.read_backup(entry))


def _observe(target: Path) -> tuple[Path, dict, dict, dict]:
    entry = entry_root(target)
    manifest, files = backup.read_backup(entry)
    state = _state(target)
    paths = set(files) | set(state['appliedPaths'])
    paths.update(backup.collect(target, manifest))
    current = {path: _read(target, _source_path(path)) for path in paths}
    target_config = _document(target, CONFIG, missing=True)
    if str(CONFIG) in files:
        source_config = json.loads(files[str(CONFIG)])
        source_binding = parse_maintenance(source_config.get('maintenance')) if isinstance(source_config, dict) else None
        selected = binding(target)
        if (source_binding is None or source_binding.mode != 'repository'
                or source_binding.branch != selected.branch or source_binding.entry != selected.entry
                or repository.validate_repository(source_binding.repository).casefold()
                != repository.validate_repository(selected.repository).casefold()):
            raise ValueError('backed-up .agents/config.json must retain the selected maintenance binding')
    conflicts, changes, diffs = [], [], {}
    for path, actual in sorted(current.items()):
        desired = files.get(path)
        if actual == desired:
            continue
        changes.append(path)
        conflicts.append(path)
        try:
            diffs[path] = ''.join(difflib.unified_diff(
                (actual or b'').decode('utf-8').splitlines(True), (desired or b'').decode('utf-8').splitlines(True),
                fromfile='target/' + path, tofile='source/' + path))
            if not diffs[path]:
                diffs[path] = 'File added' if actual is None else 'File deleted'
        except UnicodeDecodeError:
            diffs[path] = 'Binary file differs'
    observation = {'source': str(entry), 'changes': changes, 'conflicts': conflicts, 'diffs': diffs,
                   'source_fingerprint': backup.fingerprint(manifest, files),
                   'automatic': state['automatic'], 'scope': manifest}
    observation['fingerprint'] = _digest(_json({'observation': observation,
        'current': {path: _digest(content) for path, content in current.items()}, 'config': target_config, 'state': state}))
    return entry, files, state, observation


def inspect(target: Path) -> dict:
    """Read backup scope and drift without fetching, parsing native files or writing."""
    selected = binding(target)
    if selected is None or selected.mode != 'repository':
        return {'mode': selected.mode if selected else 'unselected', 'selection_required': selected is None}
    return {'mode': 'repository', **_observe(target)[3]}


def require_converged(target: Path) -> str | None:
    report = inspect(target)
    if report['mode'] != 'repository':
        return None
    if report['changes']:
        raise ValueError('project configuration differs from its source; inspect/apply or explicitly adopt before continuing')
    return report['source_fingerprint']


def apply(target: Path, *, accept_existing: str | None = None,
          automatic: bool | None = None) -> dict:
    """Restore selected files only after exact inspection acceptance of any differences."""
    entry, files, state, report = _observe(target)
    if accept_existing is not None and accept_existing != report['fingerprint']:
        raise ValueError('reviewed configuration fingerprint changed')
    if report['conflicts'] and accept_existing != report['fingerprint']:
        raise ValueError('project configuration conflict; inspect differences and choose keep local or '
                         'use the configuration repository before accepting the exact restoration: '
                         + ', '.join(report['conflicts']))
    automatic = state['automatic'] if automatic is None else automatic
    if (not report['changes'] and state['sourceFingerprint'] == report['source_fingerprint']
            and automatic == state['automatic']):
        return {'mode': 'repository', 'applied': False, 'skipped': True, 'source': str(entry),
                'managed_paths': sorted([*files, str(STATE)]), 'changed_paths': []}
    desired, deletes = [], []
    for path in sorted(set(files) | set(state['appliedPaths'])):
        relative = _source_path(path)
        content = files.get(path)
        if content is None:
            deletes.append(relative)
        else:
            desired.append(DesiredFile(relative, content))
    manifest = report['scope']
    desired.append(_state_file(target, entry, manifest, files, automatic=automatic))
    directories = manifest['directories']
    plan = build_plan(target, desired, delete_paths=deletes,
                      replace_roots=[PurePosixPath(value) for value in directories])
    if _observe(target)[3]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed while planning')
    def postcondition() -> None:
        after = _observe(target)[3]
        if after['changes'] or after['source_fingerprint'] != report['source_fingerprint']:
            raise ValueError('configuration changed during application')
    apply_plan(target, plan, postcondition=postcondition)
    return {'mode': 'repository', 'applied': True, 'skipped': False, 'source': str(entry),
            'managed_paths': sorted([*files, str(CONFIG), str(STATE)]),
            'changed_paths': [str(item.path) for item in plan.changes if item.kind is not ChangeKind.UNCHANGED]}


def adopt(target: Path, paths: Sequence[str], *,
          all_paths: bool = False) -> dict:
    """Back up explicitly accepted target files after updating the repository."""
    entry, files, _, report = _observe(target)
    if not paths and not all_paths:
        raise ValueError('adoption requires explicit files or --all')
    if all_paths and paths:
        raise ValueError('--all cannot be combined with selected files')
    manifest = report['scope']
    if all_paths:
        files = backup.collect(target, manifest)
        manifest['files'] = [path for path in manifest['files'] if path in files]
    else:
        for value in paths:
            relative = _source_path(value)
            destination = confined_target(target, relative)
            selected = str(relative)
            for old in list(files):
                if old == selected or relative in PurePosixPath(old).parents:
                    files.pop(old)
            if destination.is_dir():
                files.update(backup.directory_files(target, selected))
                covered = any(directory == selected or PurePosixPath(directory) in relative.parents
                              for directory in manifest['directories'])
                if not covered:
                    manifest['directories'] = [directory for directory in manifest['directories']
                                              if relative not in PurePosixPath(directory).parents]
                    manifest['directories'].append(selected)
                manifest['files'] = [path for path in manifest['files'] if relative not in PurePosixPath(path).parents]
            else:
                content = _read(target, relative)
                if content is not None:
                    files[selected] = content
                covered = any(PurePosixPath(directory) in relative.parents for directory in manifest['directories'])
                if not covered:
                    manifest['files'] = [path for path in manifest['files'] if path != selected]
                    if content is not None:
                        manifest['files'].append(selected)
    desired = [DesiredFile(PurePosixPath('files') / path, content) for path, content in files.items()]
    desired.append(DesiredFile(PurePosixPath('manifest.json'), _json(manifest)))
    deletes = [PurePosixPath('files') / path for path in backup.read_backup(entry)[1] if path not in files]
    if _observe(target)[3]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed during backup planning')
    apply_plan(entry, build_plan(entry, desired, delete_paths=deletes), postcondition=lambda: backup.read_backup(entry))
    return {'adopted': sorted(files) if all_paths else list(paths), 'source': str(entry)}


def save_generated(target: Path, outputs: Mapping[str, bytes], retired: Sequence[str], *,
                   target_outputs: Mapping[str, bytes] | None = None) -> DesiredFile | None:
    """Save accepted setup outputs before their guarded target transaction."""
    selected = binding(target)
    if selected is None or selected.mode != 'repository':
        return None
    entry, files, state, report = _observe(target)
    if report['changes']:
        raise ValueError('configuration source or target changed before generated handoff')
    manifest = report['scope']
    updates = dict(outputs)
    updates.update({path: content for path, content in (target_outputs or {}).items()
                    if path in files or path in backup.DEFAULT_FILES
                    or any(PurePosixPath(directory) in PurePosixPath(path).parents
                           for directory in (*manifest['directories'], *backup.DEFAULT_DIRECTORIES))})
    for value, content in updates.items():
        _source_path(value)
        files[value] = content
        if value not in manifest['files'] and not any(
                PurePosixPath(directory) in PurePosixPath(value).parents for directory in manifest['directories']):
            manifest['files'].append(value)
    for value in retired:
        if value not in updates:
            files.pop(value, None)
    manifest['files'] = sorted(path for path in manifest['files'] if path in files)
    desired = [DesiredFile(PurePosixPath('files') / path, content) for path, content in files.items()]
    desired.append(DesiredFile(PurePosixPath('manifest.json'), _json(manifest)))
    deletes = [PurePosixPath('files') / path for path in backup.read_backup(entry)[1] if path not in files]
    if _observe(target)[3]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed before generated handoff')
    apply_plan(entry, build_plan(entry, desired, delete_paths=deletes), postcondition=lambda: backup.read_backup(entry))
    return _state_file(target, entry, manifest, files, automatic=state['automatic'])
