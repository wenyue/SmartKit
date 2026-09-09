from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path, PurePosixPath
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'skills/setup-project-agents/scripts'))

import workflow
from agents_setup import project_sync
from agents_setup.catalog import load_catalog
from agents_setup.generation import current_contracts
from agents_setup.ownership import OWNERSHIP_PATH, _actual_tree_digest, load_ownership
from agents_setup.planner import build_plan
from agents_setup.project import inspect_project
from agents_setup.renderer import render_desired_state
from agents_setup.transaction import apply_plan
from agents_setup.structured import parse_document


class SyncProjectTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / 'project'
        self.target.mkdir()
        self.catalog = load_catalog(REPO_ROOT)
        self.config = {'agents': [self.agent('local')], 'mcp': [self.server('local')]}
        self.write('.agents/agents/local.md', '# Project agent\n')
        self.save_config()
        self.write('AGENTS.md', '# Project\r\n\r\n## Agent skills\r\n\r\nKeep exact bytes.\r\n')
        generated = self.root / 'generated'
        outputs = []
        for contract in current_contracts(REPO_ROOT, self.catalog):
            output = generated / contract.target
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b'project generated source\n')
            outputs.append(contract.target)
        rendered = render_desired_state(
            REPO_ROOT, self.target, self.catalog,
            inspect_project(self.target, catalog=self.catalog).config,
            generated, generated_outputs=tuple(outputs),
        )
        apply_plan(self.target, build_plan(
            self.target, rendered.files, rendered.fields,
            delete_paths=rendered.delete_paths, replace_roots=rendered.replace_roots,
        ))

    @staticmethod
    def agent(name):
        return {'id': name, 'source': f'.agents/agents/{name}.md', 'description': 'Project agent',
                'harnesses': {'codex': {'sandbox_mode': 'workspace-write'},
                              'cursor': {'readonly': False},
                              'copilot': {'disable_model_invocation': False}, 'qoder': {}}}

    @staticmethod
    def server(name):
        return {'id': name, 'command': 'python', 'args': ['-m', 'local'],
                'harnesses': ['codex', 'cursor', 'copilot', 'qoder']}

    def write(self, relative, content):
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode('utf-8'))

    def save_config(self):
        for agent in self.config.get('agents', []):
            if not (self.target / agent['source']).exists():
                self.write(agent['source'], '# Project agent\n')
        self.write('.agents/config.json', json.dumps(self.config))

    def snapshot(self):
        return {path.relative_to(self.target).as_posix(): path.read_bytes()
                for path in self.target.rglob('*') if path.is_file()}

    def sync(self, check=False):
        return project_sync.synchronize_project(REPO_ROOT, self.target, check_only=check)

    def add_external(self):
        self.config['skills'] = [{'source': 'example/repository', 'ref': 'main',
                                 'include': ['skills/external-check']}]
        self.save_config()
        self.write('.agents/skills/external-check/SKILL.md', '# External preserved\n')
        path = self.target / OWNERSHIP_PATH
        lock = json.loads(path.read_bytes())
        lock['sources'] = [{'id': 'example/repository', 'url': 'https://github.com/example/repository',
                            'requested_ref': 'main', 'resolved_ref': 'main', 'ref_kind': 'branch',
                            'commit': 'a' * 40, 'license': {'spdx': 'MIT', 'path': 'LICENSE', 'sha256': 'b' * 64},
                            'skills': [{'id': 'example/external-check', 'path': 'skills/external-check'}]}]
        lock['assets'].append({'kind': 'tree', 'role': 'skill', 'path': '.agents/skills/external-check',
                               'digest': _actual_tree_digest(self.target, PurePosixPath('.agents/skills/external-check')),
                               'source': 'example/repository', 'source_path': 'skills/external-check'})
        path.write_text(json.dumps(lock), encoding='utf-8')

    def test_local_sync_converges_all_supported_routes_and_preserves_other_owners(self):
        self.add_external()
        self.write('.agents/rules/30-local.md', '# Local\n\nStrength: `Default`\n\nScope: Local work.\n')
        self.write('.agents/skills/local-check/SKILL.md', '# Local skill\n')
        self.config['agents'] = [self.agent('renamed')]
        self.config['mcp'] = [self.server('renamed')]
        self.save_config()
        self.write('.cursor/mcp.json', json.dumps({'mcpServers': {
            'local': {'type': 'stdio', 'command': 'python', 'args': ['-m', 'local'], 'user': 'preserve'},
            'unrelated': {'url': 'https://example.invalid/mcp'}}}))
        before = self.snapshot()
        old_lock = load_ownership(self.target)
        with mock.patch.object(workflow.bootstrap, 'main') as bootstrap_main, \
             mock.patch.object(workflow, '_create_session') as create_session:
            checked = self.sync(True)
            self.assertEqual(checked.check, 'drift')
            self.assertEqual(self.snapshot(), before)
            result = self.sync()
            bootstrap_main.assert_not_called()
            create_session.assert_not_called()
        self.assertEqual(result.check, 'clean')
        self.assertIn('.agents/skills/local-check/SKILL.md', result.preserved_paths)
        for path in ('.codex/agents/renamed.toml', '.cursor/agents/renamed.md',
                     '.github/agents/renamed.agent.md', '.qoder/agents/renamed.md'):
            self.assertTrue((self.target / path).is_file(), path)
            self.assertFalse((self.target / path.replace('renamed', 'local')).exists())
        for path, fmt, key in (('.codex/config.toml', 'toml', 'mcp_servers'),
                               ('.cursor/mcp.json', 'json', 'mcpServers'),
                               ('.vscode/mcp.json', 'json', 'servers'),
                               ('.qoder/mcp.json', 'json', 'mcpServers')):
            doc = parse_document((self.target / path).read_bytes(), fmt)
            self.assertEqual(doc[key]['renamed']['command'], 'python')
            if key == 'mcpServers' and path.startswith('.cursor'):
                self.assertEqual(doc[key]['local'], {'user': 'preserve'})
                self.assertIn('unrelated', doc[key])
            else:
                self.assertNotIn('local', doc[key])
        after = self.snapshot()
        self.assertEqual(after['.codex/agents/change-set-verifier.toml'], before['.codex/agents/change-set-verifier.toml'])
        self.assertEqual(after['.agents/skills/external-check/SKILL.md'], before['.agents/skills/external-check/SKILL.md'])
        self.assertTrue(after['AGENTS.md'].startswith(b'# Project\r\n\r\n'))
        self.assertIn(b'## Agent skills\r\n\r\nKeep exact bytes.\r\n', after['AGENTS.md'])
        self.assertIn(b'30-local.md', after['AGENTS.md'])
        new_lock = load_ownership(self.target)
        self.assertEqual(new_lock.contracts, old_lock.contracts)
        self.assertEqual(new_lock.sources, old_lock.sources)
        for asset in old_lock.assets:
            if not asset.role.startswith('project-'):
                self.assertIn(asset, new_lock.assets)
        self.assertEqual(self.sync(True).changed_paths, ())
        self.assertEqual(self.sync().changed_paths, ())
        self.assertEqual(self.snapshot(), after)

    def test_local_edits_update_mappings_and_rule_metadata_without_regeneration(self):
        self.write('.agents/rules/30-before.md', '# Local\n\nStrength: `Default`\n\nScope: Old scope.\n')
        self.sync()
        (self.target / '.agents/rules/30-before.md').unlink()
        self.write('.agents/rules/31-after.md', '# Local\n\nStrength: `Mandatory`\n\nScope: New scope.\n')
        self.config['agents'][0]['description'] = 'Updated project responsibility'
        self.config['agents'][0]['harnesses'].pop('cursor')
        self.config['mcp'][0]['command'] = 'updated-runtime'
        self.config['mcp'][0]['args'] = []
        self.config['mcp'][0]['env'] = ['LOCAL_TOKEN']
        self.save_config()
        contracts = load_ownership(self.target).contracts
        self.sync()
        self.assertFalse((self.target / '.cursor/agents/local.md').exists())
        self.assertIn(b'Updated project responsibility', (self.target / '.qoder/agents/local.md').read_bytes())
        document = parse_document((self.target / '.codex/config.toml').read_bytes(), 'toml')
        self.assertEqual(document['mcp_servers']['local']['command'], 'updated-runtime')
        self.assertEqual(document['mcp_servers']['local']['env_vars'], ['LOCAL_TOKEN'])
        entry = (self.target / 'AGENTS.md').read_bytes()
        self.assertNotIn(b'30-before.md', entry)
        self.assertIn(b'New scope.', entry)
        self.assertEqual(load_ownership(self.target).contracts, contracts)
        self.assertEqual(self.sync().changed_paths, ())

    def test_native_drift_during_planning_refuses_to_overwrite_observed_document(self):
        self.config['mcp'][0]['command'] = 'updated-runtime'
        self.save_config()
        real_build = project_sync.build_plan
        original = self.snapshot()
        drifted = b'{"unrelated": "concurrent writer"}\n'
        def changed_target(*args, **kwargs):
            (self.target / '.cursor/mcp.json').write_bytes(drifted)
            return real_build(*args, **kwargs)
        with mock.patch.object(project_sync, 'build_plan', side_effect=changed_target):
            with self.assertRaisesRegex(project_sync.ProjectSyncError, 'adapters changed while synchronization was planned'):
                self.sync()
        after = self.snapshot()
        self.assertEqual(after.pop('.cursor/mcp.json'), drifted)
        original.pop('.cursor/mcp.json')
        self.assertEqual(after, original)

    def test_deletion_retires_only_project_mappings_and_keeps_generated_sources(self):
        before = self.snapshot()
        self.config = {}
        self.save_config()
        self.sync()
        self.assertFalse((self.target / '.qoder/agents/local.md').exists())
        self.assertEqual((self.target / '.codex/agents/change-set-verifier.toml').read_bytes(),
                         before['.codex/agents/change-set-verifier.toml'])
        self.assertEqual((self.target / '.agents/rules/00-project-tools.md').read_bytes(),
                         before['.agents/rules/00-project-tools.md'])
        self.assertEqual(self.sync().changed_paths, ())

    def test_external_declaration_changes_require_full_setup_without_writing(self):
        self.add_external()
        for skills in ([], [{'source': 'example/repository', 'ref': 'next', 'include': ['skills/external-check']}]):
            self.config['skills'] = skills
            self.save_config()
            before = self.snapshot()
            with self.assertRaisesRegex(project_sync.ProjectSyncError, 'external Skill declarations changed; run full setup'):
                self.sync()
            self.assertEqual(self.snapshot(), before)

    def test_legacy_or_missing_ownership_requires_full_setup_but_rule_index_still_works(self):
        path = self.target / OWNERSHIP_PATH
        lock = json.loads(path.read_bytes())
        lock.pop('project_sync')
        path.write_text(json.dumps(lock), encoding='utf-8')
        for remove in (False, True):
            if remove:
                path.unlink()
            before = self.snapshot()
            with self.assertRaisesRegex(project_sync.ProjectSyncError, 'run full setup first'):
                self.sync()
            self.assertEqual(self.snapshot(), before)
            with redirect_stdout(StringIO()):
                self.assertEqual(workflow.main(['sync-project-rules', '--target', str(self.target)]), 0)

    def test_unmanaged_equal_adapter_and_default_collision_are_refused(self):
        self.config['agents'] = [self.agent('new')]
        self.save_config()
        self.write('.cursor/agents/new.md', 'user content')
        before = self.snapshot()
        with self.assertRaisesRegex(project_sync.ProjectSyncError, 'unrecorded Agent adapter collision'):
            self.sync()
        self.assertEqual(self.snapshot(), before)
        (self.target / '.cursor/agents/new.md').unlink()
        self.config['agents'] = [self.agent('change-set-verifier')]
        self.save_config()
        with self.assertRaisesRegex(project_sync.ProjectSyncError, 'collision'):
            self.sync()

    def test_modified_project_adapter_and_ambiguous_rule_section_refuse_without_mutation(self):
        path = self.target / '.qoder/agents/local.md'
        original = path.read_bytes()
        path.write_bytes(b'user modified adapter')
        before = self.snapshot()
        with self.assertRaisesRegex(project_sync.ProjectSyncError, 'modified outside setup'):
            self.sync()
        self.assertEqual(self.snapshot(), before)
        path.write_bytes(original)
        with (self.target / 'AGENTS.md').open('ab') as stream:
            stream.write(b'\n## Project rules\n')
        with self.assertRaisesRegex(project_sync.ProjectSyncError, 'duplicate'):
            self.sync()

    def test_input_drift_during_apply_rolls_back_owned_changes_and_preserves_drift(self):
        self.config['agents'] = [self.agent('renamed')]
        self.save_config()
        before = self.snapshot()
        real_apply = project_sync.apply_plan
        def drift(target, plan, *, postcondition):
            self.write('.agents/agents/renamed.md', '# Concurrent source edit\n')
            return real_apply(target, plan, postcondition=postcondition)
        with mock.patch.object(project_sync, 'apply_plan', side_effect=drift):
            with self.assertRaisesRegex(project_sync.ProjectSyncError, 'inputs changed during synchronization'):
                self.sync()
        after = self.snapshot()
        self.assertEqual(after.pop('.agents/agents/renamed.md'), b'# Concurrent source edit\n')
        before.pop('.agents/agents/renamed.md')
        self.assertEqual(after, before)

    def test_cli_check_never_creates_a_session_or_fetches(self):
        self.config['agents'] = []
        self.save_config()
        out = StringIO()
        with redirect_stdout(out), mock.patch.object(workflow, '_create_session') as create, \
             mock.patch.object(workflow.bootstrap, 'main') as bootstrap:
            self.assertEqual(workflow.main(['sync-project', '--target', str(self.target), '--check']), 1)
        create.assert_not_called()
        bootstrap.assert_not_called()
        self.assertEqual(json.loads(out.getvalue())['phase'], 'sync-project')
