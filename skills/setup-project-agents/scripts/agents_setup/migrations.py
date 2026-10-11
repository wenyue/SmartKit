"""Read release-declared project migrations; never infer them from version inequality."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath

from .catalog import _SEMVER, load_catalog
from .models import ContractError
from .ownership import load_ownership
from .project import confined_target


@dataclass(frozen=True)
class Migration:
    version: str
    guide: str


class SetupStatus(Enum):
    UNINITIALIZED = 'uninitialized'
    BASELINE_REQUIRED = 'baseline-required'


@dataclass(frozen=True)
class SetupVersion:
    version: str


def version_key(value: str) -> tuple:
    """Order validated SemVer releases, ignoring build metadata."""
    if not isinstance(value, str) or _SEMVER.fullmatch(value) is None:
        raise ContractError('setup version must be a semantic version')
    release, _, prerelease = value.split('+', 1)[0].partition('-')
    identifiers = tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in prerelease.split('.') if part
    )
    return tuple(int(part) for part in release.split('.')), not prerelease, identifiers


def load_migrations(source_root: Path) -> tuple[Migration, ...]:
    path = source_root / 'setup-assets/catalog/migrations.json'
    try:
        document = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f'cannot read project migration declarations: {path}') from error
    if not isinstance(document, dict) or set(document) != {'migrations'}:
        raise ContractError('project migration declarations must contain migrations')
    entries = document['migrations']
    if not isinstance(entries, list):
        raise ContractError('project migrations must be an array')
    result: list[Migration] = []
    current = version_key(load_catalog(source_root).plugin_version)
    previous = None
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'version', 'guide'}:
            raise ContractError('project migration must contain version and guide')
        key = version_key(entry['version'])
        if key > current or (previous is not None and key <= previous):
            raise ContractError('project migrations must be ordered unique released versions')
        guide = entry['guide']
        if not isinstance(guide, str):
            raise ContractError('project migration guide must be a relative reference with an anchor')
        relative, separator, anchor = guide.partition('#')
        if relative != 'references/migrations.md' or not separator or not anchor:
            raise ContractError('project migration guide must reference references/migrations.md')
        try:
            content = (source_root / 'skills/setup-project-agents' / relative).read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError) as error:
            raise ContractError('project migration guide is unavailable') from error
        headings = {
            ''.join(character for character in line.lstrip('#').strip().lower().replace(' ', '-')
                    if character.isalnum() or character in '-_')
            for line in content.splitlines() if line.startswith('#')
        }
        if anchor not in headings:
            raise ContractError(f'project migration guide anchor is missing: {guide}')
        result.append(Migration(entry['version'], guide))
        previous = key
    return tuple(result)


def applicable_migrations(source_root: Path, setup_version: str | None) -> tuple[Migration, ...]:
    migrations = load_migrations(source_root)
    if setup_version is None:
        return migrations
    baseline = version_key(setup_version)
    return tuple(item for item in migrations if version_key(item.version) > baseline)


def project_setup_version(target_root: Path, source_root: Path) -> SetupStatus | SetupVersion:
    """Return initialization evidence and baseline; malformed evidence remains an error."""
    lock = confined_target(target_root, PurePosixPath('.agents/smartkit.lock.json'))
    if not lock.exists():
        return SetupStatus.UNINITIALIZED
    load_ownership(target_root, catalog=load_catalog(source_root))
    config = confined_target(target_root, PurePosixPath('.agents/config.json'))
    if not config.exists():
        return SetupStatus.BASELINE_REQUIRED
    try:
        document = json.loads(config.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f'cannot read project setup version: {config}') from error
    if not isinstance(document, dict):
        raise ContractError('project config must contain an object')
    value = document.get('setupVersion')
    if value is not None:
        version_key(value)
        return SetupVersion(value)
    return SetupStatus.BASELINE_REQUIRED
