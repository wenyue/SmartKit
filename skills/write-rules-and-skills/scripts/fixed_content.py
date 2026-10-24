"""Optional frozen-source constraints for the owning check_candidate entry."""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path, PurePosixPath
import re
from typing import Any, List, NamedTuple, Sequence, Set, Tuple

_evidence_spec = importlib.util.spec_from_file_location(
    "_smartkit_candidate_evidence", Path(__file__).with_name("candidate_evidence.py")
)
if _evidence_spec is None or _evidence_spec.loader is None:
    raise ImportError("cannot load the owned Candidate evidence reader")
evidence = importlib.util.module_from_spec(_evidence_spec)
_evidence_spec.loader.exec_module(evidence)


HELP = """Optional fixed-content check:
    Supply --fixed-content DECLARATION and --fixed-snapshot SNAPSHOT together,
    with the complete Candidate mapping. DECLARATION is a relative POSIX path
    captured in an existing candidate_evidence snapshot, alongside every source
    it names. Expected content is read from validated snapshot payloads, never
    from live source files. The snapshot must be outside the Candidate root.
    For in-place work, candidate-root and target-root may be the same directory.

    Declaration schema (both lists are required; at least one must be nonempty):
    {
      "version": 1,
      "fields": [{
        "source": {"path": "source.md", "format": "frontmatter",
                   "key": ["description"]},
        "target": {"path": "example/SKILL.md", "format": "frontmatter",
                   "key": ["description"]}
      }, {
        "source": {"path": "agents/openai.yaml", "format": "yaml",
                   "key": ["interface", "display_name"]},
        "target": {"path": "example/agents/openai.yaml", "format": "yaml",
                   "key": ["interface", "display_name"]}
      }],
      "files": [{"source": "assets/icon.svg",
                 "target": "example/assets/icon.svg"}]
    }

    Paths are canonical relative POSIX file paths. Sources must be present in
    the snapshot; targets must belong to --candidate-path, not --context-path.
    Unknown declaration members, duplicate or overlapping target constraints,
    and a whole-file constraint combined with fields in that file are invalid.
    Fields compare decoded string values exactly; files compare all bytes.
    No rewriting or normalization of Candidate content takes place.

    The bounded field reader follows block mappings with plain identifier or
    quoted keys. Fixed strings may be single-line plain, single-quoted, or
    double-quoted YAML scalars; quote numeric, boolean, or null-like text.
    It rejects unsupported or ambiguous selected values and ancestors,
    including multiline scalars, flow mappings, aliases, tags, anchors, merge
    keys, and duplicate selected keys. Unselected branches are not validated.
    This preserves unrelated metadata without claiming full YAML validation.

    Missing or unequal Candidate fields/files are problems (exit 1). Invalid
    declarations, snapshots, source fields, out-of-scope paths, or unreadable
    or unsupported Candidate syntax are input errors (exit 2). Exit 2 takes
    precedence when other checks also report problems."""


class FixedInputError(Exception):
    """A fixed-content input cannot establish a reliable comparison."""


class MissingField(Exception):
    """A supported mapping does not contain the requested key."""


class Field(NamedTuple):
    path: str
    format: str
    key: Tuple[str, ...]


class Declaration(NamedTuple):
    fields: List[Tuple[Field, Field]]
    files: List[Tuple[str, str]]


class Finding(NamedTuple):
    path: str
    line: int
    message: str
    input_error: bool = False


def _relative(raw: Any) -> str:
    if (not isinstance(raw, str) or not raw or "\\" in raw or ":" in raw
            or "\x00" in raw or raw != PurePosixPath(raw).as_posix()
            or PurePosixPath(raw).is_absolute() or ".." in PurePosixPath(raw).parts
            or raw == "."):
        raise FixedInputError(f"expected a canonical relative POSIX file path: {raw!r}")
    return raw


def _object(value: Any, keys: Set[str]) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        raise FixedInputError(f"expected an object with exactly {sorted(keys)!r}")


def _field(value: Any) -> Field:
    _object(value, {"path", "format", "key"})
    if value["format"] not in ("frontmatter", "yaml"):
        raise FixedInputError("field format must be 'frontmatter' or 'yaml'")
    key = value["key"]
    if not isinstance(key, list) or not key or any(not isinstance(k, str) or not k for k in key):
        raise FixedInputError("field key must be a nonempty list of nonempty strings")
    return Field(_relative(value["path"]), value["format"], tuple(key))


def _unique_object(pairs: Sequence[Tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise FixedInputError(f"duplicate JSON member: {key!r}")
        result[key] = value
    return result


def _declaration(data: bytes, candidate_paths: Set[str]) -> Declaration:
    try:
        raw = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    except (UnicodeError, ValueError) as exc:
        raise FixedInputError(f"cannot read declaration JSON: {exc}") from exc
    _object(raw, {"version", "fields", "files"})
    if type(raw["version"]) is not int or raw["version"] != 1:
        raise FixedInputError("declaration version must be 1")
    if not isinstance(raw["fields"], list) or not isinstance(raw["files"], list):
        raise FixedInputError("declaration fields and files must be lists")
    if not raw["fields"] and not raw["files"]:
        raise FixedInputError("declaration must contain at least one constraint")
    fields: List[Tuple[Field, Field]] = []
    files: List[Tuple[str, str]] = []
    targets: List[Tuple[str, Tuple[str, ...]]] = []
    for item in raw["fields"]:
        _object(item, {"source", "target"})
        source, target = _field(item["source"]), _field(item["target"])
        fields.append((source, target))
        targets.append((target.path, target.key))
    for item in raw["files"]:
        _object(item, {"source", "target"})
        source_path, target_path = _relative(item["source"]), _relative(item["target"])
        files.append((source_path, target_path))
        targets.append((target_path, ()))
    seen: List[Tuple[str, Tuple[str, ...]]] = []
    for path, key in targets:
        if path not in candidate_paths:
            raise FixedInputError(f"fixed target is outside the exact Candidate path set: {path!r}")
        if any(path == previous and (key[:len(other)] == other or other[:len(key)] == key)
               for previous, other in seen):
            raise FixedInputError(f"duplicate or overlapping fixed target: {path!r}, {key!r}")
        seen.append((path, key))
    return Declaration(fields, files)


ESCAPES = {
    "0": "\0", "a": "\a", "b": "\b", "t": "\t", "n": "\n", "v": "\v",
    "f": "\f", "r": "\r", "e": "\x1b", " ": " ", '"': '"', "/": "/",
    "\\": "\\", "N": "\x85", "_": "\xa0", "L": "\u2028", "P": "\u2029",
}
PLAIN_KEY = re.compile(r"(?:[A-Za-z_][A-Za-z0-9_.-]*|<<)")
NON_STRING = re.compile(
    r"(?:null|true|false|yes|no|on|off|~|=|<<|[-+]?(?:[0-9][0-9_:]*(?:\.[0-9_]*)?"
    r"(?:[eE][-+]?[0-9]+)?|0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+"
    r"|\.[0-9_]+(?:[eE][-+]?[0-9]+)?|\.inf|\.nan)"
    r"|[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}(?:[Tt \t].*)?)",
    re.IGNORECASE,
)


def _quoted(raw: str) -> Tuple[str, int]:
    quote = raw[0]
    result: List[str] = []
    index = 1
    while index < len(raw):
        char = raw[index]
        index += 1
        if (ord(char) < 32 and char != "\t") or char in "\x7f\x85\u2028\u2029":
            raise FixedInputError("unsupported raw control or line-break character in YAML string")
        if char == quote:
            if quote == "'" and index < len(raw) and raw[index] == "'":
                result.append("'")
                index += 1
                continue
            return "".join(result), index
        if quote == '"' and char == "\\":
            if index == len(raw):
                break
            escape = raw[index]
            index += 1
            if escape in ESCAPES:
                char = ESCAPES[escape]
            elif escape in ("x", "u", "U"):
                size = {"x": 2, "u": 4, "U": 8}[escape]
                digits = raw[index:index + size]
                if len(digits) != size or not re.fullmatch(r"[0-9a-fA-F]+", digits):
                    raise FixedInputError("invalid YAML Unicode escape")
                codepoint = int(digits, 16)
                if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
                    raise FixedInputError("invalid YAML Unicode code point")
                char = chr(codepoint)
                index += size
            else:
                raise FixedInputError(f"unsupported YAML escape: {escape!r}")
        result.append(char)
    raise FixedInputError("fixed strings and mapping keys must close on one line")


def _scalar(raw: str) -> str:
    value = raw.strip(" \t")
    if not value:
        raise FixedInputError("fixed field must be a string, not an empty YAML value")
    if any((ord(char) < 32 and char != "\t") or 0x7F <= ord(char) <= 0x9F
           or char in "\u2028\u2029" for char in value):
        raise FixedInputError("unsupported control character in YAML scalar")
    if value[0] in "\"'":
        decoded, end = _quoted(value)
        tail = value[end:]
        if tail and (not tail[0].isspace() or (tail.strip() and not tail.lstrip().startswith("#"))):
            raise FixedInputError("unexpected content after quoted YAML string")
        return decoded
    value = re.split(r"[ \t]+#", value, maxsplit=1)[0].rstrip(" \t")
    if (value[0] in "[],{}#&*!|>%@`" or re.match(r"[-?:](?:\s|$)", value)
            or re.search(r":(?:\s|$)", value) or NON_STRING.fullmatch(value)):
        raise FixedInputError("fixed field requires a supported single-line YAML string")
    return value


def _entry(raw: str) -> Tuple[str, str]:
    if raw.startswith(('"', "'")):
        key, end = _quoted(raw)
    else:
        match = PLAIN_KEY.match(raw)
        if match is None:
            raise FixedInputError("unsupported key syntax in selected YAML mapping")
        key, end = match[0], match.end()
    tail = raw[end:].lstrip(" \t")
    if not tail.startswith(":") or (len(tail) > 1 and tail[1] not in " \t"):
        raise FixedInputError("expected a block-mapping entry in selected YAML mapping")
    if key == "<<":
        raise FixedInputError("merge keys make the selected YAML mapping ambiguous")
    return key, tail[1:]


def _string_field(data: bytes, field: Field) -> Tuple[str, int]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeError as exc:
        raise FixedInputError(f"field document is not UTF-8: {exc}") from exc
    lines = list(enumerate(text.replace("\r\n", "\n").split("\n"), 1))
    if field.format == "frontmatter":
        if not lines or lines[0][1].rstrip() != "---":
            raise MissingField("leading frontmatter is absent")
        end = next((i for i, (_, line) in enumerate(lines[1:], 1)
                    if line.rstrip() in ("---", "...")), None)
        if end is None:
            raise FixedInputError("frontmatter is not closed")
        lines = lines[1:end]
    else:
        if lines and lines[0][1].rstrip() == "---":
            lines = lines[1:]
        for index, (_, line) in enumerate(lines):
            if line.rstrip() == "...":
                if any(t.strip() and not t.lstrip().startswith("#") for _, t in lines[index + 1:]):
                    raise FixedInputError("expected one YAML document")
                lines = lines[:index]
                break
    lines = [(number, line) for number, line in lines
             if line.strip() and not line.lstrip().startswith("#")]
    indent = 0
    for depth, requested in enumerate(field.key):
        selected = None
        index = 0
        while index < len(lines):
            number, line = lines[index]
            leading = len(line) - len(line.lstrip(" "))
            if leading != indent:
                raise FixedInputError(f"line {number}: inconsistent selected mapping indentation")
            key, raw = _entry(line[indent:])
            end = index + 1
            opens_block = not raw.strip() or raw.lstrip().startswith("#")
            while end < len(lines):
                following = lines[end][1]
                leading = len(following) - len(following.lstrip(" "))
                if not (leading > indent or (opens_block and leading == indent
                                            and re.match(r"-(?:[ \t]|$)", following[indent:]))):
                    break
                end += 1
            if key == requested:
                if selected is not None:
                    raise FixedInputError(f"line {number}: duplicate selected key {requested!r}")
                selected = number, raw, lines[index + 1:end]
            index = end
        if selected is None:
            raise MissingField(f"key {requested!r} is absent")
        number, raw, children = selected
        if depth == len(field.key) - 1:
            if children:
                raise FixedInputError(f"line {number}: fixed field is not a single-line scalar")
            return _scalar(raw), number
        if raw.strip() and not raw.lstrip().startswith("#"):
            raise FixedInputError(f"line {number}: selected ancestor must be a block mapping")
        if not children:
            raise MissingField(f"key {requested!r} has no child mapping")
        lines = children
        indent = len(lines[0][1]) - len(lines[0][1].lstrip(" "))
    raise FixedInputError("field key is empty")


def check(declaration_path: str, snapshot_path: Path, candidate_root: Path,
          candidate_paths: Set[str]) -> List[Finding]:
    """Compare accepted frozen inputs with the caller's validated Candidate scope."""
    try:
        snapshot = evidence._existing_snapshot_path(str(snapshot_path), candidate_root.resolve())
        _, values, _, _ = evidence._load_snapshot(snapshot)

        def source_bytes(path: str) -> bytes:
            if path not in values or values[path] is None:
                raise FixedInputError(f"source was not captured as present: {path!r}")
            return values[path].data

        declaration = _declaration(source_bytes(_relative(declaration_path)), candidate_paths)
        findings: List[Finding] = []
        for source, target in declaration.fields:
            try:
                try:
                    expected, _ = _string_field(source_bytes(source.path), source)
                except (MissingField, FixedInputError) as exc:
                    raise FixedInputError(f"source {source.path!r}: {exc}") from exc
                observed = evidence._observe_entry(candidate_root, target.path)
                if observed is None:
                    raise MissingField("file is absent")
                actual, line = _string_field(observed.data, target)
                if actual != expected:
                    findings.append(Finding(target.path, line, f"fixed field {target.key!r} differs from source"))
            except MissingField as exc:
                findings.append(Finding(target.path, 1, f"fixed field {target.key!r}: {exc}"))
            except (FixedInputError, evidence.EvidenceError) as exc:
                findings.append(Finding(target.path, 1, str(exc), True))
        for source_path, target_path in declaration.files:
            try:
                expected_bytes = source_bytes(source_path)
                observed = evidence._observe_entry(candidate_root, target_path)
                if observed is None or observed.data != expected_bytes:
                    findings.append(Finding(target_path, 1, "fixed file is absent or differs from source bytes"))
            except (FixedInputError, evidence.EvidenceError) as exc:
                findings.append(Finding(target_path, 1, str(exc), True))
        return findings
    except evidence.EvidenceError as exc:
        raise FixedInputError(str(exc)) from exc
