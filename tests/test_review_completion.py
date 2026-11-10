"""Exercise completion with real local Git effects and an isolated GitHub boundary."""
from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import base64
from datetime import datetime
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
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
        self.source = 'owner/repo'
        self.override_head = None
        self.override_base = None
        self.fail_next_snapshot = False
        self.uploads = []
        self.updates = []
        self.fail_after_update = False
        self.wrong_commit_sha = False
        self.before_update = None

    def graphql(self, commands, query, variables):
        head = self.override_head or self.test.remote_head()
        base = self.override_base or self.test.comparison
        if query == completion.UPDATE_QUERY:
            update = variables['input']['refUpdates'][0]
            self.updates.append(variables['input'])
            if self.before_update:
                self.before_update()
            self.test.call_git('--git-dir', str(self.test.remote), 'update-ref', update['name'],
                               update['afterOid'], update['beforeOid'])
            if self.fail_after_update:
                self.fail_after_update = False
                raise RuntimeError('lost ref-update response')
            return {'updateRefs': {'clientMutationId': None}}
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
            'headRepository': {'id': 'REPO_source', 'nameWithOwner': self.source},
            'files': {'totalCount': len(self.states),
                      'nodes': [{'path': name, 'viewerViewedState': state} for name, state in entries],
                      'pageInfo': {'hasNextPage': end < len(self.states), 'endCursor': str(end)}}}}}

    def commit(self, commands, source, head):
        return {'sha': head, 'tree': {'sha': self.test.git('rev-parse', head + '^{tree}')},
                'parents': [{'sha': item} for item in self.test.git('rev-list', '--parents', '-n', '1', head).split()[1:]]}

    def api(self, commands, method, path, payload=None):
        if method == 'GET':
            return {'ref': 'refs/heads/feature', 'object': {'type': 'commit', 'sha': self.test.remote_head()}}
        kind = path.rsplit('/', 1)[1]
        self.uploads.append((kind, payload))
        if kind == 'blobs':
            raw = base64.b64decode(payload['content'])
            arguments = ['hash-object', '-t', 'blob', '-w', '--stdin']
        elif kind == 'trees':
            raw = b''.join(('%s %s %s\t' % (entry['mode'], entry['type'], entry['sha'])).encode('ascii')
                           + entry['path'].encode('utf-8') + b'\0' for entry in payload['tree'])
            arguments = ['mktree', '-z']
        else:
            headers = ['tree ' + payload['tree']] + ['parent ' + parent for parent in payload['parents']]
            for key in ('author', 'committer'):
                identity = payload[key]
                date = datetime.fromisoformat(identity['date'])
                headers.append('%s %s <%s> %s %s' % (key, identity['name'], identity['email'],
                                                    int(date.timestamp()), date.strftime('%z')))
            raw = ('\n'.join(headers) + '\n\n' + payload['message']).encode('utf-8')
            arguments = ['hash-object', '-t', 'commit', '-w', '--stdin']
        result = subprocess.run(['git', '--git-dir', str(self.test.remote)] + arguments,
                                input=raw, capture_output=True, timeout=20)
        self.test.assertEqual(result.returncode, 0, result.stderr)
        oid = result.stdout.decode().strip()
        if kind == 'commits' and self.wrong_commit_sha:
            oid = 'f' * 40
        return {'sha': oid}


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
        if mode != 'viewed-only':
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
        self.original_graphql = completion.Commands.graphql
        self.patches = [patch.object(completion.Commands, 'graphql', lambda commands, query, variables, **options: self.github.graphql(commands, query, variables)),
                        patch.object(completion.Commands, 'commit', lambda commands, source, head: self.github.commit(commands, source, head)),
                        patch.object(completion.Commands, 'api', lambda commands, method, path, payload=None: self.github.api(commands, method, path, payload)),
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

    def run_completion(self, prepared, transport='git'):
        return completion.run(self.state, prepared['plan_id'], transport)

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

    def test_transient_initial_snapshot_retries_from_first_page(self):
        self.github.page_size = 1
        original = self.github.graphql
        cursors = []
        failed = []
        def snapshot(commands, query, variables):
            cursors.append(variables['cursor'])
            if variables['cursor'] == '1' and not failed:
                failed.append(True)
                raise completion.ViewedRequestFailure()
            return original(commands, query, variables)
        with patch.object(self.github, 'graphql', snapshot), patch.object(completion.time, 'sleep') as sleep:
            self.prepare()
        self.assertEqual(cursors, [None, '1', None, '1'])
        sleep.assert_called_once_with(1)
        self.assertFalse(self.github.marked)

    def test_transient_lost_mark_reconciles_and_skips_confirmed_write(self):
        self.github.states['already.txt'] = 'UNVIEWED'
        prepared = self.prepare()
        original = self.github.graphql
        failed = []
        def lost_response(commands, query, variables):
            result = original(commands, query, variables)
            if query == completion.MARK_QUERY and not failed:
                failed.append(True)
                raise completion.ViewedRequestFailure()
            return result
        with patch.object(self.github, 'graphql', lost_response), patch.object(completion.time, 'sleep') as sleep:
            result = self.run_completion(prepared)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(self.github.marked, ['file.txt', 'already.txt'])
        sleep.assert_called_once_with(1)

    def test_transient_final_readback_retries_without_repeating_mark(self):
        prepared = self.prepare()
        original = self.github.graphql
        failed = []
        def final_readback(commands, query, variables):
            if query == completion.PR_QUERY and self.github.marked and not failed:
                failed.append(True)
                raise completion.ViewedRequestFailure()
            return original(commands, query, variables)
        with patch.object(self.github, 'graphql', final_readback), patch.object(completion.time, 'sleep'):
            self.assertEqual(self.run_completion(prepared)['status'], 'complete')
        self.assertEqual(self.github.marked, ['file.txt'])

    def test_successful_header_body_transport_failures_retry_and_reconcile(self):
        prepared = self.prepare()
        original_call = completion.Commands.call
        for phase, stderr in (('initial', b'unexpected EOF'), ('mark', b'connection reset by peer'),
                              ('final', b'unexpected EOF')):
            self.github.states['file.txt'] = 'UNVIEWED'
            self.github.marked.clear()
            failed = []
            events = []
            def github_call(commands, arguments, **options):
                if arguments[0] != 'gh':
                    return original_call(commands, arguments, **options)
                payload = options['input_value']
                query, variables = payload['query'], payload['variables']
                kind = 'mark' if query == completion.MARK_QUERY else 'snapshot'
                events.append(kind)
                value = self.github.graphql(commands, query, variables)
                should_fail = ((phase == 'initial' and len(events) == 1) or
                               (phase == 'mark' and kind == 'mark') or
                               (phase == 'final' and kind == 'snapshot' and self.github.marked))
                if should_fail and not failed:
                    failed.append(len(events))
                    prefix = commands.logs / 'body-read-failure'
                    prefix.with_suffix('.stdout').write_bytes(b'HTTP/2.0 200 OK\r\nContent-Type: application/json\r\n\r\n')
                    prefix.with_suffix('.stderr').write_bytes(stderr)
                    raise completion.CommandFailure(arguments, 1, prefix)
                return b'HTTP/2.0 200 OK\r\n\r\n' + completion.encoded({'data': value})
            with self.subTest(phase=phase), patch.object(completion.Commands, 'graphql', self.original_graphql), \
                    patch.object(completion.Commands, 'call', github_call), \
                    patch.object(completion.time, 'sleep') as sleep:
                self.assertEqual(self.run_completion(prepared)['status'], 'complete')
                sleep.assert_called_once_with(1)
                self.assertEqual(len(failed), 1)
                self.assertEqual(events[failed[0]], 'snapshot')
                self.assertEqual(self.github.marked, ['file.txt'])

    def test_viewed_retries_stop_after_five_attempts_and_preserve_pending_phase(self):
        prepared = self.prepare()
        original = self.github.graphql
        attempts = []
        def unavailable(commands, query, variables):
            if query == completion.MARK_QUERY:
                attempts.append(variables['path'])
                raise completion.ViewedRequestFailure()
            return original(commands, query, variables)
        with patch.object(self.github, 'graphql', unavailable), patch.object(completion.time, 'sleep') as sleep:
            with self.assertRaisesRegex(RuntimeError, 'retry budget exhausted'):
                self.run_completion(prepared)
        self.assertEqual(attempts, ['file.txt'] * 5)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2, 4, 8])
        self.assertEqual(completion.read_json(self.state / 'progress.json')['phase'], 'viewed')
        self.assertFalse((self.state / 'result.json').exists())
        self.assertEqual(self.remote_head(), self.base)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.base)

    def test_viewed_retry_revalidates_version_viewer_source_workspace_and_evidence(self):
        prepared = self.prepare()
        original = self.github.graphql
        for drift, undo in (
                (lambda: setattr(self.github, 'override_head', 'c' * 40), lambda: setattr(self.github, 'override_head', None)),
                (lambda: setattr(self.github, 'viewer', 'another'), lambda: setattr(self.github, 'viewer', 'reviewer')),
                (lambda: setattr(self.github, 'override_base', 'c' * 40), lambda: setattr(self.github, 'override_base', None)),
                (lambda: setattr(self.github, 'source', 'another/repo'), lambda: setattr(self.github, 'source', 'owner/repo')),
                (lambda: self.git('rm', '--cached', 'file.txt'), lambda: self.git('reset', '--', 'file.txt')),
                (lambda: self.evidence.write_bytes(b'drift'), lambda: self.evidence.write_text('Checks passed and whole-file review complete. Prior action is authorized.', encoding='utf-8')),
                (lambda: (self.repository / 'file.txt').write_bytes(b'drift'), lambda: (self.repository / 'file.txt').write_bytes(b'baseline\n'))):
            failed = []
            def unavailable(commands, query, variables):
                if query == completion.MARK_QUERY:
                    failed.append(True)
                    raise completion.ViewedRequestFailure()
                return original(commands, query, variables)
            with self.subTest(drift=drift), patch.object(self.github, 'graphql', unavailable), \
                    patch.object(completion.time, 'sleep', side_effect=lambda delay: drift()):
                with self.assertRaises(ValueError):
                    self.run_completion(prepared)
            undo()
            self.assertEqual(len(failed), 1)
        self.assertFalse(self.github.marked)

    def test_recording_shares_deadline_across_requests_and_rate_waits(self):
        prepared = self.prepare()
        original = self.github.graphql
        now = [0]
        attempts = []
        def unavailable(commands, query, variables):
            if query == completion.MARK_QUERY:
                attempts.append(variables['path'])
                now[0] += 30
                raise completion.ViewedRequestFailure(60)
            return original(commands, query, variables)
        def sleep(delay):
            now[0] += delay
        with patch.object(self.github, 'graphql', unavailable), \
                patch.object(completion.time, 'monotonic', side_effect=lambda: now[0]), \
                patch.object(completion.time, 'sleep', side_effect=sleep) as waits:
            with self.assertRaisesRegex(RuntimeError, 'retry budget exhausted'):
                self.run_completion(prepared)
        self.assertEqual(attempts, ['file.txt', 'file.txt'])
        waits.assert_called_once_with(60)
        self.assertEqual(now[0], 120)
        self.assertEqual(completion.read_json(self.state / 'progress.json')['phase'], 'viewed')

    def test_publication_failure_is_not_automatically_retried(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        original = completion.Commands.git
        pushes = []
        def unavailable(commands, *arguments, **options):
            if arguments[0] == 'push':
                pushes.append(arguments)
                raise RuntimeError('connection reset')
            return original(commands, *arguments, **options)
        with patch.object(completion.Commands, 'git', unavailable), patch.object(completion.time, 'sleep') as sleep:
            with self.assertRaises(RuntimeError):
                self.run_completion(prepared)
        self.assertEqual(len(pushes), 1)
        sleep.assert_not_called()
        self.assertFalse(self.github.marked)

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

    def test_obsolete_request_and_in_worktree_state_fail_before_effects(self):
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

    def test_amends_published_tip_preserving_parents_and_complete_contents(self):
        parents = self.git('rev-list', '--parents', '-n', '1', self.base).split()[1:]
        (self.repository / 'file.txt').write_bytes(b'staged\n')
        self.git('add', 'file.txt')
        (self.repository / 'file.txt').write_bytes(b'final\n')
        (self.repository / 'untracked.txt').write_bytes(b'new\n')
        prepared = self.prepare('amend-push')
        self.run_completion(prepared)
        head = self.git('rev-parse', 'HEAD')
        self.assertNotEqual(head, self.base)
        self.assertEqual(self.git('rev-list', '--parents', '-n', '1', head).split()[1:], parents)
        self.assertEqual(self.git('show', 'HEAD:file.txt'), 'final')
        self.assertEqual(self.git('show', 'HEAD:already.txt'), 'already')
        self.assertEqual(self.git('show', 'HEAD:untracked.txt'), 'new')
        self.assertEqual(self.remote_head(), head)
        self.run_completion(prepared)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)

    def test_amends_unpublished_tip_with_message_only_and_preserves_earlier_history(self):
        self.git('commit', '--allow-empty', '-m', 'First outgoing')
        earlier = self.git('rev-parse', 'HEAD')
        (self.repository / 'retained.txt').write_bytes(b'retained outgoing content\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Review-owned tip')
        old = self.git('rev-parse', 'HEAD')
        prepared = self.prepare('amend-push')
        self.run_completion(prepared)
        head = self.git('rev-parse', 'HEAD')
        self.assertNotEqual(head, old)
        self.assertEqual(self.git('rev-parse', 'HEAD^'), earlier)
        self.assertEqual(self.git('show', 'HEAD:retained.txt'), 'retained outgoing content')
        self.assertEqual(self.remote_head(), head)

    def test_amend_rejects_master_main_local_or_source_before_effects(self):
        for branch in ('master', 'main'):
            with self.subTest(branch=branch):
                self.git('checkout', '-b', branch)
                with self.assertRaisesRegex(ValueError, 'outside master/main'):
                    self.prepare('amend-push', branch=branch)
                self.git('checkout', 'feature')
                self.state = self.directory / ('state-source-' + branch)
                original = self.github.graphql
                def protected_source(commands, query, variables):
                    value = original(commands, query, variables)
                    value['repository']['pullRequest']['headRefName'] = branch
                    return value
                with patch.object(self.github, 'graphql', protected_source), \
                        patch.object(completion, 'remote_head', return_value=self.base), \
                        self.assertRaisesRegex(ValueError, 'outside master/main'):
                    self.prepare('amend-push')
                self.state = self.directory / ('state-next-' + branch)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.base)
        self.assertFalse(self.github.marked)

    def test_amends_an_existing_empty_tip_without_losing_its_parents(self):
        self.git('commit', '--allow-empty', '-m', 'Review-owned empty tip')
        old = self.git('rev-parse', 'HEAD')
        prepared = self.prepare('amend-push')
        self.run_completion(prepared)
        self.assertNotEqual(self.git('rev-parse', 'HEAD'), old)
        self.assertEqual(self.git('rev-parse', 'HEAD^'), self.base)
        self.assertEqual(self.git('rev-parse', 'HEAD^{tree}'), self.git('rev-parse', self.base + '^{tree}'))

    def test_lost_amend_response_reuses_exact_commit(self):
        (self.repository / 'file.txt').write_bytes(b'amended\n')
        prepared = self.prepare('amend-push')
        original = completion.Commands.git
        commits = []
        def lose_response(commands, *arguments, **options):
            value = original(commands, *arguments, **options)
            if arguments[0] == 'commit':
                commits.append(arguments)
                raise RuntimeError('lost amend response')
            return value
        with patch.object(completion.Commands, 'git', lose_response), self.assertRaises(RuntimeError):
            self.run_completion(prepared)
        head = self.git('rev-parse', 'HEAD')
        self.run_completion(prepared)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(len(commits), 1)
        self.assertIn('--amend', commits[0])

    def test_native_publication_uses_exact_lease_and_rejects_a_racing_ref(self):
        (self.repository / 'file.txt').write_bytes(b'amended\n')
        prepared = self.prepare('amend-push')
        original = completion.Commands.git
        pushes = []
        def race(commands, *arguments, **options):
            if arguments[0] == 'push':
                pushes.append(arguments)
                self.call_git('--git-dir', str(self.remote), 'update-ref', 'refs/heads/feature', self.comparison)
            return original(commands, *arguments, **options)
        with patch.object(completion.Commands, 'git', race), self.assertRaises(RuntimeError):
            self.run_completion(prepared)
        self.assertIn('--force-with-lease=refs/heads/feature:' + self.base, pushes[0])
        self.assertEqual(self.remote_head(), self.comparison)
        self.assertFalse(self.github.marked)

    def test_api_uploads_full_outgoing_history_without_native_network_calls(self):
        (self.repository / 'nested').mkdir()
        (self.repository / 'nested/中文.bin').write_bytes(b'\x00\xffbinary\n')
        self.git('add', '-A')
        self.git('update-index', '--chmod=+x', 'nested/中文.bin')
        self.git('commit', '-m', 'Existing outgoing')
        earlier = self.git('rev-parse', 'HEAD')
        (self.repository / 'file.txt').write_bytes(b'final\n')
        (self.repository / 'already.txt').unlink()
        original = completion.Commands.git
        def offline(commands, *arguments, **options):
            self.assertNotIn(arguments[0], ('push', 'fetch', 'ls-remote'))
            return original(commands, *arguments, **options)
        with patch.object(completion.Commands, 'git', offline):
            prepared = self.prepare('commit-push')
            self.run_completion(prepared, 'github-api')
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.remote_head(), head)
        self.assertEqual(self.call_git('--git-dir', str(self.remote), 'rev-parse', head + '^'), earlier)
        self.assertEqual(self.call_git('--git-dir', str(self.remote), 'ls-tree', '-r', head),
                         self.git('ls-tree', '-r', head))
        commits = [payload for kind, payload in self.github.uploads if kind == 'commits']
        self.assertEqual(len(commits), 2)
        self.assertEqual(self.github.updates[0]['repositoryId'], 'REPO_source')
        self.assertEqual(self.github.updates[0]['refUpdates'][0]['beforeOid'], self.base)
        self.assertFalse(self.github.updates[0]['refUpdates'][0]['force'])

    def test_api_amend_and_lost_cas_response_resume_without_repeated_update(self):
        (self.repository / 'file.txt').write_bytes(b'api amendment\n')
        prepared = self.prepare('amend-push')
        self.github.fail_after_update = True
        with self.assertRaises(RuntimeError):
            self.run_completion(prepared, 'github-api')
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.remote_head(), head)
        self.run_completion(prepared)  # Transport can change without changing frozen effects.
        self.assertEqual(len(self.github.updates), 1)
        self.assertTrue(self.github.updates[0]['refUpdates'][0]['force'])
        self.assertEqual(self.github.marked, ['file.txt'])

    def test_api_sha_mismatch_stops_before_ref_or_viewed_mutation(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        self.github.wrong_commit_sha = True
        with self.assertRaisesRegex(ValueError, 'cannot reproduce exact commit'):
            self.run_completion(prepared, 'github-api')
        self.assertEqual(self.remote_head(), self.base)
        self.assertFalse(self.github.updates)
        self.assertFalse(self.github.marked)

    def test_api_cas_rejects_a_racing_source_ref(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        self.github.before_update = lambda: self.call_git('--git-dir', str(self.remote), 'update-ref',
                                                        'refs/heads/feature', self.comparison)
        with self.assertRaises(AssertionError):
            self.run_completion(prepared, 'github-api')
        self.assertEqual(self.remote_head(), self.comparison)
        self.assertFalse(self.github.marked)

    def test_api_rejects_unreproducible_signed_commit_before_upload(self):
        self.git('commit', '--allow-empty', '-m', 'Signed outgoing')
        raw = subprocess.run(['git', '-C', str(self.repository), 'cat-file', 'commit', 'HEAD'],
                             capture_output=True, check=True).stdout
        headers, message = raw.split(b'\n\n', 1)
        raw = headers + b'\ngpgsig -----BEGIN PGP SIGNATURE-----\n fake\n -----END PGP SIGNATURE-----\n\n' + message
        result = subprocess.run(['git', '-C', str(self.repository), 'hash-object', '-t', 'commit', '-w', '--stdin'],
                                input=raw, capture_output=True, check=True)
        signed = result.stdout.decode().strip()
        self.git('update-ref', 'refs/heads/feature', signed)
        # This signed outgoing commit is retained by the full publication scope.
        prepared = self.prepare('commit-push')
        with self.assertRaisesRegex(ValueError, "header 'gpgsig'"):
            self.run_completion(prepared, 'github-api')
        self.assertFalse(self.github.uploads)
        self.assertFalse(self.github.updates)
        self.assertFalse(self.github.marked)

    @unittest.skipIf(os.name == 'nt', 'POSIX executable hook fixture')
    def test_api_old_git_requires_stdin_capability_only_for_active_hook(self):
        hook = self.repository / '.git/hooks/pre-push'
        hook.write_text('#!/bin/sh\nexit 0\n', encoding='utf-8')
        hook.chmod(0o755)
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        original = completion.Commands.git
        def old_git(commands, *arguments, **options):
            if arguments == ('--version',):
                return b'git version 2.39.2\n'
            return original(commands, *arguments, **options)
        with patch.object(completion.Commands, 'git', old_git):
            with self.assertRaisesRegex(ValueError, 'requires Git 2.43'):
                self.run_completion(prepared, 'github-api')
            self.assertFalse(self.github.uploads)
            self.assertFalse(self.github.updates)
            hook.unlink()
            self.run_completion(prepared, 'github-api')
        self.assertEqual(self.remote_head(), self.git('rev-parse', 'HEAD'))

    @unittest.skipIf(os.name == 'nt', 'POSIX executable hook fixture')
    def test_api_stdin_capable_hook_receives_native_arguments_and_can_block(self):
        hook = self.repository / '.git/hooks/pre-push'
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        original = completion.Commands.git
        invocations = []
        def modern_hook(commands, *arguments, **options):
            if arguments == ('--version',):
                return b'git version 2.43.0\n'
            if arguments[0] == 'hook':
                invocations.append(arguments)
                stdin = Path(arguments[3].split('=', 1)[1]).read_bytes()
                result = subprocess.run([str(hook)] + list(arguments[-2:]), input=stdin,
                                        cwd=str(self.repository), capture_output=True, timeout=20)
                if result.returncode:
                    raise RuntimeError('pre-push hook rejected publication')
                return result.stdout
            return original(commands, *arguments, **options)
        for body, error in (('exit 1', RuntimeError), ('echo drift > file.txt', ValueError),
                            ('git checkout -b hook-diverted', ValueError)):
            hook.write_text('#!/bin/sh\n' + body + '\n', encoding='utf-8')
            hook.chmod(0o755)
            with self.subTest(body=body), patch.object(completion.Commands, 'git', modern_hook), self.assertRaises(error):
                self.run_completion(prepared, 'github-api')
            self.assertEqual(self.remote_head(), self.base)
            self.assertFalse(self.github.marked)
            self.git('checkout', 'feature')
            self.git('checkout', '--', 'file.txt')
        hook.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "' + str(self.directory / 'hook-args') + '"\ncat > "' + str(self.directory / 'hook-stdin') + '"\n', encoding='utf-8')
        with patch.object(completion.Commands, 'git', modern_hook):
            self.run_completion(prepared, 'github-api')
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual((self.directory / 'hook-args').read_text().splitlines(), ['origin', str(self.remote)])
        self.assertEqual((self.directory / 'hook-stdin').read_text(), '%s %s refs/heads/feature %s\n' % (head, head, self.base))
        self.assertEqual(self.remote_head(), head)

    def test_api_preserves_merge_parents_timezone_and_symlink_objects(self):
        self.git('checkout', '-b', 'side')
        (self.repository / 'side.txt').write_bytes(b'side\n')
        self.git('add', '-A')
        self.git('commit', '-m', 'Side outgoing')
        side = self.git('rev-parse', 'HEAD')
        self.git('checkout', 'feature')
        (self.repository / 'feature.txt').write_bytes(b'feature\n')
        if os.name != 'nt':
            os.symlink('file.txt', str(self.repository / 'linked.txt'))
        self.git('add', '-A')
        self.git('commit', '-m', 'Main outgoing')
        first = self.git('rev-parse', 'HEAD')
        with patch.dict(os.environ, {'GIT_AUTHOR_DATE': '2026-10-30T12:34:56-05:30',
                                    'GIT_COMMITTER_DATE': '2026-10-30T12:34:57+08:00'}):
            self.git('merge', '--no-ff', 'side', '-m', 'Merge reviewed history')
        merged = self.git('rev-parse', 'HEAD')
        self.run_completion(self.prepare('commit-push'), 'github-api')
        self.assertEqual(self.remote_head(), merged)
        payload = next(payload for kind, payload in self.github.uploads
                       if kind == 'commits' and payload['message'] == 'Merge reviewed history\n')
        self.assertEqual(payload['parents'], [first, side])
        self.assertTrue(payload['author']['date'].endswith('-05:30'))
        self.assertTrue(payload['committer']['date'].endswith('+08:00'))
        if os.name != 'nt':
            self.assertTrue(any(entry['mode'] == '120000' for kind, payload in self.github.uploads
                                if kind == 'trees' for entry in payload['tree']))

    def test_blocked_native_git_resumes_same_local_commit_through_api(self):
        (self.repository / 'file.txt').write_bytes(b'new\n')
        prepared = self.prepare('commit-push')
        original = completion.Commands.git
        def blocked(commands, *arguments, **options):
            if arguments[0] in ('push', 'fetch', 'ls-remote'):
                raise RuntimeError('native Git endpoint unreachable')
            return original(commands, *arguments, **options)
        with patch.object(completion.Commands, 'git', blocked):
            with self.assertRaises(RuntimeError):
                self.run_completion(prepared)
            head = self.git('rev-parse', 'HEAD')
            self.run_completion(prepared, 'github-api')
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(self.remote_head(), head)
        self.assertEqual(len(self.github.updates), 1)

class CommandAndCliTests(CompletionFixture, unittest.TestCase):
    def test_source_ref_endpoint_escapes_url_syntax_and_gh_placeholders(self):
        commands = completion.Commands(self.repository, self.directory)
        url = 'https://github.com/owner/repo.git'
        for branch, endpoint in (
                ('fix/#123', 'fix/%23123'),
                ('fix/%review', 'fix/%25review'),
                ('fix/literal%2Fname', 'fix/literal%252Fname'),
                ('fix/中文', 'fix/%E4%B8%AD%E6%96%87'),
                ('fix/{owner}/{repo}/{branch}', 'fix/%7Bowner%7D/%7Brepo%7D/%7Bbranch%7D')):
            ref = 'refs/heads/' + branch
            subprocess.run(['git', 'check-ref-format', ref], capture_output=True, timeout=20, check=True)
            response = {'ref': ref, 'object': {'type': 'commit', 'sha': self.base}}
            with self.subTest(branch=branch), \
                    patch.object(completion, 'push_url', return_value=url), \
                    patch.object(commands, 'call', return_value=completion.encoded(response)) as call:
                observed = completion.remote_head(commands, {'remote': 'origin'},
                                                  {'source': 'owner/repo', 'ref': ref}, url)
                self.assertEqual(observed, self.base)
                call.assert_called_once_with(['gh', 'api', '--hostname', 'github.com', '--method', 'GET',
                                              'repos/owner/repo/git/ref/heads/' + endpoint], input_value=None)

    def test_source_ref_readback_refuses_a_different_literal_ref(self):
        commands = completion.Commands(self.repository, self.directory)
        url = 'https://github.com/owner/repo.git'
        ref = 'refs/heads/fix/literal%2Fname'
        response = {'ref': 'refs/heads/fix/literal/name',
                    'object': {'type': 'commit', 'sha': self.base}}
        with patch.object(completion, 'push_url', return_value=url), \
                patch.object(commands, 'call', return_value=completion.encoded(response)), \
                self.assertRaisesRegex(ValueError, 'Source branch is unavailable'):
            completion.remote_head(commands, {'remote': 'origin'}, {'source': 'owner/repo', 'ref': ref}, url)

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

    def test_command_timeout_stops_owned_child_before_lock_release(self):
        commands = completion.Commands(self.repository, self.directory)
        original_spawn = subprocess.Popen
        children = []
        def spawn(*arguments, **options):
            process = original_spawn(*arguments, **options)
            children.append(process)
            return process
        started = time.monotonic()
        with completion.operation_lock(self.directory):
            with patch.object(completion.subprocess, 'Popen', spawn), self.assertRaises(subprocess.TimeoutExpired):
                commands.call([sys.executable, '-c', 'import time; time.sleep(60)'], timeout=0.05)
            self.assertIsNotNone(children[0].poll())
        self.assertLess(time.monotonic() - started, 5)
        with completion.operation_lock(self.directory):
            pass
        log = completion.read_json(next(commands.logs.glob('*.command.json')))
        self.assertTrue(log['timed_out'])
        self.assertIsNotNone(log['exit_code'])

    def test_viewed_request_classifies_http_graphql_and_network_failures(self):
        commands = completion.Commands(self.repository, self.directory)
        prefix = commands.logs / 'failed'
        prefix.with_suffix('.stderr').write_bytes(b'')
        cases = [
            (200, {'errors': [{'type': 'RATE_LIMITED', 'message': 'API rate limit exceeded'}]},
             {'x-ratelimit-remaining': '0', 'x-ratelimit-reset': '110'}, 11),
            (200, {'errors': [{'message': 'You have exceeded a secondary rate limit'}]}, {}, 60),
            (403, {'message': 'You have exceeded a secondary rate limit'}, {'retry-after': '12'}, 12),
            (429, {'message': 'slow down'}, {'retry-after': '5'}, 5),
            (200, {'errors': [{'message': 'secondary rate limit'}]},
             {'retry-after': 'Thu, 01 Jan 1970 00:02:00 GMT'}, 20),
            (200, {'errors': [{'type': 'INTERNAL', 'message': 'server failed'}]}, {}, 0),
            (500, {'message': 'server failed'}, {}, 0),
            (502, None, {}, 0), (503, None, {}, 0), (504, None, {}, 0),
        ]
        for status, body, headers, delay in cases:
            raw = ('HTTP/2.0 %s Status\r\n' % status + ''.join(
                '%s: %s\r\n' % item for item in headers.items()) + '\r\n').encode()
            raw += completion.encoded(body) if body is not None else b'unavailable'
            prefix.with_suffix('.stdout').write_bytes(raw)
            failure = completion.CommandFailure(['gh'], 1, prefix)
            with self.subTest(status=status, body=body), patch.object(commands, 'call', side_effect=failure), \
                    patch.object(completion.time, 'time', return_value=100):
                with self.assertRaises(completion.ViewedRequestFailure) as caught:
                    commands.graphql(completion.MARK_QUERY, {})
                self.assertEqual(caught.exception.delay, delay)
        for stderr in (b'TLS handshake timeout', b'connection reset by peer', b'no such host', b'unexpected EOF', b'Post https://api.github.com/graphql: EOF'):
            prefix.with_suffix('.stdout').write_bytes(b'')
            prefix.with_suffix('.stderr').write_bytes(stderr)
            with self.subTest(stderr=stderr), patch.object(commands, 'call', side_effect=completion.CommandFailure(['gh'], 1, prefix)):
                with self.assertRaises(completion.ViewedRequestFailure):
                    commands.graphql(completion.PR_QUERY, {})
        with patch.object(commands, 'call', side_effect=subprocess.TimeoutExpired(['gh'], 30)):
            with self.assertRaises(completion.ViewedRequestFailure):
                commands.graphql(completion.MARK_QUERY, {})

    def test_permanent_graphql_failures_and_other_mutations_have_no_retry_disposition(self):
        commands = completion.Commands(self.repository, self.directory)
        prefix = commands.logs / 'failed'
        prefix.with_suffix('.stderr').write_bytes(b'permission denied; unexpected EOF')
        for status, body in (
                (401, {'message': 'Bad credentials'}), (403, {'message': 'Forbidden'}),
                (404, {'message': 'Not found'}), (422, {'message': 'Invalid request'}),
                (200, {'errors': [{'type': 'FORBIDDEN', 'message': 'Not accessible'}]}),
                (200, {'errors': [{'type': 'RATE_LIMITED'}, {'type': 'FORBIDDEN'}]})):
            prefix.with_suffix('.stdout').write_bytes(('HTTP/2.0 %s Status\n\n' % status).encode() + completion.encoded(body))
            failure = completion.CommandFailure(['gh'], 1, prefix)
            with self.subTest(status=status, body=body), patch.object(commands, 'call', side_effect=failure):
                with self.assertRaises(completion.CommandFailure):
                    commands.graphql(completion.MARK_QUERY, {})
        for status, body, stderr in (
                (401, b'', b'unexpected EOF'),
                (403, b'', b'connection reset by peer'),
                (200, b'{"data":', b'unexpected end of JSON input'),
                (200, b'{"unexpected": "body"}', b'unexpected EOF')):
            prefix.with_suffix('.stdout').write_bytes(('HTTP/2.0 %s Status\n\n' % status).encode() + body)
            prefix.with_suffix('.stderr').write_bytes(stderr)
            failure = completion.CommandFailure(['gh'], 1, prefix)
            with self.subTest(status=status, body=body), patch.object(commands, 'call', side_effect=failure):
                with self.assertRaises(completion.CommandFailure):
                    commands.graphql(completion.PR_QUERY, {})
        with patch.object(commands, 'call', return_value=b'HTTP/2.0 200 OK\n\nnot JSON'):
            with self.assertRaises(ValueError):
                commands.graphql(completion.PR_QUERY, {})
        with patch.object(commands, 'call', side_effect=subprocess.TimeoutExpired(['gh'], 30)):
            with self.assertRaises(subprocess.TimeoutExpired):
                commands.graphql(completion.UPDATE_QUERY, {})

    def test_viewed_deadline_limits_requests_and_does_not_shorten_rate_waits(self):
        with patch.object(completion.time, 'monotonic', return_value=100):
            self.assertEqual(completion.viewed_timeout(280), 30)
            self.assertEqual(completion.viewed_timeout(112), 12)
            with self.assertRaisesRegex(ValueError, 'deadline'):
                completion.viewed_timeout(100)
            with patch.object(completion.time, 'sleep') as sleep:
                completion.pause_viewed(completion.ViewedRequestFailure(60), 0, 280)
                completion.pause_viewed(completion.ViewedRequestFailure(60), 1, 280)
                with self.assertRaisesRegex(RuntimeError, 'budget exhausted'):
                    completion.pause_viewed(completion.ViewedRequestFailure(180), 0, 280)
                self.assertEqual([call.args[0] for call in sleep.call_args_list], [60, 120])
        commands = completion.Commands(self.repository, self.directory)
        with patch.object(commands, 'call', return_value=b'HTTP/2.0 200 OK\n\n{"data": {}}') as call:
            commands.graphql(completion.PR_QUERY, {}, timeout=12)
        self.assertEqual(call.call_args.kwargs['timeout'], 12)
        self.assertIn('--include', call.call_args.args[0])

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

    def test_old_private_plan_is_rejected_even_with_matching_confirmation(self):
        self.state.mkdir(mode=0o700)
        plan = {'version': 1}
        completion.write_json(self.state / 'plan.json', plan)
        with self.assertRaisesRegex(ValueError, 'Unsupported private plan version'):
            completion.run(self.state, completion.digest(completion.encoded(plan)))

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

        def page(query, variables, **options):
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
            self.assertEqual(completion.main(['run', '--state', str(self.state), '--confirm', 'd' * 64, '--transport', 'github-api']), 0)
        run.assert_called_once_with(self.state.resolve(), 'd' * 64, 'github-api')
        value = json.loads(output.getvalue())
        self.assertEqual(value['status'], 'complete')
        self.assertEqual(value['viewed_count'], 1000)
        self.assertEqual(value['outgoing_commit_count'], 1000)
        self.assertEqual(value['changed_path_count'], 1)
        self.assertLess(len(output.getvalue()), 2000)


if __name__ == '__main__':
    unittest.main()
