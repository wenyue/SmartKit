from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


TOKSCALE_TIMEOUT_SECONDS = 30
SUPPORTED_CLIENTS = ('codex', 'cursor', 'copilot')
TOKEN_FIELDS = ('input', 'output', 'reasoning', 'cache_read', 'cache_write')
USAGE_ACTIVITY_FIELDS = ('message_count', 'model_activity_ms')
COORDINATION_TOOLS = (
    'spawn_agent',
    'wait_agent',
    'list_agents',
    'send_message',
    'followup_task',
    'interrupt_agent',
)
TERMINAL_AGENT_STATES = ('completed', 'failed', 'cancelled', 'canceled', 'errored')
BEHAVIOR_CAPABILITY_NAMES = (
    'tool calls',
    'incomplete calls',
    'subagent lifecycle',
    'agent coordination',
    'waits',
)
DIAGNOSTIC_SCOPES = ('turn', 'session', 'both')
PROFILE_LABELS = {
    'codex': 'Codex',
    'cursor': 'Cursor',
    'copilot': 'GitHub Copilot CLI',
}
SESSION_ID_LITERAL = r'[A-Za-z0-9._:\-]+'
SESSION_ID_PATTERN = re.compile(SESSION_ID_LITERAL)
ACQUISITION_ID_LITERAL = r'[a-f0-9]{64}'
ACQUISITION_ID_PATTERN = re.compile(ACQUISITION_ID_LITERAL)
TOKSCALE_EFFECTS = (
    'scan selected client session records in the requested date window or available local history when bounds are unavailable, and read existing Tokscale identity state',
    'may access Tokscale pricing or provider endpoints',
    'may read or write Tokscale-owned config and cache directories',
)


class UsageError(RuntimeError):
    pass


def validate_client(client: str) -> str:
    if client not in SUPPORTED_CLIENTS:
        supported = ', '.join(SUPPORTED_CLIENTS)
        raise UsageError(
            f'Unsupported client {client!r}; supported clients are: {supported}.'
        )
    return client


def validate_session_id(session_id: str) -> str:
    if not isinstance(session_id, str) or SESSION_ID_PATTERN.fullmatch(session_id) is None:
        raise UsageError(
            'Session ID must contain only letters, digits, dot, underscore, colon, or hyphen.'
        )
    return session_id


def validate_acquisition_id(acquisition_id: str) -> str:
    if (
        not isinstance(acquisition_id, str)
        or ACQUISITION_ID_PATTERN.fullmatch(acquisition_id) is None
    ):
        raise UsageError('Acquisition ID must be exactly 64 lowercase hexadecimal digits.')
    return acquisition_id


def _requested_scopes(selected_scope: str) -> tuple[str, ...]:
    if selected_scope == 'turn':
        return ('turn',)
    if selected_scope == 'session':
        return ('session',)
    if selected_scope == 'both':
        return ('turn', 'session')
    raise UsageError(f'Unsupported diagnostic scope: {selected_scope}')


def _validate_supported_scope(client: str, selected_scope: str) -> None:
    validate_client(client)
    requested = _requested_scopes(selected_scope)
    if client != 'codex' and requested == ('turn',):
        raise UsageError(
            f'{PROFILE_LABELS[client]} turn-only diagnosis is unsupported: '
            'this package has no turn-bounded evidence source for that client. '
            'Use --scope session or --scope both when whole-session Tokscale '
            'evidence is required.'
        )


def _timestamp(now: datetime | None = None) -> datetime:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        raise UsageError('Usage timestamps require timezone information.')
    return value.astimezone(timezone.utc)


def _serialize_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec='microseconds')


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise UsageError(f'Usage timestamp has no timezone: {value}')
    return parsed.astimezone(timezone.utc)


def _duration_milliseconds(start: datetime, end: datetime) -> int:
    delta = end - start
    if delta.total_seconds() < 0:
        raise UsageError('Diagnostic timestamps must remain chronological.')
    return int(delta.total_seconds() * 1000)


def session_id_matches(client: str, candidate: str, requested: str) -> bool:
    client = validate_client(client)
    if candidate == requested:
        return True
    return client == 'codex' and candidate == f'rollout-{requested}'


def _tokscale_session_id(row: dict[str, Any]) -> str:
    has_camel = 'sessionId' in row
    has_snake = 'session_id' in row
    if has_camel and has_snake and row['sessionId'] != row['session_id']:
        raise UsageError(
            'Tokscale fields sessionId and session_id contain conflicting values.'
        )
    value = row['sessionId'] if has_camel else row.get('session_id')
    return _required_text(value, 'sessionId')


def _matching_tokscale_rows(
    client: str,
    requested: str,
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    matching = []
    aliases = set()
    groups = set()
    for row in rows:
        if row.get('client') != client:
            continue
        candidate = _tokscale_session_id(row)
        if not session_id_matches(client, candidate, requested):
            continue
        normalized = normalize_usage_row(row)
        group = (
            normalized['session_id'],
            normalized['model'],
        )
        if group in groups:
            raise UsageError(
                'Tokscale returned duplicate rows for the requested '
                'client/session/model attribution.'
            )
        groups.add(group)
        aliases.add(normalized['session_id'])
        matching.append(row)
    if len(aliases) > 1:
        raise UsageError(
            'Tokscale returned both exact and normalized Codex session aliases; '
            'attribution is ambiguous.'
        )
    return matching


def _integer(
    value: Any,
    field: str,
    *,
    allow_none: bool = True,
    require_json_number: bool = False,
) -> int:
    if value is None:
        if not allow_none:
            raise UsageError(f'Tokscale field {field} must not be null.')
        return 0
    if isinstance(value, bool):
        raise UsageError(f'Tokscale field {field} must be numeric.')
    if require_json_number and not isinstance(value, (int, float)):
        raise UsageError(f'Tokscale field {field} must be numeric.')
    if isinstance(value, float) and not math.isfinite(value):
        raise UsageError(f'Tokscale field {field} must be finite.')
    if isinstance(value, float) and not value.is_integer():
        raise UsageError(f'Tokscale field {field} must be an integer.')
    try:
        result = int(value)
    except OverflowError as error:
        raise UsageError(f'Tokscale field {field} must be finite.') from error
    except (TypeError, ValueError) as error:
        raise UsageError(f'Tokscale field {field} must be numeric.') from error
    if result < 0:
        raise UsageError(f'Tokscale field {field} must not be negative.')
    return result


def _number(
    value: Any,
    field: str,
    *,
    allow_none: bool = True,
    require_json_number: bool = False,
) -> float:
    if value is None:
        if not allow_none:
            raise UsageError(f'Tokscale field {field} must not be null.')
        return 0.0
    if isinstance(value, bool):
        raise UsageError(f'Tokscale field {field} must be numeric.')
    if require_json_number and not isinstance(value, (int, float)):
        raise UsageError(f'Tokscale field {field} must be numeric.')
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise UsageError(f'Tokscale field {field} must be numeric.') from error
    if not math.isfinite(result):
        raise UsageError(f'Tokscale field {field} must be finite.')
    if result < 0:
        raise UsageError(f'Tokscale field {field} must not be negative.')
    return result


def _tokscale_integer_alias(
    representations: tuple[tuple[str, bool, Any], ...],
    field: str,
) -> int:
    values = [
        (
            name,
            _integer(
                value,
                name,
                allow_none=False,
                require_json_number=True,
            ),
        )
        for name, present, value in representations
        if present
    ]
    if not values:
        return _integer(
            None,
            field,
            allow_none=False,
            require_json_number=True,
        )
    if any(value != values[0][1] for _, value in values[1:]):
        names = ' and '.join(name for name, _ in values)
        raise UsageError(f'Tokscale fields {names} contain conflicting values.')
    return values[0][1]


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise UsageError(f'Tokscale field {field} must be a nonempty string.')
    return value


def normalize_usage_row(row: dict[str, Any]) -> dict[str, Any]:
    performance = row.get('performance', {})
    if not isinstance(performance, dict):
        raise UsageError('Tokscale performance data must be an object.')
    provider = row.get('provider')
    return {
        'client': _required_text(row.get('client'), 'client'),
        'session_id': _tokscale_session_id(row),
        'provider': '' if provider is None else _required_text(provider, 'provider'),
        'model': _required_text(row.get('model'), 'model'),
        'input': _integer(
            row.get('input'), 'input', allow_none=False, require_json_number=True
        ),
        'output': _integer(
            row.get('output'), 'output', allow_none=False, require_json_number=True
        ),
        'reasoning': _integer(
            row.get('reasoning'),
            'reasoning',
            allow_none=False,
            require_json_number=True,
        ),
        'cache_read': _tokscale_integer_alias(
            (
                ('cacheRead', 'cacheRead' in row, row.get('cacheRead')),
                ('cache_read', 'cache_read' in row, row.get('cache_read')),
            ),
            'cacheRead',
        ),
        'cache_write': _tokscale_integer_alias(
            (
                ('cacheWrite', 'cacheWrite' in row, row.get('cacheWrite')),
                ('cache_write', 'cache_write' in row, row.get('cache_write')),
            ),
            'cacheWrite',
        ),
        'cost': _number(
            row.get('cost'), 'cost', allow_none=False, require_json_number=True
        ),
        'message_count': _tokscale_integer_alias(
            (
                ('messageCount', 'messageCount' in row, row.get('messageCount')),
                ('message_count', 'message_count' in row, row.get('message_count')),
            ),
            'messageCount',
        ),
        'model_activity_ms': _tokscale_integer_alias(
            (
                (
                    'performance.totalDurationMs',
                    'totalDurationMs' in performance,
                    performance.get('totalDurationMs'),
                ),
                (
                    'model_activity_ms',
                    'model_activity_ms' in row,
                    row.get('model_activity_ms'),
                ),
            ),
            'performance.totalDurationMs',
        ),
    }


def _empty_usage_totals() -> dict[str, int | float]:
    return {
        'input': 0,
        'output': 0,
        'reasoning': 0,
        'cache_read': 0,
        'cache_write': 0,
        'total_tokens': 0,
        'cost': 0.0,
        'message_count': 0,
        'model_activity_ms': 0,
    }


def _aggregate_usage(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int | float]]:
    normalized_rows = [normalize_usage_row(row) for row in rows]
    totals = _empty_usage_totals()
    for row in normalized_rows:
        for field in TOKEN_FIELDS:
            totals[field] += row[field]
        for field in USAGE_ACTIVITY_FIELDS:
            totals[field] += row[field]
        totals['cost'] += row['cost']
    totals['total_tokens'] = sum(int(totals[field]) for field in TOKEN_FIELDS)
    return normalized_rows, totals


def _tokscale_date(value: datetime) -> str:
    return value.astimezone().date().isoformat()


def tokscale_executable(
    *,
    os_name: str | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> str:
    platform = os_name or os.name
    candidates = ('tokscale.cmd', 'tokscale.exe') if platform == 'nt' else ('tokscale',)
    for candidate in candidates:
        resolved = which(candidate)
        if resolved:
            return resolved
    raise UsageError('Installed Tokscale executable was not found on PATH.')


def _run_tokscale(
    command: list[str],
    runner: Callable[..., subprocess.CompletedProcess[str]],
    operation: str,
) -> subprocess.CompletedProcess[str]:
    try:
        completed = runner(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=TOKSCALE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise UsageError(
            f'Tokscale {operation} timed out after {TOKSCALE_TIMEOUT_SECONDS} seconds.'
        ) from error
    except OSError as error:
        raise UsageError(f'Tokscale {operation} could not run: {error}') from error
    if completed.returncode != 0:
        raise UsageError(
            f'Tokscale {operation} exited with code {completed.returncode}; '
            'provider output was withheld.'
        )
    return completed


def read_tokscale_version(
    executable: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> str:
    completed = _run_tokscale([executable, '--version'], runner, 'version probe')
    match = re.fullmatch(
        r'tokscale\s+([0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?)\s*',
        completed.stdout,
    )
    if match is None:
        raise UsageError('Tokscale version output used an unsupported schema.')
    return match.group(1)


def probe_tokscale_identity(
    client: str,
    executable: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, str | None]:
    if client != 'cursor':
        return {'status': 'not-required', 'reason': None}
    try:
        completed = runner(
            [executable, 'cursor', 'status'],
            capture_output=True,
            text=True,
            check=False,
            timeout=TOKSCALE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {
            'status': 'failed',
            'reason': 'Tokscale Cursor identity probe timed out.',
        }
    except OSError:
        return {
            'status': 'failed',
            'reason': 'Tokscale Cursor identity probe could not run.',
        }
    if completed.returncode != 0:
        return {
            'status': 'unavailable',
            'reason': 'No existing valid Tokscale Cursor identity was available.',
        }
    return {'status': 'available', 'reason': None}


def acquire_tokscale_evidence(
    client: str,
    session_id: str,
    started_at: datetime | None,
    ended_at: datetime | None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    *,
    now: Callable[[], datetime] = _timestamp,
) -> dict[str, Any]:
    """Acquire one versioned provider record without retaining provider output."""
    client = validate_client(client)
    session_id = validate_session_id(session_id)
    observed_from = now()
    executable = None
    version = None
    schema_status = 'not-validated'
    identity = {'status': 'unknown', 'reason': None}
    rows: list[dict[str, Any]] = []
    error = None
    try:
        executable = tokscale_executable()
        version = read_tokscale_version(executable, runner)
        identity = probe_tokscale_identity(client, executable, runner)
        rows = capture_tokscale_snapshot(
            client,
            started_at,
            ended_at,
            runner,
            session_id=session_id,
            executable=executable,
        )
        schema_status = 'validated'
        _matching_tokscale_rows(client, session_id, rows)
    except UsageError as caught:
        error = str(caught)
        rows = []
    observed_through = now()
    return {
        'outcome': 'failed' if error else 'succeeded',
        'cause': error,
        'executable': executable,
        'version': version,
        'schema_status': schema_status,
        'identity': identity,
        'observed_from': _serialize_timestamp(observed_from),
        'observed_through': _serialize_timestamp(observed_through),
        'rows': rows,
        'effects': list(TOKSCALE_EFFECTS),
    }


def capture_tokscale_snapshot(
    client: str,
    started_at: datetime | None,
    ended_at: datetime | None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    *,
    session_id: str | None = None,
    executable: str | None = None,
) -> list[dict[str, Any]]:
    client = validate_client(client)
    command = [
        executable or tokscale_executable(),
        '--json',
        '--client',
        client,
    ]
    if started_at is not None and ended_at is not None:
        command.extend(
            [
                '--since',
                _tokscale_date(started_at),
                '--until',
                _tokscale_date(ended_at),
            ]
        )
    command.extend(['--group-by', 'client,session,model', '--no-spinner'])
    completed = _run_tokscale(command, runner, f'collection for client {client}')
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise UsageError(f'Tokscale returned invalid JSON for client {client}.') from error
    if not isinstance(payload, dict) or not isinstance(payload.get('entries'), list):
        raise UsageError(f'Tokscale JSON for client {client} has no entries array.')
    entries = payload['entries']
    selected_entries = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise UsageError(
                f'Tokscale JSON for client {client} contains a non-object entry.'
            )
        entry_client = _required_text(entry.get('client'), 'client')
        if entry_client != client:
            raise UsageError(
                f'Tokscale JSON for client {client} contains a row for '
                f'client {entry_client}.'
            )
        entry_session = _tokscale_session_id(entry)
        if session_id is not None and not session_id_matches(
            client, entry_session, session_id
        ):
            continue
        required = (
            ('client',),
            ('sessionId', 'session_id'),
            ('model',),
            ('input',),
            ('output',),
            ('reasoning',),
            ('cacheRead', 'cache_read'),
            ('cacheWrite', 'cache_write'),
            ('cost',),
            ('messageCount', 'message_count'),
            ('performance', 'model_activity_ms'),
        )
        missing = [
            '/'.join(names) for names in required if not any(name in entry for name in names)
        ]
        if missing:
            raise UsageError(
                'Tokscale JSON is incompatible with session diagnostics; '
                f"missing normalized field(s): {', '.join(missing)}."
            )
        performance = entry.get('performance')
        if (
            'model_activity_ms' not in entry
            and (
                not isinstance(performance, dict)
                or 'totalDurationMs' not in performance
            )
        ):
            raise UsageError(
                'Tokscale JSON is incompatible with session diagnostics; '
                'missing normalized field: performance.totalDurationMs.'
            )
        normalize_usage_row(entry)
        selected_entries.append(entry)
    return selected_entries


def detect_current_session(
    client: str | None = None, session_id: str | None = None
) -> tuple[str | None, str | None]:
    client_supplied = client is not None
    session_id_supplied = session_id is not None
    if client_supplied or session_id_supplied:
        if not client_supplied or not session_id_supplied:
            raise UsageError('Client and session ID must be provided together.')
        return validate_client(client), validate_session_id(session_id)
    codex_session = os.environ.get('CODEX_THREAD_ID')
    if codex_session:
        return 'codex', validate_session_id(codex_session)
    return None, None


def _codex_log_paths(codex_home: Path, session_id: str) -> list[Path]:
    timestamped_name = re.compile(
        r'^rollout-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-'
        + re.escape(session_id)
        + r'$'
    )

    def matches(path: Path) -> bool:
        return path.stem in (session_id, f'rollout-{session_id}') or bool(
            timestamped_name.fullmatch(path.stem)
        )

    paths = []
    for root in (codex_home / 'sessions', codex_home / 'archived_sessions'):
        if root.is_dir():
            paths.extend(
                path
                for path in root.rglob('*.jsonl')
                if matches(path)
            )
    return sorted(set(paths))


def _validate_codex_tool_event(event: dict[str, Any]) -> None:
    if event.get('type') != 'response_item':
        return
    payload = event.get('payload') or {}
    payload_type = payload.get('type')
    if payload_type in ('custom_tool_call', 'function_call'):
        if not isinstance(payload.get('call_id'), str) or not payload['call_id']:
            raise UsageError('Codex tool call_id must be a nonempty string.')
        if not isinstance(payload.get('name'), str) or not payload['name']:
            raise UsageError('Codex tool name must be a nonempty string.')
        arguments_field = 'input' if payload_type == 'custom_tool_call' else 'arguments'
        if arguments_field not in payload:
            raise UsageError(
                f'Codex {payload_type} must contain {arguments_field}.'
            )
    elif payload_type in ('custom_tool_call_output', 'function_call_output'):
        if not isinstance(payload.get('call_id'), str) or not payload['call_id']:
            raise UsageError('Codex tool call_id must be a nonempty string.')
        if 'output' not in payload:
            raise UsageError(f'Codex {payload_type} must contain output.')


def _coherent_codex_tool_events(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    open_calls = {}
    completed_calls = set()
    coherent = []
    invalid = 0
    for event in events:
        if event.get('type') != 'response_item':
            coherent.append(event)
            continue
        payload = event.get('payload') or {}
        payload_type = payload.get('type')
        call_id = payload.get('call_id')
        if payload_type in ('custom_tool_call', 'function_call'):
            if call_id in open_calls or call_id in completed_calls:
                invalid += 1
                continue
            open_calls[call_id] = f'{payload_type}_output'
        elif payload_type in ('custom_tool_call_output', 'function_call_output'):
            if open_calls.get(call_id) != payload_type:
                invalid += 1
                continue
            del open_calls[call_id]
            completed_calls.add(call_id)
        coherent.append(event)
    return coherent, invalid


def _load_codex_log_snapshot(
    session_id: str,
    codex_home: Path | None = None,
    captured_at: datetime | None = None,
    *,
    capture_cutoff_after_read: bool = False,
) -> dict[str, Any]:
    observation_started = (
        _timestamp(captured_at)
        if captured_at is not None
        else _timestamp() if capture_cutoff_after_read else None
    )
    configured_home = os.environ.get('CODEX_HOME')
    root = (
        codex_home
        if codex_home is not None
        else Path(configured_home) if configured_home else Path.home() / '.codex'
    )
    events = []
    warnings = []
    causes = []
    invalid_json = 0
    paths = _codex_log_paths(root, session_id)
    source_lines = []
    if len(paths) > 1:
        message = (
            f'Multiple exact Codex log candidates were found for session '
            f'{session_id}; local attribution is ambiguous.'
        )
        warnings.append(message)
        causes.append({'kind': 'ambiguous-multiple-logs', 'message': message})
    else:
        for path in paths:
            try:
                lines = path.read_text(encoding='utf-8').splitlines()
            except OSError as error:
                message = f'Codex log could not be read: {error}'
                warnings.append(message)
                causes.append({'kind': 'unreadable', 'message': message})
                continue
            source_lines.append(lines)
    cutoff = (
        _timestamp(captured_at)
        if captured_at is not None
        else _timestamp() if capture_cutoff_after_read else None
    )
    for lines in source_lines:
        for line in lines:
            try:
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise UsageError('Codex log event must be an object.')
                event['_parsed_timestamp'] = _parse_timestamp(str(event['timestamp']))
                if cutoff is not None and event['_parsed_timestamp'] > cutoff:
                    continue
                payload = event.get('payload')
                if payload is not None and not isinstance(payload, dict):
                    raise UsageError('Codex log event payload must be an object.')
                if isinstance(payload, dict) and payload.get('type') == 'token_count':
                    info = payload.get('info')
                    if info is not None and not isinstance(info, dict):
                        raise UsageError('Codex token info must be an object.')
                    if (
                        isinstance(info, dict)
                        and 'total_token_usage' in info
                        and not isinstance(info['total_token_usage'], dict)
                    ):
                        raise UsageError(
                            'Codex total token usage must be an object.'
                        )
                _validate_codex_tool_event(event)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError, UsageError):
                invalid_json += 1
                continue
            events.append(event)
    events.sort(key=lambda event: event['_parsed_timestamp'])
    events, incoherent_tools = _coherent_codex_tool_events(events)
    invalid_json += incoherent_tools
    if invalid_json:
        message = f'{invalid_json} Codex log line(s) were invalid.'
        warnings.append(message)
        causes.append({'kind': 'malformed', 'message': message})
    if causes:
        outcome = 'failed'
    elif not paths:
        outcome = 'unavailable'
        causes.append(
            {'kind': 'no-matching-log', 'message': 'Codex log was not found.'}
        )
    elif not events:
        outcome = 'unavailable'
        causes.append(
            {
                'kind': 'no-events',
                'message': 'Codex log contained no readable diagnostic events.',
            }
        )
    else:
        outcome = 'available'
    return {
        'events': events,
        'warnings': warnings,
        'acquisition': {
            'outcome': outcome,
            'causes': causes,
            'observed_from': (
                _serialize_timestamp(observation_started)
                if observation_started is not None
                else None
            ),
            'observed_through': (
                _serialize_timestamp(cutoff) if cutoff is not None else None
            ),
        },
        'captured_at': _serialize_timestamp(cutoff) if cutoff is not None else None,
    }


def _codex_events(
    session_id: str,
    codex_home: Path | None = None,
    snapshot: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    evidence = snapshot or _load_codex_log_snapshot(session_id, codex_home)
    return list(evidence['events']), list(evidence['warnings'])


def _codex_acquisition_messages(snapshot: dict[str, Any]) -> list[str]:
    return [
        str(cause['message'])
        for cause in snapshot['acquisition'].get('causes', [])
    ]


def codex_session_bounds(
    session_id: str,
    codex_home: Path | None = None,
    snapshot: dict[str, Any] | None = None,
) -> tuple[datetime, datetime] | None:
    events, _ = _codex_events(session_id, codex_home, snapshot)
    if not events:
        return None
    return events[0]['_parsed_timestamp'], events[-1]['_parsed_timestamp']


def _codex_current_turn_discovery(
    session_id: str,
    codex_home: Path | None = None,
    snapshot: dict[str, Any] | None = None,
) -> tuple[tuple[datetime, datetime] | None, list[str]]:
    events, warnings = _codex_events(session_id, codex_home, snapshot)
    if not events:
        return None, warnings
    boundary_index = _latest_codex_user_boundary_index(events)
    if boundary_index is None:
        return None, warnings
    return (
        events[boundary_index]['_parsed_timestamp'],
        events[-1]['_parsed_timestamp'],
    ), warnings


def codex_current_turn_bounds(
    session_id: str,
    codex_home: Path | None = None,
    snapshot: dict[str, Any] | None = None,
) -> tuple[datetime, datetime] | None:
    bounds, _ = _codex_current_turn_discovery(session_id, codex_home, snapshot)
    return bounds


def _is_codex_user_boundary(event: dict[str, Any]) -> bool:
    payload = event.get('payload') or {}
    return (
        event.get('type') == 'event_msg'
        and payload.get('type') == 'user_message'
    ) or (
        event.get('type') == 'response_item'
        and payload.get('type') == 'message'
        and payload.get('role') == 'user'
    )


def _latest_codex_user_boundary_index(
    events: list[dict[str, Any]],
) -> int | None:
    return next(
        (
            index
            for index in range(len(events) - 1, -1, -1)
            if _is_codex_user_boundary(events[index])
        ),
        None,
    )


def _normalize_tool_name(name: str) -> str:
    normalized = name.strip().lower().replace('__', '.').replace('::', '.')
    return normalized.rsplit('.', 1)[-1] or 'unknown'


def _jsonish(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _structured_result_failure(value: Any) -> bool | None:
    value = _jsonish(value)
    if not isinstance(value, dict):
        return None
    if value.get('isError') is True or value.get('is_error') is True:
        return True
    status = str(value.get('status', '')).lower()
    if status in ('error', 'failed'):
        return True
    observed_success = (
        value.get('isError') is False
        or value.get('is_error') is False
        or status in ('ok', 'success', 'succeeded', 'completed')
    )
    for field in ('exit_code', 'exitCode', 'returncode', 'return_code'):
        if field not in value:
            continue
        exit_code = value[field]
        if isinstance(exit_code, bool):
            continue
        if isinstance(exit_code, (int, float)) and math.isfinite(exit_code):
            return exit_code != 0
        if isinstance(exit_code, str) and re.fullmatch(
            r'[+-]?\d+', exit_code.strip()
        ):
            return int(exit_code) != 0
    return False if observed_success else None


def _failure_envelope_texts(value: Any) -> list[str]:
    parsed = _jsonish(value)
    if isinstance(parsed, str):
        return [parsed]
    if isinstance(parsed, list):
        return [
            item['text']
            for item in parsed
            if isinstance(item, dict)
            and item.get('type') in ('text', 'input_text', 'output_text')
            and isinstance(item.get('text'), str)
        ]
    if isinstance(parsed, dict):
        texts = [
            parsed[field]
            for field in ('error', 'message')
            if isinstance(parsed.get(field), str)
        ]
        for field in ('content', 'output'):
            if field in parsed:
                texts.extend(_failure_envelope_texts(parsed[field]))
        return texts
    return []


def _tool_failed(output: Any) -> bool:
    structured = _structured_result_failure(output)
    if structured is not None:
        return structured
    return any(
        re.search(
            r'^(?:execution error:|script (?:failed\b|error:)|tool error:|collab .* failed:)',
            text.strip().lower(),
        )
        or re.search(
            r'(?:^|\n)process exited with code '
            r'(?:-[0-9]+|\+?[1-9][0-9]*)[.!]?(?:\n|$)',
            text.strip().lower(),
        )
        for text in _failure_envelope_texts(output)
    )


def _call_fingerprint(tool_name: str, payload: dict[str, Any]) -> str:
    arguments = str(payload.get('input', payload.get('arguments', '')))
    return hashlib.sha256(f'{tool_name}\0{arguments}'.encode()).hexdigest()


def _value_contains_acquisition_id(value: Any, acquisition_id: str) -> bool:
    if isinstance(value, str):
        return re.search(
            rf'(?<![a-f0-9]){re.escape(acquisition_id)}(?![a-f0-9])', value
        ) is not None
    if isinstance(value, dict):
        return any(
            _value_contains_acquisition_id(item, acquisition_id)
            for item in value.values()
        )
    if isinstance(value, list):
        return any(
            _value_contains_acquisition_id(item, acquisition_id) for item in value
        )
    return False


def _self_call_attribution(
    events: list[dict[str, Any]], acquisition_id: str | None
) -> dict[str, Any]:
    if acquisition_id is None:
        return {
            'status': 'not-requested',
            'matches': 0,
            'excluded_call_id': None,
            'reason': None,
        }
    acquisition_id = validate_acquisition_id(acquisition_id)
    matches = []
    for event in events:
        if event.get('type') != 'response_item':
            continue
        payload = event.get('payload') or {}
        if payload.get('type') not in ('custom_tool_call', 'function_call'):
            continue
        arguments = payload.get('input', payload.get('arguments'))
        if _value_contains_acquisition_id(arguments, acquisition_id):
            matches.append(str(payload['call_id']))
    if len(matches) == 1:
        return {
            'status': 'available',
            'matches': 1,
            'excluded_call_id': matches[0],
            'reason': None,
        }
    if not matches:
        return {
            'status': 'unavailable',
            'matches': 0,
            'excluded_call_id': None,
            'reason': 'The current acquisition call was not observed in the Codex tool-call records.',
        }
    return {
        'status': 'failed',
        'matches': len(matches),
        'excluded_call_id': None,
        'reason': (
            'Multiple Codex tool-call records carried the current acquisition ID; '
            'self-call attribution was ambiguous and no call was excluded.'
        ),
    }


def _spawned_agent_aliases(output: Any) -> tuple[str | None, set[str]]:
    data = _jsonish(output)
    if isinstance(data, dict):
        aliases = {
            str(data[field])
            for field in ('agent_id', 'task_name')
            if data.get(field)
        }
        if aliases:
            canonical = str(data.get('task_name') or data.get('agent_id'))
            return canonical, aliases
    return None, set()


def _wait_evidence(output: Any) -> tuple[bool, dict[str, str]]:
    data = _jsonish(output)
    if not isinstance(data, dict):
        return False, {}
    statuses = data.get('status') or {}
    terminal = {}
    if isinstance(statuses, dict):
        for agent_id, raw_status in statuses.items():
            if isinstance(raw_status, dict):
                state = next(
                    (name for name in TERMINAL_AGENT_STATES if name in raw_status),
                    '',
                )
            else:
                state = str(raw_status).lower()
            if state in TERMINAL_AGENT_STATES:
                terminal[str(agent_id)] = state
    return bool(data.get('timed_out')), terminal


def _listed_agent_evidence(output: Any) -> tuple[set[str], set[str], set[str]]:
    data = _jsonish(output)
    if not isinstance(data, dict) or not isinstance(data.get('agents'), list):
        return set(), set(), set()
    live = set()
    completed = set()
    failed = set()
    for agent in data['agents']:
        if not isinstance(agent, dict):
            continue
        name = str(agent.get('agent_name', ''))
        if not name or name == '/root':
            continue
        raw_status = agent.get('agent_status', '')
        if isinstance(raw_status, dict):
            statuses = {str(key).lower() for key in raw_status}
            status = next(
                (
                    candidate
                    for candidate in (
                        'running',
                        'idle',
                        'waiting',
                        *TERMINAL_AGENT_STATES,
                    )
                    if candidate in statuses
                ),
                '',
            )
        else:
            status = str(raw_status).lower()
        if status in ('running', 'idle', 'waiting'):
            live.add(name)
        elif status == 'completed':
            completed.add(name)
        elif status in ('failed', 'cancelled', 'canceled', 'errored'):
            failed.add(name)
    return live, completed, failed


def analyze_codex_tool_activity(
    session_id: str,
    codex_home: Path | None = None,
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
    snapshot: dict[str, Any] | None = None,
    acquisition_id: str | None = None,
    scope_start_index: int | None = None,
) -> dict[str, Any]:
    evidence = snapshot or _load_codex_log_snapshot(session_id, codex_home)
    events, warnings = _codex_events(session_id, codex_home, evidence)
    acquisition = evidence['acquisition']
    self_call_attribution = _self_call_attribution(events, acquisition_id)
    if self_call_attribution['reason']:
        warnings.append(str(self_call_attribution['reason']))
    if not events:
        activity = _unavailable_tool_activity(
            warnings or _codex_acquisition_messages(evidence),
            status=(
                'failed'
                if acquisition['outcome'] == 'failed'
                else 'unavailable'
            ),
        )
        activity['acquisition'] = acquisition
        activity['self_call_attribution'] = self_call_attribution
        return activity

    if scope_start_index is not None and not 0 <= scope_start_index < len(events):
        raise UsageError('Codex scope start event index was outside the snapshot.')

    scope_start = _timestamp(started_at or events[0]['_parsed_timestamp'])
    scope_end = _timestamp(ended_at or events[-1]['_parsed_timestamp'])
    tool_rows: dict[str, dict[str, int | str]] = {}
    pending: dict[str, tuple[datetime, str, str, bool]] = {}
    live_agents: set[str] = set()
    agent_aliases: dict[str, str] = {}
    scope_spawned_agents: set[str] = set()
    scope_completed_agents: set[str] = set()
    scope_failed_agents: set[str] = set()
    scope_list_completed: set[str] = set()
    scope_list_failed: set[str] = set()
    lifecycle_starts = 0
    lifecycle_interactions = 0
    lifecycle_interruptions = 0
    lifecycle_events = 0
    lifecycle_schema_failed = False
    observed_peak_live = 0
    wait_without_live = 0
    wait_timeouts = 0
    consecutive_wait_timeouts = 0
    max_consecutive_wait_timeouts = 0
    previous_fingerprint = None
    repeated_identical_calls = 0

    for event_index, event in enumerate(events):
        event_time = event['_parsed_timestamp']
        if event_time > scope_end:
            break
        in_scope = scope_start <= event_time <= scope_end and (
            scope_start_index is None
            or event_time > scope_start
            or event_index >= scope_start_index
        )
        if in_scope:
            observed_peak_live = max(observed_peak_live, len(live_agents))
        payload = event.get('payload') or {}
        if (
            event.get('type') == 'event_msg'
            and payload.get('type') == 'sub_agent_activity'
        ):
            agent_id = payload.get('agent_thread_id')
            agent_path = payload.get('agent_path')
            kind = payload.get('kind')
            if (
                not isinstance(agent_id, str)
                or not agent_id
                or not isinstance(agent_path, str)
                or not agent_path
                or kind not in ('started', 'interacted', 'interrupted')
            ):
                if in_scope:
                    lifecycle_schema_failed = True
                    warnings.append(
                        'A Codex subagent lifecycle event used an unsupported schema.'
                    )
                continue
            if in_scope:
                lifecycle_events += 1
                if kind == 'started':
                    lifecycle_starts += 1
                elif kind == 'interacted':
                    lifecycle_interactions += 1
                else:
                    lifecycle_interruptions += 1
            continue
        if event.get('type') != 'response_item':
            continue
        payload_type = payload.get('type')
        call_id = str(payload.get('call_id', ''))
        if payload_type in ('custom_tool_call', 'function_call') and call_id:
            if call_id == self_call_attribution['excluded_call_id']:
                continue
            tool_name = _normalize_tool_name(str(payload.get('name', '')))
            fingerprint = _call_fingerprint(tool_name, payload)
            pending[call_id] = (event_time, tool_name, fingerprint, in_scope)
            if in_scope:
                row = tool_rows.setdefault(
                    tool_name,
                    {
                        'name': tool_name,
                        'started': 0,
                        'completed': 0,
                        'failed': 0,
                        'incomplete': 0,
                        'duration_ms': 0,
                        'longest_ms': 0,
                    },
                )
                row['started'] = int(row['started']) + 1
                if fingerprint == previous_fingerprint:
                    repeated_identical_calls += 1
                previous_fingerprint = fingerprint
                if tool_name == 'wait_agent' and not live_agents:
                    wait_without_live += 1
        elif (
            payload_type in ('custom_tool_call_output', 'function_call_output')
            and call_id in pending
        ):
            call_start, tool_name, _, call_in_scope = pending.pop(call_id)
            output = payload.get('output')
            failed = _tool_failed(output)

            if tool_name == 'spawn_agent' and not failed:
                agent_id, aliases = _spawned_agent_aliases(output)
                if agent_id:
                    for alias in aliases:
                        agent_aliases[alias] = agent_id
                    live_agents.add(agent_id)
                    if call_in_scope:
                        scope_spawned_agents.add(agent_id)
            elif tool_name == 'wait_agent':
                timed_out, terminal = _wait_evidence(output)
                if call_in_scope:
                    if timed_out:
                        consecutive_wait_timeouts += 1
                        max_consecutive_wait_timeouts = max(
                            max_consecutive_wait_timeouts,
                            consecutive_wait_timeouts,
                        )
                        wait_timeouts += 1
                    else:
                        consecutive_wait_timeouts = 0
                for agent_id, state in terminal.items():
                    canonical_id = agent_aliases.get(agent_id, agent_id)
                    live_agents.discard(canonical_id)
                    if state == 'completed':
                        if call_in_scope:
                            scope_completed_agents.add(canonical_id)
                    else:
                        if call_in_scope:
                            scope_failed_agents.add(canonical_id)
            elif tool_name == 'list_agents' and not failed:
                listed_live, listed_completed, listed_failed = (
                    _listed_agent_evidence(output)
                )
                listed_live = {
                    agent_aliases.get(agent_id, agent_id)
                    for agent_id in listed_live
                }
                listed_completed = {
                    agent_aliases.get(agent_id, agent_id)
                    for agent_id in listed_completed
                }
                listed_failed = {
                    agent_aliases.get(agent_id, agent_id)
                    for agent_id in listed_failed
                }
                live_agents = listed_live
                if call_in_scope:
                    scope_list_completed.update(listed_completed)
                    scope_list_failed.update(listed_failed)
            if in_scope:
                observed_peak_live = max(observed_peak_live, len(live_agents))
            if call_in_scope:
                duration_ms = _duration_milliseconds(call_start, event_time)
                row = tool_rows[tool_name]
                row['completed'] = int(row['completed']) + 1
                row['duration_ms'] = int(row['duration_ms']) + duration_ms
                row['longest_ms'] = max(int(row['longest_ms']), duration_ms)
                if failed:
                    row['failed'] = int(row['failed']) + 1

    for _, tool_name, _, call_in_scope in pending.values():
        if call_in_scope:
            row = tool_rows[tool_name]
            row['incomplete'] = int(row['incomplete']) + 1

    started_calls = sum(int(row['started']) for row in tool_rows.values())
    completed_calls = sum(int(row['completed']) for row in tool_rows.values())
    failed_calls = sum(int(row['failed']) for row in tool_rows.values())
    incomplete_calls = sum(int(row['incomplete']) for row in tool_rows.values())
    if incomplete_calls:
        warnings.append(f'{incomplete_calls} tool call(s) had no completed log output.')

    findings = []
    if incomplete_calls:
        findings.append('incomplete-tool-calls')
    if failed_calls:
        findings.append('failed-tool-calls')
    if wait_without_live:
        findings.append('wait-without-observed-live-agent')
    if scope_failed_agents or scope_list_failed:
        findings.append('agent-failures')
    if lifecycle_interruptions:
        findings.append('interrupted-subagent-lifecycle')
    if self_call_attribution['status'] == 'failed':
        findings.append('ambiguous-self-call-attribution')

    coordination = {name: 0 for name in COORDINATION_TOOLS}
    for name in COORDINATION_TOOLS:
        coordination[name] = int(tool_rows.get(name, {}).get('started', 0))
    coordination.update(
        {
            'spawn_successes': len(scope_spawned_agents),
            'spawn_failures': int(tool_rows.get('spawn_agent', {}).get('failed', 0)),
            'completed_agents': len(
                scope_completed_agents | scope_list_completed
            ),
            'failed_agents': len(scope_failed_agents | scope_list_failed),
            'observed_peak_live_agents': observed_peak_live,
            'observed_live_agents_at_end': len(live_agents),
            'wait_timeouts': wait_timeouts,
            'max_consecutive_wait_timeouts': max_consecutive_wait_timeouts,
            'wait_without_observed_live_agent': wait_without_live,
            'lifecycle_started_events': lifecycle_starts,
            'lifecycle_interacted_events': lifecycle_interactions,
            'lifecycle_interrupted_events': lifecycle_interruptions,
        }
    )
    acquisition_status = acquisition['outcome']
    if acquisition_status == 'failed':
        base_surface_status = 'failed'
    elif acquisition_status == 'unavailable':
        base_surface_status = 'unavailable'
    else:
        base_surface_status = 'available'
    coordination_calls = sum(coordination[name] for name in COORDINATION_TOOLS)
    surface_coverage = {
        'tool calls': {
            'status': base_surface_status,
            'evidence': (
                'Codex response_item tool-call records'
                if base_surface_status == 'available'
                else None
            ),
            'reason': None,
        },
        'incomplete calls': {
            'status': base_surface_status,
            'evidence': (
                'Codex response_item call/output pairing'
                if base_surface_status == 'available'
                else None
            ),
            'reason': None,
        },
        'subagent lifecycle': {
            'status': (
                base_surface_status
                if base_surface_status != 'available'
                else 'failed' if lifecycle_schema_failed
                else 'available' if lifecycle_events
                else 'unavailable'
            ),
            'evidence': (
                'Codex sub_agent_activity lifecycle records'
                if lifecycle_events
                else None
            ),
            'reason': (
                'A Codex subagent lifecycle event used an unsupported schema.'
                if lifecycle_schema_failed
                else None if lifecycle_events
                else 'No supported Codex subagent lifecycle records were present.'
            ),
        },
        'agent coordination': {
            'status': (
                base_surface_status
                if base_surface_status != 'available'
                else 'available' if coordination_calls
                else 'unavailable'
            ),
            'evidence': (
                'Codex coordination tool call/output records'
                if coordination_calls
                else None
            ),
            'reason': (
                None
                if coordination_calls
                else 'No supported Codex coordination tool record was present.'
            ),
        },
        'waits': {
            'status': (
                base_surface_status
                if base_surface_status != 'available' or coordination['wait_agent']
                else 'unavailable'
            ),
            'evidence': (
                'Codex wait_agent call/output records'
                if coordination['wait_agent']
                else None
            ),
            'reason': (
                None
                if coordination['wait_agent']
                else 'Codex sub_agent_activity does not identify waits, and no wait_agent record was present.'
            ),
        },
    }
    acquisition_reasons = '; '.join(_codex_acquisition_messages(evidence))
    for surface in surface_coverage.values():
        if surface['status'] in ('failed', 'unavailable') and not surface['reason']:
            surface['reason'] = acquisition_reasons or 'Codex local-log evidence was unavailable.'
    return {
        'status': (
            'failed'
            if acquisition['outcome'] == 'failed'
            or self_call_attribution['status'] == 'failed'
            else 'partial' if warnings else 'available'
        ),
        'started_calls': started_calls,
        'completed_calls': completed_calls,
        'failed_calls': failed_calls,
        'incomplete_calls': incomplete_calls,
        'repeated_identical_calls': repeated_identical_calls,
        'observed_duration_ms': sum(int(row['duration_ms']) for row in tool_rows.values()),
        'longest_call_ms': max(
            (int(row['longest_ms']) for row in tool_rows.values()), default=0
        ),
        'tools': [tool_rows[name] for name in sorted(tool_rows)],
        'coordination': coordination,
        'findings': findings,
        'warnings': warnings,
        'acquisition': acquisition,
        'self_call_attribution': self_call_attribution,
        'surface_coverage': surface_coverage,
    }


def _read_codex_token_totals_evidence(
    session_id: str,
    codex_home: Path | None = None,
    snapshot: dict[str, Any] | None = None,
) -> tuple[dict[str, int] | None, list[str]]:
    latest: tuple[datetime, dict[str, Any]] | None = None
    events, problems = _codex_events(session_id, codex_home, snapshot)
    for event in events:
        payload = event.get('payload') or {}
        info = payload.get('info') or {}
        totals = info.get('total_token_usage')
        if (
            event.get('type') != 'event_msg'
            or payload.get('type') != 'token_count'
            or not isinstance(totals, dict)
        ):
            continue
        event_time = event['_parsed_timestamp']
        if latest is None or event_time > latest[0]:
            latest = event_time, totals
    if latest is None:
        return None, problems
    return _normalize_codex_token_totals(latest[1]), problems


def read_codex_token_totals(
    session_id: str,
    codex_home: Path | None = None,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, int] | None:
    totals, _ = _read_codex_token_totals_evidence(
        session_id, codex_home, snapshot
    )
    return totals


def _normalize_codex_token_totals(raw: dict[str, Any]) -> dict[str, int]:
    def counter(field: str, *, required: bool) -> int:
        if field not in raw:
            if required:
                raise UsageError(f'Codex token field {field} is required.')
            return 0
        value = raw[field]
        if value is None:
            raise UsageError(f'Codex token field {field} must not be null.')
        if isinstance(value, bool) or not isinstance(value, int):
            raise UsageError(f'Codex token field {field} must be an integer.')
        if value < 0:
            raise UsageError(f'Codex token field {field} must not be negative.')
        return value

    total_input = counter('input_tokens', required=True)
    cache_read = counter('cached_input_tokens', required=False)
    cache_write = counter('cache_write_input_tokens', required=False)
    total_output = counter('output_tokens', required=True)
    reasoning = counter('reasoning_output_tokens', required=False)
    if cache_read + cache_write > total_input:
        raise UsageError('Codex cached input exceeds total input tokens.')
    if reasoning > total_output:
        raise UsageError('Codex reasoning output exceeds total output tokens.')
    return {
        'input': total_input - cache_read - cache_write,
        'cache_read': cache_read,
        'cache_write': cache_write,
        'output': total_output - reasoning,
        'reasoning': reasoning,
        'total_tokens': total_input + total_output,
    }


def read_codex_token_delta(
    session_id: str,
    started_at: datetime,
    ended_at: datetime,
    codex_home: Path | None = None,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, int] | None:
    events, _ = _codex_events(session_id, codex_home, snapshot)
    boundary_index = _latest_codex_user_boundary_index(events)
    if (
        boundary_index is None
        or events[boundary_index]['_parsed_timestamp'] != started_at
    ):
        raise UsageError('Codex current-turn user boundary was not found.')
    earlier_user_boundary = False
    before = None
    after = None
    for index, event in enumerate(events):
        event_time = event['_parsed_timestamp']
        payload = event.get('payload') or {}
        if index < boundary_index and _is_codex_user_boundary(event):
            earlier_user_boundary = True
        info = payload.get('info') or {}
        raw = info.get('total_token_usage')
        if (
            event.get('type') != 'event_msg'
            or payload.get('type') != 'token_count'
            or not isinstance(raw, dict)
        ):
            continue
        totals = _normalize_codex_token_totals(raw)
        if index < boundary_index:
            before = totals
        if boundary_index < index and event_time <= ended_at:
            after = totals
    if after is None:
        return None
    if before is None and earlier_user_boundary:
        raise UsageError(
            'Codex cumulative token baseline before the current-turn boundary '
            'was not found.'
        )
    baseline = before or {field: 0 for field in (*TOKEN_FIELDS, 'total_tokens')}
    delta = {}
    for field in (*TOKEN_FIELDS, 'total_tokens'):
        value = after[field] - baseline[field]
        if value < 0:
            raise UsageError(f'Codex cumulative token counter decreased for {field}.')
        delta[field] = value
    return delta


def build_session_usage(
    client: str,
    session_id: str,
    captured_at: datetime,
    *,
    tokscale_rows: list[dict[str, Any]],
    snapshot_error: str | None = None,
    snapshot_unavailable: str | None = None,
    codex_home: Path | None = None,
    codex_snapshot: dict[str, Any] | None = None,
    tokscale_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    client = validate_client(client)
    try:
        matching_rows = _matching_tokscale_rows(client, session_id, tokscale_rows)
    except UsageError as error:
        matching_rows = []
        snapshot_error = str(error)
    warnings = [message for message in (snapshot_error, snapshot_unavailable) if message]
    collection = {
        'outcome': (
            'failed'
            if snapshot_error
            else 'unavailable' if snapshot_unavailable else 'succeeded'
        ),
        'cause': snapshot_error or snapshot_unavailable,
    }
    provider = tokscale_evidence or {
        **collection,
        'executable': None,
        'version': None,
        'schema_status': 'not-recorded',
        'observed_from': None,
        'observed_through': None,
        'effects': list(TOKSCALE_EFFECTS),
    }
    fallback = {'outcome': 'not-attempted', 'cause': None}
    local_log_acquisition = (
        codex_snapshot.get('acquisition') if codex_snapshot is not None else None
    )
    if matching_rows:
        rows, totals = _aggregate_usage(matching_rows)
        return {
            'client': client,
            'session_id': session_id,
            'captured_at': _serialize_timestamp(captured_at),
            'status': 'available',
            'source': 'tokscale',
            'cost_status': 'available',
            'rows': rows,
            'totals': totals,
            'warnings': warnings,
            'collection': collection,
            'provider': provider,
            'fallback': fallback,
            'local_log_acquisition': local_log_acquisition,
        }
    if client == 'codex':
        codex_evidence = codex_snapshot or _load_codex_log_snapshot(
            session_id, codex_home
        )
        local_log_acquisition = codex_evidence['acquisition']
        try:
            log_totals, fallback_problems = _read_codex_token_totals_evidence(
                session_id, codex_home, codex_evidence
            )
        except UsageError as error:
            fallback = {'outcome': 'failed', 'cause': str(error)}
            warnings.append(str(error))
            log_totals = None
        else:
            if local_log_acquisition['outcome'] == 'failed':
                fallback_messages = _codex_acquisition_messages(codex_evidence)
                fallback_cause = '; '.join(fallback_messages)
                fallback = {'outcome': 'failed', 'cause': fallback_cause}
                warnings.extend(fallback_problems or fallback_messages)
        if log_totals is not None:
            if fallback['outcome'] != 'failed':
                fallback = {'outcome': 'succeeded', 'cause': None}
            totals = _empty_usage_totals()
            totals.update(log_totals)
            if not snapshot_error and not snapshot_unavailable:
                warnings.append('Tokscale returned no matching session row.')
            return {
                'client': client,
                'session_id': session_id,
                'captured_at': _serialize_timestamp(captured_at),
                'status': 'partial',
                'source': 'codex-log',
                'cost_status': 'unavailable',
                'rows': [],
                'totals': totals,
                'warnings': warnings,
                'collection': collection,
                'provider': provider,
                'fallback': fallback,
                'local_log_acquisition': local_log_acquisition,
            }
        if fallback['outcome'] != 'failed':
            fallback = {'outcome': 'no-evidence', 'cause': None}
    if not snapshot_error and not snapshot_unavailable and fallback['outcome'] != 'failed':
        if client == 'codex':
            warnings.append('No matching Tokscale row or Codex token event was found.')
        elif client == 'cursor':
            warnings.append(
                'No exact Tokscale row was available for the requested Cursor session.'
            )
            identity = provider.get('identity', {})
            if identity.get('status') in ('failed', 'unavailable'):
                warnings.append(
                    str(identity.get('reason') or 'Tokscale Cursor identity was unavailable.')
                )
        else:
            warnings.append(
                'No exact Tokscale row was available for the requested GitHub '
                'Copilot CLI session.'
            )
    return {
        'client': client,
        'session_id': session_id,
        'captured_at': _serialize_timestamp(captured_at),
        'status': 'failed' if fallback['outcome'] == 'failed' else 'unavailable',
        'source': 'none',
        'cost_status': 'unavailable',
        'rows': [],
        'totals': _empty_usage_totals(),
        'warnings': warnings,
        'collection': collection,
        'provider': provider,
        'fallback': fallback,
        'local_log_acquisition': local_log_acquisition,
    }


def build_unrequested_session_usage(
    client: str, session_id: str, captured_at: datetime
) -> dict[str, Any]:
    return {
        'client': validate_client(client),
        'session_id': session_id,
        'captured_at': _serialize_timestamp(captured_at),
        'status': 'unavailable',
        'source': 'none',
        'cost_status': 'unavailable',
        'rows': [],
        'totals': _empty_usage_totals(),
        'warnings': ['Whole-session usage was not requested.'],
        'collection': {'outcome': 'not-attempted', 'cause': None},
        'provider': {
            'outcome': 'not-attempted',
            'cause': None,
            'executable': None,
            'version': None,
            'schema_status': 'not-requested',
            'observed_from': None,
            'observed_through': None,
            'effects': [],
        },
        'fallback': {'outcome': 'not-attempted', 'cause': None},
        'local_log_acquisition': None,
    }


def build_codex_turn_usage(
    session_id: str,
    captured_at: datetime,
    bounds: tuple[datetime, datetime] | None,
    codex_home: Path | None = None,
    codex_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    delta = (
        None
        if bounds is None
        else read_codex_token_delta(
            session_id, bounds[0], bounds[1], codex_home, codex_snapshot
        )
    )
    totals = _empty_usage_totals()
    warnings = []
    if delta is None:
        warnings.append('Current-turn cumulative token evidence was not found.')
    else:
        totals.update(delta)
    return {
        'client': 'codex',
        'session_id': session_id,
        'captured_at': _serialize_timestamp(captured_at),
        'status': 'unavailable' if delta is None else 'available',
        'source': 'codex-log-delta' if delta is not None else 'none',
        'cost_status': 'unavailable',
        'rows': [],
        'totals': totals,
        'warnings': warnings,
    }


def _build_codex_turn_usage_evidence(
    session_id: str,
    captured_at: datetime,
    bounds: tuple[datetime, datetime] | None,
    codex_home: Path | None = None,
    codex_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        return build_codex_turn_usage(
            session_id, captured_at, bounds, codex_home, codex_snapshot
        )
    except UsageError as error:
        return {
            'client': 'codex',
            'session_id': session_id,
            'captured_at': _serialize_timestamp(captured_at),
            'status': 'failed',
            'source': 'none',
            'cost_status': 'unavailable',
            'rows': [],
            'totals': _empty_usage_totals(),
            'warnings': [str(error)],
        }


def _format_tokens(value: int | float) -> str:
    return f'{int(value):,}'


def _unique_problems(messages: list[str]) -> list[str]:
    return list(dict.fromkeys(message.strip() for message in messages if message.strip()))


def _collection_failed(session_usage: dict[str, Any]) -> bool:
    return session_usage.get('collection', {}).get('outcome') == 'failed'


def _fallback_failed(session_usage: dict[str, Any]) -> bool:
    return session_usage.get('fallback', {}).get('outcome') == 'failed'


def _capability(
    name: str,
    status: str,
    *,
    scope: str,
    relevant: bool = True,
    evidence: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    if status not in ('available', 'unavailable', 'failed'):
        raise UsageError(f'Invalid capability status for {name}: {status}')
    return {
        'name': name,
        'scope': scope,
        'status': status,
        'relevant': relevant,
        'evidence': evidence,
        'reason': reason,
    }


def _activity_capability_status(activity: dict[str, Any]) -> str:
    if activity.get('status') == 'failed':
        return 'failed'
    if activity.get('status') != 'unavailable':
        return 'available'
    return 'unavailable'


def _report_codex_acquisition(
    session_usage: dict[str, Any],
    session_activity: dict[str, Any],
    explicit: dict[str, Any] | None,
) -> dict[str, Any] | None:
    return (
        explicit
        or session_activity.get('acquisition')
        or session_usage.get('local_log_acquisition')
    )


def _profile_behavior_reason(client: str) -> str:
    return (
        f'This diagnostic profile has no {PROFILE_LABELS[client]} local behavior '
        'evidence integration; this does not claim that the harness can never expose it.'
    )


def _behavior_capability(
    client: str,
    scope: str,
    name: str,
    activity: dict[str, Any] | None,
) -> dict[str, Any]:
    if client != 'codex':
        return _capability(
            name,
            'unavailable',
            scope=scope,
            reason=_profile_behavior_reason(client),
        )
    if activity is None:
        return _capability(
            name,
            'unavailable',
            scope=scope,
            reason=f'Requested Codex {scope} behavior evidence was unavailable.',
        )
    surface = activity.get('surface_coverage', {}).get(name)
    if surface is not None:
        return _capability(
            name,
            str(surface['status']),
            scope=scope,
            evidence=surface.get('evidence'),
            reason=surface.get('reason'),
        )
    status = _activity_capability_status(activity)
    reasons = _unique_problems(list(activity.get('warnings', [])))
    return _capability(
        name,
        status,
        scope=scope,
        evidence='Codex local-log behavior records' if status == 'available' else None,
        reason=(
            '; '.join(reasons)
            or (
                f'Requested Codex {scope} behavior evidence was unavailable.'
                if status != 'available'
                else None
            )
        ),
    )


def build_capability_coverage(
    session_usage: dict[str, Any],
    session_activity: dict[str, Any],
    *,
    turn_usage: dict[str, Any] | None,
    turn_activity: dict[str, Any] | None,
    turn_bounds: tuple[datetime, datetime] | None,
    turn_discovery_problems: list[str] | None,
    selected_scope: str,
    codex_acquisition: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    client = validate_client(str(session_usage['client']))
    local_acquisition = _report_codex_acquisition(
        session_usage, session_activity, codex_acquisition
    )
    usage_warnings = list(session_usage.get('warnings', []))
    if session_usage['status'] == 'failed':
        usage_status = 'failed'
    elif session_usage['status'] != 'unavailable':
        usage_status = 'available'
    else:
        usage_status = (
            'failed' if _collection_failed(session_usage) else 'unavailable'
        )
    coverage = [
        _capability(
            'session usage',
            usage_status,
            scope='session',
            relevant=selected_scope in ('session', 'both'),
            evidence=(
                f"{session_usage['source']} whole-session usage"
                if usage_status == 'available'
                else None
            ),
            reason='; '.join(usage_warnings) if usage_status != 'available' else None,
        )
    ]

    if session_usage['cost_status'] == 'available':
        cost_status = 'available'
        cost_reason = None
    elif _collection_failed(session_usage):
        cost_status = 'failed'
        cost_reason = '; '.join(usage_warnings)
    else:
        cost_status = 'unavailable'
        cost_reason = '; '.join(usage_warnings) or (
            'No exact Tokscale client/session/model row supplied estimated '
            'API-equivalent cost.'
        )
    coverage.append(
        _capability(
            'estimated API-equivalent cost',
            cost_status,
            scope='session',
            relevant=selected_scope in ('session', 'both'),
            evidence=(
                'Tokscale whole-session client/session/model cost fields'
                if cost_status == 'available'
                else None
            ),
            reason=cost_reason,
        )
    )

    session_relevant = selected_scope in ('session', 'both')
    if session_usage['source'] == 'tokscale':
        model_status = 'available'
        model_reason = None
    elif _collection_failed(session_usage):
        model_status = 'failed'
        model_reason = '; '.join(usage_warnings)
    elif usage_warnings:
        model_status = 'unavailable'
        model_reason = '; '.join(usage_warnings)
    elif client == 'codex':
        model_status = 'unavailable'
        model_reason = 'No matching session/model activity row was available.'
    else:
        model_status = 'unavailable'
        model_reason = 'Tokscale model-activity evidence was not available.'
    coverage.append(
        _capability(
            'model activity',
            model_status,
            scope='session',
            relevant=session_relevant,
            evidence=(
                'Tokscale whole-session client/session/model grouping and duration fields'
                if session_usage['source'] == 'tokscale'
                else None
            ),
            reason=model_reason,
        )
    )

    turn_relevant = selected_scope in ('turn', 'both')
    discovery_problems = turn_discovery_problems or []
    if (
        client == 'codex'
        and local_acquisition is not None
        and local_acquisition['outcome'] == 'failed'
    ):
        turn_status = 'failed'
        turn_reason = '; '.join(
            str(cause['message'])
            for cause in local_acquisition.get('causes', [])
        )
        turn_evidence = None
    elif client == 'codex' and discovery_problems and local_acquisition is None:
        turn_status = 'failed'
        turn_reason = '; '.join(discovery_problems)
        turn_evidence = None
    elif client == 'codex' and turn_usage is not None and turn_bounds is not None:
        if turn_usage['status'] == 'failed':
            turn_status = 'failed'
        elif turn_usage['status'] == 'unavailable':
            turn_status = 'unavailable'
        else:
            turn_status = 'available'
        turn_reason = (
            None
            if turn_status == 'available'
            else '; '.join(turn_usage.get('warnings', []))
        )
        turn_evidence = (
            'Codex local-log current-turn boundary and cumulative token delta'
            if turn_status == 'available'
            else None
        )
    elif client == 'codex':
        turn_status = 'unavailable'
        turn_reason = (
            '; '.join(
                str(cause['message'])
                for cause in local_acquisition.get('causes', [])
            )
            if local_acquisition is not None
            and local_acquisition['outcome'] == 'unavailable'
            else 'Current-turn boundary was not found in the Codex local log.'
        )
        turn_evidence = None
    else:
        turn_status = 'unavailable'
        turn_reason = _profile_behavior_reason(client)
        turn_evidence = None
    coverage.append(
        _capability(
            'current turn',
            turn_status,
            scope='turn',
            relevant=turn_relevant,
            evidence=turn_evidence,
            reason=turn_reason,
        )
    )
    coverage.extend(
        (
            _capability(
                'current-turn model activity',
                'unavailable',
                scope='turn',
                relevant=turn_relevant,
                reason=(
                    'Unsupported: this package owns no turn-bounded model-activity '
                    'provider or invocation path.'
                ),
            ),
            _capability(
                'current-turn estimated API-equivalent cost',
                'unavailable',
                scope='turn',
                relevant=turn_relevant,
                reason=(
                    'Unsupported: this package owns no turn-bounded cost provider or '
                    'invocation path.'
                ),
            ),
        )
    )

    activities = {'turn': turn_activity, 'session': session_activity}
    for scope in _requested_scopes(selected_scope):
        for name in BEHAVIOR_CAPABILITY_NAMES:
            coverage.append(
                _behavior_capability(client, scope, name, activities[scope])
            )
    return coverage


def _build_scope_report(
    name: str,
    usage: dict[str, Any],
    tool_activity: dict[str, Any],
    bounds: tuple[datetime, datetime] | None,
) -> dict[str, Any]:
    totals = usage['totals']
    return {
        'name': name,
        'observed_from': (
            _serialize_timestamp(bounds[0]) if bounds is not None else None
        ),
        'observed_through': (
            _serialize_timestamp(bounds[1]) if bounds is not None else None
        ),
        'span_ms': (
            None if bounds is None else _duration_milliseconds(bounds[0], bounds[1])
        ),
        'tokens': {
            'status': usage['status'],
            'input': int(totals['input']),
            'cache_read': int(totals['cache_read']),
            'cache_write': int(totals['cache_write']),
            'output': int(totals['output']),
            'reasoning': int(totals['reasoning']),
            'total': int(totals['total_tokens']),
        },
        'cost': (
            'unavailable'
            if usage['cost_status'] == 'unavailable'
            else f"{chr(36)}{totals['cost']:.6f} USD"
        ),
        'message_count': int(totals['message_count']),
        'model_activity_ms': (
            int(totals['model_activity_ms'])
            if usage['source'] == 'tokscale'
            else None
        ),
        'models': [
            {
                'provider': row['provider'],
                'model': row['model'],
                'total_tokens': sum(int(row[field]) for field in TOKEN_FIELDS),
                'message_count': int(row['message_count']),
                'model_activity_ms': int(row['model_activity_ms']),
                'estimated_api_equivalent_cost': float(row['cost']),
            }
            for row in usage.get('rows', [])
        ],
        'tool_activity': tool_activity,
        'findings': list(tool_activity.get('findings', [])),
        'problems': _unique_problems(
            list(usage.get('warnings', []))
            + list(tool_activity.get('warnings', []))
        ),
    }


def build_diagnostic_report(
    session_usage: dict[str, Any],
    session_activity: dict[str, Any],
    session_bounds: tuple[datetime, datetime] | None,
    *,
    turn_usage: dict[str, Any] | None = None,
    turn_activity: dict[str, Any] | None = None,
    turn_bounds: tuple[datetime, datetime] | None = None,
    turn_discovery_problems: list[str] | None = None,
    selected_scope: str = 'both',
    codex_acquisition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    requested_scopes = _requested_scopes(selected_scope)
    client = validate_client(str(session_usage['client']))
    local_acquisition = _report_codex_acquisition(
        session_usage, session_activity, codex_acquisition
    )
    self_call_attribution = (
        session_activity.get('self_call_attribution')
        if selected_scope in ('session', 'both')
        else (turn_activity or {}).get('self_call_attribution')
    )
    scopes = []
    if selected_scope in ('turn', 'both') and turn_usage is not None and turn_activity is not None:
        scopes.append(_build_scope_report('current turn', turn_usage, turn_activity, turn_bounds))
    if selected_scope in ('session', 'both'):
        scopes.append(
            _build_scope_report(
                'whole session', session_usage, session_activity, session_bounds
            )
        )
    findings = [
        f"{scope['name']}: {finding}"
        for scope in scopes
        for finding in scope['findings']
    ]
    capabilities = build_capability_coverage(
        session_usage,
        session_activity,
        turn_usage=turn_usage,
        turn_activity=turn_activity,
        turn_bounds=turn_bounds,
        turn_discovery_problems=turn_discovery_problems,
        selected_scope=selected_scope,
        codex_acquisition=local_acquisition,
    )
    unavailable_evidence = [
        f"{capability['scope']} {capability['name']}: {capability['reason']}"
        for capability in capabilities
        if capability['relevant'] and capability['status'] == 'unavailable'
    ]
    session_requested = 'session' in requested_scopes
    failed_acquisition = []
    if local_acquisition is not None and local_acquisition['outcome'] == 'failed':
        failed_acquisition.extend(
            str(cause['message'])
            for cause in local_acquisition.get('causes', [])
        )
    provider = session_usage.get('provider', {})
    if (
        session_requested
        and provider.get('outcome') == 'failed'
        and provider.get('cause')
    ):
        failed_acquisition.append(str(provider['cause']))
    if (
        self_call_attribution is not None
        and self_call_attribution.get('status') == 'failed'
    ):
        failed_acquisition.append(str(self_call_attribution['reason']))
    provider_identity = provider.get('identity', {})
    if (
        session_requested
        and provider_identity.get('status') == 'failed'
        and provider_identity.get('reason')
    ):
        failed_acquisition.append(str(provider_identity['reason']))
    recovery_prerequisites = []
    if session_requested and _collection_failed(session_usage):
        recovery_prerequisites.append(
            'Make the same installed Tokscale provider available with compatible '
            'version output and JSON schema, then authorize and rerun the same '
            'client/session pair. The diagnostic does not install or repair it.'
        )
    if session_requested and _fallback_failed(session_usage):
        recovery_prerequisites.append(
            'Repair or restore the exact Codex local session log token totals; '
            'the reported local fallback cause must be resolved before usage can '
            'be recovered.'
        )
    if (
        session_requested
        and client == 'cursor'
        and session_usage['status'] == 'unavailable'
    ):
        if provider_identity.get('status') == 'unavailable':
            recovery_prerequisites.append(
                'Provide an existing valid Tokscale Cursor identity, then separately '
                'authorize a rerun of the same pair. The diagnostic does not log in.'
            )
        elif provider_identity.get('status') == 'failed':
            recovery_prerequisites.append(
                'Resolve the reported Tokscale Cursor identity probe failure, then '
                'separately authorize a rerun of the same pair.'
            )
    if (
        client == 'codex'
        and local_acquisition is not None
        and local_acquisition['outcome'] in ('failed', 'unavailable')
    ):
        recovery_prerequisites.append(
            'Provide the exact Codex local log for the requested thread and make it '
            'readable and well-formed; Tokscale usage does not replace local '
            'behavior evidence.'
        )
    source_boundaries = []
    if local_acquisition is not None:
        source_boundaries.append(
            {
                'source': 'Codex local log',
                'status': local_acquisition['outcome'],
                'version': None,
                'observed_from': (
                    local_acquisition.get('observed_from')
                    or 'not recorded by this caller'
                ),
                'observed_through': (
                    local_acquisition.get('observed_through')
                    or session_usage['captured_at']
                ),
                'effects': [
                    'read the exact Codex local session log',
                    'retain no transcript or tool content after this attempt',
                ],
            }
        )
    if session_requested and provider.get('outcome') in ('succeeded', 'failed'):
        source_boundaries.append(
            {
                'source': 'Tokscale',
                'status': provider['outcome'],
                'executable': provider.get('executable'),
                'version': provider.get('version'),
                'schema_status': provider.get('schema_status'),
                'identity_status': provider_identity.get('status'),
                'observed_from': (
                    provider.get('observed_from') or 'not recorded by this caller'
                ),
                'observed_through': (
                    provider.get('observed_through') or 'not recorded by this caller'
                ),
                'effects': provider.get('effects', []),
            }
        )
    return {
        'client': client,
        'session_id': session_usage['session_id'],
        'captured_at': session_usage['captured_at'],
        'selected_scope': selected_scope,
        'profile': PROFILE_LABELS[client],
        'self_call_attribution': self_call_attribution,
        'source_boundaries': source_boundaries,
        'capabilities': capabilities,
        'session_usage': _build_scope_report(
            'whole session', session_usage, session_activity, session_bounds
        ),
        'scopes': scopes,
        'findings': _unique_problems(findings),
        'problems': _unique_problems(findings),
        'unavailable_evidence': _unique_problems(unavailable_evidence),
        'failed_acquisition': _unique_problems(failed_acquisition),
        'limitations': [
            'Summed model and tool durations can overlap the elapsed span.',
            'Subagent lifecycle counts are observed lower bounds.',
            'Child-session tokens require a stable child mapping for attribution.',
            'Session usage coverage does not establish behavior health.',
            'Each acquisition boundary applies only to its source; no cross-source atomic snapshot is claimed.',
        ]
        + (
            [
                'Current-turn model activity and estimated API-equivalent cost are unsupported: this package owns no turn-bounded provider or invocation path.'
            ]
            if selected_scope in ('turn', 'both')
            else []
        ),
        'recovery_prerequisites': recovery_prerequisites,
    }


def _markdown_text(value: Any) -> str:
    single_line = re.sub(r'[\x00-\x1f\x7f]+', ' ', str(value)).strip()
    escaped = re.sub(r'([\\`*{}\[\]<>#|&])', r'\\\1', single_line)
    return re.sub(r'(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])', r'\\_', escaped)


def _render_scope(
    lines: list[str],
    scope: dict[str, Any],
    *,
    include_usage: bool = True,
    include_behavior: bool = True,
) -> None:
    tokens = scope['tokens']
    if tokens['status'] in ('unavailable', 'failed'):
        token_summary = tokens['status']
    else:
        qualifier = '' if tokens['status'] == 'available' else f" ({tokens['status']})"
        token_summary = (
            f"{_format_tokens(tokens['total'])} total"
            f"{qualifier} (input {_format_tokens(tokens['input'])}, "
            f"cached input {_format_tokens(tokens['cache_read'])}, "
            f"cache write {_format_tokens(tokens['cache_write'])}, "
            f"output {_format_tokens(tokens['output'])}, "
            f"reasoning {_format_tokens(tokens['reasoning'])})"
        )
    lines.append(f"#### {_markdown_text(scope['name'].title())}")
    if scope['observed_from'] is not None:
        lines.append(
            f"- Boundaries: {_markdown_text(scope['observed_from'])} through "
            f"{_markdown_text(scope['observed_through'])}"
        )
    else:
        lines.append('- Boundaries: unavailable')
    if include_usage:
        lines.extend(
            [
                f"- Span: {scope['span_ms']} ms"
                if scope['span_ms'] is not None
                else '- Span: unavailable',
                f'- Tokens: {token_summary}',
                f"- Estimated API-equivalent cost: {scope['cost']}",
                (
                    f"- Model activity: {scope['model_activity_ms']} ms across "
                    f"{scope['message_count']} message(s)"
                    if scope['model_activity_ms'] is not None
                    else '- Model activity: unavailable'
                ),
            ]
        )
        model_summary = ', '.join(
            f"{_markdown_text(model['provider'] or 'unknown-provider')}/"
            f"{_markdown_text(model['model'])}: "
            f"{_format_tokens(model['total_tokens'])} tokens, "
            f"{model['message_count']} message(s), "
            f"{model['model_activity_ms']} ms, "
            f"{chr(36)}{model['estimated_api_equivalent_cost']:.6f} USD "
            'estimated API-equivalent cost'
            for model in scope['models']
        ) or 'unavailable'
        lines.append(f'- Models: {model_summary}')
    if not include_behavior:
        return
    activity = scope['tool_activity']
    surfaces = activity.get('surface_coverage', {})
    tool_surface = surfaces.get('tool calls', {})
    if activity['status'] == 'unavailable':
        lines.append('- Tool calls: unavailable')
    else:
        if tool_surface.get('status') == 'failed':
            lines.append(
                '- Tool calls: failed — '
                f"{_markdown_text(tool_surface.get('reason') or 'collection failed')}"
            )
        tool_label = (
            'Observed tool calls' if activity['status'] == 'failed' else 'Tool calls'
        )
        lines.append(
            f"- {tool_label}: {activity['started_calls']} started, "
            f"{activity['completed_calls']} completed, {activity['failed_calls']} failed, "
            f"{activity['incomplete_calls']} incomplete"
        )
        lines.append(
            f"- Tool timing: {activity['observed_duration_ms']} ms summed, "
            f"{activity['longest_call_ms']} ms longest, "
            f"{activity['repeated_identical_calls']} consecutive identical repeat(s)"
        )
        tool_summary = ', '.join(
            f"{_markdown_text(tool['name'])}={tool['started']} started/"
            f"{tool['failed']} failed "
            f"({tool['duration_ms']} ms)"
            for tool in activity['tools']
        ) or 'none'
        lines.append(f'- Tools: {tool_summary}')
    coordination = activity.get('coordination', {})
    lifecycle_surface = surfaces.get('subagent lifecycle', {})
    if lifecycle_surface.get('status') == 'available':
        lines.append(
            '- Subagent lifecycle: '
            f"started={coordination.get('lifecycle_started_events', 0)}, "
            f"interacted={coordination.get('lifecycle_interacted_events', 0)}, "
            f"interrupted={coordination.get('lifecycle_interrupted_events', 0)}"
        )
    else:
        lines.append(
            f"- Subagent lifecycle: {lifecycle_surface.get('status', 'unavailable')} — "
            f"{_markdown_text(lifecycle_surface.get('reason') or 'no supported evidence')}"
        )
    coordination_surface = surfaces.get('agent coordination', {})
    if coordination_surface.get('status') == 'available':
        calls = ', '.join(
            f'{name}={coordination.get(name, 0)}'
            for name in COORDINATION_TOOLS
            if coordination.get(name, 0)
        )
        lines.append(f'- Agent coordination calls: {calls}')
        lines.append(
            '- Observed agent state: '
            f"spawned={coordination.get('spawn_successes', 0)}, "
            f"spawn failures={coordination.get('spawn_failures', 0)}, "
            f"completed={coordination.get('completed_agents', 0)}, "
            f"failed={coordination.get('failed_agents', 0)}, "
            f"peak live={coordination.get('observed_peak_live_agents', 0)}, "
            f"live at end={coordination.get('observed_live_agents_at_end', 0)}"
        )
    else:
        lines.append(
            f"- Agent coordination: {coordination_surface.get('status', 'unavailable')} — "
            f"{_markdown_text(coordination_surface.get('reason') or 'no supported evidence')}"
        )
    wait_surface = surfaces.get('waits', {})
    if wait_surface.get('status') == 'available':
        lines.append(
            '- Wait behavior: '
            f"timeouts={coordination.get('wait_timeouts', 0)}, "
            f"max consecutive timeouts={coordination.get('max_consecutive_wait_timeouts', 0)}, "
            'without observed live agent='
            f"{coordination.get('wait_without_observed_live_agent', 0)}"
        )
    else:
        lines.append(
            f"- Wait behavior: {wait_surface.get('status', 'unavailable')} — "
            f"{_markdown_text(wait_surface.get('reason') or 'no supported evidence')}"
        )


def render_diagnostic_markdown(report: dict[str, Any]) -> str:
    lines = [
        '### Agent Session Diagnostics',
        '',
        '#### Identity and Scope',
        f"- Session: {_markdown_text(report['client'])}/"
        f"{_markdown_text(report['session_id'])}",
        f"- Requested scope: {_markdown_text(report['selected_scope'])}",
        f"- Harness profile: {_markdown_text(report['profile'])}",
        f"- Report reference time (UTC): {_markdown_text(report['captured_at'])}",
        '- Source boundaries:',
    ]
    if report['source_boundaries']:
        for boundary in report['source_boundaries']:
            version = (
                f"; version {_markdown_text(boundary['version'])}"
                if boundary.get('version')
                else ''
            )
            executable = (
                f"; executable {_markdown_text(boundary['executable'])}"
                if boundary.get('executable')
                else ''
            )
            identity = (
                f"; identity {_markdown_text(boundary['identity_status'])}"
                if boundary.get('identity_status')
                else ''
            )
            schema = (
                f"; schema {_markdown_text(boundary['schema_status'])}"
                if boundary.get('schema_status')
                else ''
            )
            lines.append(
                f"  - {_markdown_text(boundary['source'])}: "
                f"{_markdown_text(boundary['status'])}{executable}{version}{schema}{identity}; observed from "
                f"{_markdown_text(boundary['observed_from'])} through "
                f"{_markdown_text(boundary['observed_through'])}"
            )
            effects = '; '.join(boundary.get('effects', [])) or 'none recorded'
            lines.append(f"    - Effects: {_markdown_text(effects)}")
    else:
        lines.append('  - No source was acquired.')
    attribution = report.get('self_call_attribution')
    if attribution and attribution['status'] != 'not-requested':
        detail = attribution.get('reason') or 'Exactly one matching call was excluded.'
        lines.append(
            '- Self-call attribution: '
            f"{_markdown_text(attribution['status'])} — {_markdown_text(detail)}"
        )
    lines.extend(
        [
        '',
        '#### Capability Coverage',
        ]
    )
    for capability in report['capabilities']:
        capability_label = capability['name']
        if capability_label in BEHAVIOR_CAPABILITY_NAMES:
            capability_label = f"{capability['scope']} {capability_label}"
        detail = '; '.join(
            value
            for value in (capability['evidence'], capability['reason'])
            if value
        ) or 'no detail'
        relevance = 'relevant' if capability['relevant'] else 'not requested'
        lines.append(
            f"- {_markdown_text(capability_label)}: "
            f"{_markdown_text(capability['status'])} "
            f"({_markdown_text(relevance)}) — {_markdown_text(detail)}"
        )
    if report['selected_scope'] in ('session', 'both'):
        lines.extend(['', '#### Session Usage and API-Equivalent Cost'])
        _render_scope(
            lines,
            report['session_usage'],
            include_behavior=False,
        )
    lines.extend(['', '#### Turn, Tool, and Coordination Evidence'])
    for scope in report['scopes']:
        lines.append('')
        _render_scope(
            lines,
            scope,
            include_usage=scope['name'] == 'current turn',
        )
    if not report['scopes']:
        lines.append('- No requested behavior scope had available evidence.')
    lines.extend(['', '#### Observed Problems'])
    if report['problems']:
        lines.extend(f'- {_markdown_text(problem)}' for problem in report['problems'])
    else:
        lines.append('- Problems: none from available evidence')
    lines.extend(['', '#### Unavailable Evidence'])
    if report['unavailable_evidence']:
        lines.extend(
            f'- {_markdown_text(item)}' for item in report['unavailable_evidence']
        )
    else:
        lines.append('- None')
    lines.extend(['', '#### Failed Acquisition'])
    if report['failed_acquisition']:
        lines.extend(
            f'- {_markdown_text(item)}' for item in report['failed_acquisition']
        )
    else:
        lines.append('- None')
    lines.extend(
        [
            '',
            '#### Overall Conclusion',
            '- Agent-authored after contextual judgment; the wrapper does not infer task health.',
            '',
            '#### Limitations',
        ]
    )
    lines.extend(
        f'- {_markdown_text(limitation)}' for limitation in report['limitations']
    )
    lines.extend(['', '#### Recovery Prerequisites'])
    if report['recovery_prerequisites']:
        lines.extend(
            f'- {_markdown_text(prerequisite)}'
            for prerequisite in report['recovery_prerequisites']
        )
    else:
        lines.append('- None identified by factual evidence collection.')
    return '\n'.join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Diagnose one stable agent session.')
    subparsers = parser.add_subparsers(dest='command', required=True)
    diagnose = subparsers.add_parser('diagnose')
    diagnose.add_argument('--client')
    diagnose.add_argument('--session-id')
    diagnose.add_argument(
        '--acquisition-id', required=True, type=validate_acquisition_id
    )
    diagnose.add_argument(
        '--scope', choices=DIAGNOSTIC_SCOPES, default='both'
    )
    return parser


def _unavailable_tool_activity(
    warnings: list[str], *, status: str = 'unavailable'
) -> dict[str, Any]:
    reason = '; '.join(warnings) or 'Codex local-log evidence was unavailable.'
    return {
        'status': status,
        'started_calls': 0,
        'completed_calls': 0,
        'failed_calls': 0,
        'incomplete_calls': 0,
        'repeated_identical_calls': 0,
        'observed_duration_ms': 0,
        'longest_call_ms': 0,
        'tools': [],
        'coordination': {},
        'findings': [],
        'warnings': warnings,
        'surface_coverage': {
            name: {'status': status, 'evidence': None, 'reason': reason}
            for name in BEHAVIOR_CAPABILITY_NAMES
        },
    }


def unavailable_tool_activity(problem: str) -> dict[str, Any]:
    return _unavailable_tool_activity([problem])


def _unavailable_codex_turn_activity(
    snapshot: dict[str, Any],
    acquisition_id: str,
    problems: list[str],
) -> dict[str, Any]:
    attribution = _self_call_attribution(snapshot['events'], acquisition_id)
    warnings = list(problems)
    if attribution['reason']:
        warnings.append(str(attribution['reason']))
    acquisition = snapshot['acquisition']
    status = (
        'failed'
        if acquisition['outcome'] == 'failed' or attribution['status'] == 'failed'
        else 'unavailable'
    )
    activity = _unavailable_tool_activity(_unique_problems(warnings), status=status)
    activity['acquisition'] = acquisition
    activity['self_call_attribution'] = attribution
    if attribution['status'] == 'failed':
        activity['findings'].append('ambiguous-self-call-attribution')
    return activity


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 10):
        print('ERROR: Python 3.10 or newer is required.', file=sys.stderr)
        return 2
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    try:
        client, session_id = detect_current_session(args.client, args.session_id)
        if not client or not session_id:
            raise UsageError(
                'No supported current session was detected; pass --client and --session-id.'
            )
        _validate_supported_scope(client, args.scope)
        if client == 'codex':
            codex_snapshot = _load_codex_log_snapshot(
                session_id, capture_cutoff_after_read=True
            )
            captured = _parse_timestamp(codex_snapshot['captured_at'])
        else:
            codex_snapshot = None
            captured = _timestamp()
        session_bounds = (
            codex_session_bounds(session_id, snapshot=codex_snapshot)
            if client == 'codex'
            else None
        )
        provider_bounds = (
            session_bounds
            if codex_snapshot is not None
            and codex_snapshot['acquisition']['outcome'] == 'available'
            else None
        )
        started_at, ended_at = provider_bounds or (None, None)
        if args.scope in ('session', 'both'):
            tokscale_evidence = acquire_tokscale_evidence(
                client,
                session_id,
                started_at,
                ended_at,
            )
            usage_report = build_session_usage(
                client,
                session_id,
                captured,
                tokscale_rows=tokscale_evidence['rows'],
                snapshot_error=(
                    tokscale_evidence['cause']
                    if tokscale_evidence['outcome'] == 'failed'
                    else None
                ),
                codex_snapshot=codex_snapshot,
                tokscale_evidence=tokscale_evidence,
            )
        else:
            usage_report = build_unrequested_session_usage(
                client, session_id, captured
            )
        if client == 'codex':
            snapshot_warnings = list(codex_snapshot['warnings'])
            acquisition = codex_snapshot['acquisition']
            acquisition_messages = _codex_acquisition_messages(codex_snapshot)
            if args.scope in ('session', 'both'):
                session_activity = analyze_codex_tool_activity(
                    session_id,
                    started_at=session_bounds[0] if session_bounds else None,
                    ended_at=session_bounds[1] if session_bounds else None,
                    snapshot=codex_snapshot,
                    acquisition_id=args.acquisition_id,
                )
            else:
                session_activity = _unavailable_tool_activity(
                    snapshot_warnings
                    or acquisition_messages
                    or ['Whole-session behavior was not requested.'],
                    status=(
                        'failed'
                        if acquisition['outcome'] == 'failed'
                        else 'unavailable'
                    ),
                )
                session_activity['acquisition'] = acquisition
            if args.scope in ('turn', 'both'):
                turn_bounds, turn_discovery_problems = (
                    _codex_current_turn_discovery(
                        session_id, snapshot=codex_snapshot
                    )
                )
                turn_usage = _build_codex_turn_usage_evidence(
                    session_id,
                    captured,
                    turn_bounds,
                    codex_snapshot=codex_snapshot,
                )
                turn_activity = (
                    analyze_codex_tool_activity(
                        session_id,
                        started_at=turn_bounds[0],
                        ended_at=turn_bounds[1],
                        snapshot=codex_snapshot,
                        acquisition_id=args.acquisition_id,
                        scope_start_index=_latest_codex_user_boundary_index(
                            codex_snapshot['events']
                        ),
                    )
                    if turn_bounds
                    else _unavailable_codex_turn_activity(
                        codex_snapshot,
                        args.acquisition_id,
                        turn_discovery_problems
                        or acquisition_messages
                        or ['Current-turn boundary was not found in the Codex log.'],
                    )
                )
                if turn_bounds:
                    turn_activity['acquisition'] = acquisition
            else:
                turn_bounds = None
                turn_discovery_problems = []
                turn_usage = None
                turn_activity = None
        else:
            session_activity = unavailable_tool_activity(
                _profile_behavior_reason(client)
            )
            turn_bounds = None
            turn_discovery_problems = []
            turn_usage = None
            turn_activity = None
        report = build_diagnostic_report(
            usage_report,
            session_activity,
            session_bounds,
            turn_usage=turn_usage,
            turn_activity=turn_activity,
            turn_bounds=turn_bounds,
            turn_discovery_problems=turn_discovery_problems,
            selected_scope=args.scope,
            codex_acquisition=(
                codex_snapshot['acquisition'] if codex_snapshot is not None else None
            ),
        )
        print(render_diagnostic_markdown(report))
    except (OSError, ValueError, json.JSONDecodeError, UsageError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
