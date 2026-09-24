from __future__ import annotations

import json
import io
import os
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'runtime/ponytail/state.py'


class PonytailStateTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.environment = dict(os.environ)
        self.environment.pop('PONYTAIL_DEFAULT_MODE', None)
        for key in ('APPDATA', 'LOCALAPPDATA', 'XDG_CONFIG_HOME', 'XDG_STATE_HOME'):
            self.environment[key] = self.temporary.name

    def command(self, *arguments):
        result = subprocess.run(
            [sys.executable, str(STATE), *arguments], capture_output=True,
            text=True, env=self.environment, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_current_mode_is_isolated_from_defaults_and_other_sessions(self):
        first = self.command('init', '--harness', 'codex', '--session-id', 'first')
        second = self.command('init', '--harness', 'codex', '--session-id', 'second')
        self.assertEqual(first['mode'], 'full')
        self.command('set', '--handle', first['handle'], 'ultra')
        self.command('default', 'lite')
        self.assertEqual(self.command('show', '--handle', first['handle'])['mode'], 'ultra')
        self.assertEqual(self.command('show', '--handle', second['handle'])['mode'], 'full')
        self.assertEqual(self.command('init', '--harness', 'codex', '--session-id', 'first'),
                         {'handle': first['handle'], 'mode': 'ultra'})
        self.assertEqual(self.command('init', '--harness', 'codex', '--session-id', 'third')['mode'],
                         'lite')

    def test_children_inherit_once_and_then_change_independently(self):
        parent = self.command('init', '--harness', 'codex', '--session-id', 'parent')
        self.command('set', '--handle', parent['handle'], 'off')
        child = self.command('fork', '--handle', parent['handle'])
        sibling = self.command('fork', '--handle', parent['handle'])
        self.assertEqual(child['mode'], 'off')
        self.assertNotEqual(child['handle'], sibling['handle'])
        self.command('set', '--handle', parent['handle'], 'full')
        self.command('set', '--handle', child['handle'], 'ultra')
        self.assertEqual(self.command('show', '--handle', parent['handle'])['mode'], 'full')
        self.assertEqual(self.command('show', '--handle', sibling['handle'])['mode'], 'off')
        self.assertEqual(self.command('show', '--handle', child['handle'])['mode'], 'ultra')

    def test_native_session_hook_restores_each_hosts_current_handle(self):
        for harness, identity_key in (('codex', 'session_id'), ('copilot', 'sessionId'),
                                      ('cursor', 'conversation_id'), ('qoder', 'session_id')):
            with self.subTest(harness=harness):
                self.command('default', 'full')
                initial = self.command('init', '--harness', harness, '--session-id', 'native')
                self.command('set', '--handle', initial['handle'], 'ultra')
                self.command('default', 'off')
                environment = dict(self.environment, PLUGIN_ROOT=str(ROOT),
                                   PLUGIN_DATA=self.temporary.name)
                result = subprocess.run(
                    [sys.executable, str(ROOT / 'runtime/rules/dispatch.py'),
                     '--harness', harness, '--event', 'session'],
                    input=json.dumps({identity_key: 'native', 'source': 'resume'}),
                    text=True, capture_output=True, env=environment, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                context = (output.get('additionalContext') or output.get('additional_context')
                           or output['hookSpecificOutput']['additionalContext'])
                self.assertIn(initial['handle'], context)
                self.assertIn('mode: ultra', context)
                self.assertIn('Before any delegation, load the ponytail Skill', context)
                self.assertIn('non-coding tasks and off mode', context)
                self.assertNotIn('## Ladder', context)

    def test_environment_override_only_initializes_new_sessions(self):
        self.command('default', 'lite')
        self.environment['PONYTAIL_DEFAULT_MODE'] = 'ultra'
        first = self.command('init', '--harness', 'codex', '--session-id', 'first')
        self.assertEqual(first['mode'], 'ultra')
        self.command('set', '--handle', first['handle'], 'off')
        result = self.command('default', 'full')
        self.assertEqual(result, {'defaultMode': 'full', 'effectiveDefaultMode': 'ultra'})
        self.assertEqual(self.command('init', '--harness', 'codex', '--session-id', 'first')['mode'],
                         'off')

    def test_missing_or_invalid_state_is_not_silently_replaced(self):
        config = Path(self.temporary.name) / 'smartkit/ponytail.json'
        config.parent.mkdir(parents=True)
        config.write_text('{broken', encoding='utf-8')
        result = subprocess.run(
            [sys.executable, str(STATE), 'default', 'lite'], capture_output=True,
            text=True, env=self.environment, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn('invalid Ponytail JSON', result.stderr)
        self.assertEqual(config.read_text(), '{broken')
        result = subprocess.run(
            [sys.executable, str(STATE), 'set', '--handle', 'a' * 64, 'full'],
            capture_output=True, text=True, env=self.environment, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn('state is missing', result.stderr)

    def test_compaction_restores_mode_without_reinitializing_from_default(self):
        for harness, identity_key in (('cursor', 'conversation_id'), ('copilot', 'sessionId')):
            with self.subTest(harness=harness):
                current = self.command('init', '--harness', harness, '--session-id', 'compact')
                self.command('set', '--handle', current['handle'], 'lite')
                self.command('default', 'off')
                environment = dict(self.environment, PLUGIN_ROOT=str(ROOT),
                                   PLUGIN_DATA=self.temporary.name)
                restored = None
                for event in ('compact', 'tool'):
                    result = subprocess.run(
                        [sys.executable, str(ROOT / 'runtime/rules/dispatch.py'),
                         '--harness', harness, '--event', event],
                        input=json.dumps({identity_key: 'compact'}), text=True,
                        capture_output=True, env=environment, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    restored = json.loads(result.stdout)
                self.assertIn(current['handle'], str(restored))
                self.assertIn('mode: lite', str(restored))

    def test_hook_without_native_id_reports_unavailable_without_creating_state(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'runtime/rules/dispatch.py'),
             '--harness', 'codex', '--event', 'session'],
            input='{}', text=True, capture_output=True,
            env=dict(self.environment, PLUGIN_ROOT=str(ROOT)), check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('host supplied no native conversation ID', result.stdout)
        self.assertFalse((Path(self.temporary.name) / 'smartkit').exists())

    def test_concurrent_initialization_publishes_one_complete_choice(self):
        processes = [subprocess.Popen(
            [sys.executable, str(STATE), 'init', '--harness', 'codex', '--session-id', 'shared'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.environment,
        ) for _ in range(4)]
        results = []
        for process in processes:
            output, error = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, error)
            results.append(json.loads(output))
        self.assertTrue(all(result == results[0] for result in results))
        self.assertEqual(results[0]['mode'], 'full')

    def test_invalid_environment_does_not_partially_change_saved_default(self):
        self.command('default', 'lite')
        self.environment['PONYTAIL_DEFAULT_MODE'] = 'review'
        result = subprocess.run(
            [sys.executable, str(STATE), 'default', 'ultra'], capture_output=True,
            text=True, env=self.environment, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.environment.pop('PONYTAIL_DEFAULT_MODE')
        self.assertEqual(self.command('default')['defaultMode'], 'lite')

    def test_saved_preferences_use_the_platforms_config_directory(self):
        root = Path(self.temporary.name)
        self.environment['APPDATA'] = str(root / 'windows')
        self.environment['XDG_CONFIG_HOME'] = str(root / 'xdg')
        self.command('default', 'lite')
        expected = root / ('windows' if os.name == 'nt' else 'xdg') / 'smartkit/ponytail.json'
        self.assertTrue(expected.is_file(), str(expected))
        self.assertEqual(json.loads(expected.read_text())['defaultMode'], 'lite')

    def test_failed_write_reports_failure_and_preserves_current_mode(self):
        current = self.command('init', '--harness', 'codex', '--session-id', 'write-failure')
        self.command('set', '--handle', current['handle'], 'ultra')
        arguments = [str(STATE), 'set', '--handle', current['handle'], 'off']
        with mock.patch.dict(os.environ, self.environment, clear=True), \
                mock.patch.object(sys, 'argv', arguments), \
                mock.patch('os.replace', side_effect=OSError('injected write failure')), \
                redirect_stderr(io.StringIO()) as error, \
                self.assertRaises(SystemExit) as stopped:
            runpy.run_path(str(STATE), run_name='__main__')
        self.assertEqual(stopped.exception.code, 1)
        self.assertIn('injected write failure', error.getvalue())
        self.assertEqual(self.command('show', '--handle', current['handle'])['mode'], 'ultra')

    def test_invalid_saved_mode_is_not_silently_overwritten(self):
        config = Path(self.temporary.name) / 'smartkit/ponytail.json'
        config.parent.mkdir(parents=True)
        original = '{"defaultMode":"review","other":"keep"}'
        config.write_text(original, encoding='utf-8')
        result = subprocess.run(
            [sys.executable, str(STATE), 'default', 'lite'], capture_output=True,
            text=True, env=self.environment, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn('Ponytail mode must be', result.stderr)
        self.assertEqual(config.read_text(encoding='utf-8'), original)


if __name__ == '__main__':
    unittest.main()
