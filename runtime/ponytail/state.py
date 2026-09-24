#!/usr/bin/env python
"""Persist Ponytail defaults separately from explicitly identified conversation state."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sys
import tempfile


MODES = ('off', 'lite', 'full', 'ultra')
HARNESSES = ('codex', 'copilot', 'cursor', 'qoder')


class StateError(ValueError):
    """The requested mode operation could not preserve its state contract."""


def config_path() -> Path:
    if os.name == 'nt':
        configured = os.environ.get('APPDATA') or str(Path.home() / 'AppData' / 'Roaming')
    else:
        configured = os.environ.get('XDG_CONFIG_HOME')
    base = Path(configured) if configured else Path.home() / '.config'
    return base / 'smartkit' / 'ponytail.json'


def state_path(handle: str) -> Path:
    if re.fullmatch(r'[0-9a-f]{64}', handle) is None:
        raise StateError('invalid Ponytail conversation handle')
    configured = os.environ.get('XDG_STATE_HOME')
    if not configured and os.name == 'nt':
        configured = os.environ.get('LOCALAPPDATA') or os.environ.get('APPDATA')
    base = Path(configured) if configured else Path.home() / '.local' / 'state'
    return base / 'smartkit' / 'ponytail' / f'{handle}.json'


def read_object(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding='utf-8-sig'))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StateError(f'invalid Ponytail JSON: {path}: {error}') from error
    if not isinstance(value, dict):
        raise StateError(f'Ponytail state must be a JSON object: {path}')
    return value


def mode_value(value: object) -> str:
    if not isinstance(value, str) or value not in MODES:
        raise StateError('Ponytail mode must be off, lite, full, or ultra')
    return value


def store(path: Path, value: dict[str, object], *, initialize: bool = False) -> None:
    """Publish complete JSON atomically; initialization never overwrites an existing choice."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(json.dumps(value, sort_keys=True) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        if initialize:
            try:
                os.link(temporary, path)
            except FileExistsError:
                pass  # Another initializer published first; its complete state remains authoritative.
        else:
            os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def default_mode() -> str:
    override = os.environ.get('PONYTAIL_DEFAULT_MODE')
    if override:
        return mode_value(override.strip().lower())
    path = config_path()
    try:
        config = read_object(path)
    except FileNotFoundError:
        return 'full'
    return mode_value(config.get('defaultMode', 'full'))


def show(handle: str) -> dict[str, str]:
    try:
        state = read_object(state_path(handle))
    except FileNotFoundError as error:
        raise StateError('Ponytail conversation state is missing; restore its original handle') from error
    return {'handle': handle, 'mode': mode_value(state.get('mode'))}


def initialize(harness: str, session_id: str) -> dict[str, str]:
    if harness not in HARNESSES or not session_id.strip():
        raise StateError('a supported Harness and nonempty native conversation ID are required')
    handle = hashlib.sha256(f'{harness}\0{session_id}'.encode()).hexdigest()
    path = state_path(handle)
    if not path.exists():
        store(path, {'mode': default_mode()}, initialize=True)
    return show(handle)


def session_context(payload: dict[str, object], harness: str) -> str:
    identity = (payload.get('conversation_id') or payload.get('session_id')) if harness == 'cursor' else (
        payload.get('sessionId') if harness == 'copilot' else payload.get('session_id')
    )
    if not isinstance(identity, str) or not identity.strip():
        return ('Ponytail session state unavailable: the host supplied no native conversation ID. '
                'Do not substitute a project path, process ID, or shared state file.\n')
    state = initialize(harness, identity)
    return (f'Ponytail host conversation handle: {state["handle"]}; mode: {state["mode"]}. '
            'A delegated Ponytail handle in the task takes precedence over this host handle. '
            'Before any delegation, load the ponytail Skill and follow its child-state '
            'inheritance protocol, including for non-coding tasks and off mode. '
            'Use that Skill for mode operations; preserve the selected handle on handoff.\n')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init')
    init.add_argument('--harness', choices=HARNESSES, required=True)
    init.add_argument('--session-id', required=True)
    for command in ('show', 'set', 'fork'):
        child = commands.add_parser(command)
        child.add_argument('--handle', required=True)
        if command == 'set':
            child.add_argument('mode', choices=MODES)
    default = commands.add_parser('default')
    default.add_argument('mode', choices=MODES, nargs='?')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            result = initialize(args.harness, args.session_id)
        elif args.command == 'show':
            result = show(args.handle)
        elif args.command == 'set':
            show(args.handle)
            store(state_path(args.handle), {'mode': args.mode})
            result = show(args.handle)
        elif args.command == 'fork':
            parent = show(args.handle)
            handle = secrets.token_hex(32)
            store(state_path(handle), {'mode': parent['mode']}, initialize=True)
            result = show(handle)
        else:
            path = config_path()
            try:
                config = read_object(path)
            except FileNotFoundError:
                config = {}
            saved = mode_value(config.get('defaultMode', 'full'))
            if args.mode is not None:
                saved = args.mode
            override = os.environ.get('PONYTAIL_DEFAULT_MODE')
            effective = mode_value(override.strip().lower()) if override else saved
            if args.mode is not None:
                config['defaultMode'] = args.mode
                store(path, config)
            result = {'defaultMode': saved, 'effectiveDefaultMode': effective}
        print(json.dumps(result))
        return 0
    except (OSError, StateError) as error:
        print(f'Ponytail state failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
