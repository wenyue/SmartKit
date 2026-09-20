from __future__ import annotations

import re
from pathlib import Path

from .external_contract import is_link_like
from .markdown import live_text


class RuleMetadataError(ValueError):
    """Raised when policy metadata is missing, ambiguous, or conditional."""


_FIELD = re.compile(r'^(?:\*\*)?(Strength|Scope|Loading):(?:\*\*)?[ \t]*(.*)$', re.IGNORECASE)
_NAME = re.compile(r"^name:[ \t]*(?:'([^']+)'|\"([^\"]+)\"|([a-z0-9][a-z0-9-]*))[ \t]*$")


def read_policy(path: Path) -> str:
    if is_link_like(path) or not path.is_file():
        raise RuleMetadataError(f'policy entry is missing or unsafe: {path}')
    try:
        return path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as error:
        raise RuleMetadataError(f'cannot read UTF-8 policy entry: {path}') from error


def reject_conditional_rule(text: str, label: str) -> None:
    """Refuse explicit legacy loading controls; source authoring owns migration."""
    for line in live_text(text).splitlines():
        match = re.match(
            r'^(?:\*\*)?(loading|alwaysApply|globs|applyTo):(?:\*\*)?\s*(.*?)\s*$',
            line, re.IGNORECASE,
        )
        if match is None:
            continue
        key, value = match.groups()
        value = value.strip('`\"\'').strip()
        unconditional = (
            key.lower() == 'loading' and value.lower() == 'always'
            or key.lower() == 'alwaysapply' and value.lower() == 'true'
            or key.lower() == 'applyto' and value == '**'
        )
        if not unconditional:
            raise RuleMetadataError(
                f'legacy conditional project Rule declaration in {label}: {line.strip()}; '
                'separately authorize source authoring into a rule-led Skill before setup'
            )


def policy_metadata(text: str, label: str) -> tuple[str, str]:
    lines = live_text(text).splitlines()
    values: dict[str, str] = {}
    for index, line in enumerate(lines):
        if re.match(r'^ {0,3}#{2,6}\s', line):
            break
        match = _FIELD.fullmatch(line)
        if match is None or match.group(1).lower() == 'loading':
            continue
        key, value = match.group(1).lower(), match.group(2).strip()
        if key in values:
            raise RuleMetadataError(f'duplicate {key} metadata: {label}')
        if key == 'scope':
            continuation = []
            for following in lines[index + 1:]:
                if not following.strip() or following.lstrip().startswith('#') or _FIELD.match(following):
                    break
                continuation.append(following.strip())
            value = ' '.join([value, *continuation]).strip()
        values[key] = value.strip('`')
    if values.get('strength') not in {'Mandatory', 'Default', 'Advisory'} or not values.get('scope'):
        raise RuleMetadataError(f'policy requires valid Strength and nonempty Scope metadata: {label}')
    return values['strength'], values['scope']


def validate_rule_skill(text: str, name: str, label: str) -> None:
    """Validate native rule-led entries without changing ordinary Skill discovery."""
    if not name.startswith('rule-'):
        return
    lines = text.splitlines()
    if not lines or lines[0] != '---' or '---' not in lines[1:]:
        raise RuleMetadataError(f'rule-led Skill requires YAML frontmatter: {label}')
    end = lines.index('---', 1)
    invocation = [line for line in lines[1:end] if line.startswith('disable-model-invocation:')]
    if len(invocation) > 1 or (invocation and re.fullmatch(
        r'disable-model-invocation:[ \t]*(?:false|False|FALSE)[ \t]*(?:#.*)?', invocation[0],
    ) is None):
        raise RuleMetadataError(f'rule-led Skill must support model invocation: {label}')
    names = [line for line in lines[1:end] if line.startswith('name:')]
    match = _NAME.fullmatch(names[0]) if len(names) == 1 else None
    if match is None or next(item for item in match.groups() if item is not None) != name:
        raise RuleMetadataError(f'rule-led Skill frontmatter name must match folder {name}: {label}')
    descriptions = [index for index in range(1, end) if lines[index].startswith('description:')]
    if len(descriptions) != 1:
        raise RuleMetadataError(f'rule-led Skill requires one nonempty description: {label}')
    index = descriptions[0]
    description = lines[index].split(':', 1)[1].strip()
    if description in {'|', '>', '|-', '>-', '|+', '>+'}:
        parts = []
        for following in lines[index + 1:end]:
            if following and not following[0].isspace():
                break
            parts.append(following.strip())
        description = ' '.join(parts).strip()
    if not description.strip('\"\'').strip() or description in {'null', '~', 'false', 'true', '[]', '{}'}:
        raise RuleMetadataError(f'rule-led Skill requires a nonempty description: {label}')
    policy_metadata('\n'.join(lines[end + 1:]), label)
