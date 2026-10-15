"""Export captured UTF-8 comparisons as fixed, self-contained HTML files."""
from __future__ import annotations

import argparse
import difflib
import html
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, Sequence, Tuple


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


def _markdown(title: str, url: str) -> str:
    label = re.sub(r"([\\`*\[\]])", r"\\\1", html.escape(title, quote=False)).replace("_", "&#95;")
    return "[" + label + "](" + url + ")"


def _runtime(relative: str) -> ModuleType:
    """Load only this plugin's dependency, including dataclass module identity."""
    path = (Path(__file__).resolve().parents[3] / relative).resolve()
    if not path.is_file():
        raise FileNotFoundError("shared runtime unavailable: " + str(path))
    name = path.stem
    existing = sys.modules.get(name)
    if existing is not None:
        location = getattr(existing, "__file__", None)
        if not location or Path(location).resolve() != path:
            raise OSError("shared runtime module belongs to another plugin copy: " + name)
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise OSError("shared runtime unavailable: " + str(path))
    runtime = importlib.util.module_from_spec(spec)
    sys.modules[name] = runtime
    try:
        spec.loader.exec_module(runtime)
    except BaseException as error:
        # Failed imports, including interruptions, must not leave a reusable partial module.
        sys.modules.pop(name, None)
        if isinstance(error, ImportError):
            raise OSError("shared runtime unavailable at %s: %s" % (path, error)) from error
        raise
    return runtime


def _valid_url(url: str, identity: str, filename: str) -> bool:
    match = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})/artifacts/"
                         + re.escape(identity + "/" + filename), url)
    return match is not None and int(match.group(1)) <= 65535


def export_batch(source: Path) -> List[Dict[str, str]]:
    """Capture and render one comparison group, then explicitly publish its HTML.

    The shared cache owns storage and expiry. Failed delivery preserves a complete
    cached comparison and identifies it for publication retry without recapture.
    """
    comparisons = capture_batch(source.resolve(strict=True))
    payloads = {}  # type: Dict[str, bytes]
    mapping = []  # type: List[Dict[str, str]]
    for number, comparison in enumerate(comparisons, 1):
        folder = "%04d/" % number
        for side, content in (("before", comparison.before), ("after", comparison.after)):
            if content is not None:
                payloads[folder + side + ".txt"] = content
        filename = folder + "diff.html"
        payloads[filename] = render_diff(comparison).encode("utf-8")
        mapping.append({"id": comparison.id, "title": comparison.title, "file": filename})
    payloads["manifest.json"] = json.dumps(mapping, ensure_ascii=True, indent=2).encode("utf-8")
    artifact = _runtime("runtime/artifacts/artifact_cache.py").create_artifact(
        payloads, public_files=[record["file"] for record in mapping])
    try:
        urls = _runtime("runtime/web/web_service.py").publish_artifact(artifact.id)
        results = []  # type: List[Dict[str, str]]
        for record in mapping:
            filename = record["file"]
            url = urls[filename]
            if not _valid_url(url, artifact.id, filename):
                raise ValueError("shared web service returned an invalid artifact URL")
            results.append({"id": record["id"], "title": record["title"],
                            "path": str(artifact.files[filename].path), "url": url,
                            "markdown": _markdown(record["title"], url)})
    except (OSError, ValueError):
        print("HTTP preview delivery failed; cached artifact %s remains at %s; shared service or publication may remain"
              % (artifact.id, artifact.files["manifest.json"].path.parent), file=sys.stderr)
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

Success returns a JSON array with id, title, absolute HTML path (metadata), url,
and HTTP Markdown link. Its rendered label equals the title, including underscores.
The returned id identifies the comparison; publish --id instead takes the shared
artifact ID from the URL's /artifacts/<artifact-id>/ segment.
Raw before.txt/after.txt snapshots, generated HTML, and a private manifest.json
mapping id/title/file are stored together by the shared artifact cache. Missing
sides have no snapshot file. Only HTML is declared public, then explicitly
published through the shared web service; raw snapshots and mapping stay private.
The immutable mapping omits URLs, which can change when the service restarts.

All input validation and rendering finish before cache creation. Rendering
failures have no cache effects. Cache creation and cleanup use the shared owner's
failure contract. HTTP delivery failures exit 2 with no links, retain the cached
comparison, and report its artifact ID/location and diagnostics. A shared service
or publication mark can remain; the exporter does not roll back shared state.
Republish the retained ID to refresh URLs without recapture or expiry renewal.

Python 3.8 or newer and the full SmartKit plugin distribution are required. Shared
runtime modules resolve from this loaded exporter, independently of the reviewed
repository or current working directory. Operations and lifetime details are in
these supported CLIs (<plugin-root> is the loaded SmartKit installation):
  python "<plugin-root>/runtime/artifacts/artifact_cache.py" --help
  python "<plugin-root>/runtime/web/web_service.py" --help
  python "<plugin-root>/runtime/web/web_service.py" publish --id artifact-ID

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
