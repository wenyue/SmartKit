#!/usr/bin/env python
"""Capture and compare deterministic, Candidate-read-only evidence."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import stat
import struct
import sys
from typing import Any, Iterable, NamedTuple


SNAPSHOT_SCHEMA = "smartkit.candidate-evidence"
CAPTURE_REPORT_SCHEMA = "smartkit.candidate-evidence-capture-report"
COMPARE_REPORT_SCHEMA = "smartkit.candidate-evidence-report"
INVALID_EXIT = 2
PATH_BOUNDARY_EXIT = 3
TEXT_LINE_ENDINGS = (
    "\n",
    "\r",
    "\v",
    "\f",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x85",
    "\u2028",
    "\u2029",
)


class EvidenceError(Exception):
    """The requested evidence is invalid or cannot be determined."""


class ObservedFile(NamedTuple):
    data: bytes
    executable_bits: int | None


def executable_mode() -> str:
    """Windows permission emulation does not establish POSIX executable bits."""
    return "posix-executable-bits" if os.name == "posix" else "unsupported"


def normalize_relative(raw: str) -> str:
    """Return one normalized relative POSIX path or raise EvidenceError."""
    if not raw or "\x00" in raw:
        raise EvidenceError("paths must be non-empty relative POSIX paths")
    source = PurePosixPath(raw)
    if source.is_absolute() or ".." in source.parts:
        raise EvidenceError(f"path is outside the allowed relative namespace: {raw!r}")
    normalized = posixpath.normpath(raw)
    candidate = PurePosixPath(normalized)
    if normalized in ("", ".") or candidate.is_absolute() or ".." in candidate.parts:
        raise EvidenceError(f"path does not name a Candidate entry: {raw!r}")
    try:
        normalized.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise EvidenceError(f"path is not representable as UTF-8: {raw!r}") from exc
    return candidate.as_posix()


def canonical_paths(raw_paths: Iterable[str]) -> list[str]:
    paths = sorted({normalize_relative(raw) for raw in raw_paths})
    if not paths:
        raise EvidenceError("at least one Candidate path is required")
    return paths


def _resolved_root(raw: str) -> Path:
    try:
        root = Path(raw).resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise EvidenceError(f"Candidate root is unavailable: {raw!r}") from exc
    if not root.is_dir():
        raise EvidenceError(f"Candidate root is not a directory: {raw!r}")
    return root


def _inside(path: Path, directory: Path) -> bool:
    return path == directory or directory in path.parents


def _new_snapshot_path(raw: str, root: Path) -> Path:
    try:
        output = Path(raw)
        if os.path.lexists(output):
            raise EvidenceError(f"snapshot output already exists: {raw!r}")
        parent = output.parent.resolve(strict=True)
    except EvidenceError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise EvidenceError(f"snapshot parent is unavailable: {str(output.parent)!r}") from exc
    if not parent.is_dir():
        raise EvidenceError(f"snapshot parent is not a directory: {str(output.parent)!r}")
    resolved = parent / output.name
    if _inside(resolved, root):
        raise EvidenceError("snapshot output must be outside the Candidate root")
    return resolved


def _existing_snapshot_path(raw: str, root: Path) -> Path:
    try:
        source = Path(raw)
        if source.is_symlink():
            raise EvidenceError("snapshot directory cannot be a symlink")
        snapshot = source.resolve(strict=True)
    except EvidenceError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise EvidenceError(f"snapshot is unavailable: {raw!r}") from exc
    if not snapshot.is_dir():
        raise EvidenceError(f"snapshot is not a directory: {raw!r}")
    if _inside(snapshot, root):
        raise EvidenceError("snapshot must be outside the Candidate root")
    return snapshot


def _same_stat(
    left: os.stat_result, right: os.stat_result, *, compare_ctime: bool = True
) -> bool:
    return (not compare_ctime or left.st_ctime_ns == right.st_ctime_ns) and (
        left.st_dev,
        left.st_ino,
        left.st_mode,
        left.st_size,
        left.st_mtime_ns,
    ) == (
        right.st_dev,
        right.st_ino,
        right.st_mode,
        right.st_size,
        right.st_mtime_ns,
    )


def _observe_entry(root: Path, relative: str) -> ObservedFile | None:
    current = root
    chain: list[tuple[Path, os.stat_result]] = []
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        current = current / part
        try:
            observed = os.lstat(current)
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise EvidenceError(f"cannot observe Candidate path {relative!r}: {exc}") from exc
        if stat.S_ISLNK(observed.st_mode):
            raise EvidenceError(f"Candidate path traverses a symlink: {relative!r}")
        if index < len(parts) - 1:
            if not stat.S_ISDIR(observed.st_mode):
                raise EvidenceError(f"Candidate path has a non-directory ancestor: {relative!r}")
        elif not stat.S_ISREG(observed.st_mode):
            raise EvidenceError(f"present Candidate entry is not a regular file: {relative!r}")
        chain.append((current, observed))

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(current, flags)
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            data = stream.read()
            after = os.fstat(stream.fileno())
    except OSError as exc:
        raise EvidenceError(f"cannot read Candidate path {relative!r}: {exc}") from exc
    if not stat.S_ISREG(before.st_mode) or not _same_stat(before, after):
        raise EvidenceError(f"Candidate entry changed during observation: {relative!r}")
    # Windows path and handle queries can report different ctime values for one file.
    # Keep ctime checks within each API to detect changes during the observation.
    if (
        not _same_stat(chain[-1][1], before, compare_ctime=os.name != "nt")
        or len(data) != before.st_size
    ):
        raise EvidenceError(f"Candidate entry changed during observation: {relative!r}")
    for path, original in chain:
        try:
            current_stat = os.lstat(path)
        except OSError as exc:
            raise EvidenceError(f"Candidate path changed during observation: {relative!r}") from exc
        if not _same_stat(original, current_stat):
            raise EvidenceError(f"Candidate path changed during observation: {relative!r}")
    bits = before.st_mode & 0o111 if executable_mode() == "posix-executable-bits" else None
    return ObservedFile(data, bits)


def observe(root: Path, paths: Iterable[str]) -> dict[str, ObservedFile | None]:
    return {path: _observe_entry(root, path) for path in paths}


def stable_observation(root: Path, paths: list[str]) -> dict[str, ObservedFile | None]:
    first = observe(root, paths)
    second = observe(root, paths)
    if first != second:
        raise EvidenceError("Candidate changed between the two complete observations")
    return second


def fingerprint(
    paths: Iterable[str], values: dict[str, ObservedFile | None], mode: str
) -> str:
    digest = hashlib.sha256()
    digest.update(b"smartkit-candidate-evidence\x00" + mode.encode("ascii") + b"\x00")
    for path in paths:
        path_bytes = path.encode("utf-8")
        observed = values[path]
        digest.update(struct.pack(">Q", len(path_bytes)))
        digest.update(path_bytes)
        digest.update(b"\x00" if observed is None else b"\x01")
        if observed is not None:
            digest.update(bytes([255 if observed.executable_bits is None else observed.executable_bits]))
            digest.update(struct.pack(">Q", len(observed.data)))
            digest.update(observed.data)
    return digest.hexdigest()


def _metadata(observed: ObservedFile | None) -> dict[str, Any]:
    if observed is None:
        return {"present": False, "sha256": None, "size": None, "executable_bits": None}
    return {
        "present": True,
        "sha256": hashlib.sha256(observed.data).hexdigest(),
        "size": len(observed.data),
        "executable_bits": observed.executable_bits,
    }


def _manifest(root: Path, paths: list[str], values: dict[str, ObservedFile | None]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for index, path in enumerate(paths):
        observed = values[path]
        meta = _metadata(observed)
        entries.append(
            {
                "path": path,
                "payload": f"payloads/{index:06d}.bin" if observed is not None else None,
                **meta,
            }
        )
    return {
        "entries": entries,
        "executable_mode": executable_mode(),
        "fingerprint": fingerprint(paths, values, executable_mode()),
        "root": str(root),
        "schema": SNAPSHOT_SCHEMA,
    }


def _write_snapshot(
    output: Path, manifest: dict[str, Any], values: dict[str, ObservedFile | None]
) -> None:
    output.mkdir(mode=0o700)
    payloads = output / "payloads"
    payloads.mkdir(mode=0o700)
    for entry in manifest["entries"]:
        observed = values[entry["path"]]
        if observed is not None:
            payload_path = output / entry["payload"]
            with payload_path.open("xb") as stream:
                stream.write(observed.data)
    encoded = json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    with (output / "manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded)


def _regular_snapshot_file(path: Path, label: str) -> bytes:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise EvidenceError(f"snapshot {label} is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise EvidenceError(f"snapshot {label} is not a regular file")
    try:
        data = path.read_bytes()
        after = os.lstat(path)
    except OSError as exc:
        raise EvidenceError(f"snapshot {label} cannot be read") from exc
    if not _same_stat(observed, after) or len(data) != observed.st_size:
        raise EvidenceError(f"snapshot {label} changed during validation")
    return data


def _load_snapshot(
    snapshot: Path,
) -> tuple[list[str], dict[str, ObservedFile | None], str, Path]:
    raw_manifest = _regular_snapshot_file(snapshot / "manifest.json", "manifest")
    try:
        manifest = json.loads(raw_manifest.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("snapshot manifest is not valid UTF-8 JSON") from exc
    if not isinstance(manifest, dict) or set(manifest) != {
        "entries",
        "executable_mode",
        "fingerprint",
        "root",
        "schema",
    }:
        raise EvidenceError("snapshot manifest has an invalid shape")
    if manifest["schema"] != SNAPSHOT_SCHEMA:
        raise EvidenceError("snapshot schema is unsupported")
    mode = manifest["executable_mode"]
    if mode not in ("posix-executable-bits", "unsupported"):
        raise EvidenceError("snapshot executable-mode policy is invalid")
    if mode != executable_mode():
        raise EvidenceError("snapshot executable-mode policy is unsupported on this platform")
    captured_root_value = manifest["root"]
    if not isinstance(captured_root_value, str):
        raise EvidenceError("snapshot root information is invalid")
    try:
        captured_root = Path(captured_root_value)
        canonical_root = captured_root.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise EvidenceError("snapshot captured root is unavailable") from exc
    if (
        not captured_root.is_absolute()
        or not canonical_root.is_dir()
        or str(canonical_root) != captured_root_value
    ):
        raise EvidenceError("snapshot captured root is not an absolute canonical directory")
    expected_fingerprint = manifest["fingerprint"]
    if (
        not isinstance(expected_fingerprint, str)
        or len(expected_fingerprint) != 64
        or any(character not in "0123456789abcdef" for character in expected_fingerprint)
    ):
        raise EvidenceError("snapshot fingerprint is invalid")
    raw_entries = manifest["entries"]
    if not isinstance(raw_entries, list) or not raw_entries:
        raise EvidenceError("snapshot entries must be a non-empty list")

    paths: list[str] = []
    values: dict[str, ObservedFile | None] = {}
    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, dict) or set(entry) != {
            "path",
            "executable_bits",
            "payload",
            "present",
            "sha256",
            "size",
        }:
            raise EvidenceError("snapshot entry has an invalid shape")
        path = entry["path"]
        if not isinstance(path, str) or normalize_relative(path) != path:
            raise EvidenceError("snapshot entry path is not canonical")
        if not isinstance(entry["present"], bool):
            raise EvidenceError(f"snapshot presence state is invalid for {path!r}")
        if entry["present"]:
            bits = entry["executable_bits"]
            if mode == "posix-executable-bits":
                if (not isinstance(bits, int) or isinstance(bits, bool)
                        or bits < 0 or bits & ~0o111):
                    raise EvidenceError(f"snapshot executable bits are invalid for {path!r}")
            elif bits is not None:
                raise EvidenceError(f"unsupported executable bits must be null for {path!r}")
            expected_payload = f"payloads/{index:06d}.bin"
            if entry["payload"] != expected_payload:
                raise EvidenceError(f"snapshot payload mapping is invalid for {path!r}")
            size = entry["size"]
            content_hash = entry["sha256"]
            if (
                not isinstance(size, int)
                or isinstance(size, bool)
                or size < 0
                or not isinstance(content_hash, str)
                or len(content_hash) != 64
                or any(character not in "0123456789abcdef" for character in content_hash)
            ):
                raise EvidenceError(f"snapshot metadata is invalid for {path!r}")
            payloads_directory = snapshot / "payloads"
            if payloads_directory.is_symlink() or not payloads_directory.is_dir():
                raise EvidenceError("snapshot payloads directory is invalid")
            data = _regular_snapshot_file(snapshot / expected_payload, f"payload for {path!r}")
            if len(data) != size or hashlib.sha256(data).hexdigest() != content_hash:
                raise EvidenceError(f"snapshot payload does not match its metadata for {path!r}")
            observed = ObservedFile(data, bits)
        else:
            if (
                entry["payload"] is not None
                or entry["size"] is not None
                or entry["sha256"] is not None
                or entry["executable_bits"] is not None
            ):
                raise EvidenceError(f"missing snapshot entry has payload metadata for {path!r}")
            observed = None
        paths.append(path)
        values[path] = observed

    if paths != sorted(set(paths)):
        raise EvidenceError("snapshot paths are not sorted and unique")
    actual_fingerprint = fingerprint(paths, values, mode)
    if actual_fingerprint != expected_fingerprint:
        raise EvidenceError("snapshot fingerprint does not match its contents and mode metadata")
    return paths, values, actual_fingerprint, canonical_root


def _text(data: bytes | None) -> str | None:
    if data is None:
        return ""
    try:
        decoded = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return None if "\x00" in decoded else decoded


def _display_lines(text: str) -> list[str]:
    return [json.dumps(line, ensure_ascii=True) for line in text.splitlines(keepends=True)]


def _delta(path: str, before: ObservedFile | None, after: ObservedFile | None) -> dict[str, Any]:
    before_text = _text(None if before is None else before.data)
    after_text = _text(None if after is None else after.data)
    if before_text is None or after_text is None:
        return {"kind": "binary"}
    from_name = "/dev/null" if before is None else f"a/{path}"
    to_name = "/dev/null" if after is None else f"b/{path}"
    lines = difflib.unified_diff(
        _display_lines(before_text),
        _display_lines(after_text),
        fromfile=from_name,
        tofile=to_name,
        lineterm="",
    )
    records = list(lines)
    rendered = "\n".join(records)
    if rendered:
        rendered += "\n"
    return {
        "after_final_newline": after_text.endswith(TEXT_LINE_ENDINGS),
        "before_final_newline": before_text.endswith(TEXT_LINE_ENDINGS),
        "kind": "text",
        "unified": rendered,
    }


def _change_kind(before: ObservedFile | None, after: ObservedFile | None) -> str:
    if before is None:
        return "added"
    if after is None:
        return "deleted"
    return "modified"


def capture(args: argparse.Namespace) -> int:
    root = _resolved_root(args.root)
    paths = canonical_paths(args.path)
    output = _new_snapshot_path(args.output, root)
    values = stable_observation(root, paths)
    manifest = _manifest(root, paths, values)
    try:
        _write_snapshot(output, manifest, values)
    except OSError as exc:
        raise EvidenceError(
            f"cannot create snapshot at {str(output)!r}; a partial snapshot may remain at "
            f"{str(output)!r} and requires Controller cleanup: {exc}"
        ) from exc
    print(
        json.dumps(
            {
                "fingerprint": manifest["fingerprint"],
                "executable_mode": manifest["executable_mode"],
                "paths": paths,
                "schema": CAPTURE_REPORT_SCHEMA,
            },
            sort_keys=True,
        )
    )
    return 0


def compare(args: argparse.Namespace) -> int:
    root = _resolved_root(args.root)
    snapshot = _existing_snapshot_path(args.snapshot, root)
    paths, baseline, baseline_fingerprint, captured_root = _load_snapshot(snapshot)
    if captured_root != root:
        raise EvidenceError(
            "snapshot was captured for a different Candidate root: "
            f"{str(captured_root)!r} != {str(root)!r}"
        )
    allowed_change_paths = sorted(
        {normalize_relative(raw) for raw in args.allowed_change_path}
    )
    unknown_allowed_paths = sorted(set(allowed_change_paths) - set(paths))
    if unknown_allowed_paths:
        raise EvidenceError(
            "allowed change path is outside the frozen Candidate allowlist: "
            + ", ".join(unknown_allowed_paths)
        )
    current = stable_observation(root, paths)
    changes: list[dict[str, Any]] = []
    changed_paths: list[str] = []
    for path in paths:
        before = baseline[path]
        after = current[path]
        if before == after:
            continue
        changed_paths.append(path)
        changes.append(
            {
                "after": _metadata(after),
                "before": _metadata(before),
                "change": _change_kind(before, after),
                "delta": _delta(path, before, after),
                "path": path,
            }
        )
    changed_within_subset = [path for path in changed_paths if path in allowed_change_paths]
    violations = [path for path in changed_paths if path not in allowed_change_paths]
    report = {
        "allowed_change_paths": allowed_change_paths,
        "changed_paths": changed_paths,
        "changed_paths_within_allowed_subset": changed_within_subset,
        "changes": changes,
        "current_fingerprint": fingerprint(paths, current, executable_mode()),
        "executable_mode": executable_mode(),
        "frozen_paths": paths,
        "path_boundary": "PASS" if not violations else "VIOLATION",
        "path_boundary_violations": violations,
        "schema": COMPARE_REPORT_SCHEMA,
        "snapshot_fingerprint": baseline_fingerprint,
    }
    print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    return 0 if not violations else PATH_BOUNDARY_EXIT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Capture and compare deterministic evidence for an exact Candidate path allowlist."
        ),
        epilog=(
            "Output schemas: capture stdout "
            f"{CAPTURE_REPORT_SCHEMA}, snapshot manifest {SNAPSHOT_SCHEMA}; "
            f"compare stdout {COMPARE_REPORT_SCHEMA}. Exit 0: capture succeeded, or compare "
            "evidence is valid with no path-subset violation; exit 2: usage error or "
            "invalid/indeterminate evidence; exit 3: compare found a changed path outside "
            "--allowed-change-path. Compare reports path-subset evidence, not operation "
            "authorization or the workflow's final Candidate boundary judgment. Evidence binds "
            "presence, bytes and POSIX executable bits (mode & 0111); other permission bits are "
            "outside its scope. Windows and other non-POSIX platforms record executable mode "
            "as unsupported with null bits. Comparing across these mode policies is refused."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture_parser = subparsers.add_parser(
        "capture", help="capture a new immutable baseline snapshot"
    )
    capture_parser.add_argument("--root", required=True, help="Candidate root directory")
    capture_parser.add_argument(
        "--output", required=True, help="new snapshot directory outside the Candidate root"
    )
    capture_parser.add_argument(
        "--path",
        action="append",
        required=True,
        help="allowed relative POSIX Candidate path; repeat for each entry",
    )
    capture_parser.set_defaults(handler=capture)

    compare_parser = subparsers.add_parser(
        "compare", help="compare the frozen baseline with the current Candidate"
    )
    compare_parser.add_argument("--root", required=True, help="Candidate root directory")
    compare_parser.add_argument("--snapshot", required=True, help="baseline snapshot directory")
    compare_parser.add_argument(
        "--allowed-change-path",
        action="append",
        default=[],
        help="relative Candidate path allowed to change; repeat as needed",
    )
    compare_parser.set_defaults(handler=compare)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except EvidenceError as exc:
        print(f"candidate_evidence: {exc}", file=sys.stderr)
        return INVALID_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
