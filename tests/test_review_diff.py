"""Exercise live Git comparisons without link registrations or baseline writes."""
import json
import io
import html
import os
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from html.parser import HTMLParser
import urllib.error
import urllib.parse
import urllib.request
from unittest.mock import Mock, patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_web import ORIGIN, HOST, artifacts, cli, editor_bridge, http_server, service, storage
from local_web.apps import comparisons, diff
from local_web_test_support import isolate_local_web


class DiffFixture:
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="live diff 中文 ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.environment = patch.dict(os.environ, {
            "HOME": str(self.base), "USERPROFILE": str(self.base), "LOCALAPPDATA": str(self.base / "local"),
            "XDG_CACHE_HOME": str(self.base / "cache"), "XDG_STATE_HOME": str(self.base / "state"),
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.repo = self.base / "repo & 中文"
        self.repo.mkdir()
        self.run_git("init")
        self.name = "a_中文 & #.py"
        self.file = self.repo / self.name
        self.file.write_bytes(b"baseline\n")
        self.run_git("add", "--", self.name)
        self.oid = self.run_git("rev-parse", ":" + self.name).decode().strip()
        self.target = diff.Target(self.repo, self.name, "blob:" + self.oid)
        self.file.write_bytes(b"first edit\n")

    def run_git(self, *arguments):
        result = subprocess.run(["git", "-C", str(self.repo)] + list(arguments), capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def entry(self, **extra):
        return dict({"id": "M1", "path": self.name}, **extra)

    def batch(self, *entries, **extra):
        return dict({"repo": str(self.repo), "base": "blob:" + self.oid,
                     "files": list(entries) if entries else [self.entry()]}, **extra)

    @contextmanager
    def editor_dispatch(self, status=0, *, registered=False):
        # Keep real Git subprocesses separate from the mocked editor launch.
        process = Mock()
        process.wait.return_value = status
        editor = SimpleNamespace(Popen=Mock(return_value=process), DEVNULL=subprocess.DEVNULL,
                                 TimeoutExpired=subprocess.TimeoutExpired)
        with patch.object(diff, "find_vscode", return_value=Path("Code.exe")), patch.object(diff, "subprocess", editor), patch.object(editor_bridge, "open_registered_diff", return_value=registered):
            yield editor.Popen

class DiffTests(DiffFixture, unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "requires native Windows consoles")
    def test_git_comparison_runs_without_a_console(self):
        source = '''
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
from local_web.apps import comparisons
run = subprocess.run
def probe_console(command, **options):
    return run([sys.executable, "-c", "import ctypes; print(bool(ctypes.windll.kernel32.GetConsoleWindow()))"],
               **options)
with patch.object(comparisons.subprocess, "run", side_effect=probe_console):
    print(comparisons.git(Path(sys.argv[2]), "rev-parse", "--show-toplevel").decode().strip())
'''
        result = subprocess.run([sys.executable, "-B", "-c", source, str(ROOT / "runtime"), str(self.repo)],
                                capture_output=True, timeout=10, creationflags=subprocess.DETACHED_PROCESS)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), b"False")

    def test_index_context_is_resolved_once_without_mutable_url_state(self):
        with patch.object(service, "ensure_service"):
            result = diff.links(self.batch(base="index"))[0]
        target = diff.target_from_query(result["url"].split("?", 1)[1])
        self.assertEqual(target.base, "blob:" + self.oid)
        self.file.write_bytes(b"later index\n")
        self.run_git("add", "--", self.name)
        self.assertEqual(diff.read_comparison(target).before, b"baseline\n")
        with self.assertRaises(ValueError):
            diff.target_from_query(self.target.query().replace("blob%3A" + self.oid, "index"))

    def test_live_after_and_fixed_index_blob_without_link_storage(self):
        index_before = self.run_git("ls-files", "--stage")
        with patch.object(service, "ensure_service") as ensure:
            links = diff.links(self.batch())
        ensure.assert_called_once_with()
        self.assertNotIn("sig=", links[0]["url"])
        self.assertNotIn("expires", links[0]["url"])
        self.assertIn("&#95;", links[0]["markdown"])
        parsed = diff.target_from_query(links[0]["url"].split("?", 1)[1])
        self.assertEqual(parsed, self.target)
        self.assertEqual(diff.read_comparison(parsed).before, b"baseline\n")
        self.file.write_bytes(b"later edit\n")
        self.run_git("add", "--", self.name)
        current = diff.read_comparison(parsed)
        self.assertEqual(current.before, b"baseline\n")
        self.assertEqual(current.after, b"later edit\n")
        after_index = self.run_git("ls-files", "--stage")
        diff.read_comparison(parsed)
        self.assertEqual(self.run_git("ls-files", "--stage"), after_index)
        self.assertNotEqual(index_before, after_index)
        self.assertFalse(artifacts.cache_root().exists())
        self.assertFalse(storage.state_dir().exists())

    def test_add_delete_empty_and_rename_are_distinct(self):
        self.file.unlink()
        self.assertIsNone(diff.read_comparison(self.target).after)
        self.file.write_bytes(b"")
        self.assertEqual(diff.read_comparison(self.target).after, b"")
        addition = diff.Target(self.repo, self.name, "absent")
        self.assertIsNone(diff.read_comparison(addition).before)
        moved = self.file.with_name("renamed.py")
        self.file.rename(moved)
        self.assertIsNone(diff.read_comparison(self.target).after)
        self.assertEqual(moved.read_bytes(), b"")

    def test_missing_repository_or_object_is_not_an_empty_baseline(self):
        with self.assertRaises(OSError):
            diff.read_comparison(diff.Target(self.repo, self.name, "blob:" + "f" * len(self.oid)))
        missing = diff.Target(self.base / "missing", self.name, self.target.base)
        with self.assertRaises(FileNotFoundError):
            diff.read_comparison(missing)
        remote = diff.Target(missing.repo, missing.path, missing.base, "https://github.com/o/r/pull/1/files")
        with patch.object(diff, "find_vscode") as find:
            value = diff.open_editor(remote)
        find.assert_not_called()
        self.assertEqual(value["url"], remote.url())
        self.assertIn(remote.github.encode(), diff.render_page(remote).content)

    def test_validation_rejects_ambiguous_parameters_and_unsafe_paths(self):
        for fields in ({"repo": str(self.repo), "path": path, "base": self.target.base}
                       for path in ("../outside", "/absolute", "a//b", "a\\b", ".git/config", "x:y")):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                diff.target_from_fields(fields)
        for base in ("HEAD", ":path", "blob:abc", "blob:" + self.oid + ":x"):
            with self.subTest(base=base), self.assertRaises(ValueError):
                diff.target_from_fields({"repo": str(self.repo), "path": self.name, "base": base})
        for query in (self.target.query() + "&path=x", self.target.query() + "&executable=cmd.exe",
                      self.target.query() + "&sig=unwanted", "repo=x&path=x&base="):
            with self.subTest(query=query), self.assertRaises(ValueError):
                diff.target_from_query(query)
        with self.assertRaises(ValueError):
            diff.target_from_fields(dict(repo=str(self.repo), path=self.name, base=self.target.base, github="https://evil.example/"))
        with patch.object(service, "ensure_service") as ensure:
            with self.assertRaises(ValueError):
                diff.links(self.batch(self.entry(), self.entry()))
        ensure.assert_not_called()

    def test_native_commit_metadata_is_fixed_and_confined(self):
        fields = dict(repo=str(self.repo), path=self.name, base=self.target.base,
                      base_commit="a" * 40, base_path="old.py")
        target = diff.target_from_fields(fields)
        self.assertEqual(diff.target_from_query(target.query()), target)
        for change in ({"base_commit": "HEAD"}, {"base_commit": "abc"}, {"base_path": "../old.py"},
                       {"base": "absent"}, {"base": "index"}, {"base": "commit:" + "b" * 40}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                diff.target_from_fields(dict(fields, **change))

    @unittest.skipIf(os.name == "nt", "POSIX symlinks; cache junctions are checked separately")
    def test_symlink_target_cannot_read_outside_the_worktree(self):
        outside = self.base / "private.py"
        outside.write_bytes(b"secret")
        self.file.unlink()
        self.file.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "redirect"):
            diff.read_comparison(self.target)

    def test_html_escapes_content_and_preserves_newline_information(self):
        comparison = diff.Comparison(self.target, b"<script>x</script>\r\n", b"<script>x</script>\n", self.file)
        output = diff.render_diff(comparison).decode("utf-8")
        self.assertIn("&lt;script&gt;", output)
        self.assertNotIn("<script>x", output)
        self.assertIn("仅换行符", output)
        self.assertIn("CRLF 1", output)
        self.assertIn("当前工作区", output)
        with self.assertRaises(UnicodeDecodeError):
            diff.render_diff(diff.Comparison(self.target, b"\xff", b"x", self.file))

    def test_editor_dispatch_uses_real_worktree_and_preserves_temporary_base(self):
        comparison = diff.read_comparison(self.target)
        process = Mock()
        process.wait.return_value = 0
        with patch.object(diff, "read_comparison", return_value=comparison), patch.object(diff, "find_vscode", return_value=Path("Code.exe")), patch.object(diff.subprocess, "Popen", return_value=process) as launch, patch.dict(os.environ, ELECTRON_RUN_AS_NODE="1"):
            value = diff.open_editor(self.target)
        self.assertEqual(value["viewer"], "vscode")
        self.assertNotIn("url", value)
        command = launch.call_args[0][0]
        self.assertEqual(command[:3], ["Code.exe", "--reuse-window", "--diff"])
        self.assertEqual(Path(command[3]).read_bytes(), b"baseline\n")
        self.assertEqual(Path(command[4]), self.file)
        self.assertNotIn("ELECTRON_RUN_AS_NODE", launch.call_args[1]["env"])
        temporary = artifacts.load_artifact(Path(command[3]).parent.parent.name)
        self.assertFalse(temporary.published)
        artifacts.cleanup_expired(temporary.expires_at)
        self.assertFalse(Path(command[3]).exists())

    def test_editor_fallback_on_absence_failure_or_materialization_error(self):
        with patch.object(diff, "find_vscode", return_value=None):
            self.assertEqual(diff.open_editor(self.target)["url"], self.target.url(html_only=True))
        remote = diff.Target(self.repo, self.name, self.target.base, "https://github.com/o/r/pull/1/files#diff-real")
        with patch.object(diff, "find_vscode", return_value=None):
            self.assertEqual(diff.open_editor(remote)["url"], remote.github)
        comparison = diff.read_comparison(self.target)
        with patch.object(diff, "read_comparison", return_value=comparison), patch.object(diff, "find_vscode", return_value=Path("Code.exe")), patch.object(diff.subprocess, "Popen", side_effect=OSError("launcher failed")):
            self.assertEqual(diff.open_editor(self.target)["url"], self.target.url(html_only=True))
        with patch.object(diff, "find_vscode", return_value=Path("Code.exe")), patch.object(artifacts, "create_artifact", side_effect=OSError("cache failed")):
            self.assertEqual(diff.open_editor(self.target)["url"], self.target.url(html_only=True))

    def test_deletion_does_not_recreate_the_worktree_file(self):
        self.file.unlink()
        comparison = diff.read_comparison(self.target)
        process = Mock()
        process.wait.return_value = 0
        with patch.object(diff, "read_comparison", return_value=comparison), patch.object(diff, "find_vscode", return_value=Path("Code.exe")), patch.object(diff.subprocess, "Popen", return_value=process) as launch:
            diff.open_editor(self.target)
        self.assertEqual(Path(launch.call_args[0][0][4]).read_bytes(), b"")
        self.assertFalse(self.file.exists())

    def test_added_file_compares_empty_base_with_real_worktree(self):
        with self.editor_dispatch() as launch, patch.object(artifacts, "create_artifact", wraps=artifacts.create_artifact) as capture:
            result = diff.open_editor(replace(self.target, base="absent"))
        self.assertEqual(result["viewer"], "vscode")
        capture.assert_called_once_with({"before.py": b""})
        command = launch.call_args[0][0]
        self.assertEqual(Path(command[3]).read_bytes(), b"")
        self.assertEqual(Path(command[4]), self.file)

    def test_nonzero_editor_exit_falls_back_and_live_process_is_dispatched(self):
        comparison = diff.read_comparison(self.target)
        process = Mock()
        process.wait.return_value = 2
        with patch.object(diff, "read_comparison", return_value=comparison), patch.object(diff, "find_vscode", return_value=Path("Code.exe")), patch.object(diff.subprocess, "Popen", return_value=process):
            self.assertEqual(diff.open_editor(self.target)["url"], self.target.url(html_only=True))
        process.wait.side_effect = [subprocess.TimeoutExpired("Code.exe", 1), 0]
        with patch.object(diff, "read_comparison", return_value=comparison), patch.object(diff, "find_vscode", return_value=Path("Code.exe")), patch.object(diff.subprocess, "Popen", return_value=process):
            self.assertEqual(diff.open_editor(self.target)["viewer"], "vscode")

    @unittest.skipUnless(os.name == "nt", "requires native Windows junctions")
    def test_windows_worktree_junction_cannot_escape(self):
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "secret.py").write_bytes(b"secret")
        link = self.repo / "linked"
        result = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        try:
            with self.assertRaisesRegex(ValueError, "redirect"):
                diff.read_comparison(diff.Target(self.repo, "linked/secret.py", "absent"))
            self.assertEqual((outside / "secret.py").read_bytes(), b"secret")
        finally:
            link.rmdir()


class BatchInputTests(DiffFixture, unittest.TestCase):
    def test_shared_context_and_file_overrides_preserve_distinct_baselines(self):
        added = self.repo / "added.py"
        added.write_bytes(b"new file\n")
        batch = self.batch(self.entry(), self.entry(id="F2", path="added.py", base="absent", title="New file"))
        with patch.object(service, "ensure_service") as ensure:
            results = diff.links(batch)
        ensure.assert_called_once_with()
        self.assertEqual([result["id"] for result in results], ["M1", "F2"])
        self.assertEqual([result["title"] for result in results], [self.name, "New file"])
        targets = [diff.target_from_query(result["url"].split("?", 1)[1]) for result in results]
        self.assertEqual(diff.read_comparison(targets[0]).before, b"baseline\n")
        self.assertIsNone(diff.read_comparison(targets[1]).before)
        self.assertEqual(diff.read_comparison(targets[1]).after, b"new file\n")
        self.assertTrue(all(set(result) == {"id", "title", "url", "markdown"} for result in results))

    def test_per_file_baseline_without_a_batch_default(self):
        batch = self.batch(self.entry(base="blob:" + self.oid))
        del batch["base"]
        with patch.object(service, "ensure_service"):
            result = diff.links(batch)[0]
        self.assertEqual(diff.target_from_query(result["url"].split("?", 1)[1]), self.target)

    def test_complete_batch_is_validated_before_service_start(self):
        for batch in (
            [], [self.entry()], {}, self.batch(files=[]), self.batch(files={}),
            self.batch(repo="relative"), self.batch(base="HEAD"),
            self.batch(self.entry(base="absent"), base="HEAD"),
            self.batch(self.entry(title=None)), self.batch(self.entry(path="../outside")),
            self.batch(self.entry(github="https://github.com/o/r/pull/1.diff")),
            self.batch(github="https://github.com/o/r/pull/1/files"),
            self.batch(head="f" * 40), self.batch(self.entry(repo=str(self.repo))),
            self.batch(self.entry(github_anchor="diff-observed")),
            self.batch(self.entry(base_path="old.py")),
            {"repo": str(self.repo), "files": [self.entry()]},
            self.batch(self.entry(), self.entry(id="F2", path="other.py", base=None)),
        ):
            with self.subTest(batch=batch), patch.object(service, "ensure_service") as ensure:
                with self.assertRaises(ValueError):
                    diff.links(batch)
                ensure.assert_not_called()

    def test_pr_metadata_generates_files_changed_and_observed_anchor(self):
        pr = {"repository": "Owner/Repo.Name", "number": 507, "head": "f" * 40}
        batch = self.batch(self.entry(), self.entry(id="F2", github_anchor="diff-observedR12-R18"), pr=pr)
        with patch.object(service, "ensure_service"):
            results = diff.links(batch)
        url = "https://github.com/Owner/Repo.Name/pull/507/files"
        expected = [
            url + "#diff-0d3dd6727fedba508a77015e633b5790ffccb390ffb6a760dc2dfc774e1284ec",
            url + "#diff-observedR12-R18",
        ]
        for result, github in zip(results, expected):
            target = diff.target_from_query(result["url"].split("?", 1)[1])
            self.assertEqual(set(result), {"id", "title", "url", "markdown"})
            self.assertEqual(target.github, github)
            self.assertEqual(target.head, pr["head"])
            page = diff.render_page(target)
            self.assertIsNone(page.redirect)
            self.assertIn(github.encode(), page.content)

    def test_default_pr_anchors_match_observed_github_file_fragments(self):
        entries = [
            self.entry(path=".agents/skills/change-set-verification/agents/openai.yaml"),
            self.entry(id="F2", path=".agents/skills/create-icon/agents/openai.yaml"),
        ]
        with patch.object(service, "ensure_service"):
            results = diff.links(self.batch(*entries, pr={"repository": "wenyue/OtakuRoom", "number": 507, "head": "f" * 40}))
        targets = [diff.target_from_query(urllib.parse.urlsplit(result["url"]).query) for result in results]
        self.assertEqual([target.github for target in targets], [
            "https://github.com/wenyue/OtakuRoom/pull/507/files#diff-e7af03f197ac95de06e34b0d00ba3b824ac4af11e8615d30743d2e889a028633",
            "https://github.com/wenyue/OtakuRoom/pull/507/files#diff-1aa4adc2dd7fb91113f483b1d7ac500edb453475dcfd261acfa04632dc5f0cfa",
        ])

    def test_pr_context_is_complete_and_cannot_supply_a_url(self):
        pr = {"repository": "o/r", "number": 507, "head": "f" * 40}
        invalid = [None, {}, dict(pr, url="https://github.com/o/r/pull/507/files")]
        invalid.extend({key: value for key, value in pr.items() if key != missing} for missing in pr)
        invalid.extend(dict(pr, repository=value) for value in (
            "https://github.com/o/r/pull/507.diff", "o", "o/r/extra", "o/..", "o/r#fragment", "o/r?query"))
        invalid.extend(dict(pr, number=value) for value in (0, -1, True, "507", 1.5))
        invalid.extend(dict(pr, head=value) for value in ("HEAD", "abc", None))
        invalid.extend((dict(pr, branch="topic"), dict(pr, source_repository="o/r"),
                        dict(pr, branch=None, source_repository=None),
                        dict(pr, branch="../topic", source_repository="o/r"),
                        dict(pr, branch="topic", source_repository="https://github.com/o/r")))
        for context in invalid:
            with self.subTest(pr=context), patch.object(service, "ensure_service") as ensure:
                with self.assertRaises(ValueError):
                    diff.links(self.batch(pr=context))
                ensure.assert_not_called()
        for anchor in ("#diff-observed", "https://github.com/o/r/pull/507/files#diff-observed", "", "diff-x\n"):
            with self.subTest(anchor=anchor), patch.object(service, "ensure_service") as ensure:
                with self.assertRaises(ValueError):
                    diff.links(self.batch(self.entry(github_anchor=anchor), pr=pr))
                ensure.assert_not_called()

    def test_pr_effective_baselines_must_be_fixed(self):
        pr = {"repository": "o/r", "number": 1, "head": "f" * 40}
        for batch in (self.batch(base="index", pr=pr), self.batch(self.entry(base="index"), pr=pr)):
            with self.subTest(batch=batch), patch.object(service, "ensure_service") as ensure:
                with self.assertRaises(ValueError):
                    diff.links(batch)
                ensure.assert_not_called()
        with patch.object(service, "ensure_service"):
            result = diff.links(self.batch(self.entry(base="blob:" + self.oid), base="index", pr=pr))[0]
        self.assertEqual(diff.target_from_query(result["url"].split("?", 1)[1]).base, "blob:" + self.oid)

    def test_cli_reads_batch_stdin_and_returns_generated_urls(self):
        batch = self.batch(pr={"repository": "o/r", "number": 507, "head": "f" * 40})
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(json.dumps(batch))), patch("sys.stdout", output), patch.object(service, "ensure_service"):
            status = cli.main(["diff", "--input", "-"])
        self.assertEqual(status, 0)
        result = json.loads(output.getvalue())[0]
        self.assertEqual(set(result), {"id", "title", "url", "markdown"})
        self.assertEqual(urllib.parse.urlsplit(result["url"]).netloc, "127.0.0.1:47821")
        self.assertEqual(urllib.parse.urlsplit(result["url"]).path, "/diff")
        self.assertTrue(result["markdown"].endswith("](" + result["url"] + ")"))
        target = diff.target_from_query(urllib.parse.urlsplit(result["url"]).query)
        self.assertEqual(target.github,
                         "https://github.com/o/r/pull/507/files#diff-0d3dd6727fedba508a77015e633b5790ffccb390ffb6a760dc2dfc774e1284ec")


class PrDiffTests(DiffFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.run_git("config", "user.name", "Diff Test")
        self.run_git("config", "user.email", "diff@example.test")
        self.run_git("config", "core.autocrlf", "false")
        self.run_git("commit", "-m", "baseline")
        self.before = self.run_git("rev-parse", "HEAD").decode().strip()
        self.run_git("add", "--", self.name)
        self.run_git("commit", "-m", "reviewed PR")
        self.head = self.run_git("rev-parse", "HEAD").decode().strip()
        self.github = "https://github.com/o/r/pull/1/files"
        self.github_file = self.github + "#diff-0d3dd6727fedba508a77015e633b5790ffccb390ffb6a760dc2dfc774e1284ec"
        self.context = diff.Target(self.repo, self.name, "commit:" + self.before, self.github, self.head)

    def prepare(self, context=None):
        target = context or self.context
        entry = self.entry(path=target.path)
        if target.base_path:
            entry["base_path"] = target.base_path
        if urllib.parse.urlsplit(target.github).fragment:
            entry["github_anchor"] = urllib.parse.urlsplit(target.github).fragment
        pr = {"repository": "o/r", "number": 1, "head": target.head}
        if target.branch:
            pr.update(branch=target.branch, source_repository=target.source_repository)
        batch = self.batch(entry, repo=str(target.repo), base=target.base,
                           pr=pr, view=target.view)
        with patch.object(service, "ensure_service"):
            result = diff.links(batch)[0]
        return diff.target_from_query(result["url"].split("?", 1)[1])

    def linked(self, name):
        path = self.base / name
        self.run_git("worktree", "add", "--detach", str(path), self.head)
        return path

    def test_commit_editor_uses_native_git_uri_without_temporary_files(self):
        target = self.prepare()
        with self.editor_dispatch(registered=True) as launch, patch.object(artifacts, "create_artifact") as capture:
            result = diff.open_editor(target)
            request = editor_bridge.open_registered_diff.call_args[0]
        self.assertEqual(result["viewer"], "vscode")
        capture.assert_not_called()
        launch.assert_not_called()
        self.assertEqual(request[0], self.repo)
        before = urllib.parse.urlsplit(request[1])
        self.assertEqual(before.scheme, "git")
        self.assertEqual(json.loads(urllib.parse.unquote(before.query)), {"path": str(self.file), "ref": self.before})
        self.assertEqual(request[2], self.file)

    def test_commit_without_a_registered_editor_uses_the_retained_blob(self):
        target = self.prepare()
        with self.editor_dispatch() as launch:
            result = diff.open_editor(target)
        self.assertEqual(result["viewer"], "vscode")
        command = launch.call_args[0][0]
        self.assertFalse(command[3].startswith("--file-uri=git:"))
        self.assertEqual(Path(command[3]).read_bytes(), b"baseline\n")
        self.assertEqual(Path(command[4]), self.file)

    def test_registered_linked_checkout_opens_in_its_own_window(self):
        linked = self.linked(self.base / "registered worktree")
        target = self.prepare(replace(self.context, repo=linked, view="worktree"))
        with self.editor_dispatch(registered=True) as launch, patch.object(artifacts, "create_artifact") as capture:
            result = diff.open_editor(target)
            request = editor_bridge.open_registered_diff.call_args[0]
        self.assertEqual(result["viewer"], "vscode")
        self.assertEqual(request[0], linked)
        self.assertEqual(request[2], linked / self.name)
        capture.assert_not_called()
        launch.assert_not_called()

    def test_linked_checkout_uses_fixed_files_without_requiring_editor_repository_detection(self):
        for name in (self.repo / ".worktrees" / "nested review", self.base / "external review"):
            with self.subTest(path=name):
                linked = self.linked(name)
                target = self.prepare(replace(self.context, repo=linked, view="worktree"))
                current = linked / self.name
                current.write_bytes(b"later linked edit\n")
                index = comparisons.git(linked, "ls-files", "--stage")
                with self.editor_dispatch() as launch:
                    result = diff.open_editor(target)
                self.assertEqual(result["viewer"], "vscode")
                launch.assert_called_once()
                command = launch.call_args[0][0]
                self.assertFalse(command[3].startswith("--file-uri=git:"))
                self.assertEqual(Path(command[3]).read_bytes(), b"baseline\n")
                self.assertEqual(Path(command[4]), current)
                self.assertEqual(current.read_bytes(), b"later linked edit\n")
                self.assertEqual(comparisons.git(linked, "ls-files", "--stage"), index)

    def test_index_snapshot_uses_only_a_matching_fixed_commit(self):
        with patch.object(service, "ensure_service"):
            target = diff.target_from_query(urllib.parse.urlsplit(diff.links(self.batch(base="index"))[0]["url"]).query)
        self.assertEqual(target.base_commit, self.head)
        self.file.write_bytes(b"staged snapshot\n")
        self.run_git("add", "--", self.name)
        with patch.object(service, "ensure_service"):
            staged = diff.target_from_query(urllib.parse.urlsplit(diff.links(self.batch(base="index"))[0]["url"]).query)
        self.assertIsNone(staged.base_commit)
        self.file.write_bytes(b"later staged change\n")
        self.run_git("add", "--", self.name)
        self.assertEqual(diff.read_comparison(target).before, b"first edit\n")
        self.assertEqual(diff.read_comparison(staged).before, b"staged snapshot\n")

    def test_native_metadata_mismatch_or_missing_commit_uses_file_comparison(self):
        target = self.prepare()
        for commit in (self.head, "f" * 40):
            with self.subTest(commit=commit), self.editor_dispatch() as launch:
                result = diff.open_editor(replace(target, base_commit=commit))
            self.assertEqual(result["viewer"], "vscode")
            command = launch.call_args[0][0]
            self.assertEqual(Path(command[3]).read_bytes(), b"baseline\n")
            self.assertEqual(Path(command[4]), self.file)
            launch.assert_called_once()

    def test_native_launch_failure_falls_back_to_web_without_relaunch(self):
        target = self.prepare()
        with self.editor_dispatch() as launch, patch.object(artifacts, "create_artifact") as capture:
            editor_bridge.open_registered_diff.side_effect = OSError("sent, result unknown")
            result = diff.open_editor(target)
        self.assertEqual(result["url"], target.github)
        capture.assert_not_called()
        launch.assert_not_called()

    def test_native_deletion_materializes_only_the_absent_current_side(self):
        self.file.unlink()
        target = self.prepare()
        with self.editor_dispatch(registered=True) as launch, patch.object(artifacts, "create_artifact", wraps=artifacts.create_artifact) as capture:
            result = diff.open_editor(target)
            after = editor_bridge.open_registered_diff.call_args[0][2]
        self.assertEqual(result["viewer"], "vscode")
        capture.assert_called_once_with({"after.py": b""})
        self.assertEqual(after.read_bytes(), b"")
        launch.assert_not_called()
        self.assertFalse(self.file.exists())

    def test_textconv_uses_files_without_executing_the_converter(self):
        target = self.prepare()
        (self.repo / ".gitattributes").write_text("*.py diff=custom\n")
        marker = self.repo / "converter-ran"
        script = self.repo / "converter.py"
        script.write_text("from pathlib import Path\nPath(__file__).with_name('converter-ran').touch()\nprint('converted')\n")
        self.run_git("config", "diff.custom.textconv", '"' + Path(sys.executable).as_posix() + '" "' + script.as_posix() + '"')
        with self.editor_dispatch() as launch:
            result = diff.open_editor(target)
        self.assertEqual(result["viewer"], "vscode")
        command = launch.call_args[0][0]
        self.assertEqual(Path(command[3]).read_bytes(), b"baseline\n")
        self.assertFalse(marker.exists())

    def test_replacement_refs_do_not_change_the_fixed_baseline(self):
        target = self.prepare()
        self.run_git("replace", self.before, self.head)
        with self.editor_dispatch() as launch:
            result = diff.open_editor(target)
        self.assertEqual(result["viewer"], "vscode")
        self.assertEqual(Path(launch.call_args[0][0][3]).read_bytes(), b"baseline\n")

    def test_current_checkout_and_commit_baseline_are_bound_without_git_writes(self):
        index = self.run_git("ls-files", "--stage")
        objects = self.run_git("count-objects", "-v")
        target = self.prepare()
        self.assertEqual(target.repo, self.repo.resolve())
        self.assertEqual(target.base, "blob:" + self.oid)
        self.assertEqual(target.base_commit, self.before)
        self.assertEqual(target.head, self.head)
        self.assertEqual(target.view, "worktree")
        self.assertEqual(diff.read_comparison(target).before, b"baseline\n")
        self.assertEqual(self.run_git("ls-files", "--stage"), index)
        self.assertEqual(self.run_git("count-objects", "-v"), objects)

    def test_pr_without_checkout_compares_fixed_sides_without_reading_current_file(self):
        self.run_git("checkout", "--detach", self.before)
        self.assertEqual(self.run_git("cat-file", "-t", self.head).strip(), b"commit")
        target = self.prepare()
        self.assertEqual(target.head, self.head)
        self.assertEqual(target.view, "snapshot")
        self.file.write_bytes(b"unrelated local content\n")
        comparison = diff.read_comparison(target)
        self.assertEqual((comparison.before, comparison.after), (b"baseline\n", b"first edit\n"))
        self.assertIsNone(comparison.worktree_file)
        self.assertIn("固定 PR 快照".encode(), diff.render_page(target, html_only=True).content)
        with self.editor_dispatch() as launch:
            self.assertEqual(diff.open_editor(target)["viewer"], "vscode")
        command = launch.call_args[0][0]
        self.assertEqual(Path(command[3]).read_bytes(), b"baseline\n")
        self.assertEqual(Path(command[4]).read_bytes(), b"first edit\n")
        self.assertNotEqual(Path(command[4]), self.file)
        with patch.object(diff, "find_vscode", return_value=None):
            self.assertEqual(diff.open_editor(target)["url"], target.url(html_only=True))

    def test_linked_detached_checkout_is_found_and_binding_survives_later_commits(self):
        self.run_git("checkout", "--detach", self.before)
        linked = self.linked("linked & checkout")
        target = self.prepare()
        self.assertEqual(target.repo, linked.resolve())
        self.assertEqual(target.head, self.head)
        self.assertEqual(target.view, "worktree")
        file = linked / self.name
        file.write_bytes(b"later committed content\n")
        for args in (("add", "--", self.name), ("commit", "-m", "later local commit")):
            result = subprocess.run(["git", "-C", str(linked)] + list(args), capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
        content = diff.render_page(target, html_only=True).content
        self.assertIn(b"later", content)
        self.assertIn(b"baseline", content)
        self.assertEqual(target.repo, linked.resolve())

    def test_multiple_checkouts_require_explicit_page_selection(self):
        linked = self.linked("other & 'checkout'")
        (linked / self.name).write_bytes(b"different local edit\n")
        target = self.prepare()
        self.assertEqual(target.head, self.head)
        with patch.object(diff, "find_vscode") as find:
            page = diff.render_page(target).content.decode("utf-8")
            response = diff.open_editor(target)
        find.assert_not_called()
        self.assertIn("选择", page)
        self.assertIn("other &amp; &#x27;checkout&#x27;", page)
        self.assertEqual(response["url"], target.url())

        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.urls = []

            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    self.urls.append(dict(attrs)["href"])

        parser = Links()
        parser.feed(diff.render_page(target, html_only=True).content.decode("utf-8"))
        local = [url for url in parser.urls if url.startswith(ORIGIN)]
        self.assertEqual(len(local), 2)
        selected = [diff.target_from_query(url.split("?", 1)[1]) for url in local]
        self.assertEqual({choice.repo for choice in selected}, {self.repo.resolve(), linked.resolve()})
        self.assertTrue(all(choice.view == "worktree" and choice.head == self.head for choice in selected))
        self.assertTrue(all("/diff/html?" in url for url in local))
        self.assertIn(self.github_file, parser.urls)

    def test_rename_uses_before_path_and_new_file_uses_absent_baseline(self):
        renamed = "renamed.py"
        self.file.rename(self.repo / renamed)
        context = replace(self.context, path=renamed, base_path=self.name)
        target = self.prepare(context)
        self.assertEqual(target.base, "blob:" + self.oid)
        self.assertEqual(target.base_commit, self.before)
        self.assertEqual(target.base_path, self.name)
        with self.editor_dispatch(registered=True) as launch:
            self.assertEqual(diff.open_editor(target)["viewer"], "vscode")
            before_uri = urllib.parse.urlsplit(editor_bridge.open_registered_diff.call_args[0][1])
        launch.assert_not_called()
        self.assertEqual(json.loads(urllib.parse.unquote(before_uri.query))["path"], str(self.repo / self.name))
        self.assertEqual(target.github, self.github + "#diff-b1cb4c2fea8f27faabf83123f17e7e992ed88c065ec16deaef2c77891f8da40d")
        self.assertEqual(diff.read_comparison(target).after, b"first edit\n")
        addition = self.repo / "new.py"
        addition.write_bytes(b"new file\n")
        target = self.prepare(replace(self.context, path="new.py"))
        self.assertEqual(target.base, "absent")
        self.assertIsNone(diff.read_comparison(target).before)

    def test_missing_before_commit_or_repository_explains_and_offers_github(self):
        for target in (replace(self.context, base="commit:" + "f" * 40),
                       replace(self.context, repo=self.base / "missing")):
            with self.subTest(target=target):
                prepared = self.prepare(target)
                page = diff.render_page(prepared)
                self.assertIsNone(page.redirect)
                self.assertIn("无法读取比较".encode(), page.content)
                self.assertIn(self.github_file.encode(), page.content)
                self.assertEqual(diff.open_editor(prepared)["url"], prepared.url())

    def source_context(self):
        self.run_git("branch", "-M", "review/target")
        self.run_git("remote", "add", "origin", "https://github.com/o/r.git")
        return replace(self.context, branch="review/target", source_repository="o/r")

    def inspect_context(self, context):
        return {"repo": str(context.repo), "pr": {"repository": "o/r", "number": 1,
                "head": context.head, "branch": context.branch, "source_repository": context.source_repository}}

    def test_inspect_keeps_wrong_current_branch_at_the_same_commit(self):
        context = self.source_context()
        self.run_git("checkout", "-b", "another-branch")
        result = diff.inspect(self.inspect_context(context))
        self.assertEqual(result["worktrees"], [])
        current = result["current"]
        self.assertEqual(current["repo"], str(self.repo.resolve()))
        self.assertEqual(current["branch"], "another-branch")
        self.assertEqual((current["repository_status"], current["branch_status"], current["status"]),
                         ("related", "different", "same"))
        self.assertEqual(current["remotes"], [{"name": "origin", "repository": "o/r"}])

    def test_inspect_distinguishes_unrelated_and_unverified_repositories(self):
        context = self.source_context()
        request = self.inspect_context(context)
        for remote, repository_status, branch_status in (
                ("https://github.com/other/repository.git", "unrelated", "different"),
                ("/local/unverified/repository", "unknown", "unknown")):
            with self.subTest(remote=remote):
                self.run_git("remote", "set-url", "origin", remote)
                result = diff.inspect(request)
                self.assertEqual(result["worktrees"], [])
                self.assertEqual(result["current"]["repository_status"], repository_status)
                self.assertEqual(result["current"]["branch_status"], branch_status)
                self.assertEqual(result["current"]["status"], "same")
        self.run_git("remote", "remove", "origin")
        current = diff.inspect(request)["current"]
        self.assertEqual((current["repository_status"], current["branch_status"]), ("unknown", "unknown"))

    def test_inspect_source_fork_and_alias_without_exposing_remote_credentials(self):
        context = self.source_context()
        self.run_git("remote", "add", "fork", "https://secret:password@github.com/contributor/r.git")
        self.run_git("branch", "-m", "local-review")
        self.run_git("config", "branch.local-review.remote", "fork")
        self.run_git("config", "branch.local-review.merge", "refs/heads/review/target")
        request = self.inspect_context(replace(context, source_repository="contributor/r"))
        result = diff.inspect(request)
        self.assertEqual(result["current"]["repository_status"], "related")
        self.assertEqual(result["current"]["branch_status"], "matching")
        self.assertEqual(result["current"], result["worktrees"][0])
        self.assertNotIn("secret", json.dumps(result))
        self.assertNotIn("password", json.dumps(result))
        self.run_git("remote", "remove", "origin")
        self.assertEqual(diff.inspect(request)["current"]["repository_status"], "related")

    def test_inspect_detached_current_checkout_and_another_matching_worktree(self):
        context = self.source_context()
        self.run_git("checkout", "--detach", self.head)
        linked = self.base / "review workspace"
        self.run_git("worktree", "add", str(linked), "review/target")
        result = diff.inspect(self.inspect_context(context))
        self.assertIsNone(result["current"]["branch"])
        self.assertEqual((result["current"]["branch_status"], result["current"]["status"]), ("detached", "same"))
        self.assertEqual([entry["repo"] for entry in result["worktrees"]], [str(linked.resolve())])
        self.assertEqual(result["worktrees"][0]["branch_status"], "matching")

    def test_inspect_same_name_with_ambiguous_remotes_needs_source_evidence(self):
        context = self.source_context()
        self.run_git("remote", "add", "fork", "https://github.com/contributor/r.git")
        result = diff.inspect(self.inspect_context(context))
        self.assertEqual(result["current"]["repository_status"], "related")
        self.assertEqual(result["current"]["branch_status"], "unknown")
        self.assertEqual(result["worktrees"], [])

    def test_inspect_inventories_partial_staging_renames_and_untracked_files_read_only(self):
        context = self.source_context()
        renamed = "renamed 中文.py"
        self.run_git("mv", self.name, renamed)
        changed = self.repo / renamed
        changed.write_bytes(b"unstaged change after rename\n")
        partial = self.repo / "partial.txt"
        partial.write_bytes(b"staged\n")
        self.run_git("add", "--", partial.name)
        partial.write_bytes(b"staged and unstaged\n")
        folder = self.repo / "untracked directory"
        folder.mkdir()
        (folder / "child 中文.txt").write_bytes(b"untracked\n")
        index = (self.repo / ".git/index").read_bytes()
        objects = self.run_git("count-objects", "-v")
        current = diff.inspect(self.inspect_context(context))["current"]
        self.assertTrue(current["dirty"])
        self.assertEqual(current["status"], "same")
        changes = current["changes"]
        self.assertIn({"path": renamed, "status": "R", "original_path": self.name}, changes["staged"])
        self.assertIn({"path": renamed, "status": "M", "original_path": self.name}, changes["unstaged"])
        self.assertIn({"path": "partial.txt", "status": "A"}, changes["staged"])
        self.assertIn({"path": "partial.txt", "status": "M"}, changes["unstaged"])
        self.assertEqual(changes["untracked"], [{"path": "untracked directory/child 中文.txt", "status": "?"}])
        self.assertEqual(changes["conflicted"], [])
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)
        self.assertEqual(self.run_git("count-objects", "-v"), objects)
        self.assertEqual(changed.read_bytes(), b"unstaged change after rename\n")
        self.assertEqual(partial.read_bytes(), b"staged and unstaged\n")

    @unittest.skipIf(os.name == "nt", "Windows filenames cannot contain newlines")
    def test_inspect_preserves_newlines_in_untracked_paths(self):
        context = self.source_context()
        name = "untracked\nname.txt"
        (self.repo / name).write_bytes(b"untracked\n")
        changes = diff.inspect(self.inspect_context(context))["current"]["changes"]
        self.assertEqual(changes["untracked"], [{"path": name, "status": "?"}])

    def test_inspect_reports_unmerged_paths_as_conflicts(self):
        context = self.source_context()
        self.run_git("checkout", "-b", "other")
        self.file.write_bytes(b"other edit\n")
        self.run_git("commit", "-am", "other edit")
        self.run_git("checkout", "review/target")
        self.file.write_bytes(b"source edit\n")
        self.run_git("commit", "-am", "source edit")
        merged = subprocess.run(["git", "-C", str(self.repo), "merge", "other"], capture_output=True, timeout=10)
        self.assertEqual(merged.returncode, 1, merged.stderr)
        changes = diff.inspect(self.inspect_context(context))["current"]["changes"]
        self.assertEqual(changes["conflicted"], [{"path": self.name, "status": "UU"}])
        self.assertEqual(changes["staged"], [])
        self.assertEqual(changes["unstaged"], [])

    def test_inspect_status_failure_keeps_changes_unknown(self):
        context = self.source_context()
        original = comparisons.git

        def unavailable_status(repo, *arguments):
            if arguments[0] == "status":
                raise PermissionError("status denied")
            return original(repo, *arguments)

        with patch.object(comparisons, "git", side_effect=unavailable_status):
            current = diff.inspect(self.inspect_context(context))["current"]
        self.assertIsNone(current["dirty"])
        self.assertIsNone(current["changes"])
        self.assertEqual(current["status"], "same")
        self.assertIn("status denied", current["message"])

    def test_inspect_head_only_context_does_not_claim_branch_identity(self):
        request = {"repo": str(self.repo), "pr": {"repository": "o/r", "number": 1, "head": self.head}}
        current = diff.inspect(request)["current"]
        self.assertEqual(current["branch_status"], "unknown")
        self.assertEqual(current["repository_status"], "unknown")
        self.assertEqual(current["status"], "same")

    def test_source_branch_discovery_allows_newer_commits_and_dirty_worktree(self):
        context = self.source_context()
        self.file.write_bytes(b"newer committed fix\n")
        self.run_git("add", "--", self.name)
        self.run_git("commit", "-m", "local fix")
        self.file.write_bytes(b"dirty fix\n")
        index = self.run_git("ls-files", "--stage")
        objects = self.run_git("count-objects", "-v")
        prepared = self.prepare(context)
        self.assertEqual(prepared.view, "worktree")
        self.assertEqual(prepared.head, self.head)
        self.assertEqual(diff.read_comparison(prepared).after, b"dirty fix\n")
        output = diff.inspect(self.inspect_context(context))
        observed = output["worktrees"][0]
        self.assertEqual((observed["status"], observed["ahead"], observed["behind"], observed["dirty"]),
                         ("ahead", 1, 0, True))
        self.assertEqual(self.run_git("ls-files", "--stage"), index)
        self.assertEqual(self.run_git("count-objects", "-v"), objects)

    def test_inspect_current_checkout_same_behind_diverged_and_unknown(self):
        context = self.source_context()
        request = self.inspect_context(context)
        self.assertEqual(diff.inspect(request)["worktrees"][0]["status"], "same")
        self.run_git("reset", "--hard", self.before)
        self.assertEqual(diff.inspect(request)["worktrees"][0]["status"], "behind")
        self.file.write_bytes(b"different history\n")
        self.run_git("add", "--", self.name)
        self.run_git("commit", "-m", "diverged local commit")
        observed = diff.inspect(request)["worktrees"][0]
        self.assertEqual((observed["status"], observed["ahead"], observed["behind"]), ("diverged", 1, 1))
        request["pr"]["head"] = "f" * 40
        observed = diff.inspect(request)["worktrees"][0]
        self.assertEqual(observed["status"], "unknown")
        self.assertFalse(observed["dirty"])
        self.assertIn("message", observed)

    def test_inspect_cli_is_read_only_and_starts_no_host(self):
        context = self.source_context()
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(json.dumps(self.inspect_context(context)))), patch("sys.stdout", output), patch.object(service, "ensure_service") as ensure:
            self.assertEqual(cli.main(["diff", "--inspect", "--input", "-"]), 0)
        ensure.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())["worktrees"][0]["status"], "same")
        self.assertEqual(json.loads(output.getvalue())["current"]["branch_status"], "matching")

    def test_inspection_failure_is_not_reported_as_no_matching_worktree(self):
        context = self.source_context()
        output, diagnostics = io.StringIO(), io.StringIO()
        with patch("sys.stdin", io.StringIO(json.dumps(self.inspect_context(context)))), patch("sys.stdout", output), patch("sys.stderr", diagnostics), patch.object(comparisons, "registered_worktrees", side_effect=PermissionError("lookup denied")), patch.object(service, "ensure_service") as ensure:
            self.assertEqual(cli.main(["diff", "--inspect", "--input", "-"]), 1)
        ensure.assert_not_called()
        self.assertEqual(output.getvalue(), "")
        self.assertIn("lookup denied", diagnostics.getvalue())

    def test_source_identity_rejects_same_name_branch_from_another_fork(self):
        context = self.source_context()
        self.run_git("remote", "add", "fork", "git@github.com:other/r.git")
        self.run_git("config", "branch.review/target.remote", "fork")
        self.run_git("config", "branch.review/target.merge", "refs/heads/review/target")
        result = diff.inspect(self.inspect_context(context))
        self.assertEqual(result["worktrees"], [])
        self.assertEqual(result["current"]["branch_status"], "different")
        self.assertEqual(self.prepare(context).view, "snapshot")

    def test_tracking_identifies_local_branch_alias_and_external_worktree(self):
        context = self.source_context()
        self.run_git("checkout", "--detach", self.before)
        linked = self.base / "external checkout"
        self.run_git("worktree", "add", "-b", "local-alias", str(linked), self.head)
        self.run_git("config", "branch.local-alias.remote", "origin")
        self.run_git("config", "branch.local-alias.merge", "refs/heads/review/target")
        prepared = self.prepare(context)
        self.assertEqual(prepared.repo, linked.resolve())
        self.assertEqual(prepared.view, "worktree")

    def test_registered_worktrees_prefer_project_directory_and_show_lettered_choices(self):
        context = self.source_context()
        preferred = self.repo / ".worktrees" / "arbitrary-folder"
        self.run_git("worktree", "add", "--force", str(preferred), "review/target")
        prepared = self.prepare(context)
        page = diff.render_page(prepared).content.decode()
        self.assertLess(page.index(html.escape(str(preferred.resolve()))), page.index(html.escape(str(self.repo.resolve())) + "</a>"))
        self.assertIn('<ol type="A">', page)
        self.assertEqual(page.count("<li>"), 3)
        self.assertIn("存在未提交修改", page)

    def test_forced_snapshot_and_explicit_worktree_preserve_the_users_selection(self):
        context = self.source_context()
        self.file.write_bytes(b"local live edit\n")
        snapshot = self.prepare(replace(context, view="snapshot"))
        self.assertEqual(diff.read_comparison(snapshot).after, b"first edit\n")
        self.run_git("branch", "-M", "user-selected-alias")
        bound = self.prepare(replace(context, view="worktree"))
        self.assertEqual(bound.view, "worktree")
        self.assertEqual(diff.read_comparison(bound).after, b"local live edit\n")

    def test_snapshot_rename_addition_and_deletion_use_committed_paths(self):
        self.run_git("mv", self.name, "renamed.py")
        (self.repo / "new.py").write_bytes(b"new committed file\n")
        self.run_git("add", "--", "new.py")
        self.run_git("commit", "-m", "rename and add")
        head = self.run_git("rev-parse", "HEAD").decode().strip()
        context = replace(self.context, head=head, view="snapshot")
        renamed = self.prepare(replace(context, path="renamed.py", base_path=self.name))
        self.assertEqual((diff.read_comparison(renamed).before, diff.read_comparison(renamed).after),
                         (b"baseline\n", b"first edit\n"))
        added = diff.read_comparison(self.prepare(replace(context, path="new.py")))
        self.assertEqual((added.before, added.after), (None, b"new committed file\n"))
        deleted = diff.read_comparison(self.prepare(context))
        self.assertEqual((deleted.before, deleted.after), (b"baseline\n", None))

    def test_discovery_failure_can_still_display_a_fixed_snapshot(self):
        with patch.object(comparisons, "pr_worktrees", side_effect=OSError("worktree read failed")):
            target = self.prepare()
        self.assertEqual(target.view, "snapshot")
        self.assertEqual(diff.read_comparison(target).after, b"first edit\n")

    def test_bound_pr_link_retains_diagnostics_when_objects_become_unavailable(self):
        target = self.prepare()
        with patch.object(diff, "read_comparison", side_effect=OSError("retained blob unavailable")), patch.object(diff, "find_vscode") as find:
            page = diff.render_page(target)
            self.assertIn(b"retained blob unavailable", page.content)
            self.assertIn(target.github.encode(), page.content)
            self.assertNotIn(b"fetch(", page.content)
            self.assertEqual(diff.open_editor(target)["url"], target.url())
        find.assert_not_called()

    def test_pr_context_requires_fixed_head_github_and_safe_before_path(self):
        fields = dict(repo=str(self.repo), path=self.name, base=self.context.base, head=self.head, github=self.github)
        for change in ({"head": "HEAD"}, {"head": "abc"}, {"github": ""},
                       {"base": "index"}, {"base_path": "../old.py"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                diff.target_from_fields(dict(fields, **change))
        with patch.object(service, "ensure_service"), self.assertRaises(ValueError):
            diff.links(self.batch(pr={"repository": "o/r", "number": 1}))


class DiffHttpTests(DiffFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        isolate_local_web(self, self.base)
        self.origin = service.ORIGIN
        self.server = http_server.WebServer((HOST, service.PORT), http_server.WebHandler)
        self.server.web_state = {"key": "a" * 64, "mode": "applications"}
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close_server)

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def request(self, url, *, post=False, headers=None):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        request = urllib.request.Request(url, headers=headers or {}, data=b"" if post else None)
        try:
            response = opener.open(request, timeout=5)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, response.headers, response.read()

    def test_get_does_not_launch_and_post_requires_same_origin(self):
        with patch.object(diff, "open_editor", return_value={"viewer": "vscode", "message": "dispatched"}) as launch:
            code, headers, body = self.request(self.target.url())
            self.assertEqual(code, 200)
            self.assertIn(b"document.prerendering", body)
            self.assertIn(b"window.top", body)
            self.assertIn(b'window.close()', body)
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
            self.assertIn(b"const automatic=false", body)
            self.assertIn(b"const automatic=true", self.request(self.target.url(), headers={"Sec-Fetch-Site": "cross-site", "Sec-Fetch-User": "?1"})[2])
            self.assertIn(b"const automatic=false", self.request(self.target.url(), headers={"Sec-Fetch-Site": "cross-site"})[2])
            launch.assert_not_called()
            endpoint = self.origin + "/api/diff/open?" + self.target.query()
            self.assertEqual(self.request(endpoint, post=True)[0], 403)
            self.assertEqual(self.request(endpoint, post=True, headers={"Origin": "https://evil.example"})[0], 403)
            launch.assert_not_called()
            result = self.request(endpoint, post=True, headers={"Origin": self.origin, "Sec-Fetch-Site": "same-origin"})
            self.assertEqual(result[0], 200)
            self.assertEqual(json.loads(result[2])["viewer"], "vscode")
            launch.assert_called_once_with(self.target)

    def test_html_refresh_reads_current_content_and_rejects_foreign_hosts(self):
        url = self.target.url(html_only=True)
        self.assertEqual(self.request(url)[0], 200)
        self.file.write_bytes(b"latest\n")
        code, _, content = self.request(url)
        self.assertEqual(code, 200)
        self.assertIn(b"latest", content)
        self.assertIn(b"baseline", content)
        self.assertEqual(self.request(url, headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.request(url, headers={"Origin": "null"})[0], 403)

    def test_native_locator_survives_the_web_launch_endpoint(self):
        target = replace(self.target, base_commit="a" * 40, base_path="old.py")
        with patch.object(diff, "open_editor", return_value={"viewer": "vscode", "message": "dispatched"}) as launch:
            code, _, body = self.request(self.origin + "/api/diff/open?" + target.query(),
                                         post=True, headers={"Origin": self.origin})
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["viewer"], "vscode")
        launch.assert_called_once_with(target)

    def test_fixed_snapshot_get_and_editor_post_preserve_both_committed_sides(self):
        self.run_git("config", "user.name", "Diff Test")
        self.run_git("config", "user.email", "diff@example.test")
        self.run_git("config", "core.autocrlf", "false")
        self.run_git("commit", "-m", "fixed before")
        before = self.run_git("rev-parse", "HEAD").decode().strip()
        self.run_git("add", "--", self.name)
        self.run_git("commit", "-m", "fixed after")
        head = self.run_git("rev-parse", "HEAD").decode().strip()
        self.file.write_bytes(b"unrelated current contents\n")
        target = diff.Target(self.repo, self.name, self.target.base, "https://github.com/o/r/pull/1/files",
                             head, base_commit=before, view="snapshot")
        with patch.object(diff, "find_vscode") as find:
            status, _, body = self.request(target.url(html_only=True))
        find.assert_not_called()
        self.assertEqual(status, 200)
        self.assertIn(b"baseline", body)
        self.assertIn(b"first", body)
        self.assertNotIn(b"unrelated", body)
        with self.editor_dispatch() as launch:
            status, _, body = self.request(self.origin + "/api/diff/open?" + target.query(),
                                           post=True, headers={"Origin": self.origin})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["viewer"], "vscode")
        command = launch.call_args[0][0]
        self.assertEqual(Path(command[3]).read_bytes(), b"baseline\n")
        self.assertEqual(Path(command[4]).read_bytes(), b"first edit\n")
        self.assertIn(before[:12], Path(command[3]).name)
        self.assertIn(head[:12], Path(command[4]).name)

    def test_missing_pr_objects_show_reason_and_manual_github_without_editor(self):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        github = "https://github.com/o/r/pull/1/files"
        target = diff.Target(self.repo, self.name, self.target.base, github, "f" * 40)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        with patch.object(diff, "find_vscode") as find:
            for url in (target.url(), target.url(html_only=True)):
                with opener.open(url, timeout=5) as response:
                    self.assertEqual(response.code, 200)
                    body = response.read()
                    self.assertIn("无法读取比较".encode(), body)
                    self.assertIn(github.encode(), body)
                    self.assertNotIn(b"fetch(", body)
        find.assert_not_called()


if __name__ == "__main__":
    unittest.main()
