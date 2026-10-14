"""Exercise shared link contracts without changing desktop associations."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'runtime/deep-links'
sys.path.insert(0, str(SOURCE))
links = importlib.import_module('deep_links')
registration = links.registration
actions = links.actions


class DeepLinksTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='smartkit links 中文 ')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / 'installed'
        self.before = self.base / 'before.py'
        self.after = self.base / 'after.py'
        self.before.write_text('timeout = 5\n', encoding='utf-8')
        self.after.write_text('timeout = 10\n', encoding='utf-8')

    def batch(self, viewer='auto'):
        return links.parse_tasks([{'id': 'one', 'before': 'before.py', 'after': 'after.py'}],
                                 self.base, viewer)

    def desktop(self):
        stack = mock.patch.multiple(registration, desktop_environment=mock.DEFAULT,
                                    desktop_available=mock.DEFAULT, ownership=mock.DEFAULT,
                                    registration_matches=mock.DEFAULT, register=mock.DEFAULT)
        mocks = stack.start()
        self.addCleanup(stack.stop)
        mocks['desktop_environment'].return_value = {'DISPLAY': ':test'}
        mocks['desktop_available'].return_value = True
        mocks['ownership'].return_value = 'absent'
        marker = self.root / 'association-test'
        mocks['registration_matches'].side_effect = lambda *args: marker.exists()
        mocks['register'].side_effect = lambda *args: marker.write_text('registered')
        return mocks

    def test_snapshot_survives_source_edits_and_a_new_cli_process(self):
        link = links.create(self.root, self.batch('web'))[0]
        self.after.write_text('timeout = 999\n')
        action, token = links.parse_url(link.url)
        folder, record = links.load_task(self.root, action, token)
        self.assertEqual((folder / record['after']).read_text(), 'timeout = 10\n')
        self.assertTrue((folder / 'diff.html').is_file())
        self.assertIn('smartkit://diff/', link.markdown)
        self.assertTrue(link.web_url.startswith('file:'))
        subprocess.run([sys.executable, str(SOURCE / 'deep_links.py'), '--help'], check=True,
                       stdout=subprocess.DEVNULL, cwd=self.base)
        self.assertEqual(links.load_task(self.root, action, token)[1], record)

    def test_batch_json_output_works_with_an_ascii_redirected_console(self):
        if sys.platform == 'darwin':
            self.skipTest('macOS does not use these directory overrides')
        source = self.base / 'tasks.json'
        source.write_text(json.dumps([{'id': 'one', 'title': '统计页面', 'after': 'after.py'}]))
        environment = dict(os.environ, LOCALAPPDATA=str(self.base), XDG_DATA_HOME=str(self.base),
                           PYTHONIOENCODING='ascii')
        result = subprocess.run([sys.executable, str(SOURCE / 'deep_links.py'),
                                 'create', '--input', str(source)], env=environment,
                                capture_output=True, encoding='utf-8', timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('统计页面', json.loads(result.stdout)[0]['markdown'])

    def test_artifact_dispatch_uses_its_fixed_copy(self):
        source = self.base / 'report.html'
        source.write_text('<h1>original</h1>')
        tasks = links.parse_tasks([{'id': 'report', 'action': 'artifact', 'path': 'report.html'}], self.base, 'auto')
        link = links.create(self.root, tasks)[0]
        source.write_text('<h1>changed</h1>')
        with mock.patch.object(registration, 'open_file') as opener:
            result = links.open_link(self.root, link.url)
        self.assertEqual(opener.call_args.args[0].read_text(), '<h1>original</h1>')
        self.assertEqual(result['viewer'], 'default')

    def test_add_delete_and_artifact_in_one_batch(self):
        report = self.base / 'report.html'
        report.write_text('<h1>报告</h1>', encoding='utf-8')
        tasks = links.parse_tasks([
            {'id': 'add', 'before': None, 'after': 'after.py'},
            {'id': 'delete', 'before': 'before.py', 'after': None},
            {'id': 'report', 'action': 'artifact', 'path': 'report.html'},
        ], self.base, 'auto')
        created = links.create(self.root, tasks)
        self.assertEqual([link.id for link in created], ['add', 'delete', 'report'])
        folder, record = links.load_task(self.root, *links.parse_url(created[0].url))
        self.assertEqual((folder / record['before']).read_bytes(), b'')
        folder, record = links.load_task(self.root, *links.parse_url(created[1].url))
        self.assertEqual((folder / record['after']).read_bytes(), b'')
        folder, record = links.load_task(self.root, *links.parse_url(created[2].url))
        self.assertEqual((folder / record['preview']).read_text(encoding='utf-8'), '<h1>报告</h1>')

    def test_bad_batch_commits_no_tasks(self):
        binary = self.base / 'binary.py'
        binary.write_bytes(b'\xff\x00')
        tasks = self.batch() + links.parse_tasks([{'id': 'bad', 'after': 'binary.py'}], self.base, 'auto')
        with self.assertRaises(UnicodeDecodeError):
            links.create(self.root, tasks)
        self.assertEqual(list((self.root / 'tasks').iterdir()), [])

    def test_untrusted_inputs_are_rejected_before_dispatch(self):
        for value in (None, {}, [{'id': 'x', 'action': []}],
                      [{'id': 'x', 'before': None, 'after': None}],
                      [{'id': 'x', 'after': 'after.py', 'viewer': {}}],
                      [{'id': 'x', 'after': 'after.py', 'command': 'anything'}],
                      [{'id': 'x', 'after': 'after.py'}, {'id': 'x', 'after': 'after.py'}]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                links.parse_tasks(value, self.base, 'auto')
        token = 'a' * 32
        for url in ('file:///etc/passwd', 'smartkit://run/' + token,
                    'smartkit://diff/../record', 'smartkit://diff/%2e%2e',
                    'smartkit://diff/' + token + '?command=run',
                    'smartkit://diff/' + token + '#fragment',
                    'smartkit://user@diff/' + token, 'smartkit://diff:123/' + token):
            with self.subTest(url=url), self.assertRaises(ValueError):
                links.parse_url(url)

    def test_record_cannot_redirect_to_another_action_or_outside_snapshot(self):
        link = links.create(self.root, self.batch())[0]
        action, token = links.parse_url(link.url)
        folder, record = links.load_task(self.root, action, token)
        with self.assertRaises(ValueError):
            links.load_task(self.root, 'artifact', token)
        record['after'] = '../../after.py'
        (folder / 'record.json').write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            links.open_link(self.root, link.url)
        self.assertEqual(self.after.read_text(), 'timeout = 10\n')

    @unittest.skipIf(os.name == 'nt', 'ordinary Windows accounts may not create symbolic links')
    def test_snapshot_symlinks_are_rejected(self):
        link = links.create(self.root, self.batch())[0]
        action, token = links.parse_url(link.url)
        folder, record = links.load_task(self.root, action, token)
        after = folder / record['after']
        after.unlink()
        after.symlink_to(self.after)
        with self.assertRaises(ValueError):
            links.open_link(self.root, link.url)

    def test_generated_html_escapes_code_and_title(self):
        markup = actions.render_diff('<script>alert(1)</script>', '<img src=x onerror=x>', '<script>title</script>')
        self.assertNotIn('<script>', markup)
        self.assertNotIn('<img src=', markup)
        self.assertIn('&lt;script&gt;', markup)

    def test_newline_only_changes_are_visible_in_html(self):
        for before, after in [('same\n', 'same'), ('same\r\n', 'same\n')]:
            self.assertIn('仅换行符或文件末尾换行发生变化', actions.render_diff(before, after, 'newline'))

    def test_auto_falls_back_and_explicit_vscode_keeps_failure_visible(self):
        for viewer in ('auto', 'vscode'):
            link = links.create(self.root, self.batch(viewer))[0]
            with mock.patch.object(actions, 'find_vscode', return_value=None), \
                    mock.patch.object(registration, 'open_file') as browser:
                if viewer == 'auto':
                    result = links.open_link(self.root, link.url)
                    self.assertEqual(result['viewer'], 'web')
                    self.assertTrue(result['warning'])
                    self.assertEqual(browser.call_args.args[0].name, 'diff.html')
                else:
                    with self.assertRaises(OSError):
                        links.open_link(self.root, link.url)
                    self.assertEqual(browser.call_args.args[0].name, 'open-error.html')

    def test_vscode_request_reuses_window_and_uses_only_snapshots(self):
        link = links.create(self.root, self.batch())[0]
        with mock.patch.object(actions, 'find_vscode', return_value=self.base / 'code'), \
                mock.patch.object(actions.subprocess, 'Popen') as spawn:
            spawn.return_value.wait.return_value = 0
            result = links.open_link(self.root, link.url)
        arguments = spawn.call_args.args[0]
        self.assertEqual(arguments[1:3], ['--reuse-window', '--diff'])
        self.assertTrue(all(str(self.root / 'tasks') in path for path in arguments[3:]))
        self.assertIn('发送', result['message'])

    def test_vscode_nonzero_exit_uses_web_in_auto_mode(self):
        link = links.create(self.root, self.batch())[0]
        with mock.patch.object(actions, 'find_vscode', return_value=self.base / 'code'), \
                mock.patch.object(actions.subprocess, 'Popen') as spawn, \
                mock.patch.object(registration, 'open_file') as browser:
            spawn.return_value.wait.return_value = -5
            result = links.open_link(self.root, link.url)
        self.assertEqual(result['viewer'], 'web')
        self.assertIn('-5', result['warning'])
        browser.assert_called_once()

    def test_never_enabled_hook_is_silent_and_does_not_write(self):
        with mock.patch.object(registration, 'data_root', return_value=self.root), \
                mock.patch('sys.stdout') as output:
            self.assertEqual(links.main(['ensure', '--quiet']), 0)
        output.write.assert_not_called()
        self.assertFalse(self.root.exists())

    def test_install_is_stable_idempotent_and_program_runs_outside_source(self):
        desktop = self.desktop()
        first = links.ensure(self.root, enable=True)
        archive = self.root / 'deep-links.pyz'
        before = archive.stat().st_mtime_ns
        state = (self.root / 'installation.json').read_bytes()
        second = links.ensure(self.root)
        self.assertEqual(first, second)
        self.assertEqual(archive.stat().st_mtime_ns, before)
        self.assertEqual((self.root / 'installation.json').read_bytes(), state)
        self.assertEqual(desktop['register'].call_count, 1)
        invocation = subprocess.run([sys.executable, str(archive), '--help'], cwd=self.base,
                                    capture_output=True, text=True, timeout=10)
        self.assertEqual(invocation.returncode, 0, invocation.stderr)
        self.assertIn('create', invocation.stdout)

    def test_foreign_association_is_preserved(self):
        desktop = self.desktop()
        desktop['ownership'].return_value = 'foreign'
        with self.assertRaises(FileExistsError):
            links.ensure(self.root, enable=True)
        desktop['register'].assert_not_called()
        self.assertFalse((self.root / 'deep-links.pyz').exists())

    def test_newer_install_is_never_downgraded_and_snapshots_survive_upgrade(self):
        self.desktop()
        link = links.create(self.root, self.batch())[0]
        with mock.patch.object(links, 'source_release', return_value=('9.0.0', 'a' * 64)):
            links.ensure(self.root, enable=True)
        content = (self.root / 'deep-links.pyz').read_bytes()
        links.ensure(self.root)
        self.assertEqual((self.root / 'deep-links.pyz').read_bytes(), content)
        self.assertEqual(json.loads((self.root / 'installation.json').read_text())['version'], '9.0.0')
        links.load_task(self.root, *links.parse_url(link.url))

    def test_broken_registration_is_repaired_without_replacing_program(self):
        desktop = self.desktop()
        links.ensure(self.root, enable=True)
        before = (self.root / 'deep-links.pyz').stat().st_mtime_ns
        (self.root / 'association-test').unlink()
        links.ensure(self.root)
        self.assertEqual((self.root / 'deep-links.pyz').stat().st_mtime_ns, before)
        self.assertEqual(desktop['register'].call_count, 2)

    def test_failed_registration_retains_opt_in_for_the_next_hook(self):
        desktop = self.desktop()
        desktop['register'].side_effect = OSError('desktop unavailable')
        with self.assertRaises(OSError):
            links.ensure(self.root, enable=True)
        self.assertTrue(json.loads((self.root / 'installation.json').read_text())['enabled'])
        self.assertTrue((self.root / 'deep-links.pyz').is_file())

    def test_invalid_install_metadata_is_not_replaced(self):
        self.root.mkdir()
        state = self.root / 'installation.json'
        state.write_text('{bad JSON')
        with self.assertRaises(ValueError):
            links.ensure(self.root, enable=True)
        self.assertEqual(state.read_text(), '{bad JSON')

    def test_uninstall_disables_future_hooks_and_retains_tasks(self):
        self.desktop()
        link = links.create(self.root, self.batch())[0]
        links.ensure(self.root, enable=True)
        with mock.patch.object(registration, 'unregister') as remove:
            links.uninstall(self.root)
        remove.assert_called_once()
        self.assertEqual(links.ensure(self.root), {'status': 'disabled'})
        links.load_task(self.root, *links.parse_url(link.url))
        links.clean(self.root, links.parse_url(link.url)[1])
        with self.assertRaises(FileNotFoundError):
            links.load_task(self.root, *links.parse_url(link.url))

    @unittest.skipIf(os.name == 'nt', 'POSIX locking path')
    def test_two_installers_cannot_hold_the_user_lock(self):
        with links.installation_lock(self.root):
            with self.assertRaises(BlockingIOError):
                with links.installation_lock(self.root):
                    self.fail('second installer acquired the lock')

    def test_linux_association_cleanup_preserves_other_defaults_and_bytes(self):
        path = self.base / 'mimeapps.list'
        original = ('# keep this comment\r\n[Default Applications]\r\n'
                    'text/plain=editor.desktop;\r\n'
                    'x-scheme-handler/smartkit=smartkit-deep-links.desktop;other.desktop;\r\n'
                    'x-scheme-handler/https=browser.desktop;\r\n')
        path.write_bytes(original.encode())
        registration._remove_linux_association(path)
        self.assertEqual(path.read_bytes(), original.replace('smartkit-deep-links.desktop;', '').encode())

    def test_windows_quoting_and_linux_exec_have_no_shell_command(self):
        interpreter = Path('C:/User Folder/Python/pythonw.exe')
        archive = Path('C:/User Folder/SmartKit/deep-links.pyz')
        windows = registration.windows_command(interpreter, archive)
        self.assertIn('"%1"', windows)
        self.assertNotIn('cmd.exe', windows)
        linux = registration.linux_entry(Path('/home/中文 user/python'), Path('/home/中文 user/100%/links.pyz'))
        self.assertIn('100%%', linux)
        self.assertIn('Terminal=false', linux)
        self.assertIn('open %u', linux)
        self.assertNotIn('sh -c', linux)

    def test_relative_xdg_home_is_ignored(self):
        with mock.patch.dict(os.environ, XDG_DATA_HOME='relative-directory'), \
                mock.patch.object(sys, 'platform', 'linux'):
            self.assertEqual(registration.data_root(), Path.home() / '.local/share/smartkit/deep-links')

    def test_hook_entries_use_the_same_quiet_maintainer_in_every_harness(self):
        for harness in ('codex', 'qoder', 'cursor', 'copilot'):
            value = json.loads((ROOT / 'hooks' / (harness + '.json')).read_text())
            text = json.dumps(value)
            self.assertIn('runtime', text)
            self.assertIn('deep-links', text)
            self.assertIn('ensure --quiet', text)

    def test_cross_platform_hook_launcher_has_working_help(self):
        launcher = SOURCE / 'dispatch.cmd'
        command = (['cmd.exe', '/d', '/c', str(launcher), '--help'] if os.name == 'nt'
                   else ['sh', '-c', '"$1" --help', 'smartkit-links-hook', str(launcher)])
        result = subprocess.run(command, cwd=self.base, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('usage:', result.stdout.lower())

    def test_http_previews_are_read_only_and_reject_foreign_hosts(self):
        environment = dict(os.environ, LOCALAPPDATA=str(self.base), XDG_DATA_HOME=str(self.base))
        if sys.platform == 'win32':
            root = self.base / 'SmartKit/DeepLinks'
        elif sys.platform == 'darwin':
            self.skipTest('macOS ignores these directory overrides')
        else:
            root = self.base / 'smartkit/deep-links'
        batch = links.create(root, self.batch())
        manifest = self.base / 'links.json'
        manifest.write_text(json.dumps([links.asdict(link) for link in batch]))
        process = subprocess.Popen([sys.executable, str(SOURCE / 'deep_links.py'),
                                    'serve', '--input', str(manifest)], env=environment,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            line = process.stdout.readline()
            if not line:
                self.fail(process.stderr.read())
            address = json.loads(line)['links'][0]['url']
            with urllib.request.urlopen(address, timeout=5) as response:
                self.assertIn(b'timeout', response.read())
            request = urllib.request.Request(address, method='HEAD')
            with urllib.request.urlopen(request, timeout=5) as response:
                self.assertEqual(response.read(), b'')
                self.assertEqual(response.status, 200)
            request = urllib.request.Request(address, headers={'Host': 'foreign.example'})
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request, timeout=5)
            self.assertEqual(error.exception.code, 403)
            folder, record = links.load_task(root, *links.parse_url(batch[0].url))
            self.assertFalse((folder / 'vscode-launch.log').exists())
        finally:
            process.terminate()
            process.communicate(timeout=5)


class WindowsAdapterTests(unittest.TestCase):
    def setUp(self):
        self.keys = {}
        test = self

        class Key:
            def __init__(self, root, path):
                self.identity = (root, path)
            def __enter__(self):
                return self
            def __exit__(self, *arguments):
                return False

        def create(root, path):
            parts = path.split('\\')
            for size in range(len(registration.REGISTRY_KEY.split('\\')), len(parts) + 1):
                self.keys.setdefault((root, '\\'.join(parts[:size])), {})
            return Key(root, path)

        def open_key(root, path):
            if (root, path) not in self.keys:
                raise FileNotFoundError(path)
            return Key(root, path)

        def query(key, name):
            try:
                return test.keys[key.identity][name], 1
            except KeyError:
                raise FileNotFoundError(name)

        fake = types.SimpleNamespace(HKEY_CURRENT_USER='HKCU', HKEY_CLASSES_ROOT='HKCR', REG_SZ=1,
                                     CreateKey=create, OpenKey=open_key, QueryValueEx=query,
                                     SetValueEx=lambda key, name, reserved, kind, value: self.keys[key.identity].__setitem__(name, value),
                                     DeleteKey=lambda root, path: self.keys.pop((root, path)))
        self.fake = fake
        self.patches = [mock.patch.dict(sys.modules, winreg=fake), mock.patch.object(sys, 'platform', 'win32'),
                        mock.patch.object(registration, '_notify_windows_association')]
        for patch in self.patches:
            patch.start()
            self.addCleanup(patch.stop)

    def test_only_current_user_keys_are_written_and_registration_is_read_back(self):
        interpreter, archive = Path('Python/pythonw.exe'), Path('SmartKit/deep-links.pyz')
        registration.register(interpreter, archive, {})
        self.assertTrue(all(root == 'HKCU' for root, path in self.keys))
        self.assertEqual(registration.ownership({}), 'owned')
        self.assertTrue(registration.registration_matches(interpreter, archive, {}))
        registration.unregister({})
        self.assertEqual(self.keys, {})

    def test_machine_and_user_foreign_handlers_are_not_overwritten(self):
        for root, path in (('HKCR', 'smartkit'), ('HKCU', registration.REGISTRY_KEY)):
            self.keys.clear()
            self.keys[root, path] = {'': 'foreign'}
            before = dict(self.keys)
            self.assertEqual(registration.ownership({}), 'foreign')
            with self.assertRaises(FileExistsError):
                registration.register(Path('python'), Path('program.pyz'), {})
            self.assertEqual(self.keys, before)

    def test_windows_user_choice_is_respected(self):
        for value in ('another.app', 42):
            self.keys['HKCU', registration.USER_CHOICE_KEY] = {'ProgId': value}
            self.assertEqual(registration.ownership({}), 'foreign')
            with self.assertRaises(FileExistsError):
                registration.register(Path('python'), Path('program.pyz'), {})


if __name__ == '__main__':
    unittest.main()
