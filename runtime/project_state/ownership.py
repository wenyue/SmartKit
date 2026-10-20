"""Read ownership evidence without reconciliation or filesystem changes."""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from .catalog import safe_field_key, safe_relative
from .models import ContractError
from .paths import ProjectError, confined_target, is_link_like as _is_link_like
from .sources import ExternalContractError, LICENSE_MARKERS, validate_ref, validate_source_identity


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


def _is_digest(value: object, length: int = 64) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in '0123456789abcdef' for character in value)
    )


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


def _target(target_root: Path, path: PurePosixPath) -> Path:
    try:
        return confined_target(target_root, path)
    except ProjectError as error:
        raise OwnershipError(str(error)) from error


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
