from __future__ import annotations

import re

from project_state.skill_metadata import (
    RuleMetadataError,
    _BLOCK_STRING,
    _quoted_text,
    _without_comment,
    _frontmatter,
    _string_scalar,
)

from .markdown import live_text


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
