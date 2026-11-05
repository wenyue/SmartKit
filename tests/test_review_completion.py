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
        self.source_branch = 'feature'
        self.dynamic_files = False
        self.omitted_path = None

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
        if self.dynamic_files:
            names = commands.git('diff', '--name-only', '--find-renames',
                                 self.test.comparison + '...' + self.test.remote_head()).decode().splitlines()
            self.states = {name: self.states.get(name, 'UNVIEWED') for name in names if name != self.omitted_path}
        start = int(variables['cursor'] or 0)
        entries = sorted(self.states.items())[start:start + self.page_size]
        end = start + len(entries)
        return {'viewer': {'login': self.viewer}, 'repository': {'pullRequest': {
            'id': 'PR_test', 'baseRefOid': base, 'headRefOid': head, 'headRefName': self.source_branch,
            'headRepository': {'nameWithOwner': 'owner/repo'},
            'files': {'totalCount': len(self.states),
                      'nodes': [{'path': name, 'viewerViewedState': state} for name, state in entries],
                      'pageInfo': {'hasNextPage': end < len(self.states), 'endCursor': str(end)}}}}}

    def commit(self, commands, source, head):
        return {'sha': head, 'tree': {'sha': self.test.git('rev-parse', head + '^{tree}')},
                'parents': [{'sha': item} for item in self.test.git('rev-list', '--parents', '-n', '1', head).split()[1:]]}


class CompletionFixture:
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix='completion 中文 ')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.repository = self.directory / 'repo with spaces'
        self.repository.mkdir()
        self.state = self.directory / 'private state'
        self.evidence = self.directory / 'review-evidence.txt'
        self.evidence.write_text('Checks passed and whole-file review complete. Prior action is authorized.', encoding='utf-8')
        self.comparison = 'a' * 40
        self.base = 'b' * 40

    def request(self, mode: str = 'viewed-only', **extra: object) -> Path:
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
class ReviewCompletionTests(CompletionFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
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
        self.github = FakeGitHub(self)
        self.github.dynamic_files = True
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
        self.assertEqual(self.remote_head(), self.git('rev-parse', 'HEAD'))
        self.assertEqual(self.call_git('--git-dir', str(mirror), 'rev-parse', 'refs/heads/feature'), self.base)

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

    def test_partial_viewed_response_is_reconciled_without_repeating_write(self):
        self.github.states['already.txt'] = 'UNVIEWED'
        self.github.fail_after_mark = True
        prepared = self.prepare()
        with self.assertRaises(RuntimeError):
            self.run_completion(prepared)
        self.assertEqual(self.github.marked, ['file.txt'])
        self.run_completion(prepared)
        self.assertEqual(self.github.marked, ['file.txt', 'already.txt'])

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

    def test_in_worktree_state_fails_before_effects(self):
        with self.assertRaises(ValueError):
            completion.prepare(self.request(), self.repository / 'state')
        self.assertEqual(self.remote_head(), self.base)
        self.assertFalse(self.github.marked)

    def test_published_amend_preserves_parents_and_uses_exact_lease(self):
        (self.repository / 'file.txt').write_bytes(b'amended\n')
        prepared = self.prepare('commit-push', requires_amend=True)
        original = completion.Commands.git
        pushes = []
        def record(commands, *arguments, **options):
            if arguments[0] == 'push':
                pushes.append(arguments)
            return original(commands, *arguments, **options)
        with patch.object(completion.Commands, 'git', record):
            self.run_completion(prepared)
            self.run_completion(prepared)
        self.assertEqual(self.git('rev-parse', 'HEAD^'), self.comparison)
        self.assertEqual(self.remote_head(), self.git('rev-parse', 'HEAD'))
        self.assertEqual(self.git('show', 'HEAD:file.txt'), 'amended')
        self.assertEqual(len(pushes), 1)
        self.assertIn('--force-with-lease=refs/heads/feature:' + self.base, pushes[0])

    def test_unpublished_amend_retains_earlier_outgoing_and_pushes_normally(self):
        (self.repository / 'earlier.txt').write_bytes(b'earlier\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Earlier outgoing')
        earlier = self.git('rev-parse', 'HEAD')
        (self.repository / 'file.txt').write_bytes(b'first repair\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Review repair')
        replaced = self.git('rev-parse', 'HEAD')
        (self.repository / 'file.txt').write_bytes(b'final repair\n')
        prepared = self.prepare('commit-push', requires_amend=True)
        original = completion.Commands.git
        pushes = []
        def record(commands, *arguments, **options):
            if arguments[0] == 'push':
                pushes.append(arguments)
            return original(commands, *arguments, **options)
        with patch.object(completion.Commands, 'git', record):
            self.run_completion(prepared)
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.git('rev-parse', 'HEAD^'), earlier)
        self.assertNotEqual(head, replaced)
        self.assertEqual(self.git('rev-list', '--reverse', self.base + '..HEAD').splitlines(), [earlier, head])
        self.assertEqual(self.git('show', 'HEAD:earlier.txt'), 'earlier')
        self.assertEqual(self.remote_head(), head)
        self.assertFalse(any(argument.startswith('--force') for argument in pushes[0]))

    def test_false_amend_creates_requested_new_commit_and_true_no_change_reuses_head(self):
        (self.repository / 'file.txt').write_bytes(b'new commit\n')
        self.run_completion(self.prepare('commit-push', requires_amend=False))
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.git('rev-parse', 'HEAD^'), self.base)
        self.base = head
        self.state = self.directory / 'unchanged amendment'
        self.run_completion(self.prepare('commit-push', requires_amend=True))
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)

    def test_amend_preserves_all_merge_parents_and_their_outgoing_history(self):
        self.git('checkout', '-b', 'side', self.comparison)
        (self.repository / 'side.txt').write_bytes(b'side\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Side change')
        side = self.git('rev-parse', 'HEAD')
        self.git('checkout', 'feature')
        self.git('merge', '--no-ff', 'side', '-m', 'Review merge')
        (self.repository / 'file.txt').write_bytes(b'merge repair\n')
        self.run_completion(self.prepare('commit-push', requires_amend=True, viewed_paths=['side.txt']))
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.git('rev-list', '--parents', '-n', '1', head).split()[1:], [self.base, side])
        self.assertEqual(self.git('rev-list', '--reverse', self.base + '..' + head).splitlines(), [side, head])
        self.assertEqual(self.github.marked, ['side.txt'])

    @unittest.skipIf(os.name == 'nt', 'POSIX executable hook fixture')
    def test_amend_runs_normal_hooks_and_stops_on_changed_checked_tree(self):
        (self.repository / 'file.txt').write_bytes(b'amended\n')
        hook = self.repository / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\necho hook-change > file.txt\ngit add file.txt\n', encoding='utf-8')
        hook.chmod(0o755)
        prepared = self.prepare('commit-push', requires_amend=True)
        with self.assertRaises(ValueError):
            self.run_completion(prepared)
        self.assertEqual(self.git('show', 'HEAD:file.txt'), 'hook-change')
        self.assertEqual(self.remote_head(), self.base)
        self.assertFalse(self.github.marked)

    def test_amend_rejects_nonboolean_viewed_only_and_protected_branches(self):
        for mode, value in (('commit-push', 'true'), ('viewed-only', True)):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.prepare(mode, requires_amend=value)
        self.git('branch', '-m', 'main')
        with self.assertRaises(ValueError):
            self.prepare('commit-push', branch='main', requires_amend=True)
        self.git('branch', '-m', 'feature')
        self.state = self.directory / 'protected remote'
        self.github.source_branch = 'main'
        with self.assertRaises(ValueError):
            self.prepare('commit-push', requires_amend=True)
        self.assertEqual(self.remote_head(), self.base)
        self.assertFalse(self.github.marked)

    def test_amend_lost_commit_and_push_responses_reuse_actual_effects(self):
        (self.repository / 'file.txt').write_bytes(b'amended\n')
        prepared = self.prepare('commit-push', requires_amend=True)
        original = completion.Commands.git
        attempted = []
        def lose_response(commands, *arguments, **options):
            result = original(commands, *arguments, **options)
            if arguments[0] in ('commit', 'push'):
                attempted.append(arguments[0])
                raise RuntimeError('lost ' + arguments[0] + ' response')
            return result
        with patch.object(completion.Commands, 'git', lose_response):
            with self.assertRaises(RuntimeError):
                self.run_completion(prepared)
            amended = self.git('rev-parse', 'HEAD')
            with self.assertRaises(RuntimeError):
                self.run_completion(prepared)
            self.run_completion(prepared)
        self.assertEqual(attempted, ['commit', 'push'])
        self.assertEqual(self.git('rev-parse', 'HEAD'), amended)
        self.assertEqual(self.remote_head(), amended)
        self.assertEqual(self.github.marked, ['file.txt'])

    def test_exact_lease_rejects_source_race_without_viewed_or_rollback(self):
        (self.repository / 'file.txt').write_bytes(b'amended\n')
        prepared = self.prepare('commit-push', requires_amend=True)
        drift = self.git('commit-tree', self.git('rev-parse', self.base + '^{tree}'),
                         '-p', self.base, '-m', 'Concurrent source update')
        original = completion.Commands.git
        def race(commands, *arguments, **options):
            if arguments[0] == 'push':
                self.git('push', 'origin', drift + ':refs/heads/feature')
            return original(commands, *arguments, **options)
        with patch.object(completion.Commands, 'git', race), self.assertRaises(RuntimeError):
            self.run_completion(prepared)
        self.assertEqual(self.remote_head(), drift)
        self.assertNotEqual(self.git('rev-parse', 'HEAD'), self.base)
        self.assertFalse(self.github.marked)

    def test_commit_push_without_viewed_and_viewed_only_empty_rejection(self):
        with self.assertRaises(ValueError):
            self.prepare(viewed_paths=[])
        (self.repository / 'file.txt').write_bytes(b'publish only\n')
        prepared = self.prepare('commit-push', viewed_paths=[])
        result = self.run_completion(prepared)
        self.assertEqual(result['viewed_count'], 0)
        self.assertEqual(self.remote_head(), self.git('rev-parse', 'HEAD'))
        self.assertFalse(self.github.marked)

    def test_new_viewed_path_is_checked_in_intended_diff_then_published(self):
        (self.repository / 'new.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push', viewed_paths=['new.txt'])
        plan = completion.read_json(self.state / 'plan.json')
        self.assertNotIn('new.txt', plan['pr']['files'])
        self.assertIn('new.txt', plan['intended_pr_paths'])
        self.run_completion(prepared)
        self.assertEqual(self.github.marked, ['new.txt'])
        self.assertEqual(self.git('show', 'HEAD:new.txt'), 'new')

    def test_viewed_path_outside_intended_diff_stops_before_real_effects(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        with self.assertRaises(ValueError):
            self.prepare('commit-push', viewed_paths=['missing.txt'])
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.base)
        self.assertEqual(self.git('diff', '--cached', '--name-only'), '')
        self.assertFalse(self.github.marked)

    def test_new_viewed_path_missing_after_publication_preserves_push_for_resume(self):
        (self.repository / 'new.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push', viewed_paths=['new.txt'])
        self.github.omitted_path = 'new.txt'
        with self.assertRaises(ValueError):
            self.run_completion(prepared)
        published = self.remote_head()
        self.assertNotEqual(published, self.base)
        self.assertFalse(self.github.marked)
        self.github.omitted_path = None
        self.run_completion(prepared)
        self.assertEqual(self.remote_head(), published)
        self.assertEqual(self.github.marked, ['new.txt'])

    def test_legacy_v1_plan_reuses_existing_outgoing_commit(self):
        (self.repository / 'file.txt').write_bytes(b'outgoing\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Existing outgoing')
        head = self.git('rev-parse', 'HEAD')
        self.prepare('commit-push')
        plan = completion.read_json(self.state / 'plan.json')
        del plan['original_parents']
        del plan['intended_pr_paths']
        completion.write_json(self.state / 'plan.json', plan)
        identity = completion.digest(completion.encoded(plan))
        completion.write_json(self.state / 'progress.json', {'plan_id': identity, 'phase': 'prepared'})
        completion.run(self.state, identity)
        completion.run(self.state, identity)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(self.remote_head(), head)

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

class CommandAndCliTests(CompletionFixture, unittest.TestCase):
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
        first.call([sys.executable, '-c', 'print(1)'])
        before = {path: path.read_bytes() for path in first.logs.iterdir()}
        second.call([sys.executable, '-c', 'print(2)'])
        self.assertTrue(all(path.read_bytes() == content for path, content in before.items()))
        self.assertEqual(len(list(first.logs.glob('*.command.json'))), 2)

        self.assertTrue(all('exit_code' in completion.read_json(path) for path in first.logs.glob('*.command.json')))

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

    def test_incorrect_plan_confirmation_never_mutates(self):
        self.state.mkdir(mode=0o700)
        completion.write_json(self.state / 'plan.json', {'version': 1})
        with patch.object(completion, 'references') as evidence, patch.object(completion, 'Commands') as commands:
            with self.assertRaises(ValueError):
                completion.run(self.state, '0' * 64)
        evidence.assert_not_called()
        commands.assert_not_called()

    def test_paginates_complete_viewed_states(self):
        identity = Mock()
        identity.remote_head.return_value = self.base
        identity.comparison = self.comparison
        github = FakeGitHub(identity)
        github.page_size = 1
        commands = Mock(spec=completion.Commands)
        cursors = []

        def page(query, variables):
            cursors.append(variables['cursor'])
            return github.graphql(commands, query, variables)

        commands.graphql.side_effect = page
        result = completion.pr_snapshot(commands, {'pull_request': 'owner/repo', 'number': 7})
        self.assertEqual(result['files'], github.states)
        self.assertEqual(cursors, [None, '1'])

    def test_cli_summary_is_bounded_and_counts_the_full_plan(self):
        plan = {
            'request': {'mode': 'commit-push', 'viewed_paths': ['file-{}'.format(i) for i in range(1000)]},
            'workspace': {'head': self.base, 'files': {'large-file': {'content': 'private' * 10000}}},
            'outgoing': ['c' * 40] * 1000,
        }
        summary = completion.summary(self.state, plan, 'complete')
        output = io.StringIO()
        with patch.object(completion, 'run', return_value=summary) as run, patch('sys.stdout', output):
            self.assertEqual(completion.main(['run', '--state', str(self.state), '--confirm', 'd' * 64]), 0)
        run.assert_called_once_with(self.state.resolve(), 'd' * 64)
        value = json.loads(output.getvalue())
        self.assertEqual(value['status'], 'complete')
        self.assertEqual(value['viewed_count'], 1000)
        self.assertEqual(value['outgoing_commit_count'], 1000)
        self.assertEqual(value['changed_path_count'], 1)
        self.assertLess(len(output.getvalue()), 2000)


if __name__ == '__main__':
    unittest.main()
