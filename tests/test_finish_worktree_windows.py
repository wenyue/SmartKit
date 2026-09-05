"""Controlled native-call contracts plus separately identified real-Windows integration tests."""

import contextlib
import copy
import hashlib
import importlib.util
import json
import ntpath
import os
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/finish-worktree/scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    import worktree_transfer_windows as windows
    import worktree_transfer as transfer
finally:
    sys.path.pop(0)


def contents(data):
    return {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}


class ControlledNativeCalls:
    """A deterministic contract fixture, not Windows execution or an ACL emulator."""
    def __init__(self):
        self.nodes = {}
        self.events = []
        self.next_id = 1
        self.partial_failure = False
        self.blocked = set()
        self.filesystem = "NTFS"
        self.add("C:\\", directory=True)
        self.add("C:\\fixture", directory=True)
        self.add("C:\\storage", directory=True)

    def add(self, path, data=b"", directory=False, security="owner/group/DACL", attributes=None):
        self.nodes[ntpath.normcase(path)] = {
            "kind": "directory" if directory else "file", "volume": 7,
            "file_id": self.next_id, "links": 1, "attributes": attributes if attributes is not None else (16 if directory else 32),
            "security": security, "path": path, "data": data, "streams": [] if directory else ["::$DATA"],
        }
        self.next_id += 1

    def volume(self, path):
        windows.require(self.filesystem == "NTFS", "requires local NTFS")

    @contextlib.contextmanager
    def open(self, path, access="metadata", create=False):
        key = ntpath.normcase(path)
        if access == "data" and key in self.blocked:
            raise PermissionError("held writer handle")
        if create:
            if key in self.nodes:
                raise FileExistsError(path)
            self.add(path, security="inherited parent ACL")
            self.events.append(("create", path))
        if key not in self.nodes:
            raise FileNotFoundError(path)
        yield key

    def handle_metadata(self, handle):
        return copy.deepcopy(self.nodes[handle])

    def streams(self, path):
        return self.nodes[ntpath.normcase(path)]["streams"]

    def read(self, handle):
        yield self.nodes[handle]["data"]

    def write(self, handle, chunks, attributes):
        self.events.append(("write", handle))
        data = b"".join(chunks)
        if self.partial_failure:
            self.nodes[handle]["data"] = data[:2] + self.nodes[handle]["data"][2:]
            raise OSError("injected native partial write")
        self.nodes[handle]["data"] = data
        self.nodes[handle]["attributes"] = attributes

    def move(self, source, destination):
        old, new = ntpath.normcase(source), ntpath.normcase(destination)
        if new in self.nodes:
            raise FileExistsError(destination)
        self.nodes[new] = self.nodes.pop(old)
        self.nodes[new]["path"] = destination
        self.events.append(("move", source, destination))

    def delete(self, path):
        del self.nodes[ntpath.normcase(path)]
        self.events.append(("delete", path))

    def private_directory(self, path):
        self.add(path, directory=True, security="private caller/SYSTEM ACL")
        self.events.append(("private_directory", path))


class WindowsAdapterContracts(unittest.TestCase):
    def setUp(self):
        self.native = ControlledNativeCalls()
        self.backend = windows.WindowsBackend(self.native)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.incoming = Path(self.temp.name) / "incoming"
        self.incoming.write_bytes(b"new accepted contents")

    def test_update_keeps_original_identity_acl_and_attributes(self):
        path = "C:\\fixture\\文件 with spaces.txt"
        self.native.add(path, b"old", security="custom protected ACL", attributes=34)
        before = self.backend.metadata(path)
        recorded = []
        after = self.backend.write(path, self.incoming, before, contents(b"old"), recorded.append)
        self.assertEqual(after, before)
        self.assertEqual(recorded, [before])
        self.assertEqual(self.native.nodes[ntpath.normcase(path)]["data"], self.incoming.read_bytes())

    def test_create_is_exclusive_and_records_inherited_security_before_data(self):
        path = "C:\\fixture\\new.txt"
        order = []
        def record(value):
            order.append("record")
            self.assertEqual(value["security"], "inherited parent ACL")
            self.assertEqual(self.native.nodes[ntpath.normcase(path)]["data"], b"")
        self.backend.write(path, self.incoming, {"kind": "absent"}, {"type": "absent"}, record)
        self.assertEqual(order, ["record"])
        self.assertEqual(self.native.events[0], ("create", path))
        with self.assertRaisesRegex(windows.WindowsError, "metadata drift"):
            self.backend.write(path, self.incoming, {"kind": "absent"}, {}, record)

    def test_delete_move_and_restore_keep_the_same_security_object(self):
        original, retained = "C:\\fixture\\delete.txt", "C:\\storage\\removed"
        self.native.add(original, b"retained bytes", security="unusual ordinary DACL")
        before = self.backend.metadata(original)
        self.backend.move(original, retained, before)
        self.assertEqual(self.backend.metadata(original), {"kind": "absent"})
        self.assertEqual(self.backend.metadata(retained), before)
        self.backend.move(retained, original, before)
        self.assertEqual(self.backend.metadata(original), before)

    def test_partial_native_failure_retains_receiptable_object_and_no_auto_restore(self):
        path = "C:\\fixture\\partial.txt"
        self.native.add(path, b"old contents")
        before = self.backend.metadata(path)
        self.native.partial_failure = True
        recorded = []
        with self.assertRaisesRegex(OSError, "partial write"):
            self.backend.write(path, self.incoming, before, contents(b"old contents"), recorded.append)
        self.assertEqual(recorded, [before])
        self.assertEqual(self.backend.metadata(path), before)
        self.assertEqual(self.native.nodes[ntpath.normcase(path)]["data"], b"ned contents")
        self.assertEqual([event[0] for event in self.native.events], ["write"])

    def test_new_user_acl_or_data_and_held_handles_reject_before_write(self):
        path = "C:\\fixture\\guard.txt"
        self.native.add(path, b"old")
        before = self.backend.metadata(path)
        node = self.native.nodes[ntpath.normcase(path)]
        node["security"] = "new user DACL"
        with self.assertRaisesRegex(windows.WindowsError, "metadata drift"):
            self.backend.write(path, self.incoming, before, contents(b"old"), lambda value: None)
        node["security"] = before["security"]
        node["data"] = b"new user content"
        with self.assertRaisesRegex(windows.WindowsError, "content drift"):
            self.backend.write(path, self.incoming, before, contents(b"old"), lambda value: None)
        node["data"] = b"old"
        self.native.blocked.add(ntpath.normcase(path))
        with self.assertRaises(PermissionError):
            self.backend.write(path, self.incoming, before, contents(b"old"), lambda value: None)
        self.assertEqual(self.native.events, [])

    def test_specific_unsupported_metadata_rejects(self):
        path = "C:\\fixture\\unsupported.txt"
        self.native.add(path)
        node = self.native.nodes[ntpath.normcase(path)]
        for flag in (1, 0x200, 0x400, 0x800, 0x1000, 0x4000):
            with self.subTest(flag=flag):
                node["attributes"] = flag
                with self.assertRaisesRegex(windows.WindowsError, "unsupported Windows"):
                    self.backend.metadata(path)
        node["attributes"] = 32
        node["links"] = 2
        with self.assertRaisesRegex(windows.WindowsError, "hardlinks"):
            self.backend.metadata(path)
        node["links"] = 1
        node["streams"] += [":secret:$DATA"]
        with self.assertRaisesRegex(windows.WindowsError, "alternate streams"):
            self.backend.metadata(path)

    def test_reparse_ancestor_and_non_ntfs_reject(self):
        self.native.add("C:\\fixture\\link", directory=True, attributes=16 | 0x400)
        self.native.add("C:\\fixture\\link\\file.txt")
        with self.assertRaisesRegex(windows.WindowsError, "reparse"):
            self.backend.metadata("C:\\fixture\\link\\file.txt")
        self.native.filesystem = "ReFS"
        with self.assertRaisesRegex(windows.WindowsError, "NTFS"):
            self.backend.metadata("C:\\fixture")

    def test_path_namespace_and_device_aliases_are_rejected(self):
        for path in (r"\\server\share\file", r"\\?\C:\file", r"\\.\C:\file", "C:file", r"C:\x\a:stream",
                     r"C:\x\NUL.txt", r"C:\x\COM1", r"C:\x\PROGRA~1", "C:\\x\\file. "):
            with self.subTest(path=path), self.assertRaises(windows.WindowsError):
                windows.lexical(path)
        self.assertEqual(windows.lexical("C:/fixture/文件 with spaces.txt"), "C:\\fixture\\文件 with spaces.txt")

    def test_batch_restore_checks_retained_bytes_before_the_native_move(self):
        for changed in (False, True):
            with self.subTest(changed=changed):
                root = Path(self.temp.name) / str(changed)
                operation, repository = root / "operation", root / "target"
                operation.mkdir(parents=True)
                repository.mkdir()
                retained = operation / "removed-0"
                retained.write_bytes(b"original deletion bytes")
                entry = {"path": "deleted.txt", "before": transfer.evidence.file_state(retained),
                         "after": {"type": "absent"}, "windows_removed": retained.name,
                         "windows_before": {"kind": "file", "security": "unchanged ACL"}}
                if changed:
                    retained.write_bytes(b"later user change")
                native = SimpleNamespace(
                    physical=lambda path: path,
                    metadata=lambda path: {"kind": "file"},
                    move=Mock(side_effect=lambda source, target, expected: source.rename(target)),
                )
                with patch.object(transfer, "os", SimpleNamespace(name="nt")), patch.object(transfer, "windows", return_value=native):
                    if changed:
                        with self.assertRaisesRegex(transfer.TransferError, "retained deletion content drift"):
                            transfer.write_entry(operation, repository, entry, restore=True, record=lambda: None)
                    else:
                        transfer.write_entry(operation, repository, entry, restore=True, record=lambda: None)
                if changed:
                    native.move.assert_not_called()
                    self.assertFalse((repository / "deleted.txt").exists())
                    self.assertEqual(retained.read_bytes(), b"later user change")
                else:
                    native.move.assert_called_once()
                    self.assertEqual((repository / "deleted.txt").read_bytes(), b"original deletion bytes")

    def test_operation_storage_uses_the_private_native_creation_route(self):
        self.backend.private_directory("C:\\storage\\operation")
        self.assertEqual(self.backend.metadata("C:\\storage\\operation")["security"], "private caller/SYSTEM ACL")


@unittest.skipUnless(os.name == "nt", "requires genuine Windows 10/11 local NTFS")
class WindowsNativeTransferTests(unittest.TestCase):
    """These tests call the real DLLs and Git; they are not executed by the Linux contract fixture."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="transfer Windows ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo, self.source = self.root / "target", self.root / "source"
        self.git(self.root, "init", "--quiet", "--initial-branch=main", str(self.repo))
        self.git(self.repo, "config", "user.name", "Windows Transfer Test")
        self.git(self.repo, "config", "user.email", "windows@example.invalid")
        self.git(self.repo, "config", "core.autocrlf", "false")
        for name in ("a.txt", "b.txt", "outside.txt"):
            (self.repo / name).write_bytes(b"base\n")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "--quiet", "-m", "base")
        self.baseline = self.git(self.repo, "rev-parse", "HEAD").decode().strip()
        self.git(self.repo, "worktree", "add", "--quiet", "-b", "task", str(self.source))
        self.operation = self.root / "operation"
        self.native = windows.backend()
        self.assertEqual(self.native.metadata(self.repo)["kind"], "directory")

    def git(self, repository, *args):
        return subprocess.run(["git", "--no-optional-locks", "-C", str(repository), *args],
                              check=True, capture_output=True).stdout

    def prepare(self, changes):
        entries = []
        for name, data in sorted(changes.items()):
            source = self.source / name
            if data is None:
                source.unlink(missing_ok=True)
                output = None
                after = {"type": "absent"}
            else:
                source.write_bytes(data)
                output = str(source)
                after = transfer.evidence.file_state(source)
            entries.append({"path": name, "before": transfer.evidence.file_state(self.repo / name),
                            "after": after, "output": output})
        plan = {"schema": transfer.SCHEMA, "repository": str(self.repo),
                "source": transfer.evidence.snapshot(self.source, sorted(changes)), "baseline": self.baseline,
                "changes": entries, "authority": "accepted fixture transfer", "owner": "fixture"}
        transfer.prepare(plan, self.operation)

    def test_native_create_update_delete_acl_and_complete_git_preservation(self):
        (self.repo / "outside.txt").write_bytes(b"staged\n")
        self.git(self.repo, "add", "outside.txt")
        (self.repo / "outside.txt").write_bytes(b"unstaged\n")
        (self.repo / "private.txt").write_bytes(b"untracked\n")
        owner = subprocess.run(["whoami"], capture_output=True, check=True, text=True).stdout.strip()
        subprocess.run(["icacls", str(self.repo / "a.txt"), "/inheritance:r", "/grant:r", f"{owner}:(F)"],
                       capture_output=True, check=True)
        acl_before = self.native.metadata(self.repo / "a.txt")
        before = transfer.evidence.snapshot(self.repo, inventory=True)
        self.prepare({"a.txt": b"incoming\n", "b.txt": None, "文件 new.txt": b"new\n"})
        result = transfer.apply(self.operation)
        self.assertEqual(result["phase"], "applied")
        self.assertEqual(self.native.metadata(self.repo / "a.txt"), acl_before)
        after = transfer.evidence.snapshot(self.repo, inventory=True)
        self.assertEqual(before["identity"], after["identity"])
        self.assertEqual(before["index"], after["index"])
        self.assertEqual(before["windows"]["administration"], after["windows"]["administration"])
        self.assertEqual(self.git(self.repo, "show", ":outside.txt"), b"staged\n")
        self.assertEqual((self.repo / "outside.txt").read_bytes(), b"unstaged\n")
        self.assertEqual((self.repo / "文件 new.txt").read_bytes(), b"new\n")
        self.assertFalse((self.repo / "b.txt").exists())
        receipt = transfer.load(self.operation)
        removed = next(entry for entry in receipt["entries"] if entry["path"] == "b.txt")
        self.assertEqual(self.native.metadata(self.operation / removed["windows_removed"]), removed["windows_before"])
        with self.assertRaises(transfer.TransferError):
            transfer.recover(self.operation, quiescent=True)

    def test_native_partial_batch_recovery_keeps_custom_security(self):
        before = self.native.metadata(self.repo / "a.txt")
        self.prepare({"a.txt": b"new a\n", "b.txt": b"new b\n"})
        writer = transfer.write_entry
        def fail(operation, repository, entry, **kwargs):
            if entry["path"] == "b.txt":
                raise OSError("native fixture stops second path")
            return writer(operation, repository, entry, **kwargs)
        with patch.object(transfer, "write_entry", side_effect=fail), self.assertRaises(OSError):
            transfer.apply(self.operation)
        self.assertEqual(transfer.recover(self.operation, quiescent=True)["phase"], "restored")
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"base\n")
        self.assertEqual(self.native.metadata(self.repo / "a.txt"), before)

    def test_native_changed_retained_deletion_stays_outside_target(self):
        self.prepare({"a.txt": None, "b.txt": b"later task change\n"})
        writer = transfer.write_entry
        def fail(operation, repository, entry, **kwargs):
            if entry["path"] == "b.txt":
                raise OSError("stop after native deletion")
            return writer(operation, repository, entry, **kwargs)
        with patch.object(transfer, "write_entry", side_effect=fail), self.assertRaises(OSError):
            transfer.apply(self.operation)
        receipt = transfer.load(self.operation)
        deleted = next(entry for entry in receipt["entries"] if entry["path"] == "a.txt")
        retained = self.operation / deleted["windows_removed"]
        retained.write_bytes(b"user edited the retained original\n")
        with self.assertRaisesRegex(transfer.TransferError, "retained deletion content drift"):
            transfer.recover(self.operation, quiescent=True)
        self.assertFalse((self.repo / "a.txt").exists())
        self.assertEqual(retained.read_bytes(), b"user edited the retained original\n")
        self.assertTrue((self.operation / deleted["backup"]).exists())

    def test_native_readonly_ads_and_single_admin_alias_stop_prewrite(self):
        (self.repo / "a.txt").chmod(0o444)
        try:
            with self.assertRaises(OSError):
                self.prepare({"a.txt": b"incoming\n"})
        finally:
            (self.repo / "a.txt").chmod(0o666)
        with (self.repo / "a.txt:extra").open("wb") as stream:
            stream.write(b"alternate stream")
        with self.assertRaises(OSError):
            self.prepare({"a.txt": b"incoming\n"})
        (self.repo / "a.txt:extra").unlink()
        with self.assertRaises(transfer.evidence.EvidenceError):
            transfer.evidence.snapshot(self.repo, [".GIT/config"])
        self.assertFalse(self.operation.exists())

    def test_native_held_handle_and_drift_retain_target(self):
        self.prepare({"a.txt": b"incoming\n"})
        before = (self.repo / "a.txt").read_bytes()
        with self.native.api.open(str(self.repo / "a.txt"), access="data"):
            with self.assertRaises(OSError):
                transfer.apply(self.operation)
        self.assertEqual((self.repo / "a.txt").read_bytes(), before)

    def test_native_actual_partial_write_stays_inflight_with_backup(self):
        self.prepare({"a.txt": b"accepted full result\n", "b.txt": b"later\n"})
        actual = self.native.api.write
        def partial(handle, chunks, attributes):
            actual(handle, [b"partial"], attributes)
            raise OSError("after a real native partial write")
        with patch.object(self.native.api, "write", side_effect=partial), self.assertRaises(OSError):
            transfer.apply(self.operation)
        receipt = transfer.load(self.operation)
        self.assertIsNotNone(receipt["inflight"])
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"partial")
        self.assertTrue((self.operation / "backup-0").exists())
        with self.assertRaises(transfer.TransferError):
            transfer.recover(self.operation, quiescent=True)

    def test_native_later_user_change_is_never_overwritten_by_recovery(self):
        self.prepare({"a.txt": b"new a\n", "b.txt": b"new b\n"})
        writer = transfer.write_entry
        def fail(operation, repository, entry, **kwargs):
            if entry["path"] == "b.txt":
                raise OSError("stop second native path")
            return writer(operation, repository, entry, **kwargs)
        with patch.object(transfer, "write_entry", side_effect=fail), self.assertRaises(OSError):
            transfer.apply(self.operation)
        (self.repo / "a.txt").write_bytes(b"user after failure\n")
        with self.assertRaises((OSError, transfer.TransferError)):
            transfer.recover(self.operation, quiescent=True)
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"user after failure\n")

    def test_native_compatible_overlap_uses_accepted_combined_output(self):
        lines = [f"line {number}\n" for number in range(30)]
        (self.repo / "a.txt").write_text("".join(lines))
        self.git(self.repo, "commit", "--quiet", "-am", "shared text base")
        self.baseline = self.git(self.repo, "rev-parse", "HEAD").decode().strip()
        self.git(self.source, "merge", "--ff-only", self.baseline)
        local, incoming = lines.copy(), lines.copy()
        local[2] = "target user edit\n"
        incoming[25] = "task source edit\n"
        (self.repo / "a.txt").write_text("".join(local))
        (self.source / "a.txt").write_text("".join(incoming))
        ancestor = self.root / "B"
        candidate = self.root / "combined"
        ancestor.write_text("".join(lines))
        candidate.write_bytes(self.git(self.root, "merge-file", "-p", str(self.repo / "a.txt"),
                                       str(ancestor), str(self.source / "a.txt")))
        before = transfer.evidence.snapshot(self.repo, ["a.txt"])
        plan = {"schema": transfer.SCHEMA, "repository": str(self.repo), "baseline": self.baseline,
                "source": transfer.evidence.snapshot(self.source, ["a.txt"]),
                "authority": "accepted compatible merge", "owner": "fixture",
                "changes": [{"path": "a.txt", "before": before["files"]["a.txt"],
                             "after": transfer.evidence.file_state(candidate), "output": str(candidate)}]}
        transfer.prepare(plan, self.operation)
        transfer.apply(self.operation)
        self.assertIn(b"target user edit", (self.repo / "a.txt").read_bytes())
        self.assertIn(b"task source edit", (self.repo / "a.txt").read_bytes())
        self.assertEqual(before["index"], transfer.evidence.snapshot(self.repo)["index"])

    def test_native_batch_git_observation_count_is_size_independent(self):
        counts = []
        for count in (1, 12):
            self.operation = self.root / f"operation-{count}"
            self.prepare({f"new-{i}.txt": str(i).encode() for i in range(count)})
            original = transfer.evidence.git
            calls = []
            def observed(repository, *args):
                calls.append(args[0])
                return original(repository, *args)
            with patch.object(transfer.evidence, "git", side_effect=observed):
                transfer.apply(self.operation)
            self.assertNotIn("status", calls)
            counts.append(calls)
        self.assertEqual(counts[0], counts[1])


if __name__ == "__main__":
    unittest.main()
