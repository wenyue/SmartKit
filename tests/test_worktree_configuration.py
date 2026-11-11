from __future__ import annotations

import importlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'skills/maintain-project-config/scripts'))


class WorktreeConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.target = self.root / 'external-target'
        self.git(self.source, 'init')
        self.write(self.source, 'app.py', 'print("app")\n')
        self.git(self.source, 'add', 'app.py')
        self.git(self.source, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'core.hooksPath=' + str(self.root / 'no-hooks'), 'commit', '-m', 'Initial')
        self.git(self.source, 'worktree', 'add', '-b', 'task', str(self.target))
        self.write(self.source, '.agents/config.json', json.dumps({'maintenance': {'mode': 'local-only'}}))
        self.write(self.source, 'AGENTS.md', '# Project\n')
        self.write(self.source, '.agents/skills/example/SKILL.md', '# Example\n')
        self.write(self.source, '.agents/skills/example/scripts/run.sh', '#!/bin/sh\nexit 0\n')
        if os.name == 'posix':
            (self.source / '.agents/skills/example/scripts/run.sh').chmod(0o755)
        self.maintain = importlib.import_module('maintain')
        self.copy = importlib.import_module('project_config.worktree_configuration')
        self.cli = importlib.import_module('project_config.project_configuration_cli')
        self.scope = ['.agents/config.json', 'AGENTS.md', '.agents/skills']

    @staticmethod
    def write(root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    @staticmethod
    def git(root, *arguments):
        environment = os.environ.copy()
        for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR', 'GIT_PREFIX',
                    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
            environment.pop(key, None)
        return subprocess.run(['git', '-C', str(root), *arguments], env=environment,
                              capture_output=True, text=True, check=True)

    def command(self, *arguments, source=None, target=None, scope=None):
        output, errors = StringIO(), StringIO()
        paths = self.scope if scope is None else scope
        command = ['copy-worktree', '--source', str(source or self.source), '--target', str(target or self.target)]
        for path in paths:
            command.extend(['--file', path])
        with redirect_stdout(output), redirect_stderr(errors):
            code = self.maintain.main([*command, *arguments])
        return code, json.loads(output.getvalue()) if output.getvalue() else {}, errors.getvalue()

    def snapshot(self, root):
        return {path.relative_to(root).as_posix(): (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
                for path in root.rglob('*') if path.is_file() and '.git' not in path.relative_to(root).parts}

    def test_check_then_copy_ignored_configuration_preserves_source_and_indexes(self):
        source_before = self.snapshot(self.source)
        source_index = (self.source / '.git/index').read_bytes()
        target_index = Path(self.git(self.target, 'rev-parse', '--git-path', 'index').stdout.strip())
        target_index = target_index if target_index.is_absolute() else self.target / target_index
        target_index_before = target_index.read_bytes()
        target_before = self.snapshot(self.target)
        exclude_before = (self.source / '.git/info/exclude').read_bytes()
        code, report, error = self.command('--check')
        self.assertEqual(code, 1, error)
        self.assertEqual(report['check'], 'drift')
        self.assertEqual(report['conflicting_paths'], [])
        self.assertIn('.agents/skills/example/SKILL.md', report['missing_paths'])
        self.assertEqual(self.snapshot(self.target), target_before)
        self.assertEqual((self.source / '.git/info/exclude').read_bytes(), exclude_before)
        code, report, error = self.command()
        self.assertEqual(code, 0, error)
        self.assertEqual(report['check'], 'clean')
        self.assertEqual(self.snapshot(self.source), source_before)
        self.assertEqual((self.source / '.git/index').read_bytes(), source_index)
        self.assertEqual(target_index.read_bytes(), target_index_before)
        self.assertFalse((self.target / '.agents/project-config-sync.json').exists())
        self.git(self.target, 'check-ignore', '--quiet', '.agents/skills/example/SKILL.md')
        if os.name == 'posix':
            self.assertEqual(stat.S_IMODE((self.target / '.agents/skills/example/scripts/run.sh').stat().st_mode), 0o755)
        code, report, error = self.command()
        self.assertEqual(code, 0, error)
        self.assertEqual(report['copied_paths'], [])
        self.assertEqual(self.command('--check')[0], 0)

    def test_project_shared_mode_and_target_only_files_are_preserved(self):
        self.write(self.source, '.agents/config.json', '{"maintenance":{"mode":"local"}}')
        self.write(self.target, '.agents/skills/target/SKILL.md', '# Target-owned\n')
        self.write(self.source, 'openwiki/page.md', '# Not selected\n')
        self.write(self.source, '.agents/project-config-sync.json', '{"automatic":true}')
        code, report, error = self.command()
        self.assertEqual(code, 0, error)
        self.assertEqual(report['mode'], 'local')
        self.assertEqual((self.target / '.agents/skills/target/SKILL.md').read_text(), '# Target-owned\n')
        self.assertFalse((self.target / 'openwiki').exists())
        self.assertFalse((self.target / '.agents/project-config-sync.json').exists())
        self.assertIn('AGENTS.md', self.git(self.target, 'ls-files', '--others', '--exclude-standard').stdout)

    def test_conflict_refuses_entire_copy_before_writes(self):
        self.write(self.target, 'AGENTS.md', '# Accepted target\n')
        before = self.snapshot(self.target)
        code, report, error = self.command('--check')
        self.assertEqual(code, 1, error)
        self.assertEqual(report['conflicting_paths'], ['AGENTS.md'])
        code, _, error = self.command()
        self.assertEqual(code, 2)
        self.assertIn('would replace', error)
        self.assertEqual(self.snapshot(self.target), before)

    def test_source_and_target_modes_are_never_switched(self):
        self.write(self.target, '.agents/config.json', '{"maintenance":{"mode":"local"}}')
        before = self.snapshot(self.target)
        code, _, error = self.command()
        self.assertEqual(code, 2)
        self.assertIn('mode differs', error)
        self.assertEqual(self.snapshot(self.target), before)
        self.write(self.source, '.agents/config.json', json.dumps({'maintenance': {
            'mode': 'repository', 'repository': 'user/config', 'branch': 'main', 'entry': 'app'}}))
        code, _, error = self.command()
        self.assertEqual(code, 2)
        self.assertIn('repository mode uses restoration', error)
        self.assertEqual(self.snapshot(self.target), before)

    def test_existing_target_config_may_be_retained_with_a_narrow_scope(self):
        self.write(self.target, '.agents/config.json', '{"maintenance":{"mode":"local-only"},"ruleEntry":"AGENTS.local.md"}')
        before = (self.target / '.agents/config.json').read_bytes()
        code, _, error = self.command(scope=['.agents/skills'])
        self.assertEqual(code, 0, error)
        self.assertEqual((self.target / '.agents/config.json').read_bytes(), before)

    def test_missing_binding_and_missing_explicit_scope_refuse(self):
        before = self.snapshot(self.target)
        code, _, error = self.command(scope=['.agents/skills'])
        self.assertEqual(code, 2)
        self.assertIn('select .agents/config.json', error)
        self.assertEqual(self.snapshot(self.target), before)
        code, _, _ = self.command(scope=[])
        self.assertEqual(code, 2)
        self.assertEqual(self.snapshot(self.target), before)

    def test_primary_unrelated_and_noncorresponding_targets_refuse(self):
        self.write(self.target, '.agents/config.json', '{"maintenance":{"mode":"local-only"}}')
        code, _, error = self.command(source=self.target, target=self.source, scope=['.agents/config.json'])
        self.assertEqual(code, 2)
        self.assertIn('linked target', error)
        unrelated = self.root / 'unrelated'
        unrelated.mkdir()
        self.git(unrelated, 'init')
        code, _, error = self.command(target=unrelated)
        self.assertEqual(code, 2)
        self.assertIn('same repository', error)
        nested = self.target / 'services/app'
        nested.mkdir(parents=True)
        code, _, error = self.command(target=nested)
        self.assertEqual(code, 2)
        self.assertIn('corresponding project', error)

    def test_corresponding_nested_projects_in_external_worktree(self):
        source = self.source / 'services/app'
        target = self.target / 'services/app'
        target.mkdir(parents=True)
        self.write(source, '.agents/config.json', '{"maintenance":{"mode":"local-only"}}')
        self.write(source, 'AGENTS.local.md', '# Nested\n')
        code, report, error = self.command(source=source, target=target, scope=['.agents/config.json', 'AGENTS.local.md'])
        self.assertEqual(code, 0, error)
        self.assertEqual(report['target'], str(target))
        self.assertEqual((target / 'AGENTS.local.md').read_text(), '# Nested\n')
        self.git(self.target, 'check-ignore', '--quiet', 'services/app/AGENTS.local.md')

    def test_receipt_and_parent_file_are_rejected_before_copy(self):
        self.write(self.source, '.agents/project-config-sync.json', '{}')
        before = self.snapshot(self.target)
        for path in ('.agents/project-config-sync.json', '.agents'):
            code, _, error = self.command(scope=[path])
            self.assertEqual(code, 2)
            self.assertTrue('synchronization' in error or 'project-config-sync.json' in error, error)
            self.assertEqual(self.snapshot(self.target), before)
        self.write(self.target, '.agents/skills', 'not a directory')
        before = self.snapshot(self.target)
        code, _, error = self.command()
        self.assertEqual(code, 2)
        self.assertIn('not a directory', error.lower())
        self.assertEqual(self.snapshot(self.target), before)

    @unittest.skipUnless(os.name == 'posix', 'POSIX symlinks and permission bits')
    def test_symlink_and_permission_conflicts_refuse_before_copy(self):
        (self.source / 'link.md').symlink_to(self.source / 'AGENTS.md')
        code, _, error = self.command(scope=['.agents/config.json', 'link.md'])
        self.assertEqual(code, 2)
        self.assertIn('symlink', error)
        self.assertFalse((self.target / '.agents').exists())
        self.write(self.target, 'AGENTS.md', '# Project\n')
        (self.target / 'AGENTS.md').chmod(0o600)
        code, _, error = self.command()
        self.assertEqual(code, 2)
        self.assertIn('permissions', error)
        self.assertFalse((self.target / '.agents').exists())

    def test_later_copy_failure_retains_completed_files_and_retry_copies_missing_only(self):
        original = Path.open

        def fail_once(path, *args, **kwargs):
            if path == self.target / 'AGENTS.md' and args == ('xb',):
                raise OSError('injected write failure')
            return original(path, *args, **kwargs)

        with mock.patch.object(Path, 'open', fail_once):
            code, _, error = self.command()
        self.assertEqual(code, 2)
        self.assertIn('injected write failure', error)
        self.assertIn('last attempted path', error)
        self.assertTrue((self.target / '.agents/config.json').exists())
        self.assertFalse((self.target / 'AGENTS.md').exists())
        code, report, error = self.command()
        self.assertEqual(code, 0, error)
        self.assertEqual(report['copied_paths'], ['AGENTS.md'])

    def test_exclusion_failure_keeps_copy_and_reports_incomplete_phase(self):
        with mock.patch.object(self.cli, 'sync_git_exclusions', side_effect=OSError('exclude unavailable')):
            code, _, error = self.command()
        self.assertEqual(code, 2)
        self.assertIn('Git exclusions remain incomplete', error)
        self.assertTrue((self.target / 'AGENTS.md').exists())
        code, report, error = self.command()
        self.assertEqual(code, 0, error)
        self.assertEqual(report['copied_paths'], [])

    def test_partial_current_file_is_preserved_and_retry_refuses_to_overwrite_it(self):
        original = Path.open

        class FailingWrite:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.stream.close()

            def write(self, content):
                self.stream.write(content[:1])
                self.stream.flush()
                raise OSError('injected partial write')

        def fail_during_write(path, *args, **kwargs):
            stream = original(path, *args, **kwargs)
            return FailingWrite(stream) if path == self.target / 'AGENTS.md' and args == ('xb',) else stream

        with mock.patch.object(Path, 'open', fail_during_write):
            code, _, error = self.command()
        self.assertEqual(code, 2)
        self.assertIn('injected partial write', error)
        self.assertIn('last attempted path', error)
        self.assertEqual((self.target / 'AGENTS.md').read_bytes(), b'#')
        before = self.snapshot(self.target)
        code, _, error = self.command()
        self.assertEqual(code, 2)
        self.assertIn('would replace', error)
        self.assertEqual(self.snapshot(self.target), before)


if __name__ == '__main__':
    unittest.main()
