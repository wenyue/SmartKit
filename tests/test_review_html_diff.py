"""Exercise fixed HTML and expiry using isolated temporary user-cache settings."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from typing import Iterator
from unittest import mock
from urllib.parse import unquote


SCRIPT = Path(__file__).resolve().parents[1] / "skills/review-for-humans/scripts/export_html_diff.py"
SPEC = importlib.util.spec_from_file_location("review_html_diff", SCRIPT)
exporter = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = exporter
SPEC.loader.exec_module(exporter)


class ReviewHtmlDiffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="review HTML 中文 ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        environment = mock.patch.dict(os.environ, {
            "HOME": str(self.base / "home"), "USERPROFILE": str(self.base / "home"),
            "XDG_CACHE_HOME": str(self.base / "cache [中文] #1%"),
            "LOCALAPPDATA": str(self.base / "cache [中文] #1%")})
        environment.start()
        self.addCleanup(environment.stop)
        self.stderr = io.StringIO()
        redirect = contextlib.redirect_stderr(self.stderr)
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)
        self.before = self.base / "before.txt"
        self.after = self.base / "after [中文] #1%.txt"
        self.before.write_bytes(b"timeout = 5\r\n")
        self.after.write_bytes(b"timeout = 10\n")
        self.batch = self.base / "batch.json"
        self.entries = [{"id": "../id-is-not-a-path", "title": "src/统计 [x]*_`&<.py",
                         "before": self.before.name, "after": self.after.name}]
        self.write_batch(self.entries)

    def write_batch(self, entries: object) -> None:
        self.batch.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")

    def export_at(self, timestamp: float) -> list:
        with mock.patch.object(exporter.time, "time", return_value=timestamp):
            return exporter.export_batch(self.batch)

    def group(self, record: dict) -> Path:
        return Path(record["path"]).parents[2]

    @contextlib.contextmanager
    def model_windows_reparse(self, path: Path) -> Iterator[None]:
        """Model junction attributes around an actual temp-only redirect on any OS."""
        real_lstat = Path.lstat
        real_is_symlink = Path.is_symlink

        def lstat(selected: Path):
            if selected == path:
                return types.SimpleNamespace(st_mode=stat.S_IFDIR | 0o700,
                                             st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
            return real_lstat(selected)

        def is_symlink(selected: Path) -> bool:
            return False if selected == path else real_is_symlink(selected)

        with mock.patch.object(Path, "lstat", lstat), mock.patch.object(Path, "is_symlink", is_symlink):
            yield

    def test_platform_user_cache_roots_and_relative_environment_fallback(self) -> None:
        home = Path.home().resolve()
        configured = Path(os.environ["XDG_CACHE_HOME"]).resolve()
        for platform, expected in (("linux", configured), ("win32", configured),
                                   ("darwin", home / "Library/Caches")):
            with self.subTest(platform=platform), mock.patch.object(exporter.sys, "platform", platform):
                self.assertEqual(exporter.cache_root(), expected / "smartkit/review-for-humans")
        with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": "relative", "LOCALAPPDATA": "relative"}):
            for platform, expected in (("linux", home / ".cache"), ("win32", home / "AppData/Local")):
                with self.subTest(platform=platform), mock.patch.object(exporter.sys, "platform", platform):
                    self.assertEqual(exporter.cache_root(), expected / "smartkit/review-for-humans")

    def test_cli_capture_is_fixed_and_links_handle_special_characters(self) -> None:
        expired = self.group(self.export_at(1000000.0)[0])
        malformed = exporter.cache_root() / ("review-" + "0" * 32)
        malformed.mkdir()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(self.batch)],
            cwd=self.base, env=dict(os.environ, PYTHONIOENCODING="ascii"),
            capture_output=True, encoding="ascii", timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(expired.exists())
        self.assertTrue(malformed.is_dir())
        self.assertIn("Expired cache removed:", result.stderr)
        self.assertIn("Preserved unrecognized or unsafe cache:", result.stderr)
        record = json.loads(result.stdout)[0]
        path = Path(record["path"])
        self.assertEqual(self.group(record).parent, exporter.cache_root())
        original_html = path.read_bytes()
        self.before.write_bytes(b"changed before")
        self.after.write_bytes(b"changed after")
        newer = exporter.export_batch(self.batch)[0]
        self.assertNotEqual(record["path"], newer["path"])
        self.assertEqual((path.parent / "before.txt").read_bytes(), b"timeout = 5\r\n")
        self.assertEqual((path.parent / "after.txt").read_bytes(), b"timeout = 10\n")
        self.assertEqual(path.read_bytes(), original_html)
        self.assertEqual(json.loads((path.parents[1] / "manifest.json").read_text()), [record])
        destination = record["markdown"].rsplit("(<", 1)[1][:-2]
        self.assertEqual(unquote(destination), path.as_posix())
        self.assertIn(r"\[x\]\*\_\`&amp;&lt;", record["markdown"])
        self.assertTrue(path.is_absolute())
        self.assertNotIn("id-is-not-a-path", str(path))

    def test_relative_inputs_additions_deletions_and_empty_files(self) -> None:
        self.after.write_bytes(b"")
        self.write_batch([
            {"id": "add", "title": "new.txt", "before": None, "after": self.after.name},
            {"id": "delete", "title": "old.txt", "before": self.before.name, "after": None}])
        result = exporter.export_batch(self.batch)
        added, deleted = [Path(item["path"]) for item in result]
        self.assertFalse((added.parent / "before.txt").exists())
        self.assertEqual((added.parent / "after.txt").read_bytes(), b"")
        self.assertEqual((deleted.parent / "before.txt").read_bytes(), b"timeout = 5\r\n")
        self.assertFalse((deleted.parent / "after.txt").exists())
        self.assertIn("不存在", added.read_text(encoding="utf-8"))
        self.assertIn("0 字节", added.read_text(encoding="utf-8"))

    def test_invalid_batches_publish_nothing(self) -> None:
        valid = self.entries[0]
        cases = [None, {}, [], [None], [dict(valid, extra=True)],
                 [dict(valid, id=[])], [dict(valid, title="two\nlines")],
                 [valid, valid], [dict(valid, before=None, after=None)],
                 [dict(valid, after=42)], [dict(valid, after="")],
                 [dict(valid, after="missing.txt")], [dict(valid, after=".")]]
        for entries in cases:
            with self.subTest(entries=entries):
                self.write_batch(entries)
                with self.assertRaises((OSError, ValueError)):
                    exporter.export_batch(self.batch)
                self.assertFalse(exporter.cache_root().exists())
        self.batch.write_text('[{"id":"one","id":"two"}]', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON field"):
            exporter.export_batch(self.batch)

    def test_failed_writes_and_publication_preserve_unexpired_exports(self) -> None:
        original = exporter.export_batch(self.batch)[0]
        output = self.group(original)
        files = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
        with mock.patch.object(exporter.uuid, "uuid4", return_value=mock.Mock(hex=output.name[7:])):
            with self.assertRaises(FileExistsError):
                exporter.export_batch(self.batch)
        self.assertEqual({path.relative_to(output): path.read_bytes() for path in output.rglob("*")
                          if path.is_file()}, files)
        for operation in ("write_bytes", "rename"):
            with self.subTest(operation=operation), mock.patch.object(Path, operation, side_effect=OSError("disk failure")):
                with self.assertRaisesRegex(OSError, "disk failure"):
                    exporter.export_batch(self.batch)
            self.assertEqual(list(exporter.cache_root().iterdir()), [output])
        self.assertTrue(Path(original["path"]).is_file())

    def test_html_escapes_content_and_explains_newline_only_changes(self) -> None:
        title = '<img src="x" onerror="bad()"> & report'
        source = b'<script>alert("unsafe")</script>\r\n'
        before = exporter.Comparison("one", title, source, source.rstrip(b"\r\n"))
        page = exporter.render_diff(before)
        self.assertNotIn("<script>", page)
        self.assertNotIn("<img ", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("&lt;img", page)
        self.assertIn("仅换行符或文件末尾换行发生变化", page)
        self.assertIn("CRLF 1", page)
        self.assertIn("有末尾换行", page)
        self.assertIn("无末尾换行", page)
        self.assertNotIn("http://", page)
        self.assertNotIn("https://", page)

    def test_invalid_utf8_cli_returns_error_without_partial_output(self) -> None:
        self.after.write_bytes(b"\xff")
        self.write_batch([dict(self.entries[0], id="first", after=self.before.name), self.entries[0]])
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(self.batch)],
            cwd=self.base, capture_output=True, encoding="utf-8", timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn("utf-8", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse(exporter.cache_root().exists())

    def test_exact_seven_day_boundary_ignores_access_and_mtime(self) -> None:
        start = 1000000.25
        old = self.export_at(start)[0]
        old_group = self.group(old)
        old_metadata = (old_group / "files/cache.json").read_bytes()
        for path in [old_group] + list(old_group.rglob("*")):
            os.utime(path, (start + 10 * exporter.RETENTION_SECONDS,) * 2)
        Path(old["path"]).read_bytes()
        recent = self.export_at(start + exporter.RETENTION_SECONDS - 0.01)[0]
        self.assertEqual((old_group / "files/cache.json").read_bytes(), old_metadata)
        for path in [self.group(recent)] + list(self.group(recent).rglob("*")):
            os.utime(path, (0, 0))
        self.export_at(start + exporter.RETENTION_SECONDS)
        self.assertFalse(old_group.exists())
        self.assertTrue(Path(recent["path"]).exists())
        self.assertEqual(len(list(exporter.cache_root().iterdir())), 2)
        self.assertIn("Expired cache removed: " + str(old_group), self.stderr.getvalue())

    @unittest.skipIf(os.name == "nt", "Windows directory privacy uses inherited user-cache ACLs")
    def test_new_namespaces_and_export_directories_are_private_without_chmod(self) -> None:
        record = exporter.export_batch(self.batch)[0]
        root = exporter.cache_root()
        for folder in (root.parent, root, self.group(record), Path(record["path"]).parents[1],
                       Path(record["path"]).parent):
            self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
        root.chmod(0o755)
        root.parent.chmod(0o755)
        exporter.export_batch(self.batch)
        self.assertEqual(root.stat().st_mode & 0o777, 0o755)
        self.assertEqual(root.parent.stat().st_mode & 0o777, 0o755)

    def test_success_timestamp_is_recorded_after_rendering_and_inputs_precede_expiry(self) -> None:
        with mock.patch.object(exporter.time, "time", side_effect=[1000000.0, 1000010.0]):
            record = exporter.export_batch(self.batch)[0]
        group = self.group(record)
        metadata = json.loads((group / "files/cache.json").read_text())
        self.assertEqual(metadata["created_at"], 1000010.0)
        self.after.write_bytes(b"\xff")
        with self.assertRaises(UnicodeDecodeError):
            self.export_at(1000010.0 + exporter.RETENTION_SECONDS)
        self.assertTrue(group.exists())
        self.assertNotIn("Expired cache removed", self.stderr.getvalue())

    def test_foreign_and_malformed_cache_groups_and_legacy_data_are_preserved(self) -> None:
        start = 1000000.0
        groups = []
        mutations = [{"schema": "foreign/v1"}, {"directory": "different"},
                     {"created_at": True}, {"created_at": "yesterday"},
                     {"created_at": float("nan")}, {"created_at": 10 ** 500}]
        for mutation in mutations:
            group = self.group(self.export_at(start)[0])
            marker = group / "files/cache.json"
            metadata = json.loads(marker.read_text())
            metadata.update(mutation)
            marker.write_text(json.dumps(metadata), encoding="utf-8")
            groups.append(group)
        for name in ("cache.json", "manifest.json"):
            group = self.group(self.export_at(start)[0])
            (group / "files" / name).write_bytes(b"not json")
            groups.append(group)
        group = self.group(self.export_at(start)[0])
        (group / "unrelated.txt").write_text("preserve", encoding="utf-8")
        groups.append(group)
        root = exporter.cache_root()
        foreign = root / "foreign"
        foreign.mkdir()
        (foreign / "report.txt").write_bytes(b"foreign bytes")
        legacy = Path.home() / ".local/share/smartkit/deep-links"
        legacy.mkdir(parents=True)
        (legacy / "snapshot.txt").write_bytes(b"legacy bytes")
        self.export_at(start + exporter.RETENTION_SECONDS)
        self.assertTrue(all(group.is_dir() for group in groups))
        self.assertEqual((foreign / "report.txt").read_bytes(), b"foreign bytes")
        self.assertEqual((legacy / "snapshot.txt").read_bytes(), b"legacy bytes")
        self.assertNotIn("Expired cache removed", self.stderr.getvalue())

    def test_symlinks_and_namespace_redirects_are_preserved(self) -> None:
        start = 1000000.0
        record = self.export_at(start)[0]
        group = self.group(record)
        outside = self.base / "outside"
        outside.mkdir()
        sentinel = outside / "keep.txt"
        sentinel.write_bytes(b"outside bytes")
        linked = Path(record["path"]).parent / "before.txt"
        linked.unlink()
        root_link = exporter.cache_root() / ("review-" + "a" * 32)
        try:
            linked.symlink_to(sentinel)
            root_link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        self.export_at(start + exporter.RETENTION_SECONDS)
        self.assertTrue(group.is_dir())
        self.assertTrue(linked.is_symlink())
        self.assertTrue(root_link.is_symlink())
        self.assertEqual(sentinel.read_bytes(), b"outside bytes")
        root = exporter.cache_root()
        shutil.rmtree(root)
        root.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "namespace must not redirect"):
            exporter.export_batch(self.batch)
        self.assertTrue(root.is_symlink())
        self.assertEqual(sentinel.read_bytes(), b"outside bytes")

    def test_cleanup_failure_reports_completed_deletions_and_stops_generation(self) -> None:
        start = 1000000.0
        groups = sorted(self.group(self.export_at(start)[0]) for _ in range(2))
        real_remove = shutil.rmtree

        def fail_second(path, *args, **kwargs):
            if Path(path) == groups[1]:
                (groups[1] / "files/0001/before.txt").unlink()
                raise PermissionError("injected removal failure")
            return real_remove(path, *args, **kwargs)

        with mock.patch.object(exporter.time, "time", return_value=start + exporter.RETENTION_SECONDS):
            with mock.patch.object(exporter.shutil, "rmtree", side_effect=fail_second):
                with self.assertRaises(SystemExit) as failure:
                    exporter.main(["--input", str(self.batch)])
        self.assertEqual(failure.exception.code, 2)
        self.assertFalse(groups[0].exists())
        self.assertTrue(groups[1].is_dir())
        self.assertFalse((groups[1] / "files/0001/before.txt").exists())
        self.assertEqual(list(exporter.cache_root().iterdir()), [groups[1]])
        self.assertIn("Expired cache removed: " + str(groups[0]), self.stderr.getvalue())
        self.assertIn("some files may already be deleted", self.stderr.getvalue())
        self.assertIn("injected removal failure", self.stderr.getvalue())

    def test_namespace_reparse_redirect_is_rejected_before_traversal(self) -> None:
        root = exporter.cache_root()
        root.parent.mkdir(parents=True)
        outside = self.base / "outside-namespace"
        outside.mkdir()
        sentinel = outside / "keep.txt"
        sentinel.write_bytes(b"outside bytes")
        try:
            root.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("temp redirect creation unavailable")
        with self.model_windows_reparse(root):
            with self.assertRaisesRegex(ValueError, "namespace"):
                exporter.export_batch(self.batch)
        self.assertEqual(list(outside.iterdir()), [sentinel])
        self.assertTrue(root.is_symlink())

    def test_internal_reparse_redirect_preserves_the_whole_expired_group(self) -> None:
        start = 1000000.0
        record = self.export_at(start)[0]
        group = self.group(record)
        folder = Path(record["path"]).parent
        outside = self.base / "outside-snapshot"
        folder.rename(outside)
        try:
            folder.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("temp redirect creation unavailable")
        with self.model_windows_reparse(folder):
            self.export_at(start + exporter.RETENTION_SECONDS)
        self.assertTrue(group.is_dir())
        self.assertTrue(folder.is_symlink())
        self.assertEqual((outside / "before.txt").read_bytes(), b"timeout = 5\r\n")
        self.assertNotIn("Expired cache removed: " + str(group), self.stderr.getvalue())

    def test_explicit_cache_base_can_resolve_a_redirect(self) -> None:
        target = self.base / "selected-cache"
        target.mkdir()
        configured = self.base / "configured-cache"
        try:
            configured.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("temp redirect creation unavailable")
        with mock.patch.object(exporter.sys, "platform", "linux"):
            with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": str(configured)}):
                record = exporter.export_batch(self.batch)[0]
        self.assertEqual(self.group(record).parent, target.resolve() / "smartkit/review-for-humans")

    @unittest.skipUnless(os.name == "nt", "actual junction creation requires Windows")
    def test_actual_windows_junctions_are_preserved(self) -> None:
        root = exporter.cache_root()
        root.parent.mkdir(parents=True)
        outside = self.base / "outside-junction"
        outside.mkdir()
        created = subprocess.run(["cmd", "/c", "mklink", "/J", str(root), str(outside)],
                                 capture_output=True, timeout=10)
        self.assertEqual(created.returncode, 0, created.stderr)
        with self.assertRaisesRegex(ValueError, "namespace"):
            exporter.export_batch(self.batch)
        self.assertEqual(list(outside.iterdir()), [])
        root.rmdir()
        start = 1000000.0
        record = self.export_at(start)[0]
        group = self.group(record)
        folder = Path(record["path"]).parent
        target = outside / "snapshot"
        folder.rename(target)
        created = subprocess.run(["cmd", "/c", "mklink", "/J", str(folder), str(target)],
                                 capture_output=True, timeout=10)
        self.assertEqual(created.returncode, 0, created.stderr)
        self.export_at(start + exporter.RETENTION_SECONDS)
        self.assertTrue(group.is_dir())
        self.assertTrue(folder.is_dir())
        self.assertEqual((target / "before.txt").read_bytes(), b"timeout = 5\r\n")

    def test_export_failure_does_not_undo_expiry_and_leaves_no_new_group(self) -> None:
        start = 1000000.0
        old = self.group(self.export_at(start)[0])
        with mock.patch.object(exporter, "render_diff", side_effect=OSError("render failed")):
            with self.assertRaisesRegex(OSError, "render failed"):
                self.export_at(start + exporter.RETENTION_SECONDS)
        self.assertFalse(old.exists())
        self.assertEqual(list(exporter.cache_root().iterdir()), [])
        self.assertIn("Expired cache removed: " + str(old), self.stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
