from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from pathlib import Path, PurePosixPath

from .catalog import safe_field_key
from .models import Harness, McpServerSpec, McpTransport, OperatingSystem, ProjectAgentSpec, ProjectConfig
from .project import ProjectError, confined_target
from .structured import (
    StructuredConfigError, field_value, format_for_path as _format_for, parse_document,
)


class RenderError(ValueError):
    """Raised when catalog assets cannot form a deterministic desired state."""


_MCP_NATIVE = {
    Harness.CODEX: (PurePosixPath('.codex/config.toml'), 'mcp_servers'),
    Harness.CURSOR: (PurePosixPath('.cursor/mcp.json'), 'mcpServers'),
    Harness.COPILOT: (PurePosixPath('.vscode/mcp.json'), 'servers'),
    Harness.QODER: (PurePosixPath('.qoder/mcp.json'), 'mcpServers'),
}


def _safe_leaves(value: object, prefix: str = '') -> Iterable[tuple[str, object]]:
    if isinstance(value, dict):
        for key, child in value.items():
            dotted = f'{prefix}.{key}' if prefix else key
            yield from _safe_leaves(child, dotted)
    elif prefix:
        try:
            yield safe_field_key(prefix, 'template field'), value
        except ValueError as error:
            raise RenderError(f'unsafe template field: {prefix}') from error


def _load_structured(path: Path, format_name: str) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        value = parse_document(path.read_bytes(), format_name)
    except (OSError, StructuredConfigError) as error:
        raise RenderError(f'cannot parse existing native config: {path}') from error
    return value


def _copy_file(files: dict[PurePosixPath, bytes], path: PurePosixPath, content: bytes) -> None:
    if path in files:
        raise RenderError(f'duplicate rendered path: {path.as_posix()}')
    files[path] = content


def _quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _project_agent_source(target_root: Path, agent: ProjectAgentSpec) -> Path:
    try:
        source = confined_target(target_root, agent.source)
    except ProjectError as error:
        raise RenderError(str(error)) from error
    if not source.exists() or not source.is_file():
        raise RenderError(f'project Agent source is missing: {agent.source.as_posix()}')
    try:
        content = source.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as error:
        raise RenderError(
            f'project Agent source is not readable UTF-8: {agent.source.as_posix()}'
        ) from error
    if not content.strip():
        raise RenderError(f'project Agent source is empty: {agent.source.as_posix()}')
    return source


def _render_project_agents(
    files: dict[PurePosixPath, bytes],
    target_root: Path,
    config: ProjectConfig,
) -> tuple[PurePosixPath, ...]:
    preserved: list[PurePosixPath] = []
    for agent in config.agents:
        _project_agent_source(target_root, agent)
        preserved.append(agent.source)
        reference = agent.source.as_posix()
        if agent.codex is not None:
            target = PurePosixPath('.codex/agents') / f'{agent.id}.toml'
            if target in files:
                raise RenderError(
                    f'Project Agent id conflicts with Codex Plugin Agent default: '
                    f'{agent.id}'
                )
            lines = [
                f'name = {_quoted(agent.id)}',
                f'description = {_quoted(agent.description)}',
            ]
            if agent.codex.model is not None:
                lines.append(f'model = {_quoted(agent.codex.model)}')
            if agent.codex.model_reasoning_effort is not None:
                lines.append(
                    'model_reasoning_effort = '
                    f'{_quoted(agent.codex.model_reasoning_effort)}'
                )
            lines.extend((
                f'sandbox_mode = {_quoted(agent.codex.sandbox_mode)}',
                'developer_instructions = """',
                f'Follow `{reference}`.',
                'Keep this file thin and use the shared agent prompt as the source of truth.',
                '"""',
            ))
            _copy_file(
                files,
                target,
                ('\n'.join(lines) + '\n').encode(),
            )
        if agent.cursor is not None:
            lines = [
                '---',
                f'name: {_quoted(agent.id)}',
                f'description: {_quoted(agent.description)}',
            ]
            if agent.cursor.model is not None:
                lines.append(f'model: {_quoted(agent.cursor.model)}')
            lines.extend((
                f'readonly: {str(agent.cursor.readonly).lower()}',
                '---',
                '',
                f'Apply @{reference}',
            ))
            _copy_file(
                files,
                PurePosixPath('.cursor/agents') / f'{agent.id}.md',
                ('\n'.join(lines) + '\n').encode(),
            )
        if agent.copilot is not None:
            lines = [
                '---',
                f'name: {_quoted(agent.id)}',
                f'description: {_quoted(agent.description)}',
            ]
            if agent.copilot.model is not None:
                lines.append(f'model: {_quoted(agent.copilot.model)}')
            lines.extend((
                'disable-model-invocation: '
                f'{str(agent.copilot.disable_model_invocation).lower()}',
                '---',
                '',
                f'Apply @{reference}',
            ))
            _copy_file(
                files,
                PurePosixPath('.github/agents') / f'{agent.id}.agent.md',
                ('\n'.join(lines) + '\n').encode(),
            )
        if agent.qoder is not None:
            lines = [
                '---',
                f'name: {_quoted(agent.id)}',
                f'description: {_quoted(agent.description)}',
            ]
            if agent.qoder.model is not None:
                lines.append(f'model: {_quoted(agent.qoder.model)}')
            lines.extend((
                '---',
                '',
                f'Apply @{reference}',
            ))
            _copy_file(
                files,
                PurePosixPath('.qoder/agents') / f'{agent.id}.md',
                ('\n'.join(lines) + '\n').encode(),
            )
    return tuple(preserved)


def _remove_dotted_field(document: dict[str, object], key: str) -> bool:
    segments = key.split('.')
    current: dict[str, object] = document
    parents: list[tuple[dict[str, object], str]] = []
    for segment in segments[:-1]:
        value = current.get(segment)
        if not isinstance(value, dict):
            return False
        parents.append((current, segment))
        current = value
    leaf = segments[-1]
    if leaf not in current:
        return False
    del current[leaf]
    for parent, segment in reversed(parents):
        child = parent.get(segment)
        if isinstance(child, dict) and not child:
            del parent[segment]
        else:
            break
    return True


def _set_dotted_field(document: dict[str, object], key: str, value: object) -> None:
    segments = key.split('.')
    current = document
    for segment in segments[:-1]:
        child = current.get(segment)
        if child is None:
            child = {}
            current[segment] = child
        if not isinstance(child, dict):
            raise RenderError(f'MCP native parent field is not an object: {key}')
        current = child
    current[segments[-1]] = value


def _effective_mcp_server(
    server: McpServerSpec,
    harness: Harness,
    operating_system: OperatingSystem | None,
) -> tuple[str | None, tuple[str, ...], str | None, tuple[str, ...], str | None]:
    command, args, cwd, env, url = (
        server.command, server.args, server.cwd, server.env, server.url,
    )
    for override in server.overrides:
        if override.harnesses is not None and harness not in override.harnesses:
            continue
        if (
            override.operating_systems is not None
            and operating_system not in override.operating_systems
        ):
            continue
        command = override.command if override.command is not None else command
        args = override.args if override.args is not None else args
        cwd = override.cwd if override.cwd is not None else cwd
        env = override.env if override.env is not None else env
        url = override.url if override.url is not None else url
    return command, args, cwd, env, url


def _render_mcp_entry(
    server: McpServerSpec,
    harness: Harness,
    operating_system: OperatingSystem | None,
) -> dict[str, object]:
    command, args, cwd, env, url = _effective_mcp_server(
        server, harness, operating_system
    )
    if server.transport is McpTransport.HTTP:
        assert url is not None
        return {
            **({'type': 'http'} if harness not in (Harness.CODEX, Harness.QODER) else {}),
            'url': url,
        }
    assert command is not None
    entry: dict[str, object] = {
        **({'type': 'stdio'} if harness not in (Harness.CODEX, Harness.QODER) else {}),
        'command': command,
        'args': list(args),
    }
    if cwd is not None:
        entry['cwd'] = cwd
    if env:
        if harness is Harness.CODEX:
            entry['env_vars'] = list(env)
        else:
            entry['env'] = {name: '${env:' + name + '}' for name in env}
    return entry


def _render_project_mcp(
    target_root: Path,
    config: ProjectConfig,
    native_documents: dict[PurePosixPath, dict[str, object]],
    native_templates: dict[PurePosixPath, dict[str, object]],
    delete_paths: set[PurePosixPath],
    previous_owned_fields: frozenset[tuple[PurePosixPath, str]],
    operating_system: OperatingSystem | None,
) -> None:
    if not config.mcp_servers:
        return
    if operating_system is None and any(
        override.operating_systems is not None
        for server in config.mcp_servers
        for override in server.overrides
    ):
        if sys.platform == 'win32':
            operating_system = OperatingSystem.WINDOWS
        elif sys.platform.startswith('linux'):
            operating_system = OperatingSystem.LINUX
        else:
            raise RenderError(
                f'unsupported operating system for MCP overrides: {sys.platform}'
            )

    def native_document(path: PurePosixPath) -> dict[str, object]:
        if path in native_documents:
            return native_documents[path]
        format_name = _format_for(path)
        assert format_name is not None
        try:
            target_path = confined_target(target_root, path)
        except ProjectError as error:
            raise RenderError(str(error)) from error
        document = _load_structured(target_path, format_name)
        native_documents[path] = document
        return document

    touched_paths: set[PurePosixPath] = set()
    for server in config.mcp_servers:
        for harness in server.harnesses:
            path, root = _MCP_NATIVE[harness]
            key = f'{root}.{server.id}'
            desired = _render_mcp_entry(server, harness, operating_system)
            document = native_document(path)
            desired_fields = dict(_safe_leaves(desired, key))
            for owned_path, owned_key in previous_owned_fields:
                if owned_path == path and owned_key.startswith(key + '.'):
                    exists, current = field_value(document, owned_key)
                    if owned_key in desired_fields and (
                        not exists or current != desired_fields[owned_key]
                    ):
                        _remove_dotted_field(document, owned_key)
            for desired_key, desired_value in desired_fields.items():
                exists, current = field_value(document, desired_key)
                if exists and current != desired_value:
                    raise RenderError(
                        f'Project MCP entry conflicts with user configuration: '
                        f'{path.as_posix()}:{desired_key}'
                    )
                if not exists:
                    _set_dotted_field(document, desired_key, desired_value)
            template = native_templates.setdefault(path, {})
            _set_dotted_field(template, key, desired)
            touched_paths.add(path)

    for path in touched_paths:
        if not native_documents[path] and path not in native_templates:
            native_documents.pop(path)
            delete_paths.add(path)
        else:
            delete_paths.discard(path)

    return None
