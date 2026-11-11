"""Exercise worktree-owned configuration preparation against real Git checkouts."""
from __future__ import annotations

import errno
import importlib.util
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
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'skills/create-worktree/scripts/prepare_configuration.py'
SPEC = importlib.util.spec_from_file_location('worktree_configuration', ENTRY)
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


class WorktreeConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='worktree configuration ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.target = self.root / 'target'
        self.git(self.source, 'init')
        self.write(self.source, 'app.py', 'print("app")\n')
        self.git(self.source, 'add', 'app.py')
        self.git(self.source, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                 '-c', 'core.hooksPath=' + str(self.root / 'no-hooks'), 'commit', '-m', 'Initial')
        self.git(self.source, 'worktree', 'add', '-b', 'task', str(self.target))
        self.write(self.source, '.agents/config.json', json.dumps({'maintenance': {'mode': 'local-only'}}))
        self.write(self.source, '.agents/rules/project.md', '# Rule\n')
        self.write(self.source, '.agents/skills/example/SKILL.md', '# Example\n')
        self.write(self.source, '.agents/skills/example/scripts/run.sh', '#!/bin/sh\nexit 0\n')
        if os.name == 'posix':
            (self.source / '.agents/skills/example/scripts/run.sh').chmod(0o755)
        self.scope = ['.agents/config.json', '.agents/rules', '.agents/skills']

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
                              capture_output=True, text=True, check=True).stdout

    def arguments(self, *extra, source=None, target=None, scope=None):
        result = ['prepare', '--source', str(source or self.source), '--target', str(target or self.target)]
        for path in self.scope if scope is None else scope:
            result.extend(['--path', path])
        return result + list(extra)

    def command(self, *extra, **kwargs):
        output, errors = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = PREPARE.main(self.arguments(*extra, **kwargs))
        return code, json.loads(output.getvalue()) if output.getvalue() else {}, errors.getvalue()

    def fallback(self):
        return mock.patch.object(Path, 'symlink_to', side_effect=PermissionError(errno.EPERM, 'links unavailable'))

    def record(self):
        return Path(self.git(self.target, 'rev-parse', '--absolute-git-dir').strip()) / PREPARE.RECORD

    def reparse_point(self, redirected):
        original = Path.lstat
        def lstat(path):
            if path == redirected:
                return SimpleNamespace(st_mode=path.stat().st_mode, st_file_attributes=0x400)
            return original(path)
        return mock.patch.object(Path, 'lstat', lstat)

    def snapshot(self):
        return {str(path.relative_to(self.source)): path.read_bytes()
                for path in self.source.rglob('*') if path.is_file() and '.git' not in path.relative_to(self.source).parts}

    def test_actual_cli_links_and_preserves_source_and_indexes(self):
        before = self.snapshot()
        indexes = [self.git(root, 'ls-files', '--stage', '-z') for root in (self.source, self.target)]
        result = subprocess.run([sys.executable, '-B', str(ENTRY), *self.arguments()],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(json.loads(result.stdout)['paths'].values()), {'link'})
        for relative in self.scope:
            self.assertTrue((self.target / relative).is_symlink())
            self.assertEqual((self.target / relative).resolve(), (self.source / relative).resolve())
            self.assertTrue(self.git(self.target, 'check-ignore', '--', relative).strip())
        self.assertEqual(self.snapshot(), before)
        self.assertEqual([self.git(root, 'ls-files', '--stage', '-z') for root in (self.source, self.target)], indexes)

    def test_linked_edit_uses_resolved_file_and_preserves_link(self):
        self.assertEqual(self.command()[0], 0)
        logical = self.target / '.agents/config.json'
        resolved = logical.resolve()
        replacement = resolved.with_name('replacement.json')
        replacement.write_text('{"maintenance": {"mode": "local-only"}, "edited": true}')
        replacement.replace(resolved)
        self.assertTrue(logical.is_symlink())
        self.assertEqual(logical.read_bytes(), (self.source / '.agents/config.json').read_bytes())
        self.assertTrue(json.loads(logical.read_text())['edited'])

    def test_repository_mode_uses_only_local_source(self):
        self.write(self.source, '.agents/config.json', json.dumps({'maintenance': {'mode': 'repository',
                   'repository': 'unreachable/private', 'branch': 'config', 'entry': 'example'}}))
        code, report, errors = self.command()
        self.assertEqual(code, 0, errors)
        self.assertEqual(report['mode'], 'repository')
        self.assertTrue((self.target / '.agents/config.json').is_symlink())

    def test_git_shared_mode_transfers_nothing(self):
        self.write(self.source, '.agents/config.json', '{"maintenance":{"mode":"local"}}')
        for relative in self.scope:
            original, destination = self.source / relative, self.target / relative
            if original.is_file():
                self.write(self.target, relative, original.read_text())
            else:
                destination.mkdir(parents=True)
        before = list(self.target.rglob('*'))
        code, report, errors = self.command()
        self.assertEqual(code, 0, errors)
        self.assertFalse(report['transferred'])
        self.assertEqual(list(self.target.rglob('*')), before)
        self.assertFalse(self.record().exists())

    def test_missing_git_shared_configuration_is_not_filled(self):
        self.write(self.source, '.agents/config.json', '{"maintenance":{"mode":"local"}}')
        code, _, errors = self.command()
        self.assertEqual(code, 2)
        self.assertIn('Git-shared configuration is missing', errors)
        self.assertFalse((self.target / '.agents').exists())

    def test_copy_fallback_prunes_metadata_before_traversal(self):
        self.write(self.source, '.agents/skills/example/.git/objects/large', 'irrelevant')
        self.write(self.source, '.agents/skills/example/__pycache__/large.pyc', 'irrelevant')
        self.write(self.source, '.agents/skills/example/node_modules/dependency/large', 'irrelevant')
        empty = self.source / '.agents/skills/example/empty'
        empty.mkdir()
        if os.name == 'posix':
            empty.chmod(0o700)
        original = Path.iterdir
        def iterate(path):
            if path.name in {'.git', '__pycache__', 'node_modules'}:
                self.fail('excluded directory was traversed: ' + str(path))
            return original(path)
        with self.fallback(), mock.patch.object(Path, 'iterdir', iterate):
            code, report, errors = self.command()
        self.assertEqual(code, 0, errors)
        self.assertEqual(set(report['paths'].values()), {'copy'})
        self.assertFalse((self.target / '.agents/skills').is_symlink())
        self.assertFalse((self.target / '.agents/skills/example/.git').exists())
        self.assertFalse((self.target / '.agents/skills/example/node_modules').exists())
        self.assertEqual((self.target / '.agents/skills/example/SKILL.md').read_text(), '# Example\n')
        self.assertTrue((self.target / '.agents/skills/example/empty').is_dir())
        if os.name == 'posix':
            self.assertEqual(stat.S_IMODE((self.target / '.agents/skills/example/scripts/run.sh').stat().st_mode), 0o755)
            self.assertEqual(stat.S_IMODE((self.target / '.agents/skills/example/empty').stat().st_mode), 0o700)

    def test_copy_origins_survive_restart_and_support_equivalent_edits(self):
        with self.fallback():
            self.assertEqual(self.command()[0], 0)
        result = subprocess.run([sys.executable, '-B', str(ENTRY), 'inspect', '--target', str(self.target)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        origin = json.loads(result.stdout)['projects'][0]
        self.assertEqual(origin['source'], str(self.source))
        self.assertEqual(origin['paths']['.agents/rules'], 'copy')
        self.assertTrue(origin['source_available'])
        for root in (Path(origin['target']), Path(origin['source'])):
            self.write(root, '.agents/rules/new.md', '# New rule\n')
            (root / '.agents/rules/project.md').unlink()
        self.assertEqual((self.source / '.agents/rules/new.md').read_bytes(),
                         (self.target / '.agents/rules/new.md').read_bytes())
        self.assertFalse((self.source / '.agents/rules/project.md').exists())
        self.assertFalse((self.target / '.agents/rules/project.md').exists())

    def test_renamed_recorded_file_keeps_its_source_for_later_edits(self):
        old, renamed = '.agents/rules/project.md', '.agents/rules/renamed.md'
        with self.fallback():
            self.assertEqual(self.command(scope=[old])[0], 0)
        for workspace in (self.source, self.target):
            (workspace / old).rename(workspace / renamed)
        origin = PREPARE.inspect(self.target)
        record_path = Path(origin['record'])
        record = json.loads(record_path.read_text())
        paths = record['projects']['.']['paths']
        paths[renamed] = paths.pop(old)
        temporary = record_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(record))
        temporary.replace(record_path)
        self.assertEqual(self.command(scope=[renamed])[0], 0)
        self.git(self.target, 'check-ignore', '--quiet', '--', renamed)
        result = subprocess.run([sys.executable, '-B', str(ENTRY), 'inspect', '--target', str(self.target)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        project = json.loads(result.stdout)['projects'][0]
        self.assertEqual(project['paths'], {renamed: 'copy'})
        for workspace in (Path(project['target']), Path(project['source'])):
            self.write(workspace, renamed, '# Revised after rename\n')
        self.assertEqual((self.target / renamed).read_bytes(), (self.source / renamed).read_bytes())
        for workspace in (self.source, self.target):
            (workspace / renamed).unlink()
        record['projects'].pop('.')
        temporary.write_text(json.dumps(record))
        temporary.replace(record_path)
        self.assertEqual(PREPARE.inspect(self.target)['projects'], [])

    def test_copy_retry_rejects_windows_junction_at_root_or_parent(self):
        with self.fallback():
            self.assertEqual(self.command()[0], 0)
        self.write(self.source, '.agents/skills/new/SKILL.md', '# New\n')
        for relative in ('.agents/skills', '.agents'):
            with self.subTest(relative=relative):
                redirected = self.target / relative
                outside = self.root / 'outside'
                redirected.rename(outside)
                redirected.symlink_to(outside, target_is_directory=True)
                before = {str(p.relative_to(outside)): p.read_bytes() for p in outside.rglob('*') if p.is_file()}
                with self.reparse_point(redirected):
                    self.assertFalse(redirected.is_symlink())
                    code, _, errors = self.command(scope=['.agents/skills'])
                self.assertEqual(code, 2, errors)
                self.assertEqual({str(p.relative_to(outside)): p.read_bytes() for p in outside.rglob('*') if p.is_file()}, before)
                redirected.unlink()
                outside.rename(redirected)

    def test_shared_root_rename_discovers_and_updates_each_dependent(self):
        old, renamed = '.agents/rules/project.md', '.agents/rules/renamed.md'
        peer = self.root / 'peer'
        self.git(self.source, '-c', 'core.hooksPath=' + str(self.root / 'no-hooks'),
                 'worktree', 'add', '-b', 'peer', str(peer))
        for target in (self.target, peer):
            self.assertEqual(self.command(target=target, scope=[old])[0], 0)
        registered = [Path(part[len('worktree '):])
                      for part in self.git(self.source, 'worktree', 'list', '--porcelain', '-z').split('\0')
                      if part.startswith('worktree ')]
        dependents = []
        for target in registered:
            observation = PREPARE.inspect(target)
            for project in observation['projects']:
                if project['source'] == str(self.source) and old in project['paths']:
                    dependents.append((Path(project['target']), Path(observation['record'])))
        self.assertEqual({target for target, _ in dependents}, {self.target, peer})
        (self.source / old).rename(self.source / renamed)
        for target, record_path in dependents:
            (target / old).unlink()
            (target / renamed).symlink_to(self.source / renamed)
            record = json.loads(record_path.read_text())
            paths = record['projects']['.']['paths']
            paths[renamed] = paths.pop(old)
            temporary = record_path.with_suffix('.tmp')
            temporary.write_text(json.dumps(record))
            temporary.replace(record_path)
            self.assertEqual(self.command(target=target, scope=[renamed])[0], 0)
        for target, _ in dependents:
            self.assertEqual(PREPARE.inspect(target)['projects'][0]['paths'], {renamed: 'link'})
            self.assertTrue((target / renamed).is_symlink())
            self.assertEqual((target / renamed).resolve(), self.source / renamed)
            self.assertEqual((target / renamed).read_text(), '# Rule\n')
            self.assertFalse((target / old).is_symlink())

    def test_redirected_origin_and_exclusion_paths_are_preserved(self):
        record = self.record()
        outside_record = self.root / 'outside-record.json'
        outside_record.write_text('{"projects":{}}')
        record.symlink_to(outside_record)
        with self.reparse_point(record):
            self.assertEqual(self.command()[0], 2)
        self.assertEqual(outside_record.read_text(), '{"projects":{}}')
        self.assertFalse((self.target / '.agents').exists())
        record.unlink()
        info = Path(self.git(self.source, 'rev-parse', '--absolute-git-dir').strip()) / 'info'
        outside_info = self.root / 'outside-info'
        info.rename(outside_info)
        info.symlink_to(outside_info, target_is_directory=True)
        before = (outside_info / 'exclude').read_bytes()
        with self.reparse_point(info):
            self.assertEqual(self.command()[0], 2)
        self.assertEqual((outside_info / 'exclude').read_bytes(), before)
        self.assertFalse((self.target / '.agents').exists())

    def test_observed_host_rejection_can_convert_only_recorded_link(self):
        self.assertEqual(self.command()[0], 0)
        code, report, errors = self.command('--copy', scope=['.agents/config.json'])
        self.assertEqual(code, 0, errors)
        self.assertEqual(report['paths'], {'.agents/config.json': 'copy'})
        self.assertFalse((self.target / '.agents/config.json').is_symlink())
        self.assertTrue((self.target / '.agents/skills').is_symlink())
        self.assertEqual((self.target / '.agents/config.json').read_bytes(),
                         (self.source / '.agents/config.json').read_bytes())

    def test_existing_configuration_is_preserved_before_any_transfer(self):
        self.write(self.target, '.agents/rules/project.md', '# Target work\n')
        code, _, errors = self.command()
        self.assertEqual(code, 2)
        self.assertIn('preserve existing target', errors)
        self.assertEqual((self.target / '.agents/rules/project.md').read_text(), '# Target work\n')
        self.assertFalse((self.target / '.agents/config.json').exists())
        self.assertFalse(self.record().exists())

    def test_existing_link_without_origin_is_not_converted(self):
        (self.target / '.agents').mkdir()
        (self.target / '.agents/config.json').symlink_to(self.source / '.agents/config.json')
        code, _, _ = self.command('--copy', scope=['.agents/config.json'])
        self.assertEqual(code, 2)
        self.assertTrue((self.target / '.agents/config.json').is_symlink())

    def test_replaced_link_and_changed_copy_are_preserved(self):
        self.assertEqual(self.command()[0], 0)
        destination = self.target / '.agents/config.json'
        destination.unlink()
        self.write(self.target, '.agents/config.json', '{"maintenance":{"mode":"local-only"},"new":true}')
        self.assertEqual(self.command()[0], 2)
        self.assertIn('new', destination.read_text())
        self.assertEqual(self.command('--copy', scope=['.agents/rules'])[0], 0)
        self.write(self.target, '.agents/rules/project.md', '# Changed copy\n')
        code, _, errors = self.command(scope=['.agents/rules'])
        self.assertEqual(code, 2)
        self.assertIn('conflicts', errors)
        self.assertEqual((self.source / '.agents/rules/project.md').read_text(), '# Rule\n')

    def test_partial_copy_retains_origin_and_can_fill_missing_files(self):
        original = PREPARE.shutil.copyfileobj
        calls = []
        def copy(input_file, output, *args):
            calls.append(input_file.name)
            if len(calls) == 2:
                raise OSError('injected interruption')
            return original(input_file, output, *args)
        with self.fallback(), mock.patch.object(PREPARE.shutil, 'copyfileobj', copy):
            code, _, errors = self.command()
        self.assertEqual(code, 2)
        self.assertIn('Preparation incomplete', errors)
        self.assertTrue(self.record().exists())
        self.assertTrue((self.target / '.agents/config.json').exists())
        partial = self.target / '.agents/rules/project.md'
        self.assertEqual(partial.read_bytes(), b'')
        self.assertEqual(self.command()[0], 2)
        partial.unlink()  # The fixture owner resolves this explicitly identified partial output.
        with self.fallback():
            code, _, errors = self.command()
        self.assertEqual(code, 0, errors)
        self.assertEqual((self.target / '.agents/rules/project.md').read_text(), '# Rule\n')

    def test_nested_worktree_and_corresponding_monorepo_projects(self):
        nested = self.source / '.worktrees/nested'
        nested.parent.mkdir()
        self.git(self.source, 'worktree', 'move', str(self.target), str(nested))
        self.target = nested
        source_project, target_project = self.source / 'packages/app', self.target / 'packages/app'
        target_project.mkdir(parents=True)
        self.write(source_project, '.agents/config.json', '{"maintenance":{"mode":"local-only"}}')
        self.write(source_project, '.agents/rules/project.md', '# Nested\n')
        code, _, errors = self.command(source=source_project, target=target_project,
                                      scope=['.agents/config.json', '.agents/rules'])
        self.assertEqual(code, 0, errors)
        report = PREPARE.inspect(self.target)
        self.assertEqual(report['projects'][0]['target'], str(target_project))
        self.assertEqual(report['projects'][0]['source'], str(source_project))
        self.assertTrue(self.git(target_project, 'check-ignore', '--', '.agents/rules').strip())

    def test_invalid_identity_mode_and_scope_fail_without_target_writes(self):
        cases = [dict(target=self.source), dict(scope=['../outside']), dict(scope=['.git']),
                 dict(scope=['.agents']), dict(scope=['.agents/project-config-sync.json']),
                 dict(scope=['.agents/skills', '.agents/skills/example']),
                 dict(scope=['missing']), dict(scope=['new\npattern']), dict(scope=['C:outside'])]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.command(**kwargs)[0], 2)
                self.assertFalse((self.target / '.agents').exists())
        self.write(self.target, '.agents/config.json', '{"maintenance":{"mode":"local"}}')
        self.assertEqual(self.command()[0], 2)
        self.assertEqual(json.loads((self.target / '.agents/config.json').read_text())['maintenance']['mode'], 'local')

    def test_different_repository_and_project_are_rejected(self):
        other = self.root / 'other'
        other.mkdir()
        self.git(other, 'init')
        self.assertEqual(self.command(source=other)[0], 2)
        (self.target / 'different-project').mkdir()
        self.assertEqual(self.command(target=self.target / 'different-project')[0], 2)
        self.assertFalse((self.target / '.agents').exists())

    def test_tracked_deletions_are_not_recreated(self):
        self.write(self.target, '.agents/config.json', (self.source / '.agents/config.json').read_text())
        self.git(self.target, 'add', '.agents/config.json')
        before = self.git(self.target, 'ls-files', '--stage', '-z')
        (self.target / '.agents/config.json').unlink()
        code, _, errors = self.command()
        self.assertEqual(code, 2)
        self.assertIn('preserve tracked configuration', errors)
        self.assertFalse((self.target / '.agents/config.json').exists())
        self.assertEqual(self.git(self.target, 'ls-files', '--stage', '-z'), before)

    def test_symlink_conflicts_do_not_trigger_copy_fallback(self):
        with mock.patch.object(Path, 'symlink_to', side_effect=FileExistsError(errno.EEXIST, 'concurrent file')):
            code, _, _ = self.command()
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(self.record().read_text())['projects']['.']['paths']['.agents/config.json'], 'link')
        self.assertFalse((self.target / '.agents/config.json').exists())

    def test_unsafe_nested_source_link_is_not_followed_during_copy(self):
        outside = self.root / 'outside'
        outside.mkdir()
        self.write(outside, 'private', 'not selected')
        (self.source / '.agents/skills/external').symlink_to(outside, target_is_directory=True)
        with self.fallback():
            code, _, errors = self.command()
        self.assertEqual(code, 2)
        self.assertIn('leaves the selected directory', errors)
        self.assertFalse((self.target / '.agents/skills/external/private').exists())

    def test_inspection_reports_absence_invalid_record_and_missing_source(self):
        self.assertEqual(PREPARE.inspect(self.target)['projects'], [])
        self.assertFalse(self.record().exists())
        self.assertEqual(self.command()[0], 0)
        record = json.loads(self.record().read_text())
        record['projects']['.']['source'] = str(self.root / 'missing-source')
        self.record().write_text(json.dumps(record))
        self.assertFalse(PREPARE.inspect(self.target)['projects'][0]['source_available'])
        self.record().write_text('{"projects": {"../escape": {}}}')
        with self.assertRaises(ValueError):
            PREPARE.inspect(self.target)

    def test_existing_exclusion_bytes_are_preserved(self):
        ignore = Path(self.git(self.source, 'rev-parse', '--absolute-git-dir').strip()) / 'info/exclude'
        original = ignore.read_bytes() + b'\n# personal rule\n/local-cache'
        ignore.write_bytes(original)
        self.assertEqual(self.command()[0], 0)
        after = ignore.read_bytes()
        self.assertTrue(after.startswith(original + b'\n'))
        self.assertEqual(self.command()[0], 0)
        self.assertEqual(ignore.read_bytes(), after)

    def test_exclusion_restores_effective_ignore_after_a_negation(self):
        ignore = Path(self.git(self.source, 'rev-parse', '--absolute-git-dir').strip()) / 'info/exclude'
        ignore.write_text('/.agents/config.json\n!/.agents/config.json\n')
        self.assertEqual(self.command()[0], 0)
        self.git(self.target, 'check-ignore', '--quiet', '--', '.agents/config.json')


if __name__ == '__main__':
    unittest.main()
