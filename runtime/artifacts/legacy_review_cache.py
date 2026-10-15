"""Recognize and expire already-delivered review exports without moving their bytes.

This reader creates no new exports. Their original layout and seven-day deadline
remain necessary to preserve links published before shared artifact storage.
"""
from __future__ import annotations

import html
import json
import math
import re
import shutil
import stat
import sys
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

CACHE_SCHEMA = "smartkit.review-html-cache/v2"
RETENTION_SECONDS = 7 * 24 * 60 * 60


def _unique_object(pairs: Sequence[Tuple[str, object]]) -> Dict[str, object]:
    result = {}  # type: Dict[str, object]
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field: " + key)
        result[key] = value
    return result


def _markdown(title: str, url: str) -> str:
    label = re.sub(r"([\\`*\[\]])", r"\\\1", html.escape(title, quote=False)).replace("_", "&#95;")
    return "[" + label + "](" + url + ")"


def _valid_url(url: str, identity: str, filename: str) -> bool:
    match = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})/artifacts/"
                         + re.escape(identity + "/" + filename), url)
    return match is not None and int(match.group(1)) <= 65535


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
            if (not isinstance(record, dict) or set(record) != {"id", "title", "path", "url", "markdown"}
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
            if (record["path"] != str(path)
                    or not _valid_url(record["url"], entry.name, folder_name + "/diff.html")
                    or record["markdown"] != _markdown(record["title"], record["url"])):
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
            if not entry.exists():
                continue
            raise OSError("expired cache cleanup failed at %s; some files may already be deleted: %s"
                          % (entry, error)) from error
        print("Expired cache removed: " + str(entry), file=sys.stderr)
