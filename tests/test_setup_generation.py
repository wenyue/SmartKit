from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'skills/setup-project-agents/scripts'))

from agents_setup.catalog import load_catalog
from agents_setup.generation import generation_requests
from agents_setup.models import ProjectConfig
from agents_setup.ownership import OwnershipError, load_ownership
from agents_setup.planner import build_plan
from agents_setup.renderer import RenderError, render_desired_state
from agents_setup.transaction import apply_plan
from agents_setup.validation import validate_rendered_state


class SetupGenerationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source = root / 'source'
        self.target = root / 'target'
        self.target.mkdir()
        self.generated = root / 'generated'
        self.generated.mkdir()
        self.catalog = load_catalog(REPO_ROOT)
        for asset in self.catalog.assets:
            if asset.control_plane:
                continue
            source = REPO_ROOT / asset.source
            destination = self.source / asset.source
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                shutil.copyfile(source, destination)

    def requests(self):
        return generation_requests(
            self.source, self.target, self.catalog,
            load_ownership(self.target, catalog=self.catalog),
        )

    def sync(self, *, helper=False):
        requests = self.requests()
        shutil.rmtree(self.generated)
        self.generated.mkdir()
        outputs = []
        for request in requests:
            relative = PurePosixPath(request['target'])
            path = self.generated / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'generated content\n')
            outputs.append(relative)
            if helper and relative == PurePosixPath('.agents/skills/change-set-verification/SKILL.md'):
                resource = relative.parent / 'references/checks.md'
                (self.generated / resource).parent.mkdir(parents=True)
                (self.generated / resource).write_bytes(b'generated checks\n')
                outputs.append(resource)
        rendered = render_desired_state(
            self.source, self.target, self.catalog, ProjectConfig((), ()),
            self.generated, generated_outputs=tuple(outputs),
        )
        validate_rendered_state(rendered)
        plan = build_plan(
            self.target, rendered.files, rendered.fields,
            delete_paths=rendered.delete_paths, replace_roots=rendered.replace_roots,
        )
        apply_plan(self.target, plan)
        return requests, rendered

    def test_every_full_setup_regenerates_the_complete_set_with_current_project_evidence(self):
        first, _ = self.sync(helper=True)
        self.assertTrue(first)
        self.assertEqual(self.requests(), first)
        rule = self.target / '.agents/rules/01-project-contracts.md'
        skill = self.target / '.agents/skills/change-set-verification/SKILL.md'
        helper = skill.parent / 'references/checks.md'
        for path in (rule, skill, helper):
            path.write_bytes(b'project edit\n')
        self.assertEqual(self.requests(), first)
        self.assertEqual(helper.read_bytes(), b'project edit\n')
        requests, _ = self.sync()
        self.assertEqual(requests, first)
        self.assertEqual(rule.read_bytes(), b'generated content\n')
        self.assertEqual(skill.read_bytes(), b'generated content\n')
        self.assertFalse(helper.exists())
        contract = self.source / 'setup-assets/blueprints/rules/01-project-contracts.md'
        contract.write_bytes(contract.read_bytes() + b'\nChanged contract.\n')
        self.assertEqual(self.requests(), first)

    def test_removed_contract_deletes_edited_outputs_but_preserves_unrecorded_files(self):
        self.sync(helper=True)
        rule = self.target / '.agents/rules/00-project-tools.md'
        skill = self.target / '.agents/skills/change-set-verification/SKILL.md'
        helper = skill.parent / 'references/checks.md'
        local = skill.parent / 'notes.md'
        local.write_bytes(b'project notes\n')
        for path in (rule, skill, helper):
            path.write_bytes(b'project edit\n')
        retired = {'blueprint-project-tools', 'blueprint-change-set-verification'}
        self.catalog = replace(self.catalog, assets=tuple(
            asset for asset in self.catalog.assets if asset.id not in retired
        ))
        requests, rendered = self.sync()
        self.assertTrue(retired.isdisjoint(item['id'] for item in requests))
        for path in (rule, skill, helper):
            self.assertFalse(path.exists())
        self.assertEqual(local.read_bytes(), b'project notes\n')
        self.assertNotIn(b'.agents/rules/00-project-tools.md', rendered.files_by_path['AGENTS.md'])
        self.assertTrue(retired.isdisjoint(
            item.id for item in load_ownership(self.target).contracts
        ))

    def test_missing_supporting_output_requests_regeneration(self):
        self.sync(helper=True)
        helper = self.target / '.agents/skills/change-set-verification/references/checks.md'
        helper.unlink()
        requests, _ = self.sync(helper=True)
        self.assertIn('blueprint-change-set-verification', [item['id'] for item in requests])
        self.assertTrue(helper.is_file())

    def test_changed_skill_contract_retires_omitted_supporting_output(self):
        self.sync(helper=True)
        helper = self.target / '.agents/skills/change-set-verification/references/checks.md'
        helper.write_bytes(b'project edit\n')
        asset = next(item for item in self.catalog.assets if item.id == 'blueprint-change-set-verification')
        contract = self.source / asset.source
        contract.write_bytes(contract.read_bytes() + b'\nChanged checks.\n')
        self.sync()
        self.assertFalse(helper.exists())

    def test_renamed_contract_destination_retires_old_recorded_path(self):
        self.sync()
        old = self.target / '.agents/rules/01-project-contracts.md'
        old.write_bytes(b'project intent before rename\n')
        self.catalog = replace(self.catalog, assets=tuple(
            replace(asset, target=PurePosixPath('.agents/rules/03-renamed-contracts.md'))
            if asset.id == 'blueprint-project-contracts' else asset
            for asset in self.catalog.assets
        ))
        requests, _ = self.sync()
        self.assertFalse(old.exists())
        self.assertTrue((self.target / '.agents/rules/03-renamed-contracts.md').is_file())
        self.assertEqual(len(requests), len(self.requests()))

    def test_removal_rejects_a_recorded_file_replaced_by_a_directory(self):
        self.sync(helper=True)
        helper = self.target / '.agents/skills/change-set-verification/references/checks.md'
        helper.unlink()
        helper.mkdir()
        local = helper / 'project.txt'
        local.write_bytes(b'keep this file')
        self.catalog = replace(self.catalog, assets=tuple(
            asset for asset in self.catalog.assets if asset.id != 'blueprint-change-set-verification'
        ))
        with self.assertRaisesRegex(RenderError, 'not a regular file'):
            self.sync()
        self.assertEqual(local.read_bytes(), b'keep this file')
        self.assertTrue((helper.parent.parent / 'SKILL.md').exists())

    def test_contract_records_reject_paths_outside_the_declared_output(self):
        self.sync()
        path = self.target / '.agents/smartkit.lock.json'
        lock = json.loads(path.read_bytes())
        contract = next(item for item in lock['contracts'] if item['target'].endswith('SKILL.md'))
        contract['outputs'].append('.git/config')
        path.write_text(json.dumps(lock), encoding='utf-8')
        with self.assertRaisesRegex(OwnershipError, 'outside'):
            load_ownership(self.target)
