from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .external import ExternalSkillError, validated_snapshot_metadata
from .discovery import (
    DiscoveryError,
    discover_generated_skill_resources,
    discover_project_rules,
    discover_project_skills,
)
from .models import (
    Catalog,
    DesiredField,
    DesiredFile,
    OperatingSystem,
    ProjectConfig,
)
from .project import ProjectError, confined_target
from .project_rendering import (
    RenderError, _MCP_NATIVE, _safe_leaves, _load_structured, _copy_file,
    _render_project_agents, _remove_dotted_field, _render_project_mcp,
)
from .project_rules import (
    ENTRY_PATH,
    ProjectRuleSyncError,
    render_entry_agents,
    render_rule_rows,
)
from .generation import reconcile_contracts
from .ownership import (
    OWNERSHIP_PATH,
    OwnershipError,
    load_ownership,
    reconcile_ownership,
    verify_ownership,
)
from .structured import (
    dump_document as _dump_structured,
    format_for_path as _format_for,
)


@dataclass(frozen=True)
class RenderedState:
    files: tuple[DesiredFile, ...]
    fields: tuple[DesiredField, ...]
    delete_paths: tuple[PurePosixPath, ...] = ()
    replace_roots: tuple[PurePosixPath, ...] = ()
    preserved_paths: tuple[PurePosixPath, ...] = ()
    external_sources: tuple[Mapping[str, object], ...] = ()

    @property
    def files_by_path(self) -> Mapping[str, bytes]:
        return {item.path.as_posix(): item.content for item in self.files}

    @property
    def fields_by_key(self) -> Mapping[tuple[str, str], object]:
        return {(item.path.as_posix(), item.key): item.value for item in self.fields}


def _deep_merge(current: object, overlay: object) -> object:
    if isinstance(current, dict) and isinstance(overlay, dict):
        merged = dict(current)
        for key, value in overlay.items():
            merged[key] = _deep_merge(merged[key], value) if key in merged else value
        return merged
    return overlay


def _remove_template_fields(current: object, template: object) -> object:
    if not isinstance(current, dict) or not isinstance(template, dict):
        return current
    remaining = dict(current)
    for key, template_value in template.items():
        if key not in remaining:
            continue
        current_value = remaining[key]
        if isinstance(current_value, dict) and isinstance(template_value, dict):
            child = _remove_template_fields(current_value, template_value)
            if child:
                remaining[key] = child
            else:
                remaining.pop(key)
        else:
            remaining.pop(key)
    return remaining





_TRANSIENT_NAMES = frozenset({
    '__pycache__', '.DS_Store', 'Thumbs.db', '.pytest_cache', '.mypy_cache', '.ruff_cache'
})
def _is_transient(path: Path) -> bool:
    return (
        any(part in _TRANSIENT_NAMES for part in path.parts)
        or path.suffix in {'.pyc', '.pyo'}
    )


def _copy_asset(files: dict[PurePosixPath, bytes], source: Path, target: PurePosixPath) -> None:
    if source.is_file():
        _copy_file(files, target, source.read_bytes())
        return
    if source.is_dir():
        for child in sorted(
            path for path in source.rglob('*') if path.is_file() and not _is_transient(path)
        ):
            _copy_file(files, target / child.relative_to(source).as_posix(), child.read_bytes())
        return
    raise RenderError(f'catalog source is missing: {source}')


def _render_text(template: str, values: Mapping[str, object]) -> bytes:
    for key, value in values.items():
        rendered = str(value).lower() if isinstance(value, bool) else str(value)
        template = template.replace('{{' + key + '}}', rendered)
    return template.encode()










def render_desired_state(
    source_root: Path,
    target_root: Path,
    catalog: Catalog,
    config: ProjectConfig,
    generated_root: Path,
    external_root: Path | None = None,
    operating_system: OperatingSystem | None = None,
    generated_outputs: tuple[PurePosixPath, ...] | None = None,
) -> RenderedState:
    """Render only catalog-owned project assets without mutating the target."""
    try:
        previous_ownership = load_ownership(target_root, catalog=catalog)
        verify_ownership(target_root, previous_ownership)
    except OwnershipError as error:
        raise RenderError(str(error)) from error
    files: dict[PurePosixPath, bytes] = {}
    fields: list[DesiredField] = []
    native_documents: dict[PurePosixPath, dict[str, object]] = {}
    native_templates: dict[PurePosixPath, dict[str, object]] = {}
    replace_roots: set[PurePosixPath] = set()
    delete_paths: set[PurePosixPath] = set()
    assets_by_id = {asset.id: asset for asset in catalog.assets}
    for asset in catalog.assets:
        if asset.control_plane or asset.target is None:
            continue
        source = source_root / asset.source
        if asset.kind == 'skill' and source.is_dir():
            replace_roots.add(asset.target)
    previous_rule_paths = frozenset(
        asset.path
        for asset in (previous_ownership.assets if previous_ownership else ())
        if asset.role == 'rule' and asset.path.parts[:2] == ('.agents', 'rules')
    )
    previous_skill_roots = frozenset(
        asset.path if asset.kind == 'tree' else asset.path.parent
        for asset in (previous_ownership.assets if previous_ownership else ())
        if asset.role == 'skill' and asset.path.parts[:2] == ('.agents', 'skills')
    )
    recorded_outputs = {
        path for contract in (previous_ownership.contracts if previous_ownership else ())
        for path in contract.outputs
    }
    previous_rule_paths |= frozenset(
        path for path in recorded_outputs if path.parts[:2] == ('.agents', 'rules')
    )
    previous_skill_roots |= frozenset(
        contract.target.parent
        for contract in (previous_ownership.contracts if previous_ownership else ())
        if contract.target.parts[:2] == ('.agents', 'skills')
    )
    previous_owned_fields = frozenset(
        (asset.path, asset.key)
        for asset in (previous_ownership.assets if previous_ownership else ())
        if asset.kind == 'field' and asset.key is not None
    )
    sources: list[Mapping[str, object]] = []
    external_assets: dict[str, tuple[str, PurePosixPath]] = {}

    def native_document(path: PurePosixPath) -> dict[str, object]:
        if path not in native_documents:
            format_name = _format_for(path)
            assert format_name is not None
            try:
                current = confined_target(target_root, path)
            except ProjectError as error:
                raise RenderError(str(error)) from error
            native_documents[path] = _load_structured(current, format_name)
        return native_documents[path]

    try:
        project_rules = discover_project_rules(
            target_root, catalog, previous_managed=previous_rule_paths,
        )
        project_skills = discover_project_skills(
            target_root,
            catalog,
            previous_managed=previous_skill_roots
            | frozenset(
                PurePosixPath('.agents/skills') / item.name
                for item in config.external_skills
            ),
        )
        previous_generated_resources = frozenset(
            asset.path
            for asset in (previous_ownership.assets if previous_ownership else ())
            if asset.kind == 'file'
            and asset.role == 'skill'
            and asset.path.name != 'SKILL.md'
        )
        generated_skill_resources = discover_generated_skill_resources(
            target_root,
            catalog,
            previous_managed=previous_generated_resources,
        )
    except DiscoveryError as error:
        raise RenderError(str(error)) from error

    for asset in catalog.assets:
        if asset.control_plane or asset.target is None:
            continue
        asset_selected = (
            (asset.kind != 'rule' or asset.id in config.selected_rules)
            and (asset.kind != 'skill' or asset.id in config.selected_skills)
        )
        if not asset.harnesses or not asset_selected:
            if asset.kind == 'template' and _format_for(asset.target):
                format_name = _format_for(asset.target)
                assert format_name is not None
                template = _load_structured(source_root / asset.source, format_name)
                try:
                    target_path = confined_target(target_root, asset.target)
                except ProjectError as error:
                    raise RenderError(str(error)) from error
                existing = dict(native_document(asset.target))
                if existing:
                    remaining = _remove_template_fields(existing, template)
                    if remaining:
                        native_documents[asset.target] = remaining
                    else:
                        delete_paths.add(asset.target)
            continue
        if asset.kind in {'rule', 'skill', 'agent'}:
            _copy_asset(files, source_root / asset.source, asset.target)
            continue
        if asset.kind == 'template' and asset.target and _format_for(asset.target):
            format_name = _format_for(asset.target)
            assert format_name is not None
            template = _load_structured(source_root / asset.source, format_name)
            try:
                target_path = confined_target(target_root, asset.target)
            except ProjectError as error:
                raise RenderError(str(error)) from error
            existing = dict(native_document(asset.target))
            for key, _ in _safe_leaves(template):
                if (asset.target, key) in previous_owned_fields:
                    _remove_dotted_field(existing, key)
            native_documents[asset.target] = _deep_merge(template, existing)
            native_templates[asset.target] = template
            continue
        if asset.kind == 'template':
            content = (source_root / asset.source).read_bytes()
            if asset.id == 'entry-agents':
                content = _render_text(content.decode(), {
                    'project_rule_rows': render_rule_rows(
                        catalog, config, 'project', project_rules,
                    ),
                })
                try:
                    content = render_entry_agents(target_root, content)
                except ProjectRuleSyncError as error:
                    raise RenderError(str(error)) from error
            _copy_file(files, asset.target, content)
            continue
        if asset.kind == 'wrapper':
            template = (source_root / asset.source).read_text(encoding='utf-8')
            for rule_id in config.selected_rules:
                source = assets_by_id[rule_id]
                assert source.target is not None
                item = source.metadata
                cursor = item['cursor']
                github = item['github']
                if not isinstance(cursor, Mapping) or not isinstance(github, Mapping):
                    raise RenderError(f'rule metadata is invalid: {rule_id}')
                name = source.source.stem
                path = PurePosixPath(asset.target.as_posix().replace('{rule-name}', name))
                _copy_file(files, path, _render_text(template, {
                    'rule.apply_ref': source.target.as_posix(),
                    'rule.cursor_description': cursor['description'],
                    'rule.cursor_globs': json.dumps(cursor.get('globs', '**')),
                    'rule.cursor_always_apply': cursor['alwaysApply'],
                    'rule.github_apply_to': github['applyTo'],
                }))

    before_project_agents = set(files)
    project_agent_sources = _render_project_agents(files, target_root, config)
    project_files = set(files) - before_project_agents

    generated_targets = set(generated_outputs) if generated_outputs is not None else {
        asset.target
        for asset in catalog.assets
        if asset.kind == 'blueprint'
        and not asset.control_plane
        and asset.target is not None
    }
    written_generated_targets: set[PurePosixPath] = set()
    for path in sorted(
        (
            item
            for item in generated_root.rglob('*')
            if item.is_file()
            and (generated_outputs is not None or not _is_transient(item))
            and item.relative_to(generated_root).as_posix() != '.setup-generation.json'
        ),
        key=lambda item: item.as_posix(),
    ):
        relative = PurePosixPath(path.relative_to(generated_root).as_posix())
        if relative not in generated_targets:
            raise RenderError(f'undeclared generated path: {relative.as_posix()}')
        files[relative] = path.read_bytes()
        written_generated_targets.add(relative)

    contracts, retired_outputs, retained_outputs = reconcile_contracts(
        source_root, catalog, previous_ownership, tuple(written_generated_targets),
    )
    for output in retired_outputs:
        try:
            target = confined_target(target_root, output)
        except ProjectError as error:
            raise RenderError(str(error)) from error
        if target.exists() and not target.is_file():
            raise RenderError(f'contract output is not a regular file: {output.as_posix()}')
    delete_paths.update(retired_outputs)
    generated_skill_resources = tuple(
        path for path in generated_skill_resources
        if path not in retired_outputs and path not in written_generated_targets
    )

    if config.external_skills:
        if external_root is None or not external_root.is_dir() or external_root.is_symlink():
            raise RenderError('external Skill snapshot directory is missing or unsafe')
        expected_external = {item.name for item in config.external_skills}
        actual_external = {
            item.name for item in external_root.iterdir() if item.is_dir() and not item.is_symlink()
        }
        if actual_external != expected_external:
            raise RenderError('external Skill snapshot does not match project config')
        try:
            sources = list(validated_snapshot_metadata(config.external_sources, external_root))
        except ExternalSkillError as error:
            raise RenderError(str(error)) from error
        for source in sources:
            for item in source['skills']:
                assert isinstance(item, Mapping)
                name = str(item['id']).rsplit('/', 1)[-1]
                external_assets[name] = (
                    str(source['id']), PurePosixPath(str(item['path'])),
                )
        for skill in config.external_skills:
            source = external_root / skill.name
            if not (source / 'SKILL.md').is_file():
                raise RenderError(f'external Skill is missing SKILL.md: {skill.name}')
            _copy_asset(files, source, PurePosixPath('.agents/skills') / skill.name)
            replace_roots.add(PurePosixPath('.agents/skills') / skill.name)
    _render_project_mcp(
        target_root,
        config,
        native_documents,
        native_templates,
        delete_paths,
        previous_owned_fields,
        operating_system,
    )

    for path, document in native_documents.items():
        if not document:
            delete_paths.add(path)
            continue
        format_name = _format_for(path)
        assert format_name is not None
        _copy_file(files, path, _dump_structured(document, format_name))
        for key, value in _safe_leaves(native_templates.get(path, {})):
            fields.append(DesiredField(path, key, value, format_name))
    desired_files = tuple(DesiredFile(path, content) for path, content in sorted(files.items(), key=lambda item: item[0].as_posix()))
    desired_fields = tuple(sorted(fields, key=lambda item: (item.path.as_posix(), item.key)))
    try:
        ownership = reconcile_ownership(
            target_root,
            desired_files,
            desired_fields,
            tuple(replace_roots),
            sources=sources,
            external_sources=external_assets,
            structured_paths=tuple(native_documents),
        unmanaged_paths=(ENTRY_PATH, *generated_targets),
            previous=previous_ownership,
            contracts=contracts,
            project_files=tuple(project_files),
            project_fields=tuple(
                (field.path, field.key) for field in desired_fields
                if any(
                    field.path == _MCP_NATIVE[harness][0]
                    and field.key.startswith(f'{_MCP_NATIVE[harness][1]}.{server.id}.')
                    for server in config.mcp_servers for harness in server.harnesses
                )
            ),
        )
    except OwnershipError as error:
        raise RenderError(str(error)) from error
    files = {item.path: item.content for item in ownership.files}
    for path, key in ownership.remove_fields:
        document = native_documents.get(path)
        if document is None:
            document = native_document(path)
        _remove_dotted_field(document, key)
        if document:
            format_name = _format_for(path)
            assert format_name is not None
            files[path] = _dump_structured(document, format_name)
            delete_paths.discard(path)
        else:
            files.pop(path, None)
            delete_paths.add(path)
    files[OWNERSHIP_PATH] = ownership.manifest
    desired_files = tuple(DesiredFile(path, content) for path, content in sorted(files.items()))
    delete_paths.update(ownership.delete_paths)
    delete_paths.difference_update(files)
    return RenderedState(
        desired_files,
        desired_fields,
        tuple(sorted(delete_paths, key=lambda item: item.as_posix())),
        tuple(sorted(replace_roots, key=lambda item: item.as_posix())),
        tuple(
            sorted(
                {
                    *(item.path for item in project_rules),
                    *(item.path / 'SKILL.md' for item in project_skills),
                    *project_agent_sources,
                    *generated_skill_resources,
                    *retained_outputs,
                },
                key=lambda item: item.as_posix(),
            )
        ),
        tuple(dict(item) for item in sources),
    )
