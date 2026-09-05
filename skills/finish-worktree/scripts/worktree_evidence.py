"""Read-only local Git and working-file evidence; snapshots are emitted to stdout."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath


SCHEMA = "smartkit.worktree-evidence/v2"


class EvidenceError(RuntimeError):
    pass


def git(repository: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(repository), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise EvidenceError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def encoded(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def file_state(path: Path) -> dict:
    try:
        before = path.lstat()
    except FileNotFoundError:
        return {"type": "absent"}
    mode = stat.S_IMODE(before.st_mode)
    if stat.S_ISLNK(before.st_mode):
        return {"type": "symlink", "mode": mode, "target": os.readlink(path)}
    if stat.S_ISDIR(before.st_mode):
        return {"type": "directory", "mode": mode, "device": before.st_dev, "inode": before.st_ino}
    if not stat.S_ISREG(before.st_mode):
        raise EvidenceError(f"unsupported file type: {path}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (opened.st_dev, opened.st_ino, opened.st_mode) != (
            before.st_dev, before.st_ino, before.st_mode
        ):
            raise EvidenceError(f"file changed during open: {path}")
        hasher = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
        after.st_size, after.st_mtime_ns, after.st_ctime_ns
    ):
        raise EvidenceError(f"file changed during read: {path}")
    return {"type": "file", "mode": mode, "size": after.st_size, "sha256": hasher.hexdigest(),
            "uid": after.st_uid, "gid": after.st_gid}


def normalize_paths(paths: list[str]) -> list[str]:
    result = []
    for name in paths:
        path = PurePosixPath(name)
        if (not name or path.is_absolute() or PureWindowsPath(name).drive
                or ".." in path.parts or any(part.rstrip(" .").casefold() == ".git" for part in path.parts) or "\\" in name):
            raise EvidenceError(f"expected a relative worktree path outside .git: {name!r}")
        result.append(path.as_posix())
    return sorted(set(result))


def working_files(repository: Path, paths: list[str]) -> tuple[dict, dict]:
    files: dict = {}
    ancestors: dict = {}
    identities: dict = {}

    def require_checkout_directory(relative: str) -> None:
        if relative != "." and os.path.lexists(repository / relative / ".git"):
            raise EvidenceError(f"nested repository requires separate evidence: {relative}")

    def visit(relative: str) -> None:
        location = repository / relative
        if os.name == "nt":
            from worktree_transfer_windows import backend
            backend().metadata(location)
        value = file_state(location)
        if value["type"] == "file":
            info = location.lstat()
            identity = (info.st_dev, info.st_ino)
            if info.st_nlink != 1 or identity in identities and identities[identity] != relative:
                raise EvidenceError(f"physical file alias requires separate handling: {relative}")
            identities[identity] = relative
        files[relative] = value
        if value["type"] != "directory":
            return
        require_checkout_directory(relative)
        for child in sorted(location.iterdir()):
            if relative == "." and child.name == ".git":
                continue
            visit(child.relative_to(repository).as_posix())

    for relative in paths:
        parent = PurePosixPath(relative).parent
        for ancestor in reversed((parent, *parent.parents)):
            name = ancestor.as_posix()
            if os.name == "nt":
                from worktree_transfer_windows import backend
                backend().metadata(repository / name)
            value = file_state(repository / name)
            ancestors[name] = value
            if value["type"] not in ("directory", "absent"):
                raise EvidenceError(f"non-directory path ancestor: {name}")
            if value["type"] == "directory":
                require_checkout_directory(name)
        visit(relative)
    return files, ancestors


def observe(repository: Path, paths: list[str], inventory: bool = False) -> dict:
    for variable in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        if os.environ.get(variable):
            raise EvidenceError(f"unset {variable} before collecting actual checkout evidence")
    if repository.absolute() != repository.resolve(strict=True):
        raise EvidenceError("--repository must use its physical path without aliases")
    repository = repository.resolve(strict=True)
    root = Path(os.fsdecode(git(repository, "rev-parse", "--show-toplevel").rstrip(b"\n"))).resolve()
    if repository != root:
        raise EvidenceError("--repository must identify the worktree root")

    def git_path(*args: str) -> Path:
        value = Path(os.fsdecode(git(repository, "rev-parse", *args).rstrip(b"\n")))
        return (repository / value).resolve()

    git_dir = git_path("--absolute-git-dir")
    common_dir = git_path("--git-common-dir")
    index = git_path("--git-path", "index")
    entries = git(repository, "ls-files", "--stage", "-z")
    if any(entry.startswith(b"160000 ") for entry in entries.split(b"\0")):
        raise EvidenceError("submodules require separate evidence")
    shared = git(repository, "rev-parse", "--shared-index-path").rstrip(b"\n")
    shared_path = (repository / os.fsdecode(shared)).resolve() if shared else None
    files, ancestors = working_files(repository, paths)
    # Inventory is explicit: bounded transfers need no global working-file scan.
    status_bytes = git(
        repository, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored=matching"
    ) if inventory else None
    result = {
        "schema": SCHEMA,
        "repository": str(repository),
        "paths": paths,
        "inventory": inventory,
        "identity": {
            "git_dir": str(git_dir), "common_dir": str(common_dir),
            "directories": {"worktree": file_state(repository), "git": file_state(git_dir),
                            "common": file_state(common_dir)},
            "registration": encoded(git(repository, "worktree", "list", "--porcelain", "-z")),
            "head": git(repository, "rev-parse", "HEAD^{commit}").decode().strip(),
            "head_file": encoded((git_dir / "HEAD").read_bytes()),
        },
        "index": {
            "path": str(index), "state": file_state(index),
            "shared_path": str(shared_path) if shared_path else None,
            "shared_state": file_state(shared_path) if shared_path else None,
        },
        "status": encoded(status_bytes) if status_bytes is not None else None,
        "ancestors": ancestors,
        "files": files,
    }
    if os.name == "nt":
        from worktree_transfer_windows import backend
        native = backend()
        result["windows"] = {
            "files": {name: native.metadata(repository / name) for name in files},
            "ancestors": {name: native.metadata(repository / name) for name in ancestors},
            "administration": {
                "index": native.metadata(index),
                "shared_index": native.metadata(shared_path) if shared_path else None,
                "git": native.metadata(git_dir), "common": native.metadata(common_dir),
            },
        }
    return result


def snapshot(repository: Path, paths: list[str] | None = None, inventory: bool = False) -> dict:
    if inventory and paths:
        raise EvidenceError("choose bounded paths or full inventory")
    scope = ["."] if inventory else normalize_paths(paths or [])
    first = observe(repository, scope, inventory)
    if observe(repository, scope, inventory) != first:
        raise EvidenceError("worktree changed between observations")
    return first


def compare(expected: dict) -> list[str]:
    if not isinstance(expected, dict) or expected.get("schema") != SCHEMA:
        raise EvidenceError("unsupported snapshot schema")
    if not isinstance(expected.get("repository"), str) or not isinstance(expected.get("paths"), list):
        raise EvidenceError("snapshot requires repository and paths")
    if not all(isinstance(path, str) for path in expected["paths"]):
        raise EvidenceError("snapshot paths must be strings")
    if not isinstance(expected.get("inventory"), bool):
        raise EvidenceError("snapshot requires an inventory boolean")
    current = snapshot(
        Path(expected["repository"]), None if expected["inventory"] else expected["paths"],
        expected["inventory"],
    )
    if expected.keys() != current.keys():
        raise EvidenceError("snapshot has missing or unknown fields")
    return sorted(key for key in current if current[key] != expected[key])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture = commands.add_parser("snapshot", help="emit stable observed state as JSON")
    capture.add_argument("--repository", type=Path, required=True)
    capture.add_argument("--path", action="append", default=[], help="relative dependency path; repeat as needed")
    capture.add_argument("--inventory", action="store_true", help="explicit full working-file inventory")
    comparison = commands.add_parser("compare", help="compare current state with an external snapshot")
    comparison.add_argument("--snapshot", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            print(json.dumps(snapshot(args.repository, args.path, args.inventory), sort_keys=True))
            return 0
        changed = compare(json.loads(args.snapshot.read_text(encoding="utf-8")))
        print(json.dumps({"equal": not changed, "changed": changed}, sort_keys=True))
        return 1 if changed else 0
    except (EvidenceError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
