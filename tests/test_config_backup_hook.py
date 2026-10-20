"""Per-session backup discovery and explicitly authorized restoration guidance."""
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

    def test_new_checkout_requests_configuration_address_without_guessing(self):
        with mock.patch.object(self.checker.subprocess, 'run', side_effect=AssertionError('no Git lookup')):
            findings, context = self.checker.check_project_configuration(self.target)
        self.assertEqual([finding.code for finding in findings], ['project-config-restore'])
        self.assertIn('Git address, branch and project entry', findings[0].guidance)
        self.assertIn('do not scan known repositories', context)
        self.assertIn('defer and continue', findings[0].guidance)
        self.assertIn('target ' + json.dumps(str(self.target)), context)
        self.assertFalse((self.target / '.agents').exists())

    def test_copied_binding_without_receipt_still_requests_address(self):
        self.write(self.target, '.agents/config.json', json.dumps({'maintenance': self.binding}).encode())
        findings, context = self.checker.check_project_configuration(self.target)
        self.assertEqual(findings[0].code, 'project-config-restore')
        self.assertIn('even if a copied project config contains an old binding', context)

    def test_local_modes_and_non_project_directories_do_not_request_backup(self):
        for mode in ('local', 'local-only'):
            self.write(self.target, '.agents/config.json', json.dumps({'maintenance': {'mode': mode}}).encode())
            self.assertEqual(self.checker.check_project_configuration(self.target), ((), ''))
        self.assertEqual(self.checker.check_project_configuration(self.root / 'not-a-project'), ((), ''))

    def test_unchanged_backup_is_silent_and_local_drift_is_detected_read_only(self):
        self.established()
        self.assertEqual(self.checker.check_project_configuration(self.target), ((), ''))
        self.write(self.target, '.cursor/mcp.json', b'{"local":true}')
        before = (self.target / '.cursor/mcp.json').read_bytes()
        findings, context = self.checker.check_project_configuration(self.target)
        self.assertEqual(findings[0].code, 'project-config-sync')
        self.assertIn('automatic configuration synchronization as false', context)
        self.assertEqual((self.target / '.cursor/mcp.json').read_bytes(), before)

    def test_source_changes_and_deleted_scope_are_detected(self):
        self.established()
        self.write(self.entry, 'files/.cursor/mcp.json', b'{"source":"new"}')
        self.assertEqual(self.checker.check_project_configuration(self.target)[0][0].code, 'project-config-sync')
        self.write(self.entry, 'manifest.json', b'{"version":2,"files":[],"directories":[]}')
        self.assertEqual(self.checker.check_project_configuration(self.target)[0][0].code, 'project-config-sync')

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
                self.assertIn('automatic configuration synchronization as true', context)
                self.assertIn('update command before inspect/apply', context)
                self.assertIn('without applying a stale copy', context)
                self.assertIn('Do not adopt local drift, publish, regenerate MCP', context)

    def test_new_checkout_detection_is_not_hidden_by_daily_cache(self):
        with mock.patch.object(self.checker, '_run_daily_hook', return_value=self.checker.HookResult(False)), \
                mock.patch.object(self.checker, 'check_project_codegraph', return_value=()):
            for _ in range(2):
                result = self.checker.run_hook('codex', Path('unused'), project_root=self.target)
                self.assertTrue(result.requires_user_prompt)
                self.assertEqual(result.findings[0].code, 'project-config-restore')

    def test_malformed_receipt_is_reported_without_changing_it(self):
        self.established()
        self.write(self.target, str(backup.SYNC_PATH), b'{}')
        findings, _ = self.checker.check_project_configuration(self.target)
        self.assertEqual(findings[0].code, 'project-config-error')
        self.assertEqual((self.target / backup.SYNC_PATH).read_bytes(), b'{}')


if __name__ == '__main__':
    unittest.main()
