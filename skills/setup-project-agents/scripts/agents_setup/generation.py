from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from pathlib import Path, PurePosixPath

from .models import Catalog, ContractError
from .ownership import GeneratedContract, OwnershipState
from .project import confined_target


def current_contracts(source_root: Path, catalog: Catalog) -> tuple[GeneratedContract, ...]:
    result: list[GeneratedContract] = []
    for asset in catalog.assets:
        if asset.kind != 'blueprint' or asset.control_plane or asset.target is None:
            continue
        content = (source_root / asset.source).read_bytes()
        identity = json.dumps({
            'source': asset.source.as_posix(),
            'target': asset.target.as_posix(),
            'metadata': dict(asset.metadata),
            'harnesses': [item.value for item in asset.harnesses],
        }, sort_keys=True).encode('utf-8')
        fingerprint = hashlib.sha256(identity + b'\0' + content).hexdigest()
        result.append(GeneratedContract(
            asset.id, asset.source, asset.target, fingerprint, (),
        ))
    return tuple(sorted(result, key=lambda item: item.id))


def generation_requests(
    source_root: Path, target_root: Path, catalog: Catalog, previous: OwnershipState | None,
) -> list[dict[str, str]]:
    recorded = {item.id: item for item in previous.contracts} if previous else {}
    requests: list[dict[str, str]] = []
    for contract in current_contracts(source_root, catalog):
        old = recorded.get(contract.id)
        if (
            old is not None and old.fingerprint == contract.fingerprint
            and old.source == contract.source and old.target == contract.target
            and all(confined_target(target_root, path).is_file() for path in old.outputs)
        ):
            continue
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
