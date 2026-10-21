from __future__ import annotations

import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path, PurePosixPath
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / 'skills' / 'setup-project-agents' / 'scripts'
sys.path.insert(0, str(SCRIPTS_ROOT))

import bootstrap  # noqa: E402
import workflow  # noqa: E402


def run_git(directory: Path, *args: str) -> None:
    subprocess.run(
        ('git', '-C', str(directory), *args),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class SetupWorkflowTest(unittest.TestCase):

    def setUp(self):
        readiness = mock.patch.object(workflow, '_verify_codegraph', return_value={'ready': True, 'message': 'test MCP responds'})
        readiness.start()
        self.addCleanup(readiness.stop)


    @staticmethod
    def make_origin(root: Path) -> Path:
        origin = root / 'origin.git'
        work = root / 'origin-work'
        shutil.copytree(
            REPO_ROOT,
            work,
            ignore=shutil.ignore_patterns('.git', '.superpowers', '__pycache__', '*.pyc'),
        )
        subprocess.run(('git', 'init', '--bare', '--quiet', str(origin)), check=True)
        subprocess.run(('git', '-C', str(work), 'init', '--quiet'), check=True)
        run_git(work, 'checkout', '--quiet', '-b', 'master')
        run_git(work, 'config', 'user.email', 'test@example.invalid')
        run_git(work, 'config', 'user.name', 'Setup Test')
        run_git(work, 'add', '.')
        run_git(work, 'commit', '--quiet', '-m', 'workflow source')
        run_git(work, 'remote', 'add', 'origin', origin.as_uri())
        run_git(work, 'push', '--quiet', 'origin', 'master')
        return origin

    @staticmethod
    def write_generated_outputs(session: Path) -> None:
        request = json.loads((session / 'request.json').read_text(encoding='utf-8'))
        declarations = []
        for item in request['generation_requests']:
            relative = item['target']
            path = session / 'generated' / PurePosixPath(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'# generated {path.name}\n', encoding='utf-8')
            declarations.append({'id': item['id'], 'outputs': [relative]})
        (session / 'generated/.setup-generation.json').write_text(
            json.dumps({'version': 1, 'requests': declarations}), encoding='utf-8'
        )

    @staticmethod
    def write_matt_context(target: Path, entry_name: str = 'AGENTS.md') -> None:
        references = (
            'docs/agents/issue-tracker.md',
            'docs/agents/triage-labels.md',
            'docs/agents/domain.md',
        )
        for relative in references:
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'# {path.stem}\n', encoding='utf-8')
        entry = target / entry_name
        entry.parent.mkdir(parents=True, exist_ok=True)
        entry.write_text(
            '## Agent skills\n\n' + '\n'.join(
                f'See `{reference}`.' for reference in references
            ) + '\n',
            encoding='utf-8',
        )

    def test_inspect_is_read_only_for_fresh_and_initialized_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.write_matt_context(target)
            (target / '.codex').mkdir()
            (target / '.codex/config.toml').write_bytes(b'[agents.reviewer]\ndescription = "Review code"\n')
            for initialized in (False, True):
                if initialized:
                    (target / '.agents').mkdir()
                    (target / '.agents/smartkit.lock.json').write_text('{"sources":[],"assets":[]}', encoding='utf-8')
                    (target / '.agents/config.json').write_text('{"setupVersion":"1.0.0"}', encoding='utf-8')
                before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in target.rglob('*') if path.is_file()}
                output = StringIO()
                with mock.patch.object(workflow, '_create_session') as create, \
                     mock.patch.object(bootstrap, 'main') as bootstrap_main, \
                     mock.patch.object(workflow, '_setup_codegraph') as setup_runtime, \
                     redirect_stdout(output):
                    self.assertEqual(workflow.main(['inspect', '--target', str(target)]), 0)
                result = json.loads(output.getvalue())
                self.assertEqual(result['phase'], 'inspect')
                self.assertEqual(result['ownership']['initialized'], initialized)
                self.assertTrue(result['migrations']['provisional'])
                self.assertIn('.agents/rules/structure.md', [item['target'] for item in result['project_discovery']['generation_requests']])
                self.assertIn('additional_rules', result['project_discovery'])
                self.assertTrue(result['pending_assessment'])
                self.assertEqual(result['agents']['role_declarations'][0]['id'], 'reviewer')
                self.assertEqual(result['agents']['issues'], [])
                self.assertNotIn('ready', result)
                self.assertEqual(before, {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in target.rglob('*') if path.is_file()})
                create.assert_not_called()
                bootstrap_main.assert_not_called()
                setup_runtime.assert_not_called()

    def test_inspect_aggregates_missing_prerequisites_and_malformed_state(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / '.agents').mkdir()
            (target / '.agents/config.json').write_bytes(b'{broken')
            (target / '.agents/smartkit.lock.json').write_bytes(b'{broken')
            output = StringIO()
            with mock.patch.object(workflow, '_verify_codegraph', side_effect=workflow.WorkflowError('runtime missing')), redirect_stdout(output):
                self.assertEqual(workflow.main(['inspect', '--target', str(target)]), 2)
            result = json.loads(output.getvalue())
            for section in ('matt', 'configuration', 'ownership', 'codegraph'):
                self.assertIn('error', result[section])
            self.assertGreaterEqual(len(result['errors']), 4)
            self.assertEqual((target / '.agents/config.json').read_bytes(), b'{broken')

    def test_writer_inputs_public_session_preserves_request_target_and_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'target'
            self.write_matt_context(target)
            support = target / '.agents/skills/change-set-verification/references/custom.bin'
            support.parent.mkdir(parents=True)
            support.write_bytes(b'\x00\xffexact bytes\r\n')
            plan = Path(directory) / 'plan.md'
            plan.write_bytes(b'Preserve valid project obligations; assess every blueprint.\n')
            output = StringIO()
            with mock.patch.object(bootstrap, 'fetch_canonical', side_effect=bootstrap.SourceUnavailable('offline')), \
                 redirect_stdout(output), redirect_stderr(StringIO()):
                self.assertEqual(workflow.main(['start', '--target', str(target)]), 0)
            session = Path(json.loads(output.getvalue())['session'])
            self.addCleanup(lambda: workflow._remove_session(session) if session.exists() else None)
            request_bytes = (session / 'request.json').read_bytes()
            registration = session / 'generated/.setup-generation.json'
            registration_bytes = registration.read_bytes()
            before = {path: path.read_bytes() for path in target.rglob('*') if path.is_file()}
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(workflow.main(['writer-inputs', '--session', str(session), '--plan', str(plan)]), 0)
            result = json.loads(output.getvalue())
            inputs = json.loads(Path(result['inputs']).read_bytes())
            bundle = Path(result['bundle'])
            request = json.loads(request_bytes)
            self.assertEqual(inputs['request'], request)
            self.assertEqual(len(inputs['inputs']), len(request['generation_requests']))
            self.assertEqual(inputs['writer'], str(REPO_ROOT / 'skills/write-rules-and-skills/SKILL.md'))
            self.assertEqual((bundle / 'common-plan.md').read_bytes(), plan.read_bytes())
            self.assertEqual((bundle / 'existing' / support.relative_to(target)).read_bytes(), support.read_bytes())
            self.assertEqual((session / 'request.json').read_bytes(), request_bytes)
            self.assertEqual(registration.read_bytes(), registration_bytes)
            self.assertEqual(before, {path: path.read_bytes() for path in target.rglob('*') if path.is_file()})
            self.assertFalse((session / workflow._SESSION_CLAIM).exists())
            workflow._claim_session(session)
            with redirect_stderr(StringIO()):
                self.assertEqual(workflow.main(['writer-inputs', '--session', str(session), '--plan', str(plan)]), 2)
            (session / workflow._SESSION_CLAIM).unlink()
            support.write_bytes(b'changed after start')
            error = StringIO()
            with redirect_stderr(error):
                self.assertEqual(workflow.main(['writer-inputs', '--session', str(session), '--plan', str(plan)]), 2)
            self.assertIn('target changed after start', error.getvalue())
            self.assertEqual(list(session.glob('writer-inputs-*')), [bundle])
            self.assertFalse((session / workflow._SESSION_CLAIM).exists())

    def test_writer_inputs_reports_old_pinned_cli_without_falling_back(self):
        session = workflow._create_session()
        self.addCleanup(lambda: workflow._remove_session(session) if session.exists() else None)
        with mock.patch.object(workflow, '_request_context', return_value=({}, REPO_ROOT, REPO_ROOT, 'offline')), \
             mock.patch.object(workflow.subprocess, 'run', return_value=subprocess.CompletedProcess([], 2, '', 'unknown writer-inputs command\n')) as run, \
             redirect_stderr(StringIO()) as error:
            self.assertEqual(workflow.main(['writer-inputs', '--session', str(session), '--plan', 'plan.md']), 2)
        self.assertEqual(run.call_count, 1)
        self.assertIn('unknown writer-inputs', error.getvalue())
        self.assertFalse((session / workflow._SESSION_CLAIM).exists())
        self.assertTrue(session.exists())

    def test_public_start_refuses_incomplete_generation_from_pinned_implementation(self):
        import setup_project_agents as setup
        for count in (0, 1):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as directory:
                target = Path(directory) / 'target'
                self.write_matt_context(target)
                sessions = []

                def incompatible_prepare(arguments):
                    session = Path(arguments[arguments.index('--session') + 1])
                    sessions.append(session)
                    status = setup.main([
                        *arguments, '--source-root', str(REPO_ROOT),
                        '--source-commit', 'offline', '--no-bootstrap',
                    ])
                    self.assertEqual(status, 0)
                    path = session / 'request.json'
                    request = json.loads(path.read_bytes())
                    request['generation_requests'] = request['generation_requests'][:count]
                    path.write_text(json.dumps(request), encoding='utf-8')
                    return 0

                error = StringIO()
                with mock.patch.object(bootstrap, 'main', side_effect=incompatible_prepare), \
                     redirect_stdout(StringIO()), redirect_stderr(error):
                    self.assertEqual(workflow.main(['start', '--target', str(target)]), 2)
                self.assertIn('did not request the complete current generated set', error.getvalue())
                self.assertTrue(all(not session.exists() for session in sessions))
                self.assertFalse((target / '.agents/smartkit.lock.json').exists())

    def test_start_rejects_removed_platform_option(self):
        with redirect_stderr(StringIO()):
            result = workflow.main([
                'start', '--target', str(REPO_ROOT), '--platform', 'cursor'
            ])

        self.assertEqual(result, 2)

    def test_legacy_launcher_prepare_is_refused_and_its_session_is_cleaned(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'target'
            self.write_matt_context(target)
            before = {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()}
            session = workflow._create_session()
            self.addCleanup(lambda: workflow._remove_session(session) if session.exists() else None)
            bootstrap_main = bootstrap.main

            def legacy_prepare(arguments):
                index = arguments.index('--completion-protocol')
                return bootstrap_main(arguments[:index] + arguments[index + 2:])

            error = StringIO()
            with mock.patch.object(workflow, '_create_session', return_value=session), \
                 mock.patch.object(bootstrap, 'fetch_canonical', side_effect=bootstrap.SourceUnavailable('offline')), \
                 mock.patch.object(bootstrap, 'main', side_effect=legacy_prepare), \
                 redirect_stdout(StringIO()), redirect_stderr(error):
                self.assertEqual(workflow.main(['start', '--target', str(target)]), 2)
            self.assertFalse(session.exists())
            self.assertEqual(
                {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()}, before,
            )

    def test_start_requires_matt_context_before_creating_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / 'target'
            target.mkdir()
            error = StringIO()
            with mock.patch.object(workflow, '_create_session') as create_session, \
                 redirect_stderr(error):
                self.assertEqual(
                    workflow.main(['start', '--target', str(target)]), 2
                )

            create_session.assert_not_called()
            self.assertIn('setup-matt-pocock-skills/references/project-context.md', error.getvalue())

    def test_matt_context_entry_may_be_in_claude(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / 'target'
            self.write_matt_context(target, 'CLAUDE.md')

            workflow._require_matt_context(target)
            self.assertFalse((target / 'AGENTS.md').exists())

    def test_matt_context_requires_references_inside_a_real_agent_skills_section(self):
        malformed_entries = (
            '```md\n## Agent skills\n```\n\n'
            'See `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, '
            'and `docs/agents/domain.md`.\n',
            '```md\n```oops\n## Agent skills\n'
            'See `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, '
            'and `docs/agents/domain.md`.\n```\n',
            '## Agent skills\n\nNo configured context.\n\n## General\n\n'
            'See `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, '
            'and `docs/agents/domain.md`.\n',
        )
        for content in malformed_entries:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / 'target'
                self.write_matt_context(target)
                (target / 'AGENTS.md').write_text(content, encoding='utf-8')

                with self.assertRaisesRegex(workflow.WorkflowError, 'setup is incomplete'):
                    workflow._require_matt_context(target)

    def test_unreadable_agents_does_not_mask_valid_claude_matt_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / 'target'
            self.write_matt_context(target, 'CLAUDE.md')
            (target / 'AGENTS.md').write_bytes(b'\xff')

            workflow._require_matt_context(target)

    def test_canonical_repository_finish_commits_or_restores_final_config_and_receipt(self):
        import os
        from project_config import repository
        from project_config.transaction import TransactionError
        configuration = workflow.project_configuration
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            origin = self.make_origin(root)
            for fail_backup in (False, True):
                with self.subTest(fail_backup=fail_backup), mock.patch.dict(
                        os.environ, {'SMARTKIT_PROJECT_CONFIG_HOME': str(root / str(fail_backup) / 'storage')}):
                    target = root / str(fail_backup) / 'target'
                    target.mkdir(parents=True)
                    self.write_matt_context(target)
                    binding = {'mode': 'repository', 'repository': 'review/config', 'branch': 'main', 'entry': 'app'}
                    config_path = target / '.agents/config.json'
                    config_path.parent.mkdir()
                    config_path.write_text(json.dumps({'maintenance': binding, 'setupVersion': '1.2.22'}), encoding='utf-8')
                    checkout = repository._checkout_path('review/config', 'main')
                    checkout.mkdir(parents=True)
                    run_git(checkout, 'init', '--quiet')
                    run_git(checkout, 'checkout', '--quiet', '-b', 'main')
                    run_git(checkout, 'remote', 'add', 'origin', 'https://github.com/review/config.git')
                    (checkout / '.git/smartkit-project-config.json').write_text(
                        json.dumps({'repository': 'review/config', 'branch': 'main'}), encoding='utf-8')
                    entry = checkout / 'projects/app'
                    entry.mkdir(parents=True)
                    configuration.initialize_entry(target, entry, [])
                    configuration.apply(target)
                    output = StringIO()
                    with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', origin.as_uri()), redirect_stdout(output):
                        self.assertEqual(workflow.main(['start', '--target', str(target)]), 0)
                    start = json.loads(output.getvalue())
                    self.assertIsNotNone(start['source_commit'])
                    session = Path(start['session'])
                    self.addCleanup(lambda session=session: workflow._remove_session(session) if session.exists() else None)
                    self.write_generated_outputs(session)
                    apply_plan = configuration.apply_plan
                    def apply(root, plan, *, postcondition=None):
                        if fail_backup and root == entry:
                            raise TransactionError(OSError('injected final backup write failure'))
                        return apply_plan(root, plan, postcondition=postcondition)
                    output, error = StringIO(), StringIO()
                    with mock.patch.object(configuration, 'apply_plan', side_effect=apply), \
                            redirect_stdout(output), redirect_stderr(error):
                        status = workflow.main(['finish', '--session', str(session)])
                    self.assertEqual(status, 2 if fail_backup else 0, error.getvalue())
                    self.assertFalse(session.exists())
                    self.assertEqual(config_path.read_bytes(), (entry / 'files/.agents/config.json').read_bytes())
                    expected_version = '1.2.22' if fail_backup else workflow.load_catalog(REPO_ROOT).plugin_version
                    self.assertEqual(json.loads(config_path.read_bytes())['setupVersion'], expected_version)
                    self.assertEqual(configuration.inspect(target)['changes'], [])
                    scope, files = configuration.backup.read_backup(entry)
                    receipt = json.loads((target / '.agents/project-config-sync.json').read_bytes())
                    self.assertEqual(receipt['sourceFingerprint'], configuration.backup.fingerprint(scope, files))
                    self.assertTrue((entry / 'files/.agents/rules/tools.md').is_file())
                    if fail_backup:
                        self.assertIn('injected final backup write failure', error.getvalue())
                        self.assertEqual(output.getvalue(), '')
                    else:
                        finish = json.loads(output.getvalue())
                        self.assertEqual(finish['check'], 'clean')
                        self.assertIn('.agents/project-config-sync.json', finish['changed_paths'])

    def test_start_and_finish_own_session_apply_check_summary_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            origin = self.make_origin(root)
            target = root / 'target'
            target.mkdir()
            self.write_matt_context(target)
            local_rule = target / '.agents/rules/40-local-testing.md'
            local_rule.parent.mkdir(parents=True)
            local_rule.write_text(
                '# Local Testing\n\n',
                encoding='utf-8',
            )
            local_skill = target / '.agents/skills/local-check/SKILL.md'
            local_skill.parent.mkdir(parents=True)
            local_skill.write_text(
                '---\nname: local-check\ndescription: Use for local checks.\n---\n',
                encoding='utf-8',
            )
            local_rule_content = local_rule.read_bytes()
            local_skill_content = local_skill.read_bytes()
            generated_resource = (
                target
                / '.agents/skills/change-set-verification/references/verification-matrix.md'
            )
            generated_resource.parent.mkdir(parents=True)
            generated_resource.write_text('# local matrix\n', encoding='utf-8')
            generated_resource_content = generated_resource.read_bytes()
            start_output = StringIO()

            with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', origin.as_uri()):
                with redirect_stdout(start_output):
                    self.assertEqual(
                        workflow.main(['start', '--target', str(target)]),
                        0,
                    )

            start = json.loads(start_output.getvalue())
            session = Path(start['session'])
            self.assertEqual(start['phase'], 'start')
            self.assertEqual(start['generated'], str(session / 'generated'))
            self.assertRegex(start['source_fingerprint'], r'^[0-9a-f]{64}$')
            self.assertTrue((session / workflow._SESSION_MARKER).is_file())
            self.assertNotIn('models', start)
            self.assertFalse((session / 'models.json').exists())

            request = json.loads((session / 'request.json').read_bytes())
            for item in request['generation_requests']:
                path = session / 'generated' / item['target']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'generated content\n')
                with redirect_stdout(StringIO()):
                    self.assertEqual(workflow.main([
                        'register', '--session', str(session), '--request-id', item['id'],
                        '--output', str(path),
                    ]), 0)
            finish_output = StringIO()
            with redirect_stdout(finish_output):
                self.assertEqual(
                    workflow.main(['finish', '--session', str(session)]), 0
                )

            finish = json.loads(finish_output.getvalue())
            self.assertEqual(finish['phase'], 'finish')
            self.assertEqual(finish['check'], 'clean')
            self.assertEqual(finish['source_mode'], 'canonical-snapshot')
            self.assertEqual(finish['source_root'], start['source_root'])
            self.assertEqual(finish['source_fingerprint'], start['source_fingerprint'])
            self.assertEqual(finish['external_skills'], [])
            self.assertEqual(finish['external_sources'], [])
            self.assertEqual(
                finish['preserved_paths'],
                [
                    '.agents/rules/40-local-testing.md',
                    '.agents/skills/change-set-verification/references/verification-matrix.md',
                    '.agents/skills/local-check/SKILL.md',
                ],
            )
            self.assertIn(
                '.agents/rules/tools.md', finish['changed_paths']
            )
            self.assertFalse(session.exists())
            self.assertTrue((target / 'AGENTS.md').is_file())
            ownership_path = target / '.agents/smartkit.lock.json'
            self.assertTrue(ownership_path.is_file())
            ownership = json.loads(ownership_path.read_text(encoding='utf-8'))
            self.assertEqual(set(ownership), {'sources', 'assets', 'contracts', 'project_sync'})
            self.assertEqual(ownership['sources'], [])
            owned_paths = {item['path'] for item in ownership['assets']}
            self.assertNotIn('.agents/rules/tools.md', owned_paths)
            self.assertNotIn(
                '.agents/skills/change-set-verification/SKILL.md', owned_paths,
            )
            self.assertIn('.codex/rules/setup-project-agents.rules', owned_paths)
            self.assertEqual(local_rule.read_bytes(), local_rule_content)
            self.assertEqual(local_skill.read_bytes(), local_skill_content)
            self.assertEqual(
                generated_resource.read_bytes(), generated_resource_content
            )

    def test_pinned_result_rejects_malformed_external_source_provenance(self):
        malformed_sources = (
            [{'id': 'missing-validated-fields'}],
            [{
                'id': 'example/repository',
                'url': 'https://github.com/other/repository',
                'requested_ref': None,
                'resolved_ref': 'main',
                'ref_kind': 'branch',
                'commit': 'a' * 40,
                'license': {
                    'spdx': 'MIT',
                    'path': 'LICENSE',
                    'sha256': 'b' * 64,
                },
                'skills': [{
                    'id': 'example/check',
                    'path': 'skills/check',
                }],
            }],
        )
        for external_sources in malformed_sources:
            with self.subTest(external_sources=external_sources):
                completed = subprocess.CompletedProcess(
                    ('python', 'setup_project_agents.py'),
                    0,
                    json.dumps({
                        'phase': 'finish',
                        'external_sources': external_sources,
                    }),
                    '',
                )
                with mock.patch.object(
                        workflow,
                        'setup_entrypoint',
                        return_value=Path('setup.py'),
                    ), \
                     mock.patch.object(
                        workflow.subprocess,
                        'run',
                        return_value=completed,
                    ), \
                     self.assertRaisesRegex(
                        workflow.WorkflowError,
                        'pinned result external sources are invalid',
                    ):
                    workflow._run_pinned(
                        'finish',
                        session=Path('/session'),
                        target=Path('/target'),
                        source=Path('/source'),
                        commit='a' * 40,
                    )

    def test_start_preserves_agent_files_before_finish(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            origin = self.make_origin(root)
            target = root / 'target'
            self.write_matt_context(target)
            codex = target / '.codex/agents/change-set-verifier.toml'
            cursor = target / '.cursor/agents/change-set-verifier.md'
            copilot = target / '.github/agents/change-set-verifier.agent.md'
            for path in (codex, cursor, copilot):
                path.parent.mkdir(parents=True, exist_ok=True)
            codex.write_bytes(
                (REPO_ROOT / 'agents/codex/change-set-verifier.toml').read_bytes()
            )
            cursor.write_text(
                '---\nmodel: cursor-existing\nreadonly: true\n---\n',
                encoding='utf-8',
            )
            copilot.write_text(
                '---\nmodel: copilot-existing\n---\n',
                encoding='utf-8',
            )
            original = {
                path: path.read_bytes() for path in (codex, cursor, copilot)
            }
            output = StringIO()

            with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', origin.as_uri()):
                with redirect_stdout(output):
                    self.assertEqual(
                        workflow.main(['start', '--target', str(target)]),
                        0,
                    )

            session = Path(json.loads(output.getvalue())['session'])
            self.assertFalse((session / 'models.json').exists())
            request = json.loads((session / 'request.json').read_text(encoding='utf-8'))
            self.assertNotIn('selected_agents', request)
            self.assertNotIn('model_requests', request)
            with redirect_stdout(StringIO()):
                self.assertEqual(
                    workflow.main(['cancel', '--session', str(session)]),
                    0,
                )
            self.assertFalse(session.exists())
            for path, content in original.items():
                self.assertEqual(path.read_bytes(), content)

    def test_finish_failure_reports_error_cleans_session_and_does_not_write_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            origin = self.make_origin(root)
            target = root / 'target'
            target.mkdir()
            self.write_matt_context(target)
            output = StringIO()
            with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', origin.as_uri()):
                with redirect_stdout(output):
                    self.assertEqual(
                        workflow.main(['start', '--target', str(target)]),
                        0,
                    )
            session = Path(json.loads(output.getvalue())['session'])
            before = tuple(target.rglob('*'))
            error = StringIO()

            with redirect_stderr(error):
                self.assertEqual(
                    workflow.main(['finish', '--session', str(session)]), 2
                )

            self.assertIn('generation manifest does not declare every generation request', error.getvalue())
            self.assertFalse(session.exists())
            self.assertEqual(tuple(target.rglob('*')), before)

    def test_finish_installs_ignored_generated_targets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            origin = self.make_origin(root)
            target = root / 'target'
            target.mkdir()
            self.write_matt_context(target)
            run_git(target, 'init', '--quiet')
            (target / '.gitignore').write_text('.agents/\n', encoding='utf-8')
            session_output = StringIO()
            with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', origin.as_uri()):
                with redirect_stdout(session_output):
                    self.assertEqual(workflow.main(['start', '--target', str(target)]), 0)
            session = Path(json.loads(session_output.getvalue())['session'])
            self.write_generated_outputs(session)
            finish_output = StringIO()

            with redirect_stdout(finish_output):
                self.assertEqual(workflow.main(['finish', '--session', str(session)]), 0)

            finish = json.loads(finish_output.getvalue())
            self.assertEqual(finish['phase'], 'finish')
            self.assertEqual(finish['check'], 'clean')
            for relative in (
                '.agents/rules/tools.md',
                '.agents/skills/change-set-verification/SKILL.md',
            ):
                self.assertTrue((target / relative).is_file())
                ignored = subprocess.run(
                    ('git', '-C', str(target), 'check-ignore', '--quiet', '--', relative),
                    check=False,
                )
                self.assertEqual(ignored.returncode, 0)
            self.assertTrue((target / 'docs/agents').is_dir())
            ownership = json.loads(
                (target / '.agents/smartkit.lock.json').read_text(encoding='utf-8')
            )
            self.assertFalse(any(
                asset['path'].startswith('docs/agents/') for asset in ownership['assets']
            ))
            self.assertFalse(session.exists())

    def test_finish_reports_actionable_undeclared_generated_directory_error(
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            origin = self.make_origin(root)
            target = root / 'target'
            target.mkdir()
            self.write_matt_context(target)
            output = StringIO()
            with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', origin.as_uri()):
                with redirect_stdout(output):
                    self.assertEqual(
                        workflow.main(['start', '--target', str(target)]),
                        0,
                    )
            session = Path(json.loads(output.getvalue())['session'])
            self.write_generated_outputs(session)
            (session / 'generated/rules').mkdir()
            error = StringIO()

            with redirect_stderr(error):
                self.assertEqual(
                    workflow.main(['finish', '--session', str(session)]), 2
                )

            self.assertIn(
                'generated output contains an undeclared directory: rules',
                error.getvalue(),
            )
            self.assertIn(
                'declare exact outputs in .setup-generation.json',
                error.getvalue(),
            )

    def test_finish_rejects_unowned_directory_without_deleting_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            unowned = Path(temp_dir)
            marker = unowned / 'keep.txt'
            marker.write_text('keep\n', encoding='utf-8')
            with redirect_stderr(StringIO()):
                self.assertEqual(
                    workflow.main(['finish', '--session', str(unowned)]), 2
                )
            self.assertEqual(marker.read_text(encoding='utf-8'), 'keep\n')

    def test_finish_rejects_request_target_tampering_and_cleans_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            origin = self.make_origin(root)
            target = root / 'target'
            other = root / 'other'
            target.mkdir()
            other.mkdir()
            self.write_matt_context(target)
            output = StringIO()
            with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', origin.as_uri()):
                with redirect_stdout(output):
                    self.assertEqual(
                        workflow.main(['start', '--target', str(target)]),
                        0,
                    )
            session = Path(json.loads(output.getvalue())['session'])
            request_path = session / 'request.json'
            request = json.loads(request_path.read_text(encoding='utf-8'))
            request['target'] = str(other)
            request_path.write_text(json.dumps(request), encoding='utf-8')
            error = StringIO()

            with redirect_stderr(error):
                self.assertEqual(
                    workflow.main(['finish', '--session', str(session)]), 2
                )

            self.assertIn('session request changed after start', error.getvalue())
            self.assertFalse(session.exists())
            self.assertTrue((target / 'docs/agents/issue-tracker.md').is_file())
            self.assertTrue((target / 'AGENTS.md').is_file())
            self.assertFalse((target / '.agents').exists())
            self.assertEqual(tuple(other.rglob('*')), ())

    def test_finish_rejects_setup_evidence_drift_before_mutation_and_keeps_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            origin = self.make_origin(root)
            target = root / 'target'
            target.mkdir()
            self.write_matt_context(target)
            output = StringIO()
            with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', origin.as_uri()):
                with redirect_stdout(output):
                    self.assertEqual(workflow.main(['start', '--target', str(target)]), 0)
            session = Path(json.loads(output.getvalue())['session'])
            self.write_generated_outputs(session)
            config = target / '.agents/config.json'
            config.parent.mkdir(parents=True)
            config.write_text('{}\n', encoding='utf-8')
            error = StringIO()

            with redirect_stderr(error):
                result = workflow.main(['finish', '--session', str(session)])

            self.assertEqual(result, 2)
            self.assertIn('target changed after start', error.getvalue())
            self.assertEqual(config.read_text(encoding='utf-8'), '{}\n')
            self.assertFalse((target / '.agents/smartkit.lock.json').exists())
            self.assertFalse(session.exists())

    def test_finish_ignores_unrelated_target_drift_and_preserves_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            origin = self.make_origin(root)
            target = root / 'target'
            target.mkdir()
            self.write_matt_context(target)
            output = StringIO()
            with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', origin.as_uri()):
                with redirect_stdout(output):
                    self.assertEqual(workflow.main(['start', '--target', str(target)]), 0)
            session = Path(json.loads(output.getvalue())['session'])
            self.write_generated_outputs(session)
            concurrent = target / 'skills/fast-mode/SKILL.md'
            concurrent.parent.mkdir(parents=True)
            concurrent.write_text('unrelated work\n', encoding='utf-8')
            finish_output = StringIO()

            with redirect_stdout(finish_output):
                result = workflow.main(['finish', '--session', str(session)])

            self.assertEqual(result, 0)
            self.assertEqual(json.loads(finish_output.getvalue())['check'], 'clean')
            self.assertEqual(concurrent.read_text(encoding='utf-8'), 'unrelated work\n')
            self.assertTrue((target / '.agents/smartkit.lock.json').is_file())
            self.assertFalse(session.exists())

    def test_start_failure_cleans_the_owned_session(self):
        session = workflow._create_session()
        target = Path(tempfile.mkdtemp(prefix='setup-workflow-target-'))
        try:
            self.write_matt_context(target)
            with mock.patch.object(workflow, '_create_session', return_value=session), \
                 mock.patch.object(bootstrap, 'main', return_value=1):
                self.assertEqual(
                    workflow.main(['start', '--target', str(target)]), 1
                )
            self.assertFalse(session.exists())
        finally:
            shutil.rmtree(target, ignore_errors=True)

    def test_cleanup_handles_readonly_git_style_files(self):
        session = workflow._create_session()
        packed = session / 'source/.git/objects/pack/example.idx'
        packed.parent.mkdir(parents=True)
        packed.write_bytes(b'index')
        packed.chmod(stat.S_IREAD)

        workflow._remove_session(session)

        self.assertFalse(session.exists())

    def test_cleanup_failure_reports_the_exact_residual_session(self):
        session = workflow._create_session()
        with mock.patch.object(
                workflow.shutil,
                'rmtree',
                side_effect=OSError('injected cleanup failure'),
            ), \
             self.assertRaisesRegex(
                workflow.WorkflowError,
                re.escape(f'cannot remove workflow session: {session}'),
            ):
            workflow._remove_session(session)

        self.assertTrue(session.exists())
        shutil.rmtree(session)

    def test_cancel_cleans_an_owned_unfinished_session(self):
        session = workflow._create_session()
        output = StringIO()

        with redirect_stdout(output):
            self.assertEqual(
                workflow.main(['cancel', '--session', str(session)]), 0
            )

        self.assertEqual(json.loads(output.getvalue())['phase'], 'cancel')
        self.assertFalse(session.exists())

    def test_terminal_operation_claim_blocks_competing_finish_or_cancel(self):
        session = workflow._create_session()
        claimed = workflow._claim_session(session)
        self.assertEqual(claimed, session)
        error = StringIO()

        with redirect_stderr(error):
            self.assertEqual(
                workflow.main(['cancel', '--session', str(session)]), 2
            )

        self.assertIn('workflow session is already claimed', error.getvalue())
        self.assertTrue(session.exists())
        self.assertEqual(
            (session / workflow._SESSION_CLAIM).read_bytes(),
            workflow._SESSION_CLAIM_CONTENT,
        )
        workflow._remove_session(session)

    def test_offline_start_and_finish_use_the_installed_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / 'target'
            target.mkdir()
            self.write_matt_context(target)
            output = StringIO()
            warning = StringIO()
            missing = (root / 'missing.git').as_uri()

            with mock.patch.object(bootstrap, 'CANONICAL_REPOSITORY', missing), \
                 redirect_stdout(output), \
                 redirect_stderr(warning):
                self.assertEqual(
                    workflow.main(['start', '--target', str(target)]),
                    0,
                )
            start = json.loads(output.getvalue())
            session = Path(start['session'])
            self.assertIsNone(start['source_commit'])
            self.assertEqual(Path(start['source_root']), REPO_ROOT)
            self.assertIn('using installed plugin source', warning.getvalue())
            self.write_generated_outputs(session)

            finish_output = StringIO()
            with redirect_stdout(finish_output):
                self.assertEqual(
                    workflow.main(['finish', '--session', str(session)]), 0
                )

            finish = json.loads(finish_output.getvalue())
            self.assertEqual(finish['source_mode'], 'installed-fallback')
            self.assertIsNone(finish['source_commit'])
            self.assertEqual(Path(finish['source_root']), REPO_ROOT)
            self.assertEqual(finish['external_sources'], [])
            self.assertFalse(session.exists())
            self.assertTrue((target / 'AGENTS.md').is_file())


class SetupVersionCommitTest(unittest.TestCase):
    def setUp(self):
        readiness = mock.patch.object(workflow, '_verify_codegraph', return_value={'ready': True, 'message': 'test MCP responds'})
        readiness.start()
        self.addCleanup(readiness.stop)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.target = Path(self.temporary.name)
        self.config = self.target / '.agents/config.json'
        self.config.parent.mkdir()
        self.config.write_text('{"setupVersion":"1.0.0","agents":[],"mcp":[]}\n', encoding='utf-8')
        self.before = self.config.read_bytes()
        self.session = workflow._create_session()
        self.addCleanup(lambda: shutil.rmtree(self.session) if self.session.exists() else None)
        self.request = {'source_commit': None, 'source_root': str(REPO_ROOT), 'harnesses': []}

    def pinned_result(self, *args, **kwargs):
        import hashlib
        return {'changed_paths': [], 'external_skills': [], 'external_sources': [],
                'preserved_paths': [],
                'setup_config_sha256': hashlib.sha256(self.config.read_bytes()).hexdigest()}

    def run_finish(self, *, pinned=None, cleanup=None, commit=None):
        from contextlib import ExitStack
        output, error = StringIO(), StringIO()
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(workflow, '_request_context', return_value=(
                self.request, self.target, REPO_ROOT, 'offline')))
            stack.enter_context(mock.patch.object(workflow, '_run_pinned', side_effect=pinned or self.pinned_result))
            if cleanup is not None:
                stack.enter_context(mock.patch.object(workflow, '_remove_session', side_effect=cleanup))
            if commit is not None:
                stack.enter_context(mock.patch.object(workflow.project_configuration, 'apply_plan', side_effect=commit))
            stack.enter_context(redirect_stdout(output))
            stack.enter_context(redirect_stderr(error))
            status = workflow.main(['finish', '--session', str(self.session)])
        return status, output.getvalue(), error.getvalue()

    def test_success_commits_only_version_after_cleanup_and_repeat_keeps_exact_bytes(self):
        status, output, _ = self.run_finish()
        self.assertEqual(status, 0)
        version = workflow.load_catalog(REPO_ROOT).plugin_version
        self.assertEqual(json.loads(self.config.read_bytes()), {'setupVersion': version, 'agents': [], 'mcp': []})
        self.assertEqual(json.loads(output)['setup_version'], version)
        self.assertTrue(json.loads(output)['codegraph']['ready'])
        self.assertFalse(self.session.exists())
        before = self.config.read_bytes()
        modified = self.config.stat().st_mtime_ns
        self.session = workflow._create_session()
        status, output, _ = self.run_finish()
        self.assertEqual(status, 0)
        self.assertEqual(self.config.read_bytes(), before)
        self.assertEqual(self.config.stat().st_mtime_ns, modified)
        self.assertNotIn('.agents/config.json', json.loads(output)['changed_paths'])

    def test_codegraph_not_ready_prevents_finish_and_version_advance(self):
        with mock.patch.object(workflow, '_verify_codegraph', side_effect=workflow.WorkflowError('CodeGraph not ready')):
            status, _, error = self.run_finish()
        self.assertEqual(status, 2)
        self.assertIn('CodeGraph not ready', error)
        self.assertEqual(self.config.read_bytes(), self.before)
        self.assertFalse(self.session.exists())

    def test_machine_only_finish_excludes_owned_outputs_without_a_source_repository(self):
        import hashlib
        from project_state.ownership import OwnedAsset, OwnershipState
        from project_config.ownership import serialize_ownership
        run_git(self.target, 'init')
        self.config.write_text(json.dumps({'setupVersion': '1.0.0', 'maintenance': {'mode': 'local-only'}}), encoding='utf-8')
        native = self.target / '.codex/agents/generated.toml'
        native.parent.mkdir(parents=True)
        native.write_bytes(b'model = "retained"\n')
        state = OwnershipState((), (OwnedAsset(
            'file', 'project-agent', PurePosixPath('.codex/agents/generated.toml'),
            hashlib.sha256(native.read_bytes()).hexdigest(),
        ),))
        (self.target / '.agents/smartkit.lock.json').write_bytes(serialize_ownership(state))
        with mock.patch.object(workflow.project_configuration, 'entry_root', side_effect=AssertionError('unexpected source repository')):
            status, output, error = self.run_finish()
        self.assertEqual(status, 0, error)
        self.assertEqual(json.loads(output)['tracked_personal_paths'], [])
        for relative in ('.agents/config.json', '.agents/skills/future/SKILL.md', '.codex/agents/generated.toml'):
            run_git(self.target, 'check-ignore', '--quiet', relative)
        self.assertEqual(native.read_bytes(), b'model = "retained"\n')
        self.assertEqual(json.loads(self.config.read_text())['maintenance'], {'mode': 'local-only'})
        self.assertFalse((self.target / '.agents/project-config-sync.json').exists())

    def test_cleanup_failure_preserves_version(self):
        status, _, error = self.run_finish(cleanup=OSError('cleanup fault'))
        self.assertEqual(status, 2)
        self.assertEqual(self.config.read_bytes(), self.before)
        self.assertIn('cleanup fault', error)

    def test_version_commit_failure_preserves_version_and_reports_partial_configuration(self):
        status, _, error = self.run_finish(commit=workflow.TransactionError(OSError('commit fault')))
        self.assertEqual(status, 2)
        self.assertEqual(self.config.read_bytes(), self.before)
        self.assertIn('configuration applied but setup version commit failed', error)
        self.assertFalse(self.session.exists())

    def test_config_change_during_cleanup_is_preserved_and_refuses_version_commit(self):
        remove = workflow._remove_session
        external = b'{"setupVersion":"1.0.0","agents":[],"mcp":[],"$schema":"external"}\n'
        def cleanup(session):
            remove(session)
            self.config.write_bytes(external)
        status, _, error = self.run_finish(cleanup=cleanup)
        self.assertEqual(status, 2)
        self.assertEqual(self.config.read_bytes(), external)
        self.assertIn('setup version commit failed', error)

    def test_config_change_after_pinned_receipt_is_detected(self):
        def pinned(*args, **kwargs):
            result = self.pinned_result()
            self.config.write_bytes(self.before + b' ')
            return result
        status, _, error = self.run_finish(pinned=pinned)
        self.assertEqual(status, 2)
        self.assertEqual(self.config.read_bytes(), self.before + b' ')
        self.assertIn('changed after pinned finish', error)

    def test_version_plan_refuses_a_new_config_preimage(self):
        build = workflow.project_configuration.build_plan
        external = b'{"setupVersion":"1.0.0","agents":[],"$schema":"external-edit"}\n'
        def changed(*args, **kwargs):
            self.config.write_bytes(external)
            return build(*args, **kwargs)
        with mock.patch.object(workflow.project_configuration, 'build_plan', side_effect=changed):
            status, _, error = self.run_finish()
        self.assertEqual(status, 2)
        self.assertEqual(self.config.read_bytes(), external)
        self.assertIn('changed during setup version planning', error)

    def test_version_plan_refuses_config_removed_after_receipt(self):
        build = workflow.project_configuration.build_plan
        def removed(*args, **kwargs):
            self.config.unlink()
            return build(*args, **kwargs)
        with mock.patch.object(workflow.project_configuration, 'build_plan', side_effect=removed):
            status, _, error = self.run_finish()
        self.assertEqual(status, 2)
        self.assertFalse(self.config.exists())
        self.assertIn('changed during setup version planning', error)


if __name__ == '__main__':
    unittest.main()
