#!/usr/bin/env python
"""Check harness recommendations and required effective runtime values."""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


_DEFAULT_VERSION_PATTERN = r'(\d+(?:\.\d+)+(?:[-+][0-9A-Za-z.-]+)?)'
_MAX_COMMAND_OUTPUT = 16_384
_MAX_CONFIG_RPC_OUTPUT = 1_048_576
_LOCK_STALE_SECONDS = 300
_RUNTIME_PROBES = {
    'node': (('node', '--version'), _DEFAULT_VERSION_PATTERN),
}
_MCP_CHECK_FIELDS = {
    'command-exists': frozenset({'kind', 'command'}),
    'runtime-version': frozenset({'kind', 'runtime', 'minimum'}),
    'workspace-path': frozenset({'kind', 'path', 'executable'}),
    'environment-variable': frozenset({'kind', 'name'}),
}


class PolicyError(RuntimeError):
    """Raised when a tool policy cannot be evaluated safely."""


class DetectorError(PolicyError):
    """Raised when a detector exists but cannot complete."""


class VersionUnreadable(PolicyError):
    """Raised when a detector responds without a usable version."""


@dataclass(frozen=True)
class Finding:
    code: str
    tool: str
    message: str
    guidance: str
    target_kind: str | None = None
    target_id: str | None = None
    action: str | None = None


@dataclass(frozen=True)
class HookResult:
    ran: bool
    findings: tuple[Finding, ...] = ()
    internal_error: bool = False

    @property
    def requires_user_prompt(self) -> bool:
        return not self.internal_error and any(
            finding.code != 'detector-error' for finding in self.findings
        )


def parse_version(value: str) -> tuple[int, ...]:
    match = re.search(r'\d+(?:\.\d+)+', value)
    if match is None:
        raise ValueError('version contains no ordered numeric components')
    return tuple(int(part) for part in match.group(0).split('.'))


def is_strictly_greater(installed: str, target: str) -> bool:
    installed_parts = parse_version(installed)
    target_parts = parse_version(target)
    width = max(len(installed_parts), len(target_parts))
    return installed_parts + (0,) * (width - len(installed_parts)) > target_parts + (0,) * (
        width - len(target_parts)
    )


def _json_path(value: Any, dotted_path: str) -> Any:
    current = value
    for part in dotted_path.split('.'):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _expand(value: str) -> str:
    return value.format(home=str(Path.home()))


def _parse_json_command_output(output: str) -> Any:
    decoder = json.JSONDecoder()
    for match in re.finditer(r'(?m)^[ \t]*(?=[{\[])', output):
        try:
            value, _ = decoder.raw_decode(output, match.end())
        except json.JSONDecodeError:
            continue
        return value
    raise VersionUnreadable('JSON command output is invalid')


def _run_command(command: list[str], timeout: float) -> str | None:
    expanded = [_expand(argument) for argument in command]
    resolved = shutil.which(expanded[0])
    if resolved is not None:
        expanded[0] = resolved
    try:
        process = subprocess.Popen(
            expanded,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except (FileNotFoundError, PermissionError):
        return None
    except OSError as error:
        raise DetectorError('detector command failed to start') from error
    if process.stdout is None:
        process.kill()
        raise DetectorError('detector command output is unavailable')

    captured = bytearray()
    overflow = threading.Event()

    def read_output() -> None:
        while True:
            chunk = process.stdout.read(4096)
            if not chunk:
                return
            remaining = _MAX_COMMAND_OUTPUT - len(captured)
            if remaining > 0:
                captured.extend(chunk[:remaining])
            if len(chunk) > remaining:
                overflow.set()
                process.kill()
                return

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    try:
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as error:
            process.kill()
            process.wait()
            reader.join(timeout=1)
            raise DetectorError('detector command timed out') from error
        reader.join(timeout=1)
        if reader.is_alive():
            process.kill()
            process.wait()
            raise DetectorError('detector output reader did not finish')
        if overflow.is_set():
            raise DetectorError('detector command output exceeded the limit')
        if returncode != 0:
            raise DetectorError('detector command returned a failure status')
        return captured.decode('utf-8', errors='replace')
    finally:
        process.stdout.close()


def _read_manifest_version(pattern: str, json_path: str) -> str | None:
    candidates = sorted(glob.glob(_expand(pattern)), reverse=True)
    unreadable = False
    for candidate in candidates:
        try:
            parsed = json.loads(Path(candidate).read_text(encoding='utf-8'))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            unreadable = True
            continue
        value = _json_path(parsed, json_path)
        if isinstance(value, (str, int, float)):
            return str(value)
        unreadable = True
    if unreadable:
        raise VersionUnreadable('manifest contains no usable version')
    return None


def run_detector(detector: dict[str, Any]) -> str | None:
    if not isinstance(detector, dict):
        raise PolicyError('detector must be an object')
    kind = detector.get('kind')
    if kind == 'fixed':
        value = detector.get('value')
        return value if isinstance(value, str) and value else None
    if kind == 'json-manifest-glob':
        pattern = detector.get('glob')
        json_path = detector.get('json_path')
        if not isinstance(pattern, str) or not isinstance(json_path, str):
            raise PolicyError('manifest detector requires glob and json_path')
        return _read_manifest_version(pattern, json_path)
    if kind in {'command-regex', 'json-command', 'json-command-item'}:
        command = detector.get('command')
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(argument, str) and argument for argument in command)
        ):
            raise PolicyError('command detector requires a non-empty command array')
        timeout = detector.get('timeout_seconds', 5)
        if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 30:
            raise PolicyError('command detector timeout must be between 0 and 30 seconds')
        output = _run_command(command, float(timeout))
        if output is None:
            return None
        if kind in {'json-command', 'json-command-item'}:
            parsed_output = _parse_json_command_output(output)
        if kind == 'json-command':
            json_path = detector.get('json_path')
            if not isinstance(json_path, str):
                raise PolicyError('JSON command detector requires json_path')
            value = _json_path(parsed_output, json_path)
            if not isinstance(value, (str, int, float)):
                raise VersionUnreadable('JSON command output contains no usable version')
            return str(value)
        if kind == 'json-command-item':
            fields = ('items_path', 'match_path', 'match_value', 'value_path')
            if any(
                not isinstance(detector.get(field), str) or not detector[field]
                for field in fields
            ):
                raise PolicyError(
                    'JSON command item detector requires items_path, match_path, '
                    'match_value, and value_path'
                )
            items = _json_path(parsed_output, detector['items_path'])
            if not isinstance(items, list):
                raise VersionUnreadable('JSON command output contains no usable item list')
            fallback_glob = detector.get('fallback_manifest_glob')
            fallback_json_path = detector.get('fallback_manifest_json_path')
            if (fallback_glob is None) != (fallback_json_path is None) or (
                fallback_glob is not None
                and (
                    not isinstance(fallback_glob, str)
                    or not fallback_glob
                    or not isinstance(fallback_json_path, str)
                    or not fallback_json_path
                )
            ):
                raise PolicyError(
                    'JSON command item manifest fallback requires glob and json path'
                )
            matched = False
            for item in items:
                if _json_path(item, detector['match_path']) != detector['match_value']:
                    continue
                matched = True
                value = _json_path(item, detector['value_path'])
                if isinstance(value, (str, int, float)):
                    rendered = str(value)
                    try:
                        parse_version(rendered)
                        return rendered
                    except ValueError:
                        pass
                if fallback_glob is not None:
                    fallback = _read_manifest_version(fallback_glob, fallback_json_path)
                    if fallback is not None:
                        return fallback
            if matched:
                raise VersionUnreadable('matching JSON command item contains no usable version')
            return None
        pattern = detector.get('pattern', _DEFAULT_VERSION_PATTERN)
        if not isinstance(pattern, str):
            raise PolicyError('command detector pattern must be a string')
        match = re.search(pattern, output)
        if match is None:
            raise VersionUnreadable('command output contains no usable version')
        return match.group(1)
    raise PolicyError('unsupported detector kind')


def _validate_tool(tool: Any) -> dict[str, Any]:
    if not isinstance(tool, dict):
        raise PolicyError('each tool must be an object')
    for field in ('id', 'name', 'target_version', 'install', 'upgrade'):
        if not isinstance(tool.get(field), str) or not tool[field]:
            raise PolicyError(f'tool field {field} must be a non-empty string')
    if tool.get('comparison') != '>':
        raise PolicyError('tool comparison must be >')
    detectors = tool.get('detectors')
    if not isinstance(detectors, list) or not detectors:
        raise PolicyError('tool detectors must be a non-empty array')
    parse_version(tool['target_version'])
    return tool


def _validate_required_value(requirement: Any) -> dict[str, Any]:
    if not isinstance(requirement, dict):
        raise PolicyError('each required value must be an object')
    for field in ('id', 'name', 'expected', 'guidance'):
        if not isinstance(requirement.get(field), str) or not requirement[field]:
            raise PolicyError(f'required value field {field} must be a non-empty string')
    detectors = requirement.get('detectors')
    if not isinstance(detectors, list) or not detectors:
        raise PolicyError('required value detectors must be a non-empty array')
    maintenance = requirement.get('maintenance')
    if maintenance is not None:
        validated_maintenance = _validate_maintenance(maintenance)
        if validated_maintenance['kind'] != 'config-write':
            raise PolicyError('required value maintenance kind is invalid')
    return requirement


def _check_required_values(policy: dict[str, Any]) -> list[Finding]:
    requirements = policy.get('required_values', [])
    if not isinstance(requirements, list):
        raise PolicyError('policy required_values must be an array')
    findings: list[Finding] = []
    for raw_requirement in requirements:
        requirement = _validate_required_value(raw_requirement)
        actual = None
        for detector in requirement['detectors']:
            try:
                actual = run_detector(detector)
            except (PolicyError, re.error):
                continue
            if actual is not None:
                break
        if actual is None:
            findings.append(
                Finding(
                    'detector-error',
                    requirement['name'],
                    'effective value detection failed',
                    requirement['guidance'],
                    'setting' if requirement.get('maintenance') else None,
                    requirement['id'] if requirement.get('maintenance') else None,
                )
            )
            continue
        if actual != requirement['expected']:
            findings.append(
                Finding(
                    'required-value-mismatch',
                    requirement['name'],
                    f'is {actual}; it must be {requirement["expected"]} for this project',
                    requirement['guidance'],
                    'setting' if requirement.get('maintenance') else None,
                    requirement['id'] if requirement.get('maintenance') else None,
                    'configure' if requirement.get('maintenance') else None,
                )
            )
    return findings


def _validate_maintenance(maintenance: Any) -> dict[str, Any]:
    if not isinstance(maintenance, dict):
        raise PolicyError('setting maintenance is invalid')
    kind = maintenance.get('kind')
    if kind == 'config-write':
        if set(maintenance) != {'kind', 'write_key_path', 'write_value'}:
            raise PolicyError('configuration maintenance is invalid')
        if (
            not isinstance(maintenance['write_key_path'], str)
            or not maintenance['write_key_path']
            or maintenance['write_value'] is None
        ):
            raise PolicyError('configuration maintenance is invalid')
        return maintenance
    if kind == 'manual-session':
        if set(maintenance) != {'kind', 'instruction'} or not isinstance(
            maintenance.get('instruction'), str
        ) or not maintenance['instruction']:
            raise PolicyError('manual session maintenance is invalid')
        return maintenance
    raise PolicyError('setting maintenance kind is invalid')


def _validate_manual_session_action(action: Any) -> dict[str, Any]:
    if not isinstance(action, dict) or set(action) != {
        'id',
        'name',
        'detectors',
        'maintenance',
        'guidance',
    }:
        raise PolicyError('manual session action is invalid')
    for field in ('id', 'name', 'guidance'):
        if not isinstance(action.get(field), str) or not action[field]:
            raise PolicyError(
                f'manual session action field {field} must be a non-empty string'
            )
    detectors = action.get('detectors')
    if not isinstance(detectors, list) or not detectors:
        raise PolicyError('manual session action detectors must be a non-empty array')
    maintenance = _validate_maintenance(action.get('maintenance'))
    if maintenance['kind'] != 'manual-session':
        raise PolicyError('manual session action maintenance kind is invalid')
    return action


def _manual_session_action_available(action: dict[str, Any]) -> bool:
    for detector in action['detectors']:
        try:
            if run_detector(detector) is not None:
                return True
        except (PolicyError, re.error):
            continue
    return False


def _check_manual_session_actions(policy: dict[str, Any]) -> list[Finding]:
    raw_actions = policy.get('manual_session_actions', [])
    if not isinstance(raw_actions, list):
        raise PolicyError('policy manual_session_actions must be an array')
    findings: list[Finding] = []
    for raw_action in raw_actions:
        action = _validate_manual_session_action(raw_action)
        if not _manual_session_action_available(action):
            findings.append(Finding(
                'detector-error',
                action['name'],
                'session action availability detection failed',
                action['guidance'],
            ))
            continue
        findings.append(Finding(
            'manual-session-action',
            action['name'],
            'requires explicit activation for parallel subagents in this session',
            action['guidance'],
            'setting',
            action['id'],
            'configure',
        ))
    return findings


def _validate_config_requirement(requirement: Any) -> dict[str, Any]:
    if not isinstance(requirement, dict):
        raise PolicyError('each configuration requirement must be an object')
    expected_fields = {
        'id',
        'name',
        'minimum_total_threads',
        'primary_threads',
        'read_key_paths',
        'maintenance',
        'guidance',
    }
    if set(requirement) != expected_fields:
        raise PolicyError('configuration requirement fields are invalid')
    for field in (
        'id',
        'name',
        'guidance',
    ):
        if not isinstance(requirement[field], str) or not requirement[field]:
            raise PolicyError(
                f'configuration requirement field {field} must be a non-empty string'
            )
    minimum = requirement['minimum_total_threads']
    primary = requirement['primary_threads']
    if (
        type(minimum) is not int
        or type(primary) is not int
        or minimum <= primary
        or primary < 1
    ):
        raise PolicyError('configuration requirement thread counts are invalid')
    key_paths = requirement['read_key_paths']
    maintenance = _validate_maintenance(requirement['maintenance'])
    if (
        not isinstance(key_paths, list)
        or not key_paths
        or not all(isinstance(path, str) and path for path in key_paths)
        or len(key_paths) != len(set(key_paths))
        or maintenance['kind'] != 'config-write'
        or maintenance['write_key_path'] not in key_paths
        or type(maintenance['write_value']) is not int
        or maintenance['write_value'] != minimum - primary
    ):
        raise PolicyError('configuration requirement key paths are invalid')
    return requirement


class _CodexConfigRpcClient:
    def __init__(self, cwd: Path, timeout: float = 4) -> None:
        executable = shutil.which('codex')
        if executable is None:
            raise DetectorError('Codex configuration RPC is unavailable')
        try:
            self._process = subprocess.Popen(
                [executable, 'app-server'],
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, PermissionError, OSError) as error:
            raise DetectorError('Codex configuration RPC failed to start') from error
        if self._process.stdin is None or self._process.stdout is None:
            self.close()
            raise DetectorError('Codex configuration RPC pipes are unavailable')
        self._timeout = timeout
        self._next_id = 1
        self._output_size = 0
        self._overflow = threading.Event()
        self._lines: queue.Queue[bytes | None] = queue.Queue()
        self._reader = threading.Thread(target=self._read_output, daemon=True)
        self._reader.start()
        try:
            self._send({
                'method': 'initialize',
                'id': 0,
                'params': {
                    'clientInfo': {
                        'name': 'smartkit_hook',
                        'title': 'SmartKit Hook',
                        'version': '1',
                    }
                },
            })
            self._wait_for_response(0)
            self._send({'method': 'initialized', 'params': {}})
        except Exception:
            self.close()
            raise

    def _read_output(self) -> None:
        process = self._process
        output = process.stdout
        if output is None:
            self._lines.put(None)
            return
        try:
            while True:
                line = output.readline()
                if not line:
                    return
                self._output_size += len(line)
                if self._output_size > _MAX_CONFIG_RPC_OUTPUT:
                    self._overflow.set()
                    process.kill()
                    return
                self._lines.put(line)
        finally:
            self._lines.put(None)

    def _send(self, message: dict[str, Any]) -> None:
        if self._process.stdin is None:
            raise DetectorError('Codex configuration RPC input is unavailable')
        payload = (json.dumps(message, separators=(',', ':')) + '\n').encode('utf-8')
        try:
            self._process.stdin.write(payload)
            self._process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise DetectorError('Codex configuration RPC input failed') from error

    def _wait_for_response(self, request_id: int) -> dict[str, Any]:
        deadline = time.monotonic() + self._timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise DetectorError('Codex configuration RPC timed out')
            try:
                line = self._lines.get(timeout=remaining)
            except queue.Empty as error:
                raise DetectorError('Codex configuration RPC timed out') from error
            if line is None:
                if self._overflow.is_set():
                    raise DetectorError(
                        'Codex configuration RPC output exceeded the limit'
                    )
                raise DetectorError('Codex configuration RPC ended unexpectedly')
            try:
                message = json.loads(line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(message, dict) or message.get('id') != request_id:
                continue
            if 'error' in message:
                raise DetectorError('Codex configuration RPC returned an error')
            result = message.get('result')
            if not isinstance(result, dict):
                raise DetectorError(
                    'Codex configuration RPC returned an invalid result'
                )
            return result

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        self._send({'method': method, 'id': request_id, 'params': params})
        return self._wait_for_response(request_id)

    def close(self) -> None:
        process = getattr(self, '_process', None)
        if process is None:
            return
        if process.stdin is not None:
            try:
                process.stdin.close()
            except OSError:
                pass
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if process.stdout is not None:
            process.stdout.close()
        reader = getattr(self, '_reader', None)
        if reader is not None:
            reader.join(timeout=1)
        self._process = None

    def __enter__(self) -> '_CodexConfigRpcClient':
        return self

    def __exit__(self, *_error: object) -> None:
        self.close()


def _effective_spawned_threads(
    response: dict[str, Any],
    key_paths: list[str],
) -> int | None:
    config = response.get('config')
    if not isinstance(config, dict):
        raise DetectorError('Codex effective configuration is unavailable')
    for key_path in key_paths:
        value = _json_path(config, key_path)
        if value is None:
            continue
        if type(value) is not int or value < 1:
            raise DetectorError('Codex parallel-agent configuration is invalid')
        return value
    return None


def check_config_requirements(
    policy: dict[str, Any],
    project_root: Path,
    *,
    rpc: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
) -> list[Finding]:
    raw_requirements = policy.get('config_requirements', [])
    if not isinstance(raw_requirements, list):
        raise PolicyError('policy config_requirements must be an array')
    findings: list[Finding] = []

    def check_with_rpc(
        requirement: dict[str, Any],
        request: Callable[[str, dict[str, Any]], dict[str, Any]],
    ) -> None:
        read_params = {'includeLayers': False, 'cwd': str(project_root)}
        response = request('config/read', read_params)
        spawned = _effective_spawned_threads(response, requirement['read_key_paths'])
        minimum_total = requirement['minimum_total_threads']
        primary = requirement['primary_threads']
        target_spawned = minimum_total - primary
        if spawned is not None and spawned >= target_spawned:
            return
        actual = (
            'is unset'
            if spawned is None
            else f'allows {spawned + primary} concurrent agents including the primary'
        )
        findings.append(Finding(
            'required-value-mismatch',
            requirement['name'],
            f'{actual}; it must allow at least {minimum_total} concurrent agents '
            'including the primary for this project',
            requirement['guidance'],
            'setting',
            requirement['id'],
            'configure',
        ))

    validated = [
        _validate_config_requirement(raw_requirement)
        for raw_requirement in raw_requirements
    ]
    if not validated:
        return findings

    def inspect(request: Callable[[str, dict[str, Any]], dict[str, Any]]) -> None:
        for requirement in validated:
            try:
                check_with_rpc(requirement, request)
            except (PolicyError, DetectorError, OSError):
                findings.append(Finding(
                    'detector-error',
                    requirement['name'],
                    'could not verify the effective parallel-agent limit',
                    requirement['guidance'],
                ))

    if rpc is not None:
        inspect(rpc)
    else:
        try:
            with _CodexConfigRpcClient(project_root) as client:
                inspect(client.request)
        except (PolicyError, DetectorError, OSError):
            requirement = validated[0]
            findings.append(Finding(
                'detector-error',
                requirement['name'],
                'could not verify the effective parallel-agent limit',
                requirement['guidance'],
            ))
    return findings


def check_policy(policy: dict[str, Any]) -> list[Finding]:
    tools = policy.get('tools')
    if not isinstance(policy.get('harness'), str) or not isinstance(tools, list):
        raise PolicyError('policy requires harness and tools')
    config_requirements = policy.get('config_requirements', [])
    manual_session_actions = policy.get('manual_session_actions', [])
    required_values = policy.get('required_values', [])
    if (
        not isinstance(config_requirements, list)
        or not isinstance(manual_session_actions, list)
        or not isinstance(required_values, list)
    ):
        raise PolicyError('policy value requirements are invalid')
    for raw_requirement in config_requirements:
        _validate_config_requirement(raw_requirement)
    for raw_action in manual_session_actions:
        _validate_manual_session_action(raw_action)
    findings: list[Finding] = []
    for raw_tool in tools:
        tool = _validate_tool(raw_tool)
        installed = None
        detector_failed = False
        version_unreadable = False
        for detector in tool['detectors']:
            try:
                installed = run_detector(detector)
            except VersionUnreadable:
                version_unreadable = True
                continue
            except (PolicyError, re.error):
                detector_failed = True
                continue
            if installed is not None:
                break
        if installed is None:
            if version_unreadable:
                findings.append(
                    Finding(
                        'version-unreadable',
                        tool['name'],
                        'has an unreadable installed version',
                        tool['upgrade'],
                        'tool',
                        tool['id'],
                        'upgrade',
                    )
                )
            else:
                code = 'detector-error' if detector_failed else 'tool-missing'
                message = (
                    'version detection failed'
                    if detector_failed
                    else 'is not installed for this harness'
                )
                findings.append(Finding(
                    code,
                    tool['name'],
                    message,
                    tool['install'],
                    'tool' if code == 'tool-missing' else None,
                    tool['id'] if code == 'tool-missing' else None,
                    'install' if code == 'tool-missing' else None,
                ))
            continue
        try:
            greater = is_strictly_greater(installed, tool['target_version'])
        except ValueError:
            findings.append(
                Finding(
                    'version-unreadable',
                    tool['name'],
                    'has an unreadable installed version',
                    tool['upgrade'],
                    'tool',
                    tool['id'],
                    'upgrade',
                )
            )
            continue
        if not greater:
            installed_parts = parse_version(installed)
            target_parts = parse_version(tool['target_version'])
            width = max(len(installed_parts), len(target_parts))
            normalized_installed = installed_parts + (0,) * (width - len(installed_parts))
            normalized_target = target_parts + (0,) * (width - len(target_parts))
            relation = (
                'equals the target version'
                if normalized_installed == normalized_target
                else 'is older than the target version'
            )
            findings.append(
                Finding(
                    'version-not-greater',
                    tool['name'],
                    f'{relation}; it must be newer than {tool["target_version"]}',
                    tool['upgrade'],
                    'tool',
                    tool['id'],
                    'upgrade',
                )
            )
    findings.extend(_check_required_values(policy))
    findings.extend(_check_manual_session_actions(policy))
    return findings


def default_mcp_registry_path() -> Path:
    runtime_root = Path(__file__).resolve().parents[1]
    for ancestor in runtime_root.parents:
        candidate = ancestor / 'mcp' / 'registry.json'
        if candidate.is_file():
            return candidate
    raise PolicyError('plugin MCP registry is unavailable')


def resolve_project_root(cwd: Path | None = None) -> Path:
    current = (cwd or Path.cwd()).resolve()
    candidates = (current, *current.parents)
    for candidate in candidates:
        if (candidate / '.agents' / 'config.json').is_file():
            return candidate
    for candidate in candidates:
        if (candidate / '.git').exists():
            return candidate
    return current


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PolicyError(f'unable to load {label}') from error
    if not isinstance(value, dict):
        raise PolicyError(f'{label} must contain an object')
    return value


def _mcp_servers_from_registry(path: Path, harness: str) -> list[dict[str, Any]]:
    if harness not in {'codex', 'cursor', 'copilot', 'qoder'}:
        raise PolicyError('MCP harness is invalid')
    document = _load_json_object(path, 'plugin MCP registry')
    if set(document) != {'servers'} or not isinstance(document.get('servers'), list):
        raise PolicyError('plugin MCP registry is invalid')
    servers: list[dict[str, Any]] = []
    for raw_server in document['servers']:
        if not isinstance(raw_server, dict):
            raise PolicyError('plugin MCP registry is invalid')
        harnesses = raw_server.get('harnesses')
        if (
            not isinstance(harnesses, list)
            or not harnesses
            or not all(isinstance(item, str) for item in harnesses)
            or len(harnesses) != len(set(harnesses))
            or set(harnesses) - {'codex', 'cursor', 'copilot', 'qoder'}
        ):
            raise PolicyError('plugin MCP registry is invalid')
        if harness in harnesses:
            checks = _effective_readiness_checks(
                raw_server,
                raw_server,
                harness=harness,
                enabled_harnesses=harnesses,
                label='plugin MCP registry',
            )
            if checks is not None:
                servers.append({
                    'id': raw_server.get('id'),
                    'readiness': {'checks': checks},
                })
    return servers


def _current_operating_system() -> str:
    if sys.platform == 'win32':
        return 'windows'
    if sys.platform.startswith('linux'):
        return 'linux'
    raise PolicyError(f'MCP operating system is unsupported: {sys.platform}')


def _inferred_readiness_checks(effective: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    command = effective.get('command')
    if isinstance(command, str):
        if '/' in command or '\\' in command:
            workspace_prefix = '${workspaceFolder}/'
            path = (
                command[len(workspace_prefix):]
                if command.startswith(workspace_prefix)
                else command
            )
            checks.append({
                'kind': 'workspace-path', 'path': path, 'executable': True,
            })
        else:
            checks.append({'kind': 'command-exists', 'command': command})
    env = effective.get('env', [])
    if not isinstance(env, list):
        raise PolicyError('MCP configuration is invalid')
    checks.extend({'kind': 'environment-variable', 'name': name} for name in env)
    return checks


def _effective_readiness_checks(
    declared: dict[str, Any],
    effective: dict[str, Any],
    *,
    harness: str,
    enabled_harnesses: list[str],
    label: str,
) -> list[object] | None:
    readiness = declared.get('readiness')
    if readiness is None:
        return _inferred_readiness_checks(effective)
    if (
        not isinstance(readiness, dict)
        or set(readiness) - {'harnesses', 'operatingSystems', 'checks'}
    ):
        raise PolicyError(f'{label} readiness is invalid')
    selected_harnesses = enabled_harnesses
    if 'harnesses' in readiness:
        selected_harnesses = _override_selector_values(
            readiness['harnesses'], allowed={'codex', 'cursor', 'copilot', 'qoder'}
        )
        if set(selected_harnesses) - set(enabled_harnesses):
            raise PolicyError(f'{label} readiness is invalid')
    if harness not in selected_harnesses:
        return None
    if 'operatingSystems' in readiness:
        selected_operating_systems = _override_selector_values(
            readiness['operatingSystems'], allowed={'windows', 'linux'}
        )
        if _current_operating_system() not in selected_operating_systems:
            return None
    if 'checks' not in readiness:
        return _inferred_readiness_checks(effective)
    checks = readiness['checks']
    if not isinstance(checks, list):
        raise PolicyError(f'{label} readiness is invalid')
    return checks


def _override_selector_values(
    value: object,
    *,
    allowed: set[str],
) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) for item in value)
        or len(value) != len(set(value))
        or set(value) - allowed
    ):
        raise PolicyError('project MCP configuration is invalid')
    return value


def _validate_override_values(values: dict[str, Any], transport: str) -> None:
    if transport == 'http' and set(values) - {'url'}:
        raise PolicyError('project MCP configuration is invalid')
    if transport == 'stdio' and 'url' in values:
        raise PolicyError('project MCP configuration is invalid')
    for key in ('command', 'cwd'):
        if key in values and (not isinstance(values[key], str) or not values[key]):
            raise PolicyError('project MCP configuration is invalid')
    if 'args' in values and (
        not isinstance(values['args'], list)
        or not all(isinstance(item, str) and item for item in values['args'])
    ):
        raise PolicyError('project MCP configuration is invalid')
    if 'env' in values and (
        not isinstance(values['env'], list)
        or not all(
            isinstance(item, str)
            and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', item) is not None
            for item in values['env']
        )
        or len(values['env']) != len(set(values['env']))
    ):
        raise PolicyError('project MCP configuration is invalid')
    if 'url' in values and (
        not isinstance(values['url'], str)
        or not values['url'].startswith(('https://', 'http://'))
    ):
        raise PolicyError('project MCP configuration is invalid')


def _mcp_servers_from_project(project_root: Path, harness: str) -> list[dict[str, Any]]:
    if harness not in {'codex', 'cursor', 'copilot', 'qoder'}:
        raise PolicyError('MCP harness is invalid')
    path = project_root / '.agents' / 'config.json'
    if not path.is_file():
        return []
    document = _load_json_object(path, 'project agent config')
    mcp = document.get('mcp')
    if mcp is None:
        return []
    if not isinstance(mcp, list):
        raise PolicyError('project MCP configuration is invalid')
    servers: list[dict[str, Any]] = []
    for raw_server in mcp:
        if not isinstance(raw_server, dict):
            raise PolicyError('project MCP configuration is invalid')
        harnesses = raw_server.get('harnesses', ['codex', 'cursor', 'copilot', 'qoder'])
        if (
            not isinstance(harnesses, list)
            or not harnesses
            or not all(isinstance(item, str) for item in harnesses)
            or len(harnesses) != len(set(harnesses))
            or set(harnesses) - {'codex', 'cursor', 'copilot', 'qoder'}
        ):
            raise PolicyError('project MCP configuration is invalid')
        if harness in harnesses:
            base_command = raw_server.get('command')
            base_url = raw_server.get('url')
            has_base_command = isinstance(base_command, str) and bool(base_command)
            has_base_url = isinstance(base_url, str) and bool(base_url)
            if has_base_command == has_base_url:
                raise PolicyError('project MCP configuration is invalid')
            transport = 'stdio' if has_base_command else 'http'
            effective = dict(raw_server)
            overrides = raw_server.get('overrides', [])
            if not isinstance(overrides, list):
                raise PolicyError('project MCP configuration is invalid')
            operating_system = None
            for override in overrides:
                if not isinstance(override, dict) or set(override) != {'when', 'set'}:
                    raise PolicyError('project MCP configuration is invalid')
                selector = override['when']
                values = override['set']
                if (
                    not isinstance(selector, dict)
                    or not selector
                    or set(selector) - {'harnesses', 'operatingSystems'}
                    or not isinstance(values, dict)
                    or not values
                    or set(values) - {'command', 'args', 'cwd', 'env', 'url'}
                ):
                    raise PolicyError('project MCP configuration is invalid')
                selected_harnesses = (
                    _override_selector_values(
                        selector['harnesses'], allowed={'codex', 'cursor', 'copilot', 'qoder'}
                    )
                    if 'harnesses' in selector else harnesses
                )
                if set(selected_harnesses) - set(harnesses):
                    raise PolicyError('project MCP configuration is invalid')
                selected_operating_systems = (
                    _override_selector_values(
                        selector['operatingSystems'], allowed={'windows', 'linux'}
                    )
                    if 'operatingSystems' in selector else None
                )
                _validate_override_values(values, transport)
                if selected_operating_systems is not None and operating_system is None:
                    operating_system = _current_operating_system()
                if (
                    harness in selected_harnesses
                    and (
                        selected_operating_systems is None
                        or operating_system in selected_operating_systems
                    )
                ):
                    effective.update(values)
            command = effective.get('command')
            url = effective.get('url')
            has_command = isinstance(command, str) and bool(command)
            has_url = isinstance(url, str) and bool(url)
            if has_command == has_url:
                raise PolicyError('project MCP configuration is invalid')
            checks = _effective_readiness_checks(
                raw_server,
                effective,
                harness=harness,
                enabled_harnesses=harnesses,
                label='project MCP configuration',
            )
            if checks is not None:
                servers.append({
                    'id': raw_server.get('id'),
                    'readiness': {'checks': checks},
                })
    return servers


def _minimum_satisfied(installed: str, minimum: str) -> bool:
    installed_parts = parse_version(installed)
    minimum_parts = parse_version(minimum)
    width = max(len(installed_parts), len(minimum_parts))
    return installed_parts + (0,) * (width - len(installed_parts)) >= (
        minimum_parts + (0,) * (width - len(minimum_parts))
    )


def _mcp_check_finding(
    server_name: str,
    check: dict[str, Any],
    project_root: Path,
) -> Finding | None:
    kind = check.get('kind')
    allowed = _MCP_CHECK_FIELDS.get(kind)
    if allowed is None or set(check) - allowed:
        raise PolicyError('unsupported MCP readiness check')
    if kind == 'command-exists':
        command = check.get('command')
        if not isinstance(command, str) or not command:
            raise PolicyError('MCP command-exists check is invalid')
        if shutil.which(command) is None:
            return Finding(
                'mcp-prerequisite-missing',
                f'{server_name} MCP',
                f'requires the {command} command, which is unavailable',
                f'Install {command} and expose it on PATH.',
            )
        return None
    if kind == 'runtime-version':
        runtime = check.get('runtime')
        minimum = check.get('minimum')
        if runtime not in _RUNTIME_PROBES or not isinstance(minimum, str):
            raise PolicyError('MCP runtime-version check is invalid')
        command, pattern = _RUNTIME_PROBES[runtime]
        try:
            installed = run_detector({
                'kind': 'command-regex',
                'command': list(command),
                'pattern': pattern,
            })
        except (PolicyError, re.error) as error:
            raise DetectorError('MCP runtime version detection failed') from error
        if installed is None:
            return Finding(
                'mcp-prerequisite-missing',
                f'{server_name} MCP',
                f'requires the {runtime} runtime, which is unavailable',
                f'Install {runtime} {minimum} or newer and expose it on PATH.',
            )
        try:
            satisfied = _minimum_satisfied(installed, minimum)
        except ValueError as error:
            raise DetectorError('MCP runtime version is unreadable') from error
        if not satisfied:
            return Finding(
                'mcp-version-too-old',
                f'{server_name} MCP',
                f'requires {runtime} {minimum} or newer; installed version is {installed}',
                f'Upgrade {runtime} to {minimum} or newer.',
            )
        return None
    if kind == 'workspace-path':
        raw_path = check.get('path')
        executable = check.get('executable', False)
        if (
            not isinstance(raw_path, str)
            or not raw_path
            or '\\' in raw_path
            or Path(raw_path).is_absolute()
            or '..' in Path(raw_path).parts
            or type(executable) is not bool
        ):
            raise PolicyError('MCP workspace-path check is invalid')
        path = project_root.joinpath(*Path(raw_path).parts)
        available = path.is_file() and (
            not executable or os.name == 'nt' or os.access(path, os.X_OK)
        )
        if not available:
            return Finding(
                'mcp-prerequisite-missing',
                f'{server_name} MCP',
                f'requires the project file {raw_path}, which is unavailable',
                f'Install or restore {raw_path} for this project.',
            )
        return None
    if kind == 'environment-variable':
        name = check.get('name')
        if not isinstance(name, str) or re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', name) is None:
            raise PolicyError('MCP environment-variable check is invalid')
        if name not in os.environ:
            return Finding(
                'mcp-prerequisite-missing',
                f'{server_name} MCP',
                f'requires the {name} environment variable, which is unset',
                f'Set {name} in the host environment without committing its value.',
            )
        return None
    raise PolicyError('unsupported MCP readiness check')


def check_mcp_readiness(
    harness: str,
    project_root: Path,
    registry_path: Path | None = None,
) -> list[Finding]:
    registry_path = registry_path or default_mcp_registry_path()
    findings: list[Finding] = []
    try:
        servers = [
            *_mcp_servers_from_registry(registry_path, harness),
            *_mcp_servers_from_project(project_root, harness),
        ]
    except (PolicyError, DetectorError):
        findings.append(Finding(
            'detector-error',
            'MCP readiness',
            'static readiness detection failed',
            'Review the MCP declaration and retry explicitly.',
        ))
        return findings
    for server in servers:
        server_id = server.get('id')
        readiness = server.get('readiness', {'checks': []})
        if (
            not isinstance(server_id, str)
            or re.fullmatch(r'[a-z0-9][a-z0-9-]*', server_id) is None
            or not isinstance(readiness, dict)
            or set(readiness) != {'checks'}
            or not isinstance(readiness.get('checks'), list)
        ):
            findings.append(Finding(
                'detector-error',
                'MCP readiness',
                'static readiness detection failed',
                'Review the MCP declaration and retry explicitly.',
            ))
            continue
        for raw_check in readiness['checks']:
            try:
                if not isinstance(raw_check, dict):
                    raise PolicyError('MCP readiness declaration is invalid')
                finding = _mcp_check_finding(server_id, raw_check, project_root)
            except (PolicyError, DetectorError, re.error):
                findings.append(Finding(
                    'detector-error',
                    f'{server_id} MCP',
                    'static readiness detection failed',
                    'Review the MCP declaration and retry explicitly.',
                ))
                continue
            if finding is not None:
                findings.append(finding)
    return findings


def load_policy(path: Path, harness: str | None = None) -> dict[str, Any]:
    try:
        policy = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PolicyError('unable to load recommended-tool policy') from error
    if not isinstance(policy, dict):
        raise PolicyError('recommended-tool policy must contain an object')
    if harness is not None and policy.get('harness') != harness:
        raise PolicyError('recommended-tool policy harness does not match invocation')
    return policy


def default_policy_path(harness: str) -> Path:
    runtime_root = Path(__file__).resolve().parents[1]
    for ancestor in runtime_root.parents:
        plugin_policy = ancestor / 'policies' / 'recommended-tools' / f'{harness}.json'
        if plugin_policy.is_file():
            return plugin_policy
    raise PolicyError('recommended-tool policy is unavailable')


def default_cache_root() -> Path:
    local_app_data = os.environ.get('LOCALAPPDATA')
    if os.name == 'nt' and local_app_data:
        return Path(local_app_data) / 'smartkit'
    xdg_cache = os.environ.get('XDG_CACHE_HOME')
    if xdg_cache:
        return Path(xdg_cache) / 'smartkit'
    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Caches' / 'smartkit'
    return Path.home() / '.cache' / 'smartkit'


def _project_cache_key(project_root: Path) -> str:
    resolved = project_root.resolve()
    normalized = os.path.normcase(str(resolved))
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def _load_state(
    path: Path,
    date: str,
) -> str | None:
    try:
        state = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(state, dict):
        return None
    if state.get('date') != date:
        return None
    outcome = state.get('outcome')
    if outcome in {'started', 'passed', 'notified', 'error'} and set(state) == {
        'date',
        'outcome',
    }:
        return outcome
    return None


def _write_state(
    path: Path,
    date: str,
    outcome: str,
) -> None:
    if outcome not in {'started', 'passed', 'notified', 'error'}:
        raise ValueError('daily state outcome is invalid')
    state: dict[str, Any] = {
        'date': date,
        'outcome': outcome,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            json.dump(state, output)
            output.write('\n')
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _acquire_lock(path: Path) -> str:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return 'uncached'
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        try:
            if time.time() - path.stat().st_mtime <= _LOCK_STALE_SECONDS:
                return 'busy'
            path.unlink()
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except (FileNotFoundError, FileExistsError):
            return 'busy'
        except OSError:
            return 'uncached'
    except OSError:
        return 'uncached'
    try:
        os.write(descriptor, str(os.getpid()).encode('ascii'))
    finally:
        os.close(descriptor)
    return 'owned'


def run_hook(
    harness: str,
    policy_path: Path,
    cache_root: Path | None = None,
    now: datetime | None = None,
    *,
    project_root: Path | None = None,
    mcp_registry_path: Path | None = None,
    force: bool = False,
    evaluator: Callable[[dict[str, Any]], list[Finding]] | None = None,
) -> HookResult:
    cache_root = cache_root or default_cache_root()
    now = now or datetime.now().astimezone()
    project_root = resolve_project_root(project_root)
    project_cache = cache_root / _project_cache_key(project_root)
    state_path = project_cache / f'{harness}.json'
    lock_path = project_cache / f'{harness}.lock'
    try:
        date = now.date().isoformat()
        if not force and _load_state(state_path, date):
            return HookResult(False)
        lock_status = _acquire_lock(lock_path)
        if lock_status == 'busy':
            return HookResult(False)
        if lock_status == 'uncached' and not force:
            return HookResult(False, internal_error=True)
        try:
            if not force and _load_state(state_path, date):
                return HookResult(False)
            if not force:
                try:
                    _write_state(state_path, date, 'started')
                except OSError:
                    return HookResult(False, internal_error=True)
            policy = load_policy(policy_path, harness)
            if evaluator is not None:
                findings_list = evaluator(policy)
            else:
                policy_findings = check_policy(policy)
                findings_list = [
                    *policy_findings,
                    *check_config_requirements(
                        policy,
                        project_root,
                    ),
                    *check_mcp_readiness(harness, project_root, mcp_registry_path),
                ]
            findings = tuple(findings_list)
            if not findings:
                try:
                    _write_state(state_path, date, 'passed')
                except OSError:
                    pass
            elif any(finding.code != 'detector-error' for finding in findings):
                try:
                    _write_state(state_path, date, 'notified')
                except OSError:
                    pass
            else:
                try:
                    _write_state(state_path, date, 'error')
                except OSError:
                    pass
            return HookResult(True, findings)
        except Exception:
            try:
                _write_state(state_path, date, 'error')
            except OSError:
                pass
            return HookResult(True, internal_error=True)
        finally:
            if lock_status == 'owned':
                try:
                    lock_path.unlink()
                except OSError:
                    pass
    except Exception:
        return HookResult(True, internal_error=True)


def render_findings(findings: list[Finding] | tuple[Finding, ...]) -> str:
    return '\n'.join(
        f'[smartkit] {finding.tool}: {finding.message}. {finding.guidance}'
        for finding in findings
    )


def _user_consent_request(findings: str) -> str:
    return (
        f'{findings}\n'
        '[smartkit] Recommended readiness changes require approval. Reply with the '
        'names whose requested actions you approve, or decline those actions, before '
        'continuing.'
    )


def _agent_consent_request(
    findings: str,
    actionable_findings: tuple[Finding, ...],
    harness: str,
) -> str:
    maintenance_runner = Path(__file__).resolve().with_name(
        'maintain_recommended_tools.py'
    )
    plugin_fallback = (
        ' If the runner reports that manual action is required and the named tool is a '
        'Codex plugin, use an available Codex plugin-management tool for that plugin. If '
        'no such tool is available, tell the user to complete the action in the Codex '
        'Plugins interface.'
        if harness == 'codex'
        else ''
    )
    approved_actions = []
    for finding in actionable_findings:
        if finding.target_kind == 'tool':
            approved_actions.append(
                f'apply --harness {harness} --tool {finding.target_id} '
                f'--action {finding.action} --approved'
            )
        elif finding.target_kind == 'setting':
            approved_actions.append(
                f'configure --harness {harness} --setting {finding.target_id} '
                '--approved'
            )
    action_text = '; '.join(approved_actions)
    runner_instruction = (
        'After a subsequent user message grants consent, invoke the bundled internal '
        f'maintenance runner at {maintenance_runner}. Treat each semicolon-separated '
        'entry as a separate action and invoke only the entries the user approved: '
        f'{action_text}. '
        if action_text
        else ''
    )
    return (
        f'{findings}\n'
        '[smartkit] If the user explicitly declines all listed readiness actions, do not ask '
        'again or run maintenance; continue the original task. Otherwise, stop the current '
        'task now. Tell the user which tools or settings need a change and ask whether '
        'they consent to those actions. Do '
        'not show the underlying maintenance commands. Do not mutate tools or '
        'configuration before the user consents. End this turn after requesting consent '
        'and wait for the next user message. If the runner reports manual action required, '
        'relay its guidance, ask the user to complete that action in the current session, '
        'and wait for confirmation without claiming completion. '
        f'{runner_instruction}This runner is plugin '
        f'Hook support, not an exposed Skill.{plugin_fallback}'
    )


def render_hook_result(
    result: HookResult,
    harness: str,
    *,
    delivery: str = 'native',
) -> str:
    findings = render_findings(result.findings)
    rendered = findings
    if result.requires_user_prompt:
        if harness in {'codex', 'qoder'}:
            return json.dumps(
                {
                    'continue': True,
                    'systemMessage': _user_consent_request(rendered),
                    'hookSpecificOutput': {
                        'hookEventName': 'SessionStart',
                        'additionalContext': _agent_consent_request(
                            rendered, result.findings, harness
                        ),
                    },
                }
            )
        if harness == 'cursor':
            if delivery == 'context':
                return json.dumps(
                    {
                        'additional_context': _agent_consent_request(
                            rendered, result.findings, harness
                        )
                    }
                )
            return json.dumps(
                {
                    'continue': False,
                    'user_message': _user_consent_request(rendered),
                }
            )
        return json.dumps(
            {
                'additionalContext': _agent_consent_request(
                    rendered, result.findings, harness
                )
            }
        )
    if result.internal_error:
        message = '[smartkit] Recommended-tool check could not complete; continuing.'
    else:
        message = rendered
    if not message:
        return ''
    if harness in {'codex', 'qoder'}:
        return json.dumps({'continue': True, 'systemMessage': message})
    if harness == 'cursor':
        if delivery == 'context':
            return json.dumps({'additional_context': message})
        return json.dumps({'continue': True})
    return json.dumps({'additionalContext': message})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    for command in ('check', 'hook'):
        child = subparsers.add_parser(command)
        child.add_argument('--harness', required=True, choices=('codex', 'cursor', 'copilot', 'qoder'))
        child.add_argument('--policy', type=Path)
        if command == 'hook':
            child.add_argument('--force', action='store_true')
            child.add_argument(
                '--delivery',
                choices=('native', 'context'),
                default='native',
            )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    policy_path = args.policy or default_policy_path(args.harness)
    if args.command == 'hook':
        result = run_hook(
            args.harness,
            policy_path,
            force=args.force,
        )
        output = render_hook_result(
            result,
            args.harness,
            delivery=args.delivery,
        )
        if output:
            print(output)
        return 0
    try:
        findings = check_policy(load_policy(policy_path, args.harness))
    except Exception:
        print('[smartkit] Recommended-tool check could not complete.', file=sys.stderr)
        return 2
    output = render_findings(findings)
    if output:
        print(output)
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
