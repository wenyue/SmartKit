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
SCRIPTS_ROOT = REPO_ROOT / 'skills' / 'setup-project-agents' / 'scripts'
sys.path.insert(0, str(SCRIPTS_ROOT))

import workflow  # noqa: E402
from agents_setup import project_rules  # noqa: E402


class SyncProjectRulesTest(unittest.TestCase):
    @staticmethod
    def write_rule(target: Path, name: str, *, scope: str, strength: str) -> None:
        rule = target / '.agents' / 'rules' / name
        rule.parent.mkdir(parents=True, exist_ok=True)
        rule.write_text(
            f'# {name}\n\nStrength: `{strength}`\n\nScope: {scope}\n',
            encoding='utf-8',
        )

    def test_check_reports_rule_index_drift_without_any_setup_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            agents = target / 'AGENTS.md'
            original = (
                '# Repository\n\n'
                '## Project rules\n\n'
                'Use the descriptions and current task to decide which project Rules to read before related work.\n'
                'Read a Rule to check its relevance when uncertain, and re-read it whenever useful.\n\n'
                '| Description | Rule | Strength |\n'
                '| --- | --- | --- |\n'
                '| Managed tools | `.agents/rules/00-project-tools.md` | Mandatory |\n'
                '| Old scope | `.agents/rules/20-local.md` | Default |\n\n'
                'Apply SmartKit plugin Rules for shared strength and precedence. Keep project Rule policy in the\n'
                'files listed above.\n\n'
                '## Agent skills\n\nKeep this exact content.\n'
            ).encode()
            agents.write_bytes(original)
            self.write_rule(
                target,
                '10-base.md',
                scope='Shared placement decisions.',
                strength='Advisory',
            )
            self.write_rule(
                target,
                '20-common.md',
                scope='Shared placement decisions.',
                strength='Advisory',
            )
            self.write_rule(
                target,
                '20-local.md',
                scope='Current local tests.',
                strength='Default',
            )
            before = {
                path.relative_to(target): path.read_bytes()
                for path in target.rglob('*')
                if path.is_file()
            }
            output = StringIO()

            with mock.patch.object(workflow, '_create_session') as create_session, \
                 mock.patch.object(workflow.bootstrap, 'main') as bootstrap_main, \
                 redirect_stdout(output):
                status = workflow.main([
                    'sync-project-rules', '--target', str(target), '--check',
                ])

            self.assertEqual(status, 1)
            self.assertEqual(json.loads(output.getvalue()), {
                'phase': 'sync-project-rules',
                'check': 'drift',
                'changed_paths': ['AGENTS.md'],
            })
            self.assertEqual(
                {
                    path.relative_to(target): path.read_bytes()
                    for path in target.rglob('*')
                    if path.is_file()
                },
                before,
            )
            create_session.assert_not_called()
            bootstrap_main.assert_not_called()

    def test_apply_converges_add_metadata_rename_and_delete_in_one_atomic_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            agents = target / 'AGENTS.md'
            prefix = '# Repository\r\n\r\nKeep this introduction.\r\n\r\n'
            suffix = '## Agent skills\r\n\r\nKeep this exact content.\r\n'
            agents.write_bytes((
                prefix
                + '## Project rules\n\n'
                + 'Read every project Rule whose `Read when` condition matches the current task.\n\n'
                + '| Read when | Rule | Strength |\n'
                + '| --- | --- | --- |\n'
                + '| Managed tools | `.agents/rules/00-project-tools.md` | Mandatory? no |\n'
                + '| Keep this custom row | `docs/rules.md` | Local |\n'
                + '| Former common scope. | `.agents/rules/20-old-common.md` | Advisory |\n'
                + '| Former testing scope. | `.agents/rules/30-testing.md` | Default |\n'
                + '| Removed scope. | `.agents/rules/40-removed.md` | Mandatory |\n\n'
                + 'Apply SmartKit plugin Rules for shared strength and precedence. Keep project Rule policy in the\n'
                + 'files listed above.\n\n'
                + suffix
            ).encode())
            self.write_rule(
                target,
                '20-common.md',
                scope='Shared module ownership.',
                strength='Advisory',
            )
            self.write_rule(
                target,
                '30-testing.md',
                scope='Current test ownership: unit | integration.',
                strength='Mandatory',
            )
            self.write_rule(
                target,
                '50-added.md',
                scope='Newly added checks.',
                strength='Default',
            )
            unrelated = target / 'notes.txt'
            unrelated.write_bytes(b'preserve me exactly\x00\n')

            output = StringIO()
            with mock.patch.object(workflow, '_create_session') as create_session, \
                 mock.patch.object(workflow.bootstrap, 'main') as bootstrap_main, \
                 redirect_stdout(output):
                status = workflow.main([
                    'sync-project-rules', '--target', str(target),
                ])

            self.assertEqual(status, 0)
            self.assertEqual(json.loads(output.getvalue()), {
                'phase': 'sync-project-rules',
                'check': 'clean',
                'changed_paths': ['AGENTS.md'],
            })
            updated = agents.read_bytes()
            self.assertTrue(updated.startswith(prefix.encode()))
            self.assertTrue(updated.endswith(suffix.encode()))
            self.assertIn(
                b'| Managed tools | `.agents/rules/00-project-tools.md` | Mandatory? no |',
                updated,
            )
            self.assertIn(
                b'| Keep this custom row | `docs/rules.md` | Local |',
                updated,
            )
            self.assertIn(
                b'| Shared module ownership. | `.agents/rules/20-common.md` | Advisory |',
                updated,
            )
            self.assertIn(
                b'| Current test ownership: unit \\| integration. | `.agents/rules/30-testing.md` | Mandatory |',
                updated,
            )
            self.assertIn(b'| Description | Rule | Strength |', updated)
            self.assertNotIn(b'Read when', updated)
            self.assertIn(
                b'| Newly added checks. | `.agents/rules/50-added.md` | Default |',
                updated,
            )
            self.assertNotIn(b'10-base.md', updated)
            self.assertNotIn(b'20-old-common.md', updated)
            self.assertNotIn(b'40-removed.md', updated)
            self.assertEqual(unrelated.read_bytes(), b'preserve me exactly\x00\n')
            create_session.assert_not_called()
            bootstrap_main.assert_not_called()

            second_output = StringIO()
            with redirect_stdout(second_output):
                second_status = workflow.main([
                    'sync-project-rules', '--target', str(target),
                ])

            self.assertEqual(second_status, 0)
            self.assertEqual(json.loads(second_output.getvalue()), {
                'phase': 'sync-project-rules',
                'check': 'clean',
                'changed_paths': [],
            })
            self.assertEqual(agents.read_bytes(), updated)

    def test_apply_rolls_back_the_index_when_rule_metadata_changes_during_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            agents = target / 'AGENTS.md'
            original = b'# Repository\n\n## Agent skills\n\nKeep this.\n'
            agents.write_bytes(original)
            self.write_rule(
                target,
                '20-testing.md',
                scope='Original test scope.',
                strength='Default',
            )
            rule = target / '.agents/rules/20-testing.md'
            real_apply = project_rules.apply_plan

            def drift_then_apply(target_root, plan, *, postcondition):
                rule.write_text(
                    '# Testing\n\nStrength: `Mandatory`\n\nScope: Concurrent scope.\n',
                    encoding='utf-8',
                )
                return real_apply(target_root, plan, postcondition=postcondition)

            error = StringIO()
            with mock.patch.object(
                    project_rules,
                    'apply_plan',
                    side_effect=drift_then_apply,
                ), \
                 mock.patch('sys.stderr', error):
                status = workflow.main([
                    'sync-project-rules', '--target', str(target),
                ])

            self.assertEqual(status, 2)
            self.assertIn('project Rule index did not converge', error.getvalue())
            self.assertEqual(agents.read_bytes(), original)
            self.assertIn('Concurrent scope.', rule.read_text(encoding='utf-8'))

    def test_refuses_ambiguous_sections_and_invalid_rule_metadata_without_writing(self):
        invalid_cases = (
            (
                'duplicate sections',
                b'## Project rules\n\nFirst.\n\n## Project rules\n\nSecond.\n',
                '# Valid\n\nStrength: `Default`\n\nScope: Valid scope.\n',
                'duplicate ## Project rules',
            ),
            (
                'missing metadata',
                b'# Repository\n\n## Agent skills\n\nKeep this.\n',
                '# Invalid\n\nStrength: `Default`\n',
                'requires Strength and Scope metadata',
            ),
        )
        for label, agents_content, rule_content, message in invalid_cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                agents = target / 'AGENTS.md'
                agents.write_bytes(agents_content)
                rule = target / '.agents/rules/20-local.md'
                rule.parent.mkdir(parents=True)
                rule.write_text(rule_content, encoding='utf-8')
                before = {
                    path.relative_to(target): path.read_bytes()
                    for path in target.rglob('*')
                    if path.is_file()
                }
                error = StringIO()

                with redirect_stderr(error):
                    status = workflow.main([
                        'sync-project-rules', '--target', str(target),
                    ])

                self.assertEqual(status, 2)
                self.assertIn(message, error.getvalue())
                self.assertEqual(
                    {
                        path.relative_to(target): path.read_bytes()
                        for path in target.rglob('*')
                        if path.is_file()
                    },
                    before,
                )


if __name__ == '__main__':
    unittest.main()
