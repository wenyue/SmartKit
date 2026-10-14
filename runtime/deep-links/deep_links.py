"""Register, create, and open current-user SmartKit links. Requires Python 3.8+."""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import zipfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator, Sequence

import actions
import registration


TOKEN = re.compile(r'[A-Za-z0-9_-]{32}\Z')
SOURCE_FILES = ('__main__.py', 'deep_links.py', 'registration.py', 'actions.py')


Task = actions.Task


@dataclass(frozen=True)
class Link:
    id: str
    action: str
    url: str
    web_url: str
    markdown: str


def _read_json(path: Path) -> object:
    if path.is_symlink():
        raise ValueError(f'SmartKit metadata must not be a symbolic link: {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def _atomic_json(path: Path, value: object) -> None:
    descriptor, name = tempfile.mkstemp(prefix='.smartkit-', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            json.dump(value, output, ensure_ascii=False, indent=2)
            output.write('\n')
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _root_ready(root: Path) -> None:
    if root.is_symlink():
        raise ValueError('the SmartKit installation directory must not be a symbolic link')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)


@contextmanager
def installation_lock(root: Path) -> Iterator[None]:
    """Serialize installers with an OS-held lock released when its process exits."""
    _root_ready(root)
    path = root / 'registration.lock'
    with path.open('a+b') as lock:
        if sys.platform == 'win32':
            import msvcrt
            if path.stat().st_size == 0:
                lock.write(b'0')
                lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            if sys.platform == 'win32':
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)


def source_release() -> tuple[str, str]:
    if zipfile.is_zipfile(sys.argv[0]):
        with zipfile.ZipFile(sys.argv[0]) as archive:
            release = json.loads(archive.read('release.json'))
        return release['version'], release['digest']
    source = Path(__file__).resolve().parent
    version = (source.parents[1] / 'VERSION').read_text(encoding='utf-8').strip()
    digest = hashlib.sha256(version.encode())
    for name in SOURCE_FILES:
        digest.update(name.encode())
        digest.update((source / name).read_bytes())
    return version, digest.hexdigest()


def _version(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r'\d+\.\d+\.\d+', value):
        raise ValueError('invalid SmartKit release version')
    return tuple(int(part) for part in value.split('.'))


def _state(root: Path) -> dict[str, object] | None:
    path = root / 'installation.json'
    if path.is_symlink():
        raise ValueError('installation metadata must not be a symbolic link')
    if not path.exists():
        return None
    value = _read_json(path)
    if (not isinstance(value, dict) or value.get('owner') != 'smartkit'
            or type(value.get('enabled')) is not bool):
        raise ValueError('invalid SmartKit installation metadata; existing files were preserved')
    if value['enabled']:
        if not all(isinstance(value.get(key), str) for key in ('version', 'digest', 'interpreter', 'archive_hash')):
            raise ValueError('incomplete SmartKit installation metadata')
        _version(value['version'])
    return value


def _deploy(root: Path, current: dict[str, object]) -> None:
    target = root / 'deep-links.pyz'
    descriptor, name = tempfile.mkstemp(prefix='.deep-links-', suffix='.pyz', dir=root)
    os.close(descriptor)
    temporary = Path(name)
    try:
        if zipfile.is_zipfile(sys.argv[0]):
            shutil.copyfile(sys.argv[0], temporary)
        else:
            source = Path(__file__).resolve().parent
            with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                for filename in SOURCE_FILES:
                    archive.writestr(filename, (source / filename).read_bytes())
                archive.writestr('release.json', json.dumps({'version': current['version'], 'digest': current['digest']}))
        subprocess.run([sys.executable, str(temporary), '--help'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=10)
        current['archive_hash'] = hashlib.sha256(temporary.read_bytes()).hexdigest()
        # Record the new release first so an interrupted upgrade cannot be downgraded by an older Hook.
        _atomic_json(root / 'installation.json', current)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def ensure(root: Path, *, enable: bool = False) -> dict[str, str]:
    """Maintain an opted-in installation; never claim ownership of a foreign handler."""
    state = _state(root)
    if not enable and (state is None or not state['enabled']):
        return {'status': 'disabled'}
    environment = registration.desktop_environment()
    if not registration.desktop_available(environment):
        if enable:
            raise OSError('protocol registration requires a local desktop session')
        return {'status': 'skipped'}
    with installation_lock(root):
        state = _state(root)
        if not enable and (state is None or not state['enabled']):
            return {'status': 'disabled'}
        if registration.ownership(environment) == 'foreign':
            raise FileExistsError('smartkit:// is associated with another application; no association was replaced')
        version, digest = source_release()
        archive = root / 'deep-links.pyz'
        if archive.is_symlink():
            raise ValueError('the installed program must not be a symbolic link')
        if state is None and archive.exists():
            raise FileExistsError('an unowned program exists at the installation path; it was preserved')
        if state and state['enabled'] and _version(state['version']) > _version(version):
            if not archive.is_file() or hashlib.sha256(archive.read_bytes()).hexdigest() != state['archive_hash']:
                raise OSError('the newer installed SmartKit program is unavailable; an older Hook cannot replace it')
            interpreter = Path(state['interpreter'])
            if not registration.registration_matches(interpreter, archive, environment):
                registration.register(interpreter, archive, environment)
            return {'status': 'ready', 'path': str(archive)}
        interpreter = Path(sys.executable).resolve()
        if sys.platform == 'win32' and interpreter.with_name('pythonw.exe').is_file():
            interpreter = interpreter.with_name('pythonw.exe')
        intact = bool(state and state['enabled'] and state['digest'] == digest and archive.is_file()
                      and hashlib.sha256(archive.read_bytes()).hexdigest() == state['archive_hash'])
        current = {'owner': 'smartkit', 'enabled': True, 'version': version,
                   'digest': digest, 'interpreter': str(interpreter)}
        if intact:
            current['archive_hash'] = state['archive_hash']
            if current != state:
                _atomic_json(root / 'installation.json', current)
        else:
            _deploy(root, current)
        if not registration.registration_matches(interpreter, archive, environment):
            registration.register(interpreter, archive, environment)
        return {'status': 'ready', 'path': str(archive)}


def uninstall(root: Path) -> dict[str, str]:
    with installation_lock(root):
        state = _state(root)
        if state is None:
            return {'status': 'disabled'}
        # Disabling first prevents another Hook from recreating a partially removed association.
        _atomic_json(root / 'installation.json', {'owner': 'smartkit', 'enabled': False})
        registration.unregister(registration.desktop_environment())
        return {'status': 'disabled'}


def parse_tasks(value: object, base: Path, viewer: str) -> list[Task]:
    if not isinstance(value, list):
        raise ValueError('batch input must be a JSON array')
    tasks: list[Task] = []
    identities: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise ValueError('each task must be an object')
        identity, action = item.get('id'), item.get('action', 'diff')
        if not isinstance(identity, str) or not identity or identity in identities:
            raise ValueError('each task needs a unique nonempty string id')
        identities.add(identity)
        if not isinstance(action, str) or action not in actions.HANDLERS:
            raise ValueError(f'unknown action: {action}')
        tasks.append(actions.prepare_task(item, base, viewer))
    return tasks


def create(root: Path, tasks: Sequence[Task]) -> list[Link]:
    """Validate and snapshot the entire batch before returning any links."""
    _root_ready(root)
    directory = root / 'tasks'
    if directory.is_symlink():
        raise ValueError('the task directory must not be a symbolic link')
    directory.mkdir(exist_ok=True, mode=0o700)
    links: list[Link] = []
    committed: list[Path] = []
    with tempfile.TemporaryDirectory(prefix='.batch-', dir=directory) as temporary:
        staging = Path(temporary)
        for task in tasks:
            token = secrets.token_urlsafe(24)
            folder = staging / token
            folder.mkdir(mode=0o700)
            record = actions.snapshot(folder, task)
            _atomic_json(folder / 'record.json', record)
            destination = directory / token
            label = task.title.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
            url = f'smartkit://{task.action}/{token}'
            links.append(Link(task.id, task.action, url, (destination / record['preview']).as_uri(), f'[{label}]({url})'))
        try:
            for link in links:
                token = parse_url(link.url)[1]
                destination = directory / token
                if destination.exists():
                    raise FileExistsError('task ID collision; existing tasks were preserved')
                os.replace(staging / token, destination)
                committed.append(destination)
        except BaseException:
            # Any interruption aborts this batch; cleanup concerns only newly committed snapshots.
            for folder in committed:
                try:
                    shutil.rmtree(folder)
                except OSError as cleanup_error:
                    print(f'SmartKit batch cleanup failed: {cleanup_error}', file=sys.stderr)
            raise
    return links


def parse_url(url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlsplit(url)
    token = parsed.path[1:]
    if (parsed.scheme != 'smartkit' or parsed.netloc not in actions.HANDLERS
            or not parsed.path.startswith('/') or not TOKEN.fullmatch(token)
            or parsed.query or parsed.fragment):
        raise ValueError('invalid SmartKit link; expected smartkit://<action>/<task ID>')
    return parsed.netloc, token


def load_task(root: Path, action: str, token: str) -> tuple[Path, dict[str, str]]:
    if action not in actions.HANDLERS or not TOKEN.fullmatch(token):
        raise ValueError('invalid task action or ID')
    folder = root / 'tasks' / token
    if (root / 'tasks').is_symlink() or folder.is_symlink():
        raise ValueError('task snapshots must not be symbolic links')
    record = actions.validate_record(action, _read_json(folder / 'record.json'))
    for field in ('before', 'after', 'preview'):
        if field not in record:
            continue
        name = record[field]
        path = folder / name
        if not name or name in {'.', '..'} or '/' in name or '\\' in name or path.is_symlink() or not path.is_file():
            raise ValueError('invalid or missing snapshot; regenerate this task')
    return folder, record


def open_link(root: Path, url: str) -> dict[str, str]:
    action, token = parse_url(url)
    folder, record = load_task(root, action, token)
    return actions.HANDLERS[action](folder, record, registration.desktop_environment())


def clean(root: Path, token: str) -> None:
    if not TOKEN.fullmatch(token):
        raise ValueError('invalid task ID')
    folder = root / 'tasks' / token
    value = _read_json(folder / 'record.json')
    if not isinstance(value, dict) or not isinstance(value.get('action'), str):
        raise ValueError('invalid task record; cleanup did not remove it')
    load_task(root, value['action'], token)
    shutil.rmtree(folder)


def serve(root: Path, port: int, batch: object = None) -> None:
    """Serve previews on loopback; GET never launches an application."""
    class PreviewHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self._preview(body=True)

        def do_HEAD(self) -> None:
            self._preview(body=False)

        def _preview(self, *, body: bool) -> None:
            if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
                self.send_error(403)
                return
            parsed = urllib.parse.urlsplit(self.path)
            pieces = parsed.path.strip('/').split('/')
            try:
                if parsed.query or parsed.fragment or len(pieces) != 2:
                    raise ValueError('invalid preview path')
                folder, record = load_task(root, *pieces)
                preview = folder / record['preview']
                content = preview.read_bytes()
            except (OSError, ValueError):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(str(preview))[0] or 'application/octet-stream')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            if body:
                self.wfile.write(content)

        def log_message(self, format: str, *args: object) -> None:
            pass

    with ThreadingHTTPServer(('127.0.0.1', port), PreviewHandler) as server:
        base_url = f'http://127.0.0.1:{server.server_port}'
        output = {'base_url': base_url, 'url_template': '/<action>/<task ID>'}
        if batch is not None:
            if not isinstance(batch, list):
                raise ValueError('preview input must be the JSON array returned by create')
            previews = []
            for item in batch:
                if not isinstance(item, dict) or not isinstance(item.get('url'), str):
                    raise ValueError('invalid preview link')
                action, token = parse_url(item['url'])
                folder, record = load_task(root, action, token)
                previews.append({'id': record['id'], 'url': f'{base_url}/{action}/{token}'})
            output['links'] = previews
        print(json.dumps(output, ensure_ascii=True), flush=True)
        server.serve_forever()


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    installer = commands.add_parser('ensure', help='check an enabled installation; --enable opts in')
    installer.add_argument('--enable', action='store_true')
    installer.add_argument('--quiet', action='store_true')
    batch = commands.add_parser('create', help='snapshot a batch and print JSON links')
    batch.add_argument('--input', type=Path, required=True)
    batch.add_argument('--viewer', choices=sorted(actions.VIEWERS), default='auto')
    opener = commands.add_parser('open', help='dispatch a SmartKit URL')
    opener.add_argument('url')
    commands.add_parser('uninstall', help='disable auto-registration and remove the owned association')
    cleanup = commands.add_parser('clean', help='explicitly delete one task and its snapshots')
    cleanup.add_argument('task_id')
    web = commands.add_parser('serve', help='serve optional HTTP preview links until stopped')
    web.add_argument('--port', type=int, default=0)
    web.add_argument('--input', type=Path, help='the JSON array returned by create; print real HTTP URLs')
    args = parser.parse_args(arguments)
    root = registration.data_root()
    try:
        if args.command == 'ensure':
            result = ensure(root, enable=args.enable)
        elif args.command == 'uninstall':
            result = uninstall(root)
        elif args.command == 'create':
            source = args.input.resolve(strict=True)
            tasks = parse_tasks(_read_json(source), source.parent, args.viewer)
            result = [asdict(link) for link in create(root, tasks)]
        elif args.command == 'open':
            result = open_link(root, args.url)
        elif args.command == 'clean':
            clean(root, args.task_id)
            result = {'status': 'removed'}
        else:
            serve(root, args.port, _read_json(args.input) if args.input else None)
            return 0
        if not getattr(args, 'quiet', False):
            # Escaped JSON remains lossless on redirected Windows consoles with legacy encodings.
            print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        message = f'SmartKit Links: {error}'
        print(message, file=sys.stderr)
        if args.command == 'open':
            # Native activation has no terminal; preserve the failure and try desktop feedback.
            try:
                _root_ready(root)
                with (root / 'errors.log').open('a', encoding='utf-8') as log:
                    log.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {message}\n')
                registration.notify_failure(message)
            except (OSError, subprocess.SubprocessError) as feedback_error:
                print(f'SmartKit feedback failed: {feedback_error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
