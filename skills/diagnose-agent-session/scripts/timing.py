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
    'subagent lifecycle and coordination',
    'waits',
)
PROFILE_LABELS = {
    'codex': 'Codex',
    'cursor': 'Cursor',
    'copilot': 'GitHub Copilot CLI',
}
WINDOWS_LITERAL_PATH_CHARS = r'\w._:/\\ ()\-'
WINDOWS_UNQUOTED_PATH_CHARS = r'A-Za-z0-9._:/\\\-'
LINUX_LITERAL_PATH_CHARS = r'\w._/ ()\-'
LINUX_UNQUOTED_PATH_CHARS = r'A-Za-z0-9._/\-'
SESSION_ID_LITERAL = r'[A-Za-z0-9._:\-]+'
WINDOWS_ABSOLUTE_PREFIX = r'(?:[A-Za-z]:[\\/]|\\\\)'


class UsageError(RuntimeError):
    pass


def validate_client(client: str) -> str:
    if client not in SUPPORTED_CLIENTS:
        supported = ', '.join(SUPPORTED_CLIENTS)
        raise UsageError(
            f'Unsupported client {client!r}; supported clients are: {supported}.'
        )
    return client


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
        candidate = row.get('sessionId', row.get('session_id'))
        if not isinstance(candidate, str) or not session_id_matches(
            client, candidate, requested
        ):
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


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise UsageError(f'Tokscale field {field} must be a nonempty string.')
    return value


def normalize_usage_row(row: dict[str, Any]) -> dict[str, Any]:
    performance = row.get('performance') or {}
    if not isinstance(performance, dict):
        raise UsageError('Tokscale performance data must be an object.')
    session_id = row['sessionId'] if 'sessionId' in row else row.get('session_id')
    provider = row.get('provider')
    return {
        'client': _required_text(row.get('client'), 'client'),
        'session_id': _required_text(session_id, 'sessionId'),
        'provider': '' if provider is None else str(provider),
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
        'cache_read': _integer(
            row.get('cacheRead', row.get('cache_read')),
            'cacheRead',
            allow_none=False,
            require_json_number=True,
        ),
        'cache_write': _integer(
            row.get('cacheWrite', row.get('cache_write')),
            'cacheWrite',
            allow_none=False,
            require_json_number=True,
        ),
        'cost': _number(
            row.get('cost'), 'cost', allow_none=False, require_json_number=True
        ),
        'message_count': _integer(
            row.get('messageCount', row.get('message_count')),
            'messageCount',
            allow_none=False,
            require_json_number=True,
        ),
        'model_activity_ms': _integer(
            performance.get('totalDurationMs', row.get('model_activity_ms')),
            'performance.totalDurationMs',
            allow_none=False,
            require_json_number=True,
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
    return 'tokscale'


def capture_tokscale_snapshot(
    client: str,
    started_at: datetime | None,
    ended_at: datetime | None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    *,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    client = validate_client(client)
    command = [
        tokscale_executable(),
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
            f'Tokscale timed out after {TOKSCALE_TIMEOUT_SECONDS} seconds for client {client}.'
        ) from error
    except OSError as error:
        raise UsageError(f'Tokscale could not run for client {client}: {error}') from error
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or 'unknown error'
        raise UsageError(f'Tokscale failed for client {client}: {detail}')
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
        entry_session = _required_text(
            entry['sessionId'] if 'sessionId' in entry else entry.get('session_id'),
            'sessionId',
        )
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
    if client or session_id:
        if not client or not session_id:
            raise UsageError('Client and session ID must be provided together.')
        return validate_client(client), session_id
    codex_session = os.environ.get('CODEX_THREAD_ID')
    if codex_session:
        return 'codex', codex_session
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
        'acquisition': {'outcome': outcome, 'causes': causes},
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
    user_boundaries = []
    for event in events:
        payload = event.get('payload') or {}
        if (
            event.get('type') == 'event_msg'
            and payload.get('type') == 'user_message'
        ) or (
            event.get('type') == 'response_item'
            and payload.get('type') == 'message'
            and payload.get('role') == 'user'
        ):
            user_boundaries.append(event['_parsed_timestamp'])
    if not user_boundaries:
        return None, warnings
    return (max(user_boundaries), events[-1]['_parsed_timestamp']), warnings


def codex_current_turn_bounds(
    session_id: str,
    codex_home: Path | None = None,
    snapshot: dict[str, Any] | None = None,
) -> tuple[datetime, datetime] | None:
    bounds, _ = _codex_current_turn_discovery(session_id, codex_home, snapshot)
    return bounds


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
            and item.get('type') == 'text'
            and isinstance(item.get('text'), str)
        ]
    if isinstance(parsed, dict):
        return [
            parsed[field]
            for field in ('error', 'message')
            if isinstance(parsed.get(field), str)
        ]
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
        or re.fullmatch(
            r'process exited with code (?:-[0-9]+|\+?[1-9][0-9]*)[.!]?',
            text.strip().lower(),
        )
        for text in _failure_envelope_texts(output)
    )


def _call_fingerprint(tool_name: str, payload: dict[str, Any]) -> str:
    arguments = str(payload.get('input', payload.get('arguments', '')))
    return hashlib.sha256(f'{tool_name}\0{arguments}'.encode()).hexdigest()


def _shell_command(payload: dict[str, Any]) -> str | None:
    if _normalize_tool_name(str(payload.get('name', ''))) not in (
        'exec',
        'shell_command',
    ):
        return None
    arguments = payload.get('input', payload.get('arguments', ''))

    def command_from_object(
        value: Any, *, require_cmd: bool = False
    ) -> str | None:
        if not isinstance(value, dict):
            return None
        fields = [field for field in ('command', 'cmd') if field in value]
        if len(fields) != 1 or not isinstance(value[fields[0]], str):
            return None
        if require_cmd and fields[0] != 'cmd':
            return None
        transport = set(value) - {fields[0]}
        if not transport.issubset(
            {
                'justification',
                'login',
                'max_output_tokens',
                'prefix_rule',
                'sandbox_permissions',
                'shell',
                'tty',
                'workdir',
                'yield_time_ms',
            }
        ):
            return None
        if any(
            field in value and not isinstance(value[field], bool)
            for field in ('login', 'tty')
        ):
            return None
        if any(
            field in value
            and (
                isinstance(value[field], bool)
                or not isinstance(value[field], int)
                or value[field] < 0
            )
            for field in ('max_output_tokens', 'yield_time_ms')
        ):
            return None
        if any(
            field in value
            and (not isinstance(value[field], str) or not value[field])
            for field in ('justification', 'shell', 'workdir')
        ):
            return None
        if 'sandbox_permissions' in value and value['sandbox_permissions'] not in (
            'use_default',
            'require_escalated',
        ):
            return None
        if 'prefix_rule' in value and (
            not isinstance(value['prefix_rule'], list)
            or not value['prefix_rule']
            or any(not isinstance(item, str) or not item for item in value['prefix_rule'])
        ):
            return None
        return value[fields[0]].strip()

    if isinstance(arguments, dict):
        return command_from_object(arguments)
    if not isinstance(arguments, str):
        return None

    stripped = arguments.strip()
    if re.match(r'^(?:&\s*)?(?:powershell|pwsh)(?:\.exe)?\b', stripped, re.I):
        return stripped
    if re.match(r'^(?:sh|bash)\s+', stripped, re.I):
        return stripped

    def unique_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON field: {key}')
            result[key] = value
        return result

    decoder = json.JSONDecoder(object_pairs_hook=unique_object_pairs)
    if stripped.startswith('{'):
        try:
            parsed, end = decoder.raw_decode(stripped)
        except (json.JSONDecodeError, ValueError):
            return None
        if stripped[end:].strip():
            return None
        return command_from_object(parsed)

    envelope = re.match(
        r'^const[ \t]+([A-Za-z_$][A-Za-z0-9_$]*)[ \t]*=[ \t]*'
        r'await[ \t]+tools\.exec_command[ \t]*\([ \t\r\n]*',
        stripped,
    )
    if not envelope:
        return None
    try:
        parsed, end = decoder.raw_decode(stripped, envelope.end())
    except (json.JSONDecodeError, ValueError):
        return None
    variable = re.escape(envelope.group(1))
    if re.fullmatch(
        rf'[ \t\r\n]*\)[ \t]*;[ \t\r\n]*text[ \t]*\('
        rf'[ \t]*{variable}\.output[ \t]*\)[ \t]*;[ \t\r\n]*',
        stripped[end:],
    ) is None:
        return None
    return command_from_object(parsed, require_cmd=True)


def _is_diagnostic_call(payload: dict[str, Any]) -> bool:
    command = _shell_command(payload)
    if not command:
        return False
    flags = re.IGNORECASE | re.DOTALL
    windows_wrapper_path = (
        rf'(?:"{WINDOWS_ABSOLUTE_PREFIX}'
        rf'(?:[{WINDOWS_LITERAL_PATH_CHARS}]*[\\/])?diagnose-agent-session'
        rf'[\\/]scripts[\\/]task-metrics\.ps1"'
        rf"|'{WINDOWS_ABSOLUTE_PREFIX}"
        rf"(?:[{WINDOWS_LITERAL_PATH_CHARS}]*[\\/])?diagnose-agent-session"
        rf"[\\/]scripts[\\/]task-metrics\.ps1'"
        rf'|{WINDOWS_ABSOLUTE_PREFIX}'
        rf'(?:[{WINDOWS_UNQUOTED_PATH_CHARS}]*[\\/])?diagnose-agent-session'
        rf'[\\/]scripts[\\/]task-metrics\.ps1)'
    )
    linux_wrapper_path = (
        rf'(?:"/(?:[{LINUX_LITERAL_PATH_CHARS}]*/)?diagnose-agent-session/'
        rf'scripts/task-metrics\.sh"'
        rf"|'/(?:[{LINUX_LITERAL_PATH_CHARS}]*/)?diagnose-agent-session/"
        rf"scripts/task-metrics\.sh'"
        rf'|/(?:[{LINUX_UNQUOTED_PATH_CHARS}]*/)?diagnose-agent-session/'
        rf'scripts/task-metrics\.sh)'
    )
    invocation_patterns = (
        (
            r'^[ \t]*(?:&[ \t]*)?(?:powershell|pwsh)(?:\.exe)?'
            r'(?:[ \t]+-ExecutionPolicy[ \t]+Bypass)?[ \t]+-File[ \t]+'
            + windows_wrapper_path
        ),
        (
            r'^[ \t]*(?:sh|bash)[ \t]+' + linux_wrapper_path
        ),
        (
            r"^[ \t]*\$skillRoot[ \t]*=[ \t]*(['\"])"
            rf"{WINDOWS_ABSOLUTE_PREFIX}"
            rf"(?:[{WINDOWS_LITERAL_PATH_CHARS}]*[\\/])?"
            r"diagnose-agent-session[\\/]?\1[ \t]*(?:;[ \t]*|\r?\n[ \t]*)"
            r"\$wrapper[ \t]*=[ \t]*Join-Path[ \t]+\$skillRoot[ \t]+(['\"])"
            r"scripts\\task-metrics\.ps1\2[ \t]*"
            r"(?:;[ \t]*|\r?\n[ \t]*)"
            r"(?:&[ \t]*)?(?:powershell|pwsh)(?:\.exe)?"
            r"(?:[ \t]+-ExecutionPolicy[ \t]+Bypass)?"
            r"[ \t]+-File[ \t]+\$wrapper"
        ),
        (
            rf"^[ \t]*skill_root=(['\"])/"
            rf"(?:[{LINUX_LITERAL_PATH_CHARS}]*/)?"
            r"diagnose-agent-session/?\1[ \t]*(?:;[ \t]*|\r?\n[ \t]*)"
            r"(?:sh|bash)[ \t]+(['\"])\$skill_root/scripts/"
            r"task-metrics\.sh\2"
        ),
    )
    allowed_arguments = (
        r'(?:[ \t]+--scope[ \t]+(?:turn|session|both)'
        r'|[ \t]+--client[ \t]+(?:codex|cursor|copilot)'
        rf'|[ \t]+--session-id[ \t]+{SESSION_ID_LITERAL})*[ \t]*'
    )
    return any(
        re.fullmatch(
            rf'{invocation}[ \t]+diagnose{allowed_arguments}',
            command,
            flags,
        )
        is not None
        for invocation in invocation_patterns
    )


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
) -> dict[str, Any]:
    evidence = snapshot or _load_codex_log_snapshot(session_id, codex_home)
    events, warnings = _codex_events(session_id, codex_home, evidence)
    acquisition = evidence['acquisition']
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
        return activity

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
    observed_peak_live = 0
    wait_without_live = 0
    wait_timeouts = 0
    consecutive_wait_timeouts = 0
    max_consecutive_wait_timeouts = 0
    previous_fingerprint = None
    repeated_identical_calls = 0

    for event in events:
        event_time = event['_parsed_timestamp']
        if event_time > scope_end:
            break
        in_scope = scope_start <= event_time <= scope_end
        if in_scope:
            observed_peak_live = max(observed_peak_live, len(live_agents))
        if event.get('type') != 'response_item':
            continue
        payload = event.get('payload') or {}
        payload_type = payload.get('type')
        call_id = str(payload.get('call_id', ''))
        if payload_type in ('custom_tool_call', 'function_call') and call_id:
            if _is_diagnostic_call(payload):
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
        }
    )
    return {
        'status': (
            'failed'
            if acquisition['outcome'] == 'failed'
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
    total_input = _integer(raw.get('input_tokens'), 'input_tokens')
    cache_read = _integer(raw.get('cached_input_tokens'), 'cached_input_tokens')
    cache_write = _integer(
        raw.get('cache_write_input_tokens'), 'cache_write_input_tokens'
    )
    total_output = _integer(raw.get('output_tokens'), 'output_tokens')
    reasoning = _integer(raw.get('reasoning_output_tokens'), 'reasoning_output_tokens')
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
    before = None
    after = None
    for event in events:
        event_time = event['_parsed_timestamp']
        payload = event.get('payload') or {}
        info = payload.get('info') or {}
        raw = info.get('total_token_usage')
        if (
            event.get('type') != 'event_msg'
            or payload.get('type') != 'token_count'
            or not isinstance(raw, dict)
        ):
            continue
        totals = _normalize_codex_token_totals(raw)
        if event_time < started_at:
            before = totals
        if started_at <= event_time <= ended_at:
            after = totals
    if after is None:
        return None
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
    codex_home: Path | None = None,
    codex_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    client = validate_client(client)
    try:
        matching_rows = _matching_tokscale_rows(client, session_id, tokscale_rows)
    except UsageError as error:
        matching_rows = []
        snapshot_error = str(error)
    warnings = [snapshot_error] if snapshot_error else []
    collection = {
        'outcome': 'failed' if snapshot_error else 'succeeded',
        'cause': snapshot_error,
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
            if not snapshot_error:
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
                'fallback': fallback,
                'local_log_acquisition': local_log_acquisition,
            }
        if fallback['outcome'] != 'failed':
            fallback = {'outcome': 'no-evidence', 'cause': None}
    if not snapshot_error and fallback['outcome'] != 'failed':
        if client == 'codex':
            warnings.append('No matching Tokscale row or Codex token event was found.')
        elif client == 'cursor':
            warnings.append(
                'No matching Cursor Tokscale session row was found; an existing valid '
                'Tokscale login and completed sync are recoverable prerequisites.'
            )
        else:
            warnings.append(
                'No matching GitHub Copilot CLI Tokscale session row was found; '
                'pre-session OTEL file export was required and cannot be recovered '
                'for activity before this snapshot cutoff.'
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
        'fallback': fallback,
        'local_log_acquisition': local_log_acquisition,
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
    relevant: bool = True,
    evidence: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    if status not in ('available', 'unavailable', 'failed'):
        raise UsageError(f'Invalid capability status for {name}: {status}')
    return {
        'name': name,
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
            evidence=(
                f"{session_usage['source']} whole-session usage"
                if usage_status == 'available'
                else None
            ),
            reason='; '.join(usage_warnings) if usage_status != 'available' else None,
        )
    ]

    model_status = 'available' if session_usage['source'] == 'tokscale' else (
        'failed' if _collection_failed(session_usage) else 'unavailable'
    )
    if model_status == 'failed':
        model_reason = '; '.join(usage_warnings)
    elif model_status == 'unavailable' and client == 'codex':
        model_reason = 'No matching Tokscale session/model activity row was available.'
    elif model_status == 'unavailable':
        model_reason = (
            '; '.join(usage_warnings)
            or 'Tokscale model-activity evidence was not available.'
        )
    else:
        model_reason = None
    coverage.append(
        _capability(
            'model activity',
            model_status,
            evidence='Tokscale client/session/model grouping and duration fields'
            if model_status == 'available'
            else None,
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
            relevant=turn_relevant,
            evidence=turn_evidence,
            reason=turn_reason,
        )
    )

    activities = [session_activity]
    if selected_scope == 'turn':
        activities = [turn_activity] if turn_activity is not None else []
    elif selected_scope == 'both':
        if turn_activity is not None:
            activities.append(turn_activity)
    if client == 'codex' and activities:
        activity_statuses = [_activity_capability_status(activity) for activity in activities]
        if 'failed' in activity_statuses:
            behavior_status = 'failed'
        elif 'unavailable' in activity_statuses or (
            selected_scope == 'both' and len(activities) != 2
        ):
            behavior_status = 'unavailable'
        else:
            behavior_status = 'available'
        behavior_reasons = _unique_problems(
            [
                warning
                for activity in activities
                for warning in activity.get('warnings', [])
            ]
        )
        behavior_reason = '; '.join(behavior_reasons) or (
            'Requested Codex local-log behavior evidence was unavailable.'
            if behavior_status != 'available'
            else None
        )
        behavior_evidence = (
            'Codex local-log call and coordination records'
            if behavior_status == 'available'
            else None
        )
    elif client != 'codex':
        behavior_status = 'unavailable'
        behavior_reason = _profile_behavior_reason(client)
        behavior_evidence = None
    else:
        behavior_status = 'unavailable'
        behavior_reason = 'Requested Codex local-log behavior evidence was unavailable.'
        behavior_evidence = None
    for name in BEHAVIOR_CAPABILITY_NAMES:
        coverage.append(
            _capability(
                name,
                behavior_status,
                evidence=behavior_evidence,
                reason=behavior_reason,
            )
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
    if selected_scope not in ('turn', 'session', 'both'):
        raise UsageError(f'Unsupported diagnostic scope: {selected_scope}')
    client = validate_client(str(session_usage['client']))
    local_acquisition = _report_codex_acquisition(
        session_usage, session_activity, codex_acquisition
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
    problems = [problem for scope in scopes for problem in scope['problems']]
    if selected_scope in ('turn', 'both') and turn_usage is None:
        problems.append(
            f'Current-turn diagnostics are unavailable for the '
            f'{PROFILE_LABELS[client]} profile.'
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
    unavailable_surfaces = [
        f"{capability['name']}: {capability['reason']}"
        for capability in capabilities
        if capability['relevant'] and capability['status'] in ('unavailable', 'failed')
    ]
    recovery_prerequisites = []
    if _collection_failed(session_usage):
        recovery_prerequisites.append(
            'Resolve the reported Tokscale collection failure for the same '
            'client/session pair; install or restore a compatible build when the '
                'reported cause identifies missing or incompatible Tokscale.'
        )
    if _fallback_failed(session_usage):
        recovery_prerequisites.append(
            'Repair or restore the exact Codex local session log token totals; '
            'the reported local fallback cause must be resolved before usage can '
            'be recovered.'
        )
    if (
        not _collection_failed(session_usage)
        and not _fallback_failed(session_usage)
        and session_usage['status'] == 'unavailable'
    ):
        if client == 'cursor':
            recovery_prerequisites.append(
                'Use an existing valid Tokscale login and complete Cursor sync, then rerun '
                'the same client/session pair; the diagnostic performs neither action.'
            )
        elif client == 'copilot':
            recovery_prerequisites.append(
                'Activity before this snapshot cutoff cannot regain missing usage and '
                'model-activity telemetry. For future activity, configure OTEL file '
                'export before the session starts.'
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
    return {
        'client': client,
        'session_id': session_usage['session_id'],
        'captured_at': session_usage['captured_at'],
        'selected_scope': selected_scope,
        'profile': PROFILE_LABELS[client],
        'capabilities': capabilities,
        'session_usage': _build_scope_report(
            'whole session', session_usage, session_activity, session_bounds
        ),
        'scopes': scopes,
        'findings': _unique_problems(findings),
        'problems': _unique_problems(problems + unavailable_surfaces),
        'limitations': [
            'Summed model and tool durations can overlap the elapsed span.',
            'Subagent lifecycle counts are observed lower bounds.',
            'Child-session tokens require a stable child mapping for attribution.',
            'Session usage coverage does not establish behavior health.',
        ],
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
    if activity['status'] == 'unavailable':
        lines.extend(['- Tool calls: unavailable', '- Agent coordination: unavailable'])
    else:
        if activity['status'] == 'failed':
            reason = _markdown_text(
                '; '.join(activity.get('warnings', [])) or 'collection failed'
            )
            lines.extend(
                [
                    f'- Tool calls: failed — {reason}',
                    f'- Agent coordination: failed — {reason}',
                ]
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
        coordination = activity['coordination']
        calls = ', '.join(
            f'{name}={coordination.get(name, 0)}'
            for name in COORDINATION_TOOLS
            if coordination.get(name, 0)
        ) or 'none observed'
        lines.append(f'- Agent coordination calls: {calls}')
        lines.append(
            '- Agent lifecycle: '
            f"spawned={coordination.get('spawn_successes', 0)}, "
            f"spawn failures={coordination.get('spawn_failures', 0)}, "
            f"completed={coordination.get('completed_agents', 0)}, "
            f"failed={coordination.get('failed_agents', 0)}, "
            f"observed peak live={coordination.get('observed_peak_live_agents', 0)}, "
            f"observed live at end={coordination.get('observed_live_agents_at_end', 0)}"
        )
        lines.append(
            '- Wait behavior: '
            f"timeouts={coordination.get('wait_timeouts', 0)}, "
            f"max consecutive timeouts={coordination.get('max_consecutive_wait_timeouts', 0)}, "
            'without observed live agent='
            f"{coordination.get('wait_without_observed_live_agent', 0)}"
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
        f"- Snapshot cutoff (UTC): {_markdown_text(report['captured_at'])}",
        '',
        '#### Capability Coverage',
    ]
    for capability in report['capabilities']:
        detail = capability['evidence'] or capability['reason'] or 'no detail'
        relevance = 'relevant' if capability['relevant'] else 'not requested'
        lines.append(
            f"- {_markdown_text(capability['name'])}: "
            f"{_markdown_text(capability['status'])} "
            f"({_markdown_text(relevance)}) — {_markdown_text(detail)}"
        )
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
    lines.extend(['', '#### Problems and Unavailable Surfaces'])
    lines.append(
        f"- Findings: {_markdown_text('; '.join(report['findings']))}"
        if report['findings']
        else '- Findings: none from available evidence'
    )
    if report['problems']:
        lines.extend(f'- {_markdown_text(problem)}' for problem in report['problems'])
    else:
        lines.append('- Problems: none from available evidence')
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
        '--scope', choices=('turn', 'session', 'both'), default='both'
    )
    return parser


def _unavailable_tool_activity(
    warnings: list[str], *, status: str = 'unavailable'
) -> dict[str, Any]:
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
    }


def unavailable_tool_activity(problem: str) -> dict[str, Any]:
    return _unavailable_tool_activity([problem])


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
        rows = []
        error = None
        try:
            rows = capture_tokscale_snapshot(
                client, None, None, session_id=session_id
            )
        except UsageError as usage_error:
            error = str(usage_error)
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
        started_at, ended_at = session_bounds or (None, None)
        usage_report = build_session_usage(
            client,
            session_id,
            captured,
            tokscale_rows=rows,
            snapshot_error=error,
            codex_snapshot=codex_snapshot,
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
                    )
                    if turn_bounds
                    else _unavailable_tool_activity(
                        turn_discovery_problems
                        or acquisition_messages
                        or ['Current-turn boundary was not found in the Codex log.'],
                        status=(
                            'failed'
                            if acquisition['outcome'] == 'failed'
                            else 'unavailable'
                        ),
                    )
                )
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
