import importlib.util
"""Real batch mechanics in disposable linked worktrees; semantic acceptance is caller-owned."""

import json
import os
import subprocess
import sys
import tempfile
import struct
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/finish-worktree/scripts/worktree_transfer.py"
sys.path.insert(0, str(SCRIPT.parent))
try:
    spec = importlib.util.spec_from_file_location("worktree_transfer", SCRIPT)
    transfer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(transfer)
finally:
    sys.path.pop(0)
evidence = transfer.evidence


def git(repository, *args):
    return subprocess.run(["git", "--no-optional-locks", "-C", str(repository), *args],
                          check=True, capture_output=True).stdout


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux mechanics; native Windows has its own suite")
class TransferTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "target"
        git(self.root, "init", "--quiet", "--initial-branch=main", str(self.repo))
        git(self.repo, "config", "user.name", "Transfer Test")
        git(self.repo, "config", "user.email", "transfer@example.invalid")
        for name in ("a.txt", "b.txt", "outside.txt"):
            (self.repo / name).write_text(f"base {name}\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "--quiet", "-m", "base")
        self.baseline = git(self.repo, "rev-parse", "HEAD").decode().strip()
        self.source = self.root / "source"
        git(self.repo, "worktree", "add", "--quiet", "-b", "task", str(self.source))
        self.operation = self.root / "operation"

    def plan(self, contents, source_contents=None):
        changes = []
        for number, (name, content) in enumerate(sorted(contents.items())):
            incoming = (source_contents or contents)[name]
            source_path = self.source / name
            source_path.parent.mkdir(parents=True, exist_ok=True)
            if incoming is None:
                if source_path.exists():
                    source_path.unlink()
            else:
                source_path.write_bytes(incoming)
            output = None
            after = {"type": "absent"}
            if content is not None:
                output = self.root / f"candidate-{number}"
                output.write_bytes(content)
                before_mode = evidence.file_state(self.repo / name)
                output.chmod(before_mode["mode"] if before_mode["type"] == "file" else 0o644)
                after = evidence.file_state(output)
            changes.append({"path": name, "before": evidence.file_state(self.repo / name),
                            "after": after, "output": str(output) if output else None})
        paths = sorted(contents)
        return {"schema": transfer.SCHEMA, "repository": str(self.repo), "baseline": self.baseline,
                "source": evidence.snapshot(self.source, paths), "changes": changes,
                "authority": "accepted task transfer request", "owner": "task owner"}

    def prepare(self, contents, source_contents=None):
        return transfer.prepare(self.plan(contents, source_contents), self.operation)

    def test_prepare_can_freeze_accepted_source_directly(self):
        plan = self.plan({"a.txt": b"accepted source\n"})
        plan["changes"][0]["output"] = str(self.source / "a.txt")
        plan["changes"][0]["after"] = plan["source"]["files"]["a.txt"]
        transfer.prepare(plan, self.operation)
        receipt = transfer.load(self.operation)
        self.assertEqual((self.operation / receipt["entries"][0]["output"]).read_bytes(), b"accepted source\n")
        self.assertEqual(transfer.apply(self.operation)["phase"], "applied")
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"accepted source\n")

    def test_same_base_create_update_delete_and_staging_preservation(self):
        (self.repo / "outside.txt").write_text("staged outside\n")
        git(self.repo, "add", "outside.txt")
        (self.repo / "outside.txt").write_text("unstaged outside\n")
        (self.repo / "untracked.txt").write_text("private target\n")
        plan = self.plan({"a.txt": b"task a\n", "b.txt": None, "new.txt": b"new task\n"})
        before = evidence.snapshot(self.repo, inventory=True)
        source_before = evidence.snapshot(self.source, inventory=True)
        transfer.prepare(plan, self.operation)
        self.assertEqual(evidence.compare(before), [])
        result = transfer.apply(self.operation)
        self.assertEqual(result["phase"], "applied")
        self.assertTrue(result["boundary_preserved"])
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"task a\n")
        self.assertFalse((self.repo / "b.txt").exists())
        self.assertEqual((self.repo / "new.txt").read_bytes(), b"new task\n")
        after = evidence.snapshot(self.repo, inventory=True)
        self.assertEqual(before["index"], after["index"])
        self.assertEqual(before["identity"], after["identity"])
        self.assertEqual(git(self.repo, "show", ":outside.txt"), b"staged outside\n")
        self.assertEqual((self.repo / "outside.txt").read_bytes(), b"unstaged outside\n")
        self.assertEqual((self.repo / "untracked.txt").read_bytes(), b"private target\n")
        self.assertEqual(evidence.compare(source_before), [])
        receipt = transfer.load(self.operation)
        self.assertEqual((self.operation / receipt["entries"][0]["backup"]).read_bytes(), b"base a.txt\n")

    def test_native_compatible_merge_preserves_staged_and_unstaged_same_path(self):
        lines = [f"line {index}\n" for index in range(40)]
        (self.repo / "a.txt").write_text("".join(lines))
        git(self.repo, "commit", "--quiet", "-am", "shared text base")
        self.baseline = git(self.repo, "rev-parse", "HEAD").decode().strip()
        git(self.source, "merge", "--ff-only", self.baseline)
        staged = lines.copy()
        staged[3] = "target staged\n"
        (self.repo / "a.txt").write_text("".join(staged))
        git(self.repo, "add", "a.txt")
        working = staged.copy()
        working[12] = "target unstaged\n"
        (self.repo / "a.txt").write_text("".join(working))
        source = lines.copy()
        source[30] = "incoming task\n"
        ancestor, local, incoming = [self.root / name for name in ("B", "W", "S")]
        ancestor.write_text("".join(lines))
        local.write_text("".join(working))
        incoming.write_text("".join(source))
        combined = git(self.root, "merge-file", "-p", str(local), str(ancestor), str(incoming))
        before_index = (self.repo / ".git/index").read_bytes()
        self.prepare({"a.txt": combined}, {"a.txt": incoming.read_bytes()})
        transfer.apply(self.operation)
        self.assertEqual((self.repo / "a.txt").read_bytes(), combined)
        self.assertEqual((self.repo / ".git/index").read_bytes(), before_index)
        self.assertEqual(git(self.repo, "show", ":a.txt"), "".join(staged).encode())

    def test_identical_result_performs_no_file_write(self):
        content = (self.repo / "a.txt").read_bytes()
        self.prepare({"a.txt": content})
        with patch.object(transfer, "write_entry", side_effect=AssertionError("unexpected write")):
            self.assertEqual(transfer.apply(self.operation)["phase"], "applied")
        self.assertEqual(transfer.load(self.operation)["entries"][0]["state"], "unchanged")

    def test_prepared_candidate_drift_rejects_before_preparation(self):
        plan = self.plan({"a.txt": b"accepted\n"})
        Path(plan["changes"][0]["output"]).write_bytes(b"different\n")
        before = evidence.snapshot(self.repo, inventory=True)
        with self.assertRaisesRegex(transfer.TransferError, "accepted output drift"):
            transfer.prepare(plan, self.operation)
        self.assertEqual(evidence.compare(before), [])
        self.assertFalse(self.operation.exists())

    def test_source_or_target_drift_stops_before_first_write(self):
        for side in ("source", "target"):
            with self.subTest(side=side):
                self.operation = self.root / f"operation-{side}"
                self.prepare({"a.txt": b"incoming\n"})
                path = (self.source if side == "source" else self.repo) / "a.txt"
                path.write_bytes(b"later user edit\n")
                before = evidence.snapshot(self.repo, inventory=True)
                with self.assertRaisesRegex(transfer.TransferError, "drift"):
                    transfer.apply(self.operation)
                self.assertEqual(evidence.compare(before), [])

    def fail_second_write(self):
        writer = transfer.write_entry
        def fail(operation, repository, entry, restore=False):
            if not restore and entry["path"] == "b.txt":
                raise OSError("injected write rejection")
            return writer(operation, repository, entry, restore)
        with patch.object(transfer, "write_entry", side_effect=fail):
            with self.assertRaisesRegex(OSError, "injected"):
                transfer.apply(self.operation)

    def test_partial_failure_recovery_restores_only_proven_writes(self):
        self.prepare({"a.txt": b"new a\n", "b.txt": b"new b\n"})
        self.fail_second_write()
        receipt = transfer.load(self.operation)
        self.assertEqual(receipt["entries"][0]["state"], "written")
        self.assertIsNone(receipt["inflight"])
        result = transfer.recover(self.operation, quiescent=True)
        self.assertEqual(result["phase"], "restored")
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"base a.txt\n")
        self.assertEqual((self.repo / "b.txt").read_bytes(), b"base b.txt\n")
        self.assertIn("injected", transfer.load(self.operation)["error"])

    def test_recovery_keeps_later_user_edit_and_backup(self):
        self.prepare({"a.txt": b"new a\n", "b.txt": b"new b\n"})
        self.fail_second_write()
        (self.repo / "a.txt").write_bytes(b"user after failure\n")
        with self.assertRaisesRegex(transfer.TransferError, "drift"):
            transfer.recover(self.operation, quiescent=True)
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"user after failure\n")
        self.assertTrue((self.operation / "backup-0").exists())

    def test_drift_during_batch_stops_later_path_without_whole_repo_rescan(self):
        self.prepare({"a.txt": b"new a\n", "b.txt": b"new b\n"})
        writer = transfer.write_entry
        def drift(operation, repository, entry, restore=False):
            writer(operation, repository, entry, restore)
            if entry["path"] == "a.txt":
                (self.repo / "b.txt").write_bytes(b"user changed next path\n")
        with patch.object(transfer, "write_entry", side_effect=drift):
            with self.assertRaisesRegex(transfer.TransferError, "drift"):
                transfer.apply(self.operation)
        self.assertEqual((self.repo / "b.txt").read_bytes(), b"user changed next path\n")
        self.assertEqual(transfer.recover(self.operation, quiescent=True)["phase"], "restored")
        self.assertEqual((self.repo / "b.txt").read_bytes(), b"user changed next path\n")

    def test_interrupted_receipt_requires_observation_and_retains_ambiguous_output(self):
        self.prepare({"a.txt": b"new a\n", "b.txt": b"new b\n"})
        writer = transfer.write_entry
        def interrupted(*args, **kwargs):
            writer(*args, **kwargs)
            raise SystemExit("simulated process interruption after replace")
        with patch.object(transfer, "write_entry", side_effect=interrupted):
            with self.assertRaises(SystemExit):
                transfer.apply(self.operation)
        observation = transfer.inspect(self.operation)
        self.assertEqual(observation["phase"], "applying")
        self.assertEqual(observation["inflight"]["path"], "a.txt")
        self.assertEqual(observation["paths"]["a.txt"], "after")
        with self.assertRaisesRegex(transfer.TransferError, "ambiguous"):
            transfer.recover(self.operation, quiescent=True)
        with self.assertRaisesRegex(transfer.TransferError, "original prepared"):
            transfer.apply(self.operation)
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"new a\n")

    def test_completed_transfer_survives_later_verification_failure(self):
        self.prepare({"a.txt": b"new a\n"})
        transfer.apply(self.operation)
        verification = subprocess.run([sys.executable, "-c", "raise SystemExit(1)"], check=False)
        self.assertEqual(verification.returncode, 1)
        with self.assertRaisesRegex(transfer.TransferError, "does not admit"):
            transfer.recover(self.operation, quiescent=True)
        self.assertEqual(transfer.inspect(self.operation)["phase"], "applied")
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"new a\n")
        self.assertTrue((self.operation / "backup-0").exists())

    def test_boundary_observation_count_is_independent_of_batch_size(self):
        counts = []
        for size in (1, 24):
            self.operation = self.root / f"batch-{size}"
            contents = {f"file-{number:02}.txt": f"content {number}\n".encode() for number in range(size)}
            plan = self.plan(contents)
            actual_git = evidence.git
            calls = []
            actual_state = evidence.file_state
            def counted(repository, *args):
                calls.append(args[0])
                return actual_git(repository, *args)
            def bounded(path):
                if Path(path) == self.repo / "outside.txt":
                    raise AssertionError("read unrelated working contents")
                return actual_state(path)
            with patch.object(evidence, "git", side_effect=counted), patch.object(evidence, "file_state", side_effect=bounded):
                transfer.prepare(plan, self.operation)
                transfer.apply(self.operation)
            self.assertNotIn("status", calls)
            counts.append(Counter(calls))
        self.assertEqual(counts[0], counts[1])
        self.assertGreater(counts[0]["rev-parse"], 0)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux-specific admission contract")
    def test_unsupported_mode_and_nonexistent_parent_leave_target_untouched(self):
        plan = self.plan({"a.txt": b"new\n"})
        output = Path(plan["changes"][0]["output"])
        output.chmod(0o4644)
        plan["changes"][0]["after"] = evidence.file_state(output)
        before = evidence.snapshot(self.repo, inventory=True)
        with self.assertRaisesRegex(transfer.TransferError, "unsupported mode"):
            transfer.prepare(plan, self.operation)
        self.assertEqual(evidence.compare(before), [])
        plan = self.plan({"new-directory/file.txt": b"new\n"})
        with self.assertRaisesRegex(transfer.TransferError, "existing real parent"):
            transfer.prepare(plan, self.operation)
        self.assertFalse((self.repo / "new-directory").exists())

    @unittest.skipUnless(os.name == "posix", "POSIX symlinks/hardlinks")
    def test_symlink_and_hardlink_boundaries_reject_before_preparation(self):
        (self.repo / "a.txt").unlink()
        (self.repo / "a.txt").symlink_to(self.root / "unowned")
        plan = self.plan({"a.txt": b"incoming\n"})
        with self.assertRaisesRegex(transfer.TransferError, "regular files|physical path"):
            transfer.prepare(plan, self.operation)
        (self.repo / "a.txt").unlink()
        os.link(self.repo / "b.txt", self.repo / "a.txt")
        plan = self.plan({"a.txt": b"incoming\n"})
        with self.assertRaisesRegex(evidence.EvidenceError, "alias"):
            transfer.prepare(plan, self.operation)
        self.assertFalse(self.operation.exists())

    def test_nested_repository_ancestor_rejects_bounded_batch(self):
        git(self.repo, "init", "--quiet", "nested")
        (self.repo / "nested/file.txt").write_bytes(b"nested user\n")
        plan = self.plan({"nested/file.txt": b"incoming\n"})
        with self.assertRaisesRegex(evidence.EvidenceError, "nested repository"):
            transfer.prepare(plan, self.operation)
        self.assertEqual((self.repo / "nested/file.txt").read_bytes(), b"nested user\n")
        self.assertFalse(self.operation.exists())

    @unittest.skipUnless(os.name == "posix", "requires POSIX transfer backend")
    def test_cli_prepare_apply_inspect_and_refused_recovery(self):
        plan = self.plan({"a.txt": b"cli\n"})
        plan_file = self.root / "plan.json"
        plan_file.write_text(json.dumps(plan))
        launcher = [sys.executable, str(SCRIPT)]
        for command in ("prepare", "apply", "inspect"):
            arguments = [command, "--operation", str(self.operation)]
            if command == "prepare":
                arguments += ["--plan", str(plan_file)]
            result = subprocess.run(launcher + arguments, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("phase", json.loads(result.stdout))
        result = subprocess.run(launcher + ["recover", "--operation", str(self.operation), "--quiescent"], capture_output=True)
        self.assertEqual(result.returncode, 2)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux-specific admission contract")
    def test_unsupported_host_or_missing_metadata_api_rejects_before_operation(self):
        plan = self.plan({"a.txt": b"accepted\n"})
        before = evidence.snapshot(self.repo, inventory=True)
        with patch.object(transfer.sys, "platform", "win32"):
            with self.assertRaisesRegex(transfer.TransferError, "host is unsupported"):
                transfer.prepare(plan, self.operation)
        original = transfer.os.listxattr
        try:
            del transfer.os.listxattr
            with self.assertRaisesRegex(transfer.TransferError, "host is unsupported"):
                transfer.prepare(plan, self.operation)
        finally:
            transfer.os.listxattr = original
        self.assertFalse(self.operation.exists())
        self.assertEqual(evidence.compare(before), [])

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux-specific admission contract")
    def test_canonical_path_alias_rejection_precedes_mutation(self):
        plan = self.plan({"a.txt": b"accepted\n"})
        with patch.object(transfer.os, "readlink", return_value="/different/physical/path"):
            with self.assertRaisesRegex(transfer.TransferError, "physical path alias"):
                transfer.prepare(plan, self.operation)
        self.assertFalse(self.operation.exists())
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"base a.txt\n")

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux-specific admission contract")
    def test_inherited_default_acl_rejects_operation_storage(self):
        plan = self.plan({"a.txt": b"accepted\n"})
        acl = struct.pack("<I", 2) + b"".join(struct.pack("<HHI", tag, permissions, 0xffffffff)
                                             for tag, permissions in ((1, 7), (4, 5), (32, 5)))
        os.setxattr(self.root, "system.posix_acl_default", acl)
        before = evidence.snapshot(self.repo, inventory=True)
        with self.assertRaisesRegex(transfer.TransferError, "directory extended metadata"):
            transfer.prepare(plan, self.operation)
        self.assertFalse(self.operation.exists())
        self.assertEqual(evidence.compare(before), [])

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux-specific admission contract")
    def test_prepared_artifact_metadata_and_hardlinks_stop_before_first_write(self):
        for field, mutation in (("pending", "xattr"), ("output", "xattr"), ("backup", "xattr"), ("pending", "hardlink")):
            with self.subTest(field=field, mutation=mutation):
                self.operation = self.root / f"operation-{field}-{mutation}"
                self.prepare({"a.txt": b"accepted\n"})
                entry = transfer.load(self.operation)["entries"][0]
                artifact = self.operation / entry[field]
                if mutation == "xattr":
                    os.setxattr(artifact, "user.unsupported", b"metadata")
                else:
                    os.link(artifact, self.operation / "alias")
                before = evidence.snapshot(self.repo, inventory=True)
                with self.assertRaisesRegex(transfer.TransferError, "extended attributes|hardlink"):
                    transfer.apply(self.operation)
                self.assertEqual(evidence.compare(before), [])

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux-specific admission contract")
    def test_generated_restore_metadata_never_replaces_target(self):
        self.prepare({"a.txt": b"new a\n", "b.txt": b"new b\n"})
        self.fail_second_write()
        copy = transfer.copy_file
        def changed_copy(source, destination, mode):
            copy(source, destination, mode)
            if destination.name.endswith("-restore"):
                os.setxattr(destination, "user.unsupported", b"metadata")
        with patch.object(transfer, "copy_file", side_effect=changed_copy):
            with self.assertRaisesRegex(transfer.TransferError, "extended attributes"):
                transfer.recover(self.operation, quiescent=True)
        self.assertEqual((self.repo / "a.txt").read_bytes(), b"new a\n")
        self.assertEqual(os.listxattr(self.repo / "a.txt"), [])
        self.assertTrue((self.operation / "backup-0").exists())


@unittest.skipIf(os.name == "nt", "Windows uses its native admission path")
class UnsupportedHostTests(unittest.TestCase):
    def test_unsupported_host_rejects_before_observation_or_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            target = root / "target"
            target.mkdir()
            sentinel = target / "user.txt"
            sentinel.write_bytes(b"preserve user state")
            operation = root / "operation"
            plan = {"schema": transfer.SCHEMA, "repository": str(target)}
            for platform in ("darwin", "freebsd14"):
                with self.subTest(platform=platform), patch.object(transfer.sys, "platform", platform):
                    with patch.object(evidence, "snapshot", side_effect=AssertionError("unexpected Git observation")):
                        with self.assertRaisesRegex(transfer.TransferError, "host is unsupported"):
                            transfer.prepare(plan, operation)
                    self.assertFalse(operation.exists())
                    self.assertEqual(sentinel.read_bytes(), b"preserve user state")
                    self.assertEqual(list(target.iterdir()), [sentinel])


if __name__ == "__main__":
    unittest.main()
