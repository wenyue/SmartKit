"""Exercise live Git comparisons without link registrations or baseline writes."""
import json
import os
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_web import ORIGIN, HOST, PORT, artifacts, http_server, service, storage
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
        return dict({"id": "M1", "title": self.name, "repo": str(self.repo), "path": self.name,
                     "base": "blob:" + self.oid}, **extra)

class DiffTests(DiffFixture, unittest.TestCase):
    def test_index_context_is_resolved_once_without_mutable_url_state(self):
        with patch.object(service, "ensure_service"):
            result = diff.links([self.entry(base="index")])[0]
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
            links = diff.links([self.entry()])
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
                diff.links([self.entry(), self.entry()])
        ensure.assert_not_called()

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
        self.context = diff.Target(self.repo, self.name, "commit:" + self.before, self.github, self.head)

    def prepare(self, context=None):
        target = context or self.context
        with patch.object(service, "ensure_service"):
            result = diff.links([dict(id="M1", title=target.path, **dict(
                (name, value[0]) for name, value in urllib.parse.parse_qs(target.query()).items()))])[0]
        return diff.target_from_query(result["url"].split("?", 1)[1])

    def linked(self, name):
        path = self.base / name
        self.run_git("worktree", "add", "--detach", str(path), self.head)
        return path

    def test_current_checkout_and_commit_baseline_are_bound_without_git_writes(self):
        index = self.run_git("ls-files", "--stage")
        objects = self.run_git("count-objects", "-v")
        target = self.prepare()
        self.assertEqual(target.repo, self.repo.resolve())
        self.assertEqual(target.base, "blob:" + self.oid)
        self.assertIsNone(target.head)
        self.assertEqual(diff.read_comparison(target).before, b"baseline\n")
        self.assertEqual(self.run_git("ls-files", "--stage"), index)
        self.assertEqual(self.run_git("count-objects", "-v"), objects)

    def test_pr_objects_and_branch_without_checkout_go_to_github(self):
        self.run_git("checkout", "--detach", self.before)
        self.assertEqual(self.run_git("cat-file", "-t", self.head).strip(), b"commit")
        target = self.prepare()
        self.assertEqual(target.head, self.head)
        self.assertEqual(diff.render_page(target).redirect, self.github)
        with patch.object(diff, "find_vscode") as find:
            self.assertEqual(diff.open_editor(target)["url"], self.github)
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
        self.assertIn(self.github, parser.urls)

    def test_rename_uses_before_path_and_new_file_uses_absent_baseline(self):
        renamed = "renamed.py"
        self.file.rename(self.repo / renamed)
        context = replace(self.context, path=renamed, base_path=self.name)
        target = self.prepare(context)
        self.assertEqual(target.base, "blob:" + self.oid)
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
                self.assertEqual(diff.render_page(prepared).redirect, self.github)
                self.assertEqual(diff.open_editor(prepared)["url"], self.github)

    def test_pr_context_requires_fixed_head_github_and_safe_before_path(self):
        fields = dict(repo=str(self.repo), path=self.name, base=self.context.base, head=self.head, github=self.github)
        for change in ({"head": "HEAD"}, {"head": "abc"}, {"github": ""},
                       {"base": "index"}, {"base_path": "../old.py"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                diff.target_from_fields(dict(fields, **change))
        with patch.object(service, "ensure_service"), self.assertRaises(ValueError):
            diff.links([self.entry(github=self.github)])


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
