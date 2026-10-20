"""Persistent personal Git repositories, preserving local work on every refusal.

Validation errors use ValueError; failed subprocesses and filesystem operations use
OSError. Git failures can retain local changes or commits and never imply rollback.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Optional, Sequence


_REPOSITORY = re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?/[A-Za-z0-9][A-Za-z0-9._-]*\Z')
_HOST = r'[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*'
_ENTRY = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*\Z')


def _run(arguments: Sequence[str], *, cwd: Optional[Path] = None, host: str = 'github.com') -> subprocess.CompletedProcess:
    # Keep credentials and user Git configuration, but never inherit another repository's routing.
    environment = os.environ.copy()
    if arguments[0] == 'gh':
        environment['GH_HOST'] = host
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR', 'GIT_PREFIX',
                'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        environment.pop(key, None)
    try:
        return subprocess.run(arguments, cwd=cwd, env=environment, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired as error:
        raise OSError('Git or GitHub operation timed out; inspect its state before retrying') from error


def _checked(arguments: Sequence[str], *, cwd: Optional[Path] = None, host: str = 'github.com') -> str:
    result = _run(arguments, cwd=cwd, host=host)
    if result.returncode:
        raise OSError('{} failed: {}'.format(arguments[0], result.stderr.strip()))
    return result.stdout.rstrip('\n')


def _git(path: Path, *arguments: str, host: str = 'github.com') -> str:
    # gh keeps tokens in the existing credential store; the fallback helper is command-local.
    return _checked(('git', '-c', 'credential.https://' + host + '.helper=!gh auth git-credential',
                     '-C', str(path), *arguments))


def validate_repository(value: object) -> str:
    """Normalize an owner/name or credential-free HTTPS URL, retaining host identity.

    Bare names and github.com URLs share the existing owner/name storage key.
    Enterprise URLs retain their host so credentials and checkouts cannot collide.
    """
    if isinstance(value, str):
        if _REPOSITORY.fullmatch(value) and not value.endswith('.git'):
            return value
        match = re.fullmatch(r'https://(' + _HOST + r')/([^/]+/[^/]+)', value)
        if match:
            host, name = match.groups()
            if name.endswith('.git'):
                name = name[:-4]
            if _REPOSITORY.fullmatch(name) and not name.endswith('.git'):
                return name if host.lower() == 'github.com' else 'https://' + host.lower() + '/' + name
    raise ValueError('repository must be a GitHub owner/repository name or credential-free HTTPS repository URL')


def _repository_parts(repository: str) -> tuple[str, str]:
    value = validate_repository(repository)
    if value.startswith('https://'):
        host, name = value[len('https://'):].split('/', 1)
        return host, name
    return 'github.com', value


def validate_branch(value: object) -> str:
    if not isinstance(value, str) or not value or value.startswith('-') or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError('branch must be a literal Git branch name')
    result = _run(('git', 'check-ref-format', '--branch', value))
    if result.returncode or result.stdout.strip() != value:
        raise ValueError('branch must be a literal Git branch name')
    return value


def validate_entry(value: object) -> str:
    if not isinstance(value, str) or not _ENTRY.fullmatch(value):
        raise ValueError('entry must be a single project slug')
    return value


def state_root() -> Path:
    """Return durable user storage, independently of disposable artifact caches."""
    override = os.environ.get('SMARTKIT_PROJECT_CONFIG_HOME')
    if override:
        return Path(override).expanduser().absolute()
    if os.name == 'nt':
        local = os.environ.get('LOCALAPPDATA')
        return (Path(local) if local else Path.home() / 'AppData' / 'Local') / 'SmartKit' / 'project-config'
    base = os.environ.get('XDG_DATA_HOME')
    return (Path(base) if base and Path(base).is_absolute() else Path.home() / '.local' / 'share') / 'smartkit' / 'project-config'


def _checkout_path(repository: str, branch: str) -> Path:
    identity = (validate_repository(repository).lower() + '\0' + branch).encode('utf-8')
    return state_root() / 'repositories' / hashlib.sha256(identity).hexdigest()[:32]


def _safe_path(path: Path) -> Path:
    path = Path(path).absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        reparse = getattr(current.lstat(), 'st_file_attributes', 0) & 0x400 if current.exists() else 0
        if current.is_symlink() or reparse:
            raise ValueError('repository storage contains a symlink: {}'.format(current))
    return path


def _origin(path: Path) -> str:
    urls = _git(path, 'config', '--get-all', 'remote.origin.url').splitlines()
    if len(urls) != 1:
        raise ValueError('configuration repository requires exactly one origin URL')
    url = urls[0]
    if url.startswith('git@'):
        url = 'https://' + url[len('git@'):].replace(':', '/', 1)
    elif url.startswith('ssh://git@'):
        url = 'https://' + url[len('ssh://git@'):]
    if not url.startswith('https://'):
        raise ValueError('origin must be a credential-free GitHub repository URL')
    identity = validate_repository(url)
    push_urls = _run(('git', '-C', str(path), 'config', '--get-all', 'remote.origin.pushurl'))
    if push_urls.returncode not in (0, 1) or push_urls.stdout.strip():
        raise ValueError('separate origin push URLs are not supported')
    return identity


def _verify(path: Path, branch: str, repository: Optional[str] = None) -> Path:
    path = _safe_path(path)
    if not (path / '.git').is_dir() or (path / '.git').is_symlink():
        raise ValueError('configuration checkout must have its own Git directory')
    if Path(_git(path, 'rev-parse', '--show-toplevel')).resolve() != path.resolve():
        raise ValueError('configuration checkout root changed')
    metadata = path / '.git' / 'smartkit-project-config.json'
    _safe_path(metadata)
    try:
        record = json.loads(metadata.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, UnicodeError) as error:
        raise ValueError('configuration checkout identity record is invalid') from error
    if not isinstance(record, dict):
        raise ValueError('configuration checkout identity record is invalid')
    expected = validate_repository(record.get('repository'))
    if record.get('branch') != branch or (repository is not None and expected.lower() != repository.lower()):
        raise ValueError('configuration checkout binding changed')
    if _origin(path).lower() != expected.lower():
        raise ValueError('configuration repository origin changed')
    if _git(path, 'symbolic-ref', '--quiet', 'HEAD') != 'refs/heads/' + branch:
        raise ValueError('configuration repository branch changed')
    return path


def open_checkout(repository: str, branch: str) -> Path:
    """Read an existing verified checkout without contacting GitHub or changing it."""
    repository = validate_repository(repository)
    branch = validate_branch(branch)
    return _verify(_checkout_path(repository, branch), branch, repository)


def _personal_repository(repository: str, *, create: bool) -> None:
    host, name = _repository_parts(repository)
    user = json.loads(_checked(('gh', 'api', 'user'), host=host))
    owner = name.split('/')[0]
    if not isinstance(user, dict) or not isinstance(user.get('login'), str) or user['login'].lower() != owner.lower():
        raise ValueError('configuration repository must belong to the authenticated personal account')
    result = _run(('gh', 'api', 'repos/' + name), host=host)
    if result.returncode and create and 'HTTP 404' in result.stderr:
        _checked(('gh', 'repo', 'create', name, '--private'), host=host)
        result = _run(('gh', 'api', 'repos/' + name), host=host)
    if result.returncode:
        raise OSError('cannot verify private configuration repository: ' + result.stderr.strip())
    document = json.loads(result.stdout)
    repo_owner = document.get('owner') if isinstance(document, dict) else None
    if (not isinstance(repo_owner, dict) or repo_owner.get('type') != 'User'
            or not isinstance(repo_owner.get('login'), str)
            or repo_owner['login'].lower() != owner.lower()
            or document.get('private') is not True
            or str(document.get('full_name', '')).lower() != name.lower()):
        raise ValueError('configuration repository must be private and owned by the authenticated user')


def checkout(repository: str, branch: str, *, create: bool = False) -> Path:
    """Connect a private personal repo; creation needs the explicit create flag.

    Local changes remain intact when no fast-forward is needed; dirty advancement
    and divergence are refused. Failed clones remain available for inspection.
    """
    repository = validate_repository(repository)
    branch = validate_branch(branch)
    _personal_repository(repository, create=create)
    path = _safe_path(_checkout_path(repository, branch))
    if path.exists():
        _verify(path, branch, repository)
        update(path, branch)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    host, _ = _repository_parts(repository)
    _checked(('gh', 'repo', 'clone', repository, str(path), '--', '--no-checkout'), host=host)
    if _origin(path).lower() != repository.lower():
        raise ValueError('cloned configuration origin does not match its binding')
    existing = _run(('git', '-C', str(path), 'show-ref', '--verify', 'refs/remotes/origin/' + branch))
    if existing.returncode == 0:
        _git(path, 'checkout', '--quiet', branch)
    elif not _git(path, 'ls-remote', '--heads', 'origin', host=host):
        _git(path, 'symbolic-ref', 'HEAD', 'refs/heads/' + branch)
    else:
        raise ValueError('selected configuration branch does not exist in the repository')
    metadata = path / '.git' / 'smartkit-project-config.json'
    metadata.write_text(json.dumps({'repository': repository, 'branch': branch}) + '\n', encoding='utf-8')
    return _verify(path, branch, repository)


def _head(path: Path) -> str:
    result = _run(('git', '-C', str(path), 'rev-parse', '--verify', 'HEAD'))
    if result.returncode == 0:
        return result.stdout.strip()
    if _git(path, 'for-each-ref', '--format=%(refname)', 'refs/heads/'):
        raise OSError('cannot read configuration branch HEAD: ' + result.stderr.strip())
    return ''


def _idle(path: Path) -> None:
    for name in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer'):
        if (path / '.git' / name).exists():
            raise ValueError('configuration checkout has an unfinished Git operation')


def _fetch(path: Path, branch: str) -> str:
    host, _ = _repository_parts(_origin(path))
    ref = 'refs/heads/' + branch
    remote = _git(path, 'ls-remote', '--heads', 'origin', ref, host=host)
    if not remote:
        if _git(path, 'ls-remote', '--heads', 'origin', host=host):
            raise ValueError('selected configuration branch is missing from the remote')
        return ''
    _git(path, 'fetch', '--no-tags', 'origin', ref, host=host)
    return _git(path, 'rev-parse', '--verify', 'FETCH_HEAD^{commit}')


def _ancestor(path: Path, ancestor: str, descendant: str) -> bool:
    result = _run(('git', '-C', str(path), 'merge-base', '--is-ancestor', ancestor, descendant))
    if result.returncode not in (0, 1):
        raise OSError('cannot verify configuration commit ancestry: ' + result.stderr.strip())
    return result.returncode == 0


def update(path: Path, branch: str) -> dict:
    """Verify the remote and fast-forward only when local work permits it.

    Dirty current or locally ahead checkouts are retained without touching their
    index or files. Remote advancement or divergence with local changes is refused
    after fetching, so a caller can distinguish pending local work from stale work.
    """
    branch = validate_branch(branch)
    path = _verify(path, branch)
    _idle(path)
    # Ordinary status may refresh the index; inspection must preserve its exact bytes.
    local_changes = bool(_git(path, '--no-optional-locks', 'status', '--porcelain', '--untracked-files=all'))
    before = _head(path)
    remote = _fetch(path, branch)
    if not remote or before == remote or (before and _ancestor(path, remote, before)):
        return {'commit': before, 'remoteCommit': remote, 'updated': False, 'localChanges': local_changes}
    if local_changes:
        raise ValueError('configuration checkout has local changes and the remote branch requires advancement '
                         'or conflict resolution; local index and files were preserved')
    if before and not _ancestor(path, before, remote):
        raise ValueError('configuration branch diverged; local commits and files were preserved')
    _git(path, 'merge', '--ff-only', remote)
    after = _head(path)
    if after != remote:
        raise ValueError('configuration fast-forward did not reach the fetched commit')
    local_changes = bool(_git(path, '--no-optional-locks', 'status', '--porcelain', '--untracked-files=all'))
    return {'commit': after, 'remoteCommit': remote, 'updated': after != before, 'localChanges': local_changes}


def _paths(path: Path, paths: Sequence[str]) -> list:
    if isinstance(paths, (str, bytes)) or not paths:
        raise ValueError('commit scope requires exact relative file paths')
    selected = []
    for value in paths:
        if (not isinstance(value, str) or not value or value.startswith(('/', '-', ':'))
                or any(character in value for character in '\\:<>\"|?*')
                or any(ord(c) < 32 or ord(c) == 127 for c in value)
                or any(part in ('', '.', '..') or part.lower() == '.git' or part.endswith((' ', '.'))
                       or re.fullmatch(r'(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part, re.IGNORECASE)
                       for part in value.split('/'))):
            raise ValueError('commit scope contains an unsafe relative file path')
        target = _safe_path(path / value)
        if target.is_dir() or (target.exists() and not target.is_file()):
            raise ValueError('commit scope must name individual regular files')
        selected.append(value)
    return sorted(set(selected))


def _commit_record(path: Path, commit: str, branch: str, selected: Sequence[str], parent: str) -> dict:
    lineage = _git(path, 'rev-list', '--parents', '-n', '1', commit).split()
    expected = [commit, parent] if parent else [commit]
    changed = set(filter(None, _git(path, 'diff-tree', '--root', '--no-commit-id', '--no-renames', '--name-only', '-r', '-z', commit).split('\0')))
    if lineage != expected or not changed or not changed.issubset(selected):
        raise ValueError('created commit exceeded the selected scope; local commit preserved, publication refused')
    for value in changed:
        entry = _git(path, 'ls-tree', commit, '--', ':(literal)' + value)
        if entry and not entry.startswith(('100644 ', '100755 ')):
            raise ValueError('commit scope contains a symlink or non-file Git object')
    return {'commit': commit, 'parent': parent, 'branch': branch, 'paths': list(selected)}


def commit_scope(path: Path, branch: str, paths: Sequence[str], message: str) -> str:
    """Commit exact caller-owned file edits without including unrelated index entries.

    The caller must establish ownership of unstaged selected-path edits before
    writing them. Preexisting staged selections are ambiguous and refused. Hooks
    run normally; a failed post-hook scope check preserves the commit but creates
    no publication receipt. The caller must revalidate applied source after hooks.
    """
    branch = validate_branch(branch)
    path = _verify(path, branch)
    _idle(path)
    selected = _paths(path, paths)
    if not isinstance(message, str) or not message.strip() or '\0' in message:
        raise ValueError('commit message must be nonempty text')
    specs = [':(literal)' + value for value in selected]
    if _git(path, 'diff', '--cached', '--name-only', '-z', '--', *specs):
        raise ValueError('selected paths already contain staged work; commit scope is ambiguous')
    parent = _head(path)
    _git(path, 'add', '--', *specs)
    _git(path, 'commit', '--only', '--message', message, '--', *specs)
    commit = _head(path)
    _verify(path, branch)
    _paths(path, selected)
    record = _commit_record(path, commit, branch, selected, parent)
    receipt = _safe_path(path / '.git' / 'smartkit-project-config-commits' / (commit + '.json'))
    receipt.parent.mkdir(exist_ok=True)
    receipt.write_text(json.dumps(record, sort_keys=True) + '\n', encoding='utf-8')
    return commit


def _check_receipt(path: Path, branch: str, commit: str) -> None:
    receipt = _safe_path(path / '.git' / 'smartkit-project-config-commits' / (commit + '.json'))
    try:
        record = json.loads(receipt.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeError) as error:
        raise ValueError('outgoing commit lacks a verified scope receipt; publication refused') from error
    if (not isinstance(record, dict) or record.get('commit') != commit
            or record.get('branch') != branch or not isinstance(record.get('parent'), str)
            or not isinstance(record.get('paths'), list)):
        raise ValueError('outgoing commit scope receipt is invalid')
    selected = _paths(path, record['paths'])
    _commit_record(path, commit, branch, selected, record['parent'])
    specs = [':(literal)' + value for value in selected]
    if _git(path, 'status', '--porcelain', '--untracked-files=all', '--', *specs):
        raise ValueError('selected configuration files have uncommitted changes after verification')


def _check_outgoing(path: Path, commit: str, remote: str) -> None:
    revision = remote + '..' + commit if remote else commit
    outgoing = _git(path, 'rev-list', '--reverse', revision).splitlines()
    extra = [candidate for candidate in outgoing if candidate != commit]
    if extra:
        details = []
        for candidate in extra:
            changed = _git(path, 'diff-tree', '--root', '-m', '--no-commit-id', '--no-renames',
                           '--name-only', '-r', '-z', candidate).split('\0')
            details.append('{} {}'.format(candidate, json.dumps(sorted(set(filter(None, changed))), ensure_ascii=False)))
        raise ValueError('additional outgoing commits are outside this publish request; '
                         'resolve explicitly before retrying: ' + '; '.join(details))
    if outgoing != [commit]:
        raise ValueError('the requested commit is not the sole outgoing configuration commit')


def publish(path: Path, branch: str, commit: str) -> dict:
    """Normally push one explicitly selected commit and confirm remote reachability.

    The named commit needs a locally recorded, rechecked scope receipt and must
    be the only outgoing commit. Earlier receipts prove provenance, not this
    request's publication authority; extra commits require explicit resolution.
    Repeating this operation first inspects the remote, so that same retained
    commit can be retried after rejection or an uncertain transport result.
    Failures retain local commits and applied files and never authorize force push.
    """
    branch = validate_branch(branch)
    path = _verify(path, branch)
    _idle(path)
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}(?:[0-9a-f]{24})?', commit):
        raise ValueError('publish requires a full commit object ID')
    if _head(path) != commit:
        raise ValueError('configuration HEAD changed after the caller verified its source')
    _check_receipt(path, branch, commit)
    _personal_repository(_origin(path), create=False)
    remote = _fetch(path, branch)
    if remote and _ancestor(path, commit, remote):
        return {'commit': commit, 'remoteCommit': remote, 'published': True}
    if remote and not _ancestor(path, remote, commit):
        raise ValueError('remote configuration branch advanced or diverged; local commit preserved')
    _check_outgoing(path, commit, remote)
    _verify(path, branch)
    if _head(path) != commit:
        raise ValueError('configuration HEAD changed before publication')
    host, _ = _repository_parts(_origin(path))
    _git(path, '-c', 'push.followTags=false', '-c', 'remote.origin.mirror=false',
         'push', '--no-follow-tags', '--recurse-submodules=no', 'origin', commit + ':refs/heads/' + branch, host=host)
    remote = _fetch(path, branch)
    if not remote or not _ancestor(path, commit, remote):
        raise ValueError('push returned success but the configuration commit is not verified on the remote')
    return {'commit': commit, 'remoteCommit': remote, 'published': True}
