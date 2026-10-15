"""Export captured UTF-8 comparisons as fixed, self-contained HTML files."""
from __future__ import annotations

import argparse
import difflib
import html
import json
import math
import os
import re
import shutil
import stat
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import quote


CACHE_SCHEMA = "smartkit.review-html-cache/v1"
RETENTION_SECONDS = 7 * 24 * 60 * 60


@dataclass(frozen=True)
class Comparison:
    id: str
    title: str
    before: Optional[bytes]
    after: Optional[bytes]


def _unique_object(pairs: Sequence[Tuple[str, object]]) -> Dict[str, object]:
    result = {}  # type: Dict[str, object]
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field: " + key)
        result[key] = value
    return result


def capture_batch(source: Path) -> List[Comparison]:
    """Validate the whole batch and capture bytes before creating any output."""
    entries = json.loads(source.read_bytes().decode("utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(entries, list) or not entries:
        raise ValueError("input must be a nonempty JSON array")
    comparisons = []  # type: List[Comparison]
    identities = set()
    for number, entry in enumerate(entries, 1):
        if not isinstance(entry, dict) or set(entry) != {"id", "title", "before", "after"}:
            raise ValueError("entry %d needs exactly id, title, before, and after" % number)
        for key in ("id", "title"):
            value = entry[key]
            if not isinstance(value, str) or not value or any(ord(c) < 32 for c in value):
                raise ValueError("entry %d: %s must be a nonempty single line" % (number, key))
        identity = entry["id"]
        if identity in identities:
            raise ValueError("duplicate id: " + identity)
        identities.add(identity)
        contents = []  # type: List[Optional[bytes]]
        for side in ("before", "after"):
            name = entry[side]
            if name is None:
                contents.append(None)
                continue
            if not isinstance(name, str) or not name:
                raise ValueError("entry %d: %s must be a nonempty path or null" % (number, side))
            path = (source.parent / name).resolve(strict=True)
            if not path.is_file():
                raise ValueError("entry %d: %s is not a regular file" % (number, side))
            content = path.read_bytes()
            content.decode("utf-8")
            contents.append(content)
        if contents == [None, None]:
            raise ValueError("entry %d needs at least one existing side" % number)
        comparisons.append(Comparison(identity, entry["title"], contents[0], contents[1]))
    return comparisons


def _describe(content: Optional[bytes]) -> str:
    if content is None:
        return "不存在"
    crlf = content.count(b"\r\n")
    ending = "有末尾换行" if content.endswith((b"\n", b"\r")) else "无末尾换行"
    return "%d 字节；CRLF %d，LF %d，CR %d；%s" % (
        len(content), crlf, content.count(b"\n") - crlf, content.count(b"\r") - crlf, ending)


def render_diff(comparison: Comparison) -> str:
    before = comparison.before.decode("utf-8") if comparison.before is not None else ""
    after = comparison.after.decode("utf-8") if comparison.after is not None else ""
    table = difflib.HtmlDiff(tabsize=4, wrapcolumn=120).make_table(
        before.splitlines(), after.splitlines(), fromdesc="修改前", todesc="修改后", context=False)
    newline_note = ("<p>仅换行符或文件末尾换行发生变化；原始字节保存在前后快照中。</p>"
                    if before != after and before.splitlines() == after.splitlines() else "")
    title = html.escape(comparison.title)
    return ("<!doctype html><html lang=\"zh-CN\"><meta charset=\"utf-8\">"
            "<title>" + title + " · Diff</title>"
            "<style>body{font:14px system-ui;margin:24px;background:#fafafa;color:#202124}"
            "h1{font-size:20px}table.diff{border-collapse:collapse;width:100%;font:13px monospace}"
            "td,th{padding:3px 8px;vertical-align:top}.diff_header{background:#e8ebef}"
            ".diff_add{background:#d6f5dd}.diff_sub{background:#ffd9d9}"
            ".diff_chg{background:#fff0b3}.diff_next{background:#eee}a{color:#245ec7}</style>"
            "<h1>" + title + "</h1><p>固定快照 · 左侧修改前，右侧修改后</p>"
            "<p>修改前：" + _describe(comparison.before) + "<br>修改后：" + _describe(comparison.after)
            + "</p>" + newline_note + "<div style=\"overflow:auto\">" + table + "</div></html>")


def _markdown(title: str, path: Path) -> str:
    label = re.sub(r"([\\`*_\[\]])", r"\\\1", html.escape(title, quote=False))
    return "[" + label + "](<" + quote(path.as_posix(), safe="/:") + ">)"


def cache_root() -> Path:
    """Select the platform user cache, never the retired deep-link data root."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    elif sys.platform == "win32":
        configured = Path(os.environ.get("LOCALAPPDATA", ""))
        base = configured if configured.is_absolute() else Path.home() / "AppData" / "Local"
    else:
        configured = Path(os.environ.get("XDG_CACHE_HOME", ""))
        base = configured if configured.is_absolute() else Path.home() / ".cache"
    return base.resolve() / "smartkit" / "review-for-humans"


def _redirected(path: Path) -> bool:
    """Reject junctions and other Windows reparse points as well as symlinks."""
    try:
        information = path.lstat()
    except FileNotFoundError:
        return False
    return (stat.S_ISLNK(information.st_mode)
            or bool(getattr(information, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT))


def _owned_creation_time(entry: Path) -> Optional[float]:
    """Recognize only this helper's complete, unmodified cache layout.

    Stored paths are checked as metadata, never followed for deletion. Unknown
    files, malformed metadata, symlinks, and reparse points leave the group untouched.
    """
    try:
        if not re.fullmatch(r"review-[0-9a-f]{32}", entry.name) or _redirected(entry) or not entry.is_dir():
            return None
        if {path.name for path in entry.iterdir()} != {"files"}:
            return None
        files = entry / "files"
        if _redirected(files) or not files.is_dir():
            return None
        for name in ("cache.json", "manifest.json"):
            path = files / name
            if _redirected(path) or not path.is_file():
                return None
        metadata = json.loads((files / "cache.json").read_bytes().decode("utf-8"),
                              object_pairs_hook=_unique_object)
        if (not isinstance(metadata, dict) or set(metadata) != {"schema", "directory", "created_at"}
                or metadata["schema"] != CACHE_SCHEMA or metadata["directory"] != entry.name):
            return None
        created = metadata["created_at"]
        if type(created) not in (int, float) or not math.isfinite(created) or created <= 0:
            return None
        manifest = json.loads((files / "manifest.json").read_bytes().decode("utf-8"),
                              object_pairs_hook=_unique_object)
        if not isinstance(manifest, list) or not manifest:
            return None
        expected = {"cache.json", "manifest.json"}
        identities = set()
        for number, record in enumerate(manifest, 1):
            if (not isinstance(record, dict) or set(record) != {"id", "title", "path", "markdown"}
                    or not all(isinstance(value, str) for value in record.values())):
                return None
            if (not record["id"] or record["id"] in identities or not record["title"]
                    or any(ord(c) < 32 for c in record["id"] + record["title"])):
                return None
            identities.add(record["id"])
            folder_name = "%04d" % number
            expected.add(folder_name)
            folder = files / folder_name
            if _redirected(folder) or not folder.is_dir():
                return None
            path = folder / "diff.html"
            if record["path"] != str(path) or record["markdown"] != _markdown(record["title"], path):
                return None
            children = list(folder.iterdir())
            names = {child.name for child in children}
            if ("diff.html" not in names or not names & {"before.txt", "after.txt"}
                    or names - {"diff.html", "before.txt", "after.txt"}
                    or any(_redirected(child) or not child.is_file() for child in children)):
                return None
        if {path.name for path in files.iterdir()} != expected:
            return None
        return float(created)
    except (OSError, ValueError, OverflowError):
        # Ownership cannot be established from unreadable or malformed records; preserve their bytes.
        return None


def cleanup_expired(root: Path, now: float) -> None:
    """Remove recognized groups at seven elapsed days; report each lasting effect."""
    for entry in sorted(root.iterdir()):
        created = _owned_creation_time(entry)
        if created is None:
            if entry.name.startswith("review-"):
                print("Preserved unrecognized or unsafe cache: " + str(entry), file=sys.stderr)
            continue
        if now - created < RETENTION_SECONDS:
            continue
        try:
            shutil.rmtree(entry)
        except OSError as error:
            raise OSError("expired cache cleanup failed at %s; some files may already be deleted: %s"
                          % (entry, error)) from error
        print("Expired cache removed: " + str(entry), file=sys.stderr)


def export_batch(source: Path) -> List[Dict[str, str]]:
    """Validate input, expire owned cache, then publish one fresh fixed export.

    Deletions are reported immediately and remain effective if generation fails.
    Unrecognized records, symlinks, and reparse points are preserved. Rendering finishes
    before the new export's pages become visible together as `files`.
    """
    source = source.resolve(strict=True)
    comparisons = capture_batch(source)
    root = cache_root()
    for directory in (root.parent, root):
        if _redirected(directory):
            raise ValueError("cache namespace must not redirect through a link or reparse point: " + str(directory))
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    cleanup_expired(root, time.time())
    output = root / ("review-" + uuid.uuid4().hex)
    results = []  # type: List[Dict[str, str]]
    with tempfile.TemporaryDirectory(prefix=".pending-review-", dir=str(root)) as temporary:
        staged = Path(temporary) / "files"
        staged.mkdir(mode=0o700)
        for number, comparison in enumerate(comparisons, 1):
            folder_name = "%04d" % number
            folder = staged / folder_name
            folder.mkdir(mode=0o700)
            for side, content in (("before", comparison.before), ("after", comparison.after)):
                if content is not None:
                    (folder / (side + ".txt")).write_bytes(content)
            (folder / "diff.html").write_bytes(render_diff(comparison).encode("utf-8"))
            path = output / "files" / folder_name / "diff.html"
            results.append({"id": comparison.id, "title": comparison.title, "path": str(path),
                            "markdown": _markdown(comparison.title, path)})
        (staged / "manifest.json").write_bytes(json.dumps(results, ensure_ascii=True, indent=2).encode("utf-8"))
        metadata = {"schema": CACHE_SCHEMA, "directory": output.name, "created_at": time.time()}
        (staged / "cache.json").write_bytes(json.dumps(metadata, ensure_ascii=True).encode("utf-8"))
        # Reserve exclusively: renaming a directory alone can replace an existing empty directory on Unix.
        output.mkdir(mode=0o700)
        try:
            staged.rename(output / "files")
        except OSError as error:
            try:
                output.rmdir()
            except OSError as cleanup_error:
                raise OSError("export failed (%s); could not remove reserved directory %s (%s)"
                              % (error, output, cleanup_error)) from error
            raise
    return results


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capture fixed UTF-8 comparisons and generate self-contained HTML before returning links.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Batch schema (JSON array; every field is required):
  [{"id":"M1-v1","title":"src/example.py","before":"before.txt","after":"after.txt"}]

Use unique nonempty ids and single-line titles. Paths resolve relative to the
batch file; null denotes the absent side of an addition or deletion. Supply
captured UTF-8 files, not refs or URLs. Neither side may be absent together.

Success returns a JSON array with id, title, absolute HTML path, and Markdown
link. A unique group under the user cache's smartkit/review-for-humans namespace
contains files/manifest.json, raw before.txt/after.txt snapshots, self-contained
HTML, and files/cache.json (schema, directory identity, successful-generation
Unix timestamp). Missing sides have no snapshot file. Cache locations:
  Linux: absolute XDG_CACHE_HOME, otherwise ~/.cache
  macOS: ~/Library/Caches
  Windows: absolute LOCALAPPDATA, otherwise ~/AppData/Local

After validating inputs, each invocation removes recognized groups generated
at least seven elapsed days earlier, then generates the new group. Access and
file mtimes do not extend retention. Cleanup happens only on a new generation;
HTML links can stop working then. HTML, raw bytes, and mapping are removed as
one group. Foreign/damaged records, symlinks, and Windows reparse points are
preserved. Legacy
deep-link snapshots are outside this cache and are never touched.

All pages are generated before links are returned. Failures exit 2 with no
links. Expiry removals are logged individually to stderr; they are not rolled
back if later cleanup or generation fails. A failed removal stops generation
and reports that the affected group may be partially deleted. Existing
unexpired and unrelated data is preserved. Open HTML directly in a browser;
no server, installation, network access, or third-party dependencies are used.

Example:
  python export_html_diff.py --input batch.json
''')
    parser.add_argument("--input", type=Path, required=True, help="JSON batch of captured before/after files")
    args = parser.parse_args(argv)
    try:
        result = export_batch(args.input)
    except (OSError, ValueError) as error:
        parser.exit(2, "error: " + str(error) + "\n")
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
