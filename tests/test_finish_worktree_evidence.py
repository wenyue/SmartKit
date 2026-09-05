"""Evidence-helper tests and native Git transfer seams, not an automated transfer engine."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/finish-worktree/scripts/worktree_evidence.py"
spec = importlib.util.spec_from_file_location("worktree_evidence", SCRIPT)
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


def git(repository, *args, check=True):
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repository), *args],
        check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


class RepositoryFixture:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "main"
        git(self.root, "init", "--quiet", "--initial-branch=main", str(self.repo))
        git(self.repo, "config", "user.name", "Evidence Test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / "text.txt").write_text("base\n")
        (self.repo / ".gitignore").write_text("ignored/\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "--quiet", "-m", "base")

    def capture(self, *paths):
        return evidence.snapshot(self.repo, list(paths), inventory=not paths)


class EvidenceTests(RepositoryFixture, unittest.TestCase):
    def test_default_is_boundary_only_and_inventory_is_explicit(self):
        actual_git = evidence.git
        calls = []
        def counted(repository, *args):
            calls.append(args[0])
            return actual_git(repository, *args)
        with patch.object(evidence, "git", side_effect=counted):
            observed = evidence.snapshot(self.repo)
            self.assertEqual(observed["files"], {})
            self.assertIsNone(observed["status"])
            self.assertNotIn("status", calls)
            scoped = evidence.snapshot(self.repo, ["text.txt"])
            self.assertEqual(set(scoped["files"]), {"text.txt"})
            self.assertNotIn("status", calls)
            inventory = evidence.snapshot(self.repo, inventory=True)
            self.assertIn("status", calls)
            self.assertIn(".gitignore", inventory["files"])
        old = dict(observed, schema="smartkit.worktree-evidence/v1")
        with self.assertRaisesRegex(evidence.EvidenceError, "schema"):
            evidence.compare(old)

    def test_single_administrative_alias_is_rejected_before_git_observation(self):
        for path in (".GIT", ".Git/config", "folder/.gIt/index", ".git /config"):
            with self.subTest(path=path), patch.object(evidence, "git", side_effect=AssertionError("Git must not run")):
                with self.assertRaisesRegex(evidence.EvidenceError, "outside .git"):
                    evidence.snapshot(self.repo, [path])

    def test_submodule_index_boundary_is_rejected(self):
        head = git(self.repo, "rev-parse", "HEAD").stdout.decode().strip()
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{head},module")
        with self.assertRaisesRegex(evidence.EvidenceError, "submodules"):
            evidence.snapshot(self.repo, ["module/file.txt"])

    def test_dirty_retention_is_read_only_and_records_every_layer(self):
        (self.repo / "text.txt").write_text("staged\n")
        git(self.repo, "add", "text.txt")
        (self.repo / "text.txt").write_text("working\n")
        (self.repo / "untracked\nname.txt").write_text("local\n")
        (self.repo / "ignored").mkdir()
        (self.repo / "ignored/secret").write_text("retained\n")
        index = self.repo / ".git/index"
        index_before = index.read_bytes()
        head_before = git(self.repo, "rev-parse", "HEAD").stdout
        observed = self.capture()
        self.assertEqual(evidence.compare(observed), [])
        self.assertEqual(index.read_bytes(), index_before)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD").stdout, head_before)
        self.assertEqual(git(self.repo, "show", ":text.txt").stdout, b"staged\n")
        self.assertEqual((self.repo / "text.txt").read_bytes(), b"working\n")
        self.assertIn("untracked\nname.txt", observed["files"])
        self.assertIn("ignored/secret", observed["files"])

    def test_compare_detects_content_drift_even_when_status_is_unchanged(self):
        (self.repo / "text.txt").write_text("local one\n")
        observed = self.capture("text.txt")
        (self.repo / "text.txt").write_text("local two\n")
        changed = evidence.compare(observed)
        self.assertIn("files", changed)
        self.assertNotIn("status", changed)

    def test_complete_index_includes_paths_outside_working_scope(self):
        observed = self.capture("absent.txt")
        (self.repo / "text.txt").write_text("staged outside scope\n")
        git(self.repo, "add", "text.txt")
        self.assertIn("index", evidence.compare(observed))
        self.assertEqual(observed["files"]["absent.txt"], {"type": "absent"})

    def test_split_index_dependency_is_captured_without_refresh(self):
        git(self.repo, "update-index", "--split-index")
        observed = self.capture()
        self.assertIsNotNone(observed["index"]["shared_path"])
        self.assertEqual(observed["index"]["shared_state"]["type"], "file")
        self.assertEqual(evidence.compare(observed), [])

    @unittest.skipUnless(os.name == "posix", "POSIX mode and symlink behavior")
    def test_modes_and_symlinks_are_observed_without_following_targets(self):
        outside = self.root / "outside"
        outside.write_text("outside\n")
        (self.repo / "link").symlink_to(outside)
        observed = self.capture("link", "text.txt")
        outside.write_text("changed outside\n")
        self.assertEqual(evidence.compare(observed), [])
        self.assertEqual(observed["files"]["link"]["target"], str(outside))
        (self.repo / "text.txt").chmod(0o755)
        self.assertIn("files", evidence.compare(observed))

    @unittest.skipUnless(os.name == "posix", "requires symlinks")
    def test_symlink_ancestor_cannot_escape_scope(self):
        (self.repo / "outside").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(evidence.EvidenceError, "non-directory path ancestor"):
            self.capture("outside/data")

    def test_detects_drift_between_snapshot_observations(self):
        observe = evidence.observe
        calls = 0

        def changing_observation(*args):
            nonlocal calls
            value = observe(*args)
            calls += 1
            if calls == 1:
                (self.repo / "text.txt").write_text("concurrent edit\n")
            return value

        with patch.object(evidence, "observe", side_effect=changing_observation):
            with self.assertRaisesRegex(evidence.EvidenceError, "between observations"):
                self.capture()

    def test_rejects_nested_repository_and_escaping_path(self):
        git(self.repo, "init", "--quiet", "nested")
        with self.assertRaisesRegex(evidence.EvidenceError, "nested repository"):
            self.capture()
        with self.assertRaises(evidence.EvidenceError):
            self.capture("../outside")

    def test_bounded_paths_reject_nested_repository_ancestors(self):
        index_before = (self.repo / ".git/index").read_bytes()
        for marker in ("directory", "file"):
            nested = self.repo / f"nested-{marker}"
            arguments = ["init", "--quiet"]
            if marker == "file":
                arguments.extend(["--separate-git-dir", str(self.root / "nested-git")])
            git(self.repo, *arguments, str(nested))
            (nested / "file.txt").write_text("nested work\n")
            (nested / "subdir").mkdir()
            (nested / "subdir/child.txt").write_text("nested child\n")
            for suffix in ("file.txt", "subdir", "subdir/child.txt", "subdir/absent.txt"):
                with self.subTest(marker=marker, suffix=suffix):
                    with self.assertRaisesRegex(evidence.EvidenceError, "nested repository"):
                        self.capture(f"{nested.name}/{suffix}")
            self.assertEqual((nested / "file.txt").read_text(), "nested work\n")
        self.assertEqual((self.repo / ".git/index").read_bytes(), index_before)
        self.assertEqual(self.capture("text.txt")["files"]["text.txt"]["type"], "file")

    def test_cli_snapshot_compare_and_invalid_input_exit_codes(self):
        snapshot_file = self.root / "evidence.json"
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "snapshot", "--repository", str(self.repo), "--inventory"],
            capture_output=True, check=True,
        )
        snapshot_file.write_bytes(result.stdout)
        command = [sys.executable, "-B", str(SCRIPT), "compare", "--snapshot", str(snapshot_file)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        (self.repo / "text.txt").write_text("drift\n")
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("files", json.loads(result.stdout)["changed"])
        snapshot_file.write_text("{}")
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)

    @unittest.skipUnless(os.name == "posix", "requires a POSIX shell")
    def test_shell_launcher_collects_and_compares_actual_state(self):
        launcher = SCRIPT.with_suffix(".sh")
        result = subprocess.run(
            ["sh", str(launcher), "snapshot", "--repository", str(self.repo), "--path", "text.txt"],
            capture_output=True, check=True,
        )
        observed = json.loads(result.stdout)
        self.assertEqual(observed, self.capture("text.txt"))
        receipt = self.root / "snapshot.json"
        receipt.write_bytes(result.stdout)
        (self.repo / "text.txt").write_text("changed\n")
        result = subprocess.run(
            ["sh", str(launcher), "compare", "--snapshot", str(receipt)], capture_output=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("files", json.loads(result.stdout)["changed"])

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell runtime unavailable")
    def test_powershell_launcher_runs_actual_helper(self):
        result = subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(SCRIPT.with_suffix(".ps1")), "--help"],
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"snapshot", result.stdout)


class NativeTransferSeamTests(RepositoryFixture, unittest.TestCase):
    # These fixtures exercise the documented native mechanisms; semantic approval remains Agent-owned.
    def setUp(self):
        super().setUp()
        self.lines = [f"line {number}\n" for number in range(40)]
        (self.repo / "text.txt").write_text("".join(self.lines))
        git(self.repo, "commit", "--quiet", "-am", "text baseline")
        self.baseline = git(self.repo, "rev-parse", "HEAD").stdout.decode().strip()
        self.source = self.root / "source"
        git(self.repo, "worktree", "add", "--quiet", "-b", "task", str(self.source))

    def prepared_text(self, incoming):
        ancestor = self.root / "B"
        local = self.root / "W"
        source = self.root / "S"
        ancestor.write_bytes(git(self.repo, "show", f"{self.baseline}:text.txt").stdout)
        local.write_bytes((self.repo / "text.txt").read_bytes())
        source.write_bytes(incoming)
        return git(self.root, "merge-file", "-p", str(local), str(ancestor), str(source), check=False)

    def test_transfer_combines_staged_unstaged_and_source_work_without_index_change(self):
        staged = self.lines.copy()
        staged[2] = "target staged\n"
        (self.repo / "text.txt").write_text("".join(staged))
        git(self.repo, "add", "text.txt")
        working = staged.copy()
        working[10] = "target unstaged\n"
        (self.repo / "text.txt").write_text("".join(working))
        source_staged = self.lines.copy()
        source_staged[25] = "source staged\n"
        (self.source / "text.txt").write_text("".join(source_staged))
        git(self.source, "add", "text.txt")
        source_working = source_staged.copy()
        source_working[35] = "source unstaged\n"
        (self.source / "text.txt").write_text("".join(source_working))
        (self.source / "new.txt").write_text("task untracked\n")
        (self.source / "private.txt").write_text("unrelated source\n")
        before = self.capture()
        source_before = evidence.snapshot(self.source)
        candidate = self.prepared_text((self.source / "text.txt").read_bytes())
        self.assertEqual(candidate.returncode, 0, candidate.stderr)
        self.assertEqual(evidence.compare(before), [])
        (self.repo / "text.txt").write_bytes(candidate.stdout)
        (self.repo / "new.txt").write_bytes((self.source / "new.txt").read_bytes())
        after = self.capture()
        self.assertEqual(before["identity"], after["identity"])
        self.assertEqual(before["index"], after["index"])
        self.assertEqual(git(self.repo, "show", ":text.txt").stdout, "".join(staged).encode())
        for content in (b"target staged", b"target unstaged", b"source staged", b"source unstaged"):
            self.assertIn(content, (self.repo / "text.txt").read_bytes())
        self.assertFalse((self.repo / "private.txt").exists())
        self.assertEqual((self.repo / "new.txt").read_bytes(), b"task untracked\n")
        self.assertEqual(evidence.compare(source_before), [])

    def test_identical_edits_are_present_once(self):
        incoming = self.lines.copy()
        incoming[20] = "shared edit\n"
        (self.repo / "text.txt").write_text("".join(incoming))
        candidate = self.prepared_text("".join(incoming).encode())
        self.assertEqual(candidate.returncode, 0)
        self.assertEqual(candidate.stdout.count(b"shared edit"), 1)

    def test_conflict_is_detected_in_temporary_storage_before_target_write(self):
        local = self.lines.copy()
        local[20] = "target choice\n"
        (self.repo / "text.txt").write_text("".join(local))
        incoming = self.lines.copy()
        incoming[20] = "source choice\n"
        before = self.capture()
        candidate = self.prepared_text("".join(incoming).encode())
        self.assertEqual(candidate.returncode, 1)
        self.assertEqual(evidence.compare(before), [])

    def test_prewrite_drift_and_intervening_recovery_edit_are_detected(self):
        before = self.capture()
        incoming = self.lines.copy()
        incoming[20] = "task\n"
        candidate = self.prepared_text("".join(incoming).encode())
        self.assertEqual(candidate.returncode, 0)
        (self.repo / "text.txt").write_text("user edit before apply\n")
        self.assertIn("files", evidence.compare(before))
        self.assertEqual((self.repo / "text.txt").read_text(), "user edit before apply\n")
        applied = self.capture()
        (self.repo / "text.txt").write_text("user edit after partial application\n")
        self.assertIn("files", evidence.compare(applied))
        self.assertEqual((self.repo / "text.txt").read_text(), "user edit after partial application\n")

    def test_ff_only_integrates_and_divergence_is_effect_free(self):
        (self.source / "task.txt").write_text("task\n")
        git(self.source, "add", "task.txt")
        git(self.source, "commit", "--quiet", "-m", "task")
        delivery = git(self.source, "rev-parse", "HEAD").stdout.decode().strip()
        git(self.repo, "merge", "--ff-only", delivery)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD").stdout.decode().strip(), delivery)
        (self.repo / "target.txt").write_text("target change\n")
        git(self.repo, "add", "target.txt")
        git(self.repo, "commit", "--quiet", "-m", "target advance")
        (self.source / "task.txt").write_text("task advance\n")
        git(self.source, "commit", "--quiet", "-am", "task advance")
        next_delivery = git(self.source, "rev-parse", "HEAD").stdout.decode().strip()
        before = self.capture()
        result = git(self.repo, "merge", "--ff-only", next_delivery, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(evidence.compare(before), [])


if __name__ == "__main__":
    unittest.main()
