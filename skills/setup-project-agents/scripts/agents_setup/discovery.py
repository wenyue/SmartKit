from __future__ import annotations

from pathlib import Path, PurePosixPath

from .external_contract import is_link_like as _is_link_like
from .models import Catalog, ProjectRuleSpec, ProjectSkillSpec
from .project import ProjectError, confined_target
from .rule_metadata import (
    RuleMetadataError, policy_metadata, read_policy, reject_conditional_rule,
    validate_rule_skill,
)


class DiscoveryError(ValueError):
    """Raised when project-owned Rule or Skill discovery is ambiguous or unsafe."""


def _managed_targets(catalog: Catalog, kind: str) -> set[PurePosixPath]:
    return {
        asset.target
        for asset in catalog.assets
        if asset.target is not None
        and (
            asset.kind == kind
            or (
                asset.kind == 'blueprint'
                and asset.target.parts[:2] == ('.agents', f'{kind}s')
            )
        )
    }


def _rule_metadata(text: str, relative: PurePosixPath) -> ProjectRuleSpec:
    try:
        strength = policy_metadata(text, relative.as_posix())
    except RuleMetadataError as error:
        raise DiscoveryError(str(error)) from error
    return ProjectRuleSpec(relative, strength)


def discover_project_rules(
    target_root: Path,
    catalog: Catalog,
    *,
    previous_managed: frozenset[PurePosixPath] = frozenset(),
) -> tuple[ProjectRuleSpec, ...]:
    root_relative = PurePosixPath('.agents/rules')
    try:
        root = confined_target(target_root, root_relative)
    except ProjectError as error:
        raise DiscoveryError(str(error)) from error
    if not root.exists():
        return ()
    if not root.is_dir():
        raise DiscoveryError('project Rule root is not a directory')
    managed = _managed_targets(catalog, 'rule')
    result: list[ProjectRuleSpec] = []
    for path in sorted(root.iterdir(), key=lambda item: item.name):
        if _is_link_like(path):
            raise DiscoveryError(f'project Rule path is a symlink: {path.name}')
        if not path.is_file() or path.suffix != '.md':
            continue
        relative = root_relative / path.name
        try:
            text = read_policy(path)
            reject_conditional_rule(text, relative.as_posix())
        except RuleMetadataError as error:
            raise DiscoveryError(str(error)) from error
        if relative in managed or relative in previous_managed:
            continue
        result.append(_rule_metadata(text, relative))
    return tuple(result)


def discover_project_skills(
    target_root: Path,
    catalog: Catalog,
    *,
    previous_managed: frozenset[PurePosixPath] = frozenset(),
) -> tuple[ProjectSkillSpec, ...]:
    root_relative = PurePosixPath('.agents/skills')
    try:
        root = confined_target(target_root, root_relative)
    except ProjectError as error:
        raise DiscoveryError(str(error)) from error
    if not root.exists():
        return ()
    if not root.is_dir():
        raise DiscoveryError('project Skill root is not a directory')
    managed_roots: set[PurePosixPath] = set()
    for asset in catalog.assets:
        if asset.target is None:
            continue
        if asset.kind == 'skill' and asset.target.parts[:2] == ('.agents', 'skills'):
            managed_roots.add(asset.target)
        elif (
            asset.kind == 'blueprint'
            and asset.target.parts[:2] == ('.agents', 'skills')
            and asset.target.name == 'SKILL.md'
        ):
            managed_roots.add(asset.target.parent)
    result: list[ProjectSkillSpec] = []
    for path in sorted(root.iterdir(), key=lambda item: item.name):
        if _is_link_like(path):
            raise DiscoveryError(f'project Skill path is a symlink: {path.name}')
        if not path.is_dir():
            continue
        relative = root_relative / path.name
        skill = path / 'SKILL.md'
        if _is_link_like(skill) or not skill.is_file():
            continue
        if path.name.startswith('rule-'):
            try:
                validate_rule_skill(read_policy(skill), path.name, str(skill))
            except RuleMetadataError as error:
                raise DiscoveryError(str(error)) from error
        if relative in managed_roots or relative in previous_managed:
            continue
        result.append(ProjectSkillSpec(path.name, relative))
    return tuple(result)


def discover_generated_skill_resources(
    target_root: Path,
    catalog: Catalog,
    *,
    previous_managed: frozenset[PurePosixPath] = frozenset(),
) -> tuple[PurePosixPath, ...]:
    """Discover project-owned files beside generated Skill entrypoints."""
    generated_entries = {
        asset.target
        for asset in catalog.assets
        if asset.kind == 'blueprint'
        and asset.target is not None
        and asset.target.parts[:2] == ('.agents', 'skills')
        and asset.target.name == 'SKILL.md'
    }
    result: set[PurePosixPath] = set()
    for entry in sorted(generated_entries, key=lambda item: item.as_posix()):
        root_relative = entry.parent
        try:
            root = confined_target(target_root, root_relative)
        except ProjectError as error:
            raise DiscoveryError(str(error)) from error
        if not root.exists():
            continue
        if not root.is_dir():
            raise DiscoveryError(
                f'generated Skill root is not a directory: {root_relative.as_posix()}'
            )
        for path in root.rglob('*'):
            if _is_link_like(path):
                raise DiscoveryError(
                    f'generated Skill resource is a symlink: '
                    f'{(root_relative / path.relative_to(root).as_posix()).as_posix()}'
                )
            if not path.is_file():
                continue
            relative = root_relative / path.relative_to(root).as_posix()
            if relative != entry and relative not in previous_managed:
                result.add(relative)
    return tuple(sorted(result, key=lambda item: item.as_posix()))
