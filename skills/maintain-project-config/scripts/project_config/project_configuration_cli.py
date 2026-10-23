"""Project configuration commands, shared with the full setup launcher."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

from project_state import config_backup as backup
from project_state.catalog import load_catalog, safe_relative
from project_state.models import Catalog
from project_state.paths import confined_target

from . import project_configuration as configuration
from . import repository
from .catalog import load_project_config, parse_maintenance
from .models import DesiredFile
from .ownership import load_ownership
from .planner import build_plan
from .project_sync import synchronize_project
from .project_rules import synchronize_project_rules
from .transaction import TransactionError, apply_plan


def add_arguments(parser: argparse.ArgumentParser, *, include_sync: bool = False) -> None:
    parser.description = ('Choose project shared, this machine only, or a separate personal configuration repository. '
                          'Inspect is local/read-only. Other commands perform only their named phase; publication is explicit. '
                          'Hold exclusive access to source and target during writes. Exit 0: phase complete; 2: refusal/failure.')
    commands = parser.add_subparsers(dest='configuration_command', required=True)
    for name, help_text in (
        ('inspect', 'Show backup binding, scope and source/target differences without fetching'),
        ('bind', 'Record a chosen mode; connect/create private source and explicitly import selected files'),
        ('update', 'Fetch and safely fast-forward the persistent source before editing'),
        ('apply', 'Restore complete backup files; no MCP generation or full setup'),
        ('adopt', 'Back up selected complete target files/directories into the source'),
        ('publish', 'Commit exact accepted source paths then normal-push, or retry a verified retained commit'),
    ):
        command = commands.add_parser(name, help=help_text, description=help_text, allow_abbrev=False)
        command.add_argument('--target', type=Path, required=True)
        if name == 'bind':
            command.add_argument('--mode', required=True, choices=('local', 'local-only', 'repository'),
                                 help='local: project shared; local-only: this machine only; repository: separate configuration repository')
            command.add_argument('--repository', help='Personal private GitHub owner/repo (github.com) or full HTTPS repository URL (including Enterprise)')
            command.add_argument('--branch', help='Explicit branch; confirm the remote default if desired')
            command.add_argument('--entry', help='One project slug within projects/')
            command.add_argument('--create-repository', action='store_true', help='Record existing user authorization to create this named private repository')
            command.add_argument('--file', action='append', default=[], help='Target-relative file or directory to back up; repeat. Omit to select existing default configuration paths')
            command.add_argument('--replace-binding', action='store_true', help='Record an explicit maintenance-mode/source switch; current source must converge first')
        if name == 'apply':
            command.add_argument('--accept-existing', help='Exact inspect fingerprint accepting all proposed source/target differences')
            command.add_argument('--auto-sync', choices=('on', 'off'), help='Record local permission for future session update/restore; default off')
        if name == 'adopt':
            command.add_argument('--file', action='append', default=[], help='Selected complete target-relative file or directory')
            command.add_argument('--all', action='store_true', help='Refresh all files and directories in the backup scope')
        if name == 'publish':
            command.add_argument('--path', action='append', default=[], help='Exact repository-relative changed file owned by this maintenance request; repeat')
            command.add_argument('--message', help='Commit message for the selected scope')
            command.add_argument('--commit', help='Retry a retained verified scope commit; mutually exclusive with --path/--message')
    if include_sync:
        for name, help_text in (
            ('sync-project', 'Synchronize established local Rule/Skill discovery and Agent/MCP/settings mappings'),
            ('sync-project-rules', 'Synchronize only the selected Project rules entry; no setup ownership required'),
        ):
            command = commands.add_parser(name, help=help_text, description=help_text, allow_abbrev=False)
            command.add_argument('--target', type=Path, required=True)
            command.add_argument('--check', action='store_true',
                                 help='Read-only: clean exits 0, drift exits 1; refusal/failure exits 2')


def _exclusion_block(content: bytes, key: str) -> tuple[bytes, bytes, list[str]]:
    """Read only this target's intact generated block; preserve other exclusions."""
    begin = f'# BEGIN SmartKit project configuration {key} '.encode('ascii')
    end = f'# END SmartKit project configuration {key}'.encode('ascii')
    lines = content.splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.startswith(begin)]
    ends = [index for index, line in enumerate(lines) if line.rstrip(b'\r\n') == end]
    if not starts and not ends:
        return content, b'', []
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValueError('SmartKit local exclusion block is incomplete; preserve it and resolve the edit')
    first, last = starts[0], ends[0]
    body = b''.join(lines[first + 1:last])
    if lines[first].rstrip(b'\r\n') != begin + hashlib.sha256(body).hexdigest().encode('ascii'):
        raise ValueError('SmartKit local exclusion block was edited; preserve it and resolve the edit')
    return b''.join(lines[:first]), b''.join(lines[last + 1:]), body.decode('utf-8').splitlines()


def exclude_local(target: Path, paths: list[str], *, enabled: bool = True, check_only: bool = False) -> list[str]:
    """Maintain this target's local exclusions, reporting tracked files without untracking.

    Disabling removes only its intact generated block. Existing user and legacy
    ignore rules remain authoritative; no business index or .gitignore is changed.
    """
    # Local excludes belong to this worktree even when the caller runs from a Git hook.
    environment = os.environ.copy()
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR', 'GIT_PREFIX',
                'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        environment.pop(key, None)
    result = subprocess.run(['git', '-C', str(target), 'rev-parse', '--show-toplevel'],
                            capture_output=True, text=True, timeout=30, env=environment)
    if result.returncode:
        return []
    worktree = Path(result.stdout.strip()).resolve()
    try:
        prefix = target.resolve().relative_to(worktree)
    except ValueError as error:
        raise ValueError('personal configuration target must be inside the Git worktree') from error
    result = subprocess.run(['git', '-C', str(target), 'rev-parse', '--git-path', 'info/exclude'],
                            capture_output=True, text=True, timeout=30, check=True, env=environment)
    path = Path(result.stdout.strip())
    path = path if path.is_absolute() else target / path
    path = confined_target(path.parent.absolute(), PurePosixPath(path.name))
    current = path.read_bytes() if path.exists() else b''
    key = hashlib.sha256(prefix.as_posix().encode('utf-8')).hexdigest()[:16]
    before, after, previous = _exclusion_block(current, key)
    tracked, patterns = [], list(previous) if enabled else []
    for value in sorted(set(paths)) if enabled else []:
        relative_path = safe_relative(value, 'local exclude path')
        directory = value.endswith('/') or confined_target(target, relative_path).is_dir()
        command = subprocess.run(['git', '-C', str(target), '--literal-pathspecs', 'ls-files', '-z', '--', str(relative_path)],
                                 capture_output=True, text=True, timeout=30, env=environment)
        if command.returncode:
            raise ValueError('cannot inspect tracked configuration paths: ' + command.stderr)
        tracked.extend(command.stdout.rstrip('\0').split('\0') if command.stdout else [])
        if command.stdout and not directory:
            continue
        relative = (prefix / str(relative_path)).as_posix()
        pattern = '/' + ''.join('\\' + char if char in '\\*?[]!# ' else char for char in relative) + ('/' if directory else '')
        ignored = subprocess.run(['git', '-C', str(target), 'check-ignore', '--quiet', '--', str(relative_path)],
                                 capture_output=True, text=True, timeout=30, env=environment)
        if ignored.returncode not in (0, 1):
            raise ValueError('cannot inspect existing ignore rules: ' + ignored.stderr)
        if ignored.returncode == 1 or pattern in previous:
            patterns.append(pattern)
    block = b''
    if patterns:
        body = ('\n'.join(sorted(set(patterns))) + '\n').encode('utf-8')
        block = (f'# BEGIN SmartKit project configuration {key} {hashlib.sha256(body).hexdigest()}\n'.encode('ascii')
                 + body + f'# END SmartKit project configuration {key}\n'.encode('ascii'))
        if before and not before.endswith(b'\n'):
            before += b'\n'
    content = before + block + after
    if not check_only and content != current:
        path.parent.mkdir(parents=True, exist_ok=True)
        apply_plan(path.parent, build_plan(path.parent, [DesiredFile(PurePosixPath(path.name), content)]))
    return sorted(set(tracked))


def sync_git_exclusions(target: Path, catalog: Catalog, paths: list[str] | None = None) -> list[str]:
    """Apply the recorded mode's Git behavior to canonical inputs and owned outputs."""
    selected = configuration.binding(target)
    if selected is None:
        return []
    if selected.mode == 'local':
        return exclude_local(target, [], enabled=False)
    personal = {'.agents/', 'AGENTS.md', 'CLAUDE.md', *(paths or [])}
    if selected.mode == 'repository':
        entry = configuration.entry_root(target)
        manifest, files = backup.read_backup(entry)
        personal.update(files)
        personal.update(manifest['directories'])
        return exclude_local(target, sorted(personal))
    config = load_project_config(target / configuration.CONFIG, catalog=catalog)
    personal.add(config.rule_entry.as_posix())
    personal.update(str(path) for agent in config.agents for path in agent.source_paths)
    personal.update(str(field.path) for field in config.settings)
    owned = load_ownership(target)
    if owned is not None:
        personal.update(str(asset.path) for asset in owned.assets)
    return exclude_local(target, sorted(personal))


def _bind(args: argparse.Namespace, catalog: Catalog) -> dict:
    target = args.target.absolute()
    if args.mode in {'local', 'local-only'}:
        if args.repository or args.branch or args.entry or args.file or args.create_repository:
            raise ValueError('local and local-only modes do not accept repository arguments')
        selected = {'mode': args.mode}
    else:
        selected = {'mode': 'repository', 'repository': args.repository, 'branch': args.branch, 'entry': args.entry}
    parse_maintenance(selected)
    current = configuration._document(target, configuration.CONFIG, missing=True)
    previous = current.get('maintenance')
    switching = previous is not None and previous != selected
    if switching and not args.replace_binding:
        raise ValueError('maintenance binding already exists; an explicit switch requires --replace-binding')
    exclude_local(target, [], enabled=False, check_only=True)
    if switching:
        configuration.require_converged(target)
    config_before = configuration._json(current)
    result = {'mode': args.mode}
    if args.mode == 'repository':
        root = repository.checkout(args.repository, args.branch, create=args.create_repository)
        entry = confined_target(root, PurePosixPath('projects') / args.entry)
        if not (entry / 'manifest.json').exists():
            entry.mkdir(parents=True, exist_ok=True)
            configuration.initialize_entry(target, entry, args.file,
                                           config_content=configuration._json({**current, 'maintenance': selected}))
        elif args.file:
            raise ValueError('initial file import is only valid for a new entry; explicitly adopt later edits')
        backup.read_backup(entry)
        result['source'] = str(entry)
    if configuration._json(configuration._document(target, configuration.CONFIG, missing=True)) != config_before:
        raise ValueError('project config changed while binding was prepared; source work is retained')
    current['maintenance'] = selected
    deletes = [configuration.STATE] if switching else []
    plan = build_plan(target, [DesiredFile(configuration.CONFIG, configuration._json(current))], delete_paths=deletes)
    apply_plan(target, plan)
    result['bound'] = True
    result['tracked_paths'] = sync_git_exclusions(target, catalog)
    return result


def _publish(args: argparse.Namespace) -> dict:
    target = args.target.absolute()
    selected = configuration.binding(target)
    if selected is None or selected.mode != 'repository':
        raise ValueError('publication needs a repository maintenance binding')
    if args.commit and (args.path or args.message):
        raise ValueError('--commit retry cannot include new commit scope or message')
    if not args.commit and (not args.path or not args.message):
        raise ValueError('publication requires exact --path selections and --message, or --commit retry')
    entry = configuration.entry_root(target)
    checkout = entry.parent.parent
    prefix = PurePosixPath('projects') / selected.entry
    for value in args.path:
        path = safe_relative(value, 'publication path')
        if prefix not in path.parents:
            raise ValueError('publication scope must stay inside the bound project entry')
    configuration.require_converged(target)
    commit = args.commit or repository.commit_scope(checkout, selected.branch, args.path, args.message)
    try:
        # Hooks may modify source inputs; those bytes must reach the target before publication.
        configuration.require_converged(target)
        return {'local_applied': True, **repository.publish(checkout, selected.branch, commit)}
    except (OSError, ValueError, subprocess.SubprocessError):
        # Supply retained-effect evidence; run() still owns the final failure diagnostic.
        print(f'Publication incomplete; local commit {commit} is retained. '
              'Inspect source, target and remote before retrying; no rollback was performed.', file=sys.stderr)
        raise


def run_sync(args: argparse.Namespace, command: str) -> int:
    """Apply one local synchronization scope without invoking full setup."""
    source = Path(__file__).resolve().parents[4]
    target = args.target.absolute()
    try:
        configuration.require_converged(target)
        if command == 'sync-project':
            result = synchronize_project(source, target, check_only=args.check)
        else:
            result = synchronize_project_rules(source, target, check_only=args.check)
        tracked = [] if args.check else sync_git_exclusions(target, load_catalog(source))
        selected = configuration.binding(target)
    except (OSError, ValueError, subprocess.SubprocessError, TransactionError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    output = {'phase': command, 'check': result.check, 'changed_paths': result.changed_paths}
    if command == 'sync-project':
        output['preserved_paths'] = result.preserved_paths
    if not args.check and selected is not None and selected.mode != 'local':
        output['tracked_paths'] = tracked
    print(json.dumps(output, ensure_ascii=False))
    return 1 if result.check == 'drift' else 0


def run(args: argparse.Namespace) -> int:
    if args.configuration_command in {'sync-project', 'sync-project-rules'}:
        return run_sync(args, args.configuration_command)
    try:
        catalog = load_catalog(Path(__file__).resolve().parents[4])
        target = args.target.absolute()
        command = args.configuration_command
        if command == 'bind':
            result = _bind(args, catalog)
        elif command == 'inspect':
            result = configuration.inspect(target)
        elif command == 'apply':
            result = configuration.apply(target, accept_existing=args.accept_existing,
                                         automatic=None if args.auto_sync is None else args.auto_sync == 'on')
            result['tracked_paths'] = sync_git_exclusions(target, catalog, result['managed_paths'])
        elif command == 'adopt':
            result = configuration.adopt(target, args.file, all_paths=args.all)
        elif command == 'update':
            selected = configuration.binding(target)
            if selected is None or selected.mode != 'repository':
                raise ValueError('update needs a repository maintenance binding')
            result = repository.update(repository.open_checkout(selected.repository, selected.branch), selected.branch)
        else:
            result = _publish(args)
        print(json.dumps({'operation': command, **result}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError, TransactionError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
