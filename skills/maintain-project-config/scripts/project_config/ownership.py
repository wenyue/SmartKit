from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from project_state.models import Catalog
from project_state.ownership import (
    OWNERSHIP_PATH,
    OwnershipError,
    OwnedAsset,
    GeneratedContract,
    OwnershipState,
    _parse_ownership_document,
    _target,
    load_ownership_file,
)
from project_state.paths import is_link_like as _is_link_like
from project_state.structured import StructuredConfigError, parse_document

from .models import DesiredField, DesiredFile
from .structured import canonical_value_bytes, field_value, format_for_path


@dataclass(frozen=True)
class OwnershipResult:
    files: tuple[DesiredFile, ...]
    manifest: bytes
    delete_paths: tuple[PurePosixPath, ...]
    remove_fields: tuple[tuple[PurePosixPath, str], ...]


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


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
    project_setting_fields: Sequence[tuple[PurePosixPath, str]] = (),
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
        replace(asset, role='project-setting') if (asset.path, asset.key) in project_setting_fields
        else replace(asset, role='project-agent') if asset.path in project_files
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
