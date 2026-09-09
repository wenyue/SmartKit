from __future__ import annotations

import re
from dataclasses import dataclass


_HEADING = re.compile(r'^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*$')
_FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})')


@dataclass(frozen=True)
class MarkdownHeading:
    start: int
    body_start: int
    level: int
    title: str


def live_headings(content: str) -> tuple[MarkdownHeading, ...]:
    """Locate Markdown headings while ignoring headings inside fenced code."""
    headings = []
    fence_character: str | None = None
    fence_length = 0
    offset = 0
    for raw_line in content.splitlines(keepends=True):
        line = raw_line.rstrip('\r\n')
        fence = _FENCE.match(line)
        if fence is not None:
            marker = fence.group(1)
            remainder = line[fence.end():]
            if fence_character is None:
                if marker[0] != '`' or '`' not in remainder:
                    fence_character = marker[0]
                    fence_length = len(marker)
            elif (
                marker[0] == fence_character
                and len(marker) >= fence_length
                and not remainder.strip()
            ):
                fence_character = None
                fence_length = 0
        elif fence_character is None:
            heading = _HEADING.match(line)
            if heading is not None:
                title = re.sub(r'[ \t]+#+[ \t]*$', '', heading.group(2)).strip()
                headings.append(MarkdownHeading(
                    start=offset,
                    body_start=offset + len(raw_line),
                    level=len(heading.group(1)),
                    title=title,
                ))
        offset += len(raw_line)
    return tuple(headings)
