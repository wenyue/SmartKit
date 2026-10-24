from __future__ import annotations

import hashlib
import json
import os
import stat
from collections.abc import Sequence
from pathlib import Path, PurePosixPath

from project_state.models import AssetSpec, Catalog, ContractError
from project_state.ownership import GeneratedContract, OwnershipState
from project_state.paths import confined_target, is_link_like


def blueprint_root(asset: AssetSpec) -> PurePosixPath:
    """A Skill blueprint owns its resource directory; a Rule owns its entry only."""
    return asset.source.parent if asset.target is not None and asset.target.name == 'SKILL.md' else asset.source


def blueprint_files(source_root: Path, asset: AssetSpec) -> tuple[PurePosixPath, ...]:
    """Enumerate the complete blueprint input without following redirected paths."""
    entry = confined_target(source_root, asset.source)
    if not entry.is_file():
        raise ContractError(f'blueprint entry is not a regular file: {asset.source}')
    relative = blueprint_root(asset)
    if relative == asset.source:
        return (relative,)
    root = confined_target(source_root, relative)
    files: list[PurePosixPath] = []

    def failed(error: OSError) -> None:
        raise ContractError(f'cannot inspect blueprint directory: {relative}') from error

    for directory, directories, names in os.walk(root, followlinks=False, onerror=failed):
        parent = Path(directory)
        for name in [*directories, *names]:
            path = parent / name
            status = path.lstat()
            if is_link_like(path) or not (stat.S_ISDIR(status.st_mode) or stat.S_ISREG(status.st_mode)):
                raise ContractError(f'blueprint resource is unsafe: {path.relative_to(source_root)}')
            if stat.S_ISREG(status.st_mode):
                files.append(PurePosixPath(path.relative_to(source_root).as_posix()))
    return tuple(sorted(files))


def current_contracts(source_root: Path, catalog: Catalog) -> tuple[GeneratedContract, ...]:
    result: list[GeneratedContract] = []
    for asset in catalog.assets:
        if asset.kind != 'blueprint' or asset.control_plane or asset.target is None:
            continue
        identity = json.dumps({
            'source': asset.source.as_posix(),
            'target': asset.target.as_posix(),
            'metadata': dict(asset.metadata),
            'harnesses': [item.value for item in asset.harnesses],
        }, sort_keys=True).encode('utf-8')
        digest = hashlib.sha256(identity + b'\0')
        if blueprint_root(asset) == asset.source:
            digest.update((source_root / asset.source).read_bytes())
        else:
            for relative in blueprint_files(source_root, asset):
                digest.update(relative.as_posix().encode('utf-8') + b'\0')
                digest.update(hashlib.sha256((source_root / relative).read_bytes()).digest())
        fingerprint = digest.hexdigest()
        result.append(GeneratedContract(
            asset.id, asset.source, asset.target, fingerprint, (),
        ))
    return tuple(sorted(result, key=lambda item: item.id))


def generation_requests(
    source_root: Path, target_root: Path, catalog: Catalog, previous: OwnershipState | None,
) -> list[dict[str, str]]:
    requests: list[dict[str, str]] = []
    for contract in current_contracts(source_root, catalog):
        requests.append({
            'id': contract.id,
            'source': contract.source.as_posix(),
            'target': contract.target.as_posix(),
        })
    return requests


def reconcile_contracts(
    source_root: Path,
    catalog: Catalog,
    previous: OwnershipState | None,
    generated_outputs: Sequence[PurePosixPath],
) -> tuple[tuple[GeneratedContract, ...], set[PurePosixPath], set[PurePosixPath]]:
    recorded = {item.id: item for item in previous.contracts} if previous else {}
    outputs = set(generated_outputs)
    contracts: list[GeneratedContract] = []
    preserved: set[PurePosixPath] = set()
    for contract in current_contracts(source_root, catalog):
        if contract.target in outputs:
            paths = tuple(sorted(
                path for path in outputs
                if path == contract.target or (
                    contract.target.name == 'SKILL.md' and contract.target.parent in path.parents
                )
            ))
            contracts.append(GeneratedContract(
                contract.id, contract.source, contract.target, contract.fingerprint, paths,
            ))
        elif contract.id in recorded:
            old = recorded[contract.id]
            if (
                old.fingerprint != contract.fingerprint
                or old.source != contract.source or old.target != contract.target
            ):
                raise ContractError(f'changed contract requires generated outputs: {contract.id}')
            contracts.append(old)
            preserved.update(old.outputs)
    retained = {path for item in contracts for path in item.outputs}
    removed = {path for item in recorded.values() for path in item.outputs} - retained
    return tuple(contracts), removed, preserved
