from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .catalog import ContractError, load_catalog
from .discovery import DiscoveryError, discover_project_rules
from .external_contract import is_link_like as _is_link_like
from .markdown import live_headings
from .models import (
    Catalog,
    ChangeKind,
    DesiredFile,
    Plan,
    ProjectConfig,
    ProjectRuleSpec,
)
from .ownership import OwnershipError, load_ownership
from .planner import PlanningError, build_plan
from .project import ProjectError, confined_target
from .transaction import TransactionError, apply_plan


ENTRY_PATH = PurePosixPath('AGENTS.md')
PROJECT_RULES_TITLE = 'Project rules'
_RULE_PATH = re.compile(r'\.agents/rules/(\d{2}-[a-z0-9][a-z0-9-]*\.md)')
_TABLE_ROW = re.compile(r'^\|.*\|\s*$')


class ProjectRuleSyncError(ValueError):
    """Raised when the narrow project Rule index cannot converge safely."""


@dataclass(frozen=True)
class ProjectRuleSyncResult:
    check: str
    changed_paths: tuple[str, ...]


def _rule_row(
    description: str,
    rule_path: PurePosixPath | None,
    strength: str,
) -> str:
    path = '' if rule_path is None else rule_path.as_posix()
    description = description.replace('|', '\\|')
    return f'| {description} | `{path}` | {strength} |'


def render_rule_tables(source_root: Path, required: list[str], on_demand: list[str]) -> str:
    """Render only non-empty tables, including their loading instructions."""
    blocks = []
    for name, rows in (('required-rules', required), ('on-demand-rules', on_demand)):
        if rows:
            template = (
                source_root / f'setup-assets/templates/entry-files/{name}.md'
            ).read_text(encoding='utf-8')
            blocks.append(template.replace('{{rule_rows}}', '\n'.join(_sort_rows(rows))).strip())
    return '\n\n'.join(blocks)


def required_rule_paths(target_root: Path) -> frozenset[PurePosixPath]:
    """Read the project's explicit choices for additional always-read Rules."""
    return frozenset(
        path for row in _index_rows(_read_entry(target_root))
        if len(row) == 2 and (path := _row_path('| ' + ' | '.join(row) + ' |')) is not None
    )


def render_project_rule_tables(
    source_root: Path,
    target_root: Path,
    catalog: Catalog,
    config: ProjectConfig,
    section: str,
    project_rules: tuple[ProjectRuleSpec, ...],
) -> str:
    """Combine catalog loading policy with the project's explicit required rows."""
    required, on_demand = [], []
    required_paths = required_rule_paths(target_root)
    for asset in catalog.assets:
        metadata = asset.metadata
        if (
            asset.kind in {'rule', 'blueprint'}
            and metadata.get('section') == section
            and (asset.kind != 'rule' or asset.id in config.selected_rules)
        ):
            if metadata['loading'] == 'always':
                required.append(f'| `{asset.target}` | {metadata["strength"]} |')
            else:
                on_demand.append(_rule_row(
                    str(metadata['description']), asset.target, str(metadata['strength']),
                ))
    for rule in project_rules:
        if rule.path in required_paths:
            required.append(f'| `{rule.path}` | {rule.strength} |')
        elif rule.section == section:
            on_demand.append(_rule_row(rule.description, rule.path, rule.strength))
    return render_rule_tables(source_root, required, on_demand)


def project_rules_section_bounds(content: str) -> tuple[int, int] | None:
    headings = live_headings(content)
    matches = [
        index
        for index, item in enumerate(headings)
        if item.level == 2 and item.title == PROJECT_RULES_TITLE
    ]
    if len(matches) > 1:
        raise ProjectRuleSyncError(
            'project AGENTS.md has duplicate ## Project rules sections'
        )
    if not matches:
        return None
    match = matches[0]
    start = headings[match].start
    end = next(
        (item.start for item in headings[match + 1:] if item.level <= 2),
        len(content),
    )
    return start, end


def _read_entry(target_root: Path) -> bytes | None:
    try:
        entry = confined_target(target_root, ENTRY_PATH)
    except ProjectError as error:
        raise ProjectRuleSyncError(str(error)) from error
    if not entry.exists():
        return None
    if _is_link_like(entry) or not entry.is_file():
        raise ProjectRuleSyncError('project AGENTS.md is unsafe')
    try:
        content = entry.read_bytes()
        content.decode('utf-8')
    except (OSError, UnicodeDecodeError) as error:
        raise ProjectRuleSyncError(
            'project AGENTS.md is not readable UTF-8'
        ) from error
    return content


def _replace_project_rules_section(current: bytes | None, block: bytes) -> bytes:
    try:
        rendered = block.decode('utf-8')
    except UnicodeDecodeError as error:
        raise ProjectRuleSyncError(
            'entry AGENTS template is not valid UTF-8'
        ) from error
    rendered_bounds = project_rules_section_bounds(rendered)
    if (
        rendered_bounds is None
        or rendered[:rendered_bounds[0]].strip()
        or rendered[rendered_bounds[1]:].strip()
    ):
        raise ProjectRuleSyncError(
            'entry AGENTS template must contain only one Project rules section'
        )
    body = rendered.rstrip('\r\n')
    if current is None:
        return body.encode() + b'\n'
    content = current.decode('utf-8')
    bounds = project_rules_section_bounds(content)
    if bounds is None:
        if not content or content.endswith(('\n\n', '\r\n\r\n')):
            separator = ''
        elif content.endswith(('\n', '\r')):
            separator = '\n'
        else:
            separator = '\n\n'
        return (content + separator + body + '\n').encode()
    start, end = bounds
    suffix = content[end:]
    separator = '\n\n' if suffix else '\n'
    return (content[:start] + body + separator + suffix).encode()


def render_entry_agents(target_root: Path, block: bytes) -> bytes:
    """Replace only the owned Project rules section in a safe AGENTS.md."""
    return _replace_project_rules_section(_read_entry(target_root), block)


def _managed_rule_paths(
    target_root: Path,
    catalog: Catalog,
) -> frozenset[PurePosixPath]:
    paths = {
        asset.target
        for asset in catalog.assets
        if asset.target is not None
        and asset.target.parts[:2] == ('.agents', 'rules')
    }
    ownership = load_ownership(target_root, catalog=catalog)
    if ownership is not None:
        paths.update(
            asset.path
            for asset in ownership.assets
            if asset.role == 'rule'
        )
        paths.update(
            output
            for contract in ownership.contracts
            for output in contract.outputs
            if output.parts[:2] == ('.agents', 'rules')
        )
    return frozenset(paths)


def _row_path(row: str) -> PurePosixPath | None:
    match = _RULE_PATH.search(row)
    if match is None:
        return None
    return PurePosixPath('.agents/rules') / match.group(1)


def _index_rows(current: bytes | None) -> list[list[str]]:
    if current is None:
        return []
    content = current.decode('utf-8')
    bounds = project_rules_section_bounds(content)
    if bounds is None:
        return []
    rows = []
    for line in content[bounds[0]:bounds[1]].splitlines():
        if not _TABLE_ROW.fullmatch(line):
            continue
        cells = [cell.strip() for cell in re.split(r'(?<!\\)\|', line)[1:-1]]
        if cells in (['Rule', 'Strength'], ['Description', 'Rule', 'Strength']):
            continue
        if len(cells) == 3 and cells[1:] == ['Rule', 'Strength']:
            continue
        if set(line.replace('|', '').strip()) <= {'-', ':', ' '}:
            continue
        if len(cells) in {2, 3}:
            rows.append(cells)
    return rows


def _preserved_rows(
    current: bytes | None,
    managed: frozenset[PurePosixPath],
    catalog: Catalog,
) -> tuple[list[str], list[str]]:
    required, on_demand = [], []
    declared = {
        asset.target: asset.metadata
        for asset in catalog.assets
        if asset.kind in {'rule', 'blueprint'} and 'loading' in asset.metadata
    }
    for cells in _index_rows(current):
        row = '| ' + ' | '.join(cells) + ' |'
        path = _row_path(row)
        if path is not None and path not in managed:
            continue
        metadata = declared.get(path)
        if metadata is not None and metadata['loading'] == 'always':
            required.append('| ' + ' | '.join(cells[-2:]) + ' |')
        elif len(cells) == 2:
            if metadata is not None:
                on_demand.append(_rule_row(
                    str(metadata['description']), path, cells[-1],
                ))
            else:
                required.append(row)
        else:
            on_demand.append(row)
    return required, on_demand


def _sort_rows(rows: list[str]) -> list[str]:
    def key(row: str) -> tuple[bool, str]:
        path = _row_path(row)
        return path is None, row if path is None else path.as_posix()

    return sorted(rows, key=key)


def _changed_paths(plan: Plan) -> tuple[str, ...]:
    return tuple(
        change.path.as_posix()
        for change in plan.changes
        if change.kind is not ChangeKind.UNCHANGED
    )


def _plan_project_rule_sync(source_root: Path, target_root: Path) -> Plan:
    source = Path(source_root).resolve()
    target = Path(target_root).absolute()
    catalog = load_catalog(source)
    managed = _managed_rule_paths(target, catalog)
    project_rules = discover_project_rules(
        target,
        catalog,
        previous_managed=managed,
    )
    current = _read_entry(target)
    required, on_demand = _preserved_rows(current, managed, catalog)
    required_paths = required_rule_paths(target)
    for rule in project_rules:
        if rule.path in required_paths:
            required.append(f'| `{rule.path}` | {rule.strength} |')
        elif rule.section == 'project':
            on_demand.append(_rule_row(rule.description, rule.path, rule.strength))
    template = (
        source / 'setup-assets/templates/entry-files/AGENTS.md'
    ).read_text(encoding='utf-8')
    tables = render_rule_tables(source, required, on_demand)
    block = template.replace('{{project_rule_tables}}', tables).encode()
    desired = _replace_project_rules_section(current, block)
    plan = build_plan(target, (DesiredFile(ENTRY_PATH, desired),))
    change = plan.changes[0]
    observed = None if change.expected is None else change.expected.content
    if observed != current:
        raise PlanningError('project AGENTS.md changed while its Rule index was planned')
    return plan


def synchronize_project_rules(
    source_root: Path,
    target_root: Path,
    *,
    check_only: bool,
) -> ProjectRuleSyncResult:
    """Check or atomically converge only a repository's project Rule index."""
    source = Path(source_root).resolve()
    target = Path(target_root).absolute()
    try:
        plan = _plan_project_rule_sync(source, target)
        changed_paths = _changed_paths(plan)
        if not check_only and changed_paths:
            def postcondition() -> None:
                remaining = _changed_paths(_plan_project_rule_sync(source, target))
                if remaining:
                    raise ProjectRuleSyncError(
                        'project Rule index did not converge: ' + ', '.join(remaining)
                    )

            apply_plan(target, plan, postcondition=postcondition)
        return ProjectRuleSyncResult(
            'drift' if check_only and changed_paths else 'clean',
            changed_paths,
        )
    except (
        ContractError,
        DiscoveryError,
        OSError,
        OwnershipError,
        PlanningError,
        ProjectError,
        TransactionError,
    ) as error:
        raise ProjectRuleSyncError(str(error)) from error
