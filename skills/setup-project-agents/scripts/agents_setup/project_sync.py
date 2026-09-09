from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .catalog import load_catalog
from .discovery import discover_project_skills
from .external_contract import is_link_like
from .models import ChangeKind, DesiredField, DesiredFile, Plan
from .ownership import (
    OWNERSHIP_PATH, OwnershipState, load_ownership, reconcile_ownership,
    serialize_ownership, verify_ownership, _parse_ownership_document,
)
from .planner import _read_current, build_plan
from .project import confined_target, inspect_project
from .project_rendering import (
    _MCP_NATIVE, _load_structured, _remove_dotted_field, _render_project_agents,
    _render_project_mcp, _safe_leaves,
)
from .project_rules import _plan_project_rule_sync
from .structured import dump_document, field_value, format_for_path
from .transaction import TransactionError, apply_plan


class ProjectSyncError(ValueError):
    """Raised when project-only synchronization cannot converge safely."""


@dataclass(frozen=True)
class ProjectSyncResult:
    check: str
    changed_paths: tuple[str, ...]
    preserved_paths: tuple[str, ...]


def _external_declarations(config):
    return {
        source.id: (source.url, source.ref, frozenset(
            (skill.id, skill.path.as_posix()) for skill in source.skills
        )) for source in config.external_sources
    }


def _recorded_declarations(state):
    return {
        str(source['id']): (source['url'], source['requested_ref'], frozenset(
            (skill['id'], skill['path']) for skill in source['skills']
        )) for source in state.sources
    }


def _inputs(target: Path, catalog):
    """Observe local declarations and discovery entries, including additions and removals."""
    config = inspect_project(target, catalog=catalog).config
    paths = {PurePosixPath('.agents/config.json')}
    paths.update(agent.source for agent in config.agents)
    directories = []
    for relative in (PurePosixPath('.agents/rules'), PurePosixPath('.agents/skills')):
        root = confined_target(target, relative)
        if not root.exists():
            directories.append((relative, None))
            continue
        if not root.is_dir():
            raise ProjectSyncError(f'project discovery root is not a directory: {relative}')
        entries = []
        for child in sorted(root.iterdir()):
            if is_link_like(child):
                raise ProjectSyncError(f'project discovery entry is unsafe: {relative / child.name}')
            entries.append((child.name, child.is_dir()))
            if relative.name == 'rules' and child.is_file():
                paths.add(relative / child.name)
            elif relative.name == 'skills' and child.is_dir():
                paths.add(relative / child.name / 'SKILL.md')
        directories.append((relative, tuple(entries)))
    return config, tuple(directories), tuple(
        (path, _read_current(target, path)) for path in sorted(paths)
    )


def _plan(source: Path, target: Path, catalog):
    state = load_ownership(target)
    if state is None or not state.project_sync:
        raise ProjectSyncError(
            'project synchronization needs established project mapping ownership; '
            'run full setup first (sync-project-rules remains available for AGENTS.md only)'
        )
    config = inspect_project(target, catalog=catalog).config
    if _external_declarations(config) != _recorded_declarations(state):
        raise ProjectSyncError('external Skill declarations changed; run full setup')
    managed = tuple(asset for asset in state.assets if asset.role in {'project-agent', 'project-mcp'})
    retained = tuple(asset for asset in state.assets if asset not in managed)
    project_state = OwnershipState((), managed)
    files = {}
    sources = _render_project_agents(files, target, config)
    project_files = tuple(files)
    observed_paths = {OWNERSHIP_PATH, PurePosixPath('AGENTS.md'), *project_files,
                      *(asset.path for asset in managed),
                      *(_MCP_NATIVE[harness][0] for server in config.mcp_servers for harness in server.harnesses)}
    observed = {path: _read_current(target, path) for path in observed_paths}
    verify_ownership(target, project_state)
    documents = {}
    templates = {}
    deletes = set()
    previous_fields = frozenset((asset.path, asset.key) for asset in managed if asset.kind == 'field')
    # Remove recorded leaves before overlay so removed declarations and overrides retire together.
    for path, key in previous_fields:
        format_name = format_for_path(path)
        if path not in documents:
            documents[path] = _load_structured(confined_target(target, path), format_name)
        _remove_dotted_field(documents[path], key)
    _render_project_mcp(target, config, documents, templates, deletes, frozenset(), None)
    fields = []
    for path, document in documents.items():
        format_name = format_for_path(path)
        files[path] = dump_document(document, format_name)
        fields.extend(DesiredField(path, key, value, format_name)
                      for key, value in _safe_leaves(templates.get(path, {})))
    identities = {asset.identity for asset in managed}
    for path in project_files:
        if ('file', path, None) not in identities and confined_target(target, path).exists():
            raise ProjectSyncError(f'unrecorded Agent adapter collision: {path}; run full setup or resolve ownership')
    for field in fields:
        if ('field', field.path, field.key) in identities:
            continue
        document = _load_structured(confined_target(target, field.path), field.format)
        if field_value(document, field.key)[0]:
            raise ProjectSyncError(f'unrecorded MCP field collision: {field.path}:{field.key}; resolve ownership')
    for asset in retained:
        if any(asset.path == path or (asset.kind == 'tree' and asset.path in path.parents)
               for path in project_files) or any(
            asset.path == field.path and (
                asset.kind != 'field' or asset.key == field.key
                or asset.key.startswith(field.key + '.') or field.key.startswith(asset.key + '.')
            ) for field in fields
        ):
            raise ProjectSyncError(f'project mapping conflicts with preserved ownership: {asset.path}')
    result = reconcile_ownership(
        target, tuple(DesiredFile(path, content) for path, content in files.items()),
        fields, (), previous=project_state, structured_paths=tuple(documents),
        project_files=project_files, project_fields=tuple((field.path, field.key) for field in fields),
    )
    next_assets = _parse_ownership_document(json.loads(result.manifest)).assets
    files[OWNERSHIP_PATH] = serialize_ownership(OwnershipState(
        state.sources, tuple(sorted((*retained, *next_assets), key=lambda asset: (
            asset.path.as_posix(), asset.key or '', asset.kind,
        ))), state.contracts, True,
    ))
    rule_plan = _plan_project_rule_sync(source, target)
    rule_change = rule_plan.changes[0]
    files[rule_change.path] = rule_change.content
    skill_roots = frozenset(
        asset.path if asset.kind == 'tree' else asset.path.parent
        for asset in state.assets if asset.role == 'skill'
    ) | frozenset(contract.target.parent for contract in state.contracts if contract.target.name == 'SKILL.md')
    skills = discover_project_skills(target, catalog, previous_managed=skill_roots)
    preserved = tuple(sorted({
        *(source.as_posix() for source in sources),
        *((skill.path / 'SKILL.md').as_posix() for skill in skills),
        *(output.as_posix() for contract in state.contracts for output in contract.outputs),
    }))
    plan = build_plan(target, tuple(DesiredFile(path, content) for path, content in files.items()),
                      fields, delete_paths=result.delete_paths)
    if observed != {path: _read_current(target, path) for path in observed_paths}:
        raise ProjectSyncError('project adapters changed while synchronization was planned; retry from current inputs')
    return plan, preserved


def _changed(plan: Plan) -> tuple[str, ...]:
    return tuple(change.path.as_posix() for change in plan.changes if change.kind is not ChangeKind.UNCHANGED)


def synchronize_project(source_root: Path, target_root: Path, *, check_only: bool) -> ProjectSyncResult:
    """Reconcile recorded project mappings without fetch, generation, or shared upgrades."""
    source, target = Path(source_root).resolve(), Path(target_root).absolute()
    try:
        catalog = load_catalog(source)
        inputs = _inputs(target, catalog)
        # Bind the ownership read and existing adapters to the plan, not just its eventual writes.
        ownership_before = _read_current(target, OWNERSHIP_PATH)
        plan, preserved = _plan(source, target, catalog)
        if inputs != _inputs(target, catalog) or ownership_before != _read_current(target, OWNERSHIP_PATH):
            raise ProjectSyncError('project inputs changed while synchronization was planned; retry from current inputs')
        changed = _changed(plan)
        if not check_only and changed:
            def postcondition():
                if inputs != _inputs(target, catalog):
                    raise ProjectSyncError('project inputs changed during synchronization; retry from current inputs')
                if _changed(_plan(source, target, catalog)[0]):
                    raise ProjectSyncError('project synchronization did not converge')
            apply_plan(target, plan, postcondition=postcondition)
        return ProjectSyncResult('drift' if check_only and changed else 'clean', changed, preserved)
    except (OSError, ValueError, TransactionError) as error:
        raise ProjectSyncError(str(error)) from error
