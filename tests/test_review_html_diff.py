"""Exercise review capture, rendering, private mapping, and explicit HTTP delivery."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, build_opener


SCRIPT = Path(__file__).resolve().parents[1] / "skills/review-for-humans/scripts/export_html_diff.py"
SPEC = importlib.util.spec_from_file_location("review_html_diff", SCRIPT)
exporter = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = exporter
SPEC.loader.exec_module(exporter)
CACHE_MODULE = "runtime/artifacts/artifact_cache.py"
WEB_MODULE = "runtime/web/web_service.py"


class ReviewHtmlDiffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="review HTML 中文 ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        environment = mock.patch.dict(os.environ, {
            "HOME": str(self.base / "home"), "USERPROFILE": str(self.base / "home"),
            "XDG_CACHE_HOME": str(self.base / "cache [中文] #1%"),
            "XDG_STATE_HOME": str(self.base / "state [中文] #1%"),
            "LOCALAPPDATA": str(self.base / "cache [中文] #1%")})
        environment.start()
        self.addCleanup(environment.stop)
        self.stderr = io.StringIO()
        redirect = contextlib.redirect_stderr(self.stderr)
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)
        self.load_runtime = exporter._runtime
        self.cache = self.load_runtime(CACHE_MODULE)
        self.publication = mock.Mock(side_effect=self.publish_files)

        def runtime(relative: str):
            if relative == WEB_MODULE:
                return types.SimpleNamespace(publish_artifact=self.publication)
            return self.load_runtime(relative)

        runtime_patch = mock.patch.object(exporter, "_runtime", side_effect=runtime)
        runtime_patch.start()
        self.addCleanup(runtime_patch.stop)
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

    def publish_files(self, identity: str, *, port: int = 43123) -> dict:
        artifact = self.cache.mark_published(identity)
        return {name: "http://127.0.0.1:%d/artifacts/%s/%s" % (port, identity, name)
                for name, entry in artifact.files.items() if entry.public}

    def group(self, record: dict) -> Path:
        return Path(record["path"]).parents[2]

    def copy_exporter(self) -> Path:
        target = self.base / "plugin/skills/review-for-humans/scripts/export_html_diff.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SCRIPT, target)
        return target

    def test_cli_capture_is_fixed_and_links_handle_special_characters(self) -> None:
        (self.cache.user_cache_dir() / "smartkit/review-for-humans").mkdir(parents=True)
        # Stop the real subprocess's authenticated service before restoring its
        # environment or removing its private cache/state.
        self.addCleanup(lambda: self.load_runtime(WEB_MODULE).stop_service())
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--input", str(self.batch)],
            cwd=self.base, env=dict(os.environ, PYTHONIOENCODING="ascii"),
            capture_output=True, encoding="ascii", timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)[0]
        self.assertEqual(set(record), {"id", "title", "path", "url", "markdown"})
        self.assertEqual(record["id"], self.entries[0]["id"])
        self.assertEqual(record["title"], self.entries[0]["title"])
        path = Path(record["path"])
        self.assertEqual(self.group(record).parent, self.cache.cache_root())
        original_html = path.read_bytes()
        self.before.write_bytes(b"changed before")
        self.after.write_bytes(b"changed after")
        newer = exporter.export_batch(self.batch)[0]
        self.assertNotEqual(record["path"], newer["path"])
        self.assertEqual((path.parent / "before.txt").read_bytes(), b"timeout = 5\r\n")
        self.assertEqual((path.parent / "after.txt").read_bytes(), b"timeout = 10\n")
        self.assertEqual(path.read_bytes(), original_html)
        mapping = [{"id": record["id"], "title": record["title"], "file": "0001/diff.html"}]
        self.assertEqual(json.loads((path.parents[1] / "manifest.json").read_text()), mapping)
        destination = record["markdown"].rsplit("](", 1)[1][:-1]
        self.assertEqual(destination, record["url"])
        self.assertEqual(urlsplit(destination).hostname, "127.0.0.1")
        self.assertEqual(urlsplit(destination).path, "/artifacts/" + self.group(record).name + "/0001/diff.html")
        self.assertIn(r"\[x\]\*&#95;\`&amp;&lt;", record["markdown"])
        self.assertNotIn(r"\_", record["markdown"])
        opener = build_opener(ProxyHandler({}))
        with opener.open(destination, timeout=2) as response:
            self.assertEqual(response.headers.get_content_type(), "text/html")
            self.assertEqual(response.read(), original_html)
        for private in ("0001/before.txt", "0001/after.txt", "manifest.json"):
            url = destination.rsplit("/0001/diff.html", 1)[0] + "/" + private
            with self.subTest(private=private), self.assertRaises(HTTPError) as error:
                opener.open(url, timeout=2)
            self.assertEqual(error.exception.code, 404)
            error.exception.close()
        self.assertTrue(path.is_absolute())
        self.assertNotIn("id-is-not-a-path", str(path))

    def test_publication_receives_complete_html_and_private_immutable_mapping(self) -> None:
        captured = []

        def publish(identity: str) -> dict:
            artifact = self.cache.load_artifact(identity)
            self.assertFalse(artifact.published)
            self.assertEqual({name for name, entry in artifact.files.items() if entry.public}, {"0001/diff.html"})
            self.assertIn(b"<!doctype html>", self.cache.read_file(artifact.files["0001/diff.html"]))
            self.assertEqual(self.cache.read_file(artifact.files["0001/before.txt"]), self.before.read_bytes())
            self.assertEqual(self.cache.read_file(artifact.files["0001/after.txt"]), self.after.read_bytes())
            manifest = artifact.files["manifest.json"]
            self.assertFalse(manifest.public)
            content = self.cache.read_file(manifest)
            self.assertEqual(json.loads(content), [{"id": self.entries[0]["id"], "title": self.entries[0]["title"],
                                                   "file": "0001/diff.html"}])
            captured.append((manifest, content))
            return self.publish_files(identity)

        self.publication.side_effect = publish
        record = exporter.export_batch(self.batch)[0]
        manifest, original = captured[0]
        self.assertEqual(self.cache.read_file(manifest), original)
        self.assertNotIn(record["url"].encode(), original)

    def test_markdown_title_renders_literal_underscores_and_delimiters(self) -> None:
        markdown = exporter._markdown("_name_/scene_view_[a]*`&<.py", "http://127.0.0.1:43123/artifacts/artifact-x/diff.html")
        self.assertEqual(markdown, r"[&#95;name&#95;/scene&#95;view&#95;\[a\]\*\`&amp;&lt;.py](http://127.0.0.1:43123/artifacts/artifact-x/diff.html)")
        self.assertNotIn(r"\_", markdown)

    def test_links_use_the_current_origin_returned_by_publication(self) -> None:
        for port in (43123, 43124):
            with self.subTest(port=port):
                self.publication.side_effect = lambda identity: self.publish_files(identity, port=port)
                record = exporter.export_batch(self.batch)[0]
                self.assertEqual(urlsplit(record["url"]).port, port)
                self.assertTrue(record["markdown"].endswith("](" + record["url"] + ")"))

    def test_failed_delivery_retains_complete_comparison_and_returns_no_links(self) -> None:
        for failure in (OSError("web service startup failed"), ValueError("publication refused")):
            with self.subTest(failure=str(failure)):
                self.publication.side_effect = failure
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout), self.assertRaises(SystemExit) as result:
                    exporter.main(["--input", str(self.batch)])
                self.assertEqual(result.exception.code, 2)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn(str(failure), self.stderr.getvalue())
        groups = list(self.cache.cache_root().iterdir())
        self.assertEqual(len(groups), 2)
        for group in groups:
            artifact = self.cache.load_artifact(group.name)
            self.assertFalse(artifact.published)
            self.assertEqual(self.cache.read_file(artifact.files["0001/before.txt"]), self.before.read_bytes())
            self.assertTrue(artifact.files["0001/diff.html"].path.is_file())
            self.assertTrue(artifact.files["manifest.json"].path.is_file())
            self.assertIn("cached artifact " + group.name, self.stderr.getvalue())
            self.assertIn(str(group / "files"), self.stderr.getvalue())

    def test_creation_failure_does_not_publish(self) -> None:
        with mock.patch.object(self.cache, "create_artifact", side_effect=OSError("cache write failed")):
            with self.assertRaisesRegex(OSError, "cache write failed"):
                exporter.export_batch(self.batch)
        self.publication.assert_not_called()

    def test_manifest_failure_does_not_publish_an_incomplete_comparison(self) -> None:
        original = exporter.export_batch(self.batch)[0]
        self.publication.reset_mock()
        write = Path.write_bytes

        def fail_manifest(path: Path, content: bytes) -> int:
            if path.name == "manifest.json":
                raise OSError("manifest disk failure")
            return write(path, content)

        with mock.patch.object(Path, "write_bytes", fail_manifest):
            with self.assertRaisesRegex(OSError, "manifest disk failure"):
                exporter.export_batch(self.batch)
        self.publication.assert_not_called()
        self.assertEqual(list(self.cache.cache_root().iterdir()), [self.group(original)])
        self.assertTrue(Path(original["path"]).is_file())

    def test_missing_shared_cache_fails_without_storage_or_file_links(self) -> None:
        isolated = self.copy_exporter()
        result = subprocess.run([sys.executable, "-B", str(isolated), "--input", str(self.batch)],
                                cwd=self.base, capture_output=True, encoding="utf-8", timeout=10)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn(CACHE_MODULE, result.stderr.replace("\\", "/"))
        self.assertFalse(self.cache.cache_root().exists())

    def test_missing_web_runtime_retains_shared_cache_comparison(self) -> None:
        isolated = self.copy_exporter()
        target = isolated.parents[3] / CACHE_MODULE
        target.parent.mkdir(parents=True)
        shutil.copy2(SCRIPT.parents[3] / CACHE_MODULE, target)
        result = subprocess.run([sys.executable, "-B", str(isolated), "--input", str(self.batch)],
                                cwd=self.base, capture_output=True, encoding="utf-8", timeout=10)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn(WEB_MODULE, result.stderr.replace("\\", "/"))
        group = next(self.cache.cache_root().iterdir())
        self.assertIn("cached artifact " + group.name, result.stderr)
        self.assertEqual((group / "files/0001/before.txt").read_bytes(), self.before.read_bytes())
        self.assertTrue((group / "files/manifest.json").is_file())

    def test_runtime_loading_rejects_foreign_aliases_and_missing_local_files(self) -> None:
        foreign = types.ModuleType("artifact_cache")
        foreign.__file__ = str(self.base / "other-plugin/runtime/artifacts/artifact_cache.py")
        with mock.patch.dict(sys.modules, {"artifact_cache": foreign}):
            with self.assertRaisesRegex(OSError, "another plugin copy"):
                self.load_runtime(CACHE_MODULE)
        isolated = self.copy_exporter()
        with mock.patch.object(exporter, "__file__", str(isolated)):
            with self.assertRaises(FileNotFoundError):
                self.load_runtime(CACHE_MODULE)

    def test_failed_runtime_import_leaves_no_partial_module_alias(self) -> None:
        isolated = self.copy_exporter()
        target = isolated.parents[3] / CACHE_MODULE
        target.parent.mkdir(parents=True)
        target.write_text("raise ImportError('cache dependency unavailable')\n", encoding="utf-8")
        with mock.patch.object(exporter, "__file__", str(isolated)), mock.patch.dict(sys.modules):
            sys.modules.pop("artifact_cache", None)
            with self.assertRaisesRegex(OSError, "cache dependency unavailable"):
                self.load_runtime(CACHE_MODULE)
            self.assertNotIn("artifact_cache", sys.modules)

    def test_relative_inputs_additions_deletions_and_empty_files(self) -> None:
        self.after.write_bytes(b"")
        self.write_batch([
            {"id": "add", "title": "new.txt", "before": None, "after": self.after.name},
            {"id": "delete", "title": "old.txt", "before": self.before.name, "after": None}])
        result = exporter.export_batch(self.batch)
        self.assertEqual([item["id"] for item in result], ["add", "delete"])
        added, deleted = [Path(item["path"]) for item in result]
        self.assertFalse((added.parent / "before.txt").exists())
        self.assertEqual((added.parent / "after.txt").read_bytes(), b"")
        self.assertEqual((deleted.parent / "before.txt").read_bytes(), b"timeout = 5\r\n")
        self.assertFalse((deleted.parent / "after.txt").exists())
        self.assertIn("不存在", added.read_text(encoding="utf-8"))
        self.assertIn("0 字节", added.read_text(encoding="utf-8"))

    def test_invalid_batches_create_nothing(self) -> None:
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
                self.assertFalse(self.cache.cache_root().exists())
        self.batch.write_text('[{"id":"one","id":"two"}]', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON field"):
            exporter.export_batch(self.batch)
        self.publication.assert_not_called()

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
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--input", str(self.batch)],
                                cwd=self.base, capture_output=True, encoding="utf-8", timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn("utf-8", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse(self.cache.cache_root().exists())

    def test_rendering_failure_precedes_shared_cache_creation(self) -> None:
        with mock.patch.object(self.cache, "create_artifact") as create:
            with mock.patch.object(exporter, "render_diff", side_effect=OSError("render failed")):
                with self.assertRaisesRegex(OSError, "render failed"):
                    exporter.export_batch(self.batch)
        create.assert_not_called()
        self.publication.assert_not_called()
        self.assertFalse(self.cache.cache_root().exists())


if __name__ == "__main__":
    unittest.main()
