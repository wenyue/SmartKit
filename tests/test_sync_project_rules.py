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
    def write_rule(target: Path, name: str, *, body: str, strength: str) -> None:
        rule = target / '.agents' / 'rules' / name
        rule.parent.mkdir(parents=True, exist_ok=True)
        rule.write_text(
            f'# {name}\n\nStrength: `{strength}`\n\n{body}\n',
            encoding='utf-8',
        )

    def test_check_reports_rule_index_drift_without_any_setup_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            agents = target / 'AGENTS.md'
            original = (
                '# Repository\n\n'
                '## Project rules\n\n'
                '### Required rules\n\n'
                '| Rule | Strength |\n'
                '| --- | --- |\n'
                '| `.agents/rules/tools.md` | Mandatory |\n'
                '| `.agents/rules/20-local.md` | Default |\n\n'
                'Apply SmartKit plugin Rules for shared strength and precedence. Keep project Rule policy in the\n'
                'files listed above.\n\n'
                '## Agent skills\n\nKeep this exact content.\n'
            ).encode()
            agents.write_bytes(original)
            self.write_rule(
                target,
                '10-base.md',
                body='Shared placement decisions.',
                strength='Advisory',
            )
            self.write_rule(
                target,
                '20-common.md',
                body='Shared placement decisions.',
                strength='Advisory',
            )
            self.write_rule(
                target,
                '20-local.md',
                body='Current local tests.',
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
                + '### Required rules\n\n'
                + '| Rule | Strength |\n'
                + '| --- | --- |\n'
                + '| `.agents/rules/tools.md` | Mandatory? no |\n'
                + '| `docs/rules.md` | Local |\n'
                + '| `.agents/rules/20-old-common.md` | Advisory |\n'
                + '| `.agents/rules/30-testing.md` | Default |\n'
                + '| `.agents/rules/40-removed.md` | Mandatory |\n\n'
                + 'Apply SmartKit plugin Rules for shared strength and precedence. Keep project Rule policy in the\n'
                + 'files listed above.\n\n'
                + suffix
            ).encode())
            self.write_rule(
                target,
                '20-common.md',
                body='Shared module ownership.',
                strength='Advisory',
            )
            self.write_rule(
                target,
                '30-testing.md',
                body='Current test ownership: unit | integration.',
                strength='Mandatory',
            )
            self.write_rule(
                target,
                '50-added.md',
                body='Newly added checks.',
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
                b'- `.agents/rules/tools.md`',
                updated,
            )
            self.assertIn(
                b'- `docs/rules.md`',
                updated,
            )
            self.assertIn(
                b'- `.agents/rules/20-common.md`',
                updated,
            )
            self.assertIn(
                b'- `.agents/rules/30-testing.md`',
                updated,
            )
            self.assertNotIn(b'| Rule | Strength |', updated)
            self.assertNotIn(b'Read when', updated)
            self.assertIn(
                b'- `.agents/rules/50-added.md`',
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

    def test_required_local_rules_keep_loading_policy_independent_of_strength(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            entry = target / 'AGENTS.md'
            entry.write_text(
                '# Repository\n\n## Project rules\n\n### Required rules\n\n'
                '| Rule | Strength |\n| --- | --- |\n'
                '| `.agents/rules/00-local.md` | Default |\n', encoding='utf-8',
            )
            self.write_rule(target, '00-local.md', body='Local guidance.', strength='Advisory')
            self.write_rule(target, '20-checks.md', body='Local checks.', strength='Mandatory')
            project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=False)
            text = entry.read_text(encoding='utf-8')
            self.assertNotIn('### On-demand rules', text)
            self.assertIn('- `.agents/rules/00-local.md`', text)
            self.assertNotIn('Local guidance.', text)
            self.assertNotIn('| Description |', text)
            self.assertIn('- `.agents/rules/20-checks.md`', text)
            self.assertEqual(
                project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=True).check,
                'clean',
            )
            (target / '.agents/rules/20-checks.md').unlink()
            project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=False)
            self.assertNotIn('### On-demand rules', entry.read_text(encoding='utf-8'))
            (target / '.agents/rules/00-local.md').unlink()
            project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=False)
            empty = entry.read_text(encoding='utf-8')
            self.assertNotIn('### Required rules', empty)
            self.assertNotIn('| Rule |', empty)

    def test_legacy_conditional_rules_refuse_without_writing(self):
        for name in ('03-project-flutter.md', '10-local.md', 'local-policy.md'):
            for check in (False, True):
                with self.subTest(name=name, check=check), tempfile.TemporaryDirectory() as directory:
                    target = Path(directory)
                    entry = target / 'AGENTS.md'
                    entry.write_text(
                        '## Project rules\n\n### On-demand rules\n\n'
                        '| Description | Rule | Strength |\n| --- | --- | --- |\n'
                        f'| Library usage. | `.agents/rules/{name}` | Advisory |\n',
                        encoding='utf-8',
                    )
                    self.write_rule(target, name, body='Library usage.', strength='Default')
                    before = {path.relative_to(target): path.read_bytes()
                              for path in target.rglob('*') if path.is_file()}
                    error = StringIO()
                    with redirect_stderr(error):
                        status = workflow.main([
                            'sync-project-rules', '--target', str(target),
                            *(['--check'] if check else []),
                        ])
                    self.assertEqual(status, 2)
                    self.assertIn('rule-', error.getvalue())
                    self.assertIn('AGENTS.md', error.getvalue())
                    self.assertEqual(
                        {path.relative_to(target): path.read_bytes()
                         for path in target.rglob('*') if path.is_file()}, before,
                    )

    def test_unconditional_tables_accept_optional_outer_pipes(self):
        for heading in ('Required rules', 'Unconditional rules'):
            for left, right in (('| ', ' |'), ('', ''), ('| ', ''), ('', ' |')):
                with self.subTest(heading=heading, edges=(left, right)), \
                     tempfile.TemporaryDirectory() as directory:
                    target = Path(directory)
                    self.write_rule(target, 'local.md', body='Local work.', strength='Default')
                    entry = target / 'AGENTS.md'
                    rows = ('Rule | Strength', '--- | ---',
                            '`docs/policy.md` | Mandatory', '`.agents/rules/local.md` | Default')
                    entry.write_text(
                        '# Repository\n\n## Project rules\n\n### ' + heading + '\n\n' +
                        ''.join(left + row + right + '\n' for row in rows) +
                        '\n## Agent skills\n\nPreserve this.\n', encoding='utf-8',
                    )
                    original = entry.read_bytes()
                    self.assertEqual(project_rules.synchronize_project_rules(
                        REPO_ROOT, target, check_only=True,
                    ).check, 'drift')
                    self.assertEqual(entry.read_bytes(), original)
                    self.assertEqual(project_rules.synchronize_project_rules(
                        REPO_ROOT, target, check_only=False,
                    ).check, 'clean')
                    updated = entry.read_text(encoding='utf-8')
                    self.assertIn('- `docs/policy.md`', updated)
                    self.assertIn('- `.agents/rules/local.md`', updated)
                    self.assertNotIn('| Rule | Strength |', updated)
                    self.assertTrue(updated.endswith('## Agent skills\n\nPreserve this.\n'))
                    self.assertEqual(project_rules.synchronize_project_rules(
                        REPO_ROOT, target, check_only=True,
                    ).changed_paths, ())

    def test_conditional_tables_refuse_with_optional_outer_pipes(self):
        for left, right in (('| ', ' |'), ('', ''), ('| ', ''), ('', ' |')):
            with self.subTest(edges=(left, right)), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                self.write_rule(target, 'local.md', body='Local work.', strength='Default')
                rows = ('Description | Rule | Strength', '--- | --- | ---',
                        'Library work | `.agents/rules/local.md` | Default')
                (target / 'AGENTS.md').write_text(
                    '## Project rules\n\n### On-demand rules\n\n' +
                    ''.join(left + row + right + '\n' for row in rows), encoding='utf-8',
                )
                before = {p.relative_to(target): p.read_bytes()
                          for p in target.rglob('*') if p.is_file()}
                for check in (False, True):
                    with self.subTest(check=check):
                        with self.assertRaisesRegex(project_rules.ProjectRuleSyncError, 'rule-'):
                            project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=check)
                        self.assertEqual({p.relative_to(target): p.read_bytes()
                                          for p in target.rglob('*') if p.is_file()}, before)

    def test_ambiguous_rule_list_item_refuses_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.write_rule(target, 'local.md', body='Local work.', strength='Default')
            entry = target / 'AGENTS.md'
            entry.write_text(
                '## Project rules\n\n### Required rules\n\n'
                '- load `.agents/rules/local.md` when needed\n',
                encoding='utf-8',
            )
            before = {
                path.relative_to(target): path.read_bytes()
                for path in target.rglob('*')
                if path.is_file()
            }

            with self.assertRaisesRegex(
                project_rules.ProjectRuleSyncError,
                'ambiguous Rule list item',
            ):
                project_rules.synchronize_project_rules(
                    REPO_ROOT,
                    target,
                    check_only=False,
                )

            self.assertEqual(
                {
                    path.relative_to(target): path.read_bytes()
                    for path in target.rglob('*')
                    if path.is_file()
                },
                before,
            )

    def test_conditional_table_schema_cannot_be_bypassed_by_short_rows(self):
        for left, right in (('| ', ' |'), ('', ''), ('| ', ''), ('', ' |')):
            for row in ('When editing tests | `.agents/rules/local.md`',
                        'When editing tests | `.agents/rules/local.md` | '):
                with self.subTest(edges=(left, right), row=row), \
                     tempfile.TemporaryDirectory() as directory:
                    target = Path(directory)
                    self.write_rule(target, 'local.md', body='Local work.', strength='Default')
                    (target / 'AGENTS.md').write_text(
                        '## Project rules\n\n' + ''.join(
                            left + content + right + '\n' for content in
                            ('Description | Rule | Strength', '--- | --- | ---', row)
                        ), encoding='utf-8',
                    )
                    before = {p.relative_to(target): p.read_bytes()
                              for p in target.rglob('*') if p.is_file()}
                    for check in (False, True):
                        with self.subTest(check=check):
                            with self.assertRaises(project_rules.ProjectRuleSyncError):
                                project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=check)
                            self.assertEqual({p.relative_to(target): p.read_bytes()
                                              for p in target.rglob('*') if p.is_file()}, before)

    def test_conditional_rule_metadata_refuses_yaml_key_variants(self):
        for declaration in ('  loading: on-demand', 'loading : on-demand',
                            '"loading": on-demand', "'loading': on-demand",
                            '  alwaysApply: false', '  globs: "*.py"', '  applyTo: "*.py"'):
            with self.subTest(declaration=declaration), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                self.write_rule(target, 'local.md', body='Local work.', strength='Default')
                rule = target / '.agents/rules/local.md'
                rule.write_text('---\n' + declaration + '\n---\n' +
                                rule.read_text(encoding='utf-8'), encoding='utf-8')
                (target / 'AGENTS.md').write_text('## Project rules\n', encoding='utf-8')
                before = {p.relative_to(target): p.read_bytes()
                          for p in target.rglob('*') if p.is_file()}
                for check in (False, True):
                    with self.subTest(check=check):
                        with self.assertRaisesRegex(project_rules.ProjectRuleSyncError, 'rule-'):
                            project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=check)
                        self.assertEqual({p.relative_to(target): p.read_bytes()
                                          for p in target.rglob('*') if p.is_file()}, before)

    def test_invalid_rule_loading_diagnostic_identifies_the_control(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.write_rule(target, 'local.md', body='Local work.', strength='Default')
            rule = target / '.agents/rules/local.md'
            rule.write_text('---\nloading: >\n    first\n  second\n---\n' +
                            rule.read_text(encoding='utf-8'), encoding='utf-8')
            before = rule.read_bytes()
            with self.assertRaises(project_rules.ProjectRuleSyncError) as caught:
                project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=False)
            self.assertIn('loading', str(caught.exception))
            self.assertNotIn('description', str(caught.exception))
            self.assertEqual(rule.read_bytes(), before)
            self.assertFalse((target / 'AGENTS.md').exists())

    def test_names_have_no_loading_semantics_and_skills_need_no_rule_index(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ('plain.md', '01-old.md', '99-later.md'):
                self.write_rule(target, name, body='Project work.', strength='Default')
            skill = target / '.agents/skills/rule-testing/SKILL.md'
            skill.parent.mkdir(parents=True)
            skill.write_text(
                '---\nname: rule-testing\ndescription: Use when writing tests.\n---\n'
                '# Tests\n\nStrength: `Default`\n\n',
                encoding='utf-8',
            )
            original_skill = skill.read_bytes()
            project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=False)
            text = (target / 'AGENTS.md').read_text(encoding='utf-8')
            for name in ('plain.md', '01-old.md', '99-later.md'):
                self.assertIn(f'- `.agents/rules/{name}`', text)
            self.assertNotIn('On-demand', text)
            self.assertNotIn('rule-testing', text)
            self.assertEqual(skill.read_bytes(), original_skill)

    def test_sync_accepts_completed_source_and_index_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            entry = target / 'AGENTS.md'
            entry.write_text('## Project rules\n\n## Agent skills\n\nKeep this.\n',
                             encoding='utf-8')
            skill = target / '.agents/skills/rule-library/SKILL.md'
            skill.parent.mkdir(parents=True)
            skill.write_text(
                '---\nname: rule-library\ndescription: Use for library work.\n---\n'
                '# Library\n\nStrength: `Default`\n\n',
                encoding='utf-8',
            )
            original = skill.read_bytes()
            result = project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=False)
            self.assertEqual(result.check, 'clean')
            self.assertEqual(skill.read_bytes(), original)
            self.assertNotIn('On-demand', entry.read_text(encoding='utf-8'))
            self.assertTrue(entry.read_text(encoding='utf-8').endswith('## Agent skills\n\nKeep this.\n'))

    def test_existing_rule_metadata_section_and_section_strength_remain_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            rule = target / '.agents/rules/20-existing.md'
            rule.parent.mkdir(parents=True)
            rule.write_text(
                '# Policy\n\n## Metadata\n\nStrength: `Default`\n\n'
                '\n## Special cases\n\nStrength: `Mandatory`\n\nKeep required evidence.\n',
                encoding='utf-8',
            )
            original = rule.read_bytes()
            result = project_rules.synchronize_project_rules(REPO_ROOT, target, check_only=False)
            self.assertEqual(result.check, 'clean')
            self.assertEqual(rule.read_bytes(), original)
            self.assertIn('- `.agents/rules/20-existing.md`',
                          (target / 'AGENTS.md').read_text(encoding='utf-8'))

    def test_apply_rolls_back_the_index_when_rule_set_changes_during_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            agents = target / 'AGENTS.md'
            original = b'# Repository\n\n## Agent skills\n\nKeep this.\n'
            agents.write_bytes(original)
            self.write_rule(
                target,
                '20-testing.md',
                body='Original test policy.',
                strength='Default',
            )
            real_apply = project_rules.apply_plan

            def drift_then_apply(target_root, plan, *, postcondition):
                self.write_rule(
                    target,
                    '30-concurrent.md',
                    body='Concurrent policy.',
                    strength='Mandatory',
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
            self.assertIn(
                'Concurrent policy.',
                (target / '.agents/rules/30-concurrent.md').read_text(encoding='utf-8'),
            )

    def test_refuses_ambiguous_sections_and_invalid_rule_metadata_without_writing(self):
        invalid_cases = (
            (
                'duplicate sections',
                b'## Project rules\n\nFirst.\n\n## Project rules\n\nSecond.\n',
                '# Valid\n\nStrength: `Default`\n\n',
                'duplicate ## Project rules',
            ),
            (
                'invalid strength',
                b'# Repository\n\n## Agent skills\n\nKeep this.\n',
                '# Invalid\n\nStrength: `Sometimes`\n',
                'requires valid Strength metadata',
            ),
            (
                'missing metadata',
                b'# Repository\n\n## Agent skills\n\nKeep this.\n',
                '# Invalid\n\nNo default strength.\n',
                'requires valid Strength metadata',
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
