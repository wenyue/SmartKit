#!/usr/bin/env python
"""Run every read-only document check this Skill owns; see --help for the checks."""

from __future__ import annotations

import argparse
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import textwrap
import unicodedata
from typing import Callable, Dict, Iterator, List, NamedTuple, Optional, Sequence, Set, Tuple, Union
from urllib.parse import unquote as percent_decode


INPUT_ERROR_EXIT = 2
PROBLEM_EXIT = 1


class Finding(NamedTuple):
    line: int
    message: str
    # The check could not finish this item, so the result is incomplete.
    input_error: bool = False


class Document(NamedTuple):
    path: Path
    text: str
    anchors: Callable[[Path], Set[str]]
    mapping: Optional["PathMapping"] = None


class InputError(Exception):
    """A required input or path mapping cannot be checked safely."""


def confined_path(root: Path, relative: Path) -> Path:
    """Inspect only descendants of an explicitly selected root, without following links."""
    current = root
    for part in relative.parts:
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            break
        except OSError as exc:
            raise InputError(f"cannot inspect mapped path {current}: {exc}") from exc
        if (stat.S_ISLNK(metadata.st_mode)
                or getattr(metadata, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
            raise InputError(f"mapped path traverses a link: {current}")
    return root / relative


class PathMapping(NamedTuple):
    candidate_root: Path
    target_root: Path
    candidate_paths: Set[Path]
    context_paths: Set[Path]

    def input_relative(self, source: Path) -> Path:
        try:
            relative = Path(os.path.abspath(source)).relative_to(self.candidate_root)
        except ValueError as exc:
            raise InputError(f"input is outside --candidate-root: {source}") from exc
        if relative not in self.candidate_paths:
            raise InputError(f"input is outside the exact Candidate path set: {source}")
        confined_path(self.candidate_root, relative)
        return relative

    def resolve(self, source: Path, location: str) -> Path:
        relative = self.input_relative(source)
        destination = self.target_root / relative
        if location:
            destination = Path(os.path.abspath(destination.parent / location))
        try:
            final_relative = destination.relative_to(self.target_root)
        except ValueError as exc:
            raise InputError(f"link leaves --target-root: {location}") from exc
        mapped_paths = self.candidate_paths | self.context_paths
        if final_relative in mapped_paths:
            # A frozen mapped path owns absence too; stale target bytes cannot replace it.
            return confined_path(self.candidate_root, final_relative)
        for mapped_path in mapped_paths:
            if (final_relative in mapped_path.parents
                    and confined_path(self.candidate_root, mapped_path).is_file()):
                return confined_path(self.candidate_root, final_relative)
        return confined_path(self.target_root, final_relative)


def mapped_paths(root: Path, raw_paths: Sequence[str], option: str) -> Set[Path]:
    paths: Set[Path] = set()
    for raw in raw_paths:
        relative = PurePosixPath(raw)
        if (not raw or "\x00" in raw or "\\" in raw or SCHEME.match(raw)
                or relative.is_absolute() or ".." in relative.parts or not relative.parts):
            raise InputError(f"{option} must be a relative POSIX file path: {raw!r}")
        path = Path(*relative.parts)
        try:
            candidate = confined_path(root, path)
        except (InputError, OSError) as exc:
            raise InputError(f"{option}: {exc}") from exc
        if candidate.exists() and not candidate.is_file():
            raise InputError(f"present {option} is not a regular file: {raw!r}")
        paths.add(path)
    return paths


def path_mapping(args: argparse.Namespace) -> Optional[PathMapping]:
    supplied = (args.candidate_root is not None, args.target_root is not None,
                bool(args.candidate_path), bool(args.context_path))
    if not any(supplied):
        return None
    if args.context_path and not all(supplied[:3]):
        raise InputError(
            "--context-path requires --candidate-root, --target-root and --candidate-path"
        )
    if not all(supplied[:3]):
        raise InputError("mapping requires --candidate-root, --target-root and --candidate-path")
    roots = [Path(os.path.abspath(raw)) for raw in (args.candidate_root, args.target_root)]
    for root in roots:
        if not root.is_dir():
            raise InputError(f"mapped root is not an available directory: {root}")
    candidate_paths = mapped_paths(roots[0], args.candidate_path, "Candidate path")
    context_paths = mapped_paths(roots[0], args.context_path, "--context-path")
    overlap = candidate_paths & context_paths
    if overlap:
        path = min(overlap, key=str)
        raise InputError(
            f"--context-path must be disjoint from --candidate-path: {path.as_posix()!r}"
        )
    return PathMapping(roots[0], roots[1], candidate_paths, context_paths)


def read_markdown(path: Path) -> str:
    try:
        if not path.is_file():
            raise OSError("not a regular file")
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError, ValueError) as exc:
        raise InputError(str(exc)) from exc


def frontmatter_end(lines: Sequence[str]) -> int:
    """Return the index after a closed leading frontmatter block, or 0 when there is none."""
    if not lines or lines[0].lstrip("\ufeff").rstrip() != "---":
        return 0
    for index in range(1, len(lines)):
        if lines[index].rstrip() in ("---", "..."):
            return index + 1
    return 0


# paragraph-lines ---------------------------------------------------------

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
    body = frontmatter_end(lines)
    table = False
    previous_hard = False

    for index, original in enumerate(lines):
        number = index + 1
        if index < body:
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


def check_paragraph_lines(document: Document) -> List[Finding]:
    return [
        Finding(number, f"paragraph started at line {start} continues on another physical line")
        for number, start in wrapped_lines(document.text)
    ]


# relative-links ----------------------------------------------------------

CONTAINERS = re.compile(r"^(?:\s*>)*\s*")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)")
LINK_OPENER = re.compile(r"(?<!\\)\]\(")
REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[([^\]]+)\]:[ \t]*(<[^>]*>|\S+)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
ATX_HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
NOT_SETEXT_TEXT = re.compile(r"^\s*(?:[>#|]|[-+*][ \t]|\d{1,9}[.)][ \t])")
HTML_ANCHOR = re.compile(r"<a\s[^>]*?\b(?:id|name)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
MARKDOWN_SUFFIXES = (".md", ".markdown")


def content_lines(text: str) -> Iterator[Tuple[int, str]]:
    """Yield lines outside leading frontmatter and fenced code."""
    lines = text.splitlines()
    fence: Optional[Tuple[str, int]] = None
    for index in range(frontmatter_end(lines), len(lines)):
        line = lines[index]
        bare = CONTAINERS.sub("", line, count=1)
        if fence is not None:
            if re.fullmatch(re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*", bare):
                fence = None
            continue
        opening = re.match(r"^(`{3,}|~{3,})(.*)$", bare)
        if opening and not (opening[1][0] == "`" and "`" in opening[2]):
            fence = (opening[1][0], len(opening[1]))
            continue
        yield index + 1, line


def github_slug(heading: str) -> str:
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = re.sub(r"<[^>]+>", "", text).replace("`", "").strip().lower()
    kept = []
    for character in text:
        if character == " ":
            kept.append("-")
        elif (character == "-" or character.isalnum()
              or unicodedata.category(character) in ("Mn", "Mc", "Me", "Pc")):
            kept.append(character)
    return "".join(kept)


def heading_anchors(text: str) -> Set[str]:
    anchors: Set[str] = set()
    seen: Dict[str, int] = {}
    previous: Optional[Tuple[int, str]] = None
    for number, line in content_lines(text):
        anchors.update(match[1] for match in HTML_ANCHOR.finditer(line))
        heading: Optional[str] = None
        atx = ATX_HEADING.match(line)
        if atx:
            heading = atx[1] or ""
        elif (SETEXT_UNDERLINE.match(line) and previous is not None and previous[0] == number - 1
              and previous[1].strip() and not NOT_SETEXT_TEXT.match(previous[1])
              and not ATX_HEADING.match(previous[1])):
            heading = previous[1]
        previous = (number, line)
        if heading is None:
            continue
        slug = github_slug(heading)
        repeat = seen.get(slug, 0)
        seen[slug] = repeat + 1
        anchors.add(slug if repeat == 0 else f"{slug}-{repeat}")
    return anchors


def parse_destination(line: str, start: int) -> Optional[str]:
    """Return the inline link destination that starts at `start`, if complete."""
    index = start
    while index < len(line) and line[index] in " \t":
        index += 1
    if line.startswith("<", index):
        end = line.find(">", index + 1)
        if end == -1 or ")" not in line[end:]:
            return None
        return line[index + 1:end]
    depth = 0
    end = index
    while end < len(line):
        character = line[end]
        if character == "\\":
            end += 2
            continue
        if character.isspace():
            break
        if character == "(":
            depth += 1
        elif character == ")":
            if depth == 0:
                break
            depth -= 1
        end += 1
    if ")" not in line[end:]:
        return None
    return re.sub(r"\\(.)", r"\1", line[index:end])


def link_targets(line: str) -> Iterator[str]:
    line = CODE_SPAN.sub("", line)
    definition = REFERENCE_DEFINITION.match(CONTAINERS.sub("", line, count=1))
    if definition and not definition[1].startswith("^"):
        target = definition[2]
        yield target[1:-1] if target.startswith("<") else target
        return
    for opener in LINK_OPENER.finditer(line):
        if "[" not in line[:opener.start()]:
            continue
        target = parse_destination(line, opener.end())
        if target is not None:
            yield target


def check_link(document: Document, number: int, target: str) -> Optional[Finding]:
    if not target.strip():
        return Finding(number, "link has an empty target")
    if SCHEME.match(target) or target.startswith("//"):
        return None
    location, has_fragment, fragment = target.partition("#")
    location = percent_decode(location.partition("?")[0])
    if location.startswith("/"):
        return None
    where = location or "this file"
    try:
        if document.mapping is None:
            destination = document.path.parent / location if location else document.path
        else:
            destination = document.mapping.resolve(document.path, location)
        exists = destination.exists()
        is_dir = exists and destination.is_dir()
    except (OSError, ValueError, InputError) as exc:
        return Finding(number, f"cannot inspect link target {where}: {exc}", True)
    if not exists:
        return Finding(number, f"link target does not exist: {target}")
    if not (has_fragment and fragment) or destination.suffix.lower() not in MARKDOWN_SUFFIXES or is_dir:
        return None
    try:
        anchors = document.anchors(destination)
    except InputError as exc:
        return Finding(number, f"cannot read link target {where} to resolve #{fragment}: {exc}", True)
    if percent_decode(fragment) not in anchors:
        return Finding(number, f"anchor #{fragment} matches no heading or HTML anchor in {where}")
    return None


def check_relative_links(document: Document) -> List[Finding]:
    findings = []
    for number, line in content_lines(document.text):
        for target in link_targets(line):
            finding = check_link(document, number, target)
            if finding is not None:
                findings.append(finding)
    return findings


# skill-frontmatter -------------------------------------------------------

QUOTED_KEY = re.compile(r"""^(?:"((?:[^"\\]|\\.)*)"|'((?:[^']|'')*)')[ \t]*:(?:[ \t]+(.*))?$""")
PLAIN_KEY = re.compile(r"""^((?:[^\s\-?:,\[\]{}#&*!|>'"%@`]|[-?:](?=\S)).*?)[ \t]*:(?:[ \t]+(.*))?$""")
SEQUENCE_ENTRY = re.compile(r"^-(?:[ \t]|$)")
BLOCK_SCALAR = re.compile(r"^([|>])[+-]?[1-9]?[+-]?[ \t]*(?:#.*)?$")
DOUBLE_QUOTED = re.compile(r'^"((?:[^"\\]|\\.)*)"[ \t]*(?:#.*)?$')
SINGLE_QUOTED = re.compile(r"^'((?:[^']|'')*)'[ \t]*(?:#.*)?$")
ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\", "/": "/", " ": " "}
UNSUPPORTED = "is not a plain, quoted, or block string this check can read"
PLAIN_MAPPING = ("is plain text containing ': ' or ending in ':', which YAML reads as a mapping; "
                 "quote it or use a | or > block scalar")


class UnreadableValue(Exception):
    """A name or description value whose string this check cannot establish."""


def unescape(text: str) -> str:
    return re.sub(r"\\(.)", lambda escape: ESCAPES.get(escape[1], escape[0]), text)


def top_level_entry(line: str) -> Optional[Tuple[str, str]]:
    """Return the key and inline value of a top-level 'key: value' line."""
    quoted = QUOTED_KEY.match(line)
    if quoted:
        key = unescape(quoted[1]) if quoted[1] is not None else quoted[2].replace("''", "'")
        return key, (quoted[3] or "").strip()
    plain = PLAIN_KEY.match(line)
    return None if plain is None else (plain[1], (plain[2] or "").strip())


def scalar_value(raw: str, continuation: List[str]) -> str:
    """Return the string a supported scalar form denotes; raise UnreadableValue otherwise."""
    following = [line.strip() for line in continuation if line.strip()]
    if not raw or raw.startswith("#"):
        following = [line for line in following if not line.startswith("#")]
        if not following:
            return ""
        raw, following = following[0], following[1:]
    block = BLOCK_SCALAR.match(raw)
    if block:
        return ("\n" if block[1] == "|" else " ").join(following)
    joined = " ".join([raw] + following)
    if raw.startswith('"'):
        quoted = DOUBLE_QUOTED.match(joined)
        if quoted is None:
            raise UnreadableValue(UNSUPPORTED)
        return unescape(quoted[1])
    if raw.startswith("'"):
        quoted = SINGLE_QUOTED.match(joined)
        if quoted is None:
            raise UnreadableValue(UNSUPPORTED)
        return quoted[1].replace("''", "'")
    if raw[0] in "[{&*!%@`|>" or re.match(r"[-?:](?:[ \t]|$)", raw):
        raise UnreadableValue(UNSUPPORTED)
    parts = [re.sub(r"(?:^|[ \t]+)#.*$", "", line).strip() for line in [raw] + following]
    if any(re.search(r":(?:[ \t]|$)", part) for part in parts):
        raise UnreadableValue(PLAIN_MAPPING)
    plain = " ".join(part for part in parts if part)
    return "" if plain in ("~", "null", "Null", "NULL") else plain


def check_skill_frontmatter(document: Document) -> List[Finding]:
    if document.path.name != "SKILL.md":
        return []
    lines = document.text.splitlines()
    if not lines or lines[0].lstrip("\ufeff").rstrip() != "---":
        return [Finding(1, "SKILL.md must begin with a '---' YAML frontmatter line")]
    closing = frontmatter_end(lines) - 1
    if closing < 0:
        return [Finding(1, "frontmatter is not closed by a '---' line")]
    findings: List[Finding] = []
    after = [index for index in range(closing + 1, len(lines)) if lines[index].strip()][:2]
    if (len(after) == 2 and lines[after[0]].rstrip() == "---"
            and re.match(r"^[A-Za-z_][\w.-]*[ \t]*:(?:[ \t]|$)", lines[after[1]])):
        findings.append(Finding(after[0] + 1, "a second YAML block follows the frontmatter; keep metadata in one block"))

    values: Dict[str, Tuple[int, str, List[str]]] = {}
    index = 1
    while index < closing:
        line = lines[index].rstrip()
        number = index + 1
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        entry = top_level_entry(line)
        if entry is None:
            findings.append(Finding(number, "cannot read this frontmatter line as a top-level 'key: value' entry"))
            continue
        key, raw = entry
        # An empty value may own a block sequence written at the key's own column.
        opens_block = not raw or raw.startswith("#")
        continuation = []
        while index < closing:
            following = lines[index]
            if (following.strip() and following[0] not in " \t"
                    and not (opens_block and (SEQUENCE_ENTRY.match(following) or following.startswith("#")))):
                break
            continuation.append(following)
            index += 1
        if key not in ("name", "description"):
            continue
        if key in values:
            findings.append(Finding(number, f"duplicate frontmatter key '{key}'"))
            continue
        values[key] = (number, raw, continuation)

    directory = Path(os.path.abspath(document.path)).parent.name
    for key in ("name", "description"):
        if key not in values:
            findings.append(Finding(1, f"frontmatter has no {key} field"))
            continue
        number, raw, continuation = values[key]
        try:
            value = scalar_value(raw, continuation)
        except UnreadableValue as exc:
            findings.append(Finding(number, f"{key} {exc}"))
            continue
        if key == "name" and value != directory:
            findings.append(Finding(number, f"name '{value}' does not match the containing directory '{directory}'"))
        elif key == "description" and not value.strip():
            findings.append(Finding(number, "description is empty"))
    findings.sort(key=lambda finding: finding.line)
    return findings


# entry -------------------------------------------------------------------

class Check(NamedTuple):
    name: str
    run: Callable[[Document], List[Finding]]
    help: str


CHECKS = (
    Check("paragraph-lines", check_paragraph_lines, (
        "Every prose paragraph, including list-item and quoted paragraphs, occupies one physical "
        "line; readers use editor soft wrapping, and there is no width limit. Exempt: a leading "
        "YAML frontmatter block closed by '---' or '...', fenced and indented code, headings, list "
        "item boundaries, pipe tables with a "
        "delimiter row, link reference definitions with their titles or indented continuations, "
        "common HTML blocks and standalone tag lines, and intentional hard breaks (two trailing "
        "spaces or an unescaped trailing backslash). This is a bounded block scanner, not a full "
        "Markdown validator; malformed or extension-specific constructs need manual review."
    )),
    Check("relative-links", check_relative_links, (
        "Relative targets of inline links, images, and link reference definitions must exist, "
        "by default resolved from the directory of the file that contains the link, after percent-decoding "
        "and dropping any ?query. A #fragment into a .md or .markdown file, including a bare "
        "#fragment into the same file, must match a heading anchor or an <a id/name> in that file. "
        "Heading anchors follow GitHub: lowercase the heading text, drop punctuation other than "
        "hyphens and underscores, turn each space into a hyphen, and suffix repeated anchors with "
        "-1, -2, and so on; matching is exact. The target file is read only to resolve its anchors; "
        "nothing else is scanned and URLs are never fetched. Not checked: targets with a URL scheme "
        "(https:, mailto:, and others) or starting with //, root-relative /paths, fragments into "
        "directories or non-Markdown files, reference-style uses such as [text][label], and "
        "destinations that continue onto another line. A closed leading frontmatter block, fenced "
        "code, and code spans are skipped; links in HTML comments and indented code are checked "
        "like prose, and underscore emphasis, HTML entities, and multi-line setext text in "
        "headings are taken literally."
    )),
    Check("skill-frontmatter", check_skill_frontmatter, (
        "Applies only to files named SKILL.md. The file begins with one YAML frontmatter block "
        "opened by '---' and closed by '---' or '...', not followed by a second block. Its "
        "top-level name equals the name of the directory containing the file, and its description "
        "is a non-empty string. Without a YAML library, the check reads top-level 'key: value' "
        "lines with plain or quoted keys, together with each value's indented lines and any '- ' "
        "sequence items written at the key's column under an empty value. Another top-level line, "
        "such as a stray sequence item or an explicit '?' key, is reported because it can hide or "
        "break those fields. Plain, single- or double-quoted, and | or > block scalars are "
        "understood. For name and description, a duplicate key, another form (flow collections, "
        "anchors, aliases, tags), and plain text containing ': ' or ending in ':', which YAML reads "
        "as a mapping, are reported. Other fields and their YAML syntax are not validated."
    )),
)


def build_parser() -> argparse.ArgumentParser:
    def paragraph(text: str, indent: str = "") -> str:
        return textwrap.fill(text, width=79, initial_indent=indent, subsequent_indent=indent,
                             break_on_hyphens=False)

    sections = ["Checks:"]
    for check in CHECKS:
        sections.append(f"  {check.name}\n{paragraph(check.help, '    ')}")
    sections.append(paragraph(
        "For staged or backup files retaining their final target-relative layout, supply "
        "--candidate-root, --target-root and repeated --candidate-path for the complete frozen "
        "Candidate scope, including missing/deleted paths. Inputs must belong to that exact "
        "scope. When other accepted Candidates share the staging or backup root, repeat "
        "--context-path for their exact frozen paths, including missing/deleted paths. Context paths "
        "are authoritative over the target for link resolution, but are never inputs and their prose "
        "is not checked. "
        "Relative links use mapped files for declared destinations, even when absent, and retained "
        "target files otherwise; undeclared Candidate-root files are ignored. Surviving mapped "
        "descendants establish new directories. Anchors use the selected file. Candidate and context "
        "paths must be disjoint. "
        "Mapped paths must remain beneath the selected roots without symlink or reparse-point "
        "traversal. Mapping does not grant target access or scan additional documents; the "
        "caller supplies authorized roots and scope. Without these options, links resolve "
        "beside their input files as before."
    ))
    sections.append(paragraph(
        "Pass Markdown files explicitly; directories are not traversed, and files are never "
        "changed. Document problems go to stdout as 'path:line: check-name: message'. Usage and "
        "input errors, including an unreadable input or link target, go to stderr."
    ))
    sections.append(paragraph(
        "Exit 0: no problem found. Exit 1: document problems only. Exit 2: usage or input error; "
        "the result is incomplete, so 2 takes precedence over 1."
    ))
    parser = argparse.ArgumentParser(
        description="Run every read-only document check owned by write-rules-and-skills.",
        epilog="\n\n".join(sections),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="+", help="Markdown file paths; use -- before paths starting with -")
    parser.add_argument("--candidate-root", help="staging or backup root with target-relative layout")
    parser.add_argument("--target-root", help="authorized final target root for retained link destinations")
    parser.add_argument("--candidate-path", action="append", default=[],
                        help="relative POSIX path in the exact frozen Candidate scope; repeat for all paths")
    parser.add_argument("--context-path", action="append", default=[],
                        help="relative POSIX path in another accepted Candidate; repeat for all paths")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        mapping = path_mapping(args)
    except (InputError, OSError, ValueError) as exc:
        print(f"cannot use path mapping: {exc}", file=sys.stderr)
        return INPUT_ERROR_EXIT
    cache: Dict[Path, Union[Set[str], InputError]] = {}

    def anchors(path: Path) -> Set[str]:
        key = path.absolute()
        if key not in cache:
            try:
                cache[key] = heading_anchors(read_markdown(key))
            except InputError as exc:
                cache[key] = exc
        result = cache[key]
        if isinstance(result, InputError):
            raise result
        return result

    problems = input_errors = False
    for raw in args.paths:
        path = Path(raw)
        try:
            if mapping is not None:
                path = mapping.candidate_root / mapping.input_relative(path)
            text = read_markdown(path)
        except InputError as exc:
            print(f"{raw}: cannot check input: {exc}", file=sys.stderr)
            input_errors = True
            continue
        document = Document(path, text, anchors, mapping)
        results = [(finding, check.name) for check in CHECKS for finding in check.run(document)]
        for finding, name in sorted(results, key=lambda result: result[0].line):
            report = f"{raw}:{finding.line}: {name}: {finding.message}"
            if finding.input_error:
                print(report, file=sys.stderr)
                input_errors = True
            else:
                print(report)
                problems = True
    if input_errors:
        return INPUT_ERROR_EXIT
    return PROBLEM_EXIT if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
