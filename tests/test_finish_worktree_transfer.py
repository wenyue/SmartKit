"""Exercise the documented native transfer recipe in disposable repositories."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Optional


def git(repository: Path, *args: str, check: bool = True,
        global_config: Optional[Path] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repository), *args],
        check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=dict(os.environ, GIT_CONFIG_GLOBAL=str(global_config) if global_config else os.devnull,
                 GIT_CONFIG_NOSYSTEM="1"),
    )


class NativeTransferTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.target = self.root / "target"
        git(self.root, "init", "--quiet", "--initial-branch=main", str(self.target))
        git(self.target, "config", "user.name", "Transfer Test")
        git(self.target, "config", "user.email", "transfer@example.invalid")
        git(self.target, "config", "core.autocrlf", "false")
        for name in ("text.txt", "delete.txt", "outside.txt"):
            (self.target / name).write_bytes(b"base\n")
        git(self.target, "add", ".")
        git(self.target, "commit", "--quiet", "-m", "base")
        self.source = self.root / "source"
        git(self.target, "worktree", "add", "--quiet", "-b", "task", str(self.source))
        self.operation = self.root / "operation"
        self.operation.mkdir()
        self.before = self.operation / "before"
        self.after = self.operation / "after"
        self.before.mkdir()
        self.after.mkdir()
        self.patch = self.operation / "transfer.patch"

    def boundary(self) -> tuple:
        shared = git(self.target, "rev-parse", "--shared-index-path").stdout.decode().strip()
        shared_path = self.target / shared if shared else None
        return (git(self.target, "symbolic-ref", "HEAD").stdout,
                git(self.target, "rev-parse", "HEAD").stdout,
                (self.target / ".git/index").read_bytes(),
                shared_path.read_bytes() if shared_path else None)

    def prepare(self, outputs: Dict[str, Optional[bytes]], *,
                global_config: Optional[Path] = None) -> None:
        for name, content in outputs.items():
            current = self.target / name
            if current.exists():
                backup = self.before / name
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(current, backup)
            if content is not None:
                output = self.after / name
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(content)
                if current.exists():
                    output.chmod(current.stat().st_mode & 0o777)
        self.make_patch(global_config=global_config)

    def make_patch(self, *, global_config: Optional[Path] = None) -> None:
        result = git(self.operation, "-c", "diff.noprefix=true", "-c", "core.autocrlf=false", "diff", "--no-index",
                     "--binary", "--no-renames", "--no-ext-diff", "--no-textconv", "--no-color",
                     "--src-prefix=a/", "--dst-prefix=b/", "--", "before", "after", check=False,
                     global_config=global_config)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.patch.write_bytes(result.stdout)

    def apply_patch(self, *, check: bool = True) -> subprocess.CompletedProcess:
        return git(self.target, "-c", "core.autocrlf=false", "apply", "-p2", "--whitespace=nowarn", str(self.patch), check=check)

    def test_binary_add_delete_and_dirty_staging_are_preserved(self) -> None:
        (self.target / "text.txt").write_bytes(b"staged\n")
        (self.target / "outside.txt").write_bytes(b"staged outside\n")
        git(self.target, "add", ".")
        (self.target / "text.txt").write_bytes(b"staged\nworking\n")
        (self.target / "outside.txt").write_bytes(b"unstaged outside\n")
        (self.target / "untracked.txt").write_bytes(b"private\n")
        boundary = self.boundary()
        source = git(self.source, "status", "--porcelain=v1", "-z").stdout
        outputs = {"text.txt": b"staged\nworking\ntask\n", "delete.txt": None,
                   "binary space.bin": bytes(range(256)), "empty.txt": b""}
        self.prepare(outputs)
        git(self.target, "-c", "core.autocrlf=false", "apply", "-p2", "--check", "--whitespace=nowarn", str(self.patch))
        self.apply_patch()
        for name, content in outputs.items():
            if content is None:
                self.assertFalse((self.target / name).exists())
            else:
                self.assertEqual((self.target / name).read_bytes(), content)
        self.assertEqual(self.boundary(), boundary)
        self.assertEqual((self.target / "outside.txt").read_bytes(), b"unstaged outside\n")
        self.assertEqual((self.target / "untracked.txt").read_bytes(), b"private\n")
        self.assertEqual(git(self.source, "status", "--porcelain=v1", "-z").stdout, source)
        self.assertEqual((self.before / "text.txt").read_bytes(), b"staged\nworking\n")
        self.assertEqual((self.before / "delete.txt").read_bytes(), b"base\n")

    def test_native_merge_combines_staged_unstaged_and_incoming_edits(self) -> None:
        base = ["line %s\n" % number for number in range(40)]
        (self.target / "text.txt").write_text("".join(base))
        git(self.target, "commit", "--quiet", "-am", "text baseline")
        staged = base.copy()
        staged[3] = "staged target\n"
        (self.target / "text.txt").write_text("".join(staged))
        git(self.target, "add", "text.txt")
        working = staged.copy()
        working[12] = "unstaged target\n"
        incoming = base.copy()
        incoming[30] = "task result\n"
        paths = [self.operation / name for name in ("W", "B", "S")]
        for path, lines in zip(paths, (working, base, incoming)):
            path.write_bytes("".join(lines).encode())
        (self.target / "text.txt").write_bytes(paths[0].read_bytes())
        merged = git(self.operation, "merge-file", "-p", *map(str, paths)).stdout
        boundary = self.boundary()
        self.prepare({"text.txt": merged})
        self.apply_patch()
        self.assertEqual((self.target / "text.txt").read_bytes(), merged)
        for text in (b"staged target", b"unstaged target", b"task result"):
            self.assertIn(text, merged)
        self.assertEqual(self.boundary(), boundary)

    def test_raw_crlf_and_binary_with_external_autocrlf_input(self) -> None:
        git(self.target, "config", "core.autocrlf", "true")
        (self.target / "text.txt").write_bytes(b"before\r\n")
        outputs = {"text.txt": b"after\r\nextra\r\n", "new.bin": b"\x00\xff\r\n"}
        boundary = self.boundary()
        source = git(self.source, "status", "--porcelain=v1", "-z").stdout
        mode = (self.target / "text.txt").stat().st_mode
        outside_config = self.root / "outside.gitconfig"
        outside_config.write_text("[core]\n\tautocrlf = input\n", encoding="utf-8")
        config = outside_config.read_bytes()
        self.assertEqual(git(self.operation, "config", "--get", "core.autocrlf",
                             global_config=outside_config).stdout.strip(), b"input")
        self.prepare(outputs, global_config=outside_config)
        result = self.apply_patch(check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name, content in outputs.items():
            self.assertEqual((self.target / name).read_bytes(), content)
        self.assertEqual((self.before / "text.txt").read_bytes(), b"before\r\n")
        self.assertEqual((self.target / "text.txt").stat().st_mode, mode)
        self.assertEqual(self.boundary(), boundary)
        self.assertEqual(git(self.source, "status", "--porcelain=v1", "-z").stdout, source)
        self.assertEqual(outside_config.read_bytes(), config)

    def test_working_file_application_still_consults_filters(self) -> None:
        git(self.target, "config", "filter.forbidden.clean", "exit 97")
        git(self.target, "config", "filter.forbidden.required", "true")
        (self.target / ".gitattributes").write_bytes(b"*.txt filter=forbidden\n")
        self.prepare({"text.txt": b"incoming\n"})
        boundary = self.boundary()
        result = git(self.target, "-c", "core.autocrlf=false", "apply", "-p2", "--check",
                     str(self.patch), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.target / "text.txt").read_bytes(), b"base\n")
        self.assertEqual(self.boundary(), boundary)

    def test_direct_byte_write_preserves_mode_and_leaves_failure_backup(self) -> None:
        git(self.target, "config", "filter.forbidden.clean", "exit 97")
        git(self.target, "config", "filter.forbidden.required", "true")
        (self.target / ".gitattributes").write_bytes(b"*.txt filter=forbidden\n")
        path = self.target / "text.txt"
        if os.name != "nt":
            path.chmod(0o600)
        mode = path.stat().st_mode
        self.prepare({"text.txt": b"short\r\n", "delete.txt": None})
        boundary = self.boundary()
        with path.open("r+b") as target:
            self.assertEqual(target.read(), (self.before / "text.txt").read_bytes())
            target.seek(0)
            target.write((self.after / "text.txt").read_bytes())
            target.truncate()
        self.assertEqual(path.read_bytes(), b"short\r\n")
        self.assertEqual(path.stat().st_mode, mode)
        # An interrupted batch retains its partial result; a later edit makes rollback unsafe.
        path.write_bytes(b"later user edit\n")
        self.assertNotEqual(path.read_bytes(), (self.after / "text.txt").read_bytes())
        self.assertEqual((self.before / "text.txt").read_bytes(), b"base\n")
        self.assertEqual((self.target / "delete.txt").read_bytes(), b"base\n")
        self.assertEqual(self.boundary(), boundary)

    def test_split_index_remains_byte_identical(self) -> None:
        git(self.target, "update-index", "--split-index")
        boundary = self.boundary()
        self.prepare({"text.txt": b"incoming\n"})
        self.apply_patch()
        self.assertEqual(self.boundary(), boundary)

    def test_conflicting_later_edit_rejects_without_partial_application(self) -> None:
        self.prepare({"text.txt": b"incoming\n", "delete.txt": None})
        (self.target / "text.txt").write_bytes(b"later user edit\n")
        boundary = self.boundary()
        result = self.apply_patch(check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.target / "text.txt").read_bytes(), b"later user edit\n")
        self.assertEqual((self.target / "delete.txt").read_bytes(), b"base\n")
        self.assertEqual((self.before / "text.txt").read_bytes(), b"base\n")
        self.assertEqual(self.boundary(), boundary)

    def test_patch_check_does_not_replace_whole_file_precondition(self) -> None:
        original = b"".join(("line %s\n" % i).encode() for i in range(30))
        (self.target / "text.txt").write_bytes(original)
        self.prepare({"text.txt": original.replace(b"line 1\n", b"incoming\n")})
        (self.target / "text.txt").write_bytes(original.replace(b"line 25\n", b"later edit\n"))
        git(self.target, "-c", "core.autocrlf=false", "apply", "-p2", "--check", str(self.patch))
        self.assertNotEqual((self.target / "text.txt").read_bytes(),
                            (self.before / "text.txt").read_bytes())

    @unittest.skipIf(os.name == "nt", "POSIX executable-bit behavior")
    def test_executable_mode_change_and_ordinary_modes(self) -> None:
        initial_mode = (self.target / "text.txt").stat().st_mode & 0o777
        self.prepare({"text.txt": b"incoming\n"})
        (self.after / "text.txt").chmod(initial_mode | 0o111)
        self.make_patch()
        self.apply_patch()
        self.assertEqual((self.target / "text.txt").stat().st_mode & 0o777, initial_mode | 0o111)
        self.assertEqual((self.before / "text.txt").stat().st_mode & 0o777, initial_mode)


if __name__ == "__main__":
    unittest.main()
