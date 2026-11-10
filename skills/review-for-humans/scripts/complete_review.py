#!/usr/bin/env python
"""Freeze and resume authorized PR completion; full evidence stays in private state."""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import tempfile
from typing import Iterator, Optional
from urllib.parse import quote


CLI_HELP = r"""
SUPPORTED PLANS
  A verified github.com PR on its selected local branch, with one effect mode.
  viewed-only records Viewed. commit-push creates a commit when content changed,
  reuses existing outgoing commits, publishes when needed, then records Viewed.
  amend-push amends the review-owned tip when its content or message changed,
  preserves its parents, publishes the complete outgoing scope, then records Viewed.
  The caller must establish that amendment belongs to this review. Both local
  and source branches must be outside master/main for amend-push.
  All modes require a nonempty viewed_paths set whose paths already exist in the PR
  before publication. An empty set or an eligible file entering the PR only after
  the push needs the Skill's manual delivery workflow. Never omit a required path
  or invent one to fit this helper.

  Mirrored push remotes, detached workspaces, unresolved Git operations, special
  index flags, and changed submodule/directory entries need the manual workflow.
  Requires Python 3.8+, Git, authenticated gh with PR/source access and readbacks,
  and prepared source objects. All gh API calls target github.com. The helper does
  not install tools, fetch, synchronize, or select a workspace.

CALLER CONTRACT
  The Skill entry owns user intent and review progression; references/delivery.md
  owns full-workspace/outgoing scope, semantic coverage, checks, authorization,
  and completion. Read those owners before using this mechanical interface.
  Supply the complete eligible Viewed set and stable absolute evidence files
  outside the worktree supporting readiness, current-conversation review of all
  non-test delivery changes, disclosed effects, and authorization. Evidence hashes
  bind bytes, not meaning: this tool cannot establish semantic review. A plan_id
  identifies frozen effects and grants no permission.

REQUEST JSON (--input)
  {
    "repository": "/absolute/selected-worktree",
    "branch": "review-branch",
    "pull_request": "owner/repository",
    "number": 123,
    "base": "1111111111111111111111111111111111111111",
    "head": "2222222222222222222222222222222222222222",
    "viewer": "reviewer-login",
    "viewed_paths": ["src/feature.py"],
    "mode": "commit-push",
    "remote": "origin",
    "message": "Fix reviewed behavior",
    "evidence": ["/absolute/private/review-and-checks.json"]
  }
  Use the exact local branch and full lowercase 40-hex commit IDs. number is a
  positive PR number; pull_request is the PR owner's owner/repository slug.
  GitHub supplies the verified source repository/ref, including forks. viewer
  must match the reviewed authenticated identity. viewed_paths is a nonempty
  unique list of repository-relative forward-slash paths; evidence is a nonempty
  list of existing files. Unrecognized fields are rejected.

  For viewed-only, omit remote/message. Only this mode requires local HEAD to
  equal the reviewed PR head. Publication modes permit verified outgoing descendants.
  viewed-only freezes/preserves local differences mechanically, but the delivery
  contract permits it only when no commit/publication effect remains.
  For either publication mode, supply remote and message. The actual destination
  must be the verified source ref, including when fetch and push URLs differ.
  amend-push includes the retained tip content in the disclosed/reviewed scope.

PRIVATE STATE AND EVIDENCE
  Choose a new state directory outside the worktree through the owning artifact
  lifecycle. Retain it unpublished as the recovery evidence. Creation uses
  owner-only POSIX permissions; on Windows choose an account-private directory
  with suitable inherited access.

  prepare retains the plan, original index bytes, tracked binary diffs, changed
  file bytes/symlink targets, intended complete tree, outgoing ancestry/delta,
  full PR pagination, expected commit parents, and evidence digests. Plans use
  private version 2. Obsolete versions are rejected without migration. Preparation
  and source-ref readbacks use gh rather than native Git network access.
  Publication preparation uses an isolated index/native clean filters and may add Git objects, while verifying
  the real index, branch, HEAD, and contents remain unchanged. Inspect the full
  inventory and logs for scope disclosure; compact counts are insufficient.

COMMANDS
  Resolve <skill-root> from the actual loaded Skill, not the target cwd.
  python "<skill-root>/scripts/complete_review.py" prepare --input "/private/request.json" --state "/private/completion-state"
  python "<skill-root>/scripts/complete_review.py" run --state "/private/completion-state" --confirm "<plan_id>"

  After exact-effect authorization, run locks and revalidates the plan, stages
  intended content when needed, runs normal hooks, and verifies tree/parent,
  outgoing ancestry, and source destination. It publishes only while the source
  ref matches the frozen old SHA, without automatic tag/submodule publication.
  It verifies source ref, PR
  version and published commit/tree, then marks remaining paths and reads back
  the entire selected set with unchanged PR version. Confirmed effects are reused
  and no redundant commit is created. No review advancement occurs.

TRANSPORT (--transport ON run)
  git (default) uses native Git publication with an exact-SHA force-with-lease.
  Only amend-push may replace a published tip. Both modes verify frozen outgoing
  ancestry before publication. Normal commit and publication hooks run.

  github-api uses gh Git Data calls to upload the missing outgoing object closure,
  checks every resulting SHA, and atomically updates the source ref with beforeOid.
  It runs the applicable pre-push hook through git hook run with the same remote,
  URL and OID:refspec stdin as the native route. An active hook requires Git 2.43+
  with --to-stdin support. Older Git is supported when no pre-push hook is active.
  API commit messages, identities and tree paths must be UTF-8. Commit headers
  must be ordinary tree/parent/author/committer headers. Signatures, extra headers, and any API-normalized object identity stop
  before ref update. Use git transport for such objects. Native commit signing
  and hooks remain enabled. Object uploads may remain unreachable after failure.

  Example API execution or recovery on blocked native Git endpoints
  python "<skill-root>/scripts/complete_review.py" run --state "/private/completion-state" --confirm "<plan_id>" --transport github-api

  Transport is an execution choice, outside the frozen plan. Change it on resume
  only within the same authorized effects and method restrictions. There is no
  automatic fallback. The helper first reconciles actual source/PR state, reuses
  confirmed publication, and uploads or publishes only missing work.

VIEWED RETRIES AND BACKGROUND WORK
  Complete PR snapshots (including initial preparation/revalidation) and the
  Viewed recording/readback batch each allow at most five attempts within 180
  seconds. Each Viewed-related gh request has a 30-second timeout, shortened to
  the remaining batch budget. Transient network, timeout, server and rate-limit
  failures retry; ordinary backoff is 1/2/4/8 seconds. Retry-After and primary
  reset times are minimum waits; rate-limit waits grow exponentially. A rate
  limit without timing waits at least 60 seconds. A wait that cannot fit the
  deadline leaves the operation incomplete instead of retrying early.
  Authentication, invalid responses, changed identity/version/content/evidence,
  and other permanent failures stop. Every recording retry first reads the
  complete actual Viewed state, checks the frozen identity/version, and skips
  VIEWED paths, including a write whose response was lost. Only the Viewed
  requests receive automatic retries; commit, push, object uploads and source-ref
  mutations retain the explicit recovery route below.

  phase=viewed in progress.json, with its resulting head, means local/publication
  prerequisites are verified and only recording/readback remains. The operation
  lock protects this helper, not external workspace/evidence edits. Follow
  Delivery for concurrent review, managed-session lifetime, and status collection.

OUTPUT AND EXIT STATUS
  Stdout is compact JSON with status, version/counts, plan/progress paths, and
  private logs. Status is prepared or complete on success, incomplete on a caught
  failure, or interrupted on KeyboardInterrupt. Every Git/gh subprocess retains
  arguments, identity, stdout/stderr, exit status, and duration in private logs.
  Exit 0: requested command succeeded (prepare froze a plan; run completed all
  required effects/readbacks). Exit 1: incomplete. Exit 2: CLI usage error.
  Exit 130: interrupted. Inspect failures and residue; no automatic rollback.

RECOVERY
  After an interrupted run or lost response, inspect retained evidence and run
  the same command with the same state and plan_id. It inspects actual effects
  and resumes only missing work, including partial Viewed. Native locks release
  on process exit; after a post-spawn failure the parent waits for its owned
  Git/gh child to stop before releasing the lock.

  Changed content, branch, evidence, viewer, source, base/head, publication scope,
  or detected hook changes stop dependent effects. Preserve state; settle the
  inventory, checks, re-review, and consent through the Skill entry and Delivery.
  Prepare a new plan only for settled changed effects. Failed preparation retains
  private diagnostics. Missing readbacks or uncertain subprocess state remain
  incomplete: do not delete locks, reset, retry speculative writes, or treat a
  failed run as completed delivery.
"""

PREPARE_HELP = """Freeze exact effects and private recovery evidence without committing, pushing,
or marking Viewed. Read the top-level --help for supported plans and the request
JSON contract. --state must be a new private directory outside the worktree.
Preparation can write private evidence and Git objects; it verifies that the real
index, branch, HEAD, and worktree contents remain unchanged. Inspect the full
inventory/logs before disclosing the plan; a returned plan_id is not permission."""

RUN_HELP = """Execute or resume a prepared plan only after its exact effects are authorized.
Use the same private --state and frozen --confirm plan_id. Revalidation precedes
effects; actual completed effects are inspected before reuse. The top-level
--help describes capabilities, outputs, and recovery. Exit 0 means all required
run effects and readbacks completed; failures remain incomplete and preserve
recovery evidence. This command never advances the human review."""


SHA = re.compile(r'[0-9a-f]{40}')
SLUG = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')
GIT_ROUTING = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
               'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
               'GIT_PREFIX', 'GIT_NAMESPACE', 'GIT_CONFIG', 'GIT_CONFIG_COUNT')
PR_QUERY = '''query($owner:String!,$name:String!,$number:Int!,$cursor:String){
 viewer{login} repository(owner:$owner,name:$name){pullRequest(number:$number){
 id baseRefOid headRefOid headRefName headRepository{id nameWithOwner}
 files(first:100,after:$cursor){totalCount nodes{path viewerViewedState}
 pageInfo{hasNextPage endCursor}}}}}'''
UPDATE_QUERY = '''mutation($input:UpdateRefsInput!){updateRefs(input:$input){clientMutationId}}'''
MARK_QUERY = '''mutation($id:ID!,$path:String!){markFileAsViewed(input:{
 pullRequestId:$id,path:$path}){pullRequest{baseRefOid headRefOid}}}'''


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + '\n').encode('utf-8')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_bytes(encoded(value))
    temporary.chmod(0o600)
    os.replace(str(temporary), str(path))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding='utf-8'))
    require(isinstance(value, dict), 'Expected a JSON object: ' + str(path))
    return value


@contextmanager
def operation_lock(state: Path) -> Iterator[None]:
    """Native locks release on process exit, including an interrupted writer."""
    with (state / 'operation.lock').open('a+b') as stream:
        if os.name == 'nt':
            import msvcrt
            stream.write(b'\0')
            stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


class CommandFailure(RuntimeError):
    """Retain failed command evidence for the owning integration boundary."""

    def __init__(self, arguments: list[str], code: int, prefix: Path) -> None:
        super().__init__('%s exited %s; see %s' % (arguments[0], code, prefix))
        self.output = prefix.with_suffix('.stdout').read_bytes()
        self.stderr = prefix.with_suffix('.stderr').read_bytes()


class ViewedRequestFailure(RuntimeError):
    """A transient Viewed request may be retried after its minimum wait."""

    def __init__(self, delay: float = 0) -> None:
        super().__init__('Transient GitHub Viewed request failure; inspect private logs')
        self.delay = delay


def viewed_timeout(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    require(remaining > 0, 'Viewed batch exceeded its 180-second deadline; resume the same state')
    return min(30, remaining)


def pause_viewed(error: ViewedRequestFailure, attempt: int, deadline: float) -> None:
    # Server timing is a minimum; repeated rate limits also receive exponential backoff.
    delay = max(1, error.delay) * (2 ** attempt)
    if attempt == 4 or time.monotonic() + delay >= deadline:
        raise RuntimeError('Viewed retry budget exhausted; resume the same state') from error
    time.sleep(delay)


class Commands:
    """Own raw subprocess evidence without sending it through the Agent context."""

    def __init__(self, repository: Path, state: Path) -> None:
        self.repository = repository
        self.logs = state / 'logs'
        self.logs.mkdir(exist_ok=True, mode=0o700)
        self.environment = dict(os.environ)
        for key in list(self.environment):
            if key in GIT_ROUTING or key.startswith(('GIT_CONFIG_KEY_', 'GIT_CONFIG_VALUE_')):
                self.environment.pop(key)
        self.environment['GIT_OPTIONAL_LOCKS'] = '0'

    def call(self, arguments: list[str], *, input_value: Optional[dict] = None,
             environment: Optional[dict[str, str]] = None, allow_failure: bool = False,
             timeout: Optional[float] = None) -> bytes:
        descriptor, name = tempfile.mkstemp(prefix='command-', suffix='.command.json', dir=str(self.logs))
        os.close(descriptor)
        prefix = Path(name[:-len('.command.json')])
        metadata = {'arguments': arguments, 'cwd': str(self.repository)}
        write_json(prefix.with_suffix('.command.json'), metadata)
        input_bytes = encoded(input_value) if input_value is not None else None
        if input_bytes is not None:
            prefix.with_suffix('.input.json').write_bytes(input_bytes)
        with prefix.with_suffix('.stdout').open('wb') as output, prefix.with_suffix('.stderr').open('wb') as error:
            started = time.monotonic()
            process = subprocess.Popen(arguments, cwd=str(self.repository),
                                       env=dict(self.environment, **(environment or {})),
                                       stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                                       stdout=output, stderr=error)
            try:
                metadata['pid'] = process.pid
                write_json(prefix.with_suffix('.command.json'), metadata)
                try:
                    process.communicate(input_bytes, timeout=timeout)
                except subprocess.TimeoutExpired:
                    metadata['timed_out'] = True
                    process.kill()
                    process.communicate()
                    raise
            finally:
                # Every post-spawn exit retains ownership until the child stops, including log failures.
                try:
                    if process.stdin is not None and not process.stdin.closed:
                        process.stdin.close()
                finally:
                    process.wait()
                metadata.update(exit_code=process.returncode, elapsed_seconds=time.monotonic() - started)
                write_json(prefix.with_suffix('.command.json'), metadata)
        if process.returncode and not allow_failure:
            raise CommandFailure(arguments, process.returncode, prefix)
        return prefix.with_suffix('.stdout').read_bytes()

    def git(self, *arguments: str, **options: object) -> bytes:
        return self.call(['git', '-C', str(self.repository)] + list(arguments), **options)

    def graphql(self, query: str, variables: dict, *, timeout: Optional[float] = None) -> dict:
        viewed = query in (PR_QUERY, MARK_QUERY)
        arguments = ['gh', 'api', 'graphql', '--hostname', 'github.com', '--input', '-']
        if viewed:
            arguments.append('--include')
        failure = None
        try:
            raw = self.call(arguments, input_value={'query': query, 'variables': variables}, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            if not viewed:
                raise
            raise ViewedRequestFailure() from error
        except CommandFailure as error:
            if not viewed:
                raise
            failure = error
            raw = error.output
        status = None
        headers = {}
        if viewed and raw.startswith(b'HTTP/'):
            header, raw = re.split(rb'\r?\n\r?\n', raw, maxsplit=1)
            lines = header.decode('utf-8', errors='replace').splitlines()
            status = int(lines[0].split()[1])
            headers = {key.lower(): value.strip() for key, value in
                       (line.split(':', 1) for line in lines[1:] if ':' in line)}
        try:
            value = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            value = None
        errors = value.get('errors', []) if isinstance(value, dict) else []
        details = [item for item in errors if isinstance(item, dict)]
        message = str(value.get('message', '')).lower() if isinstance(value, dict) else ''
        rate_limited = (status == 429 or (bool(errors) and len(details) == len(errors)
                        and all(item.get('type') == 'RATE_LIMITED' or 'rate limit' in
                                str(item.get('message', '')).lower() for item in details))
                        or (status == 403 and 'rate limit' in message))
        if viewed and rate_limited:
            delay = 0.0
            if 'retry-after' in headers:
                try:
                    delay = float(headers['retry-after'])
                except ValueError:
                    delay = max(0, parsedate_to_datetime(headers['retry-after']).timestamp() - time.time())
                require(delay >= 0, 'Invalid GitHub Retry-After header')
            if headers.get('x-ratelimit-remaining') == '0' and 'x-ratelimit-reset' in headers:
                delay = max(delay, float(headers['x-ratelimit-reset']) - time.time() + 1)
            if not delay:
                delay = 60
            raise ViewedRequestFailure(max(0, delay)) from failure
        server_error = (bool(errors) and len(details) == len(errors) and all(
            item.get('type') in ('INTERNAL', 'INTERNAL_SERVER_ERROR', 'SERVICE_UNAVAILABLE')
            for item in details))
        # gh can emit 2xx headers before its GraphQL body read fails; parsed API errors retain their disposition.
        if viewed and (status in (500, 502, 503, 504) or server_error or
                       (failure is not None and value is None
                        and (status is None or 200 <= status < 300) and re.search(
                           rb'timeout|timed out|connection (?:reset|refused)|\bEOF\b|'
                           rb'TLS handshake|temporary failure|no such host|network is unreachable|'
                           rb'could not resolve host', failure.stderr, re.IGNORECASE))):
            raise ViewedRequestFailure() from failure
        if failure is not None:
            raise failure
        require(isinstance(value, dict) and not errors,
                'GitHub GraphQL failed; inspect private logs')
        require(isinstance(value.get('data'), dict), 'GitHub response has no data')
        return value['data']

    def api(self, method: str, path: str, payload: Optional[dict] = None) -> dict:
        arguments = ['gh', 'api', '--hostname', 'github.com', '--method', method, path]
        if payload is not None:
            arguments.extend(['--input', '-'])
        value = json.loads(self.call(arguments, input_value=payload))
        require(isinstance(value, dict), 'Invalid GitHub REST response')
        return value

    def commit(self, source: str, head: str) -> dict:
        return self.api('GET', 'repos/' + source + '/git/commits/' + head)


def pr_snapshot(commands: Commands, request: dict) -> dict:
    deadline = time.monotonic() + 180
    for attempt in range(5):
        try:
            return read_pr_snapshot(commands, request, deadline)
        except ViewedRequestFailure as error:
            pause_viewed(error, attempt, deadline)
    raise RuntimeError('Viewed snapshot retries exhausted')


def read_pr_snapshot(commands: Commands, request: dict, deadline: float) -> dict:
    owner, name = request['pull_request'].split('/')
    variables = {'owner': owner, 'name': name, 'number': request['number'], 'cursor': None}
    identity = None
    files = {}
    cursors = set()
    while True:
        data = commands.graphql(PR_QUERY, variables, timeout=viewed_timeout(deadline))
        pr = data['repository']['pullRequest']
        require(isinstance(pr, dict) and isinstance(pr.get('headRepository'), dict),
                'PR or source repository is unavailable')
        current = {'id': pr['id'], 'base': pr['baseRefOid'], 'head': pr['headRefOid'],
                   'source': pr['headRepository']['nameWithOwner'], 'source_id': pr['headRepository']['id'],
                   'ref': 'refs/heads/' + pr['headRefName'],
                   'viewer': data['viewer']['login']}
        require(identity is None or current == identity, 'PR identity/version changed during pagination')
        identity = current
        page = pr['files']
        for entry in page['nodes']:
            require(entry['path'] not in files, 'Duplicate PR file during pagination')
            require(entry['viewerViewedState'] in ('VIEWED', 'UNVIEWED', 'DISMISSED'),
                    'Unknown Viewed state')
            files[entry['path']] = entry['viewerViewedState']
        info = page['pageInfo']
        if not info['hasNextPage']:
            require(len(files) == page['totalCount'], 'Incomplete PR file pagination')
            break
        cursor = info['endCursor']
        require(isinstance(cursor, str) and cursor and cursor not in cursors, 'Invalid pagination cursor')
        cursors.add(cursor)
        variables['cursor'] = cursor
    identity['files'] = files
    return identity


def check_pr(observed: dict, plan: dict, head: str) -> None:
    expected = plan['pr']
    require(all(observed[key] == expected[key] for key in ('id', 'base', 'source', 'source_id', 'ref', 'viewer'))
            and observed['head'] == head, 'PR viewer, source, base or head changed')
    require(all(path in observed['files'] for path in plan['request']['viewed_paths']),
            'A selected Viewed path is no longer in the PR')


def source_slug(url: str) -> str:
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+/[^/]+?)(?:\.git)?/?', url)
    require(match is not None and SLUG.fullmatch(match[1]) is not None,
            'Source remote must be an uncredentialed github.com SSH/HTTPS URL')
    return match[1]


def references(request: dict) -> dict[str, str]:
    result = {}
    for value in request['evidence']:
        path = Path(value)
        require(path.is_absolute() and path.is_file(), 'Evidence must name readable absolute files')
        result[str(path.resolve())] = digest(path.read_bytes())
    require(bool(result), 'Retain review, checks and authorization evidence before preparation')
    return result


def request_from(path: Path) -> dict:
    value = read_json(path)
    allowed = {'repository', 'branch', 'pull_request', 'number', 'base', 'head', 'viewer',
               'viewed_paths', 'mode', 'remote', 'message', 'evidence'}
    require(not set(value) - allowed, 'Unknown request fields')
    for key in ('repository', 'branch', 'pull_request', 'base', 'head', 'viewer', 'mode'):
        require(isinstance(value.get(key), str) and bool(value[key]), 'Missing string: ' + key)
    require(value['mode'] in ('viewed-only', 'commit-push', 'amend-push'), 'Unsupported completion mode')
    require(SLUG.fullmatch(value['pull_request']) is not None, 'Invalid owner/repository')
    require(type(value.get('number')) is int and value['number'] > 0, 'Invalid PR number')
    require(SHA.fullmatch(value['base']) is not None and SHA.fullmatch(value['head']) is not None,
            'Expected full lowercase GitHub commit IDs')
    require(isinstance(value.get('viewed_paths'), list) and bool(value['viewed_paths'])
            and all(isinstance(item, str) and item and not item.startswith('/')
                    and '..' not in item.split('/') and '\\' not in item
                    for item in value['viewed_paths'])
            and len(set(value['viewed_paths'])) == len(value['viewed_paths']), 'Invalid Viewed path set')
    require(isinstance(value.get('evidence'), list), 'Evidence paths are required')
    if value['mode'] != 'viewed-only':
        require(isinstance(value.get('remote'), str) and value['remote']
                and not value['remote'].startswith('-'), 'A verified source remote name is required')
        require(isinstance(value.get('message'), str) and value['message'].strip(), 'Commit message is required')
    value['repository'] = str(Path(value['repository']).resolve())
    return value


def file_state(repository: Path, name: str) -> dict:
    path = repository / name
    if path.is_symlink():
        return {'kind': 'symlink', 'target': os.readlink(str(path))}
    if not path.exists():
        return {'kind': 'absent'}
    require(path.is_file(), 'Changed directories/submodules need the existing manual workflow: ' + name)
    return {'kind': 'file', 'sha256': digest(path.read_bytes()), 'executable': bool(path.stat().st_mode & 0o111)}


def workspace(commands: Commands) -> dict:
    root = Path(os.fsdecode(commands.git('rev-parse', '--show-toplevel')).strip()).resolve()
    require(root == commands.repository, 'Repository must be the exact selected worktree root')
    branch = commands.git('symbolic-ref', '--quiet', '--short', 'HEAD').decode().strip()
    head = commands.git('rev-parse', 'HEAD').decode().strip()
    require(not commands.git('ls-files', '--unmerged'), 'Unresolved index conflicts')
    for marker in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply'):
        location = Path(os.fsdecode(commands.git('rev-parse', '--git-path', marker)).strip())
        if not location.is_absolute():
            location = root / location
        require(not location.exists(), 'In-progress Git operation: ' + marker)
    raw_index = commands.git('rev-parse', '--git-path', 'index').decode().strip()
    index_path = Path(raw_index)
    if not index_path.is_absolute():
        index_path = root / index_path
    index = commands.git('ls-files', '--stage', '-z')
    flags = commands.git('ls-files', '-v', '-z').split(b'\0')
    require(all(not item or item[:1] == b'H' for item in flags),
            'Special index flags need the existing manual workflow')
    names = set()
    for arguments in (('diff', '--name-only', '-z', '--no-renames', 'HEAD'),
                      ('diff', '--cached', '--name-only', '-z', '--no-renames'),
                      ('ls-files', '--others', '--exclude-standard', '-z')):
        names.update(os.fsdecode(name) for name in commands.git(*arguments).split(b'\0') if name)
    return {'branch': branch, 'head': head, 'index_sha256': digest(index),
            'index_path': str(index_path.resolve()),
            'files': {name: file_state(root, name) for name in sorted(names)}}


def same_worktree(commands: Commands, observed: dict, expected: dict) -> bool:
    return (observed['branch'] == expected['branch']
            and set(observed['files']).issubset(expected['files'])
            and all(file_state(commands.repository, name) == item
                    for name, item in expected['files'].items()))


def outgoing(commands: Commands, old: str, head: str) -> list[str]:
    return commands.git('rev-list', '--reverse', '--topo-order', head, '--not', old).decode().splitlines()


def push_url(commands: Commands, request: dict, pr: dict) -> str:
    mirror = commands.git('config', '--get-all', 'remote.' + request['remote'] + '.mirror',
                          allow_failure=True).decode().splitlines()
    require(all(value.lower() in ('false', 'no', 'off', '0') for value in mirror),
            'Mirrored push remotes need the existing manual workflow')
    urls = commands.git('remote', 'get-url', '--push', '--all', request['remote']).decode().splitlines()
    require(len(urls) == 1 and source_slug(urls[0]).lower() == pr['source'].lower(),
            'Push remote does not match the PR source repository')
    return urls[0]


def remote_head(commands: Commands, request: dict, pr: dict, expected_url: str) -> str:
    require(push_url(commands, request, pr) == expected_url, 'Source push destination changed')
    value = commands.api('GET', 'repos/' + pr['source'] + '/git/ref/' + quote(pr['ref'][5:], safe='/'))
    require(value.get('ref') == pr['ref'] and value.get('object', {}).get('type') == 'commit'
            and SHA.fullmatch(value['object']['sha']) is not None, 'Source branch is unavailable')
    return value['object']['sha']


def prepare(input_path: Path, state: Path) -> dict:
    request = request_from(input_path)
    repository = Path(request['repository'])
    require(state != repository and repository not in state.parents, 'State must be outside the worktree')
    state.mkdir(mode=0o700, parents=True, exist_ok=False)
    commands = Commands(repository, state)
    with operation_lock(state):
        before = workspace(commands)
        require(before['branch'] == request['branch'], 'Selected local branch changed')
        evidence = references(request)
        pr = pr_snapshot(commands, request)
        require(pr['base'] == request['base'] and pr['head'] == request['head']
                and pr['viewer'] == request['viewer'], 'Prepared PR version/viewer differs from request')
        require(all(name in pr['files'] for name in request['viewed_paths']), 'Selected Viewed file is absent')
        index_bytes = Path(before['index_path']).read_bytes()
        (state / 'original.index').write_bytes(index_bytes)
        commands.git('diff', '--binary', '--cached', 'HEAD')
        commands.git('diff', '--binary')
        recovery = state / 'working-files'
        recovery.mkdir(mode=0o700)
        for number, (name, item) in enumerate(before['files'].items()):
            if item['kind'] == 'file':
                shutil.copyfile(str(repository / name), str(recovery / str(number)))
        tree = commands.git('rev-parse', 'HEAD^{tree}').decode().strip()
        commits = []
        destination = None
        parents = [before['head']]
        if request['mode'] != 'viewed-only':
            destination = push_url(commands, request, pr)
            require(remote_head(commands, request, pr, destination) == pr['head'], 'Source ref and PR head disagree')
            commands.git('merge-base', '--is-ancestor', pr['head'], before['head'])
            commits = outgoing(commands, pr['head'], before['head'])
            if request['mode'] == 'amend-push':
                require(before['branch'] not in ('master', 'main')
                        and pr['ref'] not in ('refs/heads/master', 'refs/heads/main'),
                        'Amendment requires both local and source branches outside master/main')
                parents = commands.git('rev-list', '--parents', '-n', '1', before['head']).decode().split()[1:]
            temporary = state / 'intended.index'
            environment = {'GIT_INDEX_FILE': str(temporary)}
            commands.git('read-tree', 'HEAD', environment=environment)
            commands.git('add', '-A', environment=environment)
            tree = commands.git('write-tree', environment=environment).decode().strip()
            commands.git('diff', '--binary', pr['head'], tree)
            if request['mode'] == 'amend-push':
                commands.git('show', '--format=fuller', '--binary', before['head'])
                commands.git('diff', '--binary', parents[0] if parents else
                             commands.git('hash-object', '-t', 'tree', '-w', '--stdin').decode().strip(), tree)
            commands.git('log', '--format=fuller', '--stat', pr['head'] + '..' + before['head'])
        else:
            require(before['head'] == pr['head'], 'Viewed-only helper requires local HEAD at the reviewed PR head')
        after = workspace(commands)
        require(after == before, 'Local state changed during preparation')
        plan = {'version': 2, 'parents': parents, 'request': request, 'workspace': before, 'pr': pr,
                'evidence': evidence, 'tree': tree, 'outgoing': commits, 'push_url': destination,
                'intended_index_sha256': (digest(commands.git('ls-files', '--stage', '-z',
                    environment={'GIT_INDEX_FILE': str(state / 'intended.index')}))
                    if request['mode'] != 'viewed-only' else before['index_sha256'])}
        write_json(state / 'plan.json', plan)
        plan_id = digest(encoded(plan))
        write_json(state / 'progress.json', {'plan_id': plan_id, 'phase': 'prepared'})
        return summary(state, plan, 'prepared')


def summary(state: Path, plan: dict, status: str, *, head: Optional[str] = None) -> dict:
    paths = plan['request']['viewed_paths']
    return {'status': status, 'plan_id': digest(encoded(plan)), 'mode': plan['request']['mode'],
            'head': head or plan['workspace']['head'], 'viewed_count': len(paths),
            'changed_path_count': len(plan['workspace']['files']),
            'outgoing_commit_count': len(plan['outgoing']), 'plan': str(state / 'plan.json'),
            'progress': str(state / 'progress.json'), 'logs': str(state / 'logs')}


def verify_commit(commands: Commands, plan: dict, head: str) -> None:
    before = plan['workspace']['head']
    require(commands.git('rev-parse', head + '^{tree}').decode().strip() == plan['tree'],
            'Commit tree differs from checked intended content')
    if head != before:
        parents = commands.git('rev-list', '--parents', '-n', '1', head).decode().split()[1:]
        require(parents == plan['parents'], 'Unexpected commit parent/history')
        require(commands.git('log', '-1', '--format=%B', head).decode().strip()
                == plan['request']['message'].strip(), 'Unexpected completion commit message')


def verify_published(commands: Commands, plan: dict, observed: dict, head: str) -> None:
    check_pr(observed, plan, head)
    value = commands.commit(observed['source'], head)
    require(value['sha'] == head and value['tree']['sha'] == plan['tree'],
            'Published commit/tree differs from checked content')
    if head != plan['workspace']['head']:
        require([item['sha'] for item in value['parents']] == plan['parents'],
                'Published commit parent differs from expected')


def commit_payload(commands: Commands, head: str) -> dict:
    """Translate the headers supported by the exact-SHA API publication contract."""
    raw = commands.git('cat-file', 'commit', head).decode('utf-8')
    headers, message = raw.split('\n\n', 1)
    values = {}
    parents = []
    for line in headers.splitlines():
        key, value = line.split(' ', 1)
        require(key in ('tree', 'parent', 'author', 'committer'),
                'GitHub API transport cannot reproduce commit header %r in %s. Use git transport' % (key, head))
        if key == 'parent':
            parents.append(value)
        else:
            require(key not in values, 'Duplicate commit header in ' + head)
            values[key] = value
    payload = {'tree': values['tree'], 'parents': parents, 'message': message}
    for key in ('author', 'committer'):
        match = re.fullmatch(r'(.*) <([^<>]*)> (-?\d+) ([+-])(\d\d)(\d\d)', values[key])
        require(match is not None, 'Unsupported Git identity in ' + head)
        name, email, seconds, sign, hours, minutes = match.groups()
        offset = timedelta(hours=int(hours), minutes=int(minutes))
        if sign == '-':
            offset = -offset
        date = datetime.fromtimestamp(int(seconds), timezone(offset)).isoformat()
        payload[key] = {'name': name, 'email': email, 'date': date}
    return payload


def api_pre_push(commands: Commands, state: Path, plan: dict, head: str) -> None:
    # Let Git select/execute hooks, including core.hooksPath and Windows shell hooks.
    version = re.search(rb'git version (\d+)\.(\d+)', commands.git('--version'))
    require(version is not None, 'Cannot determine Git hook-runner capability')
    if tuple(int(part) for part in version.groups()) < (2, 43):
        hook = Path(os.fsdecode(commands.git('rev-parse', '--git-path', 'hooks/pre-push')).strip())
        if not hook.is_absolute():
            hook = commands.repository / hook
        active = hook.is_file() and (os.name == 'nt' or os.access(str(hook), os.X_OK))
        if os.name == 'nt':
            active = active or hook.with_name(hook.name + '.exe').is_file()
        require(not active, 'GitHub API publication with a pre-push hook requires Git 2.43+ (git hook run --to-stdin)')
        return
    hook_input = state / 'pre-push.stdin'
    hook_input.write_bytes(('%s %s %s %s\n' % (head, head, plan['pr']['ref'], plan['pr']['head'])).encode('utf-8'))
    commands.git('hook', 'run', '--ignore-missing', '--to-stdin=' + str(hook_input),
                 'pre-push', '--', plan['request']['remote'], plan['push_url'])


def publish_api(commands: Commands, state: Path, plan: dict, head: str, commits: list[str]) -> None:
    payloads = {commit: commit_payload(commands, commit) for commit in commits}
    api_pre_push(commands, state, plan, head)
    workspace_after_commit(commands, plan, head)
    require(remote_head(commands, plan['request'], plan['pr'], plan['push_url']) == plan['pr']['head'],
            'Source ref changed during publication hook')
    prefix = 'repos/' + plan['pr']['source'] + '/git/'
    # Excluding the old source tip also excludes its already available object closure.
    objects = commands.git('rev-list', '--objects', '--no-object-names', head,
                           '--not', plan['pr']['head']).decode().splitlines()
    pending = set(objects) - set(commits)
    uploaded = set()

    def upload(oid: str, kind: str) -> None:
        if oid not in pending or oid in uploaded:
            return
        if kind == 'blob':
            payload = {'encoding': 'base64', 'content': base64.b64encode(commands.git('cat-file', 'blob', oid)).decode('ascii')}
            endpoint = 'blobs'
        else:
            require(kind == 'tree', 'Unsupported outgoing Git object type')
            entries = []
            for raw in commands.git('ls-tree', '-z', oid).split(b'\0'):
                if not raw:
                    continue
                metadata, name = raw.split(b'\t', 1)
                mode, entry_kind, entry_oid = metadata.decode('ascii').split()
                if entry_kind != 'commit':  # A gitlink refers to its independent repository.
                    upload(entry_oid, entry_kind)
                entries.append({'path': name.decode('utf-8'), 'mode': mode.zfill(6),
                                'type': entry_kind, 'sha': entry_oid})
            payload = {'tree': entries}
            endpoint = 'trees'
        value = commands.api('POST', prefix + endpoint, payload)
        require(value.get('sha') == oid, 'GitHub API returned a different ' + kind + ' SHA')
        uploaded.add(oid)

    for commit, payload in payloads.items():
        upload(payload['tree'], 'tree')
        value = commands.api('POST', prefix + 'commits', payload)
        require(value.get('sha') == commit,
                'GitHub API cannot reproduce exact commit ' + commit + '. Source ref was not updated')
    workspace_after_commit(commands, plan, head)
    check_pr(pr_snapshot(commands, plan['request']), plan, plan['pr']['head'])
    require(remote_head(commands, plan['request'], plan['pr'], plan['push_url']) == plan['pr']['head'],
            'Source ref changed before atomic publication')
    commands.graphql(UPDATE_QUERY, {'input': {'repositoryId': plan['pr']['source_id'], 'refUpdates': [{
        'name': plan['pr']['ref'], 'beforeOid': plan['pr']['head'], 'afterOid': head,
        'force': plan['request']['mode'] == 'amend-push' and plan['workspace']['head'] == plan['pr']['head']}]}})


def run(state: Path, confirmed: str, transport: str = 'git') -> dict:
    plan = read_json(state / 'plan.json')
    plan_id = digest(encoded(plan))
    require(plan.get('version') == 2, 'Unsupported private plan version; prepare a new plan')
    require(confirmed == plan_id, 'Confirmation does not match the frozen plan')
    require(transport in ('git', 'github-api'), 'Unsupported publication transport')
    request = plan['request']
    require(references(request) == plan['evidence'], 'Retained evidence changed or is unavailable')
    commands = Commands(Path(request['repository']), state)
    with operation_lock(state):
        progress = read_json(state / 'progress.json')
        require(progress.get('plan_id') == plan_id, 'Progress belongs to another plan')
        observed = workspace(commands)
        before = plan['workspace']
        require(observed['branch'] == before['branch'], 'Selected local branch changed')
        pr = pr_snapshot(commands, request)
        head = before['head']
        if request['mode'] == 'viewed-only':
            require(observed == before, 'Local state changed after preparation')
            check_pr(pr, plan, plan['pr']['head'])
        else:
            if observed['head'] != before['head']:
                require(progress.get('commit_attempted') is True, 'Unexpected local commit')
                head = observed['head']
                verify_commit(commands, plan, head)
                require(not observed['files'], 'Changes remain after the completion commit')
            else:
                require(same_worktree(commands, observed, before), 'Worktree content changed after preparation')
                require(observed['index_sha256'] in (before['index_sha256'], plan['intended_index_sha256']),
                        'Index changed after preparation')
            require(pr['head'] in (plan['pr']['head'], head), 'Remote PR head changed')
            check_pr(pr, plan, pr['head'])
            actual_remote = remote_head(commands, request, pr, plan['push_url'])
            require(actual_remote in (plan['pr']['head'], head), 'Remote source ref changed')
            needs_amend = (request['mode'] == 'amend-push'
                           and commands.git('log', '-1', '--format=%B', head).decode().strip() != request['message'].strip())
            local_complete = (not needs_amend and not observed['files']
                              and observed['index_sha256'] == plan['intended_index_sha256']
                              and commands.git('rev-parse', head + '^{tree}').decode().strip() == plan['tree'])
            if head == before['head'] and not local_complete:
                require(pr['head'] == plan['pr']['head'] and actual_remote == plan['pr']['head'],
                        'Remote changed before local completion')
                progress.update(phase='staging')
                write_json(state / 'progress.json', progress)
                commands.git('add', '-A')
                require(commands.git('write-tree').decode().strip() == plan['tree'], 'Staged content changed')
                staged = workspace(commands)
                require(same_worktree(commands, staged, before), 'Staging/filter changed worktree content')
                if needs_amend or commands.git('rev-parse', 'HEAD^{tree}').decode().strip() != plan['tree']:
                    progress.update(phase='committing', commit_attempted=True)
                    write_json(state / 'progress.json', progress)
                    arguments = ['commit', '-m', request['message']]
                    if request['mode'] == 'amend-push':
                        arguments.extend(['--amend', '--allow-empty'])
                    commands.git(*arguments)
                    head = commands.git('rev-parse', 'HEAD').decode().strip()
            verify_commit(commands, plan, head)
            workspace_after_commit(commands, plan, head)
            expected_outgoing = list(plan['outgoing'])
            if head != before['head']:
                if request['mode'] == 'amend-push' and before['head'] in expected_outgoing:
                    expected_outgoing.remove(before['head'])
                expected_outgoing.append(head)
            require(outgoing(commands, plan['pr']['head'], head) == expected_outgoing,
                    'Outgoing ancestry differs from approved scope')
            progress.update(phase='committed', head=head)
            write_json(state / 'progress.json', progress)
            pr = pr_snapshot(commands, request)
            require(pr['head'] in (plan['pr']['head'], head), 'PR changed before publication')
            check_pr(pr, plan, pr['head'])
            actual_remote = remote_head(commands, request, pr, plan['push_url'])
            require(actual_remote in (plan['pr']['head'], head), 'Source ref changed before publication')
            workspace_after_commit(commands, plan, head)
            if actual_remote != head:
                require(pr['head'] == plan['pr']['head'], 'PR and source ref disagree')
                progress.update(phase='pushing')
                write_json(state / 'progress.json', progress)
                if transport == 'github-api':
                    publish_api(commands, state, plan, head, expected_outgoing)
                else:
                    commands.git('push', '--no-follow-tags', '--recurse-submodules=no',
                                 '--force-with-lease=' + plan['pr']['ref'] + ':' + plan['pr']['head'],
                                 request['remote'], head + ':' + plan['pr']['ref'])
            require(remote_head(commands, request, pr, plan['push_url']) == head, 'Push needs source-ref readback')
            pr = pr_snapshot(commands, request)
            verify_published(commands, plan, pr, head)
        completion_workspace = before if request['mode'] == 'viewed-only' else workspace_after_commit(commands, plan, head)
        # The evidence is still valid immediately before the independently visible Viewed effects.
        require(references(request) == plan['evidence'], 'Evidence changed during completion')
        progress.update(phase='viewed', head=head)
        write_json(state / 'progress.json', progress)
        record_viewed(commands, plan, head, completion_workspace)
        progress.update(phase='complete', head=head, viewed=request['viewed_paths'])
        write_json(state / 'progress.json', progress)
        result = summary(state, plan, 'complete', head=head)
        write_json(state / 'result.json', result)
        return result


def record_viewed(commands: Commands, plan: dict, head: str, expected_workspace: dict) -> None:
    request = plan['request']
    deadline = time.monotonic() + 180
    for attempt in range(5):
        require(references(request) == plan['evidence'], 'Evidence changed during Viewed recording')
        require(workspace(commands) == expected_workspace, 'Local state changed during Viewed recording')
        try:
            # A failed mutation may already have succeeded: reconcile the full set before any repeat.
            pr = read_pr_snapshot(commands, request, deadline)
            check_pr(pr, plan, head)
            for path in request['viewed_paths']:
                if pr['files'][path] == 'VIEWED':
                    continue
                data = commands.graphql(MARK_QUERY, {'id': pr['id'], 'path': path},
                                        timeout=viewed_timeout(deadline))
                result = data['markFileAsViewed']['pullRequest']
                require(result['baseRefOid'] == plan['pr']['base'] and result['headRefOid'] == head,
                        'PR version changed during Viewed recording')
            final = read_pr_snapshot(commands, request, deadline)
            check_pr(final, plan, head)
            require(all(final['files'][path] == 'VIEWED' for path in request['viewed_paths']),
                    'Viewed recording is incomplete; resume the same operation')
            require(workspace(commands) == expected_workspace, 'Local state changed during Viewed recording')
            require(references(request) == plan['evidence'], 'Evidence changed during Viewed recording')
            return
        except ViewedRequestFailure as error:
            pause_viewed(error, attempt, deadline)
    raise RuntimeError('Viewed recording retries exhausted')


def workspace_after_commit(commands: Commands, plan: dict, head: str) -> dict:
    observed = workspace(commands)
    require(observed['branch'] == plan['workspace']['branch'] and observed['head'] == head
            and observed['index_sha256'] == plan['intended_index_sha256']
            and not observed['files'], 'Selected branch/index/worktree changed during completion')
    return observed


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, epilog=CLI_HELP,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest='operation', required=True)
    preparation = subparsers.add_parser('prepare', help='Freeze a reviewable plan and private recovery evidence',
                                       description=PREPARE_HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    preparation.add_argument('--input', required=True, type=Path, help='Request JSON file; full schema is in top-level --help')
    preparation.add_argument('--state', required=True, type=Path, help='New private recovery directory outside the worktree')
    completion = subparsers.add_parser('run', help='Execute/resume only effects already authorized for this plan',
                                      description=RUN_HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    completion.add_argument('--state', required=True, type=Path, help='Existing private directory created by prepare')
    completion.add_argument('--confirm', required=True, help='Frozen plan_id matching prior conversation authorization')
    completion.add_argument('--transport', choices=('git', 'github-api'), default='git',
                            help='Publication transport; may change when resuming the same authorized plan')
    arguments = parser.parse_args(argv)
    state = arguments.state.resolve()
    try:
        result = (prepare(arguments.input, state) if arguments.operation == 'prepare'
                  else run(state, arguments.confirm, arguments.transport))
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 0
    except KeyboardInterrupt:
        print(json.dumps({'status': 'interrupted', 'state': str(state), 'logs': str(state / 'logs')}))
        return 130
    except Exception as error:
        # This CLI owns final reporting for every failed operation; retain partial effects and stop.
        print(json.dumps({'status': 'incomplete', 'error': str(error)[:400],
                          'state': str(state), 'logs': str(state / 'logs')}, ensure_ascii=True))
        return 1


if __name__ == '__main__':
    sys.exit(main())
