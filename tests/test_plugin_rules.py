from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESSES = ('codex', 'copilot', 'cursor', 'qoder')


class PluginRuleContractTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='rule delivery ')
        self.addCleanup(self.temporary.cleanup)
        self.state_root = Path(self.temporary.name) / 'state'

    def run_raw_dispatch(self, harness, event, payload, *, root=ROOT, cwd=ROOT):
        environment = dict(os.environ)
        environment['PLUGIN_DATA'] = str(self.state_root)
        environment['PLUGIN_ROOT'] = str(root)
        environment['XDG_CONFIG_HOME'] = str(self.state_root / 'config')
        environment['APPDATA'] = str(self.state_root / 'config')
        environment['XDG_STATE_HOME'] = str(self.state_root / 'sessions')
        environment.pop('PONYTAIL_DEFAULT_MODE', None)
        return subprocess.run(
            [
                sys.executable, str(ROOT / 'runtime/rules/dispatch.py'),
                '--harness', harness, '--event', event,
            ],
            input=payload, capture_output=True, cwd=cwd, env=environment, check=False,
        )

    def run_dispatch(self, harness, event, payload, **kwargs):
        result = self.run_raw_dispatch(harness, event, json.dumps(payload).encode(), **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return json.loads(result.stdout)

    def session_context(self, harness, payload=None, **kwargs):
        result = self.run_dispatch(harness, 'session', payload or {}, **kwargs)
        if harness == 'cursor':
            self.assertEqual(set(result), {'additional_context'})
            return result['additional_context']
        if harness == 'copilot':
            self.assertEqual(set(result), {'additionalContext'})
            return result['additionalContext']
        self.assertEqual(set(result), {'hookSpecificOutput'})
        self.assertEqual(result['hookSpecificOutput']['hookEventName'], 'SessionStart')
        return result['hookSpecificOutput']['additionalContext']

    def assert_core_and_index(self, context, root=ROOT):
        registry = json.loads((root / 'rules/registry.json').read_text(encoding='utf-8'))
        self.assertTrue(context.startswith('## SmartKit Rule files\n'))
        self.assertIn(
            'Each `<smartkit-rule-file>` block below represents one independent Rule source file.',
            context,
        )
        self.assertIn('## SmartKit Rule index', context)
        core_count = 0
        for rule in registry['rules']:
            if rule.get('delivery', 'inline' if rule['id'].startswith('smartkit/core-') else 'indexed') == 'inline':
                core_count += 1
                body = (
                    root / 'rules' / rule['source']
                ).read_text(encoding='utf-8').rstrip('\r\n')
                opening = f'<smartkit-rule-file path="rules/{rule["source"]}">\n'
                closing = '\n</smartkit-rule-file>'
                self.assertEqual(context.count(opening), 1)
                remainder = context.split(opening, 1)[1]
                enclosed, _ = remainder.split(closing, 1)
                self.assertEqual(enclosed, body)
            else:
                self.assertIn(rule['description'], context)
                self.assertIn(rule['id'], context)
                self.assertIn(str((root / 'rules' / rule['source']).resolve()), context)
                self.assertNotIn(
                    f'<smartkit-rule-file path="rules/{rule["source"]}">', context
                )
                body = (root / 'rules' / rule['source']).read_text(encoding='utf-8').strip()
                self.assertNotIn(body, context)
        self.assertEqual(context.count('<smartkit-rule-file path='), core_count)
        self.assertEqual(context.count('</smartkit-rule-file>'), core_count)

    def fixture_root(self):
        root = Path(self.temporary.name) / 'plugin with spaces'
        shutil.copytree(ROOT / 'rules', root / 'rules')
        return root

    def test_registry_and_retired_adapter_contract(self):
        rules = json.loads((ROOT / 'rules/registry.json').read_text(encoding='utf-8'))['rules']
        self.assertEqual(rules[0]['id'], 'smartkit/core-instruction-governance')
        self.assertEqual(rules[0]['strength'], 'Mandatory')
        self.assertTrue(rules[0]['description'])
        self.assertEqual(len({item['id'] for item in rules}), len(rules))
        for rule in rules:
            self.assertTrue({'id', 'source', 'strength', 'description'} <= set(rule))
            self.assertFalse(set(rule) - {'id', 'source', 'strength', 'description', 'delivery'})
            self.assertEqual(Path(rule['source']).name, rule['source'])
            self.assertTrue((ROOT / 'rules' / rule['source']).is_file())
        self.assertFalse((ROOT / 'rules/source').exists())
        self.assertFalse((ROOT / 'rules/cursor').exists())
        self.assertFalse((ROOT / 'scripts/sync_cursor_rule_adapters.py').exists())
        self.assertNotIn('rules', json.loads((ROOT / '.cursor-plugin/plugin.json').read_text()))

    def test_every_host_gets_independent_core_rule_files_and_semantic_index(self):
        for harness in HARNESSES:
            with self.subTest(harness=harness):
                context = self.session_context(harness, {'prompt': 'Discuss Python error handling'})
                self.assert_core_and_index(context)
                self.assertIn('Codex subagent tools', context)
                self.assertLess(len(context.encode()), 50000)
        self.assertFalse(self.state_root.exists())

    def test_explicit_indexed_delivery_preserves_core_identity_and_loading_pointer(self):
        root = self.fixture_root()
        path = root / 'rules/registry.json'
        document = json.loads(path.read_text(encoding='utf-8'))
        rule = next(item for item in document['rules']
                    if item['id'] == 'smartkit/core-communication')
        rule['delivery'] = 'indexed'
        path.write_text(json.dumps(document), encoding='utf-8')
        for harness in HARNESSES:
            with self.subTest(harness=harness):
                context = self.session_context(harness, root=root)
                self.assertNotIn('# Communication Quality', context)
                self.assertIn(rule['id'], context)
                self.assertIn(rule['description'], context)
                self.assertIn(str(root / 'rules' / rule['source']), context)
                self.assertIn('# Instruction Governance', context)

    def test_invalid_delivery_and_indexed_governance_are_rejected(self):
        for delivery in ('unknown', 'indexed'):
            with self.subTest(delivery=delivery):
                root = Path(self.temporary.name) / delivery
                shutil.copytree(ROOT / 'rules', root / 'rules')
                path = root / 'rules/registry.json'
                document = json.loads(path.read_text(encoding='utf-8'))
                document['rules'][0]['delivery'] = delivery
                path.write_text(json.dumps(document), encoding='utf-8')
                result = self.run_raw_dispatch('codex', 'session', b'{}', root=root)
                self.assertNotEqual(result.returncode, 0)

    def test_context_does_not_change_when_a_file_is_mentioned(self):
        for harness in HARNESSES:
            with self.subTest(harness=harness):
                plain = self.session_context(harness)
                named = self.session_context(harness, {'prompt': 'Edit src/main.py and lib/app.dart'})
                self.assertEqual(plain, named)

    def test_code_policies_use_skill_discovery_and_leave_harness_delivery_intact(self):
        expected = {
            'rule-code', 'rule-error-handling', 'rule-code-comment',
            'rule-cpp', 'rule-flutter', 'rule-go', 'rule-python',
        }
        skills = json.loads((ROOT / 'skills/registry.json').read_text(encoding='utf-8'))
        registered = {
            item['path'] for item in skills['custom']
            if item['id'].startswith('smartkit/rule-')
        }
        self.assertEqual(registered, expected)
        public_ids = {item['id'] for item in skills['custom']}
        for retired in ('handle-operation-failure', 'write-code-comment', 'rule-operation-failure'):
            self.assertNotIn(f'smartkit/{retired}', public_ids)
            self.assertFalse((ROOT / 'skills' / retired).exists())
        owned_references = {
            'rule-error-handling': ('recovery-and-effects.md', 'persisted-data.md', 'remediation.md'),
            'rule-code-comment': ('examples.md',),
        }
        for owner, resources in owned_references.items():
            for resource in resources:
                with self.subTest(owner=owner, resource=resource):
                    self.assertTrue((ROOT / 'skills' / owner / 'references' / resource).is_file())
        for name in expected:
            with self.subTest(skill=name):
                body = (ROOT / 'skills' / name / 'SKILL.md').read_text(encoding='utf-8')
                self.assertRegex(body, rf'(?m)^name: {name}$')
                self.assertRegex(body, r'(?m)^description: .+$')
                self.assertIn('Strength: `Default`', body)
                self.assertNotIn('disable-model-invocation: true', body)
        for name in ('code', 'cpp', 'flutter', 'go', 'python'):
            self.assertFalse((ROOT / 'rules' / f'file-{name}.md').exists())
        for harness in HARNESSES:
            with self.subTest(harness=harness):
                context = self.session_context(harness)
                self.assert_core_and_index(context)
                self.assertIn('smartkit/harness-codex', context)
                self.assertNotIn('smartkit/file-', context)
                self.assertNotIn('skills/rule-', context)

    def test_absolute_index_paths_work_outside_plugin_directory(self):
        root = self.fixture_root()
        context = self.session_context('cursor', root=root, cwd=Path(self.temporary.name))
        self.assert_core_and_index(context, root)
        self.assertIn(str(root / 'rules' / 'harness-codex.md'), context)

    def test_descriptions_are_opaque_text_and_do_not_select_bodies(self):
        root = self.fixture_root()
        path = root / 'rules/registry.json'
        document = json.loads(path.read_text(encoding='utf-8'))
        document['rules'][0]['description'] = 'Governance overview.'
        indexed = next(rule for rule in document['rules'] if rule['id'] == 'smartkit/harness-codex')
        indexed['description'] = 'A | B comparison.'
        path.write_text(json.dumps(document), encoding='utf-8')
        context = self.session_context('codex', root=root)
        self.assertIn('A \\| B comparison.', context)
        self.assertIn('# Instruction Governance', context)
        self.assertNotIn('# Codex Harness Adaptation', context)
        indexed['description'] = 'Always'
        path.write_text(json.dumps(document), encoding='utf-8')
        self.assertNotIn('# Codex Harness Adaptation', self.session_context('codex', root=root))

    def test_session_reentry_restores_core_and_index_without_activation_history(self):
        for harness in ('codex', 'qoder'):
            for source in ('startup', 'resume', 'clear', 'compact'):
                with self.subTest(harness=harness, source=source):
                    self.assert_core_and_index(self.session_context(harness, {'source': source}))
        self.assertFalse(self.state_root.exists())

    def test_normal_tools_and_prompts_do_not_activate_rules_or_write_state(self):
        for harness in ('copilot', 'cursor'):
            for tool_input in (
                {'path': 'src/main.py', 'content': 'print(1)'},
                {'command': 'pwd'},
            ):
                with self.subTest(harness=harness, tool_input=tool_input):
                    result = self.run_dispatch(
                        harness, 'tool',
                        {'session_id': 'normal', 'tool_name': 'Write', 'tool_input': tool_input},
                    )
                    self.assertEqual(result, {})
        self.assertEqual(self.run_dispatch(
            'copilot', 'prompt', {'transformedPrompt': 'Edit src/main.go'},
        ), {})
        self.assertFalse(self.state_root.exists())

    def test_compaction_restores_before_a_tool_once_without_file_matching(self):
        for harness in ('copilot', 'cursor'):
            with self.subTest(harness=harness):
                session = {'conversation_id': harness} if harness == 'cursor' else {'sessionId': harness}
                self.session_context(harness, session)
                self.assertEqual(self.run_dispatch(harness, 'compact', session), {})
                payload = dict(session, tool_name='Shell', tool_input={'command': 'pwd'})
                restored = self.run_dispatch(harness, 'tool', payload)
                if harness == 'cursor':
                    self.assertEqual(set(restored), {'permission', 'agent_message'})
                    self.assertEqual(restored['permission'], 'deny')
                    context = restored['agent_message']
                else:
                    self.assertEqual(restored['permissionDecision'], 'deny')
                    context = restored['permissionDecisionReason']
                self.assert_core_and_index(context)
                self.assertEqual(self.run_dispatch(harness, 'tool', payload), {})
                self.assertEqual(self.run_dispatch(harness, 'stop', dict(session, status='completed')), {})

    def test_copilot_prompt_restores_context_and_preserves_transformed_prompt(self):
        session = {'sessionId': 'prompt'}
        self.run_dispatch('copilot', 'compact', session)
        original = 'Continue with 日本語 and a literal dollar: $HOME'
        restored = self.run_dispatch(
            'copilot', 'prompt', dict(session, transformedPrompt=original),
        )
        self.assertEqual(set(restored), {'modifiedTransformedPrompt'})
        self.assert_core_and_index(restored['modifiedTransformedPrompt'])
        self.assertTrue(restored['modifiedTransformedPrompt'].endswith('\n' + original))
        self.assertEqual(self.run_dispatch(
            'copilot', 'prompt', dict(session, transformedPrompt=original),
        ), {})

    def test_compaction_before_final_answer_restores_once(self):
        for harness in ('copilot', 'cursor'):
            with self.subTest(harness=harness):
                session = {'session_id': harness}
                self.run_dispatch(harness, 'compact', session)
                payload = dict(session, status='completed')
                restored = self.run_dispatch(harness, 'stop', payload)
                if harness == 'cursor':
                    self.assertEqual(set(restored), {'followup_message'})
                    context = restored['followup_message']
                else:
                    self.assertEqual(restored['decision'], 'block')
                    context = restored['reason']
                self.assert_core_and_index(context)
                self.assertEqual(self.run_dispatch(harness, 'stop', payload), {})

    def test_cursor_does_not_resume_an_aborted_or_failed_run(self):
        session = {'conversation_id': 'abort'}
        self.run_dispatch('cursor', 'compact', session)
        for status in ('aborted', 'error'):
            self.assertEqual(self.run_dispatch('cursor', 'stop', dict(session, status=status)), {})
        resumed = self.run_dispatch('cursor', 'tool', session)
        self.assertEqual(resumed['permission'], 'deny')

    def test_compaction_state_is_session_scoped_and_contains_no_rule_activation(self):
        self.run_dispatch('cursor', 'compact', {'conversation_id': 'one'})
        self.assertEqual(self.run_dispatch('cursor', 'tool', {'conversation_id': 'two'}), {})
        restored = self.run_dispatch('cursor', 'tool', {'session_id': 'one'})
        self.assertEqual(restored['permission'], 'deny')
        state_file, = (self.state_root / 'rule-compaction').iterdir()
        self.assertEqual(json.loads(state_file.read_text()), {
            'context_generation': 1, 'restored_generation': 1,
        })
        self.run_dispatch('cursor', 'compact', {'conversation_id': 'one'})
        self.assertEqual(self.run_dispatch('cursor', 'tool', {'conversation_id': 'one'})['permission'], 'deny')
        self.assertEqual(json.loads(state_file.read_text())['restored_generation'], 2)

    def test_failed_restoration_keeps_pending_compaction(self):
        root = self.fixture_root()
        session = {'conversation_id': 'failure'}
        self.run_dispatch('cursor', 'compact', session, root=root)
        source = root / 'rules/core-personality.md'
        body = source.read_bytes()
        source.write_bytes(b'\xff')
        failed = self.run_raw_dispatch('cursor', 'tool', json.dumps(session).encode(), root=root)
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(failed.stdout, b'')
        source.write_bytes(body)
        restored = self.run_dispatch('cursor', 'tool', session, root=root)
        self.assert_core_and_index(restored['agent_message'], root)

    def test_registry_rejects_invalid_fields_and_retired_triggers(self):
        root = self.fixture_root()
        path = root / 'rules/registry.json'
        baseline = path.read_text(encoding='utf-8')
        invalid_values = (
            ('description', ''), ('description', True), ('description', 'When\nediting'),
            ('source', '../file.md'), ('source', '/file.md'), ('source', 'source/file.md'),
            ('source', 'C:\\file.md'), ('source', 'file.txt'),
            ('strength', 'Sometimes'), ('id', 'smartkit/core-instruction-governance'),
            ('trigger', {'type': 'file', 'include_globs': ['**/*.py']}),
            ('read_when', 'Always'),
        )
        for field, value in invalid_values:
            with self.subTest(field=field, value=value):
                document = json.loads(baseline)
                document['rules'][-1][field] = value
                path.write_text(json.dumps(document), encoding='utf-8')
                result = self.run_raw_dispatch('codex', 'session', b'{}', root=root)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b'')
                self.assertIn(b'SmartKit Rule delivery skipped', result.stderr)

    def test_missing_indexed_source_and_invalid_core_rule_fail_closed(self):
        root = self.fixture_root()
        path = root / 'rules/registry.json'
        document = json.loads(path.read_text(encoding='utf-8'))
        (root / 'rules/harness-codex.md').unlink()
        result = self.run_raw_dispatch('cursor', 'session', b'{}', root=root)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b'missing source', result.stderr)
        document['rules'] = [
            rule for rule in document['rules'] if rule['id'] != 'smartkit/harness-codex'
        ]
        document['rules'][0]['strength'] = 'Default'
        path.write_text(json.dumps(document), encoding='utf-8')
        result = self.run_raw_dispatch('cursor', 'session', b'{}', root=root)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b'the first Rule must be', result.stderr)

    def test_core_rule_rejects_reserved_file_wrapper_delimiters(self):
        root = self.fixture_root()
        source = root / 'rules/core-personality.md'
        body = source.read_text(encoding='utf-8')
        for delimiter in ('<smartkit-rule-file', '</smartkit-rule-file>'):
            with self.subTest(delimiter=delimiter):
                source.write_text(body + f'\n{delimiter}\n', encoding='utf-8')
                result = self.run_raw_dispatch('codex', 'session', b'{}', root=root)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b'')
                self.assertIn(b'reserved Rule file wrapper delimiter', result.stderr)

    def test_invalid_compaction_state_fails_closed(self):
        session = {'sessionId': 'invalid-state'}
        self.run_dispatch('copilot', 'compact', session)
        state_file, = (self.state_root / 'rule-compaction').iterdir()
        for invalid in (
            '[]', '{invalid json',
            '{"context_generation": true, "restored_generation": 0}',
            '{"context_generation": 0, "restored_generation": 1}',
            '{"context_generation": -1, "restored_generation": 0}',
            '{"context_generation": 1, "restored_generation": 0, "extra": []}',
        ):
            with self.subTest(invalid=invalid):
                state_file.write_text(invalid, encoding='utf-8')
                result = self.run_raw_dispatch('copilot', 'tool', json.dumps(session).encode())
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b'')
                self.assertIn(b'invalid Rule compaction state', result.stderr)

    def test_invalid_hook_payload_fails_closed(self):
        for payload in (b'{invalid json', b'[]', b'null'):
            result = self.run_raw_dispatch('codex', 'session', payload)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, b'')
            self.assertIn(b'invalid Hook payload', result.stderr)

    def test_unsupported_host_events_are_rejected(self):
        for harness, event in (('codex', 'tool'), ('qoder', 'prompt'), ('cursor', 'prompt')):
            result = self.run_raw_dispatch(harness, event, b'{}')
            self.assertEqual(result.returncode, 1)
            self.assertIn(b'unsupported Rule delivery event', result.stderr)

    def test_hook_delivery_emits_host_boundary_diagnostic(self):
        result = self.run_raw_dispatch('cursor', 'session', b'{}')
        self.assertEqual(result.returncode, 0)
        self.assertIn(b'Host trust, acceptance, spill, and truncation remain host-owned', result.stderr)

    def test_cursor_cross_platform_launcher_preserves_protocol(self):
        launcher = ROOT / 'runtime/rules/dispatch.cmd'
        if os.name == 'nt':
            invocation = ['cmd.exe', '/d', '/c', str(launcher)]
        else:
            self.assertTrue(os.access(launcher, os.X_OK))
            invocation = ['sh', '-c', '"$1" --harness cursor --event session', 'rule-hook', str(launcher)]
        if os.name == 'nt':
            invocation += ['--harness', 'cursor', '--event', 'session']
        environment = dict(os.environ, PLUGIN_ROOT=str(ROOT), PLUGIN_DATA=str(self.state_root))
        result = subprocess.run(
            invocation, input=b'{}', capture_output=True, cwd=self.temporary.name,
            env=environment, timeout=15, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assert_core_and_index(json.loads(result.stdout)['additional_context'])


if __name__ == '__main__':
    unittest.main()
