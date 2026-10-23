from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
sys.path.insert(0, str(ROOT / 'skills/maintain-project-config/scripts'))
sys.path.insert(0, str(ROOT / 'skills/setup-project-agents/scripts'))


class ProjectConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / 'skills/maintain-project-config/scripts/project_config/project_configuration.py').is_file(),
                        'project configuration projection is not implemented')
        self.module = importlib.import_module('project_config.project_configuration')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / 'target'
        self.entry = self.root / 'entry'
        self.target.mkdir()
        self.entry.mkdir()
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
        self.module.initialize_entry(self.target, self.entry, ['.agents/rules/personal.md'])
        self.module.apply(self.target)

    def apply_reviewed(self):
        report = self.module.inspect(self.target)
        return self.module.apply(self.target, accept_existing=report['fingerprint'])

    def test_import_and_apply_preserve_local_records_and_unselected_files(self):
        self.initialize()
        self.write(self.entry, 'files/.agents/rules/personal.md', '# Changed\n')
        self.write(self.target, 'notes.txt', 'keep')
        self.apply_reviewed()
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Changed\n')
        config = json.loads((self.target / '.agents/config.json').read_text())
        self.assertEqual(config['setupVersion'], '1.2.21')
        self.assertEqual(config['maintenance'], self.binding)
        self.assertEqual((self.target / 'notes.txt').read_text(), 'keep')
        self.assertFalse((self.entry / 'config.json').exists())

    def test_established_backup_requires_review_before_replacing_target_edits(self):
        self.initialize()
        self.write(self.target, '.agents/rules/personal.md', '# Local edit\n')
        self.write(self.entry, 'files/.agents/rules/personal.md', '# Remote edit\n')
        report = self.module.inspect(self.target)
        self.assertEqual(report['conflicts'], ['.agents/rules/personal.md'])
        self.assertIn('-# Local edit', report['diffs']['.agents/rules/personal.md'])
        self.assertIn('+# Remote edit', report['diffs']['.agents/rules/personal.md'])
        before = {path: path.read_bytes() for root in (self.target, self.entry)
                  for path in root.rglob('*') if path.is_file()}
        with self.assertRaisesRegex(ValueError, 'configuration conflict'):
            self.module.apply(self.target)
        self.assertEqual({path: path.read_bytes() for root in (self.target, self.entry)
                          for path in root.rglob('*') if path.is_file()}, before)
        self.module.apply(self.target, accept_existing=report['fingerprint'])
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Remote edit\n')

    def test_adoption_backs_up_explicitly_selected_local_content(self):
        self.initialize()
        self.write(self.target, '.agents/rules/personal.md', '# Accepted local\n')
        self.module.adopt(self.target, ['.agents/rules/personal.md'])
        self.assertEqual((self.entry / 'files/.agents/rules/personal.md').read_text(), '# Accepted local\n')
        self.module.apply(self.target)
        self.write(self.entry, 'files/.agents/rules/personal.md', '# New remote\n')
        self.write(self.target, '.agents/rules/personal.md', '# Different local\n')
        self.module.adopt(self.target, ['.agents/rules/personal.md'])
        self.assertEqual((self.entry / 'files/.agents/rules/personal.md').read_text(), '# Different local\n')
        with self.assertRaisesRegex(ValueError, 'requires explicit'):
            self.module.adopt(self.target, [])

    def test_unmodified_recorded_deletion_is_applied(self):
        self.initialize()
        self.write(self.entry, 'manifest.json', '{"files":[],"directories":[]}')
        self.apply_reviewed()
        self.assertFalse((self.target / '.agents/rules/personal.md').exists())

    def test_backup_retirement_does_not_consult_setup_ownership(self):
        import hashlib
        from pathlib import PurePosixPath
        from project_state.ownership import OwnedAsset, OwnershipState
        from project_config.ownership import serialize_ownership
        self.initialize()
        relative = PurePosixPath('.agents/rules/personal.md')
        content = (self.target / relative).read_bytes()
        state = OwnershipState((), (OwnedAsset('file', 'rule', relative, hashlib.sha256(content).hexdigest()),))
        (self.target / '.agents/smartkit.lock.json').write_bytes(serialize_ownership(state))
        self.write(self.entry, 'manifest.json', '{"files":[],"directories":[]}')
        lock_before = (self.target / '.agents/smartkit.lock.json').read_bytes()
        self.apply_reviewed()
        self.assertFalse((self.target / relative).exists())
        self.assertEqual((self.target / '.agents/smartkit.lock.json').read_bytes(), lock_before)

    def test_configuration_is_backed_up_and_restored_as_a_complete_file(self):
        self.write(self.target, '.agents/config.json', json.dumps({'maintenance': self.binding, 'setupVersion': '1.2.21', 'mcp': []}))
        self.module.initialize_entry(self.target, self.entry, [])
        self.module.apply(self.target)
        self.write(self.entry, 'files/.agents/config.json', json.dumps({'maintenance': self.binding, 'replacement': True}))
        self.apply_reviewed()
        config = json.loads((self.target / '.agents/config.json').read_text())
        self.assertNotIn('mcp', config)
        self.assertIn('maintenance', config)
        self.assertNotIn('setupVersion', config)
        self.assertTrue(config['replacement'])

    def test_equivalent_git_addresses_restore_original_bytes_and_keep_receipt_valid(self):
        self.module.initialize_entry(self.target, self.entry, [])
        self.module.apply(self.target)
        source = (self.entry / 'files/.agents/config.json').read_bytes()
        alias = {**self.binding, 'repository': 'https://github.com/user/config.git'}
        self.write(self.target, '.agents/config.json', json.dumps({'maintenance': alias}))
        (self.target / '.agents/project-config-sync.json').unlink()
        report = self.module.inspect(self.target)
        self.module.apply(self.target, accept_existing=report['fingerprint'])
        self.assertEqual((self.target / '.agents/config.json').read_bytes(), source)
        self.assertEqual(self.module.inspect(self.target)['changes'], [])

    def test_agents_generated_section_is_part_of_the_complete_backup(self):
        self.write(self.target, 'AGENTS.md', '# Instructions\n\n## Project rules\n\nOld index\n\n## Personal\n\nUser rules\n')
        self.module.initialize_entry(self.target, self.entry, ['AGENTS.md'])
        self.module.apply(self.target)
        self.write(self.entry, 'files/AGENTS.md', '# Instructions\n\n## Personal\n\nUpdated personal rules\n')
        self.apply_reviewed()
        text = (self.target / 'AGENTS.md').read_text()
        self.assertEqual(text, '# Instructions\n\n## Personal\n\nUpdated personal rules\n')

    def test_initial_collision_requires_matching_review_token(self):
        self.initialize()
        (self.target / '.agents/project-config-sync.json').unlink()
        self.write(self.target, '.agents/rules/personal.md', '# Existing independent\n')
        observation = self.module.inspect(self.target)
        self.assertTrue(observation['conflicts'])
        with self.assertRaisesRegex(ValueError, 'conflict'):
            self.module.apply(self.target)
        with self.assertRaises(ValueError):
            self.module.apply(self.target, accept_existing='stale')
        self.module.apply(self.target, accept_existing=observation['fingerprint'])
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')

    def test_every_difference_requires_acceptance_with_or_without_automatic_sync(self):
        for automatic in (False, True):
            for change in ('source-edit', 'source-add-empty', 'source-delete', 'target-edit',
                           'target-add-empty', 'target-delete', 'both-edit', 'binary-edit'):
                with self.subTest(automatic=automatic, change=change):
                    root = self.root / f'{automatic}-{change}'
                    self.target, self.entry = root / 'target', root / 'entry'
                    self.target.mkdir(parents=True)
                    self.entry.mkdir()
                    self.resolve.stop()
                    self.resolve = mock.patch.object(self.module, 'entry_root', return_value=self.entry)
                    self.resolve.start()
                    self.addCleanup(self.resolve.stop)
                    self.write(self.target, '.agents/config.json', json.dumps({'maintenance': self.binding}))
                    self.write(self.target, '.agents/rules/personal.md', '# Original\n')
                    self.module.initialize_entry(self.target, self.entry, ['.agents/rules'])
                    self.module.apply(self.target, automatic=automatic)
                    source_path = self.entry / 'files/.agents/rules/personal.md'
                    target_path = self.target / '.agents/rules/personal.md'
                    if change in ('source-edit', 'both-edit'):
                        source_path.write_text('# Source\n')
                    if change in ('target-edit', 'both-edit'):
                        target_path.write_text('# Local\n')
                    if change == 'source-add-empty':
                        self.write(self.entry, 'files/.agents/rules/new.md', '')
                    if change == 'target-add-empty':
                        self.write(self.target, '.agents/rules/new.md', '')
                    if change == 'source-delete':
                        source_path.unlink()
                    if change == 'target-delete':
                        target_path.unlink()
                    if change == 'binary-edit':
                        target_path.write_bytes(b'\x00\xff')
                    self.write(self.target, 'outside.txt', 'preserve')
                    report = self.module.inspect(self.target)
                    self.assertTrue(report['changes'])
                    self.assertEqual(report['conflicts'], report['changes'])
                    self.assertTrue(all(report['diffs'].values()))
                    before = {path: (path.read_bytes(), path.stat().st_mtime_ns)
                              for directory in (self.target, self.entry)
                              for path in directory.rglob('*') if path.is_file()}
                    with self.assertRaisesRegex(ValueError, 'configuration conflict'):
                        self.module.apply(self.target)
                    self.assertEqual({path: (path.read_bytes(), path.stat().st_mtime_ns)
                                      for directory in (self.target, self.entry)
                                      for path in directory.rglob('*') if path.is_file()}, before)
                    self.module.apply(self.target, accept_existing=report['fingerprint'])
                    self.assertEqual(self.module.inspect(self.target)['changes'], [])
                    self.assertEqual((self.target / 'outside.txt').read_text(), 'preserve')

    def test_reviewed_fingerprint_expires_when_either_side_changes(self):
        self.initialize()
        receipt = self.target / '.agents/project-config-sync.json'
        previous = receipt.read_bytes()
        for root, relative in ((self.entry, 'files/.agents/rules/personal.md'),
                               (self.target, '.agents/rules/personal.md')):
            report = self.module.inspect(self.target)
            self.write(root, relative, '# Changed after inspection\n')
            with self.assertRaisesRegex(ValueError, 'reviewed configuration fingerprint changed'):
                self.module.apply(self.target, accept_existing=report['fingerprint'])
            self.assertEqual(receipt.read_bytes(), previous)
            self.write(root, relative, '# Personal\n')

    def test_public_apply_refuses_differences_without_writes_and_accepts_reviewed_state(self):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        from project_config import project_configuration_cli as cli
        import maintain
        import workflow
        self.initialize()
        self.write(self.target, '.agents/rules/personal.md', '# Keep local\n')
        receipt = self.target / '.agents/project-config-sync.json'
        previous = receipt.read_bytes()
        for run, prefix in ((maintain.main, []), (workflow.main, ['project-config'])):
            with self.subTest(prefix=prefix):
                with redirect_stdout(StringIO()) as output:
                    self.assertEqual(run([*prefix, 'inspect', '--target', str(self.target)]), 0)
                report = json.loads(output.getvalue())
                self.assertIn('-# Keep local', report['diffs']['.agents/rules/personal.md'])
                with mock.patch.object(cli, 'sync_git_exclusions') as exclusions:
                    with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
                        self.assertEqual(run([*prefix, 'apply', '--target', str(self.target)]), 2)
                    exclusions.assert_not_called()
                self.assertIn('choose keep local or use the configuration repository', errors.getvalue())
                self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Keep local\n')
                self.assertEqual(receipt.read_bytes(), previous)
        with mock.patch.object(cli, 'sync_git_exclusions', return_value=[]):
            with redirect_stdout(StringIO()):
                self.assertEqual(maintain.main(['apply', '--target', str(self.target),
                                               '--accept-existing', report['fingerprint']]), 0)
        self.assertEqual(self.module.inspect(self.target)['changes'], [])

    def test_source_cannot_export_unsafe_paths_or_its_own_receipt(self):
        self.initialize()
        for path in ('../escape', '.agents/project-config-sync.json', '.codegraph/state', '.git/config'):
            self.write(self.entry, 'manifest.json', json.dumps({'files': [path], 'directories': []}))
            with self.assertRaises(ValueError):
                self.module.inspect(self.target)

    def test_invalid_receipt_is_refused_and_established_empty_scope_can_expand(self):
        self.initialize()
        self.write(self.target, '.agents/project-config-sync.json', '{}')
        with self.assertRaisesRegex(ValueError, 'record is invalid'):
            self.module.inspect(self.target)
        (self.target / '.agents/project-config-sync.json').unlink()
        self.write(self.entry, 'manifest.json', '{"files":[],"directories":[]}')
        self.module.apply(self.target)
        self.write(self.entry, 'manifest.json', '{"files":[".agents/rules/personal.md"],"directories":[]}')
        self.write(self.target, '.agents/rules/personal.md', '# Later target work\n')
        report = self.module.inspect(self.target)
        self.module.apply(self.target, accept_existing=report['fingerprint'])
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')

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
            self.module.inspect(self.target)

    def test_generated_outputs_reach_source_before_target(self):
        self.initialize()
        generated = {'.agents/rules/personal.md': b'# Generated replacement\n'}
        state_file = self.module.save_generated(self.target, generated, [])
        self.assertEqual((self.entry / 'files/.agents/rules/personal.md').read_bytes(), generated['.agents/rules/personal.md'])
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')
        self.assertEqual(state_file.path.as_posix(), '.agents/project-config-sync.json')

    def test_native_files_and_generated_sections_are_backed_up_without_parsing(self):
        content = b'{"mcpServers":{"custom":{"command":"private-tool","unknownOption":true}},"extra":42}\r\n'
        self.write(self.target, '.cursor/mcp.json', '')
        (self.target / '.cursor/mcp.json').write_bytes(content)
        self.write(self.target, '.agents/smartkit.lock.json', 'opaque lock: backup must not parse this')
        self.module.initialize_entry(self.target, self.entry, ['.cursor/mcp.json'])
        self.module.apply(self.target)
        self.assertEqual((self.entry / 'files/.cursor/mcp.json').read_bytes(), content)
        self.write(self.target, '.cursor/mcp.json', '{"local":"discard"}')
        self.apply_reviewed()
        self.assertEqual((self.target / '.cursor/mcp.json').read_bytes(), content)
        self.assertEqual((self.target / '.agents/smartkit.lock.json').read_text(),
                         'opaque lock: backup must not parse this')
        import maintain
        from project_config import project_configuration_cli as cli
        from contextlib import redirect_stdout
        from io import StringIO
        with mock.patch.object(cli, 'synchronize_project', side_effect=AssertionError('no rendering')):
            with redirect_stdout(StringIO()):
                self.assertEqual(maintain.main(['apply', '--target', str(self.target)]), 0)

    def test_directory_backup_restores_binary_files_and_removes_only_scoped_extras(self):
        self.write(self.target, '.agents/skills/example/SKILL.md', '# Example\n')
        asset = self.target / '.agents/skills/example/icon.bin'
        asset.write_bytes(b'\x00\xff\r\n')
        self.module.initialize_entry(self.target, self.entry, ['.agents/skills'])
        self.module.apply(self.target)
        asset.write_bytes(b'local')
        self.write(self.target, '.agents/skills/local-only.txt', 'discard within scope')
        self.write(self.target, 'outside.txt', 'keep')
        self.apply_reviewed()
        self.assertEqual(asset.read_bytes(), b'\x00\xff\r\n')
        self.assertFalse((self.target / '.agents/skills/local-only.txt').exists())
        self.assertEqual((self.target / 'outside.txt').read_text(), 'keep')
        (self.entry / 'files/.agents/skills/example/icon.bin').unlink()
        self.apply_reviewed()
        self.assertFalse(asset.exists())

    def test_source_fingerprint_skips_unchanged_writes_but_cannot_accept_local_drift(self):
        self.initialize()
        path = self.target / '.agents/rules/personal.md'
        state = self.target / '.agents/project-config-sync.json'
        before = (path.stat().st_mtime_ns, state.stat().st_mtime_ns, state.read_bytes())
        self.assertTrue(self.module.apply(self.target)['skipped'])
        self.assertEqual((path.stat().st_mtime_ns, state.stat().st_mtime_ns, state.read_bytes()), before)
        receipt = json.loads(state.read_bytes())
        self.assertEqual(set(receipt), {'binding', 'source', 'sourceFingerprint', 'appliedPaths', 'automatic'})
        self.assertEqual(receipt['appliedPaths'], ['.agents/rules/personal.md'])
        self.write(self.target, '.agents/rules/personal.md', '# Drift\n')
        with self.assertRaisesRegex(ValueError, 'configuration conflict'):
            self.module.apply(self.target)
        self.assertEqual(path.read_text(), '# Drift\n')
        self.assertEqual(state.read_bytes(), before[2])
        self.assertFalse(self.apply_reviewed()['skipped'])
        self.assertEqual(path.read_text(), '# Personal\n')
        self.assertEqual(json.loads(state.read_bytes())['sourceFingerprint'], receipt['sourceFingerprint'])

    def test_receipt_changes_only_after_successful_apply(self):
        from project_config import project_configuration as configuration
        from project_config.transaction import TransactionError
        self.initialize()
        receipt = self.target / '.agents/project-config-sync.json'
        previous = receipt.read_bytes()
        self.write(self.entry, 'files/.agents/rules/personal.md', '# New source\n')
        report = self.module.inspect(self.target)
        apply_plan = configuration.apply_plan
        def with_late_source_change(root, plan, **kwargs):
            self.write(self.entry, 'files/.agents/rules/personal.md', '# Concurrent\n')
            return apply_plan(root, plan, **kwargs)
        with mock.patch.object(configuration, 'apply_plan', side_effect=with_late_source_change):
            with self.assertRaisesRegex(TransactionError, 'configuration changed'):
                self.module.apply(self.target, accept_existing=report['fingerprint'])
        self.assertEqual(receipt.read_bytes(), previous)
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')

    def test_versioned_manifests_are_rejected_without_changing_target(self):
        self.initialize()
        original = json.loads((self.entry / 'manifest.json').read_bytes())
        self.assertEqual(set(original), {'files', 'directories'})
        before = {path.relative_to(self.target): path.read_bytes()
                  for path in self.target.rglob('*') if path.is_file()}
        for manifest in ({**original, 'version': 2},
                         {'version': 1, 'files': original['files']}):
            with self.subTest(manifest=manifest):
                content = json.dumps(manifest)
                self.write(self.entry, 'manifest.json', content)
                with self.assertRaisesRegex(ValueError, 'invalid complete configuration backup manifest'):
                    self.module.apply(self.target)
                self.assertEqual((self.entry / 'manifest.json').read_text(), content)
                self.assertEqual({path.relative_to(self.target): path.read_bytes()
                                  for path in self.target.rglob('*') if path.is_file()}, before)

    def test_versioned_receipt_is_rejected_without_changing_files(self):
        self.initialize()
        receipt = self.target / '.agents/project-config-sync.json'
        state = json.loads(receipt.read_bytes())
        self.assertNotIn('version', state)
        state['version'] = 1
        content = json.dumps(state)
        receipt.write_text(content)
        self.write(self.entry, 'files/.agents/rules/personal.md', '# New source\n')
        with self.assertRaisesRegex(ValueError, 'record is invalid'):
            self.module.apply(self.target)
        self.assertEqual(receipt.read_text(), content)
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')

    def test_removed_field_selector_is_rejected_by_public_cli(self):
        from contextlib import redirect_stderr
        from io import StringIO
        import maintain
        self.initialize()
        before = (self.entry / 'manifest.json').read_bytes()
        with redirect_stderr(StringIO()) as errors:
            result = maintain.main(['adopt', '--target', str(self.target), '--field', 'skills'])
        self.assertEqual(result, 2)
        self.assertIn('unrecognized arguments: --field skills', errors.getvalue())
        self.assertEqual((self.entry / 'manifest.json').read_bytes(), before)

    def test_default_scope_and_local_automatic_preference(self):
        self.write(self.target, '.codex/config.toml', '# native file with custom content\r\n')
        self.write(self.target, '.agents/project-config-sync.json', 'not part of a backup')
        self.module.initialize_entry(self.target, self.entry, [])
        self.assertFalse((self.entry / 'files/.agents/project-config-sync.json').exists())
        (self.target / '.agents/project-config-sync.json').unlink()
        self.module.apply(self.target, automatic=True)
        receipt = json.loads((self.target / '.agents/project-config-sync.json').read_bytes())
        self.assertTrue(receipt['automatic'])
        self.assertTrue(self.module.apply(self.target)['skipped'])
        self.module.apply(self.target, automatic=False)
        self.assertFalse(json.loads((self.target / '.agents/project-config-sync.json').read_bytes())['automatic'])

    def test_first_binding_includes_the_new_complete_config_in_default_and_explicit_scope(self):
        from project_config import project_configuration_cli as cli
        import maintain
        from contextlib import redirect_stdout
        from io import StringIO
        for extra in ([], ['--file', '.agents/config.json']):
            with self.subTest(extra=extra):
                target = self.root / ('fresh-explicit' if extra else 'fresh-default')
                target.mkdir()
                checkout = self.root / ('repo-explicit' if extra else 'repo-default')
                checkout.mkdir()
                with mock.patch.object(cli.repository, 'checkout', return_value=checkout), \
                        mock.patch.object(cli.repository, 'open_checkout', return_value=checkout), \
                        mock.patch.object(cli, 'sync_git_exclusions', return_value=[]):
                    with redirect_stdout(StringIO()):
                        status = maintain.main(['bind', '--target', str(target), '--mode', 'repository',
                            '--repository', 'alice/config', '--branch', 'main', '--entry', 'app', *extra])
                self.assertEqual(status, 0)
                source = checkout / 'projects/app'
                self.assertEqual((source / 'files/.agents/config.json').read_bytes(),
                                 (target / '.agents/config.json').read_bytes())
                self.assertIn('.agents/config.json', json.loads((source / 'manifest.json').read_bytes())['files'])

    def test_directory_and_file_adoption_refresh_only_accepted_scope(self):
        self.initialize()
        self.write(self.target, '.cursor/mcp.json', '{"extra":true}\n')
        self.write(self.target, 'notes.txt', 'outside scope')
        self.module.adopt(self.target, ['.cursor/mcp.json'])
        self.module.apply(self.target)
        self.write(self.target, '.cursor/mcp.json', '{"extra":false}\n')
        self.module.adopt(self.target, [], all_paths=True)
        self.module.apply(self.target)
        self.assertEqual((self.entry / 'files/.cursor/mcp.json').read_bytes(),
                         (self.target / '.cursor/mcp.json').read_bytes())
        self.assertFalse((self.entry / 'files/notes.txt').exists())

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
        self.assertEqual(self.module.inspect(self.target)['changes'], [])
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

    def final_update(self):
        config = json.loads((self.target / '.agents/config.json').read_bytes())
        config['setupVersion'] = '1.2.23'
        content = json.dumps(config).encode()
        return self.module.prepare_config_update(self.target, content)

    def final_files(self):
        return [self.target / '.agents/config.json', self.target / '.agents/project-config-sync.json',
                self.entry / 'files/.agents/config.json']

    def test_final_update_commits_matching_config_and_receipt_without_rewriting_scope(self):
        self.module.initialize_entry(self.target, self.entry, [])
        self.module.apply(self.target, automatic=True)
        manifest = (self.entry / 'manifest.json').read_bytes()
        self.final_update().apply()
        target, receipt, source = self.final_files()
        self.assertEqual(target.read_bytes(), source.read_bytes())
        self.assertEqual(json.loads(target.read_bytes())['setupVersion'], '1.2.23')
        self.assertTrue(json.loads(receipt.read_bytes())['automatic'])
        scope, files = self.module.backup.read_backup(self.entry)
        self.assertEqual(json.loads(receipt.read_bytes())['sourceFingerprint'], self.module.backup.fingerprint(scope, files))
        self.assertEqual(self.module.inspect(self.target)['changes'], [])
        self.assertEqual((self.entry / 'manifest.json').read_bytes(), manifest)
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in self.final_files()}
        self.assertEqual(self.final_update().apply(), [])
        self.assertEqual({path: (path.read_bytes(), path.stat().st_mtime_ns) for path in self.final_files()}, before)

    def test_final_update_write_failures_restore_all_three_files(self):
        from project_config import transaction
        self.module.initialize_entry(self.target, self.entry, [])
        self.module.apply(self.target)
        before = {path: path.read_bytes() for path in self.final_files()}
        replace = transaction._replace
        for secure in dict.fromkeys((transaction._SECURE_DIR_FDS, False)):
            for failing_write in (1, 2, 3):
                with self.subTest(secure=secure, failing_write=failing_write):
                    calls = []
                    def fail(*args, **kwargs):
                        calls.append(args)
                        if len(calls) == failing_write:
                            raise OSError('injected final write failure')
                        return replace(*args, **kwargs)
                    with mock.patch.object(transaction, '_SECURE_DIR_FDS', secure), \
                            mock.patch.object(transaction, '_replace', side_effect=fail):
                        with self.assertRaisesRegex(transaction.TransactionError, 'injected final write failure'):
                            self.final_update().apply()
                    self.assertEqual({path: path.read_bytes() for path in self.final_files()}, before)

    def test_final_update_late_failure_or_interruption_compensates_source(self):
        from project_config.transaction import TransactionError
        self.module.initialize_entry(self.target, self.entry, [])
        self.module.apply(self.target)
        before = {path: path.read_bytes() for path in self.final_files()}
        apply_plan = self.module.apply_plan
        for failure in (ValueError('late validation failed'), KeyboardInterrupt('interrupted')):
            with self.subTest(failure=type(failure).__name__):
                def apply(root, plan, *, postcondition=None):
                    if root != self.target:
                        return apply_plan(root, plan, postcondition=postcondition)
                    def after_source():
                        postcondition()
                        raise failure
                    return apply_plan(root, plan, postcondition=after_source)
                with mock.patch.object(self.module, 'apply_plan', side_effect=apply):
                    with self.assertRaises(TransactionError) as caught:
                        self.final_update().apply()
                self.assertIs(caught.exception.original_error, failure)
                self.assertEqual(caught.exception.rollback_errors, ())
                self.assertEqual({path: path.read_bytes() for path in self.final_files()}, before)

    def test_final_update_compensation_preserves_concurrent_source_edit(self):
        from project_config.transaction import TransactionError
        self.module.initialize_entry(self.target, self.entry, [])
        self.module.apply(self.target)
        target, receipt, source = self.final_files()
        before = {path: path.read_bytes() for path in (target, receipt)}
        external = b'concurrent source content\n'
        apply_plan = self.module.apply_plan
        def apply(root, plan, *, postcondition=None):
            if root != self.target:
                return apply_plan(root, plan, postcondition=postcondition)
            def after_source():
                postcondition()
                source.write_bytes(external)
                raise ValueError('late validation failed')
            return apply_plan(root, plan, postcondition=after_source)
        with mock.patch.object(self.module, 'apply_plan', side_effect=apply):
            with self.assertRaisesRegex(TransactionError, 'late validation failed.*rollback failed') as caught:
                self.final_update().apply()
        self.assertTrue(caught.exception.rollback_errors)
        self.assertEqual(source.read_bytes(), external)
        self.assertEqual({path: path.read_bytes() for path in (target, receipt)}, before)

    def test_final_update_retains_nested_source_rollback_failure(self):
        from project_config.transaction import TransactionError
        self.module.initialize_entry(self.target, self.entry, [])
        self.module.apply(self.target)
        target, receipt, source = self.final_files()
        before = {path: path.read_bytes() for path in (target, receipt)}
        external = b'concurrent source content\n'
        apply_plan = self.module.apply_plan
        def apply(root, plan, *, postcondition=None):
            if root != self.entry:
                return apply_plan(root, plan, postcondition=postcondition)
            def source_failure():
                postcondition()
                source.write_bytes(external)
                raise ValueError('source validation failed')
            return apply_plan(root, plan, postcondition=source_failure)
        with mock.patch.object(self.module, 'apply_plan', side_effect=apply):
            with self.assertRaisesRegex(TransactionError, 'source validation failed.*rollback failed') as caught:
                self.final_update().apply()
        self.assertTrue(caught.exception.rollback_errors)
        self.assertEqual(source.read_bytes(), external)
        self.assertEqual({path: path.read_bytes() for path in (target, receipt)}, before)

    def test_final_update_preserves_backup_scope_without_selected_config(self):
        self.initialize()
        manifest = (self.entry / 'manifest.json').read_bytes()
        self.final_update().apply()
        self.assertFalse((self.entry / 'files/.agents/config.json').exists())
        self.assertEqual((self.entry / 'manifest.json').read_bytes(), manifest)
        self.assertEqual(self.module.inspect(self.target)['changes'], [])

    def test_final_update_refuses_source_drift_without_adopting_it(self):
        from project_config.transaction import TransactionError
        self.write(self.target, '.agents/rules/personal.md', '# Personal\n')
        self.module.initialize_entry(self.target, self.entry, [])
        self.module.apply(self.target)
        before = {path: path.read_bytes() for path in self.final_files()}
        update = self.final_update()
        external = '# Changed after preparation\n'
        self.write(self.entry, 'files/.agents/rules/personal.md', external)
        with self.assertRaisesRegex(TransactionError, 'differs from its source'):
            update.apply()
        self.assertEqual({path: path.read_bytes() for path in self.final_files()}, before)
        self.assertEqual((self.entry / 'files/.agents/rules/personal.md').read_text(), external)
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')

    def test_full_setup_keeps_complete_config_and_native_snapshots_converged(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from test_setup_cli import SetupCliTest
        import setup_project_agents
        self.module.initialize_entry(self.target, self.entry, [])
        self.module.apply(self.target)
        helper = SetupCliTest()
        session = helper.private_session(self.root)
        with redirect_stdout(StringIO()):
            self.assertEqual(helper.prepare(self.target, session), 0)
            helper.write_generated_outputs(session)
            self.assertEqual(setup_project_agents.main(['finish', '--target', str(self.target),
                '--session', str(session), *helper.source_args()]), 0)
        self.assertEqual(self.module.inspect(self.target)['changes'], [])
        for relative in ('.agents/config.json', '.codex/config.toml', '.cursor/cli.json', 'AGENTS.md'):
            self.assertEqual((self.entry / 'files' / relative).read_bytes(), (self.target / relative).read_bytes())

    def test_full_setup_local_entry_stays_within_existing_repository_backup_scope(self):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        from test_setup_cli import SetupCliTest
        import setup_project_agents
        config = {'maintenance': self.binding, 'setupVersion': '1.2.23', 'ruleEntry': 'AGENTS.local.md'}
        self.write(self.target, '.agents/config.json', json.dumps(config))
        shared = self.target / 'AGENTS.md'
        shared.write_bytes(b'# Shared route\r\n\r\nKeep the tracked project document.\r\n')
        self.write(self.target, 'AGENTS.local.md', '# Personal configuration\n')
        for relative in self.module.backup.DEFAULT_FILES:
            if relative in ('AGENTS.md', '.agents/config.json'):
                continue
            self.write(self.target, relative, '{}\n' if relative.endswith('.json') else '# Local context\n')
        for relative in self.module.backup.DEFAULT_DIRECTORIES:
            (self.target / relative).mkdir(parents=True, exist_ok=True)
        paths = [relative for relative in self.module.backup.DEFAULT_FILES if relative != 'AGENTS.md']
        paths.extend(self.module.backup.DEFAULT_DIRECTORIES)
        paths.append('AGENTS.local.md')
        self.module.initialize_entry(self.target, self.entry, paths)
        self.module.apply(self.target)
        scope = (self.entry / 'manifest.json').read_bytes()
        original = shared.read_bytes()
        helper = SetupCliTest()
        session = helper.private_session(self.root)
        with redirect_stdout(StringIO()):
            self.assertEqual(helper.prepare(self.target, session), 0)
        helper.write_generated_outputs(session)
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as error:
            self.assertEqual(setup_project_agents.main(['finish', '--target', str(self.target),
                '--session', str(session), *helper.source_args()]), 0, error.getvalue())
        self.assertEqual((self.entry / 'manifest.json').read_bytes(), scope)
        self.assertFalse((self.entry / 'files/AGENTS.md').exists())
        self.assertEqual(shared.read_bytes(), original)
        self.assertEqual((self.entry / 'files/AGENTS.local.md').read_bytes(),
                         (self.target / 'AGENTS.local.md').read_bytes())
        self.assertIn(b'- `.agents/rules/tools.md`', (self.target / 'AGENTS.local.md').read_bytes())
        self.assertEqual(self.module.inspect(self.target)['changes'], [])

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
        self.assertEqual(self.module.inspect(self.target)['changes'], [])

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

    def test_repository_switch_refuses_unadopted_target_edits_and_keeps_receipt(self):
        import maintain
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        self.initialize()
        self.write(self.target, '.agents/rules/personal.md', '# Pending target edit\n')
        before = {str(path.relative_to(self.target)): path.read_bytes()
                  for path in self.target.rglob('*') if path.is_file()}
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
            status = maintain.main(['bind', '--target', str(self.target), '--mode', 'local-only', '--replace-binding'])
        self.assertEqual(status, 2)
        self.assertIn('differs from its source', errors.getvalue())
        self.assertEqual(before, {str(path.relative_to(self.target)): path.read_bytes()
                                 for path in self.target.rglob('*') if path.is_file()})

    def test_repository_switch_to_machine_only_retires_receipt_and_keeps_both_sources(self):
        import maintain
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        self.initialize()
        source = {str(path.relative_to(self.entry)): path.read_bytes()
                  for path in self.entry.rglob('*') if path.is_file()}
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
            status = maintain.main(['bind', '--target', str(self.target), '--mode', 'local-only', '--replace-binding'])
        self.assertEqual(status, 0, errors.getvalue())
        self.assertFalse((self.target / '.agents/project-config-sync.json').exists())
        self.assertEqual(self.module.inspect(self.target)['mode'], 'local-only')
        self.assertEqual((self.target / '.agents/rules/personal.md').read_text(), '# Personal\n')
        self.assertEqual(source, {str(path.relative_to(self.entry)): path.read_bytes()
                                  for path in self.entry.rglob('*') if path.is_file()})

    def test_publish_failure_reports_retained_commit_and_preserves_local_application(self):
        import workflow
        from project_config import project_configuration_cli as cli
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        self.initialize()
        commit = 'a' * 40
        runtime = mock.Mock()
        runtime.commit_scope.return_value = commit
        runtime.publish.side_effect = OSError('remote unavailable')
        with mock.patch.object(cli, 'repository', runtime):
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
                result = workflow.main(['project-config', 'publish', '--target', str(self.target),
                    '--path', 'projects/app/manifest.json', '--message', 'Update source'])
        self.assertEqual(result, 2)
        self.assertIn(commit, errors.getvalue())
        self.assertIn('remote unavailable', errors.getvalue())
        self.assertEqual(self.module.inspect(self.target)['changes'], [])

    def test_local_excludes_ignore_inherited_git_routing(self):
        import os
        import subprocess
        from project_config.project_configuration_cli import exclude_local
        subprocess.run(['git', '-C', str(self.target), 'init'], check=True, capture_output=True)
        unrelated = self.root / 'unrelated'
        unrelated.mkdir()
        subprocess.run(['git', '-C', str(unrelated), 'init'], check=True, capture_output=True)
        before = (unrelated / '.git/info/exclude').read_bytes()
        with mock.patch.dict(os.environ, {'GIT_DIR': str(unrelated / '.git'), 'GIT_WORK_TREE': str(unrelated)}):
            self.assertEqual(exclude_local(self.target, ['.agents/config.json']), [])
        self.assertIn('/.agents/config.json', (self.target / '.git/info/exclude').read_text())
        self.assertEqual((unrelated / '.git/info/exclude').read_bytes(), before)

    def test_subdirectory_excludes_are_scoped_and_reuse_existing_ignores(self):
        import subprocess
        from project_config.project_configuration_cli import exclude_local
        monorepo = self.root / 'monorepo'
        service = monorepo / 'services/app'
        sibling = monorepo / 'services/other'
        service.mkdir(parents=True)
        sibling.mkdir(parents=True)
        def git(*arguments):
            return subprocess.run(['git', '-C', str(monorepo), *arguments], capture_output=True, text=True, check=True)
        git('init')
        self.write(service, '.gitignore', '.agents/\n')
        self.write(service, '.agents/config.json', '{}')
        exclude = monorepo / '.git/info/exclude'
        before = exclude.read_bytes()
        self.assertEqual(exclude_local(service, ['.agents/config.json']), [])
        self.assertEqual(exclude.read_bytes(), before)
        self.assertEqual(exclude_local(service, ['AGENTS.md']), [])
        self.assertIn('/services/app/AGENTS.md', exclude.read_text())
        git('check-ignore', 'services/app/AGENTS.md')
        result = subprocess.run(['git', '-C', str(monorepo), 'check-ignore', 'services/other/AGENTS.md'], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.write(service, 'tracked.md', 'business document')
        git('add', 'services/app/tracked.md')
        before = exclude.read_bytes()
        self.assertEqual(exclude_local(service, ['tracked.md']), ['tracked.md'])
        self.assertEqual(exclude.read_bytes(), before)

    def test_public_maintenance_round_trip_with_real_local_git(self):
        self.maintenance_round_trip('alice/config')

    def test_enterprise_maintenance_round_trip_with_real_local_git(self):
        self.maintenance_round_trip('https://enterprise.example/alice/config.git')

    def maintenance_round_trip(self, repository):
        from test_project_config_repository import RepositoryGitTests
        from test_setup_cli import SetupCliTest
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        import setup_project_agents
        import maintain
        fixture = RepositoryGitTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.resolve.stop()
        if repository.startswith('https://'):
            fixture.git(fixture.root, 'config', '--global', '--add', 'url.' + fixture.remote.as_uri() + '.insteadOf', repository)
        fixture.git(self.target, 'init', '--initial-branch=main')
        self.write(self.target, '.agents/config.json', '{}')
        self.write(self.target, '.agents/rules/personal.md', '# Imported\n')
        def command(*arguments):
            out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = maintain.main([*arguments, '--target', str(self.target)])
            self.assertEqual(code, 0, err.getvalue())
            return json.loads(out.getvalue())
        result = command('bind', '--mode', 'repository', '--repository', repository, '--branch', 'main',
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
        selected = sorted(path.relative_to(entry.parent.parent).as_posix() for path in entry.rglob('*') if path.is_file())
        arguments = ['publish', '--message', 'Maintain personal project configuration']
        for path in selected:
            arguments.extend(['--path', path])
        published = command(*arguments)
        self.assertTrue(published['published'])
        self.assertEqual(fixture.git(fixture.remote, 'rev-parse', 'main'), published['commit'])
        self.assertEqual(command('inspect')['changes'], [])
        self.assertEqual(fixture.git(self.target, 'check-ignore', '.agents/rules/personal.md'), '.agents/rules/personal.md')
        command('update')


class MaintenanceModeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / 'services/app'
        self.target.mkdir(parents=True)
        self.git('init')
        self.exclude = self.root / '.git/info/exclude'
        self.write('.agents/config.json', '{}')
        self.write('.agents/rules/example.md', '# Project rule\n')
        self.write('AGENTS.md', '# Project\n')
        self.write('.gitignore', 'keep-local.txt\n')

    def git(self, *arguments, check=True):
        import subprocess
        return subprocess.run(['git', '-C', str(self.root), *arguments],
                              capture_output=True, text=True, check=check)

    def write(self, relative, content):
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def command(self, *arguments):
        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        import maintain
        output, errors = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = maintain.main([*arguments, '--target', str(self.target)])
        return code, json.loads(output.getvalue()) if output.getvalue() else {}, errors.getvalue()

    def bind(self, mode, *arguments):
        code, result, error = self.command('bind', '--mode', mode, *arguments)
        self.assertEqual(code, 0, error)
        return result

    def assert_ignored(self, relative, expected=True):
        result = self.git('check-ignore', '--quiet', '--', 'services/app/' + relative, check=False)
        self.assertEqual(result.returncode, 0 if expected else 1, result.stderr)

    def test_shared_and_machine_only_are_complete_choices_without_repository_access(self):
        from project_config import project_configuration_cli as cli
        original = self.exclude.read_bytes()
        with mock.patch.object(cli.repository, 'checkout', side_effect=AssertionError('unexpected repository access')):
            self.bind('local')
            self.assertEqual(self.exclude.read_bytes(), original)
            self.assert_ignored('.agents/config.json', False)
            self.bind('local-only', '--replace-binding')
            code, result, error = self.command('inspect')
        self.assertEqual(code, 0, error)
        self.assertEqual(result['mode'], 'local-only')
        self.assertFalse(result['selection_required'])
        self.assert_ignored('.agents/config.json')
        self.assert_ignored('AGENTS.md')
        self.write('.agents/skills/later/references/support.md', 'Future support\n')
        self.assert_ignored('.agents/skills/later/references/support.md')
        self.assertEqual((self.target / '.gitignore').read_text(), 'keep-local.txt\n')
        self.assertEqual(self.git('check-ignore', '--quiet', 'services/other/.agents/config.json', check=False).returncode, 1)

    def test_tracked_configuration_is_reported_and_index_is_preserved(self):
        self.git('add', 'services/app/.agents/rules/example.md')
        before = (self.root / '.git/index').read_bytes()
        result = self.bind('local-only')
        self.assertEqual(result['tracked_paths'], ['.agents/rules/example.md'])
        self.assertEqual((self.root / '.git/index').read_bytes(), before)
        self.assert_ignored('.agents/rules/example.md', False)
        self.write('.agents/rules/new.md', '# New local rule\n')
        self.assert_ignored('.agents/rules/new.md')

    def test_switch_to_shared_removes_only_owned_excludes_and_is_repeatable(self):
        before = self.exclude.read_bytes() + b'\n/services/app/keep-local.txt\n'
        self.exclude.write_bytes(before)
        self.bind('local-only')
        private = self.exclude.read_bytes()
        self.bind('local-only')
        self.assertEqual(self.exclude.read_bytes(), private)
        self.bind('local', '--replace-binding')
        self.assertEqual(self.exclude.read_bytes(), before)
        self.assert_ignored('.agents/config.json', False)
        self.assert_ignored('AGENTS.md', False)
        self.assert_ignored('keep-local.txt')

    def test_unapproved_switch_and_edited_exclude_block_refuse_before_binding_changes(self):
        self.bind('local-only')
        before = (self.target / '.agents/config.json').read_bytes()
        excluded = self.exclude.read_bytes()
        code, _, error = self.command('bind', '--mode', 'local')
        self.assertEqual(code, 2)
        self.assertIn('--replace-binding', error)
        self.assertEqual(self.exclude.read_bytes(), excluded)
        self.exclude.write_bytes(excluded.replace(b'/services/app/AGENTS.md', b'/services/app/other.md'))
        edited = self.exclude.read_bytes()
        code, _, error = self.command('bind', '--mode', 'local', '--replace-binding')
        self.assertEqual(code, 2)
        self.assertIn('block was edited', error)
        self.assertEqual((self.target / '.agents/config.json').read_bytes(), before)
        self.assertEqual(self.exclude.read_bytes(), edited)

    def test_read_only_routes_leave_excludes_unchanged_and_rule_sync_restores_them(self):
        self.bind('local-only')
        self.exclude.write_text('# User ignore\n', encoding='utf-8')
        before = self.exclude.read_bytes()
        code, _, error = self.command('inspect')
        self.assertEqual(code, 0, error)
        code, _, error = self.command('sync-project-rules', '--check')
        self.assertIn(code, (0, 1), error)
        self.assertEqual(self.exclude.read_bytes(), before)
        code, _, error = self.command('sync-project-rules')
        self.assertEqual(code, 0, error)
        self.assert_ignored('AGENTS.md')
        self.assert_ignored('.agents/config.json')
        self.assertTrue(self.exclude.read_bytes().startswith(before))

    def test_machine_only_rejects_repository_arguments_without_writes(self):
        before = (self.target / '.agents/config.json').read_bytes()
        excluded = self.exclude.read_bytes()
        code, _, error = self.command('bind', '--mode', 'local-only', '--repository', 'user/config')
        self.assertEqual(code, 2)
        self.assertIn('do not accept repository arguments', error)
        self.assertEqual((self.target / '.agents/config.json').read_bytes(), before)
        self.assertEqual(self.exclude.read_bytes(), excluded)

    def test_exclusion_update_failure_is_reported_after_local_sync(self):
        from project_config import project_configuration_cli as cli
        self.bind('local-only')
        before = self.exclude.read_bytes()
        with mock.patch.object(cli, 'sync_git_exclusions', side_effect=OSError('exclude is read-only')):
            code, _, error = self.command('sync-project-rules')
        self.assertEqual(code, 2)
        self.assertIn('exclude is read-only', error)
        self.assertEqual(self.exclude.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
