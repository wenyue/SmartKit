"""Exercise Hook readers in an installation without either Skill's implementation."""
import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeProjectStateTests(unittest.TestCase):
    def test_hooks_and_status_read_state_without_skill_implementation(self):
        with tempfile.TemporaryDirectory(prefix='runtime readers ') as directory:
            base = Path(directory)
            plugin = base / 'plugin'
            for relative in (
                'runtime/project_state', 'runtime/recommended-tools', 'runtime/local_web',
                'setup-assets', 'skills/setup-project-agents/references/migrations',
            ):
                shutil.copytree(ROOT / relative, plugin / relative)
            shutil.copyfile(ROOT / 'VERSION', plugin / 'VERSION')
            shutil.copyfile(ROOT / 'skills/registry.json', plugin / 'skills/registry.json')
            for skill in (ROOT / 'skills').glob('rule-*'):
                destination = plugin / 'skills' / skill.name
                destination.mkdir()
                shutil.copyfile(skill / 'SKILL.md', destination / 'SKILL.md')
            project = base / 'project'
            (project / '.agents').mkdir(parents=True)
            lock = project / '.agents/smartkit.lock.json'
            lock.write_text('{"sources":[],"assets":[]}', encoding='utf-8')
            (project / '.agents/config.json').write_text(
                '{"setupVersion":"1.2.21"}', encoding='utf-8',
            )
            self.assertFalse((plugin / 'skills/maintain-project-config').exists())
            self.assertFalse((plugin / 'skills/setup-project-agents/scripts').exists())

            probe = textwrap.dedent('''\
                import importlib.abc
                import json
                import sys
                from pathlib import Path

                class RejectSkillImplementation(importlib.abc.MetaPathFinder):
                    def find_spec(self, fullname, path=None, target=None):
                        if fullname.split('.')[0] in {'agents_setup', 'project_config', '_vendor'}:
                            raise AssertionError('runtime imported Skill implementation: ' + fullname)

                sys.meta_path.insert(0, RejectSkillImplementation())
                sys.modules['tomllib'] = None
                plugin, project = map(Path, sys.argv[1:])
                sys.path[:0] = [str(plugin / 'runtime'), str(plugin / 'runtime/recommended-tools')]
                import check_recommended_tools as checker
                import user_mcp
                from local_web.apps.status import setup_snapshot
                from project_state.migrations import SetupStatus, project_setup_version

                assert user_mcp._load_toml('value = 7') == {'value': 7}
                config = project / 'mcp.json'
                original = '{ // comment\\n "mcpServers": {"example": {}},\\n}'
                config.write_text(original)
                assert user_mcp._remove_from_json(config, ['absent']) == []
                try:
                    user_mcp._remove_from_json(config, ['example'])
                except ValueError as error:
                    assert 'comments' in str(error)
                else:
                    raise AssertionError('comment-preservation refusal was lost')
                assert config.read_text() == original

                findings = checker.check_setup_migrations(project)
                assert len(findings) == 1 and findings[0].code == 'setup-required'
                notices = checker.check_project_codegraph(project, 'codex')
                assert len(notices) == 1 and 'CodeGraph is not ready' in notices[0]
                output = json.loads(checker.render_hook_result(
                    checker.HookResult(True, tuple(findings), notices=notices), 'codex'))
                assert output['continue'] is True
                context = output['hookSpecificOutput']['additionalContext']
                assert 'end this turn after requesting consent' in context.lower()
                assert 'An empty action list authorizes no runner invocation' in context
                snapshot = setup_snapshot(project)
                assert snapshot['status'] == 'initialized'
                assert snapshot['setup_version'] == '1.2.21'
                assert snapshot['plugin_version'] == (plugin / 'VERSION').read_text().strip()

                lock = project / '.agents/smartkit.lock.json'
                lock.write_text('{"sources":[],"assets":[{}]}')
                assert setup_snapshot(project)['status'] == 'failed'
                assert 'cannot establish' in checker.check_setup_migrations(project)[0].message
                lock.write_text('{"sources":[],"assets":[]}')
                config = project / '.agents/config.json'
                config.write_text('{"setupVersion":"invalid"}')
                assert setup_snapshot(project)['status'] == 'failed'
                config.unlink()
                assert project_setup_version(project, plugin) is SetupStatus.BASELINE_REQUIRED
                lock.unlink()
                assert project_setup_version(project, plugin) is SetupStatus.UNINITIALIZED
                assert checker.check_setup_migrations(project) == []
                assert checker.check_project_codegraph(project, 'codex') == ()
                assert not any(name.split('.')[0] in {'agents_setup', 'project_config', '_vendor'}
                               for name in sys.modules)
                print('isolated runtime readers passed')
            ''')
            result = subprocess.run(
                [sys.executable, '-B', '-c', probe, str(plugin), str(project)],
                cwd=base, capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), 'isolated runtime readers passed')


if __name__ == '__main__':
    unittest.main()
