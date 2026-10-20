from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Mapping
from pathlib import Path, PurePosixPath

from project_state.catalog import (
    _SEMVER,
    _fields,
    _harnesses,
    _load_json,
    _name,
    _nonempty_string,
    _object,
    _required,
    safe_field_key,
    safe_relative,
)
from project_state.models import Catalog, ContractError, Harness
from project_state.sources import ExternalContractError, validate_ref

from .models import (
    CodexAgentConfig,
    CopilotAgentConfig,
    CursorAgentConfig,
    ExternalSourceSpec,
    ExternalSkillSpec,
    McpOverride,
    McpReadiness,
    McpServerSpec,
    McpTransport,
    OperatingSystem,
    ProjectAgentSpec,
    ProjectConfig,
    QoderAgentConfig,
    NativeAgentConfig,
    MaintenanceConfig,
    DesiredField,
)


_GITHUB_SOURCE = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
_PROJECT_CONFIG_FIELDS = frozenset({'$schema', 'skills', 'mcp', 'agents', 'setupVersion', 'maintenance', 'settings'})
_EXTERNAL_SOURCE_FIELDS = frozenset({'source', 'ref', 'include'})
_MCP_SERVER_FIELDS = frozenset({
    'id', 'harnesses', 'command', 'args', 'cwd', 'env', 'url', 'overrides',
    'readiness',
})
_MCP_OVERRIDE_FIELDS = frozenset({'when', 'set'})
_MCP_OVERRIDE_SELECTOR_FIELDS = frozenset({'harnesses', 'operatingSystems'})
_MCP_OVERRIDE_VALUE_FIELDS = frozenset({'command', 'args', 'cwd', 'env', 'url'})
_MCP_READINESS_FIELDS = frozenset({'harnesses', 'operatingSystems', 'checks'})
_PROJECT_AGENT_FIELDS = frozenset({'id', 'source', 'description', 'harnesses'})
_PROJECT_AGENT_HARNESS_FIELDS = frozenset({'codex', 'cursor', 'copilot', 'qoder'})
_CODEX_AGENT_FIELDS = frozenset({'model', 'model_reasoning_effort', 'sandbox_mode'})
_CURSOR_AGENT_FIELDS = frozenset({'model', 'readonly'})
_COPILOT_AGENT_FIELDS = frozenset({'model', 'disable_model_invocation'})
_QODER_AGENT_FIELDS = frozenset({'model'})
_ENVIRONMENT_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_RUNTIME_VERSION = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$')


def _string_array(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ContractError(f'{label} must be an array of non-empty strings')
    return tuple(value)


def _mcp_text(value: object, label: str) -> str:
    text = _nonempty_string(value, label)
    if any(unicodedata.category(character) == 'Cc' for character in text):
        raise ContractError(f'{label} contains control characters')
    return text


def _mcp_env(value: object, label: str) -> tuple[str, ...]:
    names = _string_array(value, label)
    if len(names) != len(set(names)):
        raise ContractError(f'{label} has duplicate values')
    if any(_ENVIRONMENT_NAME.fullmatch(name) is None for name in names):
        raise ContractError(f'{label} contains an invalid environment variable name')
    return names


def _mcp_override(
    value: object,
    *,
    label: str,
    transport: McpTransport,
    enabled_harnesses: tuple[Harness, ...],
) -> McpOverride:
    document = _object(value, label)
    _fields(document, _MCP_OVERRIDE_FIELDS, label)
    selector = _object(_required(document, 'when', label), f'{label}.when')
    _fields(selector, _MCP_OVERRIDE_SELECTOR_FIELDS, f'{label}.when')
    if not selector:
        raise ContractError(f'{label}.when must select harnesses or operatingSystems')
    harnesses = None
    if 'harnesses' in selector:
        harnesses = _harnesses(selector['harnesses'], f'{label}.when.harnesses', ())
        if not harnesses:
            raise ContractError(f'{label}.when.harnesses must not be empty')
        if set(harnesses) - set(enabled_harnesses):
            raise ContractError(
                f'{label}.when.harnesses includes a harness not enabled by the server'
            )
    operating_systems = None
    if 'operatingSystems' in selector:
        operating_systems = _operating_systems(
            selector['operatingSystems'], f'{label}.when.operatingSystems'
        )

    values = _object(_required(document, 'set', label), f'{label}.set')
    _fields(values, _MCP_OVERRIDE_VALUE_FIELDS, f'{label}.set')
    if not values:
        raise ContractError(f'{label}.set must override at least one field')
    if transport is McpTransport.HTTP:
        if set(values) - {'url'}:
            raise ContractError(f'{label} HTTP override may declare only url')
    elif 'url' in values:
        raise ContractError(f'{label} stdio override cannot declare url')
    command = _mcp_text(values['command'], f'{label}.set.command') if 'command' in values else None
    args = _string_array(values['args'], f'{label}.set.args') if 'args' in values else None
    cwd = _mcp_text(values['cwd'], f'{label}.set.cwd') if 'cwd' in values else None
    env = _mcp_env(values['env'], f'{label}.set.env') if 'env' in values else None
    url = _mcp_text(values['url'], f'{label}.set.url') if 'url' in values else None
    if url is not None and not url.startswith(('https://', 'http://')):
        raise ContractError(f'{label}.set.url must be an HTTP URL')
    return McpOverride(harnesses, operating_systems, command, args, cwd, env, url)


def _mcp_readiness_check(value: object, label: str) -> Mapping[str, object]:
    check = _object(value, label)
    kind = check.get('kind')
    if kind == 'command-exists':
        _fields(check, frozenset({'kind', 'command'}), label)
        return {
            'kind': kind,
            'command': _mcp_text(_required(check, 'command', label), f'{label}.command'),
        }
    if kind == 'runtime-version':
        _fields(check, frozenset({'kind', 'runtime', 'minimum'}), label)
        if _required(check, 'runtime', label) != 'node':
            raise ContractError(f'{label}.runtime is unsupported')
        minimum = _mcp_text(_required(check, 'minimum', label), f'{label}.minimum')
        if _RUNTIME_VERSION.fullmatch(minimum) is None:
            raise ContractError(f'{label}.minimum must be a numeric version')
        return {'kind': kind, 'runtime': 'node', 'minimum': minimum}
    if kind == 'workspace-path':
        _fields(check, frozenset({'kind', 'path', 'executable'}), label)
        path = safe_relative(
            _mcp_text(_required(check, 'path', label), f'{label}.path'),
            f'{label}.path',
        )
        executable = check.get('executable', False)
        if type(executable) is not bool:
            raise ContractError(f'{label}.executable must be a boolean')
        return {
            'kind': kind,
            'path': path.as_posix(),
            **({'executable': True} if executable else {}),
        }
    if kind == 'environment-variable':
        _fields(check, frozenset({'kind', 'name'}), label)
        name = _mcp_text(_required(check, 'name', label), f'{label}.name')
        if _ENVIRONMENT_NAME.fullmatch(name) is None:
            raise ContractError(f'{label}.name is invalid')
        return {'kind': kind, 'name': name}
    raise ContractError(f'{label}.kind is unsupported')


def _mcp_readiness(
    value: object,
    *,
    label: str,
    enabled_harnesses: tuple[Harness, ...],
) -> McpReadiness:
    document = _object(value, label)
    _fields(document, _MCP_READINESS_FIELDS, label)
    harnesses = None
    if 'harnesses' in document:
        harnesses = _harnesses(document['harnesses'], f'{label}.harnesses', ())
        if not harnesses:
            raise ContractError(f'{label}.harnesses must not be empty')
        if set(harnesses) - set(enabled_harnesses):
            raise ContractError(
                f'{label}.harnesses includes a harness not enabled by the server'
            )
    operating_systems = (
        _operating_systems(document['operatingSystems'], f'{label}.operatingSystems')
        if 'operatingSystems' in document else None
    )
    raw_checks = document.get('checks')
    if raw_checks is not None and not isinstance(raw_checks, list):
        raise ContractError(f'{label}.checks must be an array')
    checks = (
        tuple(
            _mcp_readiness_check(check, f'{label}.checks[{index}]')
            for index, check in enumerate(raw_checks)
        )
        if raw_checks is not None else None
    )
    return McpReadiness(harnesses, operating_systems, checks)


def parse_mcp_servers(value: object) -> tuple[McpServerSpec, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ContractError('project config mcp must be an array')
    raw_servers = value
    result: list[McpServerSpec] = []
    for index, raw_server in enumerate(raw_servers):
        label = f'project config mcp[{index}]'
        document = _object(raw_server, label)
        _fields(document, _MCP_SERVER_FIELDS, label)
        server_id = _name(_required(document, 'id', label), f'{label}.id')
        harnesses = _harnesses(document.get('harnesses'), f'{label}.harnesses', tuple(Harness))
        if not harnesses:
            raise ContractError(f'{label}.harnesses must not be empty')
        has_command = 'command' in document
        has_url = 'url' in document
        if has_command == has_url:
            raise ContractError(f'{label} requires exactly one of command or url')
        transport = McpTransport.STDIO if has_command else McpTransport.HTTP
        command = args = cwd = env = url = None
        if transport is McpTransport.STDIO:
            if 'url' in document:
                raise ContractError(f'{label} stdio server cannot declare url')
            command = _mcp_text(_required(document, 'command', label), f'{label}.command')
            args = _string_array(document.get('args', []), f'{label}.args')
            cwd = _mcp_text(document['cwd'], f'{label}.cwd') if 'cwd' in document else None
            env = _mcp_env(document.get('env', []), f'{label}.env')
        else:
            if set(document).intersection({'command', 'args', 'cwd', 'env'}):
                raise ContractError(f'{label} HTTP server cannot declare stdio fields')
            url = _mcp_text(_required(document, 'url', label), f'{label}.url')
            if not url.startswith(('https://', 'http://')):
                raise ContractError(f'{label}.url must be an HTTP URL')
        raw_overrides = document.get('overrides', [])
        if not isinstance(raw_overrides, list):
            raise ContractError(f'{label}.overrides must be an array')
        overrides = tuple(
            _mcp_override(
                raw_override,
                label=f'{label}.overrides[{override_index}]',
                transport=transport,
                enabled_harnesses=harnesses,
            )
            for override_index, raw_override in enumerate(raw_overrides)
        )
        readiness = (
            _mcp_readiness(
                document['readiness'],
                label=f'{label}.readiness',
                enabled_harnesses=harnesses,
            )
            if 'readiness' in document else None
        )
        result.append(McpServerSpec(
            server_id,
            transport,
            harnesses,
            command=command,
            args=args or (),
            cwd=cwd,
            env=env or (),
            url=url,
            overrides=overrides,
            readiness=readiness,
        ))
    ids = [server.id for server in result]
    if len(ids) != len(set(ids)):
        raise ContractError('project config mcp has duplicate ids')
    return tuple(result)


def _operating_systems(value: object, label: str) -> tuple[OperatingSystem, ...]:
    if not isinstance(value, list):
        raise ContractError(f'{label} must be an array')
    result: list[OperatingSystem] = []
    for item in value:
        try:
            operating_system = OperatingSystem(item)
        except (TypeError, ValueError) as error:
            raise ContractError(f'{label} has an unsupported operating system') from error
        if operating_system in result:
            raise ContractError(f'{label} has duplicate operating systems')
        result.append(operating_system)
    if not result:
        raise ContractError(f'{label} must not be empty')
    return tuple(result)


def _selected(value: object, label: str, catalog: Catalog, kind: str) -> tuple[str, ...]:
    available = {
        asset.id
        for asset in catalog.assets
        if asset.kind == kind and not asset.control_plane
    }
    if value is None:
        return tuple(
            asset.id
            for asset in catalog.assets
            if asset.kind == kind and not asset.control_plane
        )
    if not isinstance(value, list):
        raise ContractError(f'{label} must be an array')
    selected = tuple(_name(item, label) for item in value)
    if len(set(selected)) != len(selected):
        raise ContractError(f'{label} has duplicate ids')
    if set(selected) - available:
        raise ContractError(f'{label} contains unknown ids')
    return selected


def parse_external_skills(value: object, catalog: Catalog) -> tuple[ExternalSourceSpec, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ContractError('project config skills must be an array')
    external = value
    reserved = {asset.id for asset in catalog.assets if asset.kind == 'skill'}
    result: list[ExternalSourceSpec] = []
    for index, item in enumerate(external):
        document = _object(item, f'project config skills[{index}]')
        _fields(document, _EXTERNAL_SOURCE_FIELDS, 'external source')
        source_id = _nonempty_string(
            _required(document, 'source', 'external source'), 'external source source'
        )
        if _GITHUB_SOURCE.fullmatch(source_id) is None:
            raise ContractError('external source must use owner/repository form')
        url = f'https://github.com/{source_id}'
        ref_value = document.get('ref')
        ref = None if ref_value is None else _nonempty_string(ref_value, 'external source ref')
        try:
            validate_ref(ref)
        except ExternalContractError as error:
            raise ContractError('external source ref must be a safe Git argument') from error
        source_skills: list[ExternalSkillSpec] = []
        raw_skills = document.get('include')
        if not isinstance(raw_skills, list) or not raw_skills:
            raise ContractError('external source include must be a non-empty array')
        if not all(isinstance(item, str) for item in raw_skills):
            raise ContractError('external source include must contain paths')
        if len(raw_skills) != len(set(raw_skills)):
            raise ContractError('external source include has duplicate paths')
        owner = source_id.split('/', 1)[0]
        for raw_skill in raw_skills:
            path = safe_relative(raw_skill, 'external skill path')
            name = _name(path.name, 'external skill path basename')
            if name in reserved:
                raise ContractError(f'external skill conflicts with shared skill: {name}')
            skill_id = f'{owner}/{name}'
            source_skills.append(ExternalSkillSpec(skill_id, name, path))
        result.append(ExternalSourceSpec(source_id, url, ref, tuple(source_skills)))
    source_ids = [source.id.casefold() for source in result]
    if len(source_ids) != len(set(source_ids)):
        raise ContractError('project config skills has duplicate sources')
    names = [item.name for source in result for item in source.skills]
    if len(set(names)) != len(names):
        raise ContractError('project config skills has duplicate names')
    return tuple(result)


def _agent_text(value: object, label: str) -> str:
    text = _nonempty_string(value, label)
    if any(unicodedata.category(character) == 'Cc' for character in text):
        raise ContractError(f'{label} contains control characters')
    return text


def _optional_agent_text(document: Mapping[str, object], key: str, label: str) -> str | None:
    value = document.get(key)
    return None if value is None else _agent_text(value, f'{label}.{key}')


def parse_project_agents(value: object) -> tuple[ProjectAgentSpec, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ContractError('project config agents must be an array')
    result: list[ProjectAgentSpec] = []
    for index, item in enumerate(value):
        label = f'project config agents[{index}]'
        document = _object(item, label)
        _fields(document, _PROJECT_AGENT_FIELDS, label)
        agent_id = _name(_required(document, 'id', label), f'{label}.id')
        source = safe_relative(document['source'], f'{label}.source') if 'source' in document else None
        expected_source = PurePosixPath('.agents/agents') / f'{agent_id}.md'
        if source is not None and source != expected_source:
            raise ContractError(
                f'{label}.source must be .agents/agents/{agent_id}.md'
            )
        description = _agent_text(
            _required(document, 'description', label), f'{label}.description'
        )
        harnesses = _object(_required(document, 'harnesses', label), f'{label}.harnesses')
        _fields(harnesses, _PROJECT_AGENT_HARNESS_FIELDS, f'{label}.harnesses')
        if not harnesses:
            raise ContractError(f'{label}.harnesses must not be empty')

        native: dict[str, NativeAgentConfig] = {}
        structured = dict(harnesses)
        for host, value in harnesses.items():
            if isinstance(value, dict) and 'native_source' in value:
                if set(value) != {'native_source'}:
                    raise ContractError(f'{label}.{host}: native_source is exclusive with mapped settings')
                extension = 'toml' if host == 'codex' else 'md'
                path = safe_relative(value['native_source'], f'{label}.{host}.native_source')
                if path != PurePosixPath(f'.agents/agents/{agent_id}.{host}.{extension}'):
                    raise ContractError(f'{label}.{host}.native_source must use the canonical Agent path')
                native[host] = NativeAgentConfig(path)
                structured.pop(host)
        if structured and source is None:
            raise ContractError(f'{label}.source is required for mapped harness settings')
        harnesses = structured

        codex = None
        if 'codex' in harnesses:
            config = _object(harnesses['codex'], f'{label}.harnesses.codex')
            _fields(config, _CODEX_AGENT_FIELDS, f'{label}.harnesses.codex')
            codex = CodexAgentConfig(
                sandbox_mode=_agent_text(
                    _required(config, 'sandbox_mode', f'{label}.harnesses.codex'),
                    f'{label}.harnesses.codex.sandbox_mode',
                ),
                model=_optional_agent_text(config, 'model', f'{label}.harnesses.codex'),
                model_reasoning_effort=_optional_agent_text(
                    config, 'model_reasoning_effort', f'{label}.harnesses.codex'
                ),
            )

        cursor = None
        if 'cursor' in harnesses:
            config = _object(harnesses['cursor'], f'{label}.harnesses.cursor')
            _fields(config, _CURSOR_AGENT_FIELDS, f'{label}.harnesses.cursor')
            readonly = _required(config, 'readonly', f'{label}.harnesses.cursor')
            if type(readonly) is not bool:
                raise ContractError(f'{label}.harnesses.cursor.readonly must be a boolean')
            cursor = CursorAgentConfig(
                readonly=readonly,
                model=_optional_agent_text(config, 'model', f'{label}.harnesses.cursor'),
            )

        copilot = None
        if 'copilot' in harnesses:
            config = _object(harnesses['copilot'], f'{label}.harnesses.copilot')
            _fields(config, _COPILOT_AGENT_FIELDS, f'{label}.harnesses.copilot')
            disabled = _required(
                config, 'disable_model_invocation', f'{label}.harnesses.copilot'
            )
            if type(disabled) is not bool:
                raise ContractError(
                    f'{label}.harnesses.copilot.disable_model_invocation must be a boolean'
                )
            copilot = CopilotAgentConfig(
                disable_model_invocation=disabled,
                model=_optional_agent_text(config, 'model', f'{label}.harnesses.copilot'),
            )

        qoder = None
        if 'qoder' in harnesses:
            config = _object(harnesses['qoder'], f'{label}.harnesses.qoder')
            _fields(config, _QODER_AGENT_FIELDS, f'{label}.harnesses.qoder')
            qoder = QoderAgentConfig(
                model=_optional_agent_text(config, 'model', f'{label}.harnesses.qoder'),
            )

        result.append(ProjectAgentSpec(
            agent_id, source, description,
            native.get('codex', codex), native.get('cursor', cursor),
            native.get('copilot', copilot), native.get('qoder', qoder),
        ))
    ids = [agent.id for agent in result]
    if len(ids) != len(set(ids)):
        raise ContractError('project config agents has duplicate ids')
    return tuple(result)


def parse_maintenance(value: object) -> MaintenanceConfig | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ContractError('maintenance must be an object')
    if value in ({'mode': 'local'}, {'mode': 'local-only'}):
        return MaintenanceConfig(value['mode'])
    if set(value) != {'mode', 'repository', 'branch', 'entry'} or value.get('mode') != 'repository':
        raise ContractError('maintenance requires local, local-only, or a complete repository binding')
    repository, branch, entry = value['repository'], value['branch'], value['entry']
    repository_pattern = (r'(?:https://[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?'
                          r'(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*/)?'
                          r'[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?/[A-Za-z0-9][A-Za-z0-9_.-]*')
    if (not isinstance(repository, str) or not re.fullmatch(repository_pattern, repository)
            or repository.endswith('.git.git')
            or (repository.endswith('.git') and not repository.startswith('https://'))):
        raise ContractError('maintenance repository must be a GitHub owner/repo or credential-free HTTPS repository URL')
    if (not isinstance(branch, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]*', branch)
            or any(part in {'', '.', '..'} or part.startswith('.') or part.endswith('.lock') for part in branch.split('/'))
            or '..' in branch or branch.endswith('.')):
        raise ContractError('maintenance branch must be a safe branch name')
    if not isinstance(entry, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', entry):
        raise ContractError('maintenance entry must be a single project slug')
    safe_relative(entry, 'maintenance entry')
    return MaintenanceConfig('repository', repository, branch, entry)


SETTING_PATHS = frozenset({'.codex/config.toml', '.cursor/cli.json'})


def parse_project_settings(value: object) -> tuple[DesiredField, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ContractError('settings must be an array of project-native fields')
    result = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {'path', 'key', 'value'}:
            raise ContractError('setting requires path, key and value')
        if not isinstance(item['path'], str) or item['path'] not in SETTING_PATHS:
            raise ContractError('setting path must be a supported project-native configuration')
        key = safe_field_key(item['key'], 'setting key')
        if key.split('.')[0] in {'agents', 'mcp_servers', 'mcpServers'}:
            raise ContractError('Agent and MCP settings belong to their canonical declarations')
        if item['value'] is None or isinstance(item['value'], dict):
            raise ContractError('settings must declare non-null leaf values')
        try:
            json.dumps(item['value'], allow_nan=False)
        except (TypeError, ValueError) as error:
            raise ContractError('setting value must be finite JSON') from error
        path = PurePosixPath(item['path'])
        for prior in result:
            if path == prior.path and (key == prior.key or key.startswith(prior.key + '.') or prior.key.startswith(key + '.')):
                raise ContractError('settings contain overlapping keys')
        result.append(DesiredField(path, key, item['value'], 'toml' if path.suffix == '.toml' else 'json'))
    return tuple(result)


def load_project_config(
    path: Path | None,
    *,
    catalog: Catalog,
) -> ProjectConfig:
    document: Mapping[str, object]
    if path is None or not path.exists():
        document = {}
    else:
        document = _load_json(path, 'project config')
    _fields(document, _PROJECT_CONFIG_FIELDS, 'project config')
    if 'setupVersion' in document:
        setup_version = document['setupVersion']
        if not isinstance(setup_version, str) or _SEMVER.fullmatch(setup_version) is None:
            raise ContractError('project config setupVersion must be a semantic version')
    if 'maintenance' in document and document['maintenance'] is None:
        raise ContractError('maintenance must be an object when present')
    project_external_skills = parse_external_skills(document.get('skills'), catalog)
    mcp_servers = parse_mcp_servers(document.get('mcp'))
    agents = parse_project_agents(document.get('agents'))
    return ProjectConfig(
        _selected(None, 'selected_rules', catalog, 'rule'),
        _selected(None, 'selected_skills', catalog, 'skill'),
        project_external_skills,
        mcp_servers,
        agents,
        parse_maintenance(document.get('maintenance')),
        parse_project_settings(document.get('settings')),
    )
