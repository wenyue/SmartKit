import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "skills/write-rules-and-skills/scripts/candidate_evidence.py"
SHELL_LAUNCHER = SCRIPT.with_suffix(".sh")
POWERSHELL_LAUNCHER = SCRIPT.with_suffix(".ps1")
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")
POSIX_LAUNCHER_READY = os.name == "posix" and shutil.which("dirname")


def helper_cache_state():
    cache = SCRIPT.parent / "__pycache__"
    if not cache.is_dir():
        return ()
    state = []
    for path in sorted(cache.glob("candidate_evidence.*.pyc")):
        metadata = path.stat()
        state.append(
            (
                path.name,
                metadata.st_size,
                metadata.st_mtime_ns,
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        )
    return tuple(state)


HELPER_CACHE_BEFORE = helper_cache_state()
SPEC = importlib.util.spec_from_file_location("candidate_evidence", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
EVIDENCE = importlib.util.module_from_spec(SPEC)
BYTECODE_SETTING_BEFORE = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    SPEC.loader.exec_module(EVIDENCE)
finally:
    sys.dont_write_bytecode = BYTECODE_SETTING_BEFORE
BYTECODE_SETTING_AFTER = sys.dont_write_bytecode
HELPER_CACHE_AFTER = helper_cache_state()


class CandidateEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "candidate"
        self.root.mkdir()

    def run_helper(self, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *(str(argument) for argument in arguments)],
            check=False,
            capture_output=True,
            text=True,
        )

    def make_python_candidate(
        self, directory: Path, name: str, version_ok: bool, target_exit: int = 0
    ) -> None:
        executable = directory / name
        executable.write_text(
            "#!/bin/sh\n"
            "if [ \"${1-}\" = \"-c\" ]; then\n"
            f"  exit {0 if version_ok else 1}\n"
            "fi\n"
            f"printf '%s\\n' '{name}'\n"
            "printf '%s\\n' \"$@\"\n"
            f"exit {target_exit}\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)

    def launcher_environment(self, executable_root: Path) -> dict[str, str]:
        environment = dict(os.environ)
        environment["PATH"] = str(executable_root)
        return environment

    def provide_posix_launcher_tools(self, executable_root: Path) -> None:
        dirname = shutil.which("dirname")
        self.assertIsNotNone(dirname)
        (executable_root / "dirname").symlink_to(dirname)

    def capture(self, snapshot: Path, *paths: str) -> subprocess.CompletedProcess[str]:
        arguments: list[object] = ["capture", "--root", self.root, "--output", snapshot]
        for path in paths:
            arguments.extend(("--path", path))
        return self.run_helper(*arguments)

    def compare(
        self, snapshot: Path, *allowed_change_paths: str
    ) -> subprocess.CompletedProcess[str]:
        arguments: list[object] = ["compare", "--root", self.root, "--snapshot", snapshot]
        for path in allowed_change_paths:
            arguments.extend(("--allowed-change-path", path))
        return self.run_helper(*arguments)

    def manifest(self, snapshot: Path) -> dict:
        return json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))

    def candidate_digest(self) -> str:
        digest = hashlib.sha256()
        for path in sorted(self.root.rglob("*")):
            relative = path.relative_to(self.root).as_posix().encode()
            digest.update(relative)
            digest.update(b"d" if path.is_dir() else b"f")
            if path.is_file():
                digest.update(path.read_bytes())
        return digest.hexdigest()

    def test_capture_canonicalizes_order_and_fingerprints_missing_entries(self):
        (self.root / "a.txt").write_text("alpha\n", encoding="utf-8")
        (self.root / "b.txt").write_bytes(b"beta\x00")
        first = self.capture(self.base / "snapshot-one", "b.txt", "./a.txt", "a.txt", "missing")
        second = self.capture(self.base / "snapshot-two", "missing", "a.txt", "b.txt")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(
            json.loads(first.stdout)["schema"],
            "smartkit.candidate-evidence-capture-report/v1",
        )
        first_manifest = self.manifest(self.base / "snapshot-one")
        second_manifest = self.manifest(self.base / "snapshot-two")
        self.assertEqual(
            [entry["path"] for entry in first_manifest["entries"]],
            ["a.txt", "b.txt", "missing"],
        )
        self.assertEqual(first_manifest["fingerprint"], second_manifest["fingerprint"])
        self.assertFalse(first_manifest["entries"][2]["present"])
        (self.root / "missing").write_bytes(b"")
        third = self.capture(self.base / "snapshot-three", "a.txt", "b.txt", "missing")
        self.assertEqual(third.returncode, 0, third.stderr)
        third_manifest = self.manifest(self.base / "snapshot-three")
        self.assertNotEqual(first_manifest["fingerprint"], third_manifest["fingerprint"])

    def test_compare_reports_add_modify_delete_and_stable_text_delta(self):
        (self.root / "deleted.txt").write_text("delete me", encoding="utf-8")
        (self.root / "modified.txt").write_text("before", encoding="utf-8")
        snapshot = self.base / "snapshot"
        captured = self.capture(snapshot, "modified.txt", "added.txt", "deleted.txt")
        self.assertEqual(captured.returncode, 0, captured.stderr)
        (self.root / "added.txt").write_text("new", encoding="utf-8")
        (self.root / "deleted.txt").unlink()
        (self.root / "modified.txt").write_text("after", encoding="utf-8")

        first = self.compare(snapshot, "added.txt", "deleted.txt", "modified.txt")
        second = self.compare(snapshot, "modified.txt", "deleted.txt", "added.txt")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertEqual(report["schema"], "smartkit.candidate-evidence-report/v1")
        self.assertEqual(report["path_boundary"], "PASS")
        self.assertEqual(report["changed_paths"], ["added.txt", "deleted.txt", "modified.txt"])
        self.assertEqual(
            report["changed_paths_within_allowed_subset"],
            ["added.txt", "deleted.txt", "modified.txt"],
        )
        self.assertEqual(
            {change["path"]: change["change"] for change in report["changes"]},
            {"added.txt": "added", "deleted.txt": "deleted", "modified.txt": "modified"},
        )
        modified = next(change for change in report["changes"] if change["path"] == "modified.txt")
        self.assertEqual(modified["delta"]["kind"], "text")
        self.assertIn('-"before"\n+"after"\n', modified["delta"]["unified"])
        self.assertFalse(modified["delta"]["before_final_newline"])
        self.assertFalse(modified["delta"]["after_final_newline"])
        changes = {change["path"]: change for change in report["changes"]}
        self.assertIn('+"new"\n', changes["added.txt"]["delta"]["unified"])
        self.assertIn('-"delete me"\n', changes["deleted.txt"]["delta"]["unified"])
        for change in changes.values():
            self.assertFalse(change["delta"]["before_final_newline"])
            self.assertFalse(change["delta"]["after_final_newline"])
        self.assertNotIn("operation_authorization", report)

    def test_path_boundary_violation_has_distinct_exit_and_report(self):
        (self.root / "allowed.txt").write_text("old", encoding="utf-8")
        (self.root / "outside-subset.txt").write_text("old", encoding="utf-8")
        snapshot = self.base / "snapshot"
        self.assertEqual(self.capture(snapshot, "allowed.txt", "outside-subset.txt").returncode, 0)
        (self.root / "allowed.txt").write_text("new", encoding="utf-8")
        (self.root / "outside-subset.txt").write_text("new", encoding="utf-8")

        result = self.compare(snapshot, "allowed.txt")
        self.assertEqual(result.returncode, 3)
        report = json.loads(result.stdout)
        self.assertEqual(report["changed_paths_within_allowed_subset"], ["allowed.txt"])
        self.assertEqual(report["path_boundary"], "VIOLATION")
        self.assertEqual(report["path_boundary_violations"], ["outside-subset.txt"])

    def test_rejects_invalid_candidate_paths_and_allowed_change_subset(self):
        for index, invalid in enumerate(("", "/absolute", "../escape", "a/../escape", ".")):
            with self.subTest(path=invalid):
                result = self.capture(self.base / f"bad-{index}", invalid)
                self.assertEqual(result.returncode, 2)
        (self.root / "known").write_text("value", encoding="utf-8")
        snapshot = self.base / "snapshot"
        self.assertEqual(self.capture(snapshot, "known").returncode, 0)
        result = self.compare(snapshot, "unknown")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_rejects_snapshot_captured_for_a_different_root(self):
        (self.root / "file").write_text("same", encoding="utf-8")
        snapshot = self.base / "snapshot"
        self.assertEqual(self.capture(snapshot, "file").returncode, 0)
        other_root = self.base / "other-candidate"
        other_root.mkdir()
        (other_root / "file").write_text("same", encoding="utf-8")
        result = self.run_helper(
            "compare",
            "--root",
            other_root,
            "--snapshot",
            snapshot,
            "--allowed-change-path",
            "file",
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("different Candidate root", result.stderr)

    def test_rejects_symlink_and_nonregular_entries(self):
        directory = self.root / "directory"
        directory.mkdir()
        self.assertEqual(self.capture(self.base / "directory-snapshot", "directory").returncode, 2)
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks are unavailable")
        target = self.root / "target"
        target.write_text("value", encoding="utf-8")
        link = self.root / "link"
        try:
            link.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"symlink creation is unavailable: {exc}")
        self.assertEqual(self.capture(self.base / "link-snapshot", "link").returncode, 2)

    def test_refuses_existing_or_inside_root_snapshot_output(self):
        (self.root / "file").write_text("value", encoding="utf-8")
        existing = self.base / "existing"
        existing.mkdir()
        self.assertEqual(self.capture(existing, "file").returncode, 2)
        inside = self.root / "snapshot"
        self.assertEqual(self.capture(inside, "file").returncode, 2)
        self.assertFalse(inside.exists())

    def test_capture_and_compare_do_not_mutate_candidate(self):
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "file.txt").write_text("unchanged\n", encoding="utf-8")
        before = self.candidate_digest()
        snapshot = self.base / "snapshot"
        captured = self.capture(snapshot, "nested/file.txt", "missing.txt")
        self.assertEqual(captured.returncode, 0, captured.stderr)
        self.assertEqual(self.candidate_digest(), before)
        compared = self.compare(snapshot)
        self.assertEqual(compared.returncode, 0, compared.stderr)
        self.assertEqual(self.candidate_digest(), before)

    def test_binary_change_reports_bounded_metadata(self):
        path = self.root / "binary.bin"
        path.write_bytes(b"\x00before")
        snapshot = self.base / "snapshot"
        self.assertEqual(self.capture(snapshot, "binary.bin").returncode, 0)
        path.write_bytes(b"\x00after")
        result = self.compare(snapshot, "binary.bin")
        self.assertEqual(result.returncode, 0, result.stderr)
        change = json.loads(result.stdout)["changes"][0]
        self.assertEqual(change["delta"], {"kind": "binary"})
        self.assertEqual(change["before"]["size"], 7)
        self.assertEqual(change["after"]["size"], 6)

    def test_text_delta_preserves_newline_only_and_empty_file_edges(self):
        path = self.root / "text.txt"
        path.write_text("same", encoding="utf-8")
        newline_snapshot = self.base / "newline-snapshot"
        self.assertEqual(self.capture(newline_snapshot, "text.txt").returncode, 0)
        path.write_text("same\n", encoding="utf-8")
        first = self.compare(newline_snapshot, "text.txt")
        second = self.compare(newline_snapshot, "text.txt")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        newline_delta = json.loads(first.stdout)["changes"][0]["delta"]
        self.assertIn('-"same"\n+"same\\n"\n', newline_delta["unified"])
        self.assertFalse(newline_delta["before_final_newline"])
        self.assertTrue(newline_delta["after_final_newline"])

        missing_snapshot = self.base / "missing-snapshot"
        self.assertEqual(self.capture(missing_snapshot, "empty.txt").returncode, 0)
        empty = self.root / "empty.txt"
        empty.write_bytes(b"")
        added = self.compare(missing_snapshot, "empty.txt")
        self.assertEqual(added.returncode, 0, added.stderr)
        added_change = json.loads(added.stdout)["changes"][0]
        self.assertEqual(added_change["change"], "added")
        self.assertFalse(added_change["before"]["present"])
        self.assertTrue(added_change["after"]["present"])
        self.assertEqual(added_change["delta"]["unified"], "")

        empty_snapshot = self.base / "empty-snapshot"
        self.assertEqual(self.capture(empty_snapshot, "empty.txt").returncode, 0)
        empty.unlink()
        deleted = self.compare(empty_snapshot, "empty.txt")
        self.assertEqual(deleted.returncode, 0, deleted.stderr)
        deleted_change = json.loads(deleted.stdout)["changes"][0]
        self.assertEqual(deleted_change["change"], "deleted")
        self.assertTrue(deleted_change["before"]["present"])
        self.assertFalse(deleted_change["after"]["present"])
        self.assertEqual(deleted_change["delta"]["unified"], "")

    def test_text_delta_preserves_lf_crlf_and_mixed_internal_endings(self):
        path = self.root / "endings.txt"
        cases = (
            ("lf-to-crlf", "one\ntwo\n", "one\r\ntwo\r\n"),
            ("crlf-to-lf", "one\r\ntwo\r\n", "one\ntwo\n"),
            ("mixed-internal", "one\r\ntwo\nthree\r", "one\ntwo\r\nthree\r"),
        )
        for name, before, after in cases:
            with self.subTest(name=name):
                path.write_text(before, encoding="utf-8", newline="")
                snapshot = self.base / f"snapshot-{name}"
                self.assertEqual(self.capture(snapshot, "endings.txt").returncode, 0)
                path.write_text(after, encoding="utf-8", newline="")
                first = self.compare(snapshot, "endings.txt")
                second = self.compare(snapshot, "endings.txt")
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(first.stdout, second.stdout)
                delta = json.loads(first.stdout)["changes"][0]["delta"]
                self.assertNotEqual(delta["unified"], "")
                self.assertIn("\\n", delta["unified"])
                self.assertIn("\\r\\n", delta["unified"])

    def test_dynamic_helper_load_preserves_bytecode_setting_and_cache_state(self):
        self.assertEqual(BYTECODE_SETTING_AFTER, BYTECODE_SETTING_BEFORE)
        self.assertEqual(HELPER_CACHE_AFTER, HELPER_CACHE_BEFORE)

    def test_capture_failure_reports_partial_snapshot_for_controller_cleanup(self):
        output = self.base / "partial-snapshot"

        def fail_after_creation(snapshot, _manifest, _values):
            snapshot.mkdir()
            raise OSError("simulated write failure")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(EVIDENCE, "_write_snapshot", side_effect=fail_after_creation):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = EVIDENCE.main(
                    [
                        "capture",
                        "--root",
                        str(self.root),
                        "--output",
                        str(output),
                        "--path",
                        "missing.txt",
                    ]
                )
        self.assertEqual(result, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertTrue(output.exists())
        self.assertIn(str(output), stderr.getvalue())
        self.assertIn("Controller cleanup", stderr.getvalue())

    def test_help_documents_output_schemas_and_exit_statuses(self):
        result = self.run_helper("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        normalized_help = " ".join(result.stdout.split())
        self.assertIn("capture", result.stdout)
        self.assertIn("compare", result.stdout)
        self.assertIn("smartkit.candidate-evidence-capture-report/v1", result.stdout)
        self.assertIn("smartkit.candidate-evidence-report/v1", result.stdout)
        self.assertIn("Exit 0", result.stdout)
        self.assertIn("exit 2", result.stdout)
        self.assertIn("exit 3", result.stdout)
        self.assertIn("not operation authorization", normalized_help)

    @unittest.skipUnless(POSIX_LAUNCHER_READY, "requires POSIX launcher tools")
    def test_shell_launcher_uses_first_compatible_candidate_in_fixed_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            executable_root = Path(temp_dir)
            self.provide_posix_launcher_tools(executable_root)
            self.make_python_candidate(executable_root, "python3", version_ok=False)
            self.make_python_candidate(
                executable_root, "python", version_ok=True, target_exit=7
            )

            result = subprocess.run(
                ("/bin/sh", str(SHELL_LAUNCHER), "capture", "--root", "candidate"),
                check=False,
                capture_output=True,
                text=True,
                env=self.launcher_environment(executable_root),
            )

        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], "python")
        self.assertEqual(result.stdout.splitlines()[1], str(SCRIPT))
        self.assertEqual(result.stdout.splitlines()[2:], ["capture", "--root", "candidate"])

    @unittest.skipUnless(POSIX_LAUNCHER_READY, "requires POSIX launcher tools")
    def test_shell_launcher_fails_once_when_no_candidate_qualifies(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            executable_root = Path(temp_dir)
            self.provide_posix_launcher_tools(executable_root)
            self.make_python_candidate(executable_root, "python3", version_ok=False)
            self.make_python_candidate(executable_root, "python", version_ok=False)

            result = subprocess.run(
                ("/bin/sh", str(SHELL_LAUNCHER), "--help"),
                check=False,
                capture_output=True,
                text=True,
                env=self.launcher_environment(executable_root),
            )

        expected = "ERROR: Python 3.10 or newer is required; checked python3, then python.\n"
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, expected)

    def test_launchers_share_the_bounded_python_discovery_contract(self):
        shell = SHELL_LAUNCHER.read_text(encoding="utf-8")
        powershell = POWERSHELL_LAUNCHER.read_text(encoding="utf-8")
        expected_error = "Python 3.10 or newer is required; checked python3, then python."

        self.assertIn("for python_command in python3 python; do", shell)
        self.assertIn("foreach ($pythonName in @('python3', 'python'))", powershell)
        self.assertIn(expected_error, shell)
        self.assertIn(expected_error, powershell)
        for launcher in (shell, powershell):
            self.assertEqual(launcher.count(expected_error), 1)
            self.assertIn("sys.version_info < (3, 10)", launcher)
            self.assertNotIn("python3.*", launcher)
            self.assertNotIn("uv python find", launcher)
            self.assertNotIn("py -3", launcher)

    @unittest.skipUnless(POWERSHELL and os.name == "posix", "requires PowerShell on POSIX")
    def test_powershell_launcher_uses_first_compatible_candidate_in_fixed_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            executable_root = Path(temp_dir)
            self.make_python_candidate(executable_root, "python3", version_ok=False)
            self.make_python_candidate(
                executable_root, "python", version_ok=True, target_exit=9
            )

            result = subprocess.run(
                (str(POWERSHELL), "-NoProfile", "-File", str(POWERSHELL_LAUNCHER), "compare"),
                check=False,
                capture_output=True,
                text=True,
                env=self.launcher_environment(executable_root),
            )

        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], "python")
        self.assertEqual(result.stdout.splitlines()[1], str(SCRIPT))
        self.assertEqual(result.stdout.splitlines()[2:], ["compare"])

    def test_compare_rejects_snapshot_payload_tampering(self):
        (self.root / "file.txt").write_text("baseline\n", encoding="utf-8")
        snapshot = self.base / "snapshot"
        self.assertEqual(self.capture(snapshot, "file.txt").returncode, 0)
        (snapshot / "payloads/000000.bin").write_text("tampered\n", encoding="utf-8")
        result = self.compare(snapshot, "file.txt")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
