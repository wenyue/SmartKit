"""Exercise completion with real local Git effects and an isolated GitHub boundary."""
from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('review_completion', ROOT / 'skills/review-for-humans/scripts/complete_review.py')
completion = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(completion)


class FakeGitHub:
    def __init__(self, test):
        self.test = test
        self.states = {'file.txt': 'UNVIEWED', 'already.txt': 'VIEWED'}
        self.marked = []
        self.fail_after_mark = False
        self.page_size = 100
        self.viewer = 'reviewer'
        self.override_head = None
        self.override_base = None
        self.fail_next_snapshot = False

    def graphql(self, commands, query, variables):
        head = self.override_head or self.test.remote_head()
        base = self.override_base or self.test.comparison
        if query == completion.MARK_QUERY:
            self.marked.append(variables['path'])
            self.states[variables['path']] = 'VIEWED'
            if self.fail_after_mark:
                self.fail_after_mark = False
                raise RuntimeError('lost mutation response')
            return {'markFileAsViewed': {'pullRequest': {'baseRefOid': base, 'headRefOid': head}}}
        if self.fail_next_snapshot:
            self.fail_next_snapshot = False
            raise RuntimeError('unavailable API')
        start = int(variables['cursor'] or 0)
        entries = sorted(self.states.items())[start:start + self.page_size]
        end = start + len(entries)
        return {'viewer': {'login': self.viewer}, 'repository': {'pullRequest': {
            'id': 'PR_test', 'baseRefOid': base, 'headRefOid': head, 'headRefName': 'feature',
            'headRepository': {'nameWithOwner': 'owner/repo'},
            'files': {'totalCount': len(self.states),
                      'nodes': [{'path': name, 'viewerViewedState': state} for name, state in entries],
                      'pageInfo': {'hasNextPage': end < len(self.states), 'endCursor': str(end)}}}}}

    def commit(self, commands, source, head):
        return {'sha': head, 'tree': {'sha': self.test.git('rev-parse', head + '^{tree}')},
                'parents': [{'sha': item} for item in self.test.git('rev-list', '--parents', '-n', '1', head).split()[1:]]}


class ReviewCompletionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='completion 中文 ')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.repository = self.directory / 'repo with spaces'
        self.repository.mkdir()
        self.remote = self.directory / 'remote.git'
        self.call_git('init', '--bare', str(self.remote))
        self.git('init')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Completion Test')
        self.git('config', 'commit.gpgSign', 'false')
        self.git('config', 'core.autocrlf', 'false')
        self.git('checkout', '-b', 'feature')
        self.git('commit', '--allow-empty', '-m', 'Initial comparison base')
        self.comparison = self.git('rev-parse', 'HEAD')
        (self.repository / 'file.txt').write_bytes(b'baseline\n')
        (self.repository / 'already.txt').write_bytes(b'already\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'base')
        self.base = self.git('rev-parse', 'HEAD')
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', 'origin', 'HEAD:refs/heads/feature')
        self.state = self.directory / 'private state'
        self.evidence = self.directory / 'review-evidence.txt'
        self.evidence.write_text('Checks passed and whole-file review complete. Prior action is authorized.', encoding='utf-8')
        self.github = FakeGitHub(self)
        self.patches = [patch.object(completion.Commands, 'graphql', lambda commands, query, variables: self.github.graphql(commands, query, variables)),
                        patch.object(completion.Commands, 'commit', lambda commands, source, head: self.github.commit(commands, source, head)),
                        patch.object(completion, 'source_slug', return_value='owner/repo')]
        for mocked in self.patches:
            mocked.start()
            self.addCleanup(mocked.stop)

    def call_git(self, *arguments):
        result = subprocess.run(['git'] + list(arguments), capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.decode().strip()

    def git(self, *arguments):
        return self.call_git('-C', str(self.repository), *arguments)

    def remote_head(self):
        return self.call_git('--git-dir', str(self.remote), 'rev-parse', 'refs/heads/feature')

    def request(self, mode='viewed-only', **extra):
        value = {'repository': str(self.repository), 'branch': 'feature', 'pull_request': 'owner/repo',
                 'number': 7, 'base': self.comparison, 'head': self.base, 'viewer': 'reviewer',
                 'viewed_paths': ['file.txt', 'already.txt'], 'mode': mode,
                 'evidence': [str(self.evidence)]}
        if mode == 'commit-push':
            value.update(remote='origin', message='Reviewed changes')
        value.update(extra)
        path = self.directory / 'request.json'
        path.write_text(json.dumps(value), encoding='utf-8')
        return path

    def prepare(self, mode='viewed-only', **extra):
        return completion.prepare(self.request(mode, **extra), self.state)

    def run_completion(self, prepared):
        return completion.run(self.state, prepared['plan_id'])

    def test_viewed_only_preserves_unrelated_dirty_index_and_worktree(self):
        (self.repository / 'unrelated.txt').write_bytes(b'local\n')
        self.git('add', 'unrelated.txt')
        (self.repository / 'unrelated.txt').write_bytes(b'later\n')
        before = self.git('status', '--porcelain')
        prepared = self.prepare()
        self.assertEqual(self.run_completion(prepared)['status'], 'complete')
        self.assertEqual(self.git('status', '--porcelain'), before)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.base)
        self.assertEqual(self.github.marked, ['file.txt'])
        self.run_completion(prepared)
        self.assertEqual(self.github.marked, ['file.txt'])

    def test_publish_includes_partial_staging_untracked_and_existing_outgoing_commit(self):
        (self.repository / 'earlier.txt').write_bytes(b'earlier\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Existing outgoing')
        earlier = self.git('rev-parse', 'HEAD')
        (self.repository / 'file.txt').write_bytes(b'staged\n')
        self.git('add', 'file.txt')
        (self.repository / 'file.txt').write_bytes(b'final\n')
        (self.repository / 'new file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        self.assertEqual(prepared['outgoing_commit_count'], 1)
        plan = completion.read_json(self.state / 'plan.json')
        self.assertEqual(plan['workspace']['files']['file.txt']['sha256'], completion.digest(b'final\n'))
        self.run_completion(prepared)
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.remote_head(), head)
        self.assertEqual(self.git('rev-parse', 'HEAD^'), earlier)
        self.assertEqual(self.git('show', 'HEAD:file.txt'), 'final')
        self.assertEqual(self.git('show', 'HEAD:new file.txt'), 'new')
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.run_completion(prepared)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)

    def test_staged_content_superseded_by_original_worktree_needs_no_empty_commit(self):
        (self.repository / 'file.txt').write_bytes(b'staged\n')
        self.git('add', 'file.txt')
        (self.repository / 'file.txt').write_bytes(b'baseline\n')
        prepared = self.prepare('commit-push')
        self.run_completion(prepared)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.base)
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_command_interruption_reaps_child_before_returning(self):
        commands = completion.Commands(self.repository, self.directory)
        process = Mock()
        process.pid = 123
        process.returncode = 130
        process.communicate.side_effect = KeyboardInterrupt
        with patch.object(completion.subprocess, 'Popen', return_value=process), self.assertRaises(KeyboardInterrupt):
            commands.call(['git', '--version'])
        process.wait.assert_called_once_with()
        log = completion.read_json(next(commands.logs.glob('*.command.json')))
        self.assertEqual(log['exit_code'], 130)

    def test_reuses_existing_commit_without_empty_commit(self):
        (self.repository / 'file.txt').write_bytes(b'changed\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Existing reviewed commit')
        head = self.git('rev-parse', 'HEAD')
        self.run_completion(self.prepare('commit-push'))
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(self.remote_head(), head)
        self.run_completion(completion.summary(self.state, completion.read_json(self.state / 'plan.json'), 'prepared'))
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)

    def test_existing_outgoing_lost_push_response_resumes_without_repeating_push(self):
        (self.repository / 'file.txt').write_bytes(b'outgoing\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Existing outgoing')
        head = self.git('rev-parse', 'HEAD')
        prepared = self.prepare('commit-push')
        original = completion.Commands.git
        pushed = []
        def lose_response(commands, *arguments, **options):
            value = original(commands, *arguments, **options)
            if arguments[0] == 'push':
                pushed.append(arguments)
                raise RuntimeError('lost push response')
            return value
        with patch.object(completion.Commands, 'git', lose_response), self.assertRaises(RuntimeError):
            self.run_completion(prepared)
        self.run_completion(prepared)
        self.assertEqual(self.remote_head(), head)
        self.assertEqual(len(pushed), 1)
        self.assertEqual(self.github.marked, ['file.txt'])

    @unittest.skipIf(os.name == 'nt', 'POSIX executable hook fixture')
    def test_hook_branch_drift_stops_dependent_publication_or_viewed(self):
        for hook_name in ('post-commit', 'pre-push'):
            with self.subTest(hook=hook_name):
                hook = self.repository / '.git/hooks' / hook_name
                hook.write_text('#!/bin/sh\ngit checkout -b diverted\n', encoding='utf-8')
                hook.chmod(0o755)
                (self.repository / 'file.txt').write_bytes(b'new\n')
                prepared = self.prepare('commit-push')
                with self.assertRaises(ValueError):
                    self.run_completion(prepared)
                self.assertEqual(self.git('symbolic-ref', '--short', 'HEAD'), 'diverted')
                self.assertFalse(self.github.marked)
                if hook_name == 'post-commit':
                    self.assertEqual(self.remote_head(), self.base)
                hook.unlink()
                self.git('checkout', 'feature')
                self.git('branch', '-D', 'diverted')
                self.git('reset', '--hard', self.base)
                self.git('push', 'origin', '+' + self.base + ':refs/heads/feature')
                self.state = self.directory / 'second private state'

    def test_scoped_push_does_not_follow_tags_or_push_submodules(self):
        (self.repository / 'file.txt').write_bytes(b'outgoing\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Existing outgoing')
        self.git('tag', '-a', 'private-unselected', '-m', 'not in authorized scope')
        self.git('config', 'push.followTags', 'true')
        self.git('config', 'push.recurseSubmodules', 'on-demand')
        self.run_completion(self.prepare('commit-push'))
        self.assertEqual(self.git('ls-remote', '--tags', 'origin'), '')

    def test_mirrored_push_remote_is_rejected_before_commit_or_publication(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        self.git('config', 'remote.origin.mirror', 'true')
        with self.assertRaises(ValueError):
            self.prepare('commit-push')
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.base)
        self.assertEqual(self.remote_head(), self.base)
        self.assertFalse(self.github.marked)

    def test_split_fetch_push_url_reads_the_actual_publication_destination(self):
        mirror = self.directory / 'fetch-mirror.git'
        self.call_git('clone', '--bare', str(self.remote), str(mirror))
        self.git('remote', 'set-url', 'origin', str(mirror))
        self.git('remote', 'set-url', '--push', 'origin', str(self.remote))
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        self.run_completion(prepared)
        self.run_completion(prepared)
        self.assertEqual(self.remote_head(), self.git('rev-parse', 'HEAD'))
        self.assertEqual(self.call_git('--git-dir', str(mirror), 'rev-parse', 'refs/heads/feature'), self.base)

    def test_log_write_failure_after_spawn_reaps_real_child(self):
        commands = completion.Commands(self.repository, self.directory)
        original_write = completion.write_json
        original_spawn = subprocess.Popen
        children = []
        def fail_pid(path, value):
            if isinstance(value, dict) and 'pid' in value:
                raise OSError('state write failed after spawn')
            return original_write(path, value)
        def spawn(*arguments, **options):
            process = original_spawn(*arguments, **options)
            children.append(process)
            return process
        with patch.object(completion, 'write_json', fail_pid), patch.object(completion.subprocess, 'Popen', spawn):
            with self.assertRaises(OSError):
                commands.call([sys.executable, '-c', 'import time; time.sleep(0.05)'])
        self.assertIsNotNone(children[0].poll())

    def test_stale_command_instances_never_overwrite_prior_logs(self):
        first = completion.Commands(self.repository, self.directory)
        second = completion.Commands(self.repository, self.directory)
        first.git('rev-parse', 'HEAD')
        before = {path: path.read_bytes() for path in first.logs.iterdir()}
        second.git('status', '--porcelain')
        self.assertTrue(all(path.read_bytes() == content for path, content in before.items()))
        self.assertEqual(len(list(first.logs.glob('*.command.json'))), 2)

    def test_cli_rejected_existing_state_locations_remain_unchanged(self):
        for state in (self.repository, self.directory):
            with self.subTest(state=str(state)):
                sentinel = state / 'failure.log'
                sentinel.write_bytes(b'unowned sentinel')
                before = {path: path.read_bytes() for path in state.iterdir() if path.is_file()}
                with patch('sys.stdout', io.StringIO()):
                    self.assertEqual(completion.main(['prepare', '--input', str(self.request()), '--state', str(state)]), 1)
                self.assertEqual(sentinel.read_bytes(), b'unowned sentinel')
                self.assertTrue(all(path.read_bytes() == content for path, content in before.items()))

    def test_rejects_content_index_evidence_viewer_and_base_drift(self):
        prepared = self.prepare()
        for drift, undo in (
            (lambda: (self.repository / 'file.txt').write_bytes(b'drift\n'), lambda: (self.repository / 'file.txt').write_bytes(b'baseline\n')),
            (lambda: self.evidence.write_bytes(b'drift'), lambda: self.evidence.write_text('Checks passed and whole-file review complete. Prior action is authorized.', encoding='utf-8')),
            (lambda: setattr(self.github, 'viewer', 'another'), lambda: setattr(self.github, 'viewer', 'reviewer')),
            (lambda: setattr(self.github, 'override_base', 'b' * 40), lambda: setattr(self.github, 'override_base', None))):
            drift()
            with self.assertRaises(ValueError):
                self.run_completion(prepared)
            undo()
        self.assertFalse(self.github.marked)

    def test_incorrect_plan_confirmation_never_mutates(self):
        self.prepare()
        with self.assertRaises(ValueError):
            completion.run(self.state, '0' * 64)
        self.assertFalse(self.github.marked)

    def test_partial_viewed_response_is_reconciled_without_repeating_write(self):
        self.github.states['already.txt'] = 'UNVIEWED'
        self.github.fail_after_mark = True
        prepared = self.prepare()
        with self.assertRaises(RuntimeError):
            self.run_completion(prepared)
        self.assertEqual(self.github.marked, ['file.txt'])
        self.run_completion(prepared)
        self.assertEqual(self.github.marked, ['file.txt', 'already.txt'])

    def test_paginates_complete_viewed_states(self):
        self.github.page_size = 1
        prepared = self.prepare()
        self.run_completion(prepared)
        self.assertEqual(self.github.marked, ['file.txt'])

    def test_lost_push_response_resumes_from_actual_remote(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        original = completion.Commands.git
        pushed = []
        def lose_response(commands, *arguments, **options):
            value = original(commands, *arguments, **options)
            if arguments[0] == 'push':
                pushed.append(arguments)
                raise RuntimeError('lost push response')
            return value
        with patch.object(completion.Commands, 'git', lose_response), self.assertRaises(RuntimeError):
            self.run_completion(prepared)
        self.assertEqual(len(pushed), 1)
        self.run_completion(prepared)
        self.assertEqual(self.remote_head(), self.git('rev-parse', 'HEAD'))
        self.assertEqual(len(pushed), 1)

    def test_lost_commit_response_resumes_from_actual_tree_and_parent(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        original = completion.Commands.git
        committed = []
        def lose_response(commands, *arguments, **options):
            value = original(commands, *arguments, **options)
            if arguments[0] == 'commit':
                committed.append(arguments)
                raise RuntimeError('lost commit response')
            return value
        with patch.object(completion.Commands, 'git', lose_response), self.assertRaises(RuntimeError):
            self.run_completion(prepared)
        head = self.git('rev-parse', 'HEAD')
        self.run_completion(prepared)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(len(committed), 1)

    @unittest.skipIf(os.name == 'nt', 'POSIX executable hook fixture')
    def test_normal_commit_hooks_run_and_content_drift_stops_publication(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        hook = self.repository / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\necho hook-ran > hook-result\necho changed-by-hook > file.txt\ngit add file.txt\n', encoding='utf-8')
        hook.chmod(0o755)
        prepared = self.prepare('commit-push')
        with self.assertRaises(ValueError):
            self.run_completion(prepared)
        self.assertTrue((self.repository / 'hook-result').exists())
        self.assertEqual(self.remote_head(), self.base)
        self.assertFalse(self.github.marked)

    def test_unsupported_amend_and_in_worktree_state_fail_before_effects(self):
        with self.assertRaises(ValueError):
            self.prepare('commit-push', requires_amend=True)
        with self.assertRaises(ValueError):
            completion.prepare(self.request(), self.repository / 'state')
        self.assertEqual(self.remote_head(), self.base)
        self.assertFalse(self.github.marked)

    def test_inherited_git_routing_is_removed(self):
        with patch.dict(os.environ, {'GIT_DIR': '/wrong', 'GIT_WORK_TREE': '/wrong', 'GIT_INDEX_FILE': '/wrong'}):
            self.run_completion(self.prepare())
        self.assertEqual(self.github.marked, ['file.txt'])

    def test_source_ref_drift_stops_before_staging(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        self.github.override_head = 'c' * 40
        with self.assertRaises(ValueError):
            self.run_completion(prepared)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.base)
        self.assertFalse(self.github.marked)

    def test_missing_api_never_marks_viewed(self):
        prepared = self.prepare()
        self.github.fail_next_snapshot = True
        with self.assertRaises(RuntimeError):
            self.run_completion(prepared)
        self.assertFalse(self.github.marked)

    def test_cli_summary_is_bounded_and_full_logs_are_retained(self):
        prepared = self.prepare()
        output = io.StringIO()
        with patch('sys.stdout', output):
            self.assertEqual(completion.main(['run', '--state', str(self.state), '--confirm', prepared['plan_id']]), 0)
        summary = json.loads(output.getvalue())
        self.assertEqual(summary['status'], 'complete')
        self.assertLess(len(output.getvalue()), 2000)
        commands = list((self.state / 'logs').glob('*.command.json'))
        self.assertTrue(commands)
        self.assertTrue(all('exit_code' in completion.read_json(path) for path in commands))


if __name__ == '__main__':
    unittest.main()
