import hashlib
import importlib.util
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
from unittest.mock import MagicMock
from types import SimpleNamespace
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'runtime/local_web/__main__.py'
sys.path.insert(0, str(ROOT / 'runtime'))
from local_web import service as web, artifacts, storage, http_server
from local_web.apps import status as apps
from local_web.apps import diff


class WebServiceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='smartkit-web-test-')
        self.base = Path(self.temporary.name)
        self.environment = patch.dict(os.environ, {
            'HOME': str(self.base), 'USERPROFILE': str(self.base),
            'XDG_CACHE_HOME': str(self.base / 'cache'),
            'XDG_STATE_HOME': str(self.base / 'state'),
            'LOCALAPPDATA': str(self.base / 'local'),
        })
        self.environment.start()
        self.project = self.base / 'project_with_underscores'
        self.project.mkdir()

    def tearDown(self):
        try:
            web.stop_service()
        finally:
            self.environment.stop()
            self.temporary.cleanup()


    def request(self, url, headers=None):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            response = opener.open(urllib.request.Request(url, headers=headers or {}), timeout=3)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, response.headers, response.read()

    def test_publish_only_declared_immutable_files_and_private_pages(self):
        artifact = artifacts.create_artifact({'0001/diff.html': b'<!doctype html><title>fixed_diff</title>',
                                               'raw/before.txt': b'secret before'}, public_files=['0001/diff.html'])
        path = artifact.files['0001/diff.html'].path
        info = web.ensure_service()
        candidate = info['origin'] + '/preview/' + artifact.id + '/0001/diff.html'
        self.assertEqual(self.request(candidate)[0], 404)
        urls = web.publish_artifact(artifact.id)
        url = urls['0001/diff.html']
        code, headers, body = self.request(url)
        self.assertEqual(code, 200)
        self.assertIn('text/html', headers['Content-Type'])
        self.assertEqual(body, path.read_bytes())
        self.assertIn('sandbox allow-scripts', headers['Content-Security-Policy'])
        self.assertIn("connect-src 'none'", headers['Content-Security-Policy'])
        self.assertNotIn('allow-same-origin', headers['Content-Security-Policy'])
        self.assertIsNone(headers.get('Access-Control-Allow-Origin'))
        self.assertEqual(self.request(info['origin'] + '/preview/' + artifact.id + '/raw/before.txt')[0], 404)
        self.assertEqual(self.request(url.replace('diff.html', '%2e%2e/service.json'))[0], 404)
        self.assertEqual(self.request(url, {'Host': 'attacker.example'})[0], 403)
        self.assertEqual(self.request(url, {'Origin': 'https://attacker.example'})[0], 403)
        self.assertEqual(self.request(info['origin'] + '/api/readiness/')[0], 403)
        self.assertEqual(self.request(info['apps']['readiness'], {'Origin': 'null'})[0], 403)
        self.assertEqual(self.request(info['apps']['readiness'], {'Sec-Fetch-Site': 'cross-site'})[0], 403)
        self.assertEqual(web.publish_artifact(artifact.id), urls)
        self.assertEqual(artifacts.load_artifact(artifact.id).expires_at, artifact.expires_at)
        path.write_bytes(b'changed')
        self.assertEqual(self.request(url)[0], 409)
        with self.assertRaises(ValueError):
            web.publish_artifact(artifact.id)

    def test_expiry_does_not_depend_on_physical_cleanup(self):
        artifact = artifacts.create_artifact({'diff.html': b'fixed_diff'}, public_files=['diff.html'],
                                             retention=timedelta(seconds=1))
        url = web.publish_artifact(artifact.id)['diff.html']
        time.sleep(1.05)
        code, _, body = self.request(url)
        self.assertEqual(code, 410)
        self.assertNotIn(b'fixed_diff', body)
        self.assertTrue(artifact.files['diff.html'].path.exists())
        foreign = artifacts.cache_root() / 'foreign.json'
        foreign.write_text('{"important":"preserve"}')
        artifacts.create_artifact({'new.txt': b'new'})
        self.assertIsNone(artifacts.load_artifact(artifact.id))
        self.assertTrue(foreign.exists())

    def test_startup_cleans_expired_private_groups_without_page_reads(self):
        with patch.object(artifacts.time, 'time', return_value=time.time() - 1000000):
            old = artifacts.create_artifact({'private.txt': b'expired'})
        self.assertTrue(old.files['private.txt'].path.exists())
        web.ensure_service()
        self.assertFalse(old.files['private.txt'].path.exists())

    def test_running_service_triggers_periodic_cleanup_without_a_request(self):
        storage.prepare_state()
        state = {'schema': web.SERVICE_SCHEMA, 'port': 47821, 'key': 'a' * 64, 'mode': 'applications', 'pid': 0}
        ticks = [0]
        calls = [0]
        handlers = {}

        def idle():
            calls[0] += 1
            ticks[0] = web.CLEANUP_INTERVAL + 1
            if calls[0] == 2:
                handlers[signal.SIGTERM](signal.SIGTERM, None)

        server = SimpleNamespace(server_port=43123, handle_request=idle)
        manager = MagicMock()
        manager.__enter__.return_value = server
        logger = web.logging.getLogger('smartkit.local_web')
        before = set(logger.handlers)
        try:
            with patch.object(http_server, 'WebServer', return_value=manager), patch.object(web, 'load_state', return_value=state), patch.object(web, 'write_json'), patch.object(web.time, 'monotonic', side_effect=lambda: ticks[0]), patch.object(web.signal, 'signal', side_effect=lambda number, handler: handlers.update({number: handler})), patch.object(web, 'cleanup_artifacts') as cleanup:
                web.serve()
            cleanup.assert_called_once_with()
        finally:
            for handler in set(logger.handlers) - before:
                logger.removeHandler(handler)
                handler.close()

    def test_status_page_links_are_offered_for_findings_in_each_hook_protocol(self):
        observation = {'status': 'findings', 'captured_at': time.time(), 'message': '',
                       'findings': [{'code': 'setup-required', 'tool': 'SmartKit project setup',
                                     'message': 'migration needed', 'guidance': 'Run setup'}]}
        for harness in ('codex', 'cursor', 'copilot', 'qoder'):
            with self.subTest(harness=harness):
                apps.record_project(self.project, harness, observation)
                result = subprocess.run([sys.executable, '-B', str(ENTRY), 'hook', '--harness', harness],
                                        input=json.dumps({'cwd': str(self.project)}), capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                if harness in ('codex', 'qoder'):
                    context = payload['hookSpecificOutput']['additionalContext']
                else:
                    context = payload['additional_context' if harness == 'cursor' else 'additionalContext']
                info = web.ensure_service()
                self.assertIn(info['apps']['readiness'].split('/?')[0], context)
                self.assertIn(info['apps']['setup'].split('/?')[0], context)
                self.assertNotIn('apply --harness', context)
        clean = dict(observation, status='passed', findings=[])
        apps.record_project(self.project, 'codex', clean)
        self.assertEqual(apps.hook_page_links(self.project, 'codex', web.ensure_service()['apps']), {})

    def test_reuse_detached_hook_and_restart_return_current_origin(self):
        result = subprocess.run([sys.executable, '-B', str(ENTRY), 'hook', '--harness', 'codex'],
                                input=json.dumps({'cwd': str(self.project)}), text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')
        first = web.ensure_service()
        first_key = web.load_state()['key']
        cached = artifacts.create_artifact({'diff.html': b'fixed'}, public_files=['diff.html'])
        artifact = web.publish_artifact(cached.id)['diff.html']
        subprocess.run(['git', '-C', str(self.project), 'init'], capture_output=True, check=True)
        sample = self.project / 'live.py'
        sample.write_bytes(b'baseline\n')
        subprocess.run(['git', '-C', str(self.project), 'add', 'live.py'], capture_output=True, check=True)
        baseline = subprocess.run(['git', '-C', str(self.project), 'rev-parse', ':live.py'], capture_output=True, check=True).stdout.decode().strip()
        live_url = diff.Target(self.project, 'live.py', 'blob:' + baseline).url(html_only=True)
        sample.write_bytes(b'before restart\n')
        self.assertEqual(self.request(live_url)[0], 200)
        self.assertEqual(web.ensure_service()['pid'], first['pid'])
        self.assertEqual(self.request(first['apps']['setup'])[0], 200)
        self.assertEqual(self.request(artifact)[0], 200)
        self.assertTrue(web.stop_service())
        second = web.ensure_service()
        self.assertEqual(second['origin'], first['origin'])
        sample.write_bytes(b'after restart\n')
        code, _, live_content = self.request(live_url)
        self.assertEqual(code, 200)
        self.assertIn(b'baseline', live_content)
        self.assertIn(b'after&nbsp;restart', live_content)
        self.assertNotEqual(second['pid'], first['pid'])
        self.assertNotEqual(web.load_state()['key'], first_key)
        self.assertEqual(self.request(second['apps']['setup'])[0], 200)
        self.assertTrue(second['apps']['setup'].startswith(second['origin'] + '/setup/'))
        refreshed_artifact = second['origin'] + urlsplit(artifact).path
        self.assertEqual(self.request(refreshed_artifact)[0], 200)
        result = subprocess.run([sys.executable, '-B', str(ENTRY), 'status'], text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['service']['origin'], second['origin'])


    def test_preview_only_process_exits_without_remaining_artifacts(self):
        info = web.ensure_service('previews')
        deadline = time.monotonic() + 13
        while web.health(web.load_state()) and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertIsNone(web.health(web.load_state()))
        restarted = web.ensure_service()
        self.assertNotEqual(restarted['pid'], info['pid'])
        self.assertEqual(web.load_state()['port'], int(restarted['origin'].rsplit(':', 1)[1]))

    def test_concurrent_ensure_returns_one_server(self):
        processes = [subprocess.Popen([sys.executable, '-B', str(ENTRY), 'ensure'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for _ in range(4)]
        try:
            results = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=20)
                self.assertEqual(process.returncode, 0, stderr.decode())
                results.append(json.loads(stdout))
            self.assertEqual(len({value['pid'] for value in results}), 1)
            self.assertEqual(len({value['origin'] for value in results}), 1)
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.wait()

    def test_slow_request_does_not_make_a_healthy_server_look_conflicted(self):
        info = web.ensure_service()
        port = int(info['origin'].rsplit(':', 1)[1])
        with socket.create_connection(('127.0.0.1', port), timeout=3) as slow:
            slow.sendall(b'GET /api/service/health HTTP/1.1\r\n')
            time.sleep(0.05)
            self.assertEqual(web.ensure_service()['pid'], info['pid'])


    def test_fixed_port_conflict_preserves_state_and_unknown_process(self):
        web.ensure_service()
        web.stop_service()
        state_file = storage.state_dir() / 'service.json'
        original = state_file.read_bytes()
        with socket.socket() as other:
            if os.name != 'nt':
                other.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            other.bind(('127.0.0.1', 47821))
            other.listen()
            with self.assertRaisesRegex(OSError, 'unverified'):
                web.ensure_service()
            with self.assertRaisesRegex(OSError, 'unverified'):
                web.stop_service()
            self.assertEqual(other.getsockname()[1], 47821)
            self.assertEqual(state_file.read_bytes(), original)

    def test_invalid_state_is_preserved_instead_of_replaced(self):
        web.ensure_service()
        web.stop_service()
        state_file = storage.state_dir() / 'service.json'
        original = state_file.read_bytes()
        state_file.write_bytes(b'{invalid state')
        try:
            with self.assertRaises(ValueError):
                web.ensure_service()
            self.assertEqual(state_file.read_bytes(), b'{invalid state')
        finally:
            state_file.write_bytes(original)

    def test_cache_confinement_and_redirects(self):
        web.ensure_service()
        artifact = artifacts.create_artifact({'diff.html': b'captured'}, public_files=['diff.html'])
        outside = self.base / 'private.html'
        outside.write_bytes(b'private')
        for name in ('../private', '/private', 'a\\b', 'a//b', 'a/./b'):
            with self.assertRaises(ValueError):
                artifacts.create_artifact({name: b'invalid'})
        if os.name != 'nt':
            path = artifact.files['diff.html'].path
            path.unlink()
            path.symlink_to(outside)
            with self.assertRaises(ValueError):
                web.publish_artifact(artifact.id)


    def test_readiness_and_setup_are_read_only_and_missing_evidence_is_explicit(self):
        apps.record_project(self.project, 'codex')
        self.assertEqual(apps.application_data('readiness')['projects'][0]['readiness']['status'], 'unavailable')
        observation = {'status': 'findings', 'captured_at': time.time(), 'message': '',
                       'findings': [{'code': 'test', 'tool': 'test <tool>', 'message': 'needs work', 'guidance': 'ask owner'}]}
        apps.record_project(self.project, 'codex', observation)
        apps.record_project(self.project, 'codex')
        info = web.ensure_service()
        before = {str(path): path.read_bytes() for root in (self.project, apps.cache_dir()) for path in root.rglob('*') if path.is_file()}
        for _ in range(2):
            code, _, body = self.request(info['apps']['readiness'])
            self.assertEqual(code, 200)
            self.assertIn('存在待处理发现'.encode(), body)
            self.assertIn(b'test &lt;tool&gt;', body)
            self.assertNotIn(b'test <tool>', body)
            code, _, body = self.request(info['apps']['setup'])
            self.assertEqual(code, 200)
            self.assertIn('尚未初始化'.encode(), body)
        after = {str(path): path.read_bytes() for root in (self.project, apps.cache_dir()) for path in root.rglob('*') if path.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(apps.application_data('readiness')['projects'][0]['readiness'], observation)
        state = web.load_state()
        code, _, body = self.request(info['origin'] + '/api/readiness/?key=' + state['key'])
        self.assertEqual(code, 200)
        self.assertNotIn('action', json.loads(body)['projects'][0]['readiness']['findings'][0])

    def test_preview_mode_can_upgrade_but_never_downgrade_applications(self):
        first = web.ensure_service('previews')
        self.assertEqual(first['mode'], 'previews')
        self.assertEqual(self.request(first['apps']['setup'])[0], 404)
        second = web.ensure_service('applications')
        self.assertEqual(first['pid'], second['pid'])
        self.assertEqual(self.request(second['apps']['setup'])[0], 200)
        self.assertEqual(web.ensure_service('previews')['mode'], 'applications')

    def test_readiness_owner_publishes_complete_results_but_skipped_gate_preserves_them(self):
        checker_spec = importlib.util.spec_from_file_location('web_readiness_owner', ROOT / 'runtime/recommended-tools/check_recommended_tools.py')
        checker = importlib.util.module_from_spec(checker_spec)
        sys.modules[checker_spec.name] = checker
        checker_spec.loader.exec_module(checker)
        finding = checker.Finding('missing', 'tool', 'needs work', 'ask owner', action={'private': 'never expose'})
        with patch.object(checker, 'resolve_project_root', return_value=self.project):
            checker.record_readiness_snapshot(checker.HookResult(True, (finding,)), 'codex')
            original = apps.project_records()[0]['readiness']
            checker.record_readiness_snapshot(checker.HookResult(False), 'codex')
            self.assertEqual(apps.project_records()[0]['readiness'], original)
            self.assertNotIn('action', original['findings'][0])
            checker.record_readiness_snapshot(checker.HookResult(True, internal_error=True), 'codex')
            self.assertEqual(apps.project_records()[0]['readiness']['status'], 'failed')
            checker.record_readiness_snapshot(checker.HookResult(True), 'codex')
            self.assertEqual(apps.project_records()[0]['readiness']['status'], 'passed')


if __name__ == '__main__':
    unittest.main()
