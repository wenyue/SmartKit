"""Parse native configuration for Hooks and configuration maintenance."""
from __future__ import annotations

import json

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.11+ provides the standard library module.
    from ._vendor import tomli as tomllib


class StructuredConfigError(ValueError):
    """Raised when a structured native configuration cannot be parsed or rendered."""


def parse_jsonc(value: str) -> object:
    result: list[str] = []
    quoted = False
    escaped = False
    index = 0
    while index < len(value):
        char = value[index]
        next_char = value[index + 1] if index + 1 < len(value) else ''
        if quoted:
            result.append(char)
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
            index += 1
        elif char == '"':
            quoted = True
            result.append(char)
            index += 1
        elif char == '/' and next_char == '/':
            index = value.find('\n', index)
            if index < 0:
                break
        elif char == '/' and next_char == '*':
            end = value.find('*/', index + 2)
            if end < 0:
                raise StructuredConfigError('unterminated JSONC comment')
            index = end + 2
        else:
            result.append(char)
            index += 1
    without_comments = ''.join(result)
    clean: list[str] = []
    quoted = False
    escaped = False
    index = 0
    while index < len(without_comments):
        char = without_comments[index]
        if quoted:
            clean.append(char)
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
            index += 1
            continue
        if char == '"':
            quoted = True
            clean.append(char)
            index += 1
            continue
        if char == ',':
            following = index + 1
            while following < len(without_comments) and without_comments[following].isspace():
                following += 1
            if following < len(without_comments) and without_comments[following] in '}]':
                index += 1
                continue
        clean.append(char)
        index += 1
    without_trailing_commas = ''.join(clean)
    return json.loads(without_trailing_commas)


def parse_document(content: bytes | str, format_name: str) -> dict[str, object]:
    text = content.decode() if isinstance(content, bytes) else content
    try:
        value = tomllib.loads(text) if format_name == 'toml' else parse_jsonc(text)
    except (ValueError, json.JSONDecodeError) as error:
        raise StructuredConfigError(f'invalid {format_name} configuration') from error
    if not isinstance(value, dict):
        raise StructuredConfigError(f'{format_name} configuration must be an object')
    return value
