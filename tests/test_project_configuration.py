from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/setup-project-agents/scripts'))
from agents_setup.catalog import load_catalog


class ProjectConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / 'skills/setup-project-agents/scripts/agents_setup/project_configuration.py').is_file(),
                        'project configuration projection is not implemented')
        self.module = importlib.import_module('agents_setup.project_configuration')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / 'target'
        self.entry = self.root / 'entry'
        self.target.mkdir()
        self.entry.mkdir()
        self.catalog = load_catalog(ROOT)
        self.binding = {'mode': 'repository', 'repository': 'user/config', 'branch': 'main', 'entry': 'app'}
        self.write(self.target, '.agents/config.json', json.dumps({'maintenance': self.binding, 'setupVersion': '1.2.21'}))
        self.resolve = mock.patch.object(self.module, 'entry_root', return_value=self.entry)
        self.resolve.start()
        self.addCleanup(self.resolve.stop)

    @staticmethod
    def write(root, path, value):
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(value, encoding='utf-8')

    def initialize(self):
        self.write(self.target, '.agents/rules/personal.md', '# Personal\n')
        self.module.initialize_entry(self.target, self.entry, ['.agents/rules/personal.md'], self.catalog)
        self.module.apply(self.target, self.catalog)

    def test_import_and_apply_preserve_local_records_and_unselected_files(self):
        self.initialize()
        self.write(self.entry, 'files/.agents/rules/personal.md', '# Changed\n')
        self.write(self.target, 'notes.txt', 'keep')
        self.module.apply(self.target, self.catalog)
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Changed\n')
        config = json.loads((self.target / '.agents/config.json').read_text())
        self.assertEqual(config['setupVersion'], '1.2.21')
        self.assertEqual(config['maintenance'], self.binding)
        self.assertEqual((self.target / 'notes.txt').read_text(), 'keep')
        self.assertNotIn('maintenance', json.loads((self.entry / 'config.json').read_text()))

    def test_target_edit_refuses_application_without_changing_either_side(self):
        self.initialize()
        self.write(self.target, '.agents/rules/personal.md', '# Local edit\n')
        self.write(self.entry, 'files/.agents/rules/personal.md', '# Remote edit\n')
        before = (self.target / '.agents/project-config-state.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'conflict'):
            self.module.apply(self.target, self.catalog)
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Local edit\n')
        self.assertEqual((self.target / '.agents/project-config-state.json').read_bytes(), before)

    def test_adoption_requires_unchanged_source_and_explicit_selection(self):
        self.initialize()
        self.write(self.target, '.agents/rules/personal.md', '# Accepted local\n')
        self.module.adopt(self.target, self.catalog, ['.agents/rules/personal.md'], [])
        self.assertEqual((self.entry / 'files/.agents/rules/personal.md').read_text(), '# Accepted local\n')
        self.module.apply(self.target, self.catalog)
        self.write(self.entry, 'files/.agents/rules/personal.md', '# New remote\n')
        self.write(self.target, '.agents/rules/personal.md', '# Different local\n')
        with self.assertRaisesRegex(ValueError, 'source changed'):
            self.module.adopt(self.target, self.catalog, ['.agents/rules/personal.md'], [])

    def test_unmodified_recorded_deletion_is_applied(self):
        self.initialize()
        self.write(self.entry, 'manifest.json', '{"version":1,"files":[]}')
        self.module.apply(self.target, self.catalog)
        self.assertFalse((self.target / '.agents/rules/personal.md').exists())

    def test_retirement_does_not_delete_a_file_now_owned_by_setup(self):
        import hashlib
        from pathlib import PurePosixPath
        from agents_setup.ownership import OwnedAsset, OwnershipState, serialize_ownership
        self.initialize()
        relative = PurePosixPath('.agents/rules/personal.md')
        content = (self.target / relative).read_bytes()
        state = OwnershipState((), (OwnedAsset('file', 'rule', relative, hashlib.sha256(content).hexdigest()),))
        (self.target / '.agents/smartkit.lock.json').write_bytes(serialize_ownership(state))
        self.write(self.entry, 'manifest.json', '{"version":1,"files":[]}')
        with self.assertRaisesRegex(ValueError, 'owned by setup'):
            self.module.apply(self.target, self.catalog)
        self.assertEqual((self.target / relative).read_bytes(), content)

    def test_config_field_retirement_preserves_other_fields(self):
        self.write(self.target, '.agents/config.json', json.dumps({'maintenance': self.binding, 'setupVersion': '1.2.21', 'mcp': []}))
        self.module.initialize_entry(self.target, self.entry, [], self.catalog)
        self.module.apply(self.target, self.catalog)
        self.write(self.entry, 'config.json', '{}')
        self.module.apply(self.target, self.catalog)
        config = json.loads((self.target / '.agents/config.json').read_text())
        self.assertNotIn('mcp', config)
        self.assertIn('maintenance', config)

    def test_agents_generated_section_is_preserved(self):
        self.write(self.target, 'AGENTS.md', '# Instructions\n\n## Project rules\n\nOld index\n\n## Personal\n\nUser rules\n')
        self.module.initialize_entry(self.target, self.entry, ['AGENTS.md'], self.catalog)
        self.module.apply(self.target, self.catalog)
        self.write(self.entry, 'files/AGENTS.md', '# Instructions\n\n## Personal\n\nUpdated personal rules\n')
        self.module.apply(self.target, self.catalog)
        text = (self.target / 'AGENTS.md').read_text()
        self.assertIn('Old index', text)
        self.assertIn('Updated personal rules', text)
        self.assertEqual(text.count('## Project rules'), 1)

    def test_initial_collision_requires_matching_review_token(self):
        self.initialize()
        (self.target / '.agents/project-config-state.json').unlink()
        self.write(self.target, '.agents/rules/personal.md', '# Existing independent\n')
        observation = self.module.inspect(self.target, self.catalog)
        self.assertTrue(observation['conflicts'])
        with self.assertRaisesRegex(ValueError, 'conflict'):
            self.module.apply(self.target, self.catalog)
        with self.assertRaises(ValueError):
            self.module.apply(self.target, self.catalog, accept_existing='stale')
        self.module.apply(self.target, self.catalog, accept_existing=observation['fingerprint'])
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')

    def test_source_cannot_export_local_state_or_unsafe_paths(self):
        self.initialize()
        for path in ('../escape', '.agents/smartkit.lock.json', '.codex/config.toml', '.git/config'):
            self.write(self.entry, 'manifest.json', json.dumps({'version': 1, 'files': [path]}))
            with self.assertRaises(ValueError):
                self.module.inspect(self.target, self.catalog)
        self.write(self.entry, 'manifest.json', '{"version":1,"files":[]}')
        self.write(self.entry, 'config.json', '{"setupVersion":"9.0.0"}')
        with self.assertRaises(ValueError):
            self.module.inspect(self.target, self.catalog)

    def test_empty_receipt_is_invalid_and_prior_empty_application_cannot_accept_collisions(self):
        self.initialize()
        self.write(self.target, '.agents/project-config-state.json', '{}')
        with self.assertRaisesRegex(ValueError, 'state is invalid'):
            self.module.inspect(self.target, self.catalog)
        (self.target / '.agents/project-config-state.json').unlink()
        self.write(self.entry, 'manifest.json', '{"version":1,"files":[]}')
        self.module.apply(self.target, self.catalog)
        self.write(self.entry, 'manifest.json', '{"version":1,"files":[".agents/rules/personal.md"]}')
        self.write(self.target, '.agents/rules/personal.md', '# Later target work\n')
        report = self.module.inspect(self.target, self.catalog)
        with self.assertRaisesRegex(ValueError, 'conflict'):
            self.module.apply(self.target, self.catalog, accept_existing=report['fingerprint'])

    def test_source_symlink_is_refused(self):
        self.initialize()
        path = self.entry / 'files/.agents/rules/personal.md'
        path.unlink()
        outside = self.root / 'outside'
        outside.write_text('private')
        try:
            path.symlink_to(outside)
        except OSError:
            self.skipTest('symlinks unavailable')
        with self.assertRaises(ValueError):
            self.module.inspect(self.target, self.catalog)

    def test_generated_outputs_reach_source_before_target(self):
        self.initialize()
        generated = {'.agents/rules/personal.md': b'# Generated replacement\n'}
        state_file = self.module.save_generated(self.target, self.catalog, generated, [])
        self.assertEqual((self.entry / 'files/.agents/rules/personal.md').read_bytes(), generated['.agents/rules/personal.md'])
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')
        self.assertEqual(state_file.path.as_posix(), '.agents/project-config-state.json')

    def test_full_setup_saves_generated_sources_and_freezes_source_drift(self):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        from test_setup_cli import SetupCliTest
        import setup_project_agents
        self.initialize()
        helper = SetupCliTest()
        session = helper.private_session(self.root)
        with redirect_stdout(StringIO()):
            self.assertEqual(helper.prepare(self.target, session), 0)
        request = json.loads((session / 'request.json').read_text())
        self.assertIn('configuration_fingerprint', request)
        helper.write_generated_outputs(session)
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(setup_project_agents.main(['finish', '--target', str(self.target),
                '--session', str(session), *helper.source_args()]), 0)
        self.assertEqual((self.entry / 'files/.agents/rules/tools.md').read_bytes(),
                         (self.target / '.agents/rules/tools.md').read_bytes())
        self.assertEqual(self.module.inspect(self.target, self.catalog)['changes'], [])
        session = helper.private_session(self.root)
        with redirect_stdout(StringIO()):
            self.assertEqual(helper.prepare(self.target, session), 0)
        helper.write_generated_outputs(session)
        self.write(self.entry, 'files/.agents/rules/personal.md', '# Concurrent source edit\n')
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
            self.assertEqual(setup_project_agents.main(['finish', '--target', str(self.target),
                '--session', str(session), *helper.source_args()]), 2)
        self.assertIn('configuration', errors.getvalue())
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')

    def test_full_setup_retains_source_and_rolls_back_target_on_late_source_drift(self):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        from test_setup_cli import SetupCliTest
        import setup_project_agents
        self.initialize()
        before = {p.relative_to(self.target): p.read_bytes() for p in self.target.rglob('*') if p.is_file()}
        helper = SetupCliTest()
        session = helper.private_session(self.root)
        with redirect_stdout(StringIO()):
            self.assertEqual(helper.prepare(self.target, session), 0)
        helper.write_generated_outputs(session)
        original_apply = setup_project_agents.apply_plan
        def apply_after_source_edit(target, plan, **kwargs):
            self.write(self.entry, 'files/.agents/rules/tools.md', '# Concurrent source edit\n')
            return original_apply(target, plan, **kwargs)
        with mock.patch.object(setup_project_agents, 'apply_plan', side_effect=apply_after_source_edit):
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
                self.assertEqual(setup_project_agents.main(['finish', '--target', str(self.target),
                    '--session', str(session), *helper.source_args()]), 2)
        self.assertIn('configuration', errors.getvalue())
        self.assertEqual({p.relative_to(self.target): p.read_bytes() for p in self.target.rglob('*') if p.is_file()}, before)
        self.assertEqual((self.entry / 'files/.agents/rules/tools.md').read_text(), '# Concurrent source edit\n')

    def test_native_agent_adoption_saves_source_before_target_transaction(self):
        import adopt_project_agents as adoption
        from test_setup_adoption import AgentAdoptionTest
        self.initialize()
        helper = AgentAdoptionTest()
        helper.root, helper.target = self.root, self.target
        helper.native('codex', b'model = "before"\n')
        manifest = helper.manifest({'codex': b'model = "after"\n'})
        original_apply = adoption.apply_plan
        def observed_apply(target, plan, **kwargs):
            self.assertEqual((self.entry / 'files/.agents/agents/local.codex.toml').read_bytes(), b'model = "after"\n')
            return original_apply(target, plan, **kwargs)
        with mock.patch.object(adoption, 'apply_plan', side_effect=observed_apply):
            adoption.apply(self.target, manifest)
        self.assertEqual(self.module.inspect(self.target, self.catalog)['changes'], [])

    def test_public_inspection_and_local_binding_preserve_config(self):
        import workflow
        from contextlib import redirect_stdout
        from io import StringIO
        self.write(self.target, '.agents/config.json', '{"setupVersion":"1.2.21","mcp":[]}')
        output = StringIO()
        with redirect_stdout(output):
            status = workflow.main(['project-config', 'inspect', '--target', str(self.target)])
        self.assertEqual(status, 0)
        self.assertTrue(json.loads(output.getvalue())['selection_required'])
        with redirect_stdout(StringIO()):
            self.assertEqual(workflow.main(['project-config', 'bind', '--mode', 'local', '--target', str(self.target)]), 0)
        config = json.loads((self.target / '.agents/config.json').read_text())
        self.assertEqual(config, {'setupVersion': '1.2.21', 'mcp': [], 'maintenance': {'mode': 'local'}})

    def test_publish_failure_reports_retained_commit_and_preserves_local_application(self):
        import workflow
        from agents_setup import project_configuration_cli as cli
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        self.initialize()
        commit = 'a' * 40
        runtime = mock.Mock()
        runtime.commit_scope.return_value = commit
        runtime.publish.side_effect = OSError('remote unavailable')
        with mock.patch.object(cli.configuration, 'repository_runtime', return_value=runtime), \
                mock.patch.object(cli, 'synchronize_project', return_value=mock.Mock(check='clean')):
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
                result = workflow.main(['project-config', 'publish', '--target', str(self.target),
                    '--path', 'projects/app/manifest.json', '--message', 'Update source'])
        self.assertEqual(result, 2)
        self.assertIn(commit, errors.getvalue())
        self.assertIn('remote unavailable', errors.getvalue())
        self.assertEqual(self.module.inspect(self.target, self.catalog)['changes'], [])

    def test_local_excludes_ignore_inherited_git_routing(self):
        import os
        import subprocess
        from agents_setup.project_configuration_cli import exclude_local
        subprocess.run(['git', '-C', str(self.target), 'init'], check=True, capture_output=True)
        unrelated = self.root / 'unrelated'
        unrelated.mkdir()
        subprocess.run(['git', '-C', str(unrelated), 'init'], check=True, capture_output=True)
        before = (unrelated / '.git/info/exclude').read_bytes()
        with mock.patch.dict(os.environ, {'GIT_DIR': str(unrelated / '.git'), 'GIT_WORK_TREE': str(unrelated)}):
            self.assertEqual(exclude_local(self.target, ['.agents/config.json']), [])
        self.assertIn('/.agents/config.json', (self.target / '.git/info/exclude').read_text())
        self.assertEqual((unrelated / '.git/info/exclude').read_bytes(), before)

    def test_public_maintenance_round_trip_with_real_local_git(self):
        from test_project_config_repository import RepositoryGitTests
        from test_setup_cli import SetupCliTest
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        import setup_project_agents
        import workflow
        fixture = RepositoryGitTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.resolve.stop()
        fixture.git(self.target, 'init', '--initial-branch=main')
        self.write(self.target, '.agents/config.json', '{}')
        self.write(self.target, '.agents/rules/personal.md', '# Imported\n')
        def command(*arguments):
            out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = workflow.main(['project-config', *arguments, '--target', str(self.target)])
            self.assertEqual(code, 0, err.getvalue())
            return json.loads(out.getvalue())
        result = command('bind', '--mode', 'repository', '--repository', 'alice/config', '--branch', 'main',
                         '--entry', 'app', '--file', '.agents/rules/personal.md')
        entry = Path(result['source'])
        command('apply')
        helper = SetupCliTest()
        session = helper.private_session(self.root)
        with redirect_stdout(StringIO()):
            self.assertEqual(helper.prepare(self.target, session), 0)
            helper.write_generated_outputs(session)
            self.assertEqual(setup_project_agents.main(['finish', '--target', str(self.target),
                             '--session', str(session), *helper.source_args()]), 0)
        self.assertTrue(command('update')['localChanges'])
        selected = sorted(str(path.relative_to(entry.parent.parent)) for path in entry.rglob('*') if path.is_file())
        arguments = ['publish', '--message', 'Maintain personal project configuration']
        for path in selected:
            arguments.extend(['--path', path])
        published = command(*arguments)
        self.assertTrue(published['published'])
        self.assertEqual(fixture.git(fixture.remote, 'rev-parse', 'main'), published['commit'])
        self.assertEqual(command('inspect')['changes'], [])
        self.assertEqual(fixture.git(self.target, 'check-ignore', '.agents/rules/personal.md'), '.agents/rules/personal.md')
        command('update')


if __name__ == '__main__':
    unittest.main()
