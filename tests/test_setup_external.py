from __future__ import annotations
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'skills' / 'setup-project-agents' / 'scripts'))

MIT_LICENSE = (
    REPO_ROOT / 'skills/setup-project-agents/scripts/_vendor/tomli/LICENSE'
).read_text(encoding='utf-8')
APACHE_LICENSE_SAMPLE = '''
Apache License Version 2.0, January 2004
Terms and Conditions for Use, Reproduction, and Distribution
2. Grant of Copyright License. Subject to the terms and conditions of this License.
3. Grant of Patent License. Subject to the terms and conditions of this License.
4. Redistribution. You may reproduce and distribute copies of the Work.
8. Limitation of Liability. In no event and under no legal theory shall any Contributor be liable.
9. Accepting Warranty or Additional Liability. You may charge a fee for acceptance of support,
warranty, indemnity, or other liability obligations.
END OF TERMS AND CONDITIONS
'''

from agents_setup import external  # noqa: E402
from agents_setup.external import ExternalSkillError, snapshot_external_skills  # noqa: E402
from agents_setup.external_contract import (  # noqa: E402
    ExternalContractError,
    is_link_like,
    license_matches,
)
from agents_setup.models import (  # noqa: E402
    ExternalSkillSpec,
    ExternalSourceSpec,
)


def git(directory: Path, *args: str) -> None:
    subprocess.run(
        ('git', '-C', str(directory), *args),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class SetupExternalSkillTest(unittest.TestCase):
    def make_repository(self, root: Path) -> tuple[Path, Path]:
        work = root / 'work'
        origin = root / 'origin.git'
        work.mkdir()
        git(work, 'init', '--quiet', '-b', 'main')
        git(work, 'config', 'user.email', 'test@example.invalid')
        git(work, 'config', 'user.name', 'Setup Test')
        skill = work / 'plugins/example/skills/external-check'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text(
            '---\nname: external-check\ndescription: Use for external checks.\n---\n\n# External\n',
            encoding='utf-8',
        )
        (work / 'LICENSE').write_text(MIT_LICENSE, encoding='utf-8')
        git(work, 'add', '.')
        git(work, 'commit', '--quiet', '-m', 'initial')
        subprocess.run(
            ('git', 'clone', '--quiet', '--bare', str(work), str(origin)),
            check=True,
        )
        git(work, 'remote', 'add', 'origin', str(origin))
        return work, origin

    @staticmethod
    def spec(repository: str) -> ExternalSourceSpec:
        return ExternalSourceSpec(
            'example/repository',
            repository,
            'main',
            (ExternalSkillSpec(
                'example/external-check',
                'external-check',
                PurePosixPath('plugins/example/skills/external-check'),
            ),),
        )

    def test_each_session_fetches_and_snapshots_the_current_ref(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            first_session = root / 'first'
            first_session.mkdir()
            first = snapshot_external_skills((self.spec(origin.as_uri()),), session=first_session)
            assert first is not None
            self.assertIn('# External', (first / 'external-check/SKILL.md').read_text())
            self.assertFalse((first_session / 'external-checkouts').exists())
            lock = json.loads((first / 'sources.json').read_text())
            self.assertEqual(lock['sources'][0]['resolved_ref'], 'main')
            self.assertEqual(lock['sources'][0]['ref_kind'], 'branch')
            license_item = lock['sources'][0]['license']
            self.assertEqual(license_item['spdx'], 'MIT')
            self.assertEqual(license_item['path'], 'LICENSE')
            self.assertRegex(license_item['sha256'], r'^[0-9a-f]{64}$')

            skill = work / 'plugins/example/skills/external-check/SKILL.md'
            skill.write_text(skill.read_text() + '\nUpdated.\n', encoding='utf-8')
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'update')
            git(work, 'push', '--quiet', 'origin', 'main')

            second_session = root / 'second'
            second_session.mkdir()
            second = snapshot_external_skills((self.spec(origin.as_uri()),), session=second_session)
            assert second is not None
            self.assertIn('Updated.', (second / 'external-check/SKILL.md').read_text())
            self.assertFalse((second_session / 'external-checkouts').exists())

    def test_git_commands_ignore_ambient_repository_and_config_overrides(self):
        checkout = Path('/private/external-checkout')
        with mock.patch.dict(
            os.environ,
            {
                'GIT_DIR': '/attacker/git',
                'GIT_WORK_TREE': '/attacker/tree',
                'GIT_INDEX_FILE': '/attacker/index',
                'HOME': '/attacker/home',
                'HTTPS_PROXY': 'https://attacker.invalid',
                'SSH_AUTH_SOCK': '/attacker/ssh-agent',
            },
            clear=False,
        ), mock.patch.object(
            external.subprocess,
            'run',
            return_value=subprocess.CompletedProcess(('git', 'version'), 0, '', ''),
        ) as run:
            external._run_git('version', cwd=checkout)

        environment = run.call_args.kwargs['env']
        self.assertEqual(run.call_args.kwargs['cwd'], checkout)
        self.assertNotIn('GIT_DIR', environment)
        self.assertNotIn('GIT_WORK_TREE', environment)
        self.assertNotIn('GIT_INDEX_FILE', environment)
        self.assertNotIn('HTTPS_PROXY', environment)
        self.assertNotIn('SSH_AUTH_SOCK', environment)
        self.assertEqual(environment['HOME'], str(checkout))
        self.assertEqual(environment['USERPROFILE'], str(checkout))
        self.assertEqual(environment['GIT_TERMINAL_PROMPT'], '0')
        self.assertEqual(environment['GIT_CONFIG_NOSYSTEM'], '1')
        self.assertEqual(environment['GIT_CONFIG_GLOBAL'], os.devnull)

    @unittest.skipUnless(os.name == 'posix', 'requires POSIX symlink modes')
    def test_checkout_cleanup_does_not_chmod_a_symlink_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            external_file = root / 'external'
            external_file.write_bytes(b'keep')
            external_file.chmod(stat.S_IREAD)
            checkout = root / 'checkouts'
            checkout.mkdir()
            (checkout / 'linked').symlink_to(external_file)

            external._remove_checkouts(checkout)

            self.assertFalse(checkout.exists())
            self.assertEqual(stat.S_IMODE(external_file.stat().st_mode), stat.S_IREAD)

    def test_every_external_git_command_uses_its_private_checkout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _, origin = self.make_repository(root)
            session = root / 'session'
            session.mkdir()
            checkout = session / 'external-checkouts/source-0000'
            real_run = subprocess.run

            with mock.patch.object(
                external.subprocess, 'run', wraps=real_run,
            ) as run:
                snapshot_external_skills(
                    (self.spec(origin.as_uri()),), session=session,
                )

            self.assertTrue(run.call_args_list)
            self.assertTrue(all(
                call.kwargs.get('cwd') == checkout
                for call in run.call_args_list
            ))

    def test_rejects_a_skill_whose_frontmatter_name_does_not_match(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            skill = work / 'plugins/example/skills/external-check/SKILL.md'
            skill.write_text(skill.read_text().replace('external-check', 'wrong-name'))
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'wrong name')
            git(work, 'push', '--quiet', 'origin', 'main')
            session = root / 'session'
            session.mkdir()
            with self.assertRaisesRegex(ExternalSkillError, 'name does not match'):
                snapshot_external_skills((self.spec(origin.as_uri()),), session=session)
            self.assertFalse((session / 'external-checkouts').exists())

    def test_rejects_duplicate_frontmatter_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            skill = work / 'plugins/example/skills/external-check/SKILL.md'
            skill.write_text(
                '---\nname: external-check\nname: external-check\n---\n# External\n',
                encoding='utf-8',
            )
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'duplicate name')
            git(work, 'push', '--quiet', 'origin', 'main')
            session = root / 'session'
            session.mkdir()

            with self.assertRaisesRegex(ExternalSkillError, 'one frontmatter name'):
                snapshot_external_skills((self.spec(origin.as_uri()),), session=session)

    def test_rejects_a_second_frontmatter_block(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            skill = work / 'plugins/example/skills/external-check/SKILL.md'
            skill.write_text(
                '---\nname: external-check\n---\n\n---\nname: other\n---\n',
                encoding='utf-8',
            )
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'second frontmatter block')
            git(work, 'push', '--quiet', 'origin', 'main')
            session = root / 'session'
            session.mkdir()

            with self.assertRaisesRegex(ExternalSkillError, 'duplicate YAML frontmatter'):
                snapshot_external_skills((self.spec(origin.as_uri()),), session=session)

    def test_rejects_unclosed_frontmatter_even_when_body_contains_a_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            skill = work / 'plugins/example/skills/external-check/SKILL.md'
            skill.write_text(
                '---\ndescription: no closing marker\n\nname: external-check\n',
                encoding='utf-8',
            )
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'unclosed frontmatter')
            git(work, 'push', '--quiet', 'origin', 'main')
            session = root / 'session'
            session.mkdir()

            with self.assertRaisesRegex(ExternalSkillError, 'malformed YAML frontmatter'):
                snapshot_external_skills((self.spec(origin.as_uri()),), session=session)

    def test_recognizes_standard_spdx_license_text(self):
        self.assertTrue(license_matches(
            'Apache-2.0',
            APACHE_LICENSE_SAMPLE.encode(),
        ))
        self.assertFalse(license_matches(
            'Apache-2.0',
            b'Apache License\nVersion 2.0, January 2004\n',
        ))
        self.assertFalse(license_matches('Apache-2.0', b'not a license'))
        with self.assertRaisesRegex(ExternalContractError, 'unsupported SPDX'):
            license_matches('GPL-3.0-only', b'GPL-3.0-only')

    def test_rejects_text_that_spoofs_two_supported_licenses(self):
        content = (MIT_LICENSE + APACHE_LICENSE_SAMPLE).encode()
        self.assertFalse(license_matches('MIT', content))
        self.assertFalse(license_matches('Apache-2.0', content))
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / 'LICENSE').write_bytes(content)
            with self.assertRaisesRegex(ExternalContractError, 'ambiguous'):
                external.discover_license(root, 'external source license')

    def test_link_like_recognizes_windows_reparse_points_without_is_junction(self):
        path = mock.Mock()
        path.lstat.return_value = mock.Mock(
            st_mode=stat.S_IFDIR,
            st_file_attributes=0x400,
        )

        self.assertTrue(is_link_like(path))

    def test_discovers_a_supported_copying_file_without_project_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / 'COPYING').write_text(
                APACHE_LICENSE_SAMPLE,
                encoding='utf-8',
            )
            discovered = external.discover_license(root, 'external source license')
            self.assertEqual(discovered.spdx, 'Apache-2.0')
            self.assertEqual(discovered.path, PurePosixPath('COPYING'))

    def test_rejects_a_source_without_a_recognized_root_license(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            (work / 'LICENSE').write_text('A private license.\n', encoding='utf-8')
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'unrecognized license')
            git(work, 'push', '--quiet', 'origin', 'main')
            session = root / 'session'
            session.mkdir()
            with self.assertRaisesRegex(ExternalSkillError, 'not found or recognized'):
                snapshot_external_skills((self.spec(origin.as_uri()),), session=session)
            self.assertFalse((session / 'external-checkouts').exists())

    def test_rejects_conflicting_recognized_root_licenses(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            (work / 'COPYING').write_text(
                APACHE_LICENSE_SAMPLE,
                encoding='utf-8',
            )
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'ambiguous licenses')
            git(work, 'push', '--quiet', 'origin', 'main')
            session = root / 'session'
            session.mkdir()

            with self.assertRaisesRegex(ExternalSkillError, 'license.*ambiguous'):
                snapshot_external_skills((self.spec(origin.as_uri()),), session=session)

            self.assertFalse((session / 'external-checkouts').exists())

    def test_rejects_a_symlinked_selected_path_ancestor(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            (work / 'plugins/linked').symlink_to('example', target_is_directory=True)
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'linked path')
            git(work, 'push', '--quiet', 'origin', 'main')
            spec = ExternalSourceSpec(
                'example/repository', origin.as_uri(), 'main',
                (ExternalSkillSpec(
                    'example/external-check', 'external-check',
                    PurePosixPath('plugins/linked/skills/external-check'),
                ),),
            )
            session = root / 'session'
            session.mkdir()
            with self.assertRaisesRegex(ExternalSkillError, 'contains a symlink'):
                snapshot_external_skills((spec,), session=session)

    def test_rejects_a_tag_that_moved_since_a_case_variant_existing_ref(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            git(work, 'tag', 'v1')
            git(work, 'push', '--quiet', 'origin', 'refs/tags/v1')
            tagged = ExternalSourceSpec(
                'example/repository', origin.as_uri(), 'v1',
                (ExternalSkillSpec(
                    'example/external-check', 'external-check',
                    PurePosixPath('plugins/example/skills/external-check'),
                ),),
            )
            first_session = root / 'first'
            first_session.mkdir()
            first = snapshot_external_skills((tagged,), session=first_session)
            assert first is not None
            source_metadata = json.loads((first / 'sources.json').read_text())
            for source in source_metadata['sources']:
                # The local bare repository is only a fetch fixture. An installed
                # ownership manifest records the supported GitHub source identity.
                source['url'] = 'https://github.com/example/repository'
                source['id'] = 'Example/Repository'
                source['requested_ref'] = 'V1'
                for skill_item in source['skills']:
                    skill_item['id'] = 'Example/external-check'
                    skill_item.pop('files')
            existing_manifest = first_session / 'smartkit.lock.json'
            existing_manifest.write_text(json.dumps({
                'sources': source_metadata['sources'],
                'assets': [{
                    'kind': 'tree',
                    'role': 'skill',
                    'path': '.agents/skills/external-check',
                    'digest': 'b' * 64,
                    'source': 'Example/Repository',
                    'source_path': 'plugins/example/skills/external-check',
                }],
            }), encoding='utf-8')

            skill = work / 'plugins/example/skills/external-check/SKILL.md'
            skill.write_text(skill.read_text() + '\nMoved tag.\n', encoding='utf-8')
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'move tag')
            git(work, 'tag', '--force', 'v1')
            git(work, 'push', '--quiet', '--force', 'origin', 'refs/tags/v1')

            second_session = root / 'second'
            second_session.mkdir()
            with self.assertRaisesRegex(ExternalSkillError, 'tag moved'):
                snapshot_external_skills(
                    (tagged,),
                    session=second_session,
                    existing_manifest=existing_manifest,
                )

    def test_rejects_a_recorded_tag_shadowed_by_a_branch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            git(work, 'tag', 'v1')
            git(work, 'push', '--quiet', 'origin', 'refs/tags/v1')
            tagged = ExternalSourceSpec(
                'example/repository', origin.as_uri(), 'v1',
                (ExternalSkillSpec(
                    'example/external-check', 'external-check',
                    PurePosixPath('plugins/example/skills/external-check'),
                ),),
            )
            first_session = root / 'first'
            first_session.mkdir()
            first = snapshot_external_skills((tagged,), session=first_session)
            assert first is not None
            sources = json.loads((first / 'sources.json').read_text())['sources']
            for source in sources:
                source['url'] = 'https://github.com/example/repository'
                for skill_item in source['skills']:
                    skill_item.pop('files')
            existing_manifest = first_session / 'smartkit.lock.json'
            existing_manifest.write_text(json.dumps({
                'sources': sources,
                'assets': [{
                    'kind': 'tree',
                    'role': 'skill',
                    'path': '.agents/skills/external-check',
                    'digest': 'b' * 64,
                    'source': 'example/repository',
                    'source_path': 'plugins/example/skills/external-check',
                }],
            }), encoding='utf-8')

            skill = work / 'plugins/example/skills/external-check/SKILL.md'
            skill.write_text(skill.read_text() + '\nBranch shadow.\n', encoding='utf-8')
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'shadow tag with branch')
            git(work, 'branch', 'v1')
            git(work, 'push', '--quiet', 'origin', 'refs/heads/v1')

            second_session = root / 'second'
            second_session.mkdir()
            with self.assertRaisesRegex(ExternalSkillError, 'tag moved'):
                snapshot_external_skills(
                    (tagged,),
                    session=second_session,
                    existing_manifest=existing_manifest,
                )

    def test_rejects_a_recorded_tag_shadowed_by_a_same_commit_branch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            git(work, 'tag', 'v1')
            git(work, 'push', '--quiet', 'origin', 'refs/tags/v1')
            tagged = ExternalSourceSpec(
                'example/repository', origin.as_uri(), 'v1',
                (ExternalSkillSpec(
                    'example/external-check', 'external-check',
                    PurePosixPath('plugins/example/skills/external-check'),
                ),),
            )
            first_session = root / 'first'
            first_session.mkdir()
            first = snapshot_external_skills((tagged,), session=first_session)
            assert first is not None
            sources = json.loads((first / 'sources.json').read_text())['sources']
            for source in sources:
                source['url'] = 'https://github.com/example/repository'
                for skill_item in source['skills']:
                    skill_item.pop('files')
            existing_manifest = first_session / 'smartkit.lock.json'
            existing_manifest.write_text(json.dumps({
                'sources': sources,
                'assets': [{
                    'kind': 'tree',
                    'role': 'skill',
                    'path': '.agents/skills/external-check',
                    'digest': 'b' * 64,
                    'source': 'example/repository',
                    'source_path': 'plugins/example/skills/external-check',
                }],
            }), encoding='utf-8')
            git(work, 'branch', 'v1')
            git(work, 'push', '--quiet', 'origin', 'refs/heads/v1')

            second_session = root / 'second'
            second_session.mkdir()
            with self.assertRaisesRegex(ExternalSkillError, 'tag moved'):
                snapshot_external_skills(
                    (tagged,),
                    session=second_session,
                    existing_manifest=existing_manifest,
                )

    def test_distinct_sources_receive_injective_private_checkout_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work, origin = self.make_repository(root)
            second_skill = work / 'plugins/example/skills/second-check'
            second_skill.mkdir()
            (second_skill / 'SKILL.md').write_text(
                '---\nname: second-check\ndescription: Use for second checks.\n---\n',
                encoding='utf-8',
            )
            git(work, 'add', '.')
            git(work, 'commit', '--quiet', '-m', 'add second skill')
            git(work, 'push', '--quiet', 'origin', 'main')
            specs = (
                ExternalSourceSpec(
                    'a--b/c', origin.as_uri(), 'main',
                    (ExternalSkillSpec(
                        'a--b/external-check', 'external-check',
                        PurePosixPath('plugins/example/skills/external-check'),
                    ),),
                ),
                ExternalSourceSpec(
                    'a/b--c', origin.as_uri(), 'main',
                    (ExternalSkillSpec(
                        'a/second-check', 'second-check',
                        PurePosixPath('plugins/example/skills/second-check'),
                    ),),
                ),
            )
            session = root / 'session'
            session.mkdir()

            snapshots = snapshot_external_skills(specs, session=session)

            assert snapshots is not None
            self.assertTrue((snapshots / 'external-check/SKILL.md').is_file())
            self.assertTrue((snapshots / 'second-check/SKILL.md').is_file())
            self.assertFalse((session / 'external-checkouts').exists())


if __name__ == '__main__':
    unittest.main()
