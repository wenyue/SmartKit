from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .external_contract import is_link_like
from .markdown import live_headings, live_text


class RuleMetadataError(ValueError):
    """Raised when policy metadata is missing, ambiguous, or conditional."""


_FIELD = re.compile(r'^(?:\*\*)?(Strength|Scope|Loading):(?:\*\*)?[ \t]*(.*)$', re.IGNORECASE)
_YAML_FIELD = re.compile(r"(?P<key>'(?:[^']|'')*'|\"(?:[^\"\\]|\\.)*\"|[A-Za-z_][A-Za-z0-9_-]*)[ \t]*:[ \t]*(?P<value>.*)")
_BLOCK_STRING = re.compile(r'[|>](?:[1-9][+-]?|[+-][1-9]?)?')


def read_policy(path: Path) -> str:
    if is_link_like(path) or not path.is_file():
        raise RuleMetadataError(f'policy entry is missing or unsafe: {path}')
    try:
        return path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as error:
        raise RuleMetadataError(f'cannot read UTF-8 policy entry: {path}') from error


@dataclass(frozen=True)
class _YamlField:
    value: str
    continuation: tuple[str, ...]


def _quoted_text(raw: str, label: str) -> str:
    quoted = re.fullmatch(r"('(?:[^']|'')*'|\"(?:[^\"\\]|\\.)*\")(?:(?:[ \t]+#.*)|[ \t]*)", raw)
    if quoted is None:
        raise RuleMetadataError(f'unsupported quoted frontmatter scalar: {label}')
    scalar = quoted.group(1)
    if scalar.startswith("'"):
        return scalar[1:-1].replace("''", "'")
    try:
        return json.loads(scalar)
    except json.JSONDecodeError as error:
        raise RuleMetadataError(f'unsupported frontmatter escape: {label}') from error


def _without_comment(raw: str) -> str:
    return re.split(r'(?:^|[ \t]+)#', raw, maxsplit=1)[0].rstrip()


def _frontmatter(text: str, label: str) -> tuple[dict[str, _YamlField], str]:
    """Read root block-mapping fields with simple plain or quoted string keys.

    Nested metadata and block strings are values, not native controls. Merge/complex keys,
    multiline quoted/flow values and ambiguous plain continuations refuse explicitly.
    """
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        return {}, text
    try:
        end = lines.index('---', 1)
    except ValueError as error:
        raise RuleMetadataError(f'unterminated YAML frontmatter: {label}') from error
    fields: dict[str, _YamlField] = {}
    root_indent: int | None = None
    index = 1
    while index < end:
        line = lines[index]
        if not line.strip() or line.lstrip().startswith('#'):
            index += 1
            continue
        indent = len(line) - len(line.lstrip(' '))
        if root_indent is None:
            root_indent = indent
        match = _YAML_FIELD.fullmatch(line[indent:])
        if indent != root_indent or match is None:
            raise RuleMetadataError(f'unsupported or ambiguous YAML frontmatter field: {label}: {line.strip()}')
        raw_key, value = match.group('key', 'value')
        key = _quoted_text(raw_key, label) if raw_key.startswith(("'", '"')) else raw_key
        if key == '<<' or key in fields:
            raise RuleMetadataError(f'duplicate or unsupported YAML frontmatter key {key}: {label}')
        following = index + 1
        while following < end:
            child = lines[following]
            if child.strip() and not child.lstrip().startswith('#'):
                width = len(child) - len(child.lstrip(' '))
                if width <= indent:
                    break
            following += 1
        continuation = tuple(child[indent:] for child in lines[index + 1:following])
        plain = _without_comment(value)
        if value.startswith(("'", '"')):
            _quoted_text(value, label)
            if any(child.strip() and not child.lstrip().startswith('#') for child in continuation):
                raise RuleMetadataError(f'unsupported quoted scalar continuation: {label}: {key}')
        elif plain.startswith(('|', '>')):
            if _BLOCK_STRING.fullmatch(plain) is None:
                raise RuleMetadataError(f'unsupported block scalar header: {label}: {key}')
        elif plain:
            if plain.startswith(('[', '{')) and not plain.endswith((']', '}')):
                raise RuleMetadataError(f'unsupported multiline flow value: {label}: {key}')
            if any(re.search(r':(?:\s|$)', _without_comment(child.strip())) for child in continuation):
                raise RuleMetadataError(f'ambiguous plain scalar continuation: {label}: {key}')
        fields[key] = _YamlField(value, continuation)
        index = following
    return fields, '\n'.join(lines[end + 1:])


def reject_conditional_rule(text: str, label: str) -> None:
    """Refuse explicit legacy loading controls; source authoring owns migration."""
    fields, body = _frontmatter(text, label)
    declarations: list[tuple[str, str]] = []
    seen = set()
    for key, field in fields.items():
        control = key.casefold()
        if control not in {'loading', 'alwaysapply', 'globs', 'applyto'}:
            continue
        if control in seen:
            raise RuleMetadataError(f'ambiguous duplicate Rule loading control: {label}: {key}')
        seen.add(control)
        value = field.value
        if _BLOCK_STRING.fullmatch(_without_comment(value)) or any(
            line.strip() and not line.lstrip().startswith('#') for line in field.continuation
        ):
            value = _string_scalar((f'{key}: {value}', *field.continuation), 0,
                                        1 + len(field.continuation), f'{label}: Rule {key}')
        elif value.startswith(("'", '"')):
            value = _quoted_text(value, label)
        else:
            value = _without_comment(value)
        declarations.append((control, value))
    for line in live_text(body).splitlines():
        match = re.match(
            r'^ {0,3}(?:\*\*)?(loading|alwaysApply|globs|applyTo)[ \t]*:(?:\*\*)?\s*(.*?)\s*$',
            line, re.IGNORECASE,
        )
        if match is not None:
            key, value = match.groups()
            declarations.append((key.casefold(), value.strip('`\"\'').strip()))
    for key, value in declarations:
        unconditional = (
            key == 'loading' and value.lower() == 'always'
            or key == 'alwaysapply' and value.lower() == 'true'
            or key == 'applyto' and value == '**'
        )
        if not unconditional:
            raise RuleMetadataError(
                f'legacy conditional project Rule declaration in {label}: {key}: {value}; '
                'separately authorize source authoring into a rule-led Skill before setup'
            )


def policy_metadata(text: str, label: str) -> tuple[str, str]:
    """Read the first declared defaults, leaving later section overrides intact."""
    lines = live_text(text).splitlines()
    values: dict[str, str] = {}
    for index, line in enumerate(lines):
        match = _FIELD.fullmatch(line)
        if match is None or match.group(1).lower() == 'loading':
            continue
        key, value = match.group(1).lower(), match.group(2).strip()
        if key in values:
            continue
        if key == 'scope':
            continuation = []
            for following in lines[index + 1:]:
                if not following.strip() or following.lstrip().startswith('#') or _FIELD.match(following):
                    break
                continuation.append(following.strip())
            value = ' '.join([value, *continuation]).strip()
        values[key] = value.strip('`')
        if len(values) == 2:
            break
    if values.get('strength') not in {'Mandatory', 'Default', 'Advisory'} or not values.get('scope'):
        raise RuleMetadataError(f'policy requires valid Strength and nonempty Scope metadata: {label}')
    return values['strength'], values['scope']


def _string_scalar(lines: Sequence[str], index: int, end: int, label: str) -> str:
    """Read supported native YAML strings; refuse ambiguous or non-string values."""
    raw = lines[index].split(':', 1)[1].strip()
    invalid = f'field requires a nonempty string scalar: {label}'
    if raw.startswith(("'", '"')):
        return _quoted_text(raw, label)

    value = _without_comment(raw)
    if _BLOCK_STRING.fullmatch(value):
        indent_match = re.search(r'[1-9]', value)
        indent = int(indent_match.group()) if indent_match else None
        parts = []
        for following in lines[index + 1:end]:
            if not following.strip():
                parts.append('')
                continue
            width = len(following) - len(following.lstrip(' '))
            if width == 0:
                break
            if indent is None:
                indent = width
            if width < indent or following.startswith('\t'):
                raise RuleMetadataError(f'ambiguous block string indentation: {label}')
            parts.append(following[indent:])
        return '\n'.join(parts)

    if (
        not value
        or value[0] in ',[]{}#&*!|>\'"%@`'
        or re.match(r'^[-?:](?:\s|$)', value)
        or re.search(r':(?:\s|$)', value)
        or value.lower() in {'null', '~', 'true', 'false', 'yes', 'no', 'on', 'off', '.nan', '.inf', '+.inf', '-.inf'}
        or re.fullmatch(r'[+-]?(?:[0-9][0-9_]*(?::[0-9_]+)*(?:\.[0-9_]*)?|\.[0-9_]+)(?:[eE][+-]?[0-9_]+)?', value)
        or re.fullmatch(r'[+-]?0[xXoObB][0-9a-fA-F_]+', value)
        or re.match(r'^\d{4}-\d{1,2}-\d{1,2}(?:$|[Tt\s])', value)
    ):
        raise RuleMetadataError(invalid)
    for following in lines[index + 1:end]:
        if following.strip() and not following[0].isspace():
            break
        continuation = re.split(r'(?:^|[ \t]+)#', following.strip(), maxsplit=1)[0].rstrip()
        if re.search(r':(?:\s|$)', continuation):
            raise RuleMetadataError(f'ambiguous plain string: {label}')
        if continuation:
            value += ' ' + continuation
    return value


def validate_rule_skill(text: str, name: str, label: str) -> None:
    """Validate native rule-led entries without changing ordinary Skill discovery."""
    if not name.startswith('rule-'):
        return
    if not text.startswith('---\n') and not text.startswith('---\r\n'):
        raise RuleMetadataError(f'rule-led Skill requires YAML frontmatter: {label}')
    fields, body = _frontmatter(text, label)
    invocation = fields.get('disable-model-invocation')
    if invocation is not None and (
        _without_comment(invocation.value) not in {'false', 'False', 'FALSE'}
        or any(line.strip() and not line.lstrip().startswith('#') for line in invocation.continuation)
    ):
        raise RuleMetadataError(f'rule-led Skill must support model invocation: {label}')
    name_field = fields.get('name')
    if name_field is None:
        raise RuleMetadataError(f'rule-led Skill requires one nonempty name: {label}')
    raw_name = name_field.value
    if _BLOCK_STRING.fullmatch(_without_comment(raw_name)) or any(
        line.strip() and not line.lstrip().startswith('#') for line in name_field.continuation
    ):
        raise RuleMetadataError(f'rule-led Skill name requires a single-line plain or quoted scalar: {label}')
    native_name = (_quoted_text(raw_name, f'{label}: name')
                   if raw_name.startswith(("'", '"')) else _without_comment(raw_name))
    if native_name != name:
        raise RuleMetadataError(f'rule-led Skill frontmatter name must match folder {name}: {label}')
    description_field = fields.get('description')
    if description_field is None:
        raise RuleMetadataError(f'rule-led Skill requires one nonempty description: {label}')
    description = _string_scalar(
        (f'description: {description_field.value}', *description_field.continuation),
        0, 1 + len(description_field.continuation), f'{label}: description',
    )
    if not description.strip():
        raise RuleMetadataError(f'rule-led Skill requires a nonempty description: {label}')
    sections = [heading for heading in live_headings(body)
                if heading.level >= 2 and heading.title.casefold() != 'metadata']
    introduction = body[:sections[0].start] if sections else body
    policy_metadata(introduction, label)
