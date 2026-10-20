"""Project-owned source projection for maintenance and full setup.

The repository stores canonical inputs; local synchronization renders native
outputs. Callers hold exclusive target/source access through writes.
"""
from __future__ import annotations

import difflib
import hashlib
import json
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

from project_state.catalog import safe_relative
from project_state.models import Catalog
from project_state.paths import confined_target

from . import repository
from .catalog import load_project_config, parse_maintenance
from .markdown import live_headings
from .models import ChangeKind, DesiredFile, MaintenanceConfig
from .ownership import load_ownership
from .planner import build_plan
from .transaction import apply_plan

CONFIG = PurePosixPath('.agents/config.json')
STATE = PurePosixPath('.agents/project-config-state.json')
PORTABLE = frozenset({'skills', 'agents', 'mcp', 'settings'})


def _json(content: object) -> bytes:
    return (json.dumps(content, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')


def _document(root: Path, relative: PurePosixPath, *, missing: bool = False) -> dict:
    path = confined_target(root, relative)
    if missing and not path.exists():
        return {}
    document = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(document, dict):
        raise ValueError(f'{relative} must contain an object')
    return document


def binding(target: Path) -> MaintenanceConfig | None:
    return parse_maintenance(_document(target, CONFIG, missing=True).get('maintenance'))


def binding_document(value: MaintenanceConfig) -> dict:
    return {key: item for key, item in asdict(value).items() if item is not None}


def entry_root(target: Path) -> Path:
    value = binding(target)
    if value is None or value.mode != 'repository':
        raise ValueError('project has no repository maintenance binding; bind the selected source first')
    checkout = repository.open_checkout(value.repository, value.branch)
    return confined_target(checkout, PurePosixPath('projects') / value.entry)


def _source_path(value: str) -> PurePosixPath:
    path = safe_relative(value, 'project configuration file')
    allowed = (path.as_posix() in {'AGENTS.md', 'CLAUDE.md'}
               or path.parts[:2] in {('.agents', 'rules'), ('.agents', 'skills'), ('.agents', 'agents')}
               or path.parts[0] == 'docs')
    if not allowed or any(part in {'.git', '.codegraph', '__pycache__'} for part in path.parts):
        raise ValueError(f'not a canonical project instruction or support path: {path}')
    return path


def _index_span(content: bytes) -> tuple[int, int] | None:
    text = content.decode('utf-8')
    headings = live_headings(text)
    matches = [(index, heading) for index, heading in enumerate(headings)
               if heading.level == 2 and heading.title == 'Project rules']
    if len(matches) > 1:
        raise ValueError('duplicate Project rules sections')
    if not matches:
        return None
    index, heading = matches[0]
    end = next((item.start for item in headings[index + 1:] if item.level <= 2), len(text))
    return len(text[:heading.start].encode('utf-8')), len(text[:end].encode('utf-8'))


def _personal(path: PurePosixPath, content: bytes | None) -> bytes | None:
    if content is None or path.as_posix() != 'AGENTS.md':
        return content
    span = _index_span(content)
    if span:
        content = content[:span[0]] + content[span[1]:]
    return content.rstrip() + b'\n' if content.strip() else b''


def _read(root: Path, path: PurePosixPath) -> bytes | None:
    destination = confined_target(root, path)
    if not destination.exists():
        return None
    if not destination.is_file():
        raise ValueError(f'configuration path is not a regular file: {path}')
    return destination.read_bytes()


def _digest(content: bytes | None) -> str | None:
    return hashlib.sha256(content).hexdigest() if content is not None else None


def read_entry(entry: Path, catalog: Catalog) -> tuple[dict[str, bytes], dict]:
    manifest = _document(entry, PurePosixPath('manifest.json'))
    if set(manifest) != {'version', 'files'} or manifest['version'] != 1 or not isinstance(manifest['files'], list):
        raise ValueError('invalid project configuration manifest')
    paths = [_source_path(value) for value in manifest['files']]
    if len({str(path).casefold() for path in paths}) != len(paths):
        raise ValueError('duplicate or case-colliding configuration files')
    files = {}
    for path in paths:
        content = _read(entry, PurePosixPath('files') / path)
        if content is None:
            raise ValueError(f'source configuration file is missing: {path}')
        if path.as_posix() == 'AGENTS.md' and _index_span(content):
            raise ValueError('source AGENTS.md must exclude the generated Project rules section')
        files[str(path)] = _personal(path, content)
    config = _document(entry, PurePosixPath('config.json'))
    if set(config) - PORTABLE:
        raise ValueError('source config contains local state or unsupported fields')
    parsed = load_project_config(confined_target(entry, PurePosixPath('config.json')), catalog=catalog)
    for agent in parsed.agents:
        for path in agent.source_paths:
            if str(path) not in files:
                raise ValueError(f'Agent canonical source is missing from the entry: {path}')
    return files, config


def _state(target: Path) -> dict:
    if _read(target, STATE) is None:
        return {'version': 1, 'binding': binding_document(binding(target)), 'files': {}, 'config': {}}
    state = _document(target, STATE)
    if (set(state) != {'version', 'binding', 'files', 'config'} or state['version'] != 1
            or state['binding'] != binding_document(binding(target))
            or not isinstance(state['files'], dict) or not isinstance(state['config'], dict)
            or set(state['config']) - PORTABLE):
        raise ValueError('project configuration state is invalid or belongs to another binding')
    for path, digest in state['files'].items():
        _source_path(path)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('invalid recorded configuration digest')
    return state


def _state_file(target: Path, files: Mapping[str, bytes], config: dict) -> DesiredFile:
    return DesiredFile(STATE, _json({'version': 1, 'binding': binding_document(binding(target)),
                                   'files': {path: _digest(content) for path, content in files.items()},
                                   'config': config}))


def _assert_source_ownership(target: Path, paths: Sequence[str]) -> None:
    state = load_ownership(target)
    if state is None:
        return
    for value in paths:
        path = _source_path(value)
        for asset in state.assets:
            if asset.path == path or (asset.kind == 'tree' and asset.path in path.parents):
                raise ValueError(f'configuration file is owned by setup delivery: {path}')


def initialize_entry(target: Path, entry: Path, paths: Sequence[str], catalog: Catalog) -> None:
    """Import only explicitly selected project files into a new source entry."""
    if (entry / 'manifest.json').exists() or any(entry.iterdir()):
        raise ValueError('configuration entry is not empty; inspect and connect the existing entry')
    _assert_source_ownership(target, paths)
    config = _document(target, CONFIG, missing=True)
    load_project_config(target / CONFIG, catalog=catalog)
    files = []
    for value in paths:
        path = _source_path(value)
        content = _personal(path, _read(target, path))
        if content is None:
            raise ValueError(f'selected import file does not exist: {path}')
        files.append(DesiredFile(PurePosixPath('files') / path, content))
    files.extend((DesiredFile(PurePosixPath('manifest.json'), _json({'version': 1, 'files': list(paths)})),
                  DesiredFile(PurePosixPath('config.json'), _json({k: v for k, v in config.items() if k in PORTABLE}))))
    apply_plan(entry, build_plan(entry, files), postcondition=lambda: read_entry(entry, catalog))


def _observe(target: Path, catalog: Catalog) -> tuple[Path, dict, dict, dict, dict]:
    entry = entry_root(target)
    files, config = read_entry(entry, catalog)
    state = _state(target)
    _assert_source_ownership(target, sorted(set(files) | set(state['files'])))
    current = {path: _personal(PurePosixPath(path), _read(target, PurePosixPath(path)))
               for path in set(files) | set(state['files'])}
    target_config = _document(target, CONFIG, missing=True)
    load_project_config(target / CONFIG, catalog=catalog)
    conflicts, changes, diffs = [], [], {}
    for path, actual in sorted(current.items()):
        desired = files.get(path)
        if actual == desired:
            continue
        changes.append(path)
        if _digest(actual) != state['files'].get(path):
            conflicts.append(path)
        try:
            diffs[path] = ''.join(difflib.unified_diff(
                (actual or b'').decode('utf-8').splitlines(True), (desired or b'').decode('utf-8').splitlines(True),
                fromfile='target/' + path, tofile='source/' + path))
        except UnicodeDecodeError:
            diffs[path] = 'Binary file differs'
    for key in sorted(set(config) | set(state['config'])):
        actual = {key: target_config[key]} if key in target_config else {}
        desired = {key: config[key]} if key in config else {}
        previous = {key: state['config'][key]} if key in state['config'] else {}
        if actual != desired:
            name = '.agents/config.json#' + key
            changes.append(name)
            if actual != previous:
                conflicts.append(name)
            diffs[name] = {'target': actual, 'source': desired}
    observation = {'source': str(entry), 'changes': changes, 'conflicts': conflicts, 'diffs': diffs,
                   'source_fingerprint': _digest(_json({'files': {p: _digest(c) for p, c in files.items()}, 'config': config}))}
    observation['fingerprint'] = _digest(_json({'observation': observation,
                                              'current': {p: _digest(c) for p, c in current.items()},
                                              'config': target_config, 'state': state}))
    return entry, files, config, state, observation


def inspect(target: Path, catalog: Catalog) -> dict:
    """Read source/target drift without Git access, fetching, or target writes."""
    selected = binding(target)
    if selected is None or selected.mode == 'local':
        return {'mode': selected.mode if selected else 'unselected', 'selection_required': selected is None}
    return {'mode': 'repository', **_observe(target, catalog)[4]}


def require_converged(target: Path, catalog: Catalog) -> str | None:
    report = inspect(target, catalog)
    if report['mode'] != 'repository':
        return None
    if report['changes']:
        raise ValueError('project configuration differs from its source; inspect/apply or explicitly adopt before continuing')
    return report['source_fingerprint']


def apply(target: Path, catalog: Catalog, *, accept_existing: str | None = None) -> dict:
    """Apply canonical inputs; render native outputs through local synchronization.

    accept_existing is a reviewed inspection fingerprint for first adoption only.
    It never authorizes overwriting a later edit of an already recorded input.
    """
    entry, files, config, state, report = _observe(target, catalog)
    if accept_existing is not None and accept_existing != report['fingerprint']:
        raise ValueError('reviewed configuration fingerprint changed')
    if report['conflicts']:
        first = _read(target, STATE) is None
        if not first or accept_existing != report['fingerprint']:
            raise ValueError('project configuration conflict: ' + ', '.join(report['conflicts']))
    desired, deletes = [], []
    for path in sorted(set(files) | set(state['files'])):
        relative = PurePosixPath(path)
        content = files.get(path)
        current = _read(target, relative)
        if path == 'AGENTS.md' and current is not None:
            span = _index_span(current)
            if span:
                content = (content or b'').rstrip() + b'\n\n' + current[span[0]:span[1]]
        if content is None:
            deletes.append(relative)
        else:
            desired.append(DesiredFile(relative, content))
    target_config = _document(target, CONFIG, missing=True)
    for key in set(state['config']) - set(config):
        target_config.pop(key, None)
    target_config.update(config)
    desired.extend((DesiredFile(CONFIG, _json(target_config)), _state_file(target, files, config)))
    plan = build_plan(target, desired, delete_paths=deletes)
    if _observe(target, catalog)[4]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed while planning')
    def postcondition() -> None:
        after = _observe(target, catalog)[4]
        if after['changes'] or after['source_fingerprint'] != report['source_fingerprint']:
            raise ValueError('configuration changed during application')
    apply_plan(target, plan, postcondition=postcondition)
    return {'mode': 'repository', 'applied': True, 'source': str(entry),
            'managed_paths': sorted([*files, str(CONFIG), str(STATE)]),
            'changed_paths': [str(item.path) for item in plan.changes if item.kind is not ChangeKind.UNCHANGED]}


def adopt(target: Path, catalog: Catalog, paths: Sequence[str], fields: Sequence[str]) -> dict:
    """Copy selected target edits to source only while its recorded version remains current."""
    entry, files, config, state, report = _observe(target, catalog)
    if not paths and not fields:
        raise ValueError('adoption requires explicit files or config fields')
    _assert_source_ownership(target, paths)
    desired, deletes = [], []
    for value in paths:
        path = _source_path(value)
        if _digest(files.get(value)) != state['files'].get(value):
            raise ValueError(f'source changed since last application: {value}')
        content = _personal(path, _read(target, path))
        source_path = PurePosixPath('files') / path
        if content is None:
            files.pop(value, None)
            deletes.append(source_path)
        else:
            files[value] = content
            desired.append(DesiredFile(source_path, content))
    current = _document(target, CONFIG, missing=True)
    for key in fields:
        if key not in PORTABLE:
            raise ValueError(f'not a portable configuration field: {key}')
        if (key in config) != (key in state['config']) or config.get(key) != state['config'].get(key):
            raise ValueError(f'source changed since last application: {key}')
        if key in current:
            config[key] = current[key]
        else:
            config.pop(key, None)
    desired.extend((DesiredFile(PurePosixPath('manifest.json'), _json({'version': 1, 'files': sorted(files)})),
                    DesiredFile(PurePosixPath('config.json'), _json(config))))
    plan = build_plan(entry, desired, delete_paths=deletes)
    if _observe(target, catalog)[4]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed during adoption planning')
    apply_plan(entry, plan, postcondition=lambda: read_entry(entry, catalog))
    return {'adopted': list(paths), 'fields': list(fields), 'source': str(entry)}


def save_generated(target: Path, catalog: Catalog, outputs: Mapping[str, bytes], retired: Sequence[str],
                   *, portable_config: dict | None = None) -> DesiredFile | None:
    """Save accepted setup outputs before target mutation; return its next local receipt.

    A later target failure deliberately retains the canonical source edits. The
    existing target transaction owns target rollback, never source rollback.
    """
    if binding(target) is None or binding(target).mode != 'repository':
        return None
    entry, files, config, state, report = _observe(target, catalog)
    if report['changes']:
        raise ValueError('configuration source or target changed before generated handoff')
    desired, deletes = [], []
    for value, content in outputs.items():
        path = _source_path(value)
        files[value] = content
        desired.append(DesiredFile(PurePosixPath('files') / path, content))
    for value in retired:
        if value in files and value not in outputs:
            files.pop(value)
            deletes.append(PurePosixPath('files') / _source_path(value))
    if portable_config is not None:
        config = {key: value for key, value in portable_config.items() if key in PORTABLE}
        desired.append(DesiredFile(PurePosixPath('config.json'), _json(config)))
    desired.append(DesiredFile(PurePosixPath('manifest.json'), _json({'version': 1, 'files': sorted(files)})))
    plan = build_plan(entry, desired, delete_paths=deletes)
    if _observe(target, catalog)[4]['fingerprint'] != report['fingerprint']:
        raise ValueError('configuration changed before generated handoff')
    apply_plan(entry, plan, postcondition=lambda: read_entry(entry, catalog))
    return _state_file(target, files, config)
