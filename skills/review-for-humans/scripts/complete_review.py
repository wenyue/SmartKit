#!/usr/bin/env python
"""Freeze and resume authorized PR completion; full evidence stays in private state."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
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


SHA = re.compile(r'[0-9a-f]{40}')
SLUG = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')
GIT_ROUTING = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
               'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
               'GIT_PREFIX', 'GIT_NAMESPACE', 'GIT_CONFIG', 'GIT_CONFIG_COUNT')
PR_QUERY = '''query($owner:String!,$name:String!,$number:Int!,$cursor:String){
 viewer{login} repository(owner:$owner,name:$name){pullRequest(number:$number){
 id baseRefOid headRefOid headRefName headRepository{nameWithOwner}
 files(first:100,after:$cursor){totalCount nodes{path viewerViewedState}
 pageInfo{hasNextPage endCursor}}}}}'''
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
             environment: Optional[dict[str, str]] = None, allow_failure: bool = False) -> bytes:
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
                process.communicate(input_bytes)
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
            raise RuntimeError('%s exited %s; see %s' % (arguments[0], process.returncode, prefix))
        return prefix.with_suffix('.stdout').read_bytes()

    def git(self, *arguments: str, **options: object) -> bytes:
        return self.call(['git', '-C', str(self.repository)] + list(arguments), **options)

    def graphql(self, query: str, variables: dict) -> dict:
        raw = self.call(['gh', 'api', 'graphql', '--hostname', 'github.com', '--input', '-'],
                        input_value={'query': query, 'variables': variables})
        value = json.loads(raw)
        require(isinstance(value, dict) and not value.get('errors'),
                'GitHub GraphQL failed; inspect private logs')
        require(isinstance(value.get('data'), dict), 'GitHub response has no data')
        return value['data']

    def commit(self, source: str, head: str) -> dict:
        raw = self.call(['gh', 'api', '--hostname', 'github.com',
                         'repos/' + source + '/git/commits/' + head])
        value = json.loads(raw)
        require(isinstance(value, dict), 'Invalid GitHub commit response')
        return value


def pr_snapshot(commands: Commands, request: dict) -> dict:
    owner, name = request['pull_request'].split('/')
    variables = {'owner': owner, 'name': name, 'number': request['number'], 'cursor': None}
    identity = None
    files = {}
    cursors = set()
    while True:
        data = commands.graphql(PR_QUERY, variables)
        pr = data['repository']['pullRequest']
        require(isinstance(pr, dict) and isinstance(pr.get('headRepository'), dict),
                'PR or source repository is unavailable')
        current = {'id': pr['id'], 'base': pr['baseRefOid'], 'head': pr['headRefOid'],
                   'source': pr['headRepository']['nameWithOwner'], 'ref': 'refs/heads/' + pr['headRefName'],
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
    require(all(observed[key] == expected[key] for key in ('id', 'base', 'source', 'ref', 'viewer'))
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
               'viewed_paths', 'mode', 'remote', 'message', 'requires_amend', 'evidence'}
    require(not set(value) - allowed, 'Unknown request fields')
    for key in ('repository', 'branch', 'pull_request', 'base', 'head', 'viewer', 'mode'):
        require(isinstance(value.get(key), str) and bool(value[key]), 'Missing string: ' + key)
    require(value['mode'] in ('viewed-only', 'commit-push'), 'Unsupported completion mode')
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
    require(not value.get('requires_amend'), 'Amendment/lease publication needs the existing manual workflow')
    if value['mode'] == 'commit-push':
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
    commands.git('merge-base', '--is-ancestor', old, head)
    return commands.git('rev-list', '--reverse', old + '..' + head).decode().splitlines()


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
    fields = commands.git('ls-remote', '--refs', expected_url, pr['ref']).decode().split()
    require(len(fields) == 2 and fields[1] == pr['ref'], 'Source branch is unavailable')
    return fields[0]


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
        if request['mode'] == 'commit-push':
            destination = push_url(commands, request, pr)
            require(remote_head(commands, request, pr, destination) == pr['head'], 'Source ref and PR head disagree')
            commits = outgoing(commands, pr['head'], before['head'])
            temporary = state / 'intended.index'
            environment = {'GIT_INDEX_FILE': str(temporary)}
            commands.git('read-tree', 'HEAD', environment=environment)
            commands.git('add', '-A', environment=environment)
            tree = commands.git('write-tree', environment=environment).decode().strip()
            commands.git('diff', '--binary', pr['head'], tree)
            commands.git('log', '--format=fuller', '--stat', pr['head'] + '..' + before['head'])
        else:
            require(before['head'] == pr['head'], 'Viewed-only helper requires local HEAD at the reviewed PR head')
        after = workspace(commands)
        require(after == before, 'Local state changed during preparation')
        plan = {'version': 1, 'request': request, 'workspace': before, 'pr': pr,
                'evidence': evidence, 'tree': tree, 'outgoing': commits, 'push_url': destination,
                'intended_index_sha256': (digest(commands.git('ls-files', '--stage', '-z',
                    environment={'GIT_INDEX_FILE': str(state / 'intended.index')}))
                    if request['mode'] == 'commit-push' else before['index_sha256'])}
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
        require(parents == [before], 'Unexpected commit parent/history')
        require(commands.git('log', '-1', '--format=%B', head).decode().strip()
                == plan['request']['message'].strip(), 'Unexpected completion commit message')


def verify_published(commands: Commands, plan: dict, observed: dict, head: str) -> None:
    check_pr(observed, plan, head)
    value = commands.commit(observed['source'], head)
    require(value['sha'] == head and value['tree']['sha'] == plan['tree'],
            'Published commit/tree differs from checked content')
    if head != plan['workspace']['head']:
        require([item['sha'] for item in value['parents']] == [plan['workspace']['head']],
                'Published commit parent differs from expected')


def run(state: Path, confirmed: str) -> dict:
    plan = read_json(state / 'plan.json')
    plan_id = digest(encoded(plan))
    require(plan.get('version') == 1 and confirmed == plan_id, 'Confirmation does not match the frozen plan')
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
            local_complete = (not observed['files']
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
                if commands.git('rev-parse', 'HEAD^{tree}').decode().strip() != plan['tree']:
                    progress.update(phase='committing', commit_attempted=True)
                    write_json(state / 'progress.json', progress)
                    commands.git('commit', '-m', request['message'])
                    head = commands.git('rev-parse', 'HEAD').decode().strip()
            verify_commit(commands, plan, head)
            workspace_after_commit(commands, plan, head)
            expected_outgoing = plan['outgoing'] + ([head] if head != before['head'] else [])
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
                commands.git('push', '--no-follow-tags', '--recurse-submodules=no',
                             request['remote'], head + ':' + plan['pr']['ref'])
            require(remote_head(commands, request, pr, plan['push_url']) == head, 'Push needs source-ref readback')
            pr = pr_snapshot(commands, request)
            verify_published(commands, plan, pr, head)
        completion_workspace = before if request['mode'] == 'viewed-only' else workspace_after_commit(commands, plan, head)
        # The evidence is still valid immediately before the independently visible Viewed effects.
        require(references(request) == plan['evidence'], 'Evidence changed during completion')
        progress.update(phase='viewed', head=head)
        write_json(state / 'progress.json', progress)
        for path in request['viewed_paths']:
            if pr['files'][path] == 'VIEWED':
                continue
            data = commands.graphql(MARK_QUERY, {'id': pr['id'], 'path': path})
            result = data['markFileAsViewed']['pullRequest']
            require(result['baseRefOid'] == plan['pr']['base'] and result['headRefOid'] == head,
                    'PR version changed during Viewed recording')
        final = pr_snapshot(commands, request)
        check_pr(final, plan, head)
        require(all(final['files'][path] == 'VIEWED' for path in request['viewed_paths']),
                'Viewed recording is incomplete; resume the same operation')
        require(workspace(commands) == completion_workspace,
                'Local state changed during Viewed recording')
        progress.update(phase='complete', head=head, viewed=request['viewed_paths'])
        write_json(state / 'progress.json', progress)
        result = summary(state, plan, 'complete', head=head)
        write_json(state / 'result.json', result)
        return result


def workspace_after_commit(commands: Commands, plan: dict, head: str) -> dict:
    observed = workspace(commands)
    require(observed['branch'] == plan['workspace']['branch'] and observed['head'] == head
            and observed['index_sha256'] == plan['intended_index_sha256']
            and not observed['files'], 'Selected branch/index/worktree changed during completion')
    return observed


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='operation', required=True)
    preparation = subparsers.add_parser('prepare', help='Freeze a reviewable plan and private recovery evidence')
    preparation.add_argument('--input', required=True, type=Path)
    preparation.add_argument('--state', required=True, type=Path)
    completion = subparsers.add_parser('run', help='Execute/resume only effects already authorized for this plan')
    completion.add_argument('--state', required=True, type=Path)
    completion.add_argument('--confirm', required=True, help='Frozen plan_id matching prior conversation authorization')
    arguments = parser.parse_args(argv)
    state = arguments.state.resolve()
    try:
        result = (prepare(arguments.input, state) if arguments.operation == 'prepare'
                  else run(state, arguments.confirm))
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
