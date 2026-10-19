from __future__ import annotations

import json
import os
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .catalog import safe_field_key
from .models import Harness, McpServerSpec, McpTransport, NativeAgentConfig, OperatingSystem, ProjectAgentSpec, ProjectConfig
from .project import ProjectError, confined_target
from .structured import (
    StructuredConfigError, field_value, format_for_path as _format_for, parse_document,
)


class RenderError(ValueError):
    """Raised when catalog assets cannot form a deterministic desired state."""


_MCP_NATIVE = {
    Harness.CODEX: (PurePosixPath('.codex/config.toml'), 'mcp_servers'),
    Harness.CURSOR: (PurePosixPath('.cursor/mcp.json'), 'mcpServers'),
    Harness.COPILOT: (PurePosixPath('.mcp.json'), 'mcpServers'),
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


@dataclass(frozen=True)
class RenderedProjectAgents:
    sources: tuple[PurePosixPath, ...]
    native_paths: tuple[PurePosixPath, ...]


def _render_project_agents(
    files: dict[PurePosixPath, bytes],
    target_root: Path,
    config: ProjectConfig,
) -> RenderedProjectAgents:
    preserved: list[PurePosixPath] = []
    native_paths: list[PurePosixPath] = []
    for agent in config.agents:
        reference = ''
        if agent.source is not None:
            _project_agent_source(target_root, agent)
            preserved.append(agent.source)
            reference = agent.source.as_posix()
        for host, native_config, destination in (
            ('codex', agent.codex, f'.codex/agents/{agent.id}.toml'),
            ('cursor', agent.cursor, f'.cursor/agents/{agent.id}.md'),
            ('copilot', agent.copilot, f'.github/agents/{agent.id}.agent.md'),
            ('qoder', agent.qoder, f'.qoder/agents/{agent.id}.md'),
        ):
            if isinstance(native_config, NativeAgentConfig):
                try:
                    content = confined_target(target_root, native_config.native_source).read_bytes()
                    if not content.decode('utf-8').strip():
                        raise RenderError(f'project Agent native source is empty: {native_config.native_source}')
                except (OSError, UnicodeDecodeError, ProjectError) as error:
                    raise RenderError(f'cannot read {host} Agent native source: {native_config.native_source}') from error
                if host == 'codex':
                    parse_document(content, 'toml')
                _copy_file(files, PurePosixPath(destination), content)
                preserved.append(native_config.native_source)
                native_paths.append(PurePosixPath(destination))
        if agent.codex is not None and not isinstance(agent.codex, NativeAgentConfig):
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
        if agent.cursor is not None and not isinstance(agent.cursor, NativeAgentConfig):
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
        if agent.copilot is not None and not isinstance(agent.copilot, NativeAgentConfig):
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
        if agent.qoder is not None and not isinstance(agent.qoder, NativeAgentConfig):
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
    return RenderedProjectAgents(tuple(preserved), tuple(native_paths))


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
    target_root: Path,
) -> dict[str, object]:
    command, args, cwd, env, url = _effective_mcp_server(
        server, harness, operating_system
    )
    if server.transport is McpTransport.HTTP:
        assert url is not None
        return {
            **({'type': 'http'} if harness not in (Harness.CODEX, Harness.QODER) else {}),
            'url': url,
            **({'tools': ['*']} if harness is Harness.COPILOT else {}),
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
        elif harness is Harness.COPILOT:
            entry['env'] = {name: '${' + name + '}' for name in env}
        else:
            entry['env'] = {name: '${env:' + name + '}' for name in env}
    if harness is Harness.COPILOT:
        # Copilot does not resolve VS Code workspace variables in portable configs.
        replacements = {
            '${workspaceFolder}': str(target_root),
            '${workspaceRoot}': str(target_root),
            '${workspaceFolderBasename}': target_root.name,
            '${workspaceRootFolderName}': target_root.name,
            '${cwd}': str(target_root),
            '${pathSeparator}': os.sep,
        }

        def resolve(value: str) -> str:
            for variable, replacement in replacements.items():
                value = value.replace(variable, replacement)
            return value

        entry['command'] = resolve(command)
        entry['args'] = [resolve(argument) for argument in args]
        if cwd is not None:
            entry['cwd'] = resolve(cwd)
        entry['tools'] = ['*']
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
            desired = _render_mcp_entry(server, harness, operating_system, target_root)
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


def _render_project_settings(
    target_root: Path, config: ProjectConfig, documents: dict[PurePosixPath, dict[str, object]],
    templates: dict[PurePosixPath, dict[str, object]],
    previous_owned_fields: frozenset[tuple[PurePosixPath, str]],
) -> None:
    """Overlay declared native leaves; unrelated host settings retain their owner."""
    for setting in config.settings:
        path, key = setting.path, setting.key
        if path not in documents:
            documents[path] = _load_structured(confined_target(target_root, path), setting.format)
        actual = _load_structured(confined_target(target_root, path), setting.format)
        present, value = field_value(actual, key)
        if present and value != setting.value and (path, key) not in previous_owned_fields:
            raise RenderError(f'Project setting conflicts with user configuration: {path}:{key}')
        _set_dotted_field(documents[path], key, setting.value)
        _set_dotted_field(templates.setdefault(path, {}), key, setting.value)
