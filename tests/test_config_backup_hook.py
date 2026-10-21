"""Startup synchronization only for a checkout with explicit local consent."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_recommended_tools import load_checker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from project_state import config_backup as backup


class ConfigurationBackupHookTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / 'checkout'
        (self.target / '.git').mkdir(parents=True)
        self.entry = self.root / 'config/projects/app'
        self.entry.mkdir(parents=True)
        self.checker = load_checker()
        self.binding = {'mode': 'repository', 'repository': 'alice/config', 'branch': 'main', 'entry': 'app'}

    @staticmethod
    def write(root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def established(self, automatic=False):
        self.write(self.target, '.agents/config.json', json.dumps({'maintenance': self.binding}).encode())
        manifest = {'version': 2, 'files': ['.cursor/mcp.json'], 'directories': []}
        content = b'{"mcpServers":{},"custom":true}\r\n'
        self.write(self.entry, 'manifest.json', json.dumps(manifest).encode())
        self.write(self.entry, 'files/.cursor/mcp.json', content)
        self.write(self.target, '.cursor/mcp.json', content)
        state = {'version': 1, 'binding': self.binding, 'source': str(self.entry),
                 'sourceFingerprint': backup.fingerprint(manifest, {'.cursor/mcp.json': content}),
                 'appliedPaths': ['.cursor/mcp.json'], 'automatic': automatic}
        self.write(self.target, str(backup.SYNC_PATH), json.dumps(state).encode())

    def test_new_checkout_is_silent_without_discovery_or_writes(self):
        with mock.patch.object(self.checker.subprocess, 'run', side_effect=AssertionError('no Git lookup')):
            findings, context = self.checker.check_project_configuration(self.target)
        self.assertEqual((findings, context), ((), ''))
        self.assertFalse((self.target / '.agents').exists())

    def test_copied_binding_without_receipt_is_silent(self):
        self.write(self.target, '.agents/config.json', json.dumps({'maintenance': self.binding}).encode())
        findings, context = self.checker.check_project_configuration(self.target)
        self.assertEqual((findings, context), ((), ''))

    def test_unconfigured_checkout_does_not_parse_project_configuration(self):
        self.write(self.target, '.agents/config.json', b'not JSON')
        self.assertEqual(self.checker.check_project_configuration(self.target), ((), ''))

    def test_local_modes_and_non_project_directories_do_not_request_backup(self):
        for mode in ('local', 'local-only'):
            self.write(self.target, '.agents/config.json', json.dumps({'maintenance': {'mode': mode}}).encode())
            self.assertEqual(self.checker.check_project_configuration(self.target), ((), ''))
        self.assertEqual(self.checker.check_project_configuration(self.root / 'not-a-project'), ((), ''))

    def test_disabled_sync_is_silent_even_with_local_drift(self):
        self.established()
        self.assertEqual(self.checker.check_project_configuration(self.target), ((), ''))
        self.write(self.target, '.cursor/mcp.json', b'{"local":true}')
        before = (self.target / '.cursor/mcp.json').read_bytes()
        self.assertEqual(self.checker.check_project_configuration(self.target), ((), ''))
        self.assertEqual((self.target / '.cursor/mcp.json').read_bytes(), before)

    def test_disabled_sync_does_not_read_source_or_validate_binding(self):
        self.established()
        self.write(self.entry, 'manifest.json', b'not JSON')
        self.write(self.target, '.agents/config.json', b'not JSON')
        self.assertEqual(self.checker.check_project_configuration(self.target), ((), ''))

    def test_automatic_sync_delivers_authorized_update_before_apply_each_session(self):
        self.established(automatic=True)
        with mock.patch.object(self.checker, '_run_daily_hook', return_value=self.checker.HookResult(False)), \
                mock.patch.object(self.checker, 'check_project_codegraph', return_value=()):
            for harness in ('codex', 'cursor', 'copilot', 'qoder'):
                result = self.checker.run_hook(harness, Path('unused'), project_root=self.target)
                self.assertFalse(result.ran)
                self.assertFalse(result.requires_user_prompt)
                value = json.loads(self.checker.render_hook_result(result, harness, delivery='context'))
                context = (value['hookSpecificOutput']['additionalContext'] if harness in {'codex', 'qoder'}
                           else value['additional_context' if harness == 'cursor' else 'additionalContext'])
                self.assertIn('authorized automatic configuration synchronization', context)
                self.assertIn('target ' + json.dumps(str(self.target)), context)
                self.assertIn('update command before inspect/apply', context)
                self.assertIn('without applying a stale copy', context)
                self.assertIn('Do not adopt local drift, publish, regenerate MCP', context)
                self.assertNotIn('ask whether to restore or defer', context)

    def test_new_checkout_stays_silent_across_sessions(self):
        with mock.patch.object(self.checker, '_run_daily_hook', return_value=self.checker.HookResult(False)), \
                mock.patch.object(self.checker, 'check_project_codegraph', return_value=()):
            for _ in range(2):
                result = self.checker.run_hook('codex', Path('unused'), project_root=self.target)
                self.assertFalse(result.requires_user_prompt)
                self.assertEqual(result.findings, ())
                self.assertEqual(self.checker.render_hook_result(result, 'codex'), '')

    def test_malformed_enabled_receipt_is_reported_without_changing_it(self):
        self.established(automatic=True)
        content = b'{"automatic":true}'
        self.write(self.target, str(backup.SYNC_PATH), content)
        findings, _ = self.checker.check_project_configuration(self.target)
        self.assertEqual(findings[0].code, 'project-config-error')
        self.assertEqual((self.target / backup.SYNC_PATH).read_bytes(), content)

    def test_enabled_receipt_cannot_authorize_another_binding(self):
        self.established(automatic=True)
        other = {**self.binding, 'entry': 'other'}
        content = json.dumps({'maintenance': other}).encode()
        self.write(self.target, '.agents/config.json', content)
        findings, context = self.checker.check_project_configuration(self.target)
        self.assertEqual(findings[0].code, 'project-config-error')
        self.assertEqual(context, '')
        self.assertEqual((self.target / '.agents/config.json').read_bytes(), content)

    def test_receipt_without_explicit_consent_is_silent(self):
        for automatic in (False, None, 'true', 1):
            self.write(self.target, str(backup.SYNC_PATH), json.dumps({'automatic': automatic}).encode())
            self.assertEqual(self.checker.check_project_configuration(self.target), ((), ''))


if __name__ == '__main__':
    unittest.main()
