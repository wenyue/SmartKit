from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from .catalog import safe_field_key, safe_relative
from .external_contract import (
    ExternalContractError,
    LICENSE_MARKERS,
    is_link_like as _is_link_like,
    validate_ref,
    validate_source_identity,
)
from .models import Catalog, ContractError, DesiredField, DesiredFile
from .project import ProjectError, confined_target
from .structured import (
    StructuredConfigError,
    canonical_value_bytes,
    field_value,
    format_for_path,
    parse_document,
)


OWNERSHIP_PATH = PurePosixPath('.agents/smartkit.lock.json')
_ASSET_FIELDS = frozenset({'kind', 'role', 'path', 'key', 'digest', 'source', 'source_path'})
_ASSET_KINDS = frozenset({'file', 'tree', 'field'})
_SOURCE_FIELDS = frozenset({
    'id', 'url', 'requested_ref', 'resolved_ref', 'ref_kind', 'commit', 'license', 'skills',
})
_LICENSE_FIELDS = frozenset({'spdx', 'path', 'sha256'})
_SOURCE_SKILL_FIELDS = frozenset({'id', 'path'})


class OwnershipError(ValueError):
    """Raised when SmartKit cannot safely reconcile managed project assets."""


@dataclass(frozen=True)
class OwnedAsset:
    kind: str
    role: str
    path: PurePosixPath
    digest: str
    key: str | None = None
    source: str | None = None
    source_path: PurePosixPath | None = None

    @property
    def identity(self) -> tuple[str, PurePosixPath, str | None]:
        return self.kind, self.path, self.key


@dataclass(frozen=True)
class GeneratedContract:
    id: str
    source: PurePosixPath
    target: PurePosixPath
    fingerprint: str
    outputs: tuple[PurePosixPath, ...]


@dataclass(frozen=True)
class OwnershipState:
    sources: tuple[Mapping[str, object], ...]
    assets: tuple[OwnedAsset, ...]
    contracts: tuple[GeneratedContract, ...] = ()
    project_sync: bool = False


@dataclass(frozen=True)
class OwnershipResult:
    files: tuple[DesiredFile, ...]
    manifest: bytes
    delete_paths: tuple[PurePosixPath, ...]
    remove_fields: tuple[tuple[PurePosixPath, str], ...]


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _is_digest(value: object, length: int = 64) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in '0123456789abcdef' for character in value)
    )


def _value_digest(value: object) -> str:
    return _digest(canonical_value_bytes(value))


def _tree_digest_from_files(
    root: PurePosixPath,
    files: Mapping[PurePosixPath, bytes],
) -> str:
    entries = (
        (path.relative_to(root).as_posix(), content)
        for path, content in files.items()
        if root in path.parents
    )
    return _tree_digest_entries(entries)


def _tree_digest_entries(entries) -> str:
    digest = hashlib.sha256()
    for relative, content in sorted(entries, key=lambda item: item[0]):
        digest.update(relative.encode('utf-8'))
        digest.update(b'\0')
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest()


def _target(target_root: Path, path: PurePosixPath) -> Path:
    try:
        return confined_target(target_root, path)
    except ProjectError as error:
        raise OwnershipError(str(error)) from error


def _actual_file_digest(target_root: Path, path: PurePosixPath) -> str | None:
    target = _target(target_root, path)
    if not target.exists():
        return None
    if _is_link_like(target) or not target.is_file():
        raise OwnershipError(f'managed file is unsafe: {path.as_posix()}')
    try:
        return _digest(target.read_bytes())
    except OSError as error:
        raise OwnershipError(f'cannot read managed file: {path.as_posix()}') from error


def _actual_tree_digest(target_root: Path, root: PurePosixPath) -> str | None:
    target = _target(target_root, root)
    if not target.exists():
        return None
    if _is_link_like(target) or not target.is_dir():
        raise OwnershipError(f'managed tree is unsafe: {root.as_posix()}')
    entries: list[tuple[str, bytes]] = []
    for child in target.rglob('*'):
        relative = child.relative_to(target).as_posix()
        if _is_link_like(child):
            raise OwnershipError(f'managed tree contains a symlink: {root / relative}')
        if child.is_file():
            try:
                entries.append((relative, child.read_bytes()))
            except OSError as error:
                raise OwnershipError(f'cannot read managed tree: {root.as_posix()}') from error
        elif not child.is_dir():
            raise OwnershipError(f'managed tree contains an unsafe entry: {root / relative}')
    return _tree_digest_entries(entries)


def _actual_field_digest(
    target_root: Path,
    path: PurePosixPath,
    key: str,
) -> str | None:
    target = _target(target_root, path)
    if not target.exists():
        return None
    format_name = format_for_path(path)
    if format_name is None or target.is_symlink() or not target.is_file():
        raise OwnershipError(f'managed field path is unsafe: {path.as_posix()}')
    try:
        document = parse_document(target.read_bytes(), format_name)
    except (OSError, StructuredConfigError) as error:
        raise OwnershipError(f'cannot parse managed field path: {path.as_posix()}') from error
    exists, value = field_value(document, key)
    return _value_digest(value) if exists else None


def _actual_digest(target_root: Path, asset: OwnedAsset) -> str | None:
    if asset.kind == 'file':
        return _actual_file_digest(target_root, asset.path)
    if asset.kind == 'tree':
        return _actual_tree_digest(target_root, asset.path)
    assert asset.key is not None
    return _actual_field_digest(target_root, asset.path, asset.key)


def _parse_asset(raw: object, index: int) -> OwnedAsset:
    if not isinstance(raw, Mapping) or set(raw) - _ASSET_FIELDS:
        raise OwnershipError(f'SmartKit ownership manifest asset {index} is invalid')
    kind = raw.get('kind')
    role = raw.get('role')
    digest = raw.get('digest')
    if kind not in _ASSET_KINDS or not isinstance(role, str) or not role:
        raise OwnershipError(f'SmartKit ownership manifest asset {index} is invalid')
    if not _is_digest(digest):
        raise OwnershipError(f'SmartKit ownership manifest asset {index} is invalid')
    try:
        path = safe_relative(raw.get('path'), 'ownership asset path')
    except ContractError as error:
        raise OwnershipError(str(error)) from error
    key = raw.get('key')
    if kind == 'field':
        try:
            key = safe_field_key(key, 'ownership asset key')
        except ContractError as error:
            raise OwnershipError(str(error)) from error
    elif key is not None:
        raise OwnershipError(f'SmartKit ownership manifest asset {index} is invalid')
    source = raw.get('source')
    source_path = raw.get('source_path')
    if source is not None and not isinstance(source, str):
        raise OwnershipError(f'SmartKit ownership manifest asset {index} is invalid')
    if source_path is not None:
        try:
            source_path = safe_relative(source_path, 'ownership asset source_path')
        except ContractError as error:
            raise OwnershipError(str(error)) from error
    if (source is None) != (source_path is None) or (
        source is not None and (kind != 'tree' or role != 'skill')
    ):
        raise OwnershipError(f'SmartKit ownership manifest asset {index} provenance is invalid')
    return OwnedAsset(kind, role, path, digest, key, source, source_path)


def _parse_source(
    raw: object,
    index: int,
    *,
    label: str,
) -> Mapping[str, object]:
    if not isinstance(raw, Mapping) or set(raw) != _SOURCE_FIELDS:
        raise OwnershipError(f'{label} source {index} is invalid')
    required_strings = ('id', 'url', 'resolved_ref', 'commit')
    if any(not isinstance(raw.get(key), str) or not raw[key] for key in required_strings):
        raise OwnershipError(f'{label} source {index} is invalid')
    try:
        validate_source_identity(raw['id'], raw['url'])
    except ExternalContractError as error:
        raise OwnershipError(f'{label} source {index} identity is invalid') from error
    if len(raw['commit']) != 40 or any(
        character not in '0123456789abcdef' for character in raw['commit']
    ):
        raise OwnershipError(f'{label} source {index} is invalid')
    if raw.get('requested_ref') is not None and (
        not isinstance(raw['requested_ref'], str) or not raw['requested_ref']
    ):
        raise OwnershipError(f'{label} source {index} is invalid')
    try:
        validate_ref(raw.get('requested_ref'))
    except ExternalContractError as error:
        raise OwnershipError(f'{label} source {index} ref is invalid') from error
    if raw.get('ref_kind') not in {'branch', 'tag', 'commit'}:
        raise OwnershipError(f'{label} source {index} is invalid')
    license_item = raw.get('license')
    if not isinstance(license_item, Mapping) or set(license_item) != _LICENSE_FIELDS:
        raise OwnershipError(f'{label} source {index} license is invalid')
    if (
        not isinstance(license_item.get('spdx'), str)
        or license_item['spdx'] not in LICENSE_MARKERS
        or not isinstance(license_item.get('path'), str)
        or not license_item['path']
        or not _is_digest(license_item.get('sha256'))
    ):
        raise OwnershipError(f'{label} source {index} license is invalid')
    try:
        license_path = safe_relative(license_item['path'], f'{label} source license path')
    except ContractError as error:
        raise OwnershipError(f'{label} source {index} license is invalid') from error
    skills = raw.get('skills')
    if not isinstance(skills, list) or not skills:
        raise OwnershipError(f'{label} source {index} Skills are invalid')
    normalized_skills: list[Mapping[str, object]] = []
    for skill_index, item in enumerate(skills):
        if not isinstance(item, Mapping) or set(item) != _SOURCE_SKILL_FIELDS:
            raise OwnershipError(
                f'{label} source {index} Skill {skill_index} is invalid'
            )
        if not isinstance(item.get('id'), str) or not item['id']:
            raise OwnershipError(
                f'{label} source {index} Skill {skill_index} is invalid'
            )
        try:
            skill_path = safe_relative(item.get('path'), 'ownership source Skill path')
        except ContractError as error:
            raise OwnershipError(str(error)) from error
        owner = str(raw['id']).split('/', 1)[0]
        if item['id'] != f'{owner}/{skill_path.name}':
            raise OwnershipError(
                f'{label} source {index} Skill {skill_index} identity is invalid'
            )
        normalized_skills.append({'id': item['id'], 'path': skill_path.as_posix()})
    skill_ids = [item['id'] for item in normalized_skills]
    if len(skill_ids) != len(set(skill_ids)):
        raise OwnershipError(f'{label} source {index} has duplicate Skills')
    return {
        'id': raw['id'],
        'url': raw['url'],
        'requested_ref': raw['requested_ref'],
        'resolved_ref': raw['resolved_ref'],
        'ref_kind': raw['ref_kind'],
        'commit': raw['commit'].lower(),
        'license': {
            'spdx': license_item['spdx'],
            'path': license_path.as_posix(),
            'sha256': license_item['sha256'],
        },
        'skills': normalized_skills,
    }


def normalize_external_sources(
    value: object,
    *,
    label: str = 'SmartKit ownership manifest',
) -> tuple[Mapping[str, object], ...]:
    """Validate and normalize compact external-source provenance at every trust boundary."""
    if not isinstance(value, (list, tuple)):
        raise OwnershipError(f'{label} sources are invalid')
    sources = tuple(
        _parse_source(item, index, label=label)
        for index, item in enumerate(value)
    )
    source_ids = [str(item['id']).casefold() for item in sources]
    skill_ids = [
        str(skill['id'])
        for source in sources
        for skill in source['skills']
    ]
    if len(source_ids) != len(set(source_ids)):
        raise OwnershipError(f'{label} has duplicate sources')
    if len(skill_ids) != len(set(skill_ids)):
        raise OwnershipError(f'{label} has duplicate Skills')
    return sources


def _parse_contract(raw: object) -> GeneratedContract:
    if not isinstance(raw, Mapping) or set(raw) != {
        'id', 'source', 'target', 'fingerprint', 'outputs',
    }:
        raise OwnershipError('SmartKit contract record is invalid')
    if not isinstance(raw['id'], str) or not raw['id'] or not _is_digest(raw['fingerprint']):
        raise OwnershipError('SmartKit contract identity or fingerprint is invalid')
    try:
        source = safe_relative(raw['source'], 'contract source')
        target = safe_relative(raw['target'], 'contract target')
        if not isinstance(raw['outputs'], list) or not raw['outputs']:
            raise OwnershipError('SmartKit contract outputs are invalid')
        outputs = tuple(safe_relative(item, 'contract output') for item in raw['outputs'])
    except ContractError as error:
        raise OwnershipError(str(error)) from error
    is_rule = target.parts[:2] == ('.agents', 'rules') and len(target.parts) == 3
    is_skill = (
        target.parts[:2] == ('.agents', 'skills')
        and len(target.parts) == 4 and target.name == 'SKILL.md'
    )
    if (
        not (is_rule or is_skill)
        or target not in outputs or len(outputs) != len(set(outputs))
        or (is_rule and outputs != (target,))
        or (is_skill and any(target.parent not in output.parents for output in outputs))
    ):
        raise OwnershipError('SmartKit contract outputs are outside their declared source')
    return GeneratedContract(raw['id'], source, target, raw['fingerprint'], outputs)


def _parse_ownership_document(document: object) -> OwnershipState:
    if (
        not isinstance(document, Mapping)
        or not {'sources', 'assets'} <= set(document)
        or set(document) - {'sources', 'assets', 'contracts', 'project_sync'}
    ):
        raise OwnershipError('SmartKit ownership manifest is invalid')
    if not isinstance(document.get('sources'), list):
        raise OwnershipError('SmartKit ownership manifest is invalid')
    if not isinstance(document.get('assets'), list):
        raise OwnershipError('SmartKit ownership manifest is invalid')
    sources = normalize_external_sources(document['sources'])
    assets = tuple(_parse_asset(item, index) for index, item in enumerate(document['assets']))
    identities = [item.identity for item in assets]
    if len(identities) != len(set(identities)):
        raise OwnershipError('SmartKit ownership manifest has duplicate assets')
    declared_provenance = {
        (source['id'], skill['path'], str(skill['id']).rsplit('/', 1)[-1])
        for source in sources
        for skill in source['skills']
    }
    actual_provenance = {
        (asset.source, asset.source_path.as_posix(), asset.path.name)
        for asset in assets
        if asset.source is not None and asset.source_path is not None
    }
    if declared_provenance != actual_provenance:
        raise OwnershipError('SmartKit ownership manifest Skill provenance is invalid')
    raw_contracts = document.get('contracts', [])
    if not isinstance(raw_contracts, list):
        raise OwnershipError('SmartKit contract records must be an array')
    contracts = tuple(_parse_contract(item) for item in raw_contracts)
    ids = [item.id for item in contracts]
    outputs = [path for item in contracts for path in item.outputs]
    if len(ids) != len(set(ids)) or len(outputs) != len(set(outputs)):
        raise OwnershipError('SmartKit contract records overlap')
    if any(
        asset.path == output or (asset.kind == 'tree' and asset.path in output.parents)
        for asset in assets for output in outputs
    ):
        raise OwnershipError('SmartKit contract outputs overlap managed assets')
    if 'project_sync' in document and (type(document['project_sync']) is not int or document['project_sync'] != 1):
        raise OwnershipError('SmartKit project synchronization ownership version is invalid')
    return OwnershipState(sources, assets, contracts, 'project_sync' in document)


def load_ownership_file(path: Path) -> OwnershipState | None:
    if not path.exists():
        return None
    if _is_link_like(path) or not path.is_file():
        raise OwnershipError('SmartKit ownership manifest is unsafe')
    try:
        document = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OwnershipError('SmartKit ownership manifest is invalid') from error
    return _parse_ownership_document(document)


def load_ownership(
    target_root: Path, *, catalog: Catalog | None = None,
) -> OwnershipState | None:
    state = load_ownership_file(_target(target_root, OWNERSHIP_PATH))
    if state is None or catalog is None:
        return state
    managed_sources = tuple(
        asset.target for asset in catalog.assets
        if asset.kind in {'rule', 'skill'}
        and not asset.control_plane and asset.target is not None
    )
    assets = tuple(
        asset for asset in state.assets
        if not (
            asset.kind == 'file'
            and asset.role in {'rule', 'skill'}
            and asset.path.parts[:2] == ('.agents', f'{asset.role}s')
            and not any(
                source == asset.path or source in asset.path.parents
                for source in managed_sources
            )
        )
    )
    return OwnershipState(state.sources, assets, state.contracts, state.project_sync)


def verify_ownership(target_root: Path, state: OwnershipState | None) -> None:
    if state is None:
        return
    for asset in state.assets:
        if _actual_digest(target_root, asset) != asset.digest:
            suffix = f':{asset.key}' if asset.key is not None else ''
            raise OwnershipError(
                f'SmartKit-managed asset was modified outside setup: '
                f'{asset.path.as_posix()}{suffix}'
            )


def _role(path: PurePosixPath, key: str | None = None) -> str:
    if key is not None and key.split('.', 1)[0] in {'mcp_servers', 'mcpServers', 'servers'}:
        return 'mcp'
    if 'rules' in path.parts or 'instructions' in path.parts:
        return 'rule'
    if 'skills' in path.parts:
        return 'skill'
    if 'agents' in path.parts:
        return 'agent'
    return 'config'


def _desired_assets(
    files: Mapping[PurePosixPath, bytes],
    fields: Sequence[DesiredField],
    trees: Sequence[PurePosixPath],
    external_sources: Mapping[str, tuple[str, PurePosixPath]],
    structured_paths: frozenset[PurePosixPath],
    unmanaged_paths: frozenset[PurePosixPath],
) -> tuple[OwnedAsset, ...]:
    tree_set = tuple(sorted(set(trees), key=lambda item: item.as_posix()))
    assets: list[OwnedAsset] = []
    for root in tree_set:
        source = external_sources.get(root.name)
        assets.append(OwnedAsset(
            'tree', _role(root), root, _tree_digest_from_files(root, files),
            source=source[0] if source else None,
            source_path=source[1] if source else None,
        ))
    for path, content in sorted(files.items(), key=lambda item: item[0].as_posix()):
        if (
            path == OWNERSHIP_PATH
            or path in unmanaged_paths
            or path in structured_paths
            or any(root == path or root in path.parents for root in tree_set)
        ):
            continue
        assets.append(OwnedAsset('file', _role(path), path, _digest(content)))
    assets.extend(
        OwnedAsset('field', _role(field.path, field.key), field.path, _value_digest(field.value), field.key)
        for field in fields
    )
    return tuple(sorted(assets, key=lambda item: (
        item.path.as_posix(), item.key or '', item.kind,
    )))


def reconcile_ownership(
    target_root: Path,
    desired_files: Sequence[DesiredFile],
    desired_fields: Sequence[DesiredField],
    managed_trees: Sequence[PurePosixPath],
    *,
    sources: Sequence[Mapping[str, object]] = (),
    external_sources: Mapping[str, tuple[str, PurePosixPath]] | None = None,
    structured_paths: Sequence[PurePosixPath] = (),
    unmanaged_paths: Sequence[PurePosixPath] = (),
    previous: OwnershipState | None = None,
    contracts: Sequence[GeneratedContract] = (),
    project_files: Sequence[PurePosixPath] = (),
    project_fields: Sequence[tuple[PurePosixPath, str]] = (),
) -> OwnershipResult:
    previous = previous if previous is not None else load_ownership(target_root)
    verify_ownership(target_root, previous)
    files = {item.path: item.content for item in desired_files}
    desired_assets = _desired_assets(
        files,
        desired_fields,
        managed_trees,
        external_sources or {},
        frozenset(structured_paths) | frozenset(item.path for item in desired_fields),
        frozenset(unmanaged_paths),
    )
    desired_assets = tuple(
        replace(asset, role='project-agent') if asset.path in project_files
        else replace(asset, role='project-mcp')
        if (asset.path, asset.key) in project_fields else asset
        for asset in desired_assets
    )
    previous_by_id = {
        item.identity: item for item in previous.assets
    } if previous is not None else {}
    desired_by_id = {item.identity: item for item in desired_assets}
    for identity, asset in desired_by_id.items():
        if identity in previous_by_id:
            continue
        actual = _actual_digest(target_root, asset)
        if actual is not None and actual != asset.digest:
            suffix = f':{asset.key}' if asset.key is not None else ''
            raise OwnershipError(
                f'SmartKit cannot adopt conflicting project asset: '
                f'{asset.path.as_posix()}{suffix}'
            )
    removed = [
        asset for identity, asset in previous_by_id.items() if identity not in desired_by_id
    ]
    delete_paths = tuple(
        asset.path for asset in removed if asset.kind in {'file', 'tree'}
    )
    remove_fields = tuple(
        (asset.path, asset.key)
        for asset in removed
        if asset.kind == 'field' and asset.key is not None
    )
    manifest = serialize_ownership(OwnershipState(tuple(sources), desired_assets, tuple(contracts), True))
    return OwnershipResult(
        tuple(DesiredFile(path, content) for path, content in sorted(files.items())),
        manifest,
        tuple(sorted(set(delete_paths), key=lambda item: item.as_posix())),
        tuple(sorted(remove_fields, key=lambda item: (item[0].as_posix(), item[1]))),
    )


def serialize_ownership(state: OwnershipState) -> bytes:
    """Validate and serialize recorded ownership without consulting current source assets."""
    manifest_assets = []
    for asset in state.assets:
        item: dict[str, object] = {
            'kind': asset.kind,
            'role': asset.role,
            'path': asset.path.as_posix(),
            'digest': asset.digest,
        }
        if asset.key is not None:
            item['key'] = asset.key
        if asset.source is not None:
            item['source'] = asset.source
        if asset.source_path is not None:
            item['source_path'] = asset.source_path.as_posix()
        manifest_assets.append(item)
    next_document = {
        'sources': [dict(item) for item in state.sources],
        'assets': manifest_assets,
        'contracts': [
            {
                'id': item.id,
                'source': item.source.as_posix(),
                'target': item.target.as_posix(),
                'fingerprint': item.fingerprint,
                'outputs': [path.as_posix() for path in item.outputs],
            }
            for item in sorted(state.contracts, key=lambda item: item.id)
        ],
    }
    if state.project_sync:
        next_document['project_sync'] = 1
    _parse_ownership_document(next_document)
    return (json.dumps(next_document, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
