"""Inspect project-native Agents and atomically import an explicitly reconciled adoption plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from dataclasses import replace
import agents_setup  # Expose the supported maintenance engine.
from project_config import project_configuration

from project_state.catalog import load_catalog
from project_config.catalog import load_project_config, parse_project_agents
from agents_setup.agent_discovery import (
    CODEX_CONFIG,
    HOST_PATHS as _HOST_PATHS,
    discover_native_agents,
)
from project_state.paths import is_link_like
from project_config.models import DesiredFile
from project_state.ownership import OWNERSHIP_PATH
from project_config.ownership import load_ownership, verify_ownership
from project_config.planner import build_plan
from project_state.paths import confined_target
from project_state.structured import parse_document
from project_config.transaction import TransactionError, apply_plan


_CONFIG = PurePosixPath('.agents/config.json')


def _digest(content: bytes | None) -> str | None:
    return None if content is None else hashlib.sha256(content).hexdigest()


def _read(target: Path, relative: PurePosixPath) -> bytes | None:
    path = confined_target(target, relative)
    return path.read_bytes() if path.exists() else None


def inspect(target: Path) -> dict[str, object]:
    source = Path(__file__).resolve().parents[3]
    state = load_ownership(target, catalog=load_catalog(source))
    roles = {asset.path: asset.role for asset in state.assets} if state else {}
    candidates = []
    discovery = discover_native_agents(target)
    for agent in discovery.agents:
        directory, suffix = _HOST_PATHS[agent.harness]
        canonical = PurePosixPath(
            f'.agents/agents/{agent.id}.{agent.harness}.{"toml" if agent.harness == "codex" else "md"}'
        )
        candidates.append({
            'id': agent.id, 'harness': agent.harness, 'path': agent.path.as_posix(),
            'sha256': _digest(_read(target, agent.path)), 'ownership': roles.get(agent.path, 'unmanaged'),
            'canonical_path': canonical.as_posix(),
            'canonical_sha256': _digest(_read(target, canonical)),
            'references': list(agent.references),
            'requires_relocation': agent.path != PurePosixPath(f'{directory}/{agent.id}{suffix}'),
        })
    return {
        'config_sha256': _digest(_read(target, _CONFIG)), 'agents': candidates,
        'role_declarations': [
            {'id': identity, 'harness': 'codex', 'path': CODEX_CONFIG.as_posix(), 'field': f'agents.{identity}'}
            for identity in discovery.codex_roles_without_config_file
        ],
        'issues': list(discovery.issues),
    }


def apply(target: Path, manifest: dict[str, object]) -> list[str]:
    """Import checked bytes; semantic preservation and model choices belong to the caller."""
    if not isinstance(manifest, dict) or set(manifest) != {'config_sha256', 'agents'}:
        raise ValueError('adoption manifest requires config_sha256 and agents')
    source = Path(__file__).resolve().parents[3]
    catalog = load_catalog(source)
    discovery = discover_native_agents(target)
    if discovery.issues:
        raise ValueError('; '.join(discovery.issues))
    ownership_content = _read(target, OWNERSHIP_PATH)
    state = load_ownership(target, catalog=catalog)
    verify_ownership(target, state)
    if _read(target, OWNERSHIP_PATH) != ownership_content:
        raise ValueError('Agent ownership changed while it was inspected')
    owned = {asset.path: asset for asset in state.assets} if state else {}
    original = _read(target, _CONFIG)
    if _digest(original) != manifest['config_sha256']:
        raise ValueError('project config changed after Agent inspection')
    load_project_config(target / _CONFIG, catalog=catalog)
    config = {} if original is None else json.loads(original)
    declarations = {item['id']: item for item in config.get('agents', [])}
    entries = manifest['agents']
    if not isinstance(entries, list) or not entries:
        raise ValueError('adoption agents must be a nonempty array')
    files: dict[PurePosixPath, bytes] = {}
    guards: dict[PurePosixPath, bytes | None] = {
        _CONFIG: original, OWNERSHIP_PATH: ownership_content,
    }
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'id', 'description', 'harnesses'}:
            raise ValueError('adoption Agent requires id, description, and harnesses')
        agent_id = entry['id']
        if not isinstance(agent_id, str) or agent_id in seen:
            raise ValueError('adoption Agent IDs must be unique strings')
        seen.add(agent_id)
        declared = dict(declarations.get(agent_id, {'id': agent_id}))
        if 'description' in declared and declared['description'] != entry['description']:
            raise ValueError(f'Agent description conflicts with project config: {agent_id}')
        declared['description'] = entry['description']
        harnesses = dict(declared.get('harnesses', {}))
        proposed = entry['harnesses']
        if not isinstance(proposed, dict) or not proposed:
            raise ValueError('adoption harnesses must be a nonempty object')
        for host, inputs in proposed.items():
            if host not in _HOST_PATHS or not isinstance(inputs, dict) or set(inputs) != {
                'path', 'sha256', 'canonical_sha256', 'content_file',
            }:
                raise ValueError('adoption harness requires path, sha256, canonical_sha256, content_file')
            directory, suffix = _HOST_PATHS[host]
            native = PurePosixPath(f'{directory}/{agent_id}{suffix}')
            canonical = PurePosixPath(
                f'.agents/agents/{agent_id}.{host}.{"toml" if host == "codex" else "md"}'
            )
            if inputs['path'] != native.as_posix():
                raise ValueError(f'Agent path needs explicit relocation before adoption: {inputs["path"]}')
            before = _read(target, native)
            if before is None or _digest(before) != inputs['sha256']:
                raise ValueError(f'native Agent changed after inspection: {native}')
            old_canonical = _read(target, canonical)
            if _digest(old_canonical) != inputs['canonical_sha256']:
                raise ValueError(f'canonical Agent changed after inspection: {canonical}')
            previous = harnesses.get(host)
            expected = {'native_source': canonical.as_posix()}
            asset = owned.get(native)
            if previous is not None and previous != expected and (
                asset is None or asset.kind != 'file' or asset.role != 'project-agent'
            ):
                raise ValueError(f'Agent {agent_id}/{host} has competing mapped settings; resolve source ownership before adoption')
            if old_canonical is not None and previous != expected:
                raise ValueError(f'canonical Agent path is independently owned: {canonical}')
            content_path = inputs['content_file']
            if not isinstance(content_path, str) or not content_path:
                raise ValueError('adoption content_file must name a prepared file')
            content_file = Path(content_path)
            if is_link_like(content_file):
                raise ValueError('adoption content must be a regular file')
            content = content_file.read_bytes()
            if not content.decode('utf-8').strip():
                raise ValueError('adoption content must be nonempty UTF-8')
            if host == 'codex':
                parse_document(content, 'toml')
            if asset is not None and (asset.kind != 'file' or asset.role != 'project-agent'):
                raise ValueError(f'native Agent belongs to another owner: {native}')
            files[canonical] = content
            guards[canonical] = old_canonical
            guards[native] = before
            if asset is None:
                files[native] = content
            harnesses[host] = expected
        declared['harnesses'] = harnesses
        parse_project_agents([declared])
        declarations[agent_id] = declared
    config['agents'] = list(declarations.values())
    parse_project_agents(config['agents'])
    config_bytes = (json.dumps(config, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    files[_CONFIG] = original if original is not None and json.loads(original) == config else config_bytes
    # An existing lock is an unchanged transaction input, never an adoption output.
    if ownership_content is not None:
        files[OWNERSHIP_PATH] = ownership_content
    plan = build_plan(target, [DesiredFile(path, content) for path, content in files.items()])
    for path, before in guards.items():
        if _read(target, path) != before:
            raise ValueError(f'Agent adoption input changed during planning: {path}')

    def postcondition() -> None:
        project_configuration.require_converged(target, catalog)
        for path, before in guards.items():
            expected_content = files.get(path, before)
            if _read(target, path) != expected_content:
                raise ValueError(f'Agent adoption did not converge: {path}')

    receipt = project_configuration.save_generated(
        target, catalog,
        {str(path): content for path, content in files.items() if path.parts[:2] == ('.agents', 'agents')},
        [], portable_config=config,
    )
    if receipt is not None:
        plan = replace(plan, changes=(*plan.changes, *build_plan(target, [receipt]).changes))
    apply_plan(target, plan, postcondition=postcondition)
    return [change.path.as_posix() for change in plan.changes if change.kind.value != 'unchanged']


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('inspect', 'apply'):
        child = commands.add_parser(command)
        child.add_argument('--target', type=Path, required=True)
        if command == 'apply':
            child.add_argument('--manifest', type=Path, required=True,
                               help='JSON: config_sha256 and agents[{id,description,harnesses:{host:{path,sha256,canonical_sha256,content_file}}}]')
    args = parser.parse_args(argv)
    try:
        target = args.target.absolute()
        if args.command == 'inspect':
            result = inspect(target)
        else:
            manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
            result = {'changed_paths': apply(target, manifest)}
        print(json.dumps(result, ensure_ascii=False))
        return 2 if result.get('issues') else 0
    except (OSError, ValueError, TransactionError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
