"""Project configuration commands, shared with the full setup launcher."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

from project_state.catalog import load_catalog, safe_relative
from project_state.models import Catalog
from project_state.paths import confined_target

from . import project_configuration as configuration
from . import repository
from .catalog import parse_maintenance
from .models import DesiredFile
from .planner import build_plan
from .project_sync import synchronize_project
from .project_rules import synchronize_project_rules
from .transaction import TransactionError, apply_plan


def add_arguments(parser: argparse.ArgumentParser, *, include_sync: bool = False) -> None:
    parser.description = ('Maintain canonical project configuration in a persistent personal private GitHub repository. '
                          'Inspect is local/read-only. Other commands perform only their named phase; publication is explicit. '
                          'Hold exclusive access to source and target during writes. Exit 0: phase complete; 2: refusal/failure.')
    commands = parser.add_subparsers(dest='configuration_command', required=True)
    for name, help_text in (
        ('inspect', 'Show binding, source/target diff and conflict evidence without fetching'),
        ('bind', 'Record a chosen mode; connect/create private source and explicitly import selected files'),
        ('update', 'Fetch and safely fast-forward the persistent source before editing'),
        ('apply', 'Apply canonical inputs; follow with sync-project or full setup for native outputs'),
        ('adopt', 'Copy selected target changes to an unchanged source; follow with apply and publication'),
        ('publish', 'Commit exact accepted source paths then normal-push, or retry a verified retained commit'),
    ):
        command = commands.add_parser(name, help=help_text, description=help_text, allow_abbrev=False)
        command.add_argument('--target', type=Path, required=True)
        if name == 'bind':
            command.add_argument('--mode', required=True, choices=('local', 'repository'))
            command.add_argument('--repository', help='Personal private GitHub owner/repo (github.com) or full HTTPS repository URL (including Enterprise)')
            command.add_argument('--branch', help='Explicit branch; confirm the remote default if desired')
            command.add_argument('--entry', help='One project slug within projects/')
            command.add_argument('--create-repository', action='store_true', help='Record existing user authorization to create this named private repository')
            command.add_argument('--file', action='append', default=[], help='Exact target-relative canonical file to import into a new entry; repeat for support files')
            command.add_argument('--replace-binding', action='store_true', help='Record an explicit maintenance-mode/source switch; current source must converge first')
        if name == 'apply':
            command.add_argument('--accept-existing', help='Exact inspect fingerprint accepting initial target collisions; never overwrites later recorded edits')
        if name == 'adopt':
            command.add_argument('--file', action='append', default=[], help='Exact selected canonical target-relative file')
            command.add_argument('--field', action='append', default=[], choices=sorted(configuration.PORTABLE), help='Selected portable config field')
        if name == 'publish':
            command.add_argument('--path', action='append', default=[], help='Exact repository-relative changed file owned by this maintenance request; repeat')
            command.add_argument('--message', help='Commit message for the selected scope')
            command.add_argument('--commit', help='Retry a retained verified scope commit; mutually exclusive with --path/--message')
    if include_sync:
        for name, help_text in (
            ('sync-project', 'Synchronize established local Rule/Skill discovery and Agent/MCP/settings mappings'),
            ('sync-project-rules', 'Synchronize only the AGENTS.md Project rules index; no setup ownership required'),
        ):
            command = commands.add_parser(name, help=help_text, description=help_text, allow_abbrev=False)
            command.add_argument('--target', type=Path, required=True)
            command.add_argument('--check', action='store_true',
                                 help='Read-only: clean exits 0, drift exits 1; refusal/failure exits 2')


def exclude_local(target: Path, paths: list[str]) -> list[str]:
    """Exclude untracked personal artifacts locally; tracked files retain Git ownership."""
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
    tracked = []
    patterns = []
    for value in sorted(set(paths)):
        path = safe_relative(value, 'local exclude path')
        command = subprocess.run(['git', '-C', str(target), '--literal-pathspecs', 'ls-files', '--error-unmatch', '--', str(path)],
                                 capture_output=True, text=True, timeout=30, env=environment)
        if command.returncode == 0:
            tracked.append(value)
        elif command.returncode == 1:
            ignored = subprocess.run(['git', '-C', str(target), 'check-ignore', '--quiet', '--', str(path)],
                                     capture_output=True, text=True, timeout=30, env=environment)
            if ignored.returncode == 0:
                continue
            if ignored.returncode != 1:
                raise ValueError('cannot inspect existing ignore rules: ' + ignored.stderr)
            relative = (prefix / str(path)).as_posix()
            patterns.append('/' + ''.join('\\' + char if char in '\\*?[]!# ' else char for char in relative))
        else:
            raise ValueError('cannot inspect tracked configuration paths: ' + command.stderr)
    result = subprocess.run(['git', '-C', str(target), 'rev-parse', '--git-path', 'info/exclude'],
                            capture_output=True, text=True, timeout=30, check=True, env=environment)
    path = Path(result.stdout.strip())
    path = path if path.is_absolute() else target / path
    path = confined_target(path.parent.absolute(), PurePosixPath(path.name))
    current = path.read_bytes() if path.exists() else b''
    existing = current.decode('utf-8').splitlines()
    added = [value for value in patterns if value not in existing]
    if added:
        path.parent.mkdir(parents=True, exist_ok=True)
        content = current + (b'\n' if current and not current.endswith(b'\n') else b'')
        content += ('# SmartKit personal project configuration\n' + '\n'.join(added) + '\n').encode('utf-8')
        apply_plan(path.parent, build_plan(path.parent, [DesiredFile(PurePosixPath(path.name), content)]))
    return tracked


def _bind(args: argparse.Namespace, catalog: Catalog) -> dict:
    target = args.target.absolute()
    if args.mode == 'local':
        if args.repository or args.branch or args.entry or args.file or args.create_repository:
            raise ValueError('local mode does not accept repository arguments')
        selected = {'mode': 'local'}
    else:
        selected = {'mode': 'repository', 'repository': args.repository, 'branch': args.branch, 'entry': args.entry}
    parse_maintenance(selected)
    current = configuration._document(target, configuration.CONFIG, missing=True)
    previous = current.get('maintenance')
    switching = previous is not None and previous != selected
    if switching and not args.replace_binding:
        raise ValueError('maintenance binding already exists; an explicit switch requires --replace-binding')
    if switching:
        configuration.require_converged(target, catalog)
    config_before = configuration._json(current)
    result = {'mode': args.mode}
    if args.mode == 'repository':
        root = repository.checkout(args.repository, args.branch, create=args.create_repository)
        entry = confined_target(root, PurePosixPath('projects') / args.entry)
        if not (entry / 'manifest.json').exists():
            entry.mkdir(parents=True, exist_ok=True)
            configuration.initialize_entry(target, entry, args.file, catalog)
        elif args.file:
            raise ValueError('initial --file import is only valid for a new entry; explicitly adopt later edits')
        configuration.read_entry(entry, catalog)
        result['source'] = str(entry)
    if configuration._json(configuration._document(target, configuration.CONFIG, missing=True)) != config_before:
        raise ValueError('project config changed while binding was prepared; source work is retained')
    current['maintenance'] = selected
    deletes = [configuration.STATE] if switching else []
    plan = build_plan(target, [DesiredFile(configuration.CONFIG, configuration._json(current))], delete_paths=deletes)
    apply_plan(target, plan)
    result['bound'] = True
    result['tracked_paths'] = exclude_local(target, [str(configuration.CONFIG), str(configuration.STATE), *args.file]) if args.mode == 'repository' else []
    return result


def _publish(args: argparse.Namespace, catalog: Catalog) -> dict:
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
    configuration.require_converged(target, catalog)
    checked = synchronize_project(Path(__file__).resolve().parents[4], target, check_only=True)
    if checked.check != 'clean':
        raise ValueError('native project configuration has drift; synchronize it before publication')
    commit = args.commit or repository.commit_scope(checkout, selected.branch, args.path, args.message)
    try:
        # Hooks may modify source inputs; those bytes must reach the target before publication.
        configuration.require_converged(target, catalog)
        checked = synchronize_project(Path(__file__).resolve().parents[4], target, check_only=True)
        if checked.check != 'clean':
            raise ValueError('target needs synchronization after commit hooks')
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
        configuration.require_converged(target, load_catalog(source))
        synchronize = synchronize_project if command == 'sync-project' else synchronize_project_rules
        result = synchronize(source, target, check_only=args.check)
    except (OSError, ValueError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    output = {'phase': command, 'check': result.check, 'changed_paths': result.changed_paths}
    if command == 'sync-project':
        output['preserved_paths'] = result.preserved_paths
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
            result = configuration.inspect(target, catalog)
        elif command == 'apply':
            result = configuration.apply(target, catalog, accept_existing=args.accept_existing)
            result['tracked_paths'] = exclude_local(target, result['managed_paths'])
        elif command == 'adopt':
            result = configuration.adopt(target, catalog, args.file, args.field)
        elif command == 'update':
            selected = configuration.binding(target)
            if selected is None or selected.mode != 'repository':
                raise ValueError('update needs a repository maintenance binding')
            result = repository.update(repository.open_checkout(selected.repository, selected.branch), selected.branch)
        else:
            result = _publish(args, catalog)
        print(json.dumps({'operation': command, **result}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError, TransactionError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
