from __future__ import annotations

import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path, PurePosixPath
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'skills/setup-project-agents/scripts'))

import adopt_project_agents as adoption
from agents_setup.catalog import load_catalog
from agents_setup.generation import current_contracts
from agents_setup.planner import build_plan
from agents_setup.project import inspect_project
from agents_setup.project_sync import synchronize_project
from agents_setup.renderer import RenderError, render_desired_state
from agents_setup.models import DesiredFile
from agents_setup.transaction import apply_plan
from agents_setup.validation import validate_rendered_state


class AgentAdoptionTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.target = self.root / 'target'
        self.target.mkdir()

    def native(self, host, content):
        directory, suffix = adoption._HOST_PATHS[host]
        path = self.target / directory / f'local{suffix}'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def manifest(self, replacements=None):
        inspected = adoption.inspect(self.target)
        harnesses = {}
        for entry in inspected['agents']:
            if entry['id'] != 'local':
                continue
            host = entry['harness']
            content = (replacements or {}).get(host, (self.target / entry['path']).read_bytes())
            prepared = self.root / f'{host}.prepared'
            prepared.write_bytes(content)
            harnesses[host] = {key: entry[key] for key in ('path', 'sha256', 'canonical_sha256')}
            harnesses[host]['content_file'] = str(prepared)
        return {'config_sha256': inspected['config_sha256'], 'agents': [
            {'id': 'local', 'description': 'Translate project content', 'harnesses': harnesses},
        ]}

    def install(self):
        catalog = load_catalog(REPO_ROOT)
        generated = self.root / 'generated'
        outputs = []
        for contract in current_contracts(REPO_ROOT, catalog):
            path = generated / contract.target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'project guidance\n')
            outputs.append(contract.target)
        rendered = render_desired_state(
            REPO_ROOT, self.target, catalog,
            inspect_project(self.target, catalog=catalog).config,
            generated, generated_outputs=tuple(outputs),
        )
        validate_rendered_state(rendered)
        apply_plan(self.target, build_plan(
            self.target, rendered.files, rendered.fields,
            delete_paths=rendered.delete_paths, replace_roots=rendered.replace_roots,
        ))
        return rendered

    def test_generated_wrapper_references_still_require_rendered_or_preserved_targets(self):
        self.native('codex', b'model = "working"\n')
        adoption.apply(self.target, self.manifest())
        rendered = self.install()
        wrapper = DesiredFile(
            PurePosixPath('.cursor/rules/example.mdc'), b'Apply @.agents/prompts/missing.md\n',
        )
        with self.assertRaisesRegex(RenderError, 'wrapper reference is not rendered'):
            validate_rendered_state(replace(rendered, files=(*rendered.files, wrapper)))

    def test_invalid_toml_adoption_preserves_existing_agent_and_config(self):
        native = self.native('codex', b'model = "working"\n')
        with self.assertRaisesRegex(ValueError, 'invalid toml'):
            adoption.apply(self.target, self.manifest({'codex': b'model =\n'}))
        self.assertEqual(native.read_bytes(), b'model = "working"\n')
        self.assertFalse((self.target / '.agents/config.json').exists())
        self.assertFalse((self.target / '.agents/agents/local.codex.toml').exists())

    def test_invalid_canonical_toml_cannot_be_synced_or_installed(self):
        native = self.native('codex', b'model = "working"\n')
        adoption.apply(self.target, self.manifest())
        self.install()
        lock = self.target / '.agents/smartkit.lock.json'
        original_lock = lock.read_bytes()
        canonical = self.target / '.agents/agents/local.codex.toml'
        canonical.write_bytes(b'model =\n')
        for check_only in (True, False):
            with self.subTest(check_only=check_only), self.assertRaisesRegex(ValueError, 'invalid toml'):
                synchronize_project(REPO_ROOT, self.target, check_only=check_only)
        with self.assertRaisesRegex(ValueError, 'invalid toml'):
            self.install()
        self.assertEqual(native.read_bytes(), b'model = "working"\n')
        self.assertEqual(canonical.read_bytes(), b'model =\n')
        self.assertEqual(lock.read_bytes(), original_lock)

    def test_native_prompt_references_survive_full_validation_and_repeat(self):
        prompt = self.target / '.agents/prompts/local.md'
        prompt.parent.mkdir(parents=True)
        prompt.write_bytes(b'Project translation instructions.\n')
        documents = {
            'codex': b'developer_instructions = "Follow `.agents/prompts/local.md`."\n',
            'cursor': b'---\nname: local\n---\nApply @.agents/prompts/local.md\n',
            'copilot': b'---\nname: local\n---\nFollow `.agents/prompts/local.md`.\n',
            'qoder': b'---\nname: local\n---\nFollow `.agents/prompts/local.md`.\n',
        }
        native = {host: self.native(host, content) for host, content in documents.items()}
        adoption.apply(self.target, self.manifest())
        self.install()
        self.install()
        for host, path in native.items():
            self.assertEqual(path.read_bytes(), documents[host])
        self.assertEqual(prompt.read_bytes(), b'Project translation instructions.\n')
        self.assertEqual(synchronize_project(REPO_ROOT, self.target, check_only=True).check, 'clean')

    def test_import_preserves_complete_host_documents_and_repeat_does_not_write(self):
        documents = {
            'codex': b'# Preserve comment\nmodel = "current"\ntools = ["translate"]\n[unknown]\nflag = true\n',
            'cursor': b'---\nname: local\ntools:\n  - read\ncustom: {retain: true}\n---\nFull prompt.\n',
            'copilot': b'---\nname: local\nhandoffs:\n  - label: Continue\n    agent: editor\n---\nFull prompt.\n',
            'qoder': b'---\nname: local\npermission:\n  commands: [read]\n---\nFull prompt.\n',
        }
        for host, content in documents.items():
            self.native(host, content)
        adoption.apply(self.target, self.manifest())
        config = json.loads((self.target / '.agents/config.json').read_bytes())
        self.assertNotIn('source', config['agents'][0])
        for host, settings in config['agents'][0]['harnesses'].items():
            self.assertEqual((self.target / settings['native_source']).read_bytes(), documents[host])
        self.assertEqual(adoption.apply(self.target, self.manifest()), [])
        self.install()
        self.assertEqual(synchronize_project(REPO_ROOT, self.target, check_only=True).check, 'clean')

    def test_model_update_during_first_adoption_and_managed_update_keep_ownership(self):
        path = self.native('codex', b'model = "old"\ncustom = true\n')
        updated = b'model = "new"\ncustom = true\n'
        adoption.apply(self.target, self.manifest({'codex': updated}))
        self.assertEqual(path.read_bytes(), updated)
        self.install()
        later = b'model = "later"\ncustom = true\n'
        adoption.apply(self.target, self.manifest({'codex': later}))
        self.assertEqual(path.read_bytes(), updated)
        self.assertEqual(synchronize_project(REPO_ROOT, self.target, check_only=False).check, 'clean')
        self.assertEqual(path.read_bytes(), later)

    def test_native_drift_and_canonical_collision_refuse_without_overwrite(self):
        native = self.native('codex', b'model = "old"\n')
        manifest = self.manifest()
        native.write_bytes(b'model = "external"\n')
        with self.assertRaisesRegex(ValueError, 'changed after inspection'):
            adoption.apply(self.target, manifest)
        self.assertFalse((self.target / '.agents/config.json').exists())
        canonical = self.target / '.agents/agents/local.codex.toml'
        canonical.parent.mkdir(parents=True)
        canonical.write_bytes(b'independent canonical source')
        with self.assertRaisesRegex(ValueError, 'independently owned'):
            adoption.apply(self.target, self.manifest())
        self.assertEqual(canonical.read_bytes(), b'independent canonical source')

    def test_concurrent_config_change_is_preserved(self):
        self.native('codex', b'model = "old"\n')
        manifest = self.manifest()
        real_build = adoption.build_plan
        def changed(*args, **kwargs):
            plan = real_build(*args, **kwargs)
            config = self.target / '.agents/config.json'
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_bytes(b'{"agents": []}')
            return plan
        with mock.patch.object(adoption, 'build_plan', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'changed during planning'):
                adoption.apply(self.target, manifest)
        self.assertEqual((self.target / '.agents/config.json').read_bytes(), b'{"agents": []}')
        self.assertFalse((self.target / '.agents/agents/local.codex.toml').exists())

    def test_ownership_appearing_during_planning_prevents_adoption(self):
        native = self.native('codex', b'model = "old"\n')
        manifest = self.manifest({'codex': b'model = "new"\n'})
        lock = self.target / '.agents/smartkit.lock.json'
        external = b'{"sources":[],"assets":[],"contracts":[]}\n'
        build = adoption.build_plan
        def changed(*args, **kwargs):
            lock.parent.mkdir(parents=True, exist_ok=True)
            lock.write_bytes(external)
            return build(*args, **kwargs)
        with mock.patch.object(adoption, 'build_plan', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'changed during planning.*smartkit.lock'):
                adoption.apply(self.target, manifest)
        self.assertEqual(lock.read_bytes(), external)
        self.assertEqual(native.read_bytes(), b'model = "old"\n')
        self.assertFalse((self.target / '.agents/config.json').exists())

    def test_ownership_drift_at_apply_is_preserved_and_adoption_rolls_back(self):
        for existing in (False, True):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                native = target / '.codex/agents/local.toml'
                native.parent.mkdir(parents=True)
                native.write_bytes(b'model = "old"\n')
                lock = target / '.agents/smartkit.lock.json'
                if existing:
                    lock.parent.mkdir()
                    lock.write_bytes(b'{"sources":[],"assets":[]}\n')
                saved_target = self.target
                self.target = target
                manifest = self.manifest({'codex': b'model = "new"\n'})
                self.target = saved_target
                external = b'{"sources":[],"assets":[],"contracts":[]}\n'
                commit = adoption.apply_plan
                def changed(*args, **kwargs):
                    lock.parent.mkdir(parents=True, exist_ok=True)
                    lock.write_bytes(external)
                    return commit(*args, **kwargs)
                with mock.patch.object(adoption, 'apply_plan', side_effect=changed):
                    with self.assertRaises(adoption.TransactionError):
                        adoption.apply(target, manifest)
                self.assertEqual(lock.read_bytes(), external)
                self.assertEqual(native.read_bytes(), b'model = "old"\n')
                self.assertFalse((target / '.agents/config.json').exists())
                self.assertFalse((target / '.agents/agents/local.codex.toml').exists())


if __name__ == '__main__':
    unittest.main()
