import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def git(repository, *arguments):
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repository), *arguments],
        check=True, capture_output=True,
    ).stdout


@unittest.skipUnless(os.name == "posix", "POSIX carry semantics including executable files and symlinks")
class NativeCarrySeamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="smartkit-carry-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        self.target = self.root / "carry"
        git(self.root, "init", "--quiet", "--initial-branch=main", str(self.source))
        git(self.source, "config", "user.name", "Carry Test")
        git(self.source, "config", "user.email", "carry@example.invalid")
        git(self.source, "config", "core.autocrlf", "false")
        git(self.source, "config", "core.filemode", "true")
        for name, contents in {
            ".gitignore": b"ignored/\n",
            "layered.txt": b"base\n",
            "binary.bin": b"\0base\xff",
            "old.txt": b"rename me\n",
            "deleted.txt": b"delete me\n",
            "run.sh": b"exit 0\n",
        }.items():
            (self.source / name).write_bytes(contents)
        (self.source / "link").symlink_to("layered.txt")
        git(self.source, "add", ".")
        git(self.source, "commit", "--quiet", "-m", "base")
        self.base = git(self.source, "rev-parse", "HEAD").strip()

        (self.source / "layered.txt").write_bytes(b"staged\n")
        (self.source / "binary.bin").write_bytes(b"\0staged\xff")
        git(self.source, "mv", "old.txt", "renamed.txt")
        (self.source / "run.sh").chmod(0o755)
        git(self.source, "add", "layered.txt", "binary.bin", "run.sh")
        (self.source / "layered.txt").write_bytes(b"working\n")
        (self.source / "binary.bin").write_bytes(b"\0working\xfe")
        (self.source / "deleted.txt").unlink()
        (self.source / "link").unlink()
        (self.source / "link").symlink_to("renamed.txt")
        (self.source / "untracked.txt").write_bytes(b"untracked\n")
        (self.source / "ignored").mkdir()
        (self.source / "ignored/private").write_bytes(b"fixture-only private input\n")

        self.staged_patch = self.root / "staged.patch"
        self.working_patch = self.root / "working.patch"
        options = ("--binary", "--full-index", "--no-ext-diff", "--no-textconv", "--no-renames")
        self.staged_patch.write_bytes(git(self.source, "diff", "--cached", *options))
        self.working_patch.write_bytes(git(self.source, "diff", *options))
        self.carried_modes = {
            name: stat.S_IMODE((self.source / name).stat().st_mode)
            for name in ("layered.txt", "binary.bin", "renamed.txt", "run.sh")
        }
        self.source_before = self.source_state()

    def source_state(self):
        files = {}
        for path in sorted(self.source.rglob("*")):
            if ".git" in path.relative_to(self.source).parts or path.is_dir():
                continue
            files[str(path.relative_to(self.source))] = (
                stat.S_IMODE(path.lstat().st_mode),
                os.readlink(path) if path.is_symlink() else path.read_bytes(),
            )
        return (
            git(self.source, "rev-parse", "HEAD"),
            git(self.source, "symbolic-ref", "HEAD"),
            (self.source / ".git/index").read_bytes(),
            files,
        )

    def create(self):
        git(self.source, "worktree", "add", "--quiet", "-b", "carry", str(self.target), self.base.decode())

    def apply_staged(self):
        git(self.target, "apply", "--index", "--binary", str(self.staged_patch))

    def apply_pending_working_state(self):
        git(self.target, "apply", "--binary", str(self.working_patch))
        shutil.copy2(self.source / "untracked.txt", self.target / "untracked.txt")
        for name, mode in self.carried_modes.items():
            (self.target / name).chmod(mode)

    def assert_preserved_carry(self):
        self.assertEqual(self.source_state(), self.source_before)
        self.assertEqual(git(self.target, "rev-parse", "HEAD").strip(), self.base)
        self.assertEqual(git(self.target, "ls-files", "--stage", "-z"),
                         git(self.source, "ls-files", "--stage", "-z"))
        self.assertEqual(git(self.target, "show", ":layered.txt"), b"staged\n")
        self.assertEqual((self.target / "layered.txt").read_bytes(), b"working\n")
        self.assertEqual(git(self.target, "show", ":binary.bin"), b"\0staged\xff")
        self.assertEqual((self.target / "binary.bin").read_bytes(), b"\0working\xfe")
        self.assertEqual((self.target / "renamed.txt").read_bytes(), b"rename me\n")
        self.assertFalse((self.target / "old.txt").exists())
        self.assertEqual(git(self.target, "show", ":deleted.txt"), b"delete me\n")
        self.assertFalse((self.target / "deleted.txt").exists())
        self.assertEqual(stat.S_IMODE((self.target / "run.sh").stat().st_mode), 0o755)
        self.assertEqual(git(self.target, "show", ":link"), b"layered.txt")
        self.assertEqual(os.readlink(self.target / "link"), "renamed.txt")
        self.assertEqual((self.target / "untracked.txt").read_bytes(), b"untracked\n")
        self.assertEqual(git(self.target, "ls-files", "--others", "--exclude-standard", "-z"),
                         b"untracked.txt\0")
        self.assertFalse((self.target / "ignored").exists())

    def test_same_base_carry_preserves_every_layer_and_source(self):
        self.create()
        self.apply_staged()
        self.apply_pending_working_state()
        self.assert_preserved_carry()

    def test_process_interruption_retains_partial_state_and_resumes_only_pending_layer(self):
        self.create()
        interrupted = subprocess.run(
            [sys.executable, "-c",
             "import os,subprocess,sys; "
             "subprocess.run(['git','--no-optional-locks','-C',sys.argv[1],"
             "'apply','--index','--binary',sys.argv[2]],check=True); os._exit(73)",
             str(self.target), str(self.staged_patch)],
            check=False, capture_output=True,
        )
        self.assertEqual(interrupted.returncode, 73, interrupted.stderr)
        self.assertEqual(self.source_state(), self.source_before)
        self.assertEqual(git(self.target, "ls-files", "--stage", "-z"),
                         git(self.source, "ls-files", "--stage", "-z"))
        self.assertEqual((self.target / "layered.txt").read_bytes(), b"staged\n")
        self.assertTrue((self.target / "deleted.txt").exists())
        self.assertFalse((self.target / "untracked.txt").exists())
        git(self.target, "apply", "--check", "--binary", str(self.working_patch))
        self.apply_pending_working_state()
        self.assert_preserved_carry()

    def test_pending_patch_rejects_a_later_target_edit_without_overwriting_it(self):
        self.create()
        self.apply_staged()
        (self.target / "layered.txt").write_bytes(b"user after interruption\n")
        before_index = git(self.target, "ls-files", "--stage", "-z")
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(self.target), "apply",
             "--check", "--binary", str(self.working_patch)],
            check=False, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.target / "layered.txt").read_bytes(), b"user after interruption\n")
        self.assertEqual(git(self.target, "ls-files", "--stage", "-z"), before_index)
        self.assertEqual(self.source_state(), self.source_before)

    def test_clean_creation_preserves_dirty_source_without_importing_its_changes(self):
        self.create()
        self.assertEqual(git(self.target, "status", "--porcelain=v1"), b"")
        self.assertEqual((self.target / "layered.txt").read_bytes(), b"base\n")
        self.assertFalse((self.target / "untracked.txt").exists())
        self.assertEqual(self.source_state(), self.source_before)


if __name__ == "__main__":
    unittest.main()
