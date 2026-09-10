#!/usr/bin/env python
"""Deliver core Rules and a semantic loading index through native host Hooks."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

from contract import RuleConfigError, load_registry


def plugin_root() -> Path:
    configured = (
        os.environ.get('PLUGIN_ROOT')
        or os.environ.get('QODER_PLUGIN_ROOT')
        or os.environ.get('CURSOR_PLUGIN_ROOT')
        or os.environ.get('CLAUDE_PLUGIN_ROOT')
    )
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[2]


def context_for(root: Path) -> str:
    """Inline core Rules; leave every other loading decision to the Agent."""
    rules = load_registry(root)
    blocks: list[str] = []
    indexed: list[dict[str, str]] = []
    for rule in rules:
        if not rule['id'].startswith('smartkit/core-'):
            indexed.append(rule)
            continue
        text = (root / 'rules' / rule['source']).read_text(encoding='utf-8')
        blocks.append(
            f'<!-- Rule-ID: {rule["id"]}; Owner: plugin; Strength: {rule["strength"]}; '
            f'Source: rules/{rule["source"]} -->\n{text.strip()}'
        )
    if indexed:
        rows = [
            '## SmartKit Rule index',
            '',
            'The core Rules are included above. The indexed Rules are plugin-owned. '
            'Use the descriptions and current task to decide which Rules to read before '
            'related work. Read a Rule to check its relevance when uncertain, and re-read '
            'it whenever useful, including after context compaction. Apply the Rule '
            'strength and precedence defined above. If a required Rule '
            'cannot be read, report the failure before continuing the dependent work.',
            '',
            '| Description | Rule ID | Source | Strength |',
            '| --- | --- | --- | --- |',
        ]
        for rule in indexed:
            source = str((root / 'rules' / rule['source']).resolve())
            cells = (rule['description'], rule['id'], source, rule['strength'])
            rows.append('| ' + ' | '.join(cell.replace('|', '\\|') for cell in cells) + ' |')
        blocks.append('\n'.join(rows))
    return '\n\n'.join(blocks) + '\n'


def _state_path(root: Path, payload: dict[str, object], harness: str) -> Path:
    session = (
        payload.get('session_id') or payload.get('sessionId') or payload.get('conversation_id')
    )
    identity = str(session) if session else f'{Path.cwd().resolve()}:{os.getppid()}'
    digest = hashlib.sha256(f'{root.resolve()}:{harness}:{identity}'.encode()).hexdigest()
    configured = os.environ.get('PLUGIN_DATA')
    base = Path(configured) if configured else Path(tempfile.gettempdir()) / 'smartkit-rule-state'
    return base / 'rule-compaction' / f'{digest}.json'


def _session_state(path: Path) -> dict[str, int]:
    if not path.exists():
        return {'context_generation': 0, 'restored_generation': 0}
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except OSError as error:
        raise RuleConfigError(f'cannot read Rule compaction state: {error}') from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuleConfigError(f'invalid Rule compaction state: {error}') from error
    if (
        not isinstance(value, dict)
        or set(value) != {'context_generation', 'restored_generation'}
        or any(type(item) is not int or item < 0 for item in value.values())
        or value['restored_generation'] > value['context_generation']
    ):
        raise RuleConfigError('invalid Rule compaction state')
    return value


def _store_session_state(path: Path, state: dict[str, int]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f'.{os.getpid()}.tmp')
        temporary.write_text(json.dumps(state, sort_keys=True) + '\n', encoding='utf-8')
        os.replace(temporary, path)
    except OSError as error:
        raise RuleConfigError(f'cannot write Rule compaction state: {error}') from error


def delivery(
    root: Path, payload: dict[str, object], event: str, harness: str,
) -> dict[str, object]:
    if harness not in {'codex', 'copilot', 'cursor', 'qoder'}:
        raise RuleConfigError(f'unsupported Rule Harness: {harness}')
    events = {'session'}
    if harness == 'copilot':
        events.update({'prompt', 'compact', 'tool', 'stop'})
    elif harness == 'cursor':
        events.update({'compact', 'tool', 'stop'})
    if event not in events:
        raise RuleConfigError(f'unsupported Rule delivery event for {harness}: {event}')

    if harness in {'copilot', 'cursor'}:
        state_path = _state_path(root, payload, harness)
        state = _session_state(state_path)
        if event == 'compact':
            state['context_generation'] += 1
            _store_session_state(state_path, state)
            return {}
        restore_required = state['restored_generation'] < state['context_generation']
        if event != 'session' and not restore_required:
            return {}
        if harness == 'cursor' and event == 'stop' and payload.get('status') != 'completed':
            return {}

    context = context_for(root)
    if harness in {'copilot', 'cursor'} and restore_required:
        state['restored_generation'] = state['context_generation']
        _store_session_state(state_path, state)

    if event == 'session':
        if harness == 'copilot':
            return {'additionalContext': context}
        if harness == 'cursor':
            return {'additional_context': context}
        return {'hookSpecificOutput': {
            'hookEventName': 'SessionStart',
            'additionalContext': context,
        }}
    if event == 'prompt':
        original = str(payload.get('transformedPrompt') or payload.get('prompt') or '')
        return {'modifiedTransformedPrompt': f'{context}\n{original}'}
    if event == 'tool':
        reason = (
            f'{context}\nSmartKit restored core Rules and the Rule index after context '
            'compaction. Read the applicable Rules, then retry the same tool call.'
        )
        if harness == 'cursor':
            return {'permission': 'deny', 'agent_message': reason}
        return {'permissionDecision': 'deny', 'permissionDecisionReason': reason}
    reason = (
        f'{context}\nSmartKit restored core Rules and the Rule index after context '
        'compaction. Read the applicable Rules, review the proposed answer against them, '
        'revise it if needed, and then finish the turn.'
    )
    if harness == 'cursor':
        return {'followup_message': reason}
    return {'decision': 'block', 'reason': reason}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--harness', choices=('codex', 'copilot', 'cursor', 'qoder'), required=True)
    parser.add_argument(
        '--event', choices=('session', 'prompt', 'tool', 'compact', 'stop'), required=True,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = json.load(sys.stdin)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f'SmartKit Rule delivery skipped: invalid Hook payload: {error}', file=sys.stderr)
        return 1
    if not isinstance(payload, dict):
        print(
            'SmartKit Rule delivery skipped: invalid Hook payload: expected a JSON object',
            file=sys.stderr,
        )
        return 1
    try:
        output = delivery(plugin_root(), payload, args.event, args.harness)
    except (OSError, UnicodeDecodeError, RuleConfigError) as error:
        print(f'SmartKit Rule delivery skipped: {error}', file=sys.stderr)
        return 1
    encoded = json.dumps(output)
    if output:
        print(
            'SmartKit Rule delivery attempted: '
            f'harness={args.harness}, event={args.event}, response_bytes={len(encoded.encode())}. '
            'Host trust, acceptance, spill, and truncation remain host-owned; '
            'inspect the host Hook diagnostics if expected Rule behavior is absent.',
            file=sys.stderr,
        )
    print(encoded)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
