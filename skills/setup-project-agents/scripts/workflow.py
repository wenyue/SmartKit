from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

import bootstrap
from agents_setup.external_contract import is_link_like as _is_link_like
from agents_setup.markdown import live_headings
from agents_setup.catalog import load_catalog
from agents_setup.generation import generation_requests
from agents_setup.project_sync import ProjectSyncError, synchronize_project
from agents_setup.ownership import OwnershipError, normalize_external_sources
from agents_setup.project_rules import ProjectRuleSyncError, synchronize_project_rules
from agents_setup.source import InvalidFetchedSource, setup_entrypoint


_SESSION_PREFIX = 'setup-project-agents-'
_SESSION_MARKER = '.workflow-session'
_SESSION_MARKER_CONTENT = b'setup-project-agents-workflow-v1\n'
_SESSION_CLAIM = '.workflow-claim'
_SESSION_CLAIM_CONTENT = b'setup-project-agents-workflow-claim-v1\n'
_WORKFLOW_CONTEXT = 'workflow.json'
_COMMIT = re.compile(r'^[0-9a-fA-F]{40}$')
_MATT_CONTEXT_PATHS = (
    Path('docs/agents/issue-tracker.md'),
    Path('docs/agents/triage-labels.md'),
    Path('docs/agents/domain.md'),
)
_MATT_ENTRY_PATHS = (Path('AGENTS.md'), Path('CLAUDE.md'))


class WorkflowError(ValueError):
    """Raised when the public two-stage setup workflow cannot continue safely."""


def _write_exclusive(path: Path, content: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        view = memoryview(content)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
    finally:
        os.close(descriptor)


def _create_session() -> Path:
    session = Path(tempfile.mkdtemp(prefix=_SESSION_PREFIX)).absolute()
    try:
        if os.name == 'posix':
            session.chmod(0o700)
        _write_exclusive(session / _SESSION_MARKER, _SESSION_MARKER_CONTENT)
        return session
    except BaseException:
        shutil.rmtree(session, ignore_errors=True)
        raise


def _owned_session(value: Path) -> Path:
    session = Path(value).absolute()
    temporary_root = Path(tempfile.gettempdir()).absolute()
    if session.parent != temporary_root or not session.name.startswith(_SESSION_PREFIX):
        raise WorkflowError('session is not a workflow-owned system-temporary directory')
    current = Path(session.anchor)
    for part in session.parts[1:]:
        current /= part
        try:
            status = current.lstat()
        except OSError as error:
            raise WorkflowError(f'session path cannot be inspected: {current}') from error
        if stat.S_ISLNK(status.st_mode) or _is_link_like(current):
            raise WorkflowError(f'session path contains an unsafe link: {current}')
    status = session.stat()
    if not stat.S_ISDIR(status.st_mode):
        raise WorkflowError('session is not a directory')
    if os.name == 'posix' and (
        status.st_uid != os.geteuid() or stat.S_IMODE(status.st_mode) != 0o700
    ):
        raise WorkflowError('session must be private, exact mode 0700, and current-user-owned')
    marker = session / _SESSION_MARKER
    if _is_link_like(marker) or not marker.is_file():
        raise WorkflowError('session ownership marker is missing or unsafe')
    try:
        content = marker.read_bytes()
    except OSError as error:
        raise WorkflowError('session ownership marker cannot be read') from error
    if content != _SESSION_MARKER_CONTENT:
        raise WorkflowError('session ownership marker is invalid')
    return session


def _clear_readonly_files(root: Path) -> None:
    for directory, directories, files in os.walk(root, topdown=True, followlinks=False):
        parent = Path(directory)
        directories[:] = [
            name for name in directories if not _is_link_like(parent / name)
        ]
        for name in files:
            path = parent / name
            if not _is_link_like(path):
                path.chmod(stat.S_IREAD | stat.S_IWRITE)


def _remove_session(session: Path) -> None:
    owned = _owned_session(session)
    try:
        _clear_readonly_files(owned)
        shutil.rmtree(owned)
    except OSError as error:
        raise WorkflowError(f'cannot remove workflow session: {owned}') from error
    if owned.exists():
        raise WorkflowError(f'workflow session still exists after cleanup: {owned}')


def _claim_session(session: Path) -> Path:
    owned = _owned_session(session)
    try:
        _write_exclusive(owned / _SESSION_CLAIM, _SESSION_CLAIM_CONTENT)
    except FileExistsError as error:
        raise WorkflowError(
            f'workflow session is already claimed: {owned}'
        ) from error
    except OSError as error:
        raise WorkflowError(f'cannot claim workflow session: {owned}') from error
    return owned


def _read_json(path: Path, label: str) -> Mapping[str, object]:
    if _is_link_like(path) or not path.is_file():
        raise WorkflowError(f'{label} must be a regular file')
    try:
        document = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WorkflowError(f'cannot read {label}') from error
    if not isinstance(document, Mapping):
        raise WorkflowError(f'{label} must be a JSON object')
    return document


def _write_workflow_context(session: Path, request_path: Path, request: Mapping[str, object]) -> None:
    context = {
        'target': request.get('target'),
        'source_root': request.get('source_root'),
        'source_commit': request.get('source_commit'),
        'request_sha256': hashlib.sha256(request_path.read_bytes()).hexdigest(),
    }
    content = (json.dumps(context, sort_keys=True, indent=2) + '\n').encode()
    try:
        _write_exclusive(session / _WORKFLOW_CONTEXT, content)
    except FileExistsError as error:
        raise WorkflowError('workflow context already exists') from error


def _emit(document: Mapping[str, object]) -> None:
    print(json.dumps(document, sort_keys=True))


def _agent_skills_section(content: str) -> str | None:
    headings = live_headings(content)
    for index, heading in enumerate(headings):
        if heading.level != 2 or heading.title != 'Agent skills':
            continue
        end = next(
            (
                item.start
                for item in headings[index + 1:]
                if item.level <= heading.level
            ),
            len(content),
        )
        return content[heading.body_start:end]
    return None


def _require_matt_context(target: Path) -> None:
    context_paths = tuple(target / relative for relative in _MATT_CONTEXT_PATHS)
    if any(_is_link_like(path) or not path.is_file() for path in context_paths):
        raise WorkflowError(
            'Matt repository setup is incomplete; explicitly invoke '
            'setup-matt-pocock-skills before setup-project-agents'
        )
    references = tuple(relative.as_posix() for relative in _MATT_CONTEXT_PATHS)
    for relative in _MATT_ENTRY_PATHS:
        path = target / relative
        if _is_link_like(path) or not path.is_file():
            continue
        try:
            content = path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        section = _agent_skills_section(content)
        if section is not None and all(reference in section for reference in references):
            return
    raise WorkflowError(
        'Matt repository setup is incomplete; explicitly invoke '
        'setup-matt-pocock-skills before setup-project-agents'
    )


def _start(args: argparse.Namespace) -> int:
    target = Path(args.target).absolute()
    try:
        _require_matt_context(target)
    except (OSError, WorkflowError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    session = _create_session()
    try:
        forwarded = [
            'prepare', '--target', str(target),
            '--session', str(session),
        ]
        result = bootstrap.main(forwarded)
        if result != 0:
            _remove_session(session)
            return result
        request_path = session / 'request.json'
        request = _read_json(request_path, 'session request')
        _write_workflow_context(session, request_path, request)
        _, _, source, _ = _request_context(session)
        expected = generation_requests(source, target, load_catalog(source), None)
        if request.get('generation_requests') != expected:
            raise WorkflowError(
                'pinned setup source did not request the complete current generated set; '
                'update the source implementation before full setup'
            )
        _emit({
            'phase': 'start',
            'session': str(session),
            'request': str(request_path),
            'generated': str(session / 'generated'),
            'source_root': request.get('source_root'),
            'source_commit': request.get('source_commit'),
            'source_fingerprint': request.get('source_fingerprint'),
            'harnesses': request.get('harnesses'),
            'generation_requests': request.get('generation_requests'),
        })
        return 0
    except BaseException as error:
        try:
            if session.exists():
                _remove_session(session)
        except BaseException as cleanup_error:
            print(f'ERROR: {error}; session cleanup failed: {cleanup_error}', file=sys.stderr)
            return 2
        if isinstance(error, (OSError, ValueError)):
            print(f'ERROR: {error}', file=sys.stderr)
            return 2
        raise


def _request_context(session: Path) -> tuple[Mapping[str, object], Path, Path, str]:
    request_path = session / 'request.json'
    request = _read_json(request_path, 'session request')
    context = _read_json(session / _WORKFLOW_CONTEXT, 'workflow context')
    if set(context) != {
        'target', 'source_root', 'source_commit', 'request_sha256'
    }:
        raise WorkflowError('workflow context has an invalid shape')
    try:
        request_digest = hashlib.sha256(request_path.read_bytes()).hexdigest()
    except OSError as error:
        raise WorkflowError('session request cannot be verified') from error
    if context.get('request_sha256') != request_digest:
        raise WorkflowError('session request changed after start')
    target_value = context.get('target')
    source_value = context.get('source_root')
    commit_value = context.get('source_commit')
    if any(
        request.get(key) != context.get(key)
        for key in ('target', 'source_root', 'source_commit')
    ):
        raise WorkflowError('session request differs from workflow context')
    if not isinstance(target_value, str) or not isinstance(source_value, str):
        raise WorkflowError('session request target or source root is invalid')
    target = Path(target_value).absolute()
    source = Path(source_value).absolute()
    if commit_value is None:
        commit = 'offline'
        expected_source = Path(__file__).resolve().parents[3]
    elif isinstance(commit_value, str) and _COMMIT.fullmatch(commit_value):
        commit = commit_value.lower()
        expected_source = session / 'source'
    else:
        raise WorkflowError('session request source commit is invalid')
    if os.path.normcase(str(source)) != os.path.normcase(str(expected_source.absolute())):
        raise WorkflowError('session request source root is outside the pinned workflow boundary')
    return request, target, source, commit


def _run_pinned(
    phase: str,
    *,
    session: Path,
    target: Path,
    source: Path,
    commit: str,
    extra_args: Sequence[str] = (),
) -> Mapping[str, object]:
    try:
        entrypoint = setup_entrypoint(source)
    except InvalidFetchedSource as error:
        raise WorkflowError(f'pinned setup source is invalid: {error}') from error
    command = (
        sys.executable,
        str(entrypoint),
        phase,
        '--target', str(target),
        '--session', str(session),
        '--source-root', str(source),
        '--source-commit', commit,
        '--no-bootstrap',
        *extra_args,
    )
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as error:
        raise WorkflowError(f'cannot execute pinned {phase}') from error
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end='')
    if completed.returncode != 0:
        raise WorkflowError(f'pinned {phase} failed with status {completed.returncode}')
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise WorkflowError(f'pinned {phase} returned invalid JSON') from error
    if not isinstance(result, Mapping) or result.get('phase') != phase:
        raise WorkflowError(f'pinned {phase} returned an invalid result')
    normalized = dict(result)
    if phase == 'register':
        return normalized
    try:
        external_sources = list(normalize_external_sources(
            result.get('external_sources'),
            label='pinned result external sources',
        ))
    except OwnershipError as error:
        raise WorkflowError('pinned result external sources are invalid') from error
    external_skills = result.get('external_skills')
    if (
        not isinstance(external_skills, list)
        or not all(isinstance(item, str) and item for item in external_skills)
        or len(external_skills) != len(set(external_skills))
        or sorted(external_skills) != sorted(
            str(skill['id']).rsplit('/', 1)[-1]
            for source in external_sources
            for skill in source['skills']
        )
    ):
        raise WorkflowError('pinned result external Skill provenance is invalid')
    normalized['external_skills'] = list(external_skills)
    normalized['external_sources'] = external_sources
    return normalized


def _register(args: argparse.Namespace) -> int:
    try:
        session = _claim_session(args.session)
    except WorkflowError as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    result = None
    status = 0
    try:
        _, target, source, commit = _request_context(session)
        outputs = tuple(value for path in args.output for value in ('--output', path))
        result = _run_pinned(
            'register', session=session, target=target, source=source, commit=commit,
            extra_args=('--request-id', args.request_id, *outputs),
        )
    except (OSError, WorkflowError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        status = 2
    finally:
        try:
            (session / _SESSION_CLAIM).unlink()
        except OSError as error:
            print(f'ERROR: cannot release registration claim in {session}: {error}', file=sys.stderr)
            status = 2
    if status == 0:
        assert result is not None
        _emit(result)
    return status


def _finish(args: argparse.Namespace) -> int:
    try:
        session = _claim_session(args.session)
    except WorkflowError as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    try:
        request, target, source, commit = _request_context(session)
        finish_result = _run_pinned(
            'finish', session=session, target=target, source=source, commit=commit
        )
        result = {
            'phase': 'finish',
            'source_commit': request.get('source_commit'),
            'source_fingerprint': request.get('source_fingerprint'),
            'source_root': request.get('source_root'),
            'source_mode': (
                'installed-fallback'
                if request.get('source_commit') is None
                else 'canonical-snapshot'
            ),
            'harnesses': request.get('harnesses'),
            'changed_paths': finish_result.get('changed_paths'),
            'external_skills': finish_result.get('external_skills'),
            'external_sources': finish_result.get('external_sources'),
            'preserved_paths': finish_result.get('preserved_paths'),
            'check': 'clean',
        }
        _remove_session(session)
        _emit(result)
        return 0
    except BaseException as error:
        try:
            if session.exists():
                _remove_session(session)
        except BaseException as cleanup_error:
            print(f'ERROR: {error}; session cleanup failed: {cleanup_error}', file=sys.stderr)
            return 2
        if isinstance(error, (OSError, ValueError)):
            print(f'ERROR: {error}', file=sys.stderr)
            return 2
        raise


def _cancel(args: argparse.Namespace) -> int:
    try:
        session = _claim_session(args.session)
        _remove_session(session)
        _emit({'phase': 'cancel', 'cancelled': True})
        return 0
    except (OSError, WorkflowError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2


def _sync_project_rules(args: argparse.Namespace) -> int:
    source = Path(__file__).resolve().parents[3]
    target = Path(args.target).absolute()
    try:
        result = synchronize_project_rules(
            source,
            target,
            check_only=args.check,
        )
    except ProjectRuleSyncError as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    _emit({
        'phase': 'sync-project-rules',
        'check': result.check,
        'changed_paths': result.changed_paths,
    })
    return 1 if result.check == 'drift' else 0


def _sync_project(args: argparse.Namespace) -> int:
    try:
        result = synchronize_project(
            Path(__file__).resolve().parents[3], Path(args.target).absolute(), check_only=args.check,
        )
    except ProjectSyncError as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    _emit({
        'phase': 'sync-project', 'check': result.check,
        'changed_paths': result.changed_paths, 'preserved_paths': result.preserved_paths,
    })
    return 1 if result.check == 'drift' else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Run full setup (start/register/finish/cancel), or explicit local synchronization.',
        allow_abbrev=False,
    )
    phases = parser.add_subparsers(dest='phase', required=True)
    start = phases.add_parser('start', help='Start full setup; request every current generated contract', allow_abbrev=False)
    start.add_argument('--target', type=Path, required=True)
    register = phases.add_parser('register', allow_abbrev=False)
    register.add_argument('--session', type=Path, required=True)
    register.add_argument('--request-id', required=True)
    register.add_argument('--output', action='append', required=True)
    finish = phases.add_parser('finish', allow_abbrev=False)
    finish.add_argument('--session', type=Path, required=True)
    cancel = phases.add_parser('cancel', allow_abbrev=False)
    cancel.add_argument('--session', type=Path, required=True)
    sync_project = phases.add_parser('sync-project', help='Synchronize only local project discovery and Agent/MCP mappings; no fetch or generation', allow_abbrev=False)
    sync_project.add_argument('--target', type=Path, required=True)
    sync_project.add_argument('--check', action='store_true', help='Report drift without writing (exit 1); clean exits 0, errors exit 2')
    sync_project_rules = phases.add_parser('sync-project-rules', help='Synchronize only AGENTS.md Project rules; no setup ownership required', allow_abbrev=False)
    sync_project_rules.add_argument('--target', type=Path, required=True)
    sync_project_rules.add_argument('--check', action='store_true')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    if args.phase == 'start':
        return _start(args)
    if args.phase == 'register':
        return _register(args)
    if args.phase == 'finish':
        return _finish(args)
    if args.phase == 'sync-project':
        return _sync_project(args)
    if args.phase == 'sync-project-rules':
        return _sync_project_rules(args)
    return _cancel(args)


if __name__ == '__main__':
    raise SystemExit(main())
