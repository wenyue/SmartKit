"""Prepare, apply, inspect or recover one accepted batch of regular working-file changes."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path, PurePosixPath

import worktree_evidence as evidence


SCHEMA = "smartkit.worktree-transfer/v1"


class TransferError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TransferError(message)


def windows():
    from worktree_transfer_windows import backend
    return backend()


def physical(path: Path) -> Path:
    if os.name == "nt":
        return windows().physical(path)
    require(sys.platform.startswith("linux") and hasattr(os, "listxattr") and hasattr(os, "O_PATH"),
            "batch transfer requires Linux path and extended-metadata inspection; this host is unsupported")
    absolute = path.absolute()
    require(absolute == absolute.resolve(), f"physical path required: {path}")
    existing = absolute
    while not existing.exists():
        existing = existing.parent
    descriptor = os.open(existing, os.O_PATH | os.O_NOFOLLOW)
    try:
        canonical = os.readlink(f"/proc/self/fd/{descriptor}")
        require(canonical == str(existing), f"physical path alias is unsupported: {path}")
    finally:
        os.close(descriptor)
    return absolute


def supported_directory(path: Path) -> None:
    if os.name == "nt":
        require(windows().metadata(path)["kind"] == "directory", f"real NTFS directory required: {path}")
        return
    physical(path)
    require(path.is_dir(), f"real directory required: {path}")
    require(not os.listxattr(path, follow_symlinks=False),
            f"directory extended metadata requires separate handling: {path}")


def sync_directory(directory: Path) -> None:
    if os.name == "posix":
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def save(operation: Path, receipt: dict) -> None:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=operation, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(receipt, stream, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, operation / "receipt.json")
    sync_directory(operation)


def load(operation: Path) -> dict:
    operation = physical(operation)
    receipt = json.loads((operation / "receipt.json").read_text(encoding="utf-8"))
    require(receipt.get("schema") == SCHEMA, "unsupported operation receipt")
    require(receipt.get("operation") == str(operation), "operation directory identity changed")
    return receipt


def supported(path: Path, value: dict, allow_absent: bool = True) -> None:
    physical(path)
    require(value["type"] == "file" or allow_absent and value["type"] == "absent",
            f"only regular files and absence are supported: {path}")
    if os.name == "nt":
        native = windows().metadata(path)
        require(native["kind"] == value["type"], "Windows type mismatch")
        return
    if value["type"] == "file":
        require(isinstance(value["mode"], int) and 0 <= value["mode"] <= 0o777, f"unsupported mode: {path}")
        require(path.lstat().st_nlink == 1, f"hardlink requires separate handling: {path}")
        require(not os.listxattr(path, follow_symlinks=False),
                f"extended attributes require separate handling: {path}")


def copy_file(source: Path, destination: Path, mode: int) -> None:
    supported(source, evidence.file_state(source), allow_absent=False)
    supported_directory(destination.parent)
    with source.open("rb") as incoming, destination.open("xb") as outgoing:
        shutil.copyfileobj(incoming, outgoing)
        outgoing.flush()
        os.fsync(outgoing.fileno())
    destination.chmod(mode)
    created = evidence.file_state(destination)
    require(created["mode"] == mode, "host cannot preserve the requested regular-file mode")
    supported(destination, created, allow_absent=False)


def outside(path: Path, roots: list[Path]) -> None:
    require(all(path != root and root not in path.parents for root in roots),
            f"operation inputs and storage must be outside affected worktrees/Git directories: {path}")


def guard_paths(repository: Path, paths: list[str], files: dict, ancestors: dict) -> None:
    actual_files, actual_ancestors = evidence.working_files(repository, paths)
    require(actual_files == files and actual_ancestors == ancestors, "working-file or ancestor drift")
    for name in actual_ancestors:
        supported_directory(repository / name)
    for name, value in actual_files.items():
        supported(repository / name, value)


def boundary_equal(expected: dict, actual: dict) -> bool:
    same = all(expected[key] == actual[key] for key in ("repository", "identity", "index"))
    if "windows" in expected:
        same = same and expected["windows"]["administration"] == actual.get("windows", {}).get("administration")
    return same


def prepare(plan: dict, operation: Path) -> dict:
    require(plan.get("schema") == SCHEMA, "unsupported transfer plan")
    repository = physical(Path(plan["repository"]))
    source = plan["source"]
    require(isinstance(source, dict) and source.get("schema") == evidence.SCHEMA,
            "source must be a current evidence snapshot")
    require(source.get("inventory") is False, "use bounded source evidence")
    require(not evidence.compare(source), "source snapshot drift")
    require(isinstance(plan.get("authority"), str) and bool(plan["authority"].strip()), "authority reference required")
    require(isinstance(plan.get("owner"), str) and bool(plan["owner"].strip()), "continuation owner required")
    baseline = plan.get("baseline", "")
    require(isinstance(baseline, str) and bool(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", baseline)),
            "baseline must be an exact commit OID")
    changes = plan["changes"]
    require(isinstance(changes, list) and bool(changes), "nonempty accepted change list required")
    paths = [change["path"] for change in changes]
    require(all(isinstance(path, str) for path in paths), "change paths must be strings")
    require(paths == sorted(set(paths)) and evidence.normalize_paths(paths) == paths and "." not in paths,
            "use unique sorted normalized relative file paths")
    require(len({path.casefold() for path in paths}) == len(paths), "case aliases are unsupported")
    require(all(":" not in path and all(part == part.rstrip(" .") for part in Path(path).parts) for path in paths),
            "alternate streams and platform path aliases are unsupported")
    require(all(not any(other.startswith(path + "/") for other in paths) for path in paths),
            "ancestor/descendant changes are unsupported")
    require(all(path in source["files"] for path in paths), "source snapshot must cover every change path")
    target = evidence.snapshot(repository, paths)
    require(source["identity"]["common_dir"] == target["identity"]["common_dir"],
            "source and target must share their Git common directory")
    require(source["repository"] != str(repository), "source and target must be distinct checkouts")
    source_identity = source["identity"]["directories"]["worktree"]
    target_identity = target["identity"]["directories"]["worktree"]
    require((source_identity["device"], source_identity["inode"]) !=
            (target_identity["device"], target_identity["inode"]), "source and target must be physically distinct")
    for head in (source["identity"]["head"], target["identity"]["head"]):
        evidence.git(repository, "merge-base", "--is-ancestor", baseline, head)
    roots = [Path(source["repository"]), repository, Path(target["identity"]["common_dir"]),
             Path(source["identity"]["git_dir"]), Path(target["identity"]["git_dir"])]
    operation = physical(operation)
    outside(operation, roots)
    require(not operation.exists(), "operation directory must be new")
    for name, ancestor in target["ancestors"].items():
        require(ancestor["type"] == "directory", f"existing real parent directory required: {name}")
    for change in changes:
        name = change["path"]
        require(change["before"] == target["files"][name], f"prepared target input drift: {name}")
        supported(repository / name, change["before"])
        source_value = source["files"][name]
        require(source_value["type"] in ("file", "absent"), f"unsupported source type: {name}")
        output = change["output"]
        if output is not None:
            output = physical(Path(output))
            if output != Path(source["repository"]) / name:
                outside(output, roots)
            else:
                require(change["after"] == source["files"][name], "direct source output must match accepted S")
            output_state = evidence.file_state(output)
            supported(output, output_state, allow_absent=False)
            require(output_state == change["after"], f"accepted output drift: {name}")
        else:
            require(change["after"] == {"type": "absent"}, "deleted output must be absent")
    supported_directory(operation.parent)
    if os.name == "nt":
        windows().private_directory(operation)
    else:
        operation.mkdir(mode=0o700)
    supported_directory(operation)
    receipt = {
        "schema": SCHEMA, "operation": str(operation), "phase": "preparing",
        "authority": plan["authority"], "owner": plan["owner"], "baseline": baseline,
        "source": source, "target": target, "entries": [], "inflight": None,
        "retention": "Retain source and operation until user or traceably authorized delegate accepts transfer.",
    }
    save(operation, receipt)
    try:
        for index, change in enumerate(changes):
            name = change["path"]
            before = target["files"][name]
            entry = {"path": name, "before": before, "after": {"type": "absent"},
                     "backup": None, "output": None, "pending": None, "state": "pending"}
            if before["type"] == "file":
                backup = operation / f"backup-{index}"
                copy_file(repository / name, backup, before["mode"])
                require(evidence.file_state(backup) == before, f"backup drift: {name}")
                entry["backup"] = backup.name
            if change["output"] is not None:
                output = operation / f"output-{index}"
                pending = operation / f"pending-{index}"
                copy_file(Path(change["output"]), output, change["after"]["mode"])
                copy_file(output, pending, change["after"]["mode"])
                require(evidence.file_state(output) == change["after"], f"accepted output drift: {name}")
                entry.update(output=output.name, pending=pending.name, after=change["after"])
            if before["type"] == "file":
                owner = (repository / name).stat()
                preserved = (operation / entry["backup"]).stat()
                require((owner.st_uid, owner.st_gid) == (preserved.st_uid, preserved.st_gid),
                        "file ownership requires a separately supported mechanism")
                if entry["pending"]:
                    replacement = (operation / entry["pending"]).stat()
                    require((owner.st_uid, owner.st_gid) == (replacement.st_uid, replacement.st_gid),
                            "replacement would change file ownership")
            require(operation.stat().st_dev == (repository / name).parent.stat().st_dev,
                    "operation storage must share the destination filesystem")
            if os.name == "nt":
                entry["windows_before"] = target["windows"]["files"][name]
                entry["windows_after"] = (entry["windows_before"] if entry["after"]["type"] == "file"
                                          and entry["before"]["type"] == "file" else {"kind": "absent"})
                entry["windows_removed"] = f"removed-{index}"
                entry["windows_artifacts"] = {
                    field: windows().metadata(operation / entry[field])
                    for field in ("backup", "output", "pending") if entry[field]
                }
            receipt["entries"].append(entry)
        guard_paths(repository, paths, target["files"], target["ancestors"])
        require(not evidence.compare(source), "source drift during preparation")
        require(boundary_equal(target, evidence.snapshot(repository)), "target HEAD/index drift during preparation")
        receipt["phase"] = "prepared"
        save(operation, receipt)
        return receipt
    except (OSError, ValueError, evidence.EvidenceError, TransferError) as error:
        receipt.update(phase="preparation-failed", error=str(error))
        save(operation, receipt)
        raise


@contextlib.contextmanager
def operation_lock(operation: Path, quiescent: bool = False):
    supported_directory(operation)
    lock = operation / "lock"
    if quiescent and lock.exists():
        lock.unlink()
    with lock.open("x") as stream:
        stream.write(str(os.getpid()))
        stream.flush()
        os.fsync(stream.fileno())
    try:
        yield
    finally:
        lock.unlink()


def per_path_guard(repository: Path, name: str, expected: dict, ancestors: dict) -> None:
    relevant = {str(parent): ancestors[str(parent)] for parent in PurePosixPath(name).parents}
    guard_paths(repository, [name], {name: expected}, relevant)


def entry_guard(repository: Path, entry: dict, side: str, receipt: dict) -> None:
    per_path_guard(repository, entry["path"], entry[side], receipt["target"]["ancestors"])
    if os.name == "nt":
        windows().guard(repository / entry["path"], entry[f"windows_{side}"])
        for name in (str(parent) for parent in PurePosixPath(entry["path"]).parents):
            windows().guard(repository / name, receipt["target"]["windows"]["ancestors"][name])


def artifact_guard(operation: Path, entry: dict, field: str) -> None:
    if os.name == "nt" and entry[field]:
        windows().guard(operation / entry[field], entry["windows_artifacts"][field])


def write_entry(operation: Path, repository: Path, entry: dict, restore: bool = False, record=None) -> None:
    destination = repository / entry["path"]
    if os.name == "nt":
        require(record is not None, "Windows writes require a durable receipt callback")
        native = windows()
        if restore and entry["before"]["type"] == "absent":
            native.delete(destination, entry["windows_after"])
        elif restore and entry["after"]["type"] == "absent":
            retained = operation / entry["windows_removed"]
            retained_state = evidence.file_state(retained)
            supported(retained, retained_state, allow_absent=False)
            require(retained_state == entry["before"], "Windows retained deletion content drift")
            native.move(retained, destination, entry["windows_before"])
        elif not restore and entry["after"]["type"] == "absent":
            native.move(destination, operation / entry["windows_removed"], entry["windows_before"])
        else:
            field = "backup" if restore else "pending"
            artifact_guard(operation, entry, field)
            artifact = operation / entry[field]
            supported(artifact, evidence.file_state(artifact), allow_absent=False)
            require(evidence.file_state(artifact) == entry["before" if restore else "after"], "Windows prepared input drift")
            expected = entry["windows_after"] if restore else entry["windows_before"]
            before_data = entry["after"] if restore else entry["before"]
            def remember(metadata):
                if not restore:
                    entry["windows_after"] = metadata
                record()
            native.write(destination, operation / entry[field], expected, before_data, remember)
        return
    if restore:
        if entry["before"]["type"] == "absent":
            destination.unlink()
        else:
            pending = operation / (entry["backup"] + "-restore")
            copy_file(operation / entry["backup"], pending, entry["before"]["mode"])
            supported(pending, evidence.file_state(pending), allow_absent=False)
            require(evidence.file_state(pending) == entry["before"], "restore output drift")
            os.replace(pending, destination)
    elif entry["after"]["type"] == "absent":
        destination.unlink()
    else:
        supported(operation / entry["pending"], evidence.file_state(operation / entry["pending"]), allow_absent=False)
        require(evidence.file_state(operation / entry["pending"]) == entry["after"], "pending output drift")
        os.replace(operation / entry["pending"], destination)
    sync_directory(destination.parent)


def observe_receipt(receipt: dict) -> dict:
    repository = Path(receipt["target"]["repository"])
    actual = evidence.snapshot(repository, receipt["target"]["paths"])
    states = {}
    for entry in receipt["entries"]:
        value = actual["files"][entry["path"]]
        before_matches = value == entry["before"]
        after_matches = value == entry["after"]
        if "windows" in actual:
            native = actual["windows"]["files"][entry["path"]]
            before_matches = before_matches and native == entry["windows_before"]
            after_matches = after_matches and native == entry["windows_after"]
        states[entry["path"]] = ("both" if before_matches and after_matches else
                                 "before" if before_matches else "after" if after_matches else "other")
    return {"phase": receipt["phase"], "boundary_preserved": boundary_equal(receipt["target"], actual),
            "paths": states, "inflight": receipt["inflight"],
            "locked": (Path(receipt["operation"]) / "lock").exists()}


def inspect(operation: Path) -> dict:
    return observe_receipt(load(operation))


def apply(operation: Path) -> dict:
    operation = physical(operation)
    with operation_lock(operation):
        receipt = load(operation)
        require(receipt["phase"] == "prepared", "apply requires the original prepared attempt; inspect other states")
        repository = Path(receipt["target"]["repository"])
        try:
            actual = evidence.snapshot(repository, receipt["target"]["paths"])
            require(actual == receipt["target"], "target drift before apply")
            require(not evidence.compare(receipt["source"]), "source drift before apply")
            for entry in receipt["entries"]:
                for field in ("output", "pending"):
                    if entry[field]:
                        artifact_guard(operation, entry, field)
                        supported(operation / entry[field], evidence.file_state(operation / entry[field]), allow_absent=False)
                        require(evidence.file_state(operation / entry[field]) == entry["after"], "prepared output drift")
                if entry["backup"]:
                    artifact_guard(operation, entry, "backup")
                    supported(operation / entry["backup"], evidence.file_state(operation / entry["backup"]), allow_absent=False)
                    require(evidence.file_state(operation / entry["backup"]) == entry["before"], "backup drift")
            receipt["phase"] = "applying"
            save(operation, receipt)
            for entry in receipt["entries"]:
                name = entry["path"]
                entry_guard(repository, entry, "before", receipt)
                if entry["before"] == entry["after"]:
                    entry["state"] = "unchanged"
                    continue
                receipt["inflight"] = {"path": name, "effect": "apply"}
                save(operation, receipt)
                if os.name == "nt":
                    write_entry(operation, repository, entry, record=lambda: save(operation, receipt))
                else:
                    write_entry(operation, repository, entry)
                entry_guard(repository, entry, "after", receipt)
                entry["state"] = "written"
                receipt["inflight"] = None
                save(operation, receipt)
            observed = observe_receipt(receipt)
            require(observed["boundary_preserved"] and all(value in ("after", "both") for value in observed["paths"].values()),
                    "post-apply preservation proof failed")
            receipt.update(phase="applied", observed=observed)
            save(operation, receipt)
            return observed | {"phase": "applied"}
        except (OSError, ValueError, evidence.EvidenceError, TransferError) as error:
            if receipt["inflight"] is not None:
                current = next(item for item in receipt["entries"] if item["path"] == receipt["inflight"]["path"])
                try:
                    current_files, _ = evidence.working_files(repository, [current["path"]])
                    pending_intact = current["pending"] is None or evidence.file_state(
                        operation / current["pending"]
                    ) == current["after"]
                    if os.name == "nt":
                        pending_intact = pending_intact and windows().metadata(repository / current["path"]) == current["windows_before"]
                        pending_intact = pending_intact and windows().metadata(operation / current["windows_removed"])["kind"] == "absent"
                    if pending_intact and current_files[current["path"]] == current["before"]:
                        receipt["failed_write_absent"] = current["path"]
                        receipt["inflight"] = None
                except (OSError, evidence.EvidenceError):
                    pass
            receipt.update(phase="failed", error=str(error))
            save(operation, receipt)
            raise


def recover(operation: Path, quiescent: bool = False) -> dict:
    require(quiescent, "establish original process quiescence before recovery")
    operation = physical(operation)
    with operation_lock(operation, quiescent=True):
        receipt = load(operation)
        require(receipt["phase"] in ("failed", "applying", "recovering"), "this state does not admit partial-write recovery")
        repository = Path(receipt["target"]["repository"])
        observed = observe_receipt(receipt)
        require(observed["boundary_preserved"], "HEAD/index drift; retain partial state")
        require(not all(value in ("after", "both") for value in observed["paths"].values()),
                "complete candidate remains reviewable; do not roll it back")
        require(receipt["inflight"] is None, "in-flight write is ambiguous; retain state for its owner")
        try:
            receipt["phase"] = "recovering"
            save(operation, receipt)
            for entry in reversed(receipt["entries"]):
                if entry["state"] != "written":
                    continue
                name = entry["path"]
                entry_guard(repository, entry, "after", receipt)
                if entry["backup"]:
                    artifact_guard(operation, entry, "backup")
                    supported(operation / entry["backup"], evidence.file_state(operation / entry["backup"]), allow_absent=False)
                    require(evidence.file_state(operation / entry["backup"]) == entry["before"], "backup drift")
                receipt["inflight"] = {"path": name, "effect": "restore"}
                save(operation, receipt)
                if os.name == "nt":
                    write_entry(operation, repository, entry, restore=True, record=lambda: save(operation, receipt))
                else:
                    write_entry(operation, repository, entry, restore=True)
                entry_guard(repository, entry, "before", receipt)
                entry["state"] = "restored"
                receipt["inflight"] = None
                save(operation, receipt)
            observed = observe_receipt(receipt)
            require(observed["boundary_preserved"], "post-recovery HEAD/index proof failed")
            receipt.update(phase="restored", recovery_observed=observed)
            save(operation, receipt)
            return observed | {"phase": "restored"}
        except (OSError, ValueError, evidence.EvidenceError, TransferError) as error:
            receipt.update(phase="failed", recovery_error=str(error))
            save(operation, receipt)
            raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preparation = commands.add_parser("prepare", help="freeze accepted outputs and external backups")
    preparation.add_argument("--plan", type=Path, required=True)
    preparation.add_argument("--operation", type=Path, required=True)
    for name in ("apply", "inspect", "recover"):
        command = commands.add_parser(name)
        command.add_argument("--operation", type=Path, required=True)
        if name == "recover":
            command.add_argument("--quiescent", action="store_true", help="caller established the original process has stopped")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare(json.loads(args.plan.read_text(encoding="utf-8")), args.operation)
            result = {"phase": result["phase"], "operation": result["operation"], "paths": result["target"]["paths"]}
        elif args.command == "recover":
            result = recover(args.operation, args.quiescent)
        else:
            result = {"apply": apply, "inspect": inspect}[args.command](args.operation)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, evidence.EvidenceError, TransferError) as error:
        print(json.dumps({"error": str(error), "operation": str(args.operation)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
