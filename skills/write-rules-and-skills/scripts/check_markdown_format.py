#!/usr/bin/env python
"""Read-only check for soft-wrapped Markdown prose; see --help for its bounds."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import List, Optional, Sequence, Tuple


LIST = re.compile(r"^( *)([-+*]|\d{1,9}[.)])([ \t]+)(.*)$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}#{1,6}(?:\s|$)")
RULE = re.compile(r"^ {0,3}(?:(?:\*\s*){3,}|(?:-\s*){3,}|(?:_\s*){3,})$")
SETEXT = re.compile(r"^ {0,3}(?:=+|-+)\s*$")
DEFINITION = re.compile(r"^ {0,3}\[[^\]]+\]:\s*")
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?\s*$")
HTML_BLOCK = re.compile(
    r"^ {0,3}</?(?:address|article|aside|base|blockquote|body|caption|center|col|"
    r"colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|"
    r"form|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|"
    r"nav|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|"
    r"th|thead|title|tr|track|ul)(?:\s|/?>|$)", re.IGNORECASE
)
HTML_TAG = re.compile(r"^ {0,3}</?[A-Za-z][\w-]*(?:\s+[^<>]*)?\s*/?>\s*$")


def unquote(line: str, *, limit: Optional[int] = None) -> Tuple[str, int]:
    """Retain indentation while removing explicit quote containers."""
    depth = 0
    while limit is None or depth < limit:
        match = re.match(r"^( *)> ?(.*)$", line)
        if match is None:
            return line, depth
        line = match[1] + match[2]
        depth += 1
    return line, depth


def hard_break(line: str) -> bool:
    if line.endswith("  "):
        return True
    slashes = len(line) - len(line.rstrip("\\"))
    return slashes % 2 == 1


def wrapped_lines(text: str) -> List[Tuple[int, int]]:
    """Return (continuation line, paragraph start) pairs for supported prose."""
    originals = text.splitlines()
    lines = [line.expandtabs(4) for line in originals]
    violations: List[Tuple[int, int]] = []
    paragraph: Optional[Tuple[int, int]] = None
    list_indents: List[int] = []
    quote_depth = 0
    fence: Optional[Tuple[str, int, int, int]] = None
    html_end: Optional[str] = None
    html_until_blank = False
    definition_indent: Optional[int] = None
    definition_title_pending = False
    definition_title_end: Optional[str] = None
    frontmatter = bool(lines and lines[0].lstrip("\ufeff") == "---")
    table = False
    previous_hard = False

    for index, original in enumerate(lines):
        number = index + 1
        if frontmatter:
            if index and original.strip() in ("---", "..."):
                frontmatter = False
            continue
        if fence is not None:
            character, width, fence_depth, margin = fence
            code, depth = unquote(original, limit=fence_depth)
            # Strip only the fence's existing containers: markers in code are literal.
            if depth == fence_depth and (not code.strip() or code.startswith(" " * margin)):
                code = code[margin:]
                if re.fullmatch(r" {0,3}" + re.escape(character) + "{" + str(width) + r",}\s*", code):
                    fence = None
                continue
            fence = None
        line, depth = unquote(original)
        marker = LIST.match(line)
        new_item = marker is not None and not RULE.match(line)
        if (new_item and paragraph is not None and marker[2][0].isdigit()
                and marker[2][:-1] != "1"
                and (not list_indents or len(marker[1]) >= list_indents[-1])):
            new_item = False
        if new_item:
            indent = len(marker[1])
            while list_indents and indent < list_indents[-1]:
                list_indents.pop()
            list_indents.append(indent + len(marker[2]) + len(marker[3]))
            line, extra_depth = unquote(marker[4])
            depth += extra_depth
        else:
            indent = len(line) - len(line.lstrip(" "))
            if line.strip():
                while list_indents and indent < list_indents[-1]:
                    list_indents.pop()
            if list_indents:
                line = line[list_indents[-1]:]
        # Unprefixed text may lazily continue a quote paragraph.
        if (depth == 0 and quote_depth and paragraph is not None and line.strip()
                and not new_item and not HEADING.match(line) and not RULE.match(line)
                and not SETEXT.match(line) and not FENCE.match(line)
                and not HTML_BLOCK.match(line)):
            depth = quote_depth
        if depth != quote_depth:
            paragraph = None
            quote_depth = depth
        if html_end is not None:
            if re.search(html_end, line, re.IGNORECASE):
                html_end = None
            continue
        if definition_title_end is not None:
            if line.rstrip().endswith(definition_title_end):
                definition_title_end = None
            continue
        if not line.strip():
            paragraph = None
            definition_indent = None
            definition_title_pending = False
            html_until_blank = False
            table = False
            continue
        if html_until_blank:
            continue
        if definition_indent is not None:
            title = re.match(r"^\s*([\"'(])(.*)$", line) if definition_title_pending else None
            if title is not None:
                closing = ")" if title[1] == "(" else title[1]
                if not title[2].rstrip().endswith(closing):
                    definition_title_end = closing
                definition_title_pending = False
                continue
            if len(line) - len(line.lstrip(" ")) > definition_indent:
                continue
            definition_indent = None
            definition_title_pending = False
        opening = FENCE.match(line)
        if opening and not (opening[1][0] == "`" and "`" in opening[2]):
            fence = (opening[1][0], len(opening[1]), depth, list_indents[-1] if list_indents else 0)
            paragraph = None
            continue
        html_closers = ((r"^ {0,3}<!--", r"-->"), (r"^ {0,3}<\?", r"\?>"),
                        (r"^ {0,3}<!\[CDATA\[", r"\]\]>"),
                        (r"^ {0,3}<![A-Z]", r">"),
                        (r"^ {0,3}<(script|pre|style|textarea)(?:\s|>)", None))
        html_open = False
        for pattern, ending in html_closers:
            match = re.search(pattern, line, re.IGNORECASE)
            if match is not None:
                ending = ending or r"</" + match[1] + r"\s*>"
                if not re.search(ending, line, re.IGNORECASE):
                    html_end = ending
                html_open = True
                break
        if html_open or HTML_BLOCK.match(line) or (paragraph is None and HTML_TAG.match(line)):
            html_until_blank = not html_open
            paragraph = None
            continue
        if DEFINITION.match(line):
            definition_indent = len(line) - len(line.lstrip(" "))
            definition_title_pending = bool(re.fullmatch(
                r" {0,3}\[[^\]]+\]:\s*(?:<[^>]*>|\S+)\s*", line
            ))
            paragraph = None
            continue
        if SETEXT.match(line) and paragraph is not None:
            # The underline makes all preceding paragraph text a heading.
            while violations and violations[-1][1] == paragraph[0]:
                violations.pop()
            paragraph = None
            continue
        if HEADING.match(line) or RULE.match(line) or SETEXT.match(line):
            paragraph = None
            continue
        # A table needs a delimiter row, not just a pipe in prose.
        next_line = unquote(lines[index + 1])[0] if index + 1 < len(lines) else ""
        if TABLE_SEPARATOR.match(line) or ("|" in line and TABLE_SEPARATOR.match(next_line)):
            table = True
            paragraph = None
            continue
        if table and "|" in line:
            continue
        table = False
        # Indented code cannot interrupt an existing paragraph.
        if line.startswith("    ") and (paragraph is None or new_item):
            paragraph = None
            continue
        if new_item:
            paragraph = None
        if paragraph is not None and not previous_hard:
            violations.append((number, paragraph[0]))
        if paragraph is None:
            paragraph = (number, depth)
        previous_hard = hard_break(originals[index])
    return violations


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check Markdown prose uses one physical line per paragraph (no width limit).",
        epilog=(
            "Pass explicit UTF-8 files; directories are not traversed. Includes list and quote "
            "paragraph continuations. Exempts initial YAML frontmatter, fenced/indented code, "
            "headings, lists' item boundaries, pipe tables with delimiter rows, link definitions "
            "with continuation titles/indented continuations, common HTML and standalone-tag blocks, "
            "and intentional hard breaks "
            "(two trailing spaces or an unescaped backslash). This is a bounded block scanner, "
            "not a full Markdown validator; malformed or extension-specific constructs need "
            "manual review. Files are never changed. Exit 0: no wrapping found; nonzero: wrapping, "
            "unreadable/non-UTF-8/non-file input, or usage failure."
        ),
    )
    parser.add_argument("paths", nargs="+", help="Markdown file paths; use -- before paths starting with -")
    args = parser.parse_args(argv)
    failed = False
    for raw in args.paths:
        path = Path(raw)
        try:
            if not path.is_file():
                raise OSError("not a regular file")
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError, ValueError) as exc:
            print(f"{path}: cannot check input: {exc}", file=sys.stderr)
            failed = True
            continue
        for number, start in wrapped_lines(text):
            print(f"{path}:{number}: paragraph started at line {start} continues on another physical line")
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
