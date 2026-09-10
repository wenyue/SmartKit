from __future__ import annotations

import json
from pathlib import Path, PurePosixPath


class RuleConfigError(RuntimeError):
    """Raised when the Plugin Rule registry violates its delivery contract."""


def load_registry(root: Path) -> list[dict[str, str]]:
    try:
        document = json.loads((root / 'rules/registry.json').read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuleConfigError(f'cannot load rules/registry.json: {error}') from error
    if not isinstance(document, dict) or set(document) != {'rules'}:
        raise RuleConfigError('Rule registry requires exactly a rules field')
    rules = document['rules']
    if not isinstance(rules, list) or not rules:
        raise RuleConfigError('Rule registry requires a non-empty rules array')
    ids: set[str] = set()
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict) or set(rule) != {'id', 'source', 'strength', 'description'}:
            raise RuleConfigError(f'invalid Rule at index {index}')
        if not all(
            isinstance(value, str) and value.strip() and '\n' not in value and '\r' not in value
            for value in rule.values()
        ):
            raise RuleConfigError(f'invalid Rule field at index {index}')
        rule_id = rule['id']
        if not rule_id.startswith('smartkit/') or rule_id in ids:
            raise RuleConfigError(f'duplicate or invalid Rule id at index {index}')
        ids.add(rule_id)
        if rule['strength'] not in {'Mandatory', 'Default', 'Advisory'}:
            raise RuleConfigError(f'invalid strength for {rule_id}')
        source = rule['source']
        relative = PurePosixPath(source)
        if (
            relative.name != source or relative.suffix != '.md'
            or '\\' in source or ':' in source
        ):
            raise RuleConfigError(f'invalid source for {rule_id}: expected a Markdown filename')
        if not (root / 'rules' / source).is_file():
            raise RuleConfigError(f'missing source for {rule_id}')
    first = rules[0]
    if (
        first['id'] != 'smartkit/core-instruction-governance'
        or first['strength'] != 'Mandatory'
    ):
        raise RuleConfigError(
            'the first Rule must be mandatory core-instruction-governance'
        )
    return rules
