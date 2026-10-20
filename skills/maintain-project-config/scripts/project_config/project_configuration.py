"""Back up and restore complete project configuration files.

Repository scope is authoritative. Legacy entries retain their former portable
projection until explicitly upgraded; setup rendering keeps its own checks.
"""
from __future__ import annotations

import difflib
import hashlib
import json
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

from project_state import config_backup as backup
from project_state.models import Catalog
from project_state.paths import confined_target

from . import repository
from .catalog import load_project_config, parse_maintenance
from .markdown import live_headings
from .models import ChangeKind, DesiredFile, MaintenanceConfig
from .planner import build_plan
from .transaction import apply_plan

CONFIG = PurePosixPath('.agents/config.json')
STATE = backup.SYNC_PATH
PORTABLE = frozenset({'skills', 'agents', 'mcp', 'settings'})


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


def _personal(path: PurePosixPath, content: bytes | None) -> bytes | None:
    """Preserve the old generated-index exclusion only for version-one entries."""
    if content is None or str(path) != 'AGENTS.md':
        return content
    text = content.decode('utf-8')
    headings = live_headings(text)
    matches = [(index, heading) for index, heading in enumerate(headings)
               if heading.level == 2 and heading.title == 'Project rules']
    if len(matches) > 1:
        raise ValueError('duplicate Project rules sections')
    if matches:
        index, heading = matches[0]
        end = next((item.start for item in headings[index + 1:] if item.level <= 2), len(text))
        text = text[:heading.start] + text[end:]
    return (text.rstrip() + '\n').encode('utf-8') if text.strip() else b''


def _manifest(entry: Path) -> dict:
    return _document(entry, PurePosixPath('manifest.json'))


def is_complete_backup(target: Path) -> bool:
    selected = binding(target)
    return selected is not None and selected.mode == 'repository' and _manifest(entry_root(target)).get('version') == 2


def read_entry(entry: Path, catalog: Catalog) -> tuple[dict[str, bytes], dict]:
    manifest = _manifest(entry)
    if manifest.get('version') == 2:
        return backup.read_backup(entry)[1], {}
    if (set(manifest) != {'version', 'files'} or manifest['version'] != 1
            or not isinstance(manifest['files'], list)):
        raise ValueError('invalid project configuration manifest')
    paths = [_source_path(value) for value in manifest['files']]
    if len({str(path).casefold() for path in paths}) != len(paths):
        raise ValueError('duplicate or case-colliding configuration files')
    files = {}
    for path in paths:
        content = _read(entry, PurePosixPath('files') / path)
        if content is None:
            raise ValueError(f'source configuration file is missing: {path}')
        files[str(path)] = _personal(path, content)
    config = _document(entry, PurePosixPath('config.json'))
    if set(config) - PORTABLE:
        raise ValueError('legacy source config contains local state or unsupported fields')
    load_project_config(entry / 'config.json', catalog=catalog)
    return files, config


def _state(target: Path) -> dict:
    selected = binding_document(binding(target))
    state = backup.read_receipt(target, selected)
    if state is not None:
        return state
    paths = []
    if _read(target, backup.LEGACY_SYNC_PATH) is not None:
        old = _document(target, backup.LEGACY_SYNC_PATH)
        if (set(old) != {'version', 'binding', 'files', 'config'} or old['version'] != 1
                or old['binding'] != selected or not isinstance(old['files'], dict)
                or not isinstance(old['config'], dict)):
            raise ValueError('legacy project configuration state is invalid or belongs to another binding')
        paths = [str(_source_path(value)) for value in old['files']]
    return {'version': 1, 'binding': selected, 'source': str(entry_root(target)),
            'sourceFingerprint': None, 'appliedPaths': paths, 'automatic': False}


def _fingerprint(entry: Path, files: Mapping[str, bytes], config: dict) -> str:
    contents = dict(files)
    if _manifest(entry)['version'] == 1:
        contents['@legacy-config'] = _json(config)
    return backup.fingerprint(_manifest(entry), contents)


def _state_file(target: Path, entry: Path, files: Mapping[str, bytes], config: dict,
                *, automatic: bool = False) -> DesiredFile:
    selected = binding_document(binding(target))
    if str(CONFIG) in files:
        selected = json.loads(files[str(CONFIG)])['maintenance']
    return DesiredFile(STATE, _json({'version': 1, 'binding': selected,
        'source': str(entry), 'sourceFingerprint': _fingerprint(entry, files, config),
        'appliedPaths': sorted(files), 'automatic': automatic}))


def initialize_entry(target: Path, entry: Path, paths: Sequence[str], catalog: Catalog, *,
                     config_content: bytes | None = None) -> None:
    """Capture selected files/directories, or existing default configuration paths."""
    if any(entry.iterdir()):
        raise ValueError('configuration entry is not empty; inspect and connect the existing entry')
    selections = [path for path in paths if not (path == str(CONFIG) and config_content is not None)]
    manifest = (backup.selected_manifest(target, selections) if selections or not paths
                else {'version': 2, 'files': [], 'directories': []})
    files = backup.collect(target, manifest, required=True)
    if config_content is not None and (not paths or str(CONFIG) in paths):
        files[str(CONFIG)] = config_content
        if str(CONFIG) not in manifest['files']:
            manifest['files'].append(str(CONFIG))
            manifest['files'].sort()
    desired = [DesiredFile(PurePosixPath('files') / path, content) for path, content in files.items()]
    desired.append(DesiredFile(PurePosixPath('manifest.json'), _json(manifest)))
    apply_plan(entry, build_plan(entry, desired), postcondition=lambda: read_entry(entry, catalog))


def _observe(target: Path, catalog: Catalog) -> tuple[Path, dict, dict, dict, dict]:
    entry = entry_root(target)
    files, config = read_entry(entry, catalog)
    manifest = _manifest(entry)
    complete = manifest['version'] == 2
    state = _state(target)
    paths = set(files) | set(state['appliedPaths'])
    if complete:
        paths.update(backup.collect(target, manifest))
    current = {path: _read(target, _source_path(path)) for path in paths}
    if not complete:
        current = {path: _personal(PurePosixPath(path), content) for path, content in current.items()}
    target_config = _document(target, CONFIG, missing=True)
    if complete and str(CONFIG) in files:
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
        if state['sourceFingerprint'] is None and actual is not None:
            conflicts.append(path)
        try:
            diffs[path] = ''.join(difflib.unified_diff(
                (actual or b'').decode('utf-8').splitlines(True), (desired or b'').decode('utf-8').splitlines(True),
                fromfile='target/' + path, tofile='source/' + path))
        except UnicodeDecodeError:
            diffs[path] = 'Binary file differs'
    if not complete:
        for key in sorted(PORTABLE):
            actual = {key: target_config[key]} if key in target_config else {}
            desired = {key: config[key]} if key in config else {}
            if actual != desired:
                name = str(CONFIG) + '#' + key
                changes.append(name)
                if state['sourceFingerprint'] is None and actual:
                    conflicts.append(name)
                diffs[name] = {'target': actual, 'source': desired}
    observation = {'source': str(entry), 'changes': changes, 'conflicts': conflicts, 'diffs': diffs,
                   'source_fingerprint': _fingerprint(entry, files, config), 'complete_backup': complete,
                   'automatic': state['automatic'], 'scope': manifest}
    observation['fingerprint'] = _digest(_json({'observation': observation,
        'current': {path: _digest(content) for path, content in current.items()}, 'config': target_config, 'state': state}))
    return entry, files, config, state, observation


def inspect(target: Path, catalog: Catalog) -> dict:
    """Read backup scope and drift without fetching, parsing native files or writing."""
    selected = binding(target)
    if selected is None or selected.mode != 'repository':
        return {'mode': selected.mode if selected else 'unselected', 'selection_required': selected is None}
    return {'mode': 'repository', **_observe(target, catalog)[4]}


def require_converged(target: Path, catalog: Catalog) -> str | None:
    report = inspect(target, catalog)
    if report['mode'] != 'repository':
        return None
    if report['changes']:
        raise ValueError('project configuration differs from its source; inspect/apply or explicitly adopt before continuing')
    return report['source_fingerprint']


def apply(target: Path, catalog: Catalog, *, accept_existing: str | None = None,
          automatic: bool | None = None) -> dict:
    """Restore complete selected files; an established binding overwrites local drift."""
    entry, files, config, state, report = _observe(target, catalog)
    if accept_existing is not None and accept_existing != report['fingerprint']:
        raise ValueError('reviewed configuration fingerprint changed')
    if report['conflicts'] and accept_existing != report['fingerprint']:
        raise ValueError('initial project configuration conflict; inspect and accept the exact proposed restoration: '
                         + ', '.join(report['conflicts']))
    automatic = state['automatic'] if automatic is None else automatic
    if (not report['changes'] and state['sourceFingerprint'] == report['source_fingerprint']
            and automatic == state['automatic'] and _read(target, backup.LEGACY_SYNC_PATH) is None):
        return {'mode': 'repository', 'applied': False, 'skipped': True, 'source': str(entry),
                'managed_paths': sorted([*files, str(STATE)]), 'changed_paths': []}
    desired, deletes = [], []
    for path in sorted(set(files) | set(state['appliedPaths'])):
        relative = _source_path(path)
        content = files.get(path)
        if content is None:
            deletes.append(relative)
        else:
            if not report['complete_backup'] and path == 'AGENTS.md':
                original = _read(target, relative)
                if original is not None:
                    # Legacy entries never stored the index; keep their existing local section.
                    text = original.decode('utf-8')
                    headings = live_headings(text)
                    for index, heading in enumerate(headings):
                        if heading.level == 2 and heading.title == 'Project rules':
                            end = next((item.start for item in headings[index + 1:] if item.level <= 2), len(text))
                            content = content.rstrip() + b'\n\n' + text[heading.start:end].encode('utf-8')
            desired.append(DesiredFile(relative, content))
    if not report['complete_backup']:
        target_config = _document(target, CONFIG, missing=True)
        for key in PORTABLE:
            target_config.pop(key, None)
        target_config.update(config)
        desired.append(DesiredFile(CONFIG, _json(target_config)))
    if _read(target, backup.LEGACY_SYNC_PATH) is not None:
        deletes.append(backup.LEGACY_SYNC_PATH)
    desired.append(_state_file(target, entry, files, config, automatic=automatic))
    directories = _manifest(entry).get('directories', [])
    plan = build_plan(target, desired, delete_paths=deletes,
                      replace_roots=[PurePosixPath(value) for value in directories])
    if _observe(target, catalog)[4]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed while planning')
    def postcondition() -> None:
        after = _observe(target, catalog)[4]
        if after['changes'] or after['source_fingerprint'] != report['source_fingerprint']:
            raise ValueError('configuration changed during application')
    apply_plan(target, plan, postcondition=postcondition)
    return {'mode': 'repository', 'applied': True, 'skipped': False, 'source': str(entry),
            'managed_paths': sorted([*files, str(CONFIG), str(STATE)]),
            'changed_paths': [str(item.path) for item in plan.changes if item.kind is not ChangeKind.UNCHANGED]}


def adopt(target: Path, catalog: Catalog, paths: Sequence[str], fields: Sequence[str], *,
          all_paths: bool = False) -> dict:
    """Back up explicitly accepted target files after updating the repository."""
    entry, files, config, state, report = _observe(target, catalog)
    if not paths and not fields and not all_paths:
        raise ValueError('adoption requires explicit files or --all')
    if all_paths and (paths or fields):
        raise ValueError('--all cannot be combined with selected files or legacy fields')
    manifest = _manifest(entry)
    if all_paths:
        if manifest['version'] == 1:
            selections = sorted(set(backup.selected_manifest(target, [])['files']
                + backup.selected_manifest(target, [])['directories'] + [path for path in files if _read(target, PurePosixPath(path)) is not None]))
            # Default directories already include their children from legacy file lists.
            selections = [path for path in selections if not any(PurePosixPath(other) in PurePosixPath(path).parents
                          for other in selections)]
            manifest = backup.selected_manifest(target, selections)
        files = backup.collect(target, manifest)
        manifest['files'] = [path for path in manifest['files'] if path in files]
        config = {}
    elif manifest['version'] == 2:
        if fields:
            raise ValueError('complete backups select whole files; --field is only for legacy entries')
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
    else:
        for value in paths:
            relative = _source_path(value)
            content = _personal(relative, _read(target, relative))
            if content is None:
                files.pop(str(relative), None)
            else:
                files[str(relative)] = content
        current = _document(target, CONFIG, missing=True)
        for key in fields:
            if key not in PORTABLE:
                raise ValueError(f'not a portable configuration field: {key}')
            if key in current:
                config[key] = current[key]
            else:
                config.pop(key, None)
        manifest['files'] = sorted(files)
    desired = [DesiredFile(PurePosixPath('files') / path, content) for path, content in files.items()]
    desired.append(DesiredFile(PurePosixPath('manifest.json'), _json(manifest)))
    deletes = [PurePosixPath('files') / path for path in read_entry(entry, catalog)[0] if path not in files]
    if manifest['version'] == 1:
        desired.append(DesiredFile(PurePosixPath('config.json'), _json(config)))
    elif _read(entry, PurePosixPath('config.json')) is not None:
        deletes.append(PurePosixPath('config.json'))
    if _observe(target, catalog)[4]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed during backup planning')
    apply_plan(entry, build_plan(entry, desired, delete_paths=deletes), postcondition=lambda: read_entry(entry, catalog))
    return {'adopted': sorted(files) if all_paths else list(paths), 'fields': list(fields), 'source': str(entry)}


def save_generated(target: Path, catalog: Catalog, outputs: Mapping[str, bytes], retired: Sequence[str],
                   *, portable_config: dict | None = None,
                   target_outputs: Mapping[str, bytes] | None = None) -> DesiredFile | None:
    """Save accepted setup outputs before their guarded target transaction."""
    selected = binding(target)
    if selected is None or selected.mode != 'repository':
        return None
    entry, files, config, state, report = _observe(target, catalog)
    if report['changes']:
        raise ValueError('configuration source or target changed before generated handoff')
    manifest = _manifest(entry)
    complete = manifest['version'] == 2
    updates = dict(outputs)
    if complete:
        updates.update({path: content for path, content in (target_outputs or {}).items()
                        if path in files or path in backup.DEFAULT_FILES
                        or any(PurePosixPath(directory) in PurePosixPath(path).parents
                               for directory in (*manifest['directories'], *backup.DEFAULT_DIRECTORIES))})
    for value, content in updates.items():
        _source_path(value)
        files[value] = content
        if complete and value not in manifest['files'] and not any(
                PurePosixPath(directory) in PurePosixPath(value).parents for directory in manifest['directories']):
            manifest['files'].append(value)
    for value in retired:
        if value not in updates:
            files.pop(value, None)
    if complete:
        manifest['files'] = sorted(path for path in manifest['files'] if path in files)
    else:
        manifest['files'] = sorted(files)
        if portable_config is not None:
            config = {key: value for key, value in portable_config.items() if key in PORTABLE}
    desired = [DesiredFile(PurePosixPath('files') / path, content) for path, content in files.items()]
    desired.append(DesiredFile(PurePosixPath('manifest.json'), _json(manifest)))
    if not complete:
        desired.append(DesiredFile(PurePosixPath('config.json'), _json(config)))
    deletes = [PurePosixPath('files') / path for path in read_entry(entry, catalog)[0] if path not in files]
    if _observe(target, catalog)[4]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed before generated handoff')
    apply_plan(entry, build_plan(entry, desired, delete_paths=deletes), postcondition=lambda: read_entry(entry, catalog))
    return _state_file(target, entry, files, config, automatic=state['automatic'])
