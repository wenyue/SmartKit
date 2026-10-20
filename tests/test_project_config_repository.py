"""Exercise project configuration Git operations with local disposable remotes."""

import hashlib
import json
import re
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/maintain-project-config/scripts'))
from project_config import repository


class RepositoryValidationTests(unittest.TestCase):
    def test_validates_identifiers_and_persistent_storage(self):
        self.assertEqual(repository.validate_repository('alice/project-config'), 'alice/project-config')
        self.assertEqual(repository.validate_branch('config/main'), 'config/main')
        self.assertEqual(repository.validate_entry('my.app-2'), 'my.app-2')
        for value in ('alice/config.git', '-alice/config', 'a/b/c', None):
            with self.subTest(repository=value), self.assertRaises(ValueError):
                repository.validate_repository(value)
        for value in ('--help', 'main\n', 'a..b', '@{-1}', '', None):
            with self.subTest(branch=value), self.assertRaises(ValueError):
                repository.validate_branch(value)
        for value in ('..', '.', '../config', '-config', '', None):
            with self.subTest(entry=value), self.assertRaises(ValueError):
                repository.validate_entry(value)
        persistent = Path.home() / 'project-config-test-state'
        with mock.patch.dict(os.environ, {'SMARTKIT_PROJECT_CONFIG_HOME': str(persistent)}):
            self.assertEqual(repository.state_root(), persistent)
        if os.name != 'nt':
            with mock.patch.dict(os.environ, {'SMARTKIT_PROJECT_CONFIG_HOME': '', 'XDG_DATA_HOME': 'relative-cache'}):
                self.assertEqual(repository.state_root(), Path.home() / '.local' / 'share' / 'smartkit' / 'project-config')

    def test_https_repository_identity_preserves_legacy_storage_and_separates_hosts(self):
        schema = json.loads((ROOT / 'setup-assets/catalog/project-config.schema.json').read_text())
        pattern = schema['properties']['maintenance']['oneOf'][1]['properties']['repository']['pattern']
        for value, expected in (
            ('https://github.com/alice/config.git', 'alice/config'),
            ('https://enterprise.example/alice/config.git', 'https://enterprise.example/alice/config'),
            ('https://ENTERPRISE.example/alice/config', 'https://enterprise.example/alice/config'),
        ):
            with self.subTest(repository=value):
                self.assertEqual(repository.validate_repository(value), expected)
                self.assertEqual(repository.validate_repository(expected), expected)
                self.assertIsNotNone(re.fullmatch(pattern, value))
        legacy = hashlib.sha256(b'alice/config\0main').hexdigest()[:32]
        self.assertEqual(repository._checkout_path('alice/config', 'main').name, legacy)
        self.assertEqual(repository._checkout_path('https://github.com/alice/config.git', 'main').name, legacy)
        self.assertNotEqual(repository._checkout_path('https://enterprise.example/alice/config', 'main').name, legacy)
        for value in ('https://token@enterprise.example/alice/config',
                      'https://enterprise.example:443/alice/config',
                      'https://enterprise.example/alice/config?token=secret',
                      'https://enterprise.example/alice/config#fragment',
                      'https://enterprise.example/alice/config/extra',
                      'https://-enterprise.example/alice/config',
                      'https://enterprise..example/alice/config',
                      'https://enterprise.example/alice/../config',
                      'http://enterprise.example/alice/config',
                      'ssh://git@enterprise.example/alice/config',
                      'https://enterprise.example/alice/config.git.git', 'alice/config.git'):
            with self.subTest(repository=value):
                with self.assertRaises(ValueError):
                    repository.validate_repository(value)
                self.assertIsNone(re.fullmatch(pattern, value))


class RepositoryGitTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.remote = self.root / 'remote.git'
        self.author = self.root / 'author'
        self.config = self.root / 'gitconfig'
        self.environment = mock.patch.dict(os.environ, {
            'SMARTKIT_PROJECT_CONFIG_HOME': str(self.root / 'state'),
            'GIT_CONFIG_GLOBAL': str(self.config),
            'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_AUTHOR_NAME': 'Test User', 'GIT_AUTHOR_EMAIL': 'test@example.com',
            'GIT_COMMITTER_NAME': 'Test User', 'GIT_COMMITTER_EMAIL': 'test@example.com',
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.git(self.root, 'config', '--global', 'url.' + self.remote.as_uri() + '.insteadOf', 'https://github.com/alice/config.git')
        self.git(self.root, 'init', '--bare', '--initial-branch=main', str(self.remote))
        self.git(self.root, 'clone', str(self.remote), str(self.author))
        (self.author / 'selected.txt').write_text('initial\n')
        (self.author / 'unrelated.txt').write_text('initial\n')
        self.git(self.author, 'add', '.')
        self.git(self.author, 'commit', '-m', 'initial')
        self.git(self.author, 'push', 'origin', 'main')
        self.private = True
        self.exists = True
        self.created = False
        self.owner = 'alice'
        self.github_hosts = []
        original_run = subprocess.run

        def run(arguments, **kwargs):
            if arguments[0] != 'gh':
                return original_run(arguments, **kwargs)
            self.github_hosts.append(kwargs['env']['GH_HOST'])
            if list(arguments[:3]) == ['gh', 'api', 'user']:
                return subprocess.CompletedProcess(arguments, 0, json.dumps({'login': 'alice'}), '')
            if list(arguments[:2]) == ['gh', 'api']:
                if not self.exists:
                    return subprocess.CompletedProcess(arguments, 1, '', 'HTTP 404')
                return subprocess.CompletedProcess(arguments, 0, json.dumps({
                    'private': self.private, 'owner': {'login': self.owner, 'type': 'User'},
                    'full_name': self.owner + '/config',
                }), '')
            if list(arguments[:3]) == ['gh', 'repo', 'create']:
                self.exists = True
                self.created = True
                return subprocess.CompletedProcess(arguments, 0, '', '')
            if list(arguments[:3]) == ['gh', 'repo', 'clone']:
                url = 'https://' + kwargs['env']['GH_HOST'] + '/alice/config.git'
                return original_run(['git', 'clone', '--no-checkout', url, arguments[4]], **kwargs)
            raise AssertionError(arguments)

        patcher = mock.patch.object(subprocess, 'run', side_effect=run)
        patcher.start()
        self.addCleanup(patcher.stop)

    def git(self, path, *args):
        return subprocess.run(['git', '-C', str(path), *args], check=True, capture_output=True, text=True).stdout.strip()

    def connect(self):
        return repository.checkout('alice/config', 'main')

    def test_checkout_reuses_verified_private_personal_repository_and_refuses_drift(self):
        path = self.connect()
        self.assertEqual((path / 'selected.txt').read_text(), 'initial\n')
        self.assertEqual(self.connect(), path)
        self.assertEqual(repository.open_checkout('alice/config', 'main'), path)
        self.git(path, 'remote', 'set-url', 'origin', 'https://github.com/other/config.git')
        with self.assertRaises(ValueError):
            repository.open_checkout('alice/config', 'main')
        self.git(path, 'remote', 'set-url', 'origin', 'https://github.com/alice/config.git')
        self.git(path, 'checkout', '-b', 'other')
        with self.assertRaises(ValueError):
            repository.open_checkout('alice/config', 'main')

    def test_commit_scope_ignores_inherited_foreign_index_location(self):
        path = self.connect()
        foreign_index = self.author / '.git' / 'index'
        before = foreign_index.read_bytes()
        (path / 'selected.txt').write_text('selected change\n')
        with mock.patch.dict(os.environ, {'GIT_INDEX_FILE': str(foreign_index)}):
            repository.commit_scope(path, 'main', ['selected.txt'], 'selected change')
        self.assertEqual(foreign_index.read_bytes(), before)
        self.assertEqual(self.git(path, 'status', '--porcelain'), '')

    def test_commit_scope_preserves_unrelated_staged_and_unstaged_work(self):
        path = self.connect()
        (path / 'unrelated.txt').write_text('staged work\n')
        self.git(path, 'add', 'unrelated.txt')
        (path / 'unrelated.txt').write_text('unstaged work\n')
        (path / 'selected.txt').write_text('selected change\n')
        (path / 'new.txt').write_text('new selection\n')
        commit = repository.commit_scope(path, 'main', ['selected.txt', 'new.txt'], 'selected change')
        self.assertEqual(self.git(path, 'show', commit + ':selected.txt'), 'selected change')
        self.assertEqual(self.git(path, 'show', commit + ':unrelated.txt'), 'initial')
        self.assertEqual(self.git(path, 'show', ':unrelated.txt'), 'staged work')
        self.assertEqual((path / 'unrelated.txt').read_text(), 'unstaged work\n')
        self.assertEqual(self.git(path, 'diff', '--cached', '--name-only'), 'unrelated.txt')

    def test_commit_scope_rejects_ambiguous_index_unsafe_paths_and_hook_expansion(self):
        path = self.connect()
        (path / 'selected.txt').write_text('already staged\n')
        self.git(path, 'add', 'selected.txt')
        head = self.git(path, 'rev-parse', 'HEAD')
        with self.assertRaises(ValueError):
            repository.commit_scope(path, 'main', ['selected.txt'], 'ambiguous')
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), head)
        for candidate in ('../escape', '.git/config', ':(glob)*', 'selected.txt/../unrelated.txt'):
            with self.subTest(path=candidate), self.assertRaises(ValueError):
                repository.commit_scope(path, 'main', [candidate], 'unsafe')
        if os.name != 'nt':
            (path / 'link').symlink_to(self.root, target_is_directory=True)
            with self.assertRaises(ValueError):
                repository.commit_scope(path, 'main', ['link/escape'], 'unsafe')
        self.git(path, 'commit', '-m', 'user staged work')
        (path / 'selected.txt').write_text('intended\n')
        hook = path / '.git' / 'hooks' / 'pre-commit'
        hook.write_text('#!/bin/sh\nprintf hook > unrelated.txt\ngit add -- unrelated.txt\n')
        hook.chmod(0o755)
        with self.assertRaisesRegex(ValueError, 'scope'):
            repository.commit_scope(path, 'main', ['selected.txt'], 'hook expansion')
        self.assertEqual(self.git(path, 'show', 'HEAD:unrelated.txt'), 'hook')
        self.assertEqual((path / 'selected.txt').read_text(), 'intended\n')

    def test_empty_created_repository_accepts_first_scoped_commit_and_publish(self):
        empty = self.root / 'empty.git'
        self.git(self.root, 'init', '--bare', '--initial-branch=main', str(empty))
        self.git(self.root, 'config', '--global', '--unset-all', 'url.' + self.remote.as_uri() + '.insteadOf')
        self.git(self.root, 'config', '--global', 'url.' + empty.as_uri() + '.insteadOf', 'https://github.com/alice/config.git')
        self.exists = False
        with self.assertRaises(OSError):
            self.connect()
        self.assertFalse(self.created)
        path = repository.checkout('alice/config', 'main', create=True)
        self.assertTrue(self.created)
        self.assertEqual(repository.update(path, 'main'), {'commit': '', 'remoteCommit': '', 'updated': False, 'localChanges': False})
        (path / 'selected.txt').write_bytes(b'initial \xff bytes\n')
        (path / 'unrelated.txt').write_text('unrelated staged\n')
        self.git(path, 'add', 'unrelated.txt')
        index_before = (path / '.git' / 'index').read_bytes()
        self.assertEqual(repository.update(path, 'main'), {
            'commit': '', 'remoteCommit': '', 'updated': False, 'localChanges': True,
        })
        self.assertEqual((path / '.git' / 'index').read_bytes(), index_before)
        commit = repository.commit_scope(path, 'main', ['selected.txt'], 'initial configuration')
        self.assertEqual(self.git(path, 'ls-tree', '--name-only', commit), 'selected.txt')
        self.assertEqual(self.git(path, 'diff', '--cached', '--name-only'), 'unrelated.txt')
        self.assertTrue(repository.publish(path, 'main', commit)['published'])
        self.assertEqual(self.git(empty, 'rev-parse', 'main'), commit)

    def test_publish_refuses_selected_files_changed_after_commit(self):
        path = self.connect()
        (path / 'selected.txt').write_text('owned change\n')
        commit = repository.commit_scope(path, 'main', ['selected.txt'], 'owned change')
        (path / 'selected.txt').write_text('not committed\n')
        with self.assertRaisesRegex(ValueError, 'uncommitted'):
            repository.publish(path, 'main', commit)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), self.git(self.author, 'rev-parse', 'HEAD'))
        self.assertEqual((path / 'selected.txt').read_text(), 'not committed\n')

    def test_portable_scope_rejects_windows_reserved_and_aliased_paths(self):
        path = self.connect()
        for candidate in ('NUL', 'folder/CON.txt', 'bad?.txt', '.git./config', 'trailing. ', 'name*'):
            with self.subTest(path=candidate), self.assertRaises(ValueError):
                repository.commit_scope(path, 'main', [candidate], 'unsafe')

    def test_publish_refuses_unknown_outgoing_commits(self):
        path = self.connect()
        remote_before = self.git(self.remote, 'rev-parse', 'main')
        (path / 'selected.txt').write_text('unrelated local commit\n')
        self.git(path, 'commit', '-am', 'unrelated local commit')
        (path / 'selected.txt').write_text('owned change\n')
        commit = repository.commit_scope(path, 'main', ['selected.txt'], 'owned change')
        with self.assertRaisesRegex(ValueError, 'outgoing'):
            repository.publish(path, 'main', commit)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), remote_before)
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), commit)

    def test_publish_refuses_earlier_receipted_commits_outside_this_request(self):
        path = self.connect()
        remote_before = self.git(self.remote, 'rev-parse', 'main')
        alpha = 'projects/alpha/config.json'
        beta = 'projects/beta/config.json'
        (path / alpha).parent.mkdir(parents=True)
        (path / beta).parent.mkdir(parents=True)
        (path / alpha).write_text('{"entry": "alpha"}\n')
        first = repository.commit_scope(path, 'main', [alpha], 'earlier alpha request')
        self.assertEqual(repository.update(path, 'main')['commit'], first)
        (path / beta).write_text('{"entry": "beta"}\n')
        second = repository.commit_scope(path, 'main', [beta], 'current beta request')
        with self.assertRaises(ValueError) as refused:
            repository.publish(path, 'main', second)
        self.assertIn(first, str(refused.exception))
        self.assertIn(alpha, str(refused.exception))
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), remote_before)
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), second)
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD^'), first)
        self.assertEqual(self.git(path, 'status', '--porcelain'), '')

        (path / beta).write_text('{"entry": "beta", "changed": true}\n')
        third = repository.commit_scope(path, 'main', [beta], 'later beta request')
        with self.assertRaises(ValueError) as refused:
            repository.publish(path, 'main', third)
        self.assertIn(first, str(refused.exception))
        self.assertIn(second, str(refused.exception))
        self.assertIn(alpha, str(refused.exception))
        self.assertIn(beta, str(refused.exception))
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), remote_before)
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD^'), second)
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD^^'), first)

    def test_publish_verifies_remote_and_retries_preserved_scope_commit(self):
        path = self.connect()
        (path / 'selected.txt').write_text('owned change\n')
        commit = repository.commit_scope(path, 'main', ['selected.txt'], 'owned change')
        hook = self.remote / 'hooks' / 'pre-receive'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        with self.assertRaises(OSError):
            repository.publish(path, 'main', commit)
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), commit)
        hook.unlink()
        result = repository.publish(path, 'main', commit)
        self.assertTrue(result['published'])
        self.assertEqual(result['remoteCommit'], commit)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), commit)
        self.assertTrue(repository.publish(path, 'main', commit)['published'])

    def test_publish_preserves_commit_when_remote_advances_during_push(self):
        path = self.connect()
        (path / 'selected.txt').write_text('owned change\n')
        commit = repository.commit_scope(path, 'main', ['selected.txt'], 'owned change')
        (self.author / 'unrelated.txt').write_text('concurrent update\n')
        self.git(self.author, 'commit', '-am', 'concurrent update')
        concurrent = self.git(self.author, 'rev-parse', 'HEAD')
        hook = path / '.git' / 'hooks' / 'pre-push'
        hook.write_text('#!/bin/sh\nunset GIT_DIR GIT_WORK_TREE\ngit -C "' + self.author.as_posix() + '" push origin main\n')
        hook.chmod(0o755)
        with self.assertRaises(OSError):
            repository.publish(path, 'main', commit)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), concurrent)
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), commit)
        self.assertEqual((path / 'selected.txt').read_text(), 'owned change\n')

    def test_update_fast_forwards_and_preserves_dirty_or_diverged_work(self):
        path = self.connect()
        (self.author / 'selected.txt').write_text('remote update\n')
        self.git(self.author, 'commit', '-am', 'remote update')
        self.git(self.author, 'push', 'origin', 'main')
        result = repository.update(path, 'main')
        self.assertTrue(result['updated'])
        self.assertEqual((path / 'selected.txt').read_text(), 'remote update\n')
        (path / 'unrelated.txt').write_text('local work\n')
        before = self.git(path, 'status', '--porcelain')
        current = repository.update(path, 'main')
        self.assertTrue(current['localChanges'])
        self.assertFalse(current['updated'])
        self.assertEqual(self.git(path, 'status', '--porcelain'), before)
        self.assertEqual((path / 'unrelated.txt').read_text(), 'local work\n')
        self.git(path, 'commit', '-am', 'local change')
        local = self.git(path, 'rev-parse', 'HEAD')
        (self.author / 'selected.txt').write_text('remote divergence\n')
        self.git(self.author, 'commit', '-am', 'remote divergence')
        self.git(self.author, 'push', 'origin', 'main')
        with self.assertRaises(ValueError):
            repository.update(path, 'main')
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), local)
        self.assertEqual((path / 'unrelated.txt').read_text(), 'local work\n')

    def test_update_preserves_dirty_index_and_files_when_remote_needs_no_advance(self):
        path = self.connect()
        remote = self.git(self.remote, 'rev-parse', 'main')
        (path / 'selected.txt').write_bytes(b'staged \xff bytes\n')
        self.git(path, 'add', 'selected.txt')
        (path / 'selected.txt').write_bytes(b'unstaged \xfe bytes\n')
        (path / 'untracked.txt').write_bytes(b'untracked \x00 bytes\n')
        os.utime(path / 'unrelated.txt', (1, 1))
        index_before = (path / '.git' / 'index').read_bytes()
        files_before = {name: ((path / name).read_bytes(), (path / name).stat().st_mode, (path / name).stat().st_mtime_ns)
                        for name in ('selected.txt', 'unrelated.txt', 'untracked.txt')}
        result = repository.update(path, 'main')
        self.assertEqual(result, {'commit': remote, 'remoteCommit': remote, 'updated': False, 'localChanges': True})
        self.assertEqual((path / '.git' / 'index').read_bytes(), index_before)
        self.assertEqual({name: ((path / name).read_bytes(), (path / name).stat().st_mode, (path / name).stat().st_mtime_ns)
                          for name in files_before}, files_before)

        self.git(path, 'commit', '-am', 'local pending commit')
        head = self.git(path, 'rev-parse', 'HEAD')
        index_before = (path / '.git' / 'index').read_bytes()
        result = repository.update(path, 'main')
        self.assertEqual(result, {'commit': head, 'remoteCommit': remote, 'updated': False, 'localChanges': True})
        self.assertEqual((path / '.git' / 'index').read_bytes(), index_before)
        self.assertEqual({name: ((path / name).read_bytes(), (path / name).stat().st_mode, (path / name).stat().st_mtime_ns)
                          for name in files_before}, files_before)

    def test_update_fetches_but_refuses_dirty_work_when_remote_advanced(self):
        path = self.connect()
        head = self.git(path, 'rev-parse', 'HEAD')
        (path / 'selected.txt').write_bytes(b'staged \xff bytes\n')
        self.git(path, 'add', 'selected.txt')
        (path / 'selected.txt').write_bytes(b'unstaged \xfe bytes\n')
        (path / 'untracked.txt').write_bytes(b'untracked \x00 bytes\n')
        os.utime(path / 'unrelated.txt', (1, 1))
        index_before = (path / '.git' / 'index').read_bytes()
        files_before = {name: ((path / name).read_bytes(), (path / name).stat().st_mode, (path / name).stat().st_mtime_ns)
                        for name in ('selected.txt', 'unrelated.txt', 'untracked.txt')}
        (self.author / 'selected.txt').write_text('remote update\n')
        self.git(self.author, 'commit', '-am', 'remote update')
        self.git(self.author, 'push', 'origin', 'main')
        remote = self.git(self.remote, 'rev-parse', 'main')
        with self.assertRaisesRegex(ValueError, 'local changes'):
            repository.update(path, 'main')
        self.assertEqual(self.git(path, 'rev-parse', 'FETCH_HEAD'), remote)
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), head)
        self.assertEqual((path / '.git' / 'index').read_bytes(), index_before)
        self.assertEqual({name: ((path / name).read_bytes(), (path / name).stat().st_mode, (path / name).stat().st_mtime_ns)
                          for name in files_before}, files_before)

        self.git(path, 'commit', '-am', 'local diverged commit')
        head = self.git(path, 'rev-parse', 'HEAD')
        index_before = (path / '.git' / 'index').read_bytes()
        with self.assertRaisesRegex(ValueError, 'local changes'):
            repository.update(path, 'main')
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), head)
        self.assertEqual((path / '.git' / 'index').read_bytes(), index_before)
        self.assertEqual({name: ((path / name).read_bytes(), (path / name).stat().st_mode, (path / name).stat().st_mtime_ns)
                          for name in files_before}, files_before)

    def test_checkout_rejects_missing_branch_without_using_default_branch(self):
        with self.assertRaisesRegex(ValueError, 'branch'):
            repository.checkout('alice/config', 'missing')
        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), self.git(self.author, 'rev-parse', 'HEAD'))

    def test_checkout_pins_github_host_even_when_gh_defaults_to_enterprise(self):
        original_run = subprocess.run

        def check_host(arguments, **kwargs):
            if arguments[0] == 'gh':
                self.assertEqual(kwargs['env']['GH_HOST'], 'github.com')
            return original_run(arguments, **kwargs)

        with mock.patch.dict(os.environ, {'GH_HOST': 'enterprise.example'}):
            with mock.patch.object(subprocess, 'run', side_effect=check_host):
                self.connect()

    def test_enterprise_checkout_update_publish_and_host_drift_guards(self):
        host = 'enterprise.example'
        url = 'https://' + host + '/alice/config.git'
        self.git(self.root, 'config', '--global', '--add', 'url.' + self.remote.as_uri() + '.insteadOf', url)
        public = self.connect()
        original_run = subprocess.run

        def selected_host(arguments, **kwargs):
            if arguments[0] == 'gh':
                self.assertEqual(kwargs['env']['GH_HOST'], host)
            if arguments[0] == 'git' and any(value in arguments for value in ('fetch', 'push', 'ls-remote')):
                self.assertIn('credential.https://' + host + '.helper=!gh auth git-credential', arguments)
            return original_run(arguments, **kwargs)

        with mock.patch.dict(os.environ, {'GH_HOST': 'github.com'}), \
                mock.patch.object(subprocess, 'run', side_effect=selected_host):
            path = repository.checkout(url, 'main')
            self.assertNotEqual(path, public)
            self.assertEqual(repository.checkout(url, 'main'), path)
            (path / 'selected.txt').write_text('enterprise change\n')
            commit = repository.commit_scope(path, 'main', ['selected.txt'], 'enterprise change')
            self.assertTrue(repository.publish(path, 'main', commit)['published'])
            self.assertEqual(repository.update(path, 'main')['commit'], commit)

        self.assertEqual(self.git(self.remote, 'rev-parse', 'main'), commit)
        for origin in (url, 'git@' + host + ':alice/config.git', 'ssh://git@' + host + '/alice/config'):
            self.git(path, 'remote', 'set-url', 'origin', origin)
            with mock.patch.object(repository, '_personal_repository', side_effect=AssertionError('must remain offline')):
                self.assertEqual(repository.open_checkout(url, 'main'), path)
        self.git(path, 'remote', 'set-url', 'origin', 'https://github.com/alice/config.git')
        with mock.patch.object(repository, '_fetch', side_effect=AssertionError('must refuse before fetching')):
            with self.assertRaisesRegex(ValueError, 'origin changed'):
                repository.update(path, 'main')
        self.assertEqual(repository.open_checkout('alice/config', 'main'), public)

    def test_enterprise_creation_and_private_owner_checks_use_selected_host(self):
        url = 'https://enterprise.example/alice/config.git'
        self.git(self.root, 'config', '--global', '--add', 'url.' + self.remote.as_uri() + '.insteadOf', url)
        self.exists = False
        with self.assertRaises(OSError):
            repository.checkout(url, 'main')
        self.assertFalse(self.created)
        repository.checkout(url, 'main', create=True)
        self.assertTrue(self.created)
        self.private = False
        with self.assertRaises(ValueError):
            repository.checkout(url, 'main')
        self.private = True
        self.owner = 'other'
        with self.assertRaises(ValueError):
            repository.checkout(url, 'main')
        self.assertEqual(set(self.github_hosts), {'enterprise.example'})

    def test_open_checkout_needs_no_github_access(self):
        path = self.connect()
        original_run = subprocess.run

        def offline(arguments, **kwargs):
            if arguments[0] == 'gh':
                raise AssertionError('read-only checkout must not contact GitHub')
            return original_run(arguments, **kwargs)

        with mock.patch.object(subprocess, 'run', side_effect=offline):
            self.assertEqual(repository.open_checkout('alice/config', 'main'), path)

    def test_publish_does_not_trust_success_without_remote_reachability(self):
        path = self.connect()
        (path / 'selected.txt').write_text('owned change\n')
        commit = repository.commit_scope(path, 'main', ['selected.txt'], 'owned change')
        original_run = subprocess.run

        def false_success(arguments, **kwargs):
            if arguments[0] == 'git' and 'push' in arguments:
                return subprocess.CompletedProcess(arguments, 0, 'claimed success', '')
            return original_run(arguments, **kwargs)

        with mock.patch.object(subprocess, 'run', side_effect=false_success):
            with self.assertRaisesRegex(ValueError, 'not verified'):
                repository.publish(path, 'main', commit)
        self.assertNotEqual(self.git(self.remote, 'rev-parse', 'main'), commit)

    def test_checkout_rejects_public_or_other_owned_repository(self):
        self.private = False
        with self.assertRaises(ValueError):
            self.connect()
        self.private = True
        self.owner = 'other'
        with self.assertRaises(ValueError):
            self.connect()


if __name__ == '__main__':
    unittest.main()
