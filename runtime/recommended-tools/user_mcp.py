"""Remove user-level MCP entries that duplicate SmartKit Plugin MCP servers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


_SOURCE_ROOT = Path(__file__).resolve().parents[2]


def plugin_server_ids(registry_path: Path, harness: str) -> list[str]:
    document = json.loads(registry_path.read_text(encoding='utf-8'))
    return [
        server['id'] for server in document['servers']
        if harness in server['harnesses']
    ]


def _load_toml(text: str) -> dict:
    try:
        import tomllib
    except ModuleNotFoundError:
        scripts = str(_SOURCE_ROOT / 'skills' / 'setup-project-agents' / 'scripts')
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        from _vendor import tomli as tomllib
    return tomllib.loads(text)


def _codex_server_ids(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    servers = _load_toml(path.read_text(encoding='utf-8')).get('mcp_servers')
    return set(servers) if isinstance(servers, dict) else set()


def _remove_from_codex(
    path: Path,
    ids: list[str],
    run: Callable[..., subprocess.CompletedProcess],
) -> list[str]:
    present = _codex_server_ids(path)
    found = [server_id for server_id in ids if server_id in present]
    if not found:
        return []
    codex = shutil.which('codex')
    if codex is None:
        raise OSError('codex command is unavailable')
    # The Codex CLI edits config.toml without discarding the user's formatting or comments.
    for server_id in found:
        run(
            [codex, 'mcp', 'remove', server_id],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    remaining = _codex_server_ids(path)
    if any(server_id in remaining for server_id in found):
        raise OSError('codex mcp remove left entries in place')
    return found


def _remove_from_json(path: Path, ids: list[str]) -> list[str]:
    if not path.is_file():
        return []
    document = json.loads(path.read_text(encoding='utf-8'))
    servers = document.get('mcpServers') if isinstance(document, dict) else None
    if not isinstance(servers, dict):
        return []
    found = [server_id for server_id in ids if server_id in servers]
    if not found:
        return []
    for server_id in found:
        del servers[server_id]
    descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            json.dump(document, output, indent=2, ensure_ascii=False)
            output.write('\n')
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    return found


def remove_duplicate_user_servers(
    harness: str,
    registry_path: Path,
    *,
    home: Path | None = None,
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> list[str]:
    """Return notices for user-level entries removed because the plugin provides them."""
    ids = plugin_server_ids(registry_path, harness)
    home = home or Path.home()
    if harness == 'codex':
        path = Path(os.environ.get('CODEX_HOME') or home / '.codex') / 'config.toml'
    elif harness == 'copilot':
        path = Path(os.environ.get('COPILOT_HOME') or home / '.copilot') / 'mcp-config.json'
    elif harness == 'cursor':
        path = home / '.cursor' / 'mcp.json'
    else:
        return []
    try:
        removed = (
            _remove_from_codex(path, ids, run)
            if harness == 'codex'
            else _remove_from_json(path, ids)
        )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return [
            f'[smartkit] Could not remove user-level MCP servers duplicated by the SmartKit '
            f'plugin ({", ".join(ids)}) from {path}: {error}. Remove them manually.'
        ]
    if not removed:
        return []
    return [
        f'[smartkit] Removed user-level MCP server(s) {", ".join(removed)} from {path}; '
        'the SmartKit plugin provides them. Start a new session to apply the change.'
    ]
