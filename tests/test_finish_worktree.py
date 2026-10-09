"""Verify the native consolidation sequence and its retained failure state."""

import subprocess
import tempfile
import unittest
from pathlib import Path


def git(repository: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repository), *args], check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class NativeHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "repo"
        git(self.root, "init", "--quiet", "--initial-branch=task", str(self.repo))
        git(self.repo, "config", "user.name", "History Test")
        git(self.repo, "config", "user.email", "history@example.invalid")
        (self.repo / "file.txt").write_bytes(b"base\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "--quiet", "-m", "base")
        self.base = self.oid("HEAD")
        (self.repo / "file.txt").write_bytes(b"one\n")
        git(self.repo, "commit", "--quiet", "-am", "one")
        (self.repo / "file.txt").write_bytes(b"two\n")
        git(self.repo, "commit", "--quiet", "-am", "two")
        self.old = self.oid("HEAD")
        self.tree = self.oid("HEAD^{tree}")
        self.backup = "refs/smartkit/recovery/native-test"
        self.message = self.root / "message.txt"
        self.message.write_text("delivery\n")

    def oid(self, name: str) -> str:
        return git(self.repo, "rev-parse", name).stdout.decode().strip()

    def candidate(self) -> subprocess.CompletedProcess:
        git(self.repo, "update-ref", self.backup, self.old, "")
        git(self.repo, "switch", "--detach", self.old)
        git(self.repo, "reset", "--soft", self.base)
        return git(self.repo, "commit", "--file", str(self.message), check=False)

    def hook(self, contents: str) -> None:
        path = self.repo / ".git/hooks/pre-commit"
        path.write_text("#!/bin/sh\n" + contents)
        path.chmod(0o755)

    def test_normal_hooks_and_same_tree_single_parent(self) -> None:
        self.hook("printf ran > .git/hook-ran\n")
        result = self.candidate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.repo / ".git/hook-ran").exists())
        candidate = self.oid("HEAD")
        self.assertEqual(self.oid("HEAD^{tree}"), self.tree)
        self.assertEqual(git(self.repo, "show", "-s", "--format=%P", "HEAD").stdout.strip(), self.base.encode())
        self.assertEqual(self.oid("refs/heads/task"), self.old)
        git(self.repo, "update-ref", "refs/heads/task", candidate, self.old)
        git(self.repo, "switch", "task")
        self.assertEqual(self.oid("HEAD"), candidate)
        self.assertEqual(self.oid(self.backup), self.old)
        self.assertEqual(git(self.repo, "status", "--porcelain").stdout, b"")

    def test_rejected_hook_retains_original_branch_and_its_edits(self) -> None:
        self.hook("printf 'hook edit\\n' > file.txt\nexit 1\n")
        result = self.candidate()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.oid("refs/heads/task"), self.old)
        self.assertEqual(self.oid(self.backup), self.old)
        self.assertEqual((self.repo / "file.txt").read_bytes(), b"hook edit\n")
        self.assertEqual(git(self.repo, "show", ":file.txt").stdout, b"two\n")

    def test_successful_hook_changing_tree_requires_new_acceptance(self) -> None:
        self.hook("printf 'hook edit\\n' > file.txt\ngit add file.txt\n")
        self.assertEqual(self.candidate().returncode, 0)
        self.assertNotEqual(self.oid("HEAD^{tree}"), self.tree)
        self.assertEqual(self.oid("refs/heads/task"), self.old)
        self.assertEqual(self.oid(self.backup), self.old)

    def test_existing_backup_and_moved_branch_reject_overwrite(self) -> None:
        git(self.repo, "update-ref", self.backup, self.base)
        result = git(self.repo, "update-ref", self.backup, self.old, "", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.oid(self.backup), self.base)
        git(self.repo, "update-ref", "-d", self.backup, self.base)
        self.assertEqual(self.candidate().returncode, 0)
        candidate = self.oid("HEAD")
        git(self.repo, "update-ref", "refs/heads/task", self.base, self.old)
        result = git(self.repo, "update-ref", "refs/heads/task", candidate, self.old, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.oid("refs/heads/task"), self.base)
        self.assertEqual(self.oid("HEAD"), candidate)


if __name__ == "__main__":
    unittest.main()
