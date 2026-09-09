from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'skills/setup-project-agents/scripts'))

import setup_project_agents as setup
import workflow


class SetupRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / 'target'
        self.target.mkdir()
        self.prepare()

    def prepare(self):
        self.session = workflow._create_session()
        session = self.session
        self.addCleanup(lambda: workflow._remove_session(session) if session.exists() else None)
        self.arguments = [
            '--target', str(self.target), '--session', str(session),
            '--source-root', str(REPO_ROOT), '--source-commit', 'offline', '--no-bootstrap',
        ]
        self.assertEqual(setup.main(['prepare', *self.arguments]), 0)
        request_path = session / 'request.json'
        self.request = json.loads(request_path.read_bytes())
        workflow._write_workflow_context(session, request_path, self.request)
        self.generated = session / 'generated'
        self.manifest = self.generated / '.setup-generation.json'

    def output(self, relative):
        path = self.generated / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'generated content\n')
        return path

    def register(self, request_id, *paths):
        output, error = StringIO(), StringIO()
        arguments = ['register', '--session', str(self.session), '--request-id', request_id]
        for path in paths:
            arguments.extend(('--output', str(path)))
        with redirect_stdout(output), redirect_stderr(error):
            status = workflow.main(arguments)
        return status, output.getvalue(), error.getvalue()

    def finish(self):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            return workflow.main(['finish', '--session', str(self.session)])

    def test_register_aggregates_exact_rule_and_skill_outputs(self):
        rule = '.agents/rules/00-project-tools.md'
        self.output(rule)
        self.assertEqual(self.register('blueprint-project-tools', rule)[0], 0)
        skill = self.output('.agents/skills/change-set-verification/SKILL.md')
        helper = self.output('.agents/skills/change-set-verification/references/checks.md')
        status, output, _ = self.register('blueprint-change-set-verification', skill, helper)
        self.assertEqual(status, 0)
        result = json.loads(output)
        self.assertFalse(result['ready'])
        self.assertEqual(len(result['remaining_requests']), 3)
        manifest = json.loads(self.manifest.read_bytes())
        self.assertEqual(manifest['requests'], [
            {'id': 'blueprint-project-tools', 'outputs': [rule]},
            {'id': 'blueprint-change-set-verification', 'outputs': [
                '.agents/skills/change-set-verification/SKILL.md',
                '.agents/skills/change-set-verification/references/checks.md',
            ]},
        ])
        self.assertEqual(list(self.target.iterdir()), [])
        self.assertFalse((self.session / workflow._SESSION_CLAIM).exists())

    def test_invalid_registration_preserves_manifest_target_and_retryable_session(self):
        rule = self.output('.agents/rules/00-project-tools.md')
        extra_rule = self.output('.agents/rules/extra.md')
        skill = self.output('.agents/skills/change-set-verification/SKILL.md')
        helper = self.output('.agents/skills/change-set-verification/checks.md')
        outside = Path(self.temp.name) / 'outside.md'
        outside.write_bytes(b'outside')
        cases = (
            ('unknown-request', (rule,)),
            ('blueprint-project-tools', (rule, rule)),
            ('blueprint-project-tools', (rule, extra_rule)),
            ('blueprint-change-set-verification', (helper,)),
            ('blueprint-change-set-verification', (skill, extra_rule)),
            ('blueprint-project-tools', (outside,)),
            ('blueprint-project-tools', ('../outside.md',)),
            ('blueprint-project-tools', ('.agents/rules/missing.md',)),
            ('blueprint-project-tools', (rule.parent,)),
        )
        original = self.manifest.read_bytes()
        for request_id, paths in cases:
            with self.subTest(request=request_id, paths=paths):
                self.assertEqual(self.register(request_id, *paths)[0], 2)
                self.assertEqual(self.manifest.read_bytes(), original)
                self.assertEqual(list(self.target.iterdir()), [])
                self.assertTrue(self.session.exists())
                self.assertFalse((self.session / workflow._SESSION_CLAIM).exists())
        self.assertEqual(self.register('blueprint-project-tools', rule)[0], 0)

    def test_duplicate_request_is_rejected_without_replacing_registration(self):
        rule = self.output('.agents/rules/00-project-tools.md')
        self.assertEqual(self.register('blueprint-project-tools', rule)[0], 0)
        original = self.manifest.read_bytes()
        self.assertEqual(self.register('blueprint-project-tools', rule)[0], 2)
        self.assertEqual(self.manifest.read_bytes(), original)

    def test_incomplete_registration_cannot_mutate_target(self):
        rule = self.output('.agents/rules/00-project-tools.md')
        self.assertEqual(self.register('blueprint-project-tools', rule)[0], 0)
        self.assertEqual(self.finish(), 2)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_registered_finish_then_full_regeneration_requires_new_complete_registration(self):
        for item in self.request['generation_requests']:
            path = self.output(item['target'])
            status, output, _ = self.register(item['id'], path)
            self.assertEqual(status, 0)
        self.assertTrue(json.loads(output)['ready'])
        self.assertEqual(self.finish(), 0)
        rule = self.target / '.agents/rules/00-project-tools.md'
        rule.write_bytes(b'project edit\n')
        self.prepare()
        self.assertTrue(self.request['generation_requests'])
        self.assertEqual(json.loads(self.manifest.read_bytes()), {'version': 1, 'requests': []})
        self.assertEqual(rule.read_bytes(), b'project edit\n')
        for item in self.request['generation_requests']:
            path = self.output(item['target'])
            self.assertEqual(self.register(item['id'], path)[0], 0)
        self.assertEqual(self.finish(), 0)
        self.assertNotEqual(rule.read_bytes(), b'project edit\n')

    def test_target_drift_rejects_registration(self):
        rule = self.output('.agents/rules/00-project-tools.md')
        original = self.manifest.read_bytes()
        config = self.target / '.agents/config.json'
        config.parent.mkdir(parents=True)
        config.write_bytes(b'{}\n')
        status, _, error = self.register('blueprint-project-tools', rule)
        self.assertEqual(status, 2)
        self.assertIn('target changed', error)
        self.assertEqual(self.manifest.read_bytes(), original)
        self.assertEqual(config.read_bytes(), b'{}\n')

    def test_claimed_session_cannot_register(self):
        rule = self.output('.agents/rules/00-project-tools.md')
        original = self.manifest.read_bytes()
        workflow._claim_session(self.session)
        self.assertEqual(self.register('blueprint-project-tools', rule)[0], 2)
        self.assertEqual(self.manifest.read_bytes(), original)
        self.assertEqual(
            (self.session / workflow._SESSION_CLAIM).read_bytes(), workflow._SESSION_CLAIM_CONTENT,
        )

    def test_failed_manifest_replacement_keeps_previous_state(self):
        rule = self.output('.agents/rules/00-project-tools.md')
        original = self.manifest.read_bytes()
        entries = set(self.session.iterdir())
        with mock.patch.object(setup.os, 'replace', side_effect=OSError('injected failure')), redirect_stderr(StringIO()):
            status = setup.main([
                'register', *self.arguments, '--request-id', 'blueprint-project-tools',
                '--output', str(rule),
            ])
        self.assertEqual(status, 2)
        self.assertEqual(self.manifest.read_bytes(), original)
        self.assertEqual(set(self.session.iterdir()), entries)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_claim_cleanup_failure_does_not_report_success(self):
        rule = self.output('.agents/rules/00-project-tools.md')
        with mock.patch.object(Path, 'unlink', side_effect=OSError('injected cleanup failure')):
            status, output, error = self.register('blueprint-project-tools', rule)
        self.assertEqual(status, 2)
        self.assertEqual(output, '')
        self.assertIn(str(self.session), error)
        self.assertTrue((self.session / workflow._SESSION_CLAIM).exists())
        self.assertEqual(list(self.target.iterdir()), [])

    def test_linked_output_is_rejected(self):
        rule = self.generated / '.agents/rules/00-project-tools.md'
        outside = Path(self.temp.name) / 'outside.md'
        outside.write_bytes(b'outside')
        try:
            rule.symlink_to(outside)
        except OSError:
            self.skipTest('symlinks are unavailable')
        original = self.manifest.read_bytes()
        self.assertEqual(self.register('blueprint-project-tools', rule)[0], 2)
        self.assertEqual(self.manifest.read_bytes(), original)
