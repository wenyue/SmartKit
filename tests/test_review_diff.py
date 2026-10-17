"""Exercise live Git comparisons without link registrations or baseline writes."""
import json
import io
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
from local_web import ORIGIN, HOST, PORT, artifacts, cli, http_server, service, storage
from local_web.apps import diff


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
    def editor_dispatch(self, status=0):
        # Keep real Git subprocesses separate from the mocked editor launch.
        process = Mock()
        process.wait.return_value = status
        editor = SimpleNamespace(Popen=Mock(return_value=process), DEVNULL=subprocess.DEVNULL,
                                 TimeoutExpired=subprocess.TimeoutExpired)
        with patch.object(diff, "find_vscode", return_value=Path("Code.exe")), patch.object(diff, "subprocess", editor):
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
        with patch.object(diff, "find_vscode") as find:
            value = diff.open_editor(diff.Target(missing.repo, missing.path, missing.base, "https://github.com/o/r/pull/1/files"))
        find.assert_not_called()
        self.assertEqual(value["url"], "https://github.com/o/r/pull/1/files")

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
            self.assertEqual(diff.render_page(target).redirect, github)

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
        batch = self.batch(entry, repo=str(target.repo), base=target.base,
                           pr={"repository": "o/r", "number": 1, "head": target.head})
        with patch.object(service, "ensure_service"):
            result = diff.links(batch)[0]
        return diff.target_from_query(result["url"].split("?", 1)[1])

    def linked(self, name):
        path = self.base / name
        self.run_git("worktree", "add", "--detach", str(path), self.head)
        return path

    def test_commit_editor_uses_native_git_uri_without_temporary_files(self):
        target = self.prepare()
        with self.editor_dispatch() as launch, patch.object(artifacts, "create_artifact") as capture:
            result = diff.open_editor(target)
        self.assertEqual(result["viewer"], "vscode")
        capture.assert_not_called()
        launch.assert_called_once()
        command = launch.call_args[0][0]
        self.assertEqual(command[:3], ["Code.exe", "--reuse-window", "--diff"])
        self.assertTrue(command[3].startswith("--file-uri="))
        before = urllib.parse.urlsplit(command[3].split("=", 1)[1])
        self.assertEqual(before.scheme, "git")
        self.assertEqual(json.loads(urllib.parse.unquote(before.query)), {"path": str(self.file), "ref": self.before})
        self.assertEqual(command[4], "--file-uri=" + self.file.as_uri())

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
        with self.editor_dispatch(status=2) as launch, patch.object(artifacts, "create_artifact") as capture:
            result = diff.open_editor(target)
        self.assertEqual(result["url"], target.github)
        capture.assert_not_called()
        launch.assert_called_once()

    def test_native_deletion_materializes_only_the_absent_current_side(self):
        self.file.unlink()
        target = self.prepare()
        with self.editor_dispatch() as launch, patch.object(artifacts, "create_artifact", wraps=artifacts.create_artifact) as capture:
            result = diff.open_editor(target)
        self.assertEqual(result["viewer"], "vscode")
        capture.assert_called_once_with({"after.py": b""})
        command = launch.call_args[0][0]
        self.assertTrue(command[3].startswith("--file-uri=git:"))
        after_uri = urllib.parse.urlsplit(command[4].split("=", 1)[1])
        self.assertEqual(Path(urllib.request.url2pathname(after_uri.path)).read_bytes(), b"")
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
        self.assertIsNone(target.head)
        self.assertEqual(diff.read_comparison(target).before, b"baseline\n")
        self.assertEqual(self.run_git("ls-files", "--stage"), index)
        self.assertEqual(self.run_git("count-objects", "-v"), objects)

    def test_pr_objects_and_branch_without_checkout_go_to_github(self):
        self.run_git("checkout", "--detach", self.before)
        self.assertEqual(self.run_git("cat-file", "-t", self.head).strip(), b"commit")
        target = self.prepare()
        self.assertEqual(target.head, self.head)
        self.assertEqual(diff.render_page(target).redirect, self.github_file)
        with patch.object(diff, "find_vscode") as find:
            self.assertEqual(diff.open_editor(target)["url"], self.github_file)
        find.assert_not_called()

    def test_linked_detached_checkout_is_found_and_binding_survives_later_commits(self):
        self.run_git("checkout", "--detach", self.before)
        linked = self.linked("linked & checkout")
        target = self.prepare()
        self.assertEqual(target.repo, linked.resolve())
        self.assertIsNone(target.head)
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
        self.assertTrue(all(choice.head is None for choice in selected))
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
        with self.editor_dispatch() as launch:
            self.assertEqual(diff.open_editor(target)["viewer"], "vscode")
        before_uri = urllib.parse.urlsplit(launch.call_args[0][0][3].split("=", 1)[1])
        self.assertEqual(json.loads(urllib.parse.unquote(before_uri.query))["path"], str(self.repo / self.name))
        self.assertEqual(target.github, self.github + "#diff-b1cb4c2fea8f27faabf83123f17e7e992ed88c065ec16deaef2c77891f8da40d")
        self.assertEqual(diff.read_comparison(target).after, b"first edit\n")
        addition = self.repo / "new.py"
        addition.write_bytes(b"new file\n")
        target = self.prepare(replace(self.context, path="new.py"))
        self.assertEqual(target.base, "absent")
        self.assertIsNone(diff.read_comparison(target).before)

    def test_missing_before_commit_or_repository_uses_github_not_empty_content(self):
        for target in (replace(self.context, base="commit:" + "f" * 40),
                       replace(self.context, repo=self.base / "missing")):
            with self.subTest(target=target):
                prepared = self.prepare(target)
                self.assertEqual(diff.render_page(prepared).redirect, self.github_file)
                self.assertEqual(diff.open_editor(prepared)["url"], self.github_file)

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
        self.server = http_server.WebServer((HOST, PORT), http_server.WebHandler)
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
            endpoint = ORIGIN + "/api/diff/open?" + self.target.query()
            self.assertEqual(self.request(endpoint, post=True)[0], 403)
            self.assertEqual(self.request(endpoint, post=True, headers={"Origin": "https://evil.example"})[0], 403)
            launch.assert_not_called()
            result = self.request(endpoint, post=True, headers={"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"})
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
            code, _, body = self.request(ORIGIN + "/api/diff/open?" + target.query(),
                                         post=True, headers={"Origin": ORIGIN})
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["viewer"], "vscode")
        launch.assert_called_once_with(target)

    def test_no_pr_checkout_redirects_in_same_page_without_editor_or_network_lookup(self):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        github = "https://github.com/o/r/pull/1/files"
        target = diff.Target(self.repo, self.name, self.target.base, github, "f" * 40)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        with patch.object(diff, "find_vscode") as find:
            for url in (target.url(), target.url(html_only=True)):
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    opener.open(url, timeout=5)
                with raised.exception as response:
                    self.assertEqual(response.code, 303)
                    self.assertEqual(response.headers["Location"], github)
                    self.assertEqual(response.headers["Referrer-Policy"], "no-referrer")
        find.assert_not_called()


if __name__ == "__main__":
    unittest.main()
