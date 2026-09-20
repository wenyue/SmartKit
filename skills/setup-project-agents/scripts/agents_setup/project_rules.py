from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .catalog import ContractError, load_catalog
from .discovery import DiscoveryError, discover_project_rules
from .external_contract import is_link_like as _is_link_like
from .markdown import live_headings, live_text
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
from .rule_metadata import RuleMetadataError, policy_metadata, read_policy


ENTRY_PATH = PurePosixPath('AGENTS.md')
PROJECT_RULES_TITLE = 'Project rules'
_RULE_PATH = re.compile(r'\.agents/rules/([^`|/\r\n]+\.md)(?=[`)\s]|$)')


class ProjectRuleSyncError(ValueError):
    """Raised when the narrow project Rule index cannot converge safely."""


@dataclass(frozen=True)
class ProjectRuleSyncResult:
    check: str
    changed_paths: tuple[str, ...]


def render_rule_tables(source_root: Path, required: list[str]) -> str:
    """Render the single unconditional Rule table when it has entries."""
    if not required:
        return ''
    template = (
        source_root / 'setup-assets/templates/entry-files/required-rules.md'
    ).read_text(encoding='utf-8')
    return template.replace('{{rule_rows}}', '\n'.join(_sort_rows(required))).strip()


def validate_project_rule_index(target_root: Path) -> None:
    """Refuse legacy conditional or ambiguous declarations before target effects."""
    _index_rows(_read_entry(target_root))


def render_project_rule_tables(
    source_root: Path,
    target_root: Path,
    catalog: Catalog,
    config: ProjectConfig,
    project_rules: tuple[ProjectRuleSpec, ...],
) -> str:
    validate_project_rule_index(target_root)
    required = []
    for asset in catalog.assets:
        if (
            asset.kind in {'rule', 'blueprint'}
            and asset.target is not None
            and asset.target.parts[:2] == ('.agents', 'rules')
            and (asset.kind != 'rule' or asset.id in config.selected_rules)
        ):
            required.append(f'| `{asset.target}` | {asset.metadata["strength"]} |')
    required.extend(f'| `{rule.path}` | {rule.strength} |' for rule in project_rules)
    return render_rule_tables(source_root, required)


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


def _table_cells(line: str) -> list[str] | None:
    """Split unescaped Markdown pipes, with either outer delimiter optional."""
    cells = []
    start = 0
    backslashes = 0
    for index, character in enumerate(line):
        if character == '|' and backslashes % 2 == 0:
            cells.append(line[start:index].strip())
            start = index + 1
        backslashes = backslashes + 1 if character == '\\' else 0
    if not cells:
        return None
    cells.append(line[start:].strip())
    if not cells[0]:
        cells.pop(0)
    if cells and not cells[-1]:
        cells.pop()
    return cells


def _index_rows(current: bytes | None) -> list[list[str]]:
    if current is None:
        return []
    content = current.decode('utf-8')
    bounds = project_rules_section_bounds(content)
    if bounds is None:
        return []
    section = live_text(content[bounds[0]:bounds[1]])
    rows = []
    in_table = False
    table_columns: int | None = None
    for line in section.splitlines():
        cells = _table_cells(line)
        if cells is None or line.startswith(('    ', '\t')):
            in_table = False
            table_columns = None
            continue
        header = len(cells) >= 2 and cells[-2:] == ['Rule', 'Strength']
        separator = bool(cells) and all(re.fullmatch(r':?-+:?', cell) for cell in cells)
        if not (in_table or header or separator or line.lstrip().startswith('|') or '.agents/rules/' in line):
            continue
        in_table = True
        if header and len(cells) == 2:
            table_columns = 2
            continue
        if (header and len(cells) == 3) or (not separator and len(cells) == 3):
            raise ProjectRuleSyncError(
                f'legacy conditional project Rule declaration in AGENTS.md: {line.strip()}; '
                'separately authorize source authoring into a rule-led Skill before setup'
            )
        if separator:
            if table_columns is not None and len(cells) != table_columns:
                raise ProjectRuleSyncError(f'ambiguous Rule table columns in AGENTS.md: {line.strip()}')
            table_columns = len(cells)
            continue
        if len(cells) != 2 or (table_columns is not None and len(cells) != table_columns):
            raise ProjectRuleSyncError(f'ambiguous Rule table in AGENTS.md: {line.strip()}')
        if '.agents/rules/' in line and _row_path(line) is None:
            raise ProjectRuleSyncError(f'ambiguous Rule path in AGENTS.md: {line.strip()}')
        rows.append(cells)
    if rows and any(re.search(r'\b(?:on[- ]demand|conditional)\b', heading.title, re.IGNORECASE)
                    for heading in live_headings(section)):
        raise ProjectRuleSyncError(
            'legacy conditional project Rule declaration in AGENTS.md; '
            'separately authorize source authoring into a rule-led Skill before setup'
        )
    return rows


def _preserved_rows(
    current: bytes | None,
    managed: frozenset[PurePosixPath],
) -> list[str]:
    required = []
    for cells in _index_rows(current):
        row = '| ' + ' | '.join(cells) + ' |'
        path = _row_path(row)
        if path is None or path in managed:
            required.append(row)
    return required


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
    required = _preserved_rows(current, managed)
    indexed = {_row_path(row) for row in required}
    metadata = {asset.target: asset.metadata for asset in catalog.assets}
    for relative in sorted(managed, key=lambda path: path.as_posix()):
        if relative in indexed or relative.parent != PurePosixPath('.agents/rules') or relative.suffix != '.md':
            continue
        path = confined_target(target, relative)
        if not path.is_file():
            continue
        strength = metadata.get(relative, {}).get('strength')
        if strength is None:
            strength, _ = policy_metadata(read_policy(path), relative.as_posix())
        required.append(f'| `{relative}` | {strength} |')
    required.extend(f'| `{rule.path}` | {rule.strength} |' for rule in project_rules)
    template = (
        source / 'setup-assets/templates/entry-files/AGENTS.md'
    ).read_text(encoding='utf-8')
    tables = render_rule_tables(source, required)
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
        RuleMetadataError,
        TransactionError,
    ) as error:
        raise ProjectRuleSyncError(str(error)) from error
