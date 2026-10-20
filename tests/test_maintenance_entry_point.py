"""Verify the maintenance owner's CLI without any setup implementation available."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MaintenanceEntryPointTests(unittest.TestCase):
    def test_standalone_binding_rule_sync_and_refused_full_sync(self):
        with tempfile.TemporaryDirectory(prefix='maintenance owner ') as directory:
            base = Path(directory)
            plugin = base / 'plugin'
            for relative in ('skills/maintain-project-config', 'setup-assets', 'runtime/project_state'):
                shutil.copytree(ROOT / relative, plugin / relative)
            shutil.copyfile(ROOT / 'skills/registry.json', plugin / 'skills/registry.json')
            shutil.copyfile(ROOT / 'VERSION', plugin / 'VERSION')
            for skill in (ROOT / 'skills').glob('rule-*'):
                shutil.copytree(skill, plugin / 'skills' / skill.name)
            target = base / 'project'
            (target / '.agents/rules').mkdir(parents=True)
            config = target / '.agents/config.json'
            config.write_text('{"setupVersion":"1.2.21"}', encoding='utf-8')
            (target / '.agents/rules/local.md').write_text('# Local policy\n', encoding='utf-8')
            entry = plugin / 'skills/maintain-project-config/scripts/maintain.py'

            def run(*arguments):
                return subprocess.run(
                    [sys.executable, '-B', str(entry), *arguments, '--target', str(target)],
                    cwd=base, capture_output=True, text=True, timeout=20,
                )

            inspected = run('inspect')
            self.assertEqual(inspected.returncode, 0, inspected.stderr)
            self.assertTrue(json.loads(inspected.stdout)['selection_required'])
            bound = run('bind', '--mode', 'local')
            self.assertEqual(bound.returncode, 0, bound.stderr)
            drift = run('sync-project-rules', '--check')
            self.assertEqual(drift.returncode, 1, drift.stderr)
            applied = run('sync-project-rules')
            self.assertEqual(applied.returncode, 0, applied.stderr)
            clean = run('sync-project-rules', '--check')
            self.assertEqual(clean.returncode, 0, clean.stderr)
            self.assertIn('local.md', (target / 'AGENTS.md').read_text(encoding='utf-8'))
            refused = run('sync-project')
            self.assertEqual(refused.returncode, 2)
            self.assertIn('established project mapping ownership', refused.stderr)
            self.assertEqual(json.loads(config.read_text())['setupVersion'], '1.2.21')
            self.assertFalse((plugin / 'skills/setup-project-agents').exists())

            # Exercise the bundled fallback without relying on the host's tomllib.
            probe = (
                'import sys\n'
                'sys.modules["tomllib"] = None\n'
                'sys.path.insert(0, sys.argv[1])\n'
                'import project_config\n'
                'from project_state.structured import parse_document\n'
                'assert parse_document("value = 7", "toml") == {"value": 7}\n'
                'assert not any(name.startswith("agents_setup") for name in sys.modules)\n'
            )
            result = subprocess.run(
                [sys.executable, '-B', '-c', probe, str(entry.parent)], cwd=base,
                capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
