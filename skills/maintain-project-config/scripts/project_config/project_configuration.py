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
WIKI_FILES = ('AGENTS.md', 'CLAUDE.md', '.openwikiignore')
WIKI_DIRECTORY = PurePosixPath('openwiki')
WIKI_STORAGE = PurePosixPath('wiki')


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


def _wiki_path(path: PurePosixPath) -> bool:
    return str(path) in WIKI_FILES or WIKI_DIRECTORY in path.parents


def _read_snapshot(entry: Path, *, wiki: bool) -> tuple[dict, dict[str, bytes]]:
    if wiki and not entry.exists():
        return {'files': [], 'directories': []}, {}
    if wiki:
        manifest = _document(entry, PurePosixPath('manifest.json'))
        files, directories = backup.manifest_paths(manifest)
        if set(files) - set(WIKI_FILES) or set(directories) - {str(WIKI_DIRECTORY)}:
            raise ValueError('nested OpenWiki backup contains paths outside the Wiki scope')
        return manifest, backup.collect(entry / 'files', manifest, required=True)
    return backup.read_backup(entry)


def _state(target: Path, entry: Path, *, wiki_root: Path | None) -> dict:
    selected = binding_document(binding(target))
    path = backup.WIKI_SYNC_PATH if wiki_root else STATE
    state = backup.read_receipt(wiki_root or target, selected, path=path)
    if state is not None:
        if wiki_root and (state['source'] != str(entry) or state['automatic'] or any(
                not _wiki_path(_source_path(value)) for value in state['appliedPaths'])):
            raise ValueError('OpenWiki synchronization record is invalid or belongs to another project')
        return state
    return {'binding': selected, 'source': str(entry),
            'sourceFingerprint': None, 'appliedPaths': [], 'automatic': False}


def _state_file(target: Path, entry: Path, manifest: dict, files: Mapping[str, bytes],
                *, automatic: bool = False, wiki: bool = False) -> DesiredFile:
    selected = binding_document(binding(target))
    if str(CONFIG) in files:
        selected = json.loads(files[str(CONFIG)])['maintenance']
    return DesiredFile(backup.WIKI_SYNC_PATH if wiki else STATE, _json({'binding': selected,
        'source': str(entry), 'sourceFingerprint': backup.fingerprint(manifest, files),
        'sourceManifest': manifest, 'appliedPaths': sorted(files), 'automatic': automatic}))


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


def _observe(target: Path, *, wiki_root: Path | None = None) -> tuple[Path, dict, dict, dict]:
    entry = entry_root(target)
    if wiki_root:
        entry = confined_target(entry, WIKI_STORAGE)
        if _read(wiki_root, WIKI_DIRECTORY / '.run.json') is not None:
            raise ValueError('finish the active OpenWiki run before restoring or adopting the Wiki')
    manifest, files = _read_snapshot(entry, wiki=wiki_root is not None)
    state = _state(target, entry, wiki_root=wiki_root)
    if wiki_root and state['sourceFingerprint'] is not None and not entry.exists():
        raise ValueError('the previously applied OpenWiki backup is missing')
    local_root = wiki_root or target
    previous_manifest = state.get('sourceManifest')
    previous_files = backup.collect(local_root, previous_manifest) if previous_manifest is not None else {}
    # Review local additions in retired scope before saving or explicitly removing them.
    paths = set(files) | set(state['appliedPaths']) | set(previous_files)
    paths.update(backup.collect(local_root, manifest))
    current = {path: _read(local_root, _source_path(path)) for path in paths}
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
    source_fingerprint = backup.fingerprint(manifest, files)
    previous_fingerprint = state['sourceFingerprint']
    source_changed = previous_fingerprint is not None and previous_fingerprint != source_fingerprint
    # Retain the old scope: the new manifest can hide local edits or include existing local files.
    source_updates_only = (bool(changes) and source_changed and previous_manifest is not None
                           and backup.fingerprint(previous_manifest, previous_files) == previous_fingerprint
                           and all(path in previous_files or current[path] is None for path in changes))
    observation = {'source': str(entry), 'changes': changes, 'conflicts': conflicts, 'diffs': diffs,
                   'source_fingerprint': source_fingerprint,
                   'source_changed_since_sync': source_changed,
                   'source_updates_only': source_updates_only,
                   'local_updates_only': bool(changes) and previous_fingerprint == source_fingerprint,
                   'automatic': state['automatic'], 'scope': manifest}
    if wiki_root:
        observation['wiki_root'] = str(wiki_root)
    observation['fingerprint'] = _digest(_json({'observation': observation,
        'current': {path: _digest(content) for path, content in current.items()}, 'config': target_config, 'state': state}))
    return entry, files, state, observation


def inspect(target: Path, *, wiki_root: Path | None = None) -> dict:
    """Read backup scope and drift without fetching, parsing native files or writing."""
    selected = binding(target)
    if selected is None or selected.mode != 'repository':
        return {'mode': selected.mode if selected else 'unselected', 'selection_required': selected is None}
    return {'mode': 'repository', **_observe(target, wiki_root=wiki_root)[3]}


def reconcile(target: Path, *, adopt_local: bool = False, accept_plan: str | None = None) -> dict:
    """Classify drift against the last agreement; plan only authorized local saves."""
    report = inspect(target)
    if report['mode'] != 'repository':
        raise ValueError('reconciliation needs a repository maintenance binding')
    if accept_plan is not None and not (adopt_local and report['local_updates_only']):
        raise ValueError('reviewed local adoption plan is no longer available')
    if not report['changes']:
        return {'status': 'in-sync', **report}
    if report['source_updates_only']:
        return {'status': 'source-updated', **report}
    if not (adopt_local and report['local_updates_only']):
        return {'status': 'needs-choice', **report}
    preview = accept_plan is None
    result = adopt(target, report['changes'], accept_existing=report['fingerprint'],
                   preview=preview, accept_plan=accept_plan)
    return {'status': 'planned' if preview else 'adopted', **result}


def require_converged(target: Path, *, wiki_root: Path | None = None) -> str | None:
    report = inspect(target, wiki_root=wiki_root)
    if report['mode'] != 'repository':
        return None
    if report['changes']:
        raise ValueError('project configuration differs from its source; inspect/apply or explicitly adopt before continuing')
    return report['source_fingerprint']


def apply(target: Path, *, accept_existing: str | None = None,
          automatic: bool | None = None, wiki_root: Path | None = None) -> dict:
    """Restore selected files only after exact inspection acceptance of any differences."""
    entry, files, state, report = _observe(target, wiki_root=wiki_root)
    if accept_existing is not None and accept_existing != report['fingerprint']:
        raise ValueError('reviewed configuration fingerprint changed')
    if report['conflicts'] and accept_existing != report['fingerprint']:
        raise ValueError('project configuration conflict; inspect differences and choose keep local or '
                         'use the configuration repository before accepting the exact restoration: '
                         + ', '.join(report['conflicts']))
    automatic = state['automatic'] if automatic is None else automatic
    receipt = backup.WIKI_SYNC_PATH if wiki_root else STATE
    receipt_matches = (state['sourceFingerprint'] == report['source_fingerprint']
                       and state.get('sourceManifest') == report['scope'] and automatic == state['automatic'])
    if not report['changes'] and (receipt_matches or (wiki_root and not entry.exists())):
        return {'mode': 'repository', 'applied': False, 'skipped': True, 'source': str(entry),
                'managed_paths': sorted([*files, str(receipt)]), 'changed_paths': []}
    desired, deletes = [], []
    for path in sorted(set(files) | set(state['appliedPaths']) | set(report['changes'])):
        relative = _source_path(path)
        content = files.get(path)
        if content is None:
            deletes.append(relative)
        else:
            desired.append(DesiredFile(relative, content))
    manifest = report['scope']
    desired.append(_state_file(target, entry, manifest, files, automatic=automatic, wiki=wiki_root is not None))
    directories = manifest['directories']
    plan = build_plan(wiki_root or target, desired, delete_paths=deletes,
                      replace_roots=[PurePosixPath(value) for value in directories])
    if _observe(target, wiki_root=wiki_root)[3]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed while planning')
    def postcondition() -> None:
        after = _observe(target, wiki_root=wiki_root)[3]
        if after['changes'] or after['source_fingerprint'] != report['source_fingerprint']:
            raise ValueError('configuration changed during application')
    apply_plan(wiki_root or target, plan, postcondition=postcondition)
    return {'mode': 'repository', 'applied': True, 'skipped': False, 'source': str(entry),
            'managed_paths': sorted([*files, str(receipt), *([] if wiki_root else [str(CONFIG)])]),
            'changed_paths': [str(item.path) for item in plan.changes if item.kind is not ChangeKind.UNCHANGED]}


def adopt(target: Path, paths: Sequence[str], *,
          all_paths: bool = False, accept_existing: str | None = None,
          wiki_root: Path | None = None, preview: bool = False,
          accept_plan: str | None = None) -> dict:
    """Back up explicitly accepted target files after updating the repository."""
    entry, files, state, report = _observe(target, wiki_root=wiki_root)
    if accept_existing is not None and accept_existing != report['fingerprint']:
        raise ValueError('reviewed configuration fingerprint changed')
    if not paths and not all_paths:
        raise ValueError('adoption requires explicit files or --all')
    if all_paths and paths:
        raise ValueError('--all cannot be combined with selected files')
    if accept_existing is not None and (all_paths or set(paths) - set(report['changes'])):
        raise ValueError('guarded adoption requires exact differing files from the inspection')
    previous = set(files)
    local_root = wiki_root or target
    manifest = report['scope']
    if all_paths:
        files = backup.collect(local_root, manifest)
        manifest['files'] = [path for path in manifest['files'] if path in files]
    else:
        for value in paths:
            relative = _source_path(value)
            destination = confined_target(local_root, relative)
            valid_wiki_path = (destination.is_dir() if relative == WIKI_DIRECTORY
                               else value in WIKI_FILES and not destination.is_dir())
            if wiki_root and not valid_wiki_path:
                raise ValueError(f'expected a complete OpenWiki directory or an allowed root file: {value}')
            selected = str(relative)
            for old in list(files):
                if old == selected or relative in PurePosixPath(old).parents:
                    files.pop(old)
            if destination.is_dir():
                files.update(backup.directory_files(local_root, selected))
                covered = any(directory == selected or PurePosixPath(directory) in relative.parents
                              for directory in manifest['directories'])
                if not covered:
                    manifest['directories'] = [directory for directory in manifest['directories']
                                              if relative not in PurePosixPath(directory).parents]
                    manifest['directories'].append(selected)
                manifest['files'] = [path for path in manifest['files'] if relative not in PurePosixPath(path).parents]
            else:
                content = _read(local_root, relative)
                if content is not None:
                    files[selected] = content
                covered = any(PurePosixPath(directory) in relative.parents for directory in manifest['directories'])
                if not covered:
                    manifest['files'] = [path for path in manifest['files'] if path != selected]
                    if content is not None:
                        manifest['files'].append(selected)
    prefix = WIKI_STORAGE if wiki_root else PurePosixPath()
    desired = [DesiredFile(prefix / 'files' / path, content) for path, content in files.items()]
    desired.append(DesiredFile(prefix / 'manifest.json', _json(manifest)))
    deletes = [prefix / 'files' / path for path in previous - files.keys()]
    source_root = entry.parent if wiki_root else entry
    plan = build_plan(source_root, desired, delete_paths=deletes)
    source_prefix = PurePosixPath('projects') / state['binding']['entry']
    source_changes = {str(source_prefix / change.path): _digest(change.content)
                      for change in plan.changes if change.kind is not ChangeKind.UNCHANGED}
    fingerprint = _digest(_json({'inspection': report['fingerprint'], 'source_changes': source_changes}))
    result = {'adopted': sorted(files) if all_paths else list(paths), 'source': str(entry),
              'source_changes': source_changes, 'plan_fingerprint': fingerprint}
    if accept_plan is not None and accept_plan != fingerprint:
        raise ValueError('reviewed adoption plan changed')
    if _observe(target, wiki_root=wiki_root)[3]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed during backup planning')
    if preview:
        return result

    def postcondition() -> None:
        if accept_existing is None:
            _read_snapshot(entry, wiki=wiki_root is not None)
        elif set(paths).intersection(_observe(target, wiki_root=wiki_root)[3]['changes']):
            raise ValueError('reviewed local files changed during adoption')

    apply_plan(source_root, plan, postcondition=postcondition)
    return result


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
