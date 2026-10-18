"""Discover project-native Agent definitions and the paths that freeze their inventory."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath

from .external_contract import is_link_like
from .project import confined_target
from .structured import parse_document


HOST_PATHS = {
    'codex': ('.codex/agents', '.toml'),
    'cursor': ('.cursor/agents', '.md'),
    'copilot': ('.github/agents', '.agent.md'),
    'qoder': ('.qoder/agents', '.md'),
}
CODEX_CONFIG = PurePosixPath('.codex/config.toml')


@dataclass(frozen=True)
class NativeAgent:
    harness: str
    id: str
    path: PurePosixPath
    references: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentDiscovery:
    agents: tuple[NativeAgent, ...]
    codex_roles_without_config_file: tuple[str, ...]
    evidence_paths: dict[PurePosixPath, bool]
    issues: tuple[str, ...]


def _reference_path(
    target: Path, declaring: Path, value: str, evidence: dict[PurePosixPath, bool],
) -> PurePosixPath:
    """Resolve parent segments only after checking each preceding path for links."""
    raw = declaring.parent / value
    try:
        parts = raw.relative_to(target).parts
    except ValueError as error:
        raise ValueError(f'path is outside the target: {value!r}') from error
    current = target
    for index, part in enumerate(parts):
        if part == '..':
            if current == target:
                raise ValueError(f'path is outside the target: {value!r}')
            current = current.parent
        else:
            current /= part
            evidence.setdefault(PurePosixPath(current.relative_to(target).as_posix()), False)
            if is_link_like(current):
                raise ValueError(f'Agent reference contains a symlink: {current}')
            if index < len(parts) - 1 and not current.is_dir():
                raise ValueError(f'Agent reference directory is missing or not a directory: {current}')
    return PurePosixPath(current.relative_to(target).as_posix())


def discover_native_agents(target: Path) -> AgentDiscovery:
    """Inspect only project paths; retain unsafe or unsupported references as issues.

    Evidence includes missing config files and discovery roots so adding a reference or
    definition changes the frozen session. No user configuration or outside file is read.
    """
    target = Path(target).absolute()
    evidence: dict[PurePosixPath, bool] = {CODEX_CONFIG: True}
    found: dict[tuple[str, str, PurePosixPath], NativeAgent] = {}
    roles_without_file: list[str] = []
    issues: list[str] = []

    def add(host: str, identity: str, relative: PurePosixPath, reference: str = '') -> None:
        evidence[relative] = True
        try:
            path = confined_target(target, relative)
            if not path.is_file():
                raise ValueError(f'Agent definition is missing or not a regular file: {relative}')
        except (OSError, ValueError) as error:
            issues.append(f'{reference or relative}: {error}')
            return
        key = host, identity, relative
        previous = found.get(key)
        references = previous.references if previous else ()
        found[key] = NativeAgent(host, identity, relative, references + ((reference,) if reference else ()))

    for host, (directory, suffix) in HOST_PATHS.items():
        relative_root = PurePosixPath(directory)
        evidence[relative_root] = False
        try:
            root = confined_target(target, relative_root)
            if not root.exists():
                continue
            if not root.is_dir():
                raise ValueError(f'Agent root is not a directory: {relative_root}')
            for parent, directories, files in os.walk(root, followlinks=False, onerror=lambda error: issues.append(str(error))):
                parent_path = Path(parent)
                for name in tuple(directories):
                    child = parent_path / name
                    if is_link_like(child):
                        evidence[PurePosixPath(child.relative_to(target).as_posix())] = False
                        issues.append(f'Agent discovery encountered a link: {child}')
                        directories.remove(name)
                for name in sorted(files):
                    child = parent_path / name
                    relative = PurePosixPath(child.relative_to(target).as_posix())
                    if is_link_like(child):
                        evidence[relative] = True
                        issues.append(f'Agent discovery encountered a link: {child}')
                    elif name.endswith(suffix):
                        add(host, name[:-len(suffix)], relative)
        except (OSError, ValueError) as error:
            issues.append(str(error))

    try:
        config_path = confined_target(target, CODEX_CONFIG)
        document = parse_document(config_path.read_bytes(), 'toml') if config_path.exists() else {}
        roles = document.get('agents', {})
        if not isinstance(roles, dict):
            raise ValueError(f'{CODEX_CONFIG}: agents must be a table')
        for identity, role in roles.items():
            if not isinstance(role, dict):
                continue  # Scalar settings share this table with custom role declarations.
            if 'config_file' not in role:
                roles_without_file.append(identity)
                continue  # A role may inherit defaults without a separate config file.
            reference = f'{CODEX_CONFIG}:agents.{identity}.config_file'
            value = role['config_file']
            if not isinstance(value, str) or not value.strip():
                issues.append(f'{reference}: expected a nonempty file reference')
                continue
            if value.startswith('~') or '$' in value or '%' in value or (os.name != 'nt' and PureWindowsPath(value).drive):
                issues.append(f'{reference}: unsupported path {value!r}; resolve with its host owner')
                continue
            # Codex resolves references from the declaring config, not the repository root.
            try:
                relative = _reference_path(target, config_path, value, evidence)
            except ValueError as error:
                issues.append(f'{reference}: {error}')
                continue
            add('codex', identity, relative, reference)
    except (OSError, ValueError) as error:
        issues.append(f'{CODEX_CONFIG}: {error}')

    identities: dict[tuple[str, str], set[PurePosixPath]] = {}
    for agent in found.values():
        identities.setdefault((agent.harness, agent.id), set()).add(agent.path)
    for (host, identity), paths in sorted(identities.items()):
        if len(paths) > 1:
            issues.append(f'Agent identity {host}/{identity} has multiple definitions: ' + ', '.join(str(path) for path in sorted(paths)))
    return AgentDiscovery(
        tuple(sorted(found.values(), key=lambda agent: (agent.harness, agent.id, agent.path))),
        tuple(sorted(roles_without_file)), evidence, tuple(issues),
    )
