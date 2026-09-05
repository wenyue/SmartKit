from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath

from agents_setup.catalog import (
    ContractError,
    load_catalog,
    parse_external_skills,
    parse_mcp_servers,
    parse_project_agents,
    safe_relative,
)
from agents_setup.discovery import DiscoveryError
from agents_setup.external import ExternalSkillError, snapshot_external_skills
from agents_setup.external_contract import (
    is_link_like as _is_link_like,
)
from agents_setup.models import Catalog, ChangeKind, Harness, Plan, ProjectConfig
from agents_setup.ownership import (
    OWNERSHIP_PATH,
    OwnershipError,
    load_ownership,
    verify_ownership,
)
from agents_setup.planner import PlanningError, build_plan
from agents_setup.project import ProjectError, inspect_project
from agents_setup.renderer import RenderError, render_desired_state
from agents_setup.source import InvalidFetchedSource, validate_source
from agents_setup.transaction import TransactionError, apply_plan
from agents_setup.validation import validate_rendered_state


_COMMIT = re.compile(r'^[0-9a-fA-F]{40}$')
_PROJECT_RULE = re.compile(r'^\d{2}-[a-z0-9][a-z0-9-]*\.md$')
_REQUEST_NAME = 'request.json'
_GENERATED_NAME = 'generated'
_GENERATION_MANIFEST = '.setup-generation.json'
_BLUEPRINT_TARGETS = (
    PurePosixPath('.agents/rules/00-project-tools.md'),
    PurePosixPath('.agents/rules/01-project-contracts.md'),
    PurePosixPath('.agents/rules/02-project-structure.md'),
    PurePosixPath('.agents/skills/change-set-verification/SKILL.md'),
    PurePosixPath('.agents/skills/worktree-environment-setup/SKILL.md'),
)
_HARNESSES = tuple(Harness)


class SetupError(ValueError):
    """Raised when a pinned setup session cannot be used safely."""


def normalize_source_commit(source_commit: str) -> str | None:
    """Convert the bootstrap-only offline sentinel at the pinned CLI boundary."""
    if source_commit == 'offline':
        return None
    if not isinstance(source_commit, str) or not _COMMIT.fullmatch(source_commit):
        raise ValueError('source_commit must be offline or a 40-character hexadecimal commit')
    return source_commit.lower()


def _private_session(value: Path) -> Path:
    session = Path(value).absolute()
    current = Path(session.anchor)
    for part in session.parts[1:]:
        current /= part
        try:
            status = current.lstat()
        except OSError as error:
            raise SetupError(f'session path cannot be inspected: {current}') from error
        if stat.S_ISLNK(status.st_mode) or _is_link_like(current):
            raise SetupError(f'session path contains an unsafe link: {current}')
    try:
        status = session.stat()
    except OSError as error:
        raise SetupError('session is unavailable') from error
    if not stat.S_ISDIR(status.st_mode):
        raise SetupError('session is not a directory')
    if os.name == 'posix' and (
        status.st_uid != os.geteuid() or stat.S_IMODE(status.st_mode) != 0o700
    ):
        raise SetupError('session must be private, exact mode 0700, and owned by the current user')
    return session


def _write_json(path: Path, document: Mapping[str, object]) -> None:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise SetupError(f'session file already exists: {path.name}') from error
    try:
        encoded = (json.dumps(document, sort_keys=True, indent=2) + '\n').encode('utf-8')
        remaining = encoded
        while remaining:
            written = os.write(descriptor, remaining)
            remaining = remaining[written:]
    finally:
        os.close(descriptor)


def _read_json(path: Path, label: str) -> Mapping[str, object]:
    try:
        if path.is_symlink() or not path.is_file():
            raise SetupError(f'{label} must be a regular file')
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SetupError(f'cannot read {label}') from error
    if not isinstance(value, Mapping):
        raise SetupError(f'{label} must be a JSON object')
    return value


def _request(
    source_commit: str | None,
    config: ProjectConfig,
    catalog: Catalog,
    *,
    target: Path,
    source_root: Path,
    source_fingerprint: str,
    external_snapshot_sha256: str | None,
    target_fingerprint: str,
) -> dict[str, object]:
    blueprint_assets = {
        asset.target: asset
        for asset in catalog.assets
        if asset.kind == 'blueprint' and asset.target is not None
    }
    if set(blueprint_assets) != set(_BLUEPRINT_TARGETS):
        raise SetupError('catalog does not declare the required generation targets')
    generation_requests = [
        {
            'id': blueprint_assets[path].id,
            'source': blueprint_assets[path].source.as_posix(),
            'target': path.as_posix(),
        }
        for path in _BLUEPRINT_TARGETS
    ]
    return {
        'target': str(target),
        'source_root': str(source_root),
        'source_commit': source_commit,
        'source_fingerprint': source_fingerprint,
        'external_snapshot_sha256': external_snapshot_sha256,
        'target_fingerprint': target_fingerprint,
        'harnesses': [item.value for item in _HARNESSES],
        'selected_rules': list(config.selected_rules),
        'selected_skills': list(config.selected_skills),
        'external_sources': [
            {
                'source': source.id,
                **({'ref': source.ref} if source.ref is not None else {}),
                'include': [item.path.as_posix() for item in source.skills],
            }
            for source in config.external_sources
        ],
        'mcp_servers': [
            {
                'id': server.id,
                'harnesses': [harness.value for harness in server.harnesses],
                **({'command': server.command} if server.command is not None else {}),
                **({'args': list(server.args)} if server.args else {}),
                **({'cwd': server.cwd} if server.cwd is not None else {}),
                **({'env': list(server.env)} if server.env else {}),
                **({'url': server.url} if server.url is not None else {}),
                **({
                    'overrides': [
                        {
                            'when': {
                                **({
                                    'harnesses': [
                                        harness.value for harness in override.harnesses
                                    ]
                                } if override.harnesses is not None else {}),
                                **({
                                    'operatingSystems': [
                                        item.value for item in override.operating_systems
                                    ]
                                } if override.operating_systems is not None else {}),
                            },
                            'set': {
                                **({
                                    'command': override.command
                                } if override.command is not None else {}),
                                **({
                                    'args': list(override.args)
                                } if override.args is not None else {}),
                                **({'cwd': override.cwd} if override.cwd is not None else {}),
                                **({
                                    'env': list(override.env)
                                } if override.env is not None else {}),
                                **({'url': override.url} if override.url is not None else {}),
                            },
                        }
                        for override in server.overrides
                    ]
                } if server.overrides else {}),
                **({
                    'readiness': {
                        **({
                            'harnesses': [
                                harness.value for harness in server.readiness.harnesses
                            ]
                        } if server.readiness.harnesses is not None else {}),
                        **({
                            'operatingSystems': [
                                item.value for item in server.readiness.operating_systems
                            ]
                        } if server.readiness.operating_systems is not None else {}),
                        **({
                            'checks': [dict(check) for check in server.readiness.checks]
                        } if server.readiness.checks is not None else {}),
                    }
                } if server.readiness is not None else {}),
            }
            for server in config.mcp_servers
        ],
        'project_agents': [
            {
                'id': agent.id,
                'source': agent.source.as_posix(),
                'description': agent.description,
                'harnesses': {
                    **({
                        'codex': {
                            **({'model': agent.codex.model} if agent.codex.model else {}),
                            **({
                                'model_reasoning_effort':
                                agent.codex.model_reasoning_effort
                            } if agent.codex.model_reasoning_effort else {}),
                            'sandbox_mode': agent.codex.sandbox_mode,
                        }
                    } if agent.codex is not None else {}),
                    **({
                        'cursor': {
                            **({'model': agent.cursor.model} if agent.cursor.model else {}),
                            'readonly': agent.cursor.readonly,
                        }
                    } if agent.cursor is not None else {}),
                    **({
                        'copilot': {
                            **({'model': agent.copilot.model} if agent.copilot.model else {}),
                            'disable_model_invocation':
                            agent.copilot.disable_model_invocation,
                        }
                    } if agent.copilot is not None else {}),
                },
            }
            for agent in config.agents
        ],
        'generation_requests': generation_requests,
    }


def _selected_request_ids(
    value: object,
    *,
    catalog: Catalog,
    kind: str,
) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SetupError(f'session request {kind} selections must be an array of IDs')
    if len(value) != len(set(value)):
        raise SetupError(f'session request {kind} selections contain duplicates')
    available = {
        asset.id
        for asset in catalog.assets
        if asset.kind == kind and not asset.control_plane
    }
    if set(value) - available:
        raise SetupError(f'session request {kind} selections contain unknown IDs')
    return tuple(value)


def _request_config(
    request: Mapping[str, object],
    source_commit: str | None,
    *,
    target: Path,
    source_root: Path,
    catalog: Catalog,
) -> ProjectConfig:
    required = {
        'target', 'source_root', 'source_commit', 'harnesses', 'selected_rules',
        'selected_skills', 'external_sources', 'mcp_servers', 'generation_requests',
        'external_snapshot_sha256', 'project_agents', 'source_fingerprint',
        'target_fingerprint',
    }
    if set(request) != required:
        raise SetupError('session request has an invalid shape')
    if request.get('source_commit') != source_commit:
        raise SetupError('session request source commit does not match this pinned source')
    if request.get('target') != str(target):
        raise SetupError('session request target does not match this invocation')
    if request.get('source_root') != str(source_root):
        raise SetupError('session request source root does not match this pinned source')
    source_fingerprint = request.get('source_fingerprint')
    if (
        not isinstance(source_fingerprint, str)
        or len(source_fingerprint) != 64
        or any(character not in '0123456789abcdef' for character in source_fingerprint)
    ):
        raise SetupError('session request source fingerprint is invalid')
    fingerprint = request.get('target_fingerprint')
    if (
        not isinstance(fingerprint, str)
        or len(fingerprint) != 64
        or any(character not in '0123456789abcdef' for character in fingerprint)
    ):
        raise SetupError('session request target fingerprint is invalid')
    try:
        snapshot_digest = request['external_snapshot_sha256']
        if snapshot_digest is not None and (
            not isinstance(snapshot_digest, str)
            or len(snapshot_digest) != 64
            or any(character not in '0123456789abcdef' for character in snapshot_digest)
        ):
            raise ValueError
        harnesses = tuple(Harness(item) for item in request['harnesses'])
        if harnesses != _HARNESSES:
            raise ValueError
        selections = (
            _selected_request_ids(request['selected_rules'], catalog=catalog, kind='rule'),
            _selected_request_ids(request['selected_skills'], catalog=catalog, kind='skill'),
        )
        generation = request['generation_requests']
        expected_generation = {
            asset.target.as_posix(): {
                'id': asset.id,
                'source': asset.source.as_posix(),
                'target': asset.target.as_posix(),
            }
            for asset in catalog.assets
            if asset.kind == 'blueprint' and asset.target is not None
        }
        if (
            not isinstance(generation, list)
            or len(generation) != len(_BLUEPRINT_TARGETS)
            or {
                item.get('target') for item in generation if isinstance(item, Mapping)
            } != set(expected_generation)
            or any(
                not isinstance(item, Mapping)
                or dict(item) != expected_generation.get(item.get('target'))
                for item in generation
            )
        ):
            raise ValueError
        external_sources = parse_external_skills(request['external_sources'], catalog)
        mcp_servers = parse_mcp_servers(request['mcp_servers'])
        project_agents = parse_project_agents(request['project_agents'])
        config = ProjectConfig(
            *selections, external_sources, mcp_servers, project_agents,
        )
    except (KeyError, TypeError, ValueError, SetupError) as error:
        raise SetupError('session request has invalid setup choices') from error
    return config


def _generated_outputs(
    session: Path,
    generation_requests: object,
) -> tuple[Path, tuple[PurePosixPath, ...]]:
    root = session / _GENERATED_NAME
    try:
        status = root.lstat()
    except OSError as error:
        raise SetupError('generated output directory is missing') from error
    if _is_link_like(root) or not stat.S_ISDIR(status.st_mode):
        raise SetupError('generated output directory is not a safe directory')
    if not isinstance(generation_requests, list) or not all(
        isinstance(item, Mapping) for item in generation_requests
    ):
        raise SetupError('session generation requests are invalid')
    expected_requests = {
        str(item['id']): PurePosixPath(str(item['target']))
        for item in generation_requests
    }
    manifest = _read_json(root / _GENERATION_MANIFEST, 'generation manifest')
    if set(manifest) != {'version', 'requests'} or manifest.get('version') != 1:
        raise SetupError('generation manifest has an invalid shape')
    declarations = manifest.get('requests')
    if not isinstance(declarations, list):
        raise SetupError('generation manifest requests must be an array')
    declared: set[PurePosixPath] = set()
    seen_ids: set[str] = set()
    for declaration in declarations:
        if not isinstance(declaration, Mapping) or set(declaration) != {'id', 'outputs'}:
            raise SetupError('generation manifest request has an invalid shape')
        request_id = declaration.get('id')
        outputs = declaration.get('outputs')
        if (
            not isinstance(request_id, str)
            or request_id not in expected_requests
            or request_id in seen_ids
            or not isinstance(outputs, list)
            or not outputs
            or not all(isinstance(item, str) for item in outputs)
        ):
            raise SetupError('generation manifest request does not match the session request')
        seen_ids.add(request_id)
        primary = expected_requests[request_id]
        paths: list[PurePosixPath] = []
        for value in outputs:
            try:
                path = safe_relative(value, 'generation manifest output path')
            except ContractError as error:
                raise SetupError('generation manifest contains an unsafe output path') from error
            paths.append(path)
        if len(paths) != len(set(paths)) or primary not in paths:
            raise SetupError('generation manifest must declare each primary target exactly once')
        if primary.parts[:2] == ('.agents', 'rules'):
            if set(paths) != {primary}:
                raise SetupError('generated Rule request cannot declare supporting outputs')
        elif any(path != primary and primary.parent not in path.parents for path in paths):
            raise SetupError('generated Skill supporting output is outside its Skill directory')
        if declared.intersection(paths):
            raise SetupError('generation manifest declares one output more than once')
        declared.update(paths)
    if seen_ids != set(expected_requests):
        raise SetupError('generation manifest does not declare every generation request')
    files: set[str] = set()
    expected_directories = {PurePosixPath('.')}
    for expected_path in declared:
        parent = expected_path.parent
        while parent != PurePosixPath('.'):
            expected_directories.add(parent)
            parent = parent.parent
    entries: list[Path] = []
    for directory, directories, names in os.walk(
        root, topdown=True, followlinks=False,
    ):
        parent = Path(directory)
        retained: list[str] = []
        for name in directories:
            path = parent / name
            entries.append(path)
            if not _is_link_like(path):
                retained.append(name)
        directories[:] = retained
        entries.extend(parent / name for name in names)
    for path in sorted(entries, key=lambda item: item.relative_to(root).as_posix()):
        try:
            status = path.lstat()
        except OSError as error:
            raise SetupError('generated output cannot be inspected') from error
        if _is_link_like(path):
            raise SetupError('generated output contains a link-like entry')
        relative = PurePosixPath(path.relative_to(root).as_posix())
        if path.is_file() and relative == PurePosixPath(_GENERATION_MANIFEST):
            continue
        if path.is_file():
            files.add(path.relative_to(root).as_posix())
        elif path.is_dir() and relative not in expected_directories:
            raise SetupError(
                'generated output contains an undeclared directory: '
                f'{relative.as_posix()}; declare exact outputs in {_GENERATION_MANIFEST}'
            )
        elif not path.is_dir():
            raise SetupError('generated output contains a non-file entry')
    expected = {path.as_posix() for path in declared}
    if files != expected:
        raise SetupError('generated outputs must match the exact generation manifest')
    return root, tuple(sorted(declared, key=lambda item: item.as_posix()))


def _target_link_boundary(
    root: Path,
    relative: PurePosixPath,
) -> PurePosixPath | None:
    current = root
    for part in relative.parts:
        current /= part
        if _is_link_like(current):
            return PurePosixPath(current.relative_to(root).as_posix())
    return None


def _add_target_tree(
    root: Path,
    relative: PurePosixPath,
    paths: dict[PurePosixPath, bool],
) -> None:
    """Add one setup-consumed tree without traversing a link-like boundary."""
    paths[relative] = True
    boundary = _target_link_boundary(root, relative)
    if boundary is not None:
        paths[boundary] = True
        return
    target = root.joinpath(*relative.parts)
    if not target.exists() or not target.is_dir():
        return
    for directory, directories, files in os.walk(
        target, topdown=True, followlinks=False,
    ):
        parent = Path(directory)
        retained: list[str] = []
        for name in directories:
            child = parent / name
            child_relative = PurePosixPath(child.relative_to(root).as_posix())
            paths[child_relative] = True
            if not _is_link_like(child):
                retained.append(name)
        directories[:] = retained
        for name in files:
            child = parent / name
            paths[PurePosixPath(child.relative_to(root).as_posix())] = True


def _target_evidence_paths(
    root: Path,
    *,
    source_root: Path,
    catalog: Catalog,
    config: ProjectConfig,
) -> dict[PurePosixPath, bool]:
    """Return the closed target surface consumed by setup after prepare.

    The boolean records whether file bytes, rather than only entry presence and type, are
    setup evidence. Project Skill bodies are project-owned and are not consumed by setup.
    """
    root = Path(root).absolute()
    source_root = Path(source_root).absolute()
    paths: dict[PurePosixPath, bool] = {PurePosixPath('.'): False}

    def add(relative: PurePosixPath, *, content: bool = True) -> None:
        paths[relative] = paths.get(relative, False) or content

    add(PurePosixPath('.agents/config.json'))
    add(OWNERSHIP_PATH)
    try:
        previous = load_ownership(root)
    except OwnershipError as error:
        raise SetupError(str(error)) from error
    if previous is not None:
        for asset in previous.assets:
            if asset.kind == 'tree':
                _add_target_tree(root, asset.path, paths)
            else:
                add(asset.path)

    assets_by_id = {asset.id: asset for asset in catalog.assets}
    for asset in catalog.assets:
        if asset.control_plane or asset.target is None:
            continue
        if asset.kind == 'wrapper':
            for rule_id in config.selected_rules:
                source = assets_by_id[rule_id]
                wrapper = asset.target.as_posix().replace(
                    '{rule-name}', source.source.stem,
                )
                add(PurePosixPath(wrapper))
            continue
        if asset.kind == 'skill':
            _add_target_tree(root, asset.target, paths)
            continue
        if (
            asset.kind == 'blueprint'
            and asset.target.parts[:2] == ('.agents', 'skills')
        ):
            _add_target_tree(root, asset.target.parent, paths)
            continue
        if asset.kind == 'agent':
            source = source_root.joinpath(*asset.source.parts)
            if source.is_dir():
                for child in source.iterdir():
                    if child.is_file():
                        add(asset.target / child.relative_to(source).as_posix())
            continue
        add(asset.target)

    rules_root = root / '.agents' / 'rules'
    add(PurePosixPath('.agents/rules'))
    if (
        _target_link_boundary(root, PurePosixPath('.agents/rules')) is None
        and rules_root.exists()
        and rules_root.is_dir()
    ):
        for child in rules_root.iterdir():
            if _is_link_like(child) or (
                child.is_file() and _PROJECT_RULE.fullmatch(child.name) is not None
            ):
                add(PurePosixPath(child.relative_to(root).as_posix()))

    skills_root = root / '.agents' / 'skills'
    add(PurePosixPath('.agents/skills'), content=False)
    if (
        _target_link_boundary(root, PurePosixPath('.agents/skills')) is None
        and skills_root.exists()
        and skills_root.is_dir()
    ):
        for child in skills_root.iterdir():
            relative = PurePosixPath(child.relative_to(root).as_posix())
            if _is_link_like(child):
                add(relative, content=False)
                continue
            if child.is_dir() and (
                _is_link_like(child / 'SKILL.md') or (child / 'SKILL.md').is_file()
            ):
                add(relative, content=False)
                add(relative / 'SKILL.md', content=False)

    for agent in config.agents:
        add(agent.source)
        if agent.codex is not None:
            add(PurePosixPath('.codex/agents') / f'{agent.id}.toml')
        if agent.cursor is not None:
            add(PurePosixPath('.cursor/agents') / f'{agent.id}.md')
        if agent.copilot is not None:
            add(PurePosixPath('.github/agents') / f'{agent.id}.agent.md')
        if agent.qoder is not None:
            add(PurePosixPath('.qoder/agents') / f'{agent.id}.md')
    for skill in config.external_skills:
        _add_target_tree(
            root,
            PurePosixPath('.agents/skills') / skill.name,
            paths,
        )
    native_mcp = {
        Harness.CODEX: PurePosixPath('.codex/config.toml'),
        Harness.CURSOR: PurePosixPath('.cursor/mcp.json'),
        Harness.COPILOT: PurePosixPath('.vscode/mcp.json'),
        Harness.QODER: PurePosixPath('.qoder/mcp.json'),
    }
    for server in config.mcp_servers:
        for harness in server.harnesses:
            add(native_mcp[harness])
    for relative in tuple(paths):
        for parent in relative.parents:
            if parent != PurePosixPath('.'):
                add(parent, content=False)
    return paths


def _target_fingerprint(
    root: Path,
    *,
    source_root: Path,
    catalog: Catalog,
    config: ProjectConfig,
    excluded_paths: frozenset[PurePosixPath] = frozenset(),
) -> str:
    """Fingerprint only target evidence consumed by the frozen setup request."""
    root = Path(root).absolute()
    paths = _target_evidence_paths(
        root,
        source_root=source_root,
        catalog=catalog,
        config=config,
    )
    digest = hashlib.sha256()
    digest.update(b'smartkit-setup-target\0v2\0')
    link_roots: list[PurePosixPath] = []
    for relative_path, include_content in sorted(
        paths.items(), key=lambda item: item[0].as_posix(),
    ):
        if relative_path in excluded_paths:
            continue
        if any(
            parent == relative_path or parent in relative_path.parents
            for parent in link_roots
        ):
            continue
        path = root if relative_path == PurePosixPath('.') else root.joinpath(
            *relative_path.parts
        )
        relative = relative_path.as_posix().encode('utf-8', 'surrogateescape')
        try:
            status = path.lstat()
        except FileNotFoundError:
            digest.update(
                b'M\0' + relative + b'\0' + b'0\0' + hashlib.sha256(b'').digest()
            )
            continue
        except OSError as error:
            raise SetupError('target changed while its setup fingerprint was captured') from error
        if _is_link_like(path):
            kind = b'L'
            link_roots.append(relative_path)
            try:
                content = os.fsencode(os.readlink(path))
            except OSError as error:
                raise SetupError(
                    'target contains a link-like entry that cannot be fingerprinted'
                ) from error
        elif stat.S_ISREG(status.st_mode):
            kind = b'F'
            content = b''
            if include_content:
                try:
                    content = path.read_bytes()
                except OSError as error:
                    raise SetupError(
                        'target changed while its setup fingerprint was captured'
                    ) from error
        elif stat.S_ISDIR(status.st_mode):
            kind, content = b'D', b''
        else:
            kind, content = b'O', b''
        digest.update(kind + b'\0' + relative + b'\0')
        digest.update(str(stat.S_IMODE(status.st_mode)).encode() + b'\0')
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest()


def _postcondition_exclusions(root: Path, plan: Plan) -> frozenset[PurePosixPath]:
    excluded = {
        change.path
        for change in plan.changes
        if change.kind is not ChangeKind.UNCHANGED
    }
    for change in plan.changes:
        if change.kind is not ChangeKind.CREATE:
            continue
        for parent in change.path.parents:
            if parent == PurePosixPath('.'):
                continue
            if not root.joinpath(*parent.parts).exists():
                excluded.add(parent)
    return frozenset(excluded)


def _source_fingerprint(root: Path, catalog: Catalog) -> str:
    """Bind every setup-controlled source byte used after prepare."""
    root = Path(root).absolute()
    paths = {
        root / relative
        for relative in (
            'VERSION',
            '.codex-plugin/plugin.json',
            '.cursor-plugin/plugin.json',
            '.qoder-plugin/plugin.json',
            'plugin.json',
            'skills/registry.json',
            'setup-assets/catalog/assets.json',
            'setup-assets/catalog/harnesses.json',
            'setup-assets/catalog/project-config.schema.json',
        )
    }
    sources = [root / asset.source.as_posix() for asset in catalog.assets]
    sources.extend((
        root / 'skills/setup-project-agents',
        root / 'skills/write-rules-and-skills',
        root / 'skills/writing-for-agents',
    ))
    for source in sources:
        if source.is_file():
            paths.add(source)
        elif source.is_dir():
            paths.update(
                path for path in source.rglob('*')
                if path.is_file()
                and '__pycache__' not in path.parts
                and path.suffix not in {'.pyc', '.pyo'}
            )
        else:
            raise SetupError(
                'setup source dependency is missing: '
                f'{source.relative_to(root).as_posix()}'
            )
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode()
        try:
            content = path.read_bytes()
            mode = stat.S_IMODE(path.stat().st_mode)
        except OSError as error:
            raise SetupError('setup source changed while its fingerprint was captured') from error
        digest.update(relative + b'\0' + str(mode).encode() + b'\0')
        digest.update(hashlib.sha256(content).digest())
    return digest.hexdigest()


def _stable_target_observation(
    target: Path,
    *,
    source_root: Path,
    catalog: Catalog,
):
    """Bind parsed project intent to one stable setup-evidence fingerprint."""
    project = inspect_project(target, catalog=catalog)
    fingerprint = _target_fingerprint(
        project.root,
        source_root=source_root,
        catalog=catalog,
        config=project.config,
    )
    confirmed = inspect_project(target, catalog=catalog)
    confirmed_fingerprint = _target_fingerprint(
        confirmed.root,
        source_root=source_root,
        catalog=catalog,
        config=confirmed.config,
    )
    if project.config != confirmed.config or fingerprint != confirmed_fingerprint:
        raise SetupError('target changed during start; retry from current state')
    return confirmed, confirmed_fingerprint


def _emit_result(
    *,
    phase: str,
    source_commit: str | None,
    changed_paths: Sequence[str],
    harnesses: Sequence[str],
    external_skills: Sequence[str],
    external_sources: Sequence[Mapping[str, object]],
    preserved_paths: Sequence[str],
) -> None:
    print(json.dumps({
        'phase': phase,
        'source_commit': source_commit,
        'changed_paths': sorted(changed_paths),
        'harnesses': list(harnesses),
        'external_skills': sorted(external_skills),
        'external_sources': list(external_sources),
        'preserved_paths': sorted(preserved_paths),
    }, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            'Implementation CLI for setup bootstrap and workflow only. Direct public use of '
            'prepare or finish is unsupported; use setup_project_agents.sh or '
            'setup_project_agents.ps1.'
        ),
        allow_abbrev=False,
    )
    phases = parser.add_subparsers(dest='phase', required=True)
    for phase in ('prepare', 'finish'):
        command = phases.add_parser(phase, allow_abbrev=False)
        command.add_argument('--target', type=Path, required=True)
        command.add_argument('--session', type=Path, required=True)
        command.add_argument('--source-root', type=Path, required=True)
        command.add_argument('--source-commit', required=True)
        command.add_argument('--no-bootstrap', action='store_true', required=True)
    return parser


def _prepare(args: argparse.Namespace, session: Path, source_commit: str | None) -> None:
    catalog = load_catalog(args.source_root)
    source_fingerprint = _source_fingerprint(args.source_root, catalog)
    project, target_fingerprint = _stable_target_observation(
        args.target,
        source_root=args.source_root,
        catalog=catalog,
    )
    config = project.config
    try:
        verify_ownership(project.root, load_ownership(project.root))
    except OwnershipError as error:
        raise SetupError(str(error)) from error
    generated = session / _GENERATED_NAME
    generated_rules = generated / '.agents' / 'rules'
    generated_skills = generated / '.agents' / 'skills'
    try:
        generated_rules.mkdir(parents=True, exist_ok=False)
        generated_skills.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        raise SetupError('cannot create generated output directories') from error
    external_root = snapshot_external_skills(
        config.external_sources,
        session=session,
        existing_manifest=project.root / '.agents/smartkit.lock.json',
    )
    external_snapshot_sha256 = None
    if external_root is not None:
        metadata = external_root / 'sources.json'
        try:
            external_snapshot_sha256 = hashlib.sha256(metadata.read_bytes()).hexdigest()
        except OSError as error:
            raise SetupError('cannot bind external Skill source metadata') from error
    current = inspect_project(args.target, catalog=catalog)
    if config != current.config or target_fingerprint != _target_fingerprint(
        current.root,
        source_root=args.source_root,
        catalog=catalog,
        config=current.config,
    ):
        raise SetupError('target changed during start; retry from current state')
    if source_fingerprint != _source_fingerprint(args.source_root, catalog):
        raise SetupError('setup source changed during start; retry')
    _write_json(
        session / _REQUEST_NAME,
        _request(
            source_commit,
            config,
            catalog,
            target=project.root,
            source_root=Path(args.source_root).absolute(),
            source_fingerprint=source_fingerprint,
            external_snapshot_sha256=external_snapshot_sha256,
            target_fingerprint=target_fingerprint,
        ),
    )


def _plan(
    args: argparse.Namespace,
    session: Path,
    source_commit: str | None,
    *,
    verify_target_fingerprint: bool,
):
    catalog = load_catalog(args.source_root)
    project = inspect_project(args.target, catalog=catalog)
    request = _read_json(session / _REQUEST_NAME, 'session request')
    config = _request_config(
        request,
        source_commit,
        target=project.root,
        source_root=Path(args.source_root).absolute(),
        catalog=catalog,
    )
    if (
        verify_target_fingerprint
        and request['target_fingerprint'] != _target_fingerprint(
            project.root,
            source_root=args.source_root,
            catalog=catalog,
            config=config,
        )
    ):
        raise SetupError('target changed after start; cancel and restart from current state')
    if request['source_fingerprint'] != _source_fingerprint(args.source_root, catalog):
        raise SetupError('setup source changed after start; cancel and restart')
    external_root = session / 'external-skills'
    expected_snapshot_digest = request['external_snapshot_sha256']
    if bool(config.external_sources) != (expected_snapshot_digest is not None):
        raise SetupError('session request external Skill snapshot binding is invalid')
    if expected_snapshot_digest is not None:
        try:
            actual_snapshot_digest = hashlib.sha256(
                (external_root / 'sources.json').read_bytes()
            ).hexdigest()
        except OSError as error:
            raise SetupError('external Skill source metadata is missing') from error
        if actual_snapshot_digest != expected_snapshot_digest:
            raise SetupError('external Skill source metadata changed after prepare')
    generated, generated_outputs = _generated_outputs(
        session, request['generation_requests']
    )
    rendered = render_desired_state(
        args.source_root,
        project.root,
        catalog,
        config,
        generated,
        external_root if config.external_sources else None,
        generated_outputs=generated_outputs,
    )
    validate_rendered_state(rendered)
    plan = build_plan(
        project.root,
        rendered.files,
        rendered.fields,
        delete_paths=rendered.delete_paths,
        replace_roots=rendered.replace_roots,
    )
    return plan, project.root, config, rendered


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    try:
        session = _private_session(args.session)
        validate_source(args.source_root)
        source_commit = normalize_source_commit(args.source_commit)
        if args.phase == 'prepare':
            _prepare(args, session, source_commit)
            return 0
        plan, target, config, rendered = _plan(
            args,
            session,
            source_commit,
            verify_target_fingerprint=True,
        )
        result_context = {
            'harnesses': [item.value for item in _HARNESSES],
            'external_skills': [item.name for item in config.external_skills],
            'external_sources': rendered.external_sources,
            'preserved_paths': [item.as_posix() for item in rendered.preserved_paths],
        }
        changed_paths = [
            change.path.as_posix()
            for change in plan.changes
            if change.kind.value != 'unchanged'
        ]
        request = _read_json(session / _REQUEST_NAME, 'session request')
        catalog = load_catalog(args.source_root)
        if request['source_fingerprint'] != _source_fingerprint(
            args.source_root, catalog
        ):
            raise SetupError(
                'setup source changed during planning; cancel and restart'
            )
        if request['target_fingerprint'] != _target_fingerprint(
            target,
            source_root=args.source_root,
            catalog=catalog,
            config=config,
        ):
            raise SetupError(
                'target changed after planning; cancel and restart from current state'
            )
        postcondition_exclusions = _postcondition_exclusions(target, plan)
        protected_target_fingerprint = _target_fingerprint(
            target,
            source_root=args.source_root,
            catalog=catalog,
            config=config,
            excluded_paths=postcondition_exclusions,
        )

        def postcondition() -> None:
            check_plan, _, _, _ = _plan(
                args,
                session,
                source_commit,
                verify_target_fingerprint=False,
            )
            drift = [
                change.path.as_posix()
                for change in check_plan.changes
                if change.kind.value != 'unchanged'
            ]
            if drift:
                raise SetupError(
                    'post-apply validation did not converge: ' + ', '.join(drift)
                )
            if protected_target_fingerprint != _target_fingerprint(
                target,
                source_root=args.source_root,
                catalog=catalog,
                config=config,
                excluded_paths=postcondition_exclusions,
            ):
                raise SetupError('target changed during finish')

        apply_plan(target, plan, postcondition=postcondition)
        _emit_result(
            phase=args.phase,
            source_commit=source_commit,
            changed_paths=changed_paths,
            **result_context,
        )
        return 0
    except (
        ContractError,
        DiscoveryError,
        ExternalSkillError,
        InvalidFetchedSource,
        OSError,
        PlanningError,
        ProjectError,
        RenderError,
        SetupError,
        TransactionError,
        ValueError,
    ) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
