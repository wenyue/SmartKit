"""Exercise private storage and cross-feature expiry in isolated user caches."""
import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime/artifacts'))
import artifact_cache as cache


class ArtifactCacheTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='shared-artifact-cache-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        environment = patch.dict(os.environ, {
            'HOME': str(self.base), 'USERPROFILE': str(self.base),
            'XDG_CACHE_HOME': str(self.base / 'cache'),
            'XDG_STATE_HOME': str(self.base / 'state'), 'LOCALAPPDATA': str(self.base / 'local'),
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.errors = io.StringIO()
        redirect = contextlib.redirect_stderr(self.errors)
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)

    def group(self, artifact):
        return cache.cache_root() / artifact.id

    def test_default_private_capture_is_independent_of_web_service(self):
        artifact = cache.create_artifact({'report.html': b'fixed', 'raw/input.bin': b'\x00\xff'})
        self.assertEqual(artifact.expires_at - artifact.created_at, 7 * 24 * 60 * 60)
        self.assertTrue(all(not entry.public for entry in artifact.files.values()))
        self.assertFalse(artifact.published)
        self.assertEqual(cache.read_file(artifact.files['raw/input.bin']), b'\x00\xff')
        self.assertFalse((self.base / 'state').exists())
        self.assertFalse((cache.user_cache_dir() / 'smartkit/preview').exists())

    def test_each_group_has_its_own_deadline_and_access_does_not_renew_it(self):
        with patch.object(cache.time, 'time', return_value=1000000):
            short = cache.create_artifact({'report.html': b'short'}, retention=timedelta(hours=12))
            default = cache.create_artifact({'other.bin': b'default'})
        self.assertEqual(short.expires_at, 1000000 + 43200)
        for entry in short.files.values():
            os.utime(entry.path, (short.expires_at + 999999, short.expires_at + 999999))
            cache.read_file(entry)
        self.assertEqual(cache.load_artifact(short.id).expires_at, short.expires_at)
        cache.cleanup_expired(short.expires_at)
        self.assertFalse(self.group(short).exists())
        self.assertTrue(self.group(default).exists())

    def test_retention_starts_after_all_payload_writes(self):
        clock = [1000000]
        original = Path.write_bytes

        def slow_write(path, content):
            result = original(path, content)
            if path.name != cache.METADATA_NAME:
                clock[0] += 90
            return result

        with patch.object(cache.time, 'time', side_effect=lambda: clock[0]), patch.object(Path, 'write_bytes', slow_write):
            artifact = cache.create_artifact({'a': b'one', 'nested/b': b'two'}, retention=timedelta(seconds=60))
        self.assertEqual(artifact.created_at, 1000180)
        self.assertEqual(artifact.expires_at, 1000240)

    def test_failed_payload_or_metadata_write_leaves_no_partial_group(self):
        original = Path.write_bytes
        for failure_name in ('second.bin', cache.METADATA_NAME):
            def fail_write(path, content):
                if path.name == failure_name:
                    raise OSError('test write failure')
                return original(path, content)

            with self.subTest(failure_name=failure_name), patch.object(Path, 'write_bytes', fail_write):
                with self.assertRaisesRegex(OSError, 'test write failure'):
                    cache.create_artifact({'first.bin': b'one', 'second.bin': b'two'})
            self.assertEqual(list(cache.cache_root().iterdir()), [])

    def test_public_eligibility_needs_explicit_publication_without_renewal(self):
        artifact = cache.create_artifact({'diff.html': b'<html>', 'before.txt': b'secret'}, public_files=['diff.html'])
        self.assertFalse(cache.has_unexpired_artifacts(time.time()))
        published = cache.mark_published(artifact.id)
        self.assertTrue(published.published)
        self.assertTrue(cache.has_unexpired_artifacts(time.time()))
        self.assertTrue(published.files['diff.html'].public)
        self.assertFalse(published.files['before.txt'].public)
        self.assertEqual(cache.mark_published(artifact.id).expires_at, artifact.expires_at)
        private = cache.create_artifact({'private.txt': b'secret'})
        with self.assertRaises(ValueError):
            cache.mark_published(private.id)

    def test_generation_cleans_expired_groups_from_every_producer_together(self):
        with patch.object(cache.time, 'time', return_value=1000000):
            review = cache.create_artifact({'diff.html': b'html', 'raw/before.txt': b'before'}, retention=timedelta(hours=1))
            diagram = cache.create_artifact({'diagram.svg': b'svg'}, retention=timedelta(hours=2))
        with patch.object(cache.time, 'time', return_value=1000000 + 7200):
            fresh = cache.create_artifact({'new.txt': b'new'})
        self.assertFalse(self.group(review).exists())
        self.assertFalse(self.group(diagram).exists())
        self.assertTrue(self.group(fresh).exists())

    def test_invalid_inputs_are_rejected_before_any_expiry_effect(self):
        with patch.object(cache.time, 'time', return_value=1000000):
            old = cache.create_artifact({'old': b'keep'})
        for duration in (timedelta(0), timedelta(seconds=-1), None, 7):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                cache.create_artifact({'new': b'new'}, retention=duration)
        for name in ('../x', '/x', 'a\\b', 'a//b', 'a/./b', '.artifact.json', 'a:b'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                cache.create_artifact({name: b'invalid'})
        with self.assertRaises(ValueError):
            cache.create_artifact({'a': b'file', 'a/b': b'overlap'})
        with self.assertRaises(ValueError):
            cache.create_artifact({'a': b'valid'}, public_files=['missing'])
        self.assertTrue(self.group(old).exists())

    def test_malformed_foreign_changed_and_redirected_groups_are_preserved(self):
        with patch.object(cache.time, 'time', return_value=1000000):
            changed = cache.create_artifact({'x': b'original'})
            extra = cache.create_artifact({'x': b'original'})
            broken = cache.create_artifact({'x': b'original'})
        changed.files['x'].path.write_bytes(b'user altered')
        (self.group(extra) / 'important.txt').write_bytes(b'foreign')
        (self.group(broken) / 'files' / cache.METADATA_NAME).write_bytes(b'{broken')
        foreign = cache.cache_root() / 'foreign'
        foreign.mkdir()
        (foreign / 'important.txt').write_bytes(b'preserve')
        cache.cleanup_expired(2000000)
        self.assertTrue(all(self.group(item).exists() for item in (changed, extra, broken)))
        self.assertEqual((foreign / 'important.txt').read_bytes(), b'preserve')
        self.assertIn('Preserved unrecognized or unsafe cache', self.errors.getvalue())
        if os.name != 'nt':
            target = self.base / 'foreign-target'
            target.mkdir()
            link = cache.cache_root() / 'artifact-link'
            link.symlink_to(target, target_is_directory=True)
            cache.cleanup_expired(2000000)
            self.assertTrue(link.is_symlink())
            self.assertTrue(target.exists())

    def test_cleanup_failure_preserves_completed_effects_and_stops_creation(self):
        with patch.object(cache.time, 'time', return_value=1000000):
            groups = [cache.create_artifact({'x': b'x'}) for _ in range(2)]
        groups.sort(key=lambda item: item.id)
        remove = cache.shutil.rmtree

        def failing(path, *args, **kwargs):
            if Path(path) == self.group(groups[1]):
                raise PermissionError('denied')
            return remove(path, *args, **kwargs)

        with patch.object(cache.shutil, 'rmtree', side_effect=failing):
            with self.assertRaisesRegex(OSError, 'partially|some files may already'):
                cache.create_artifact({'new': b'new'})
        self.assertFalse(self.group(groups[0]).exists())
        self.assertTrue(self.group(groups[1]).exists())
        self.assertIn('Expired cache removed', self.errors.getvalue())

    def test_cli_captures_binary_input_from_external_cwd_and_returns_no_url(self):
        source = self.base / 'inputs'
        source.mkdir()
        (source / 'raw.bin').write_bytes(b'\x00\xfffixed')
        batch = source / 'batch.json'
        batch.write_text(json.dumps({'files': {'raw/data.bin': 'raw.bin'}}))
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'runtime/artifacts/artifact_cache.py'),
                                 'create', '--input', str(batch), '--retention-seconds', '43200'],
                                cwd=self.base, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record['expires_at'] - record['created_at'], 43200)
        self.assertNotIn('url', record)
        path = Path(record['files']['raw/data.bin']['path'])
        (source / 'raw.bin').write_bytes(b'mutable input')
        self.assertEqual(path.read_bytes(), b'\x00\xfffixed')
        self.assertFalse(record['files']['raw/data.bin']['public'])

    def test_identity_collision_preserves_existing_group(self):
        artifact = cache.create_artifact({'x': b'original'})
        suffix = artifact.id[len('artifact-'):]
        with patch.object(cache.uuid, 'uuid4') as identity:
            identity.return_value.hex = suffix
            with self.assertRaises(FileExistsError):
                cache.create_artifact({'x': b'overwrite'})
        self.assertEqual(cache.read_file(artifact.files['x']), b'original')
        self.assertFalse(list(cache.cache_root().glob('.pending-*')))

    def test_platform_roots_and_relative_environment_fallback(self):
        home = self.base / 'selected-home'
        for platform, expected in (('linux', self.base / 'cache'), ('win32', self.base / 'local'),
                                   ('darwin', home / 'Library/Caches')):
            with self.subTest(platform=platform), patch.object(cache.sys, 'platform', platform), patch.object(cache.Path, 'home', return_value=home):
                self.assertEqual(cache.user_cache_dir(), expected)
        for platform, expected in (('linux', home / '.cache'), ('win32', home / 'AppData/Local')):
            with self.subTest(platform=platform), patch.object(cache.sys, 'platform', platform), patch.object(cache.Path, 'home', return_value=home), patch.dict(os.environ, XDG_CACHE_HOME='relative', LOCALAPPDATA='relative'):
                self.assertEqual(cache.user_cache_dir(), expected)

    @unittest.skipIf(os.name == 'nt', 'Windows user-cache privacy uses inherited ACLs')
    def test_new_directories_are_private_and_existing_permissions_are_not_changed(self):
        artifact = cache.create_artifact({'raw/before.txt': b'private'})
        for directory in (cache.cache_root().parent, cache.cache_root(), self.group(artifact),
                          self.group(artifact) / 'files', self.group(artifact) / 'files/raw'):
            self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)
        cache.cache_root().chmod(0o750)
        cache.create_artifact({'new.txt': b'new'})
        self.assertEqual(stat.S_IMODE(cache.cache_root().stat().st_mode), 0o750)

    @unittest.skipIf(os.name == 'nt', 'POSIX symlink fixture; Windows junction tested separately')
    def test_namespace_redirect_is_rejected_but_explicit_cache_base_relocation_is_allowed(self):
        target = self.base / 'selected-target'
        target.mkdir()
        configured = self.base / 'selected-link'
        configured.symlink_to(target, target_is_directory=True)
        with patch.dict(os.environ, XDG_CACHE_HOME=str(configured)):
            artifact = cache.create_artifact({'x': b'fixed'})
            self.assertEqual(self.group(artifact).parent, target / 'smartkit/artifacts')
        base = cache.user_cache_dir()
        base.mkdir(parents=True, exist_ok=True)
        (base / 'smartkit').symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'redirect'):
            cache.create_artifact({'x': b'blocked'})
        self.assertFalse((target / 'artifacts').exists())

    def test_damaged_numeric_metadata_is_preserved_and_future_deadlines_are_not_expired(self):
        for number in (True, -1, float('nan'), float('inf'), 10 ** 400):
            artifact = cache.create_artifact({'x': b'preserve'})
            metadata = self.group(artifact) / 'files' / cache.METADATA_NAME
            record = json.loads(metadata.read_bytes())
            record['expires_at'] = number
            metadata.write_text(json.dumps(record))
            cache.cleanup_expired(time.time())
            self.assertTrue(artifact.files['x'].path.exists())
        with patch.object(cache.time, 'time', return_value=time.time() + 1000000):
            future = cache.create_artifact({'future': b'future'})
        cache.cleanup_expired(time.time())
        self.assertTrue(self.group(future).exists())

    def test_known_legacy_exports_keep_the_original_deadline_and_are_cleaned_by_any_producer(self):
        identity = 'review-' + 'a' * 32
        old = cache.user_cache_dir() / 'smartkit/review-for-humans' / identity
        folder = old / 'files/0001'
        folder.mkdir(parents=True)
        page = folder / 'diff.html'
        page.write_bytes(b'old html')
        (folder / 'before.txt').write_bytes(b'old raw')
        created = time.time()
        metadata = {'schema': 'smartkit.review-html-cache/v2', 'directory': identity, 'created_at': created}
        (old / 'files/cache.json').write_text(json.dumps(metadata))
        url = 'http://127.0.0.1:43123/artifacts/' + identity + '/0001/diff.html'
        manifest = [{'id': 'M1', 'title': 'x.py', 'path': str(page), 'url': url, 'markdown': '[x.py](' + url + ')'}]
        (old / 'files/manifest.json').write_text(json.dumps(manifest))
        original = (old / 'files/cache.json').read_bytes()
        cache.cleanup_expired(created + 7 * 86400 - 0.1)
        self.assertEqual((old / 'files/cache.json').read_bytes(), original)
        with patch.object(cache.time, 'time', return_value=created + 7 * 86400):
            cache.create_artifact({'diagram.svg': b'new producer'})
        self.assertFalse(old.exists())

    def test_foreign_import_cannot_supply_missing_legacy_reader(self):
        legacy = cache.user_cache_dir() / 'smartkit/review-for-humans'
        legacy.mkdir(parents=True)
        fake = SimpleNamespace(__file__=str(self.base / 'other-plugin/legacy_review_cache.py'))
        with patch.dict(sys.modules, legacy_review_cache=fake):
            with self.assertRaisesRegex(OSError, 'not from the loaded plugin'):
                cache.create_artifact({'x': b'blocked'})
        self.assertEqual(list(legacy.iterdir()), [])

    def test_cold_loaded_cache_resolves_its_legacy_reader_without_import_path_help(self):
        legacy = cache.user_cache_dir() / 'smartkit/review-for-humans'
        legacy.mkdir(parents=True)
        program = '''import importlib.util, sys
spec = importlib.util.spec_from_file_location("artifact_cache", sys.argv[1])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
print(module.create_artifact({"report.html": b"cold export"}).id)
'''
        result = subprocess.run([sys.executable, '-I', '-B', '-c', program,
                                 str(ROOT / 'runtime/artifacts/artifact_cache.py')],
                                cwd=self.base, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        artifact = cache.load_artifact(result.stdout.strip())
        self.assertEqual(cache.read_file(artifact.files['report.html']), b'cold export')
        self.assertTrue(legacy.is_dir())

    @unittest.skipUnless(os.name == 'nt', 'requires native Windows junction support')
    def test_windows_namespace_junction_is_preserved_and_rejected(self):
        base = cache.user_cache_dir()
        base.mkdir(parents=True, exist_ok=True)
        target = self.base / 'junction-target'
        target.mkdir()
        (target / 'important.txt').write_bytes(b'preserve')
        link = base / 'smartkit'
        result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(link), str(target)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        try:
            with self.assertRaisesRegex(ValueError, 'redirect'):
                cache.create_artifact({'x': b'blocked'})
            self.assertEqual((target / 'important.txt').read_bytes(), b'preserve')
        finally:
            link.rmdir()


if __name__ == '__main__':
    unittest.main()
