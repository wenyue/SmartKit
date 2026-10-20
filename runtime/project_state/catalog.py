"""Validate the installed catalog used by project readiness checks."""
from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from .models import AssetSpec, Catalog, ContractError, Harness
from .skill_registry import SkillRegistryError, load_skill_registry


_SEMVER = re.compile(
    r'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)'
    r'(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)'
    r'(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?'
    r'(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$'
)


_NAME = re.compile(r'^[a-z0-9][a-z0-9-]*$')


_FIELD_NAME = re.compile(r'^[A-Za-z][A-Za-z0-9_@-]*$')


_WINDOWS_RESERVED_CHARACTERS = frozenset('<>:"\\|?*')


_WINDOWS_RESERVED_NAMES = frozenset(
    {'CON', 'PRN', 'AUX', 'NUL', 'COM¹', 'COM²', 'COM³', 'LPT¹', 'LPT²', 'LPT³'}
    | {f'COM{number}' for number in range(1, 10)}
    | {f'LPT{number}' for number in range(1, 10)}
)


_ASSET_FIELDS = frozenset({
    'id', 'kind', 'source', 'skill', 'target', 'harnesses',
    'control_plane', 'metadata',
})


_CATALOG_FIELDS = frozenset({'plugin', 'assets'})


_PLUGIN_FIELDS = frozenset({'id', 'version', 'repository', 'ref'})


def safe_relative(value: str, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or '\\' in value:
        raise ContractError(f'{label} must be a relative path')
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or re.match(r'^[A-Za-z]:', value)
        or value == '.'
        or any(part in {'.', '..'} for part in value.split('/'))
    ):
        raise ContractError(f'{label} must be a relative path')
    for part in value.split('/'):
        if (
            any(unicodedata.category(character) == 'Cc' for character in part)
            or any(character in _WINDOWS_RESERVED_CHARACTERS for character in part)
            or part.endswith((' ', '.'))
            or part.split('.', 1)[0].upper() in _WINDOWS_RESERVED_NAMES
        ):
            raise ContractError(f'{label} must be a portable relative path')
    return path


def _name(value: object, label: str) -> str:
    if not isinstance(value, str) or not _NAME.fullmatch(value):
        raise ContractError(f'{label} must be a safe name')
    return value


def safe_field_key(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ContractError(f'{label} must be a dotted safe name')
    if value == '$schema':
        return value
    for segment in value.split('.'):
        if not _FIELD_NAME.fullmatch(segment):
            raise ContractError(f'{label} must be a dotted safe name')
    return value


def _object(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ContractError(f'{label} must be an object')
    return value


def _fields(value: Mapping[str, object], allowed: frozenset[str], label: str) -> None:
    unknown = set(value) - allowed
    if unknown:
        names = ', '.join(sorted(str(item) for item in unknown))
        raise ContractError(f'unknown {label} fields: {names}')


def _required(value: Mapping[str, object], key: str, label: str) -> object:
    if key not in value:
        raise ContractError(f'{label} requires {key}')
    return value[key]


def _nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f'{label} must be a non-empty string')
    return value


def _rule_metadata(value: object, *, project_blueprint: bool) -> Mapping[str, object]:
    metadata = _object(value, 'asset metadata')
    _fields(metadata, frozenset({'section', 'loading', 'description', 'cursor', 'github'}), 'rule metadata')
    for field in ('section', 'loading', 'cursor', 'github'):
        _required(metadata, field, 'rule metadata')
    section = _nonempty_string(metadata['section'], 'rule metadata section')
    if section not in {'global', 'base', 'project'} or (project_blueprint and section != 'project'):
        raise ContractError('rule metadata section is unsupported')
    if metadata['loading'] != 'always':
        raise ContractError('rule metadata loading must be always')
    if 'description' in metadata:
        _nonempty_string(_required(metadata, 'description', 'rule metadata'), 'rule metadata description')
    cursor = _object(metadata['cursor'], 'rule metadata cursor')
    allowed_cursor = {'alwaysApply'} if project_blueprint else {'description', 'alwaysApply'}
    _fields(cursor, frozenset(allowed_cursor), 'rule metadata cursor')
    _required(cursor, 'alwaysApply', 'rule metadata cursor')
    if cursor['alwaysApply'] is not True:
        raise ContractError('rule metadata cursor alwaysApply must be true')
    if not project_blueprint:
        _nonempty_string(_required(cursor, 'description', 'rule metadata cursor'), 'rule metadata cursor description')
    github = _object(metadata['github'], 'rule metadata github')
    _fields(github, frozenset({'applyTo'}), 'rule metadata github')
    if _required(github, 'applyTo', 'rule metadata github') != '**':
        raise ContractError('rule metadata github applyTo must be **')
    for label, text in (('description', metadata.get('description')), ('cursor description', cursor.get('description'))):
        if isinstance(text, str) and not text.strip():
            raise ContractError(f'rule metadata {label} must be a non-empty string')
    return dict(metadata)


def _metadata(value: object, kind: str, target: PurePosixPath | None) -> Mapping[str, object]:
    if kind == 'rule':
        return _rule_metadata(value, project_blueprint=False)
    is_project_rule_blueprint = (
        kind == 'blueprint'
        and target is not None
        and target.parts[:2] == ('.agents', 'rules')
    )
    if is_project_rule_blueprint:
        return _rule_metadata(value, project_blueprint=True)
    if value is not None:
        metadata = _object(value, 'asset metadata')
        if metadata:
            raise ContractError(f'asset kind {kind} cannot declare metadata')
    return {}


def _harnesses(value: object, label: str, default: tuple[Harness, ...]) -> tuple[Harness, ...]:
    if value is None:
        return default
    if not isinstance(value, list):
        raise ContractError(f'{label} must be an array')
    result: list[Harness] = []
    for item in value:
        try:
            harness = Harness(item)
        except (TypeError, ValueError) as error:
            raise ContractError(f'{label} has an unsupported harness') from error
        if harness in result:
            raise ContractError(f'{label} has duplicate harnesses')
        result.append(harness)
    return tuple(result)


def parse_asset(
    value: Mapping[str, object],
    *,
    custom_skill_sources: Mapping[str, PurePosixPath] | None = None,
) -> AssetSpec:
    asset = _object(value, 'asset')
    _fields(asset, _ASSET_FIELDS, 'asset')
    asset_id = _name(_required(asset, 'id', 'asset'), 'asset id')
    kind = _name(_required(asset, 'kind', 'asset'), 'asset kind')
    source_value = asset.get('source')
    skill_id = asset.get('skill')
    if skill_id is not None:
        if not isinstance(skill_id, str) or not skill_id:
            raise ContractError('asset skill must be a Plugin Skill id')
        if source_value is not None:
            raise ContractError('asset cannot declare both source and skill')
        resolved = (custom_skill_sources or {}).get(skill_id)
        if resolved is None:
            raise ContractError(f'asset references unknown custom Skill: {skill_id}')
        source = resolved
    else:
        if not isinstance(source_value, str):
            raise ContractError('asset source must be a relative path')
        source = safe_relative(source_value, 'asset source')
    target_value = asset.get('target')
    if target_value is not None and not isinstance(target_value, str):
        raise ContractError('asset target must be a relative path')
    target = safe_relative(target_value, 'asset target') if target_value is not None else None
    harnesses = _harnesses(asset.get('harnesses'), 'asset harnesses', tuple(Harness))
    control_plane = asset.get('control_plane', False)
    if type(control_plane) is not bool:
        raise ContractError('asset control_plane must be a boolean')
    if control_plane and target is not None:
        raise ContractError('a control-plane asset cannot have a project target')
    if control_plane and (kind != 'skill' or skill_id is None):
        raise ContractError('a control-plane asset must reference one custom Skill')
    if not control_plane and skill_id is not None:
        raise ContractError('only a control-plane asset may reference a custom Skill')
    if kind == 'agent':
        if (
            target is None
            or source != PurePosixPath('agents/codex')
            or target != PurePosixPath('.codex/agents')
            or harnesses != (Harness.CODEX,)
        ):
            raise ContractError(
                'a plugin Agent asset must copy agents/codex to .codex/agents '
                'for the codex harness'
            )
    return AssetSpec(
        asset_id, kind, source, target, harnesses, control_plane,
        _metadata(asset.get('metadata'), kind, target), skill_id,
    )


def _load_json(path: Path, label: str) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except OSError as error:
        raise ContractError(f'cannot read {label}: {path}') from error
    except json.JSONDecodeError as error:
        raise ContractError(f'{label} is not valid JSON') from error
    return _object(value, label)


def load_catalog(source_root: Path) -> Catalog:
    root = source_root.resolve()
    try:
        version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    except OSError as error:
        raise ContractError(f'cannot read VERSION: {root / "VERSION"}') from error
    if not _SEMVER.fullmatch(version):
        raise ContractError('VERSION must be semantic version')
    document = _load_json(root / 'setup-assets' / 'catalog' / 'assets.json', 'catalog')
    _fields(document, _CATALOG_FIELDS, 'catalog')
    plugin = _object(_required(document, 'plugin', 'catalog'), 'catalog plugin')
    _fields(plugin, _PLUGIN_FIELDS, 'catalog plugin')
    plugin_id = _name(_required(plugin, 'id', 'catalog plugin'), 'catalog plugin id')
    plugin_version = _required(plugin, 'version', 'catalog plugin')
    if not isinstance(plugin_version, str) or not _SEMVER.fullmatch(plugin_version):
        raise ContractError('catalog plugin version must be semantic version')
    if plugin_version != version:
        raise ContractError('catalog plugin version must match VERSION')
    repository = _required(plugin, 'repository', 'catalog plugin')
    ref = _required(plugin, 'ref', 'catalog plugin')
    if not isinstance(repository, str) or not repository:
        raise ContractError('catalog plugin repository must be a string')
    if not isinstance(ref, str) or not ref:
        raise ContractError('catalog plugin ref must be a string')
    try:
        skill_registry = load_skill_registry(root)
    except SkillRegistryError as error:
        raise ContractError(str(error)) from error
    custom_skill_sources = {
        item.id: PurePosixPath('skills') / item.path
        for item in skill_registry.custom
    }
    asset_values = _required(document, 'assets', 'catalog')
    if not isinstance(asset_values, list):
        raise ContractError('catalog assets must be an array')
    assets = tuple(
        parse_asset(
            _object(item, 'catalog asset'),
            custom_skill_sources=custom_skill_sources,
        )
        for item in asset_values
    )
    if len({asset.id for asset in assets}) != len(assets):
        raise ContractError('catalog has duplicate asset ids')
    targets = [asset.target for asset in assets if asset.target is not None]
    if len(set(targets)) != len(targets):
        raise ContractError('catalog has duplicate asset targets')
    for asset in assets:
        if asset.control_plane:
            continue
        if asset.source.parts[:1] == ('setup-assets',):
            continue
        if asset.kind == 'agent':
            continue
        raise ContractError(
            f'catalog asset source is outside an allowed ownership root: {asset.source}'
        )
    return Catalog(
        plugin_id,
        plugin_version,
        repository,
        ref,
        assets,
    )
