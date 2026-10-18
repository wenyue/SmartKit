"""Contracts for removing user-level MCP entries duplicated by Plugin MCP."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / 'runtime' / 'recommended-tools' / 'user_mcp.py'
REGISTRY_PATH = REPO_ROOT / 'mcp' / 'registry.json'


def load_module():
    spec = importlib.util.spec_from_file_location('test_target_user_mcp', MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UserMcpCleanupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def setUp(self) -> None:
        environment = mock.patch.dict('os.environ')
        environment.start()
        self.addCleanup(environment.stop)
        for name in ('CODEX_HOME', 'COPILOT_HOME', 'QODER_CONFIG_DIR'):
            self.module.os.environ.pop(name, None)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.home = Path(directory.name)

    def test_plugin_server_ids_follow_the_registry(self):
        self.assertEqual(
            self.module.plugin_server_ids(REGISTRY_PATH, 'copilot'),
            ['playwright', 'codegraph'],
        )

    def test_json_harnesses_remove_only_plugin_owned_entries(self):
        for harness, relative in (
            ('copilot', '.copilot/mcp-config.json'),
            ('cursor', '.cursor/mcp.json'),
            ('qoder', '.qoder/settings.json'),
        ):
            with self.subTest(harness=harness):
                path = self.home / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({
                    'mcpServers': {
                        'dart': {'command': 'dart'},
                        'playwright': {'command': 'npx'},
                        'codegraph': {'command': 'codegraph'},
                    },
                    'other': True,
                }), encoding='utf-8')

                notices = self.module.remove_duplicate_user_servers(
                    harness, REGISTRY_PATH, home=self.home,
                )

                self.assertEqual(len(notices), 1)
                self.assertIn('playwright, codegraph', notices[0])
                self.assertEqual(json.loads(path.read_text(encoding='utf-8')), {
                    'mcpServers': {'dart': {'command': 'dart'}},
                    'other': True,
                })
                self.assertEqual(
                    self.module.remove_duplicate_user_servers(
                        harness, REGISTRY_PATH, home=self.home,
                    ),
                    [],
                )

    def test_copilot_honors_copilot_home(self):
        copilot_home = self.home / 'custom'
        copilot_home.mkdir()
        path = copilot_home / 'mcp-config.json'
        path.write_text('{"mcpServers": {"playwright": {}}}', encoding='utf-8')
        self.module.os.environ['COPILOT_HOME'] = str(copilot_home)

        notices = self.module.remove_duplicate_user_servers(
            'copilot', REGISTRY_PATH, home=self.home,
        )

        self.assertEqual(len(notices), 1)
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')), {'mcpServers': {}})

    def test_codex_removes_through_the_codex_cli(self):
        config = self.home / '.codex' / 'config.toml'
        config.parent.mkdir()
        original = (
            '# keep\n'
            'model = "x"\n\n'
            '[mcp_servers.codegraph]\ncommand = "codegraph"\n\n'
            '[mcp_servers.node_repl]\ncommand = "node_repl"\n'
        )
        config.write_text(original, encoding='utf-8')
        calls = []

        def fake_run(command, **_kwargs):
            calls.append(command[1:])
            config.write_text(
                '# keep\nmodel = "x"\n\n[mcp_servers.node_repl]\ncommand = "node_repl"\n',
                encoding='utf-8',
            )
            return subprocess.CompletedProcess(command, 0)

        with mock.patch.object(self.module.shutil, 'which', return_value='codex'):
            notices = self.module.remove_duplicate_user_servers(
                'codex', REGISTRY_PATH, home=self.home, run=fake_run,
            )

        self.assertEqual(calls, [['mcp', 'remove', 'codegraph']])
        self.assertEqual(len(notices), 1)
        self.assertIn('codegraph', notices[0])

    def test_codex_reports_entries_the_cli_left_in_place(self):
        config = self.home / '.codex' / 'config.toml'
        config.parent.mkdir()
        config.write_text('[mcp_servers.playwright]\ncommand = "npx"\n', encoding='utf-8')

        with mock.patch.object(self.module.shutil, 'which', return_value='codex'):
            notices = self.module.remove_duplicate_user_servers(
                'codex', REGISTRY_PATH, home=self.home,
                run=lambda command, **_kwargs: subprocess.CompletedProcess(command, 1),
            )

        self.assertEqual(len(notices), 1)
        self.assertIn('Could not remove', notices[0])

    def test_missing_or_unrelated_configs_produce_no_notice(self):
        for harness in ('codex', 'copilot', 'cursor', 'qoder'):
            with self.subTest(harness=harness):
                self.assertEqual(
                    self.module.remove_duplicate_user_servers(
                        harness, REGISTRY_PATH, home=self.home,
                    ),
                    [],
                )

    def test_invalid_json_is_reported_without_rewriting(self):
        path = self.home / '.cursor' / 'mcp.json'
        path.parent.mkdir()
        path.write_text('{ not json', encoding='utf-8')

        notices = self.module.remove_duplicate_user_servers(
            'cursor', REGISTRY_PATH, home=self.home,
        )

        self.assertEqual(len(notices), 1)
        self.assertIn('Could not remove', notices[0])
        self.assertEqual(path.read_text(encoding='utf-8'), '{ not json')

    def test_qoder_commented_settings_are_reported_without_rewriting(self):
        qoder_home = self.home / 'qoder-config'
        qoder_home.mkdir()
        self.module.os.environ['QODER_CONFIG_DIR'] = str(qoder_home)
        path = qoder_home / 'settings.json'
        commented = '{\n  // team note\n  "mcpServers": {"codegraph": {}}\n}\n'
        path.write_text(commented, encoding='utf-8')

        notices = self.module.remove_duplicate_user_servers(
            'qoder', REGISTRY_PATH, home=self.home,
        )

        self.assertEqual(len(notices), 1)
        self.assertIn('comments', notices[0])
        self.assertEqual(path.read_text(encoding='utf-8'), commented)

        path.write_text('{\n  // no duplicates\n  "ui": {}\n}\n', encoding='utf-8')
        self.assertEqual(
            self.module.remove_duplicate_user_servers('qoder', REGISTRY_PATH, home=self.home),
            [],
        )


if __name__ == '__main__':
    unittest.main()
