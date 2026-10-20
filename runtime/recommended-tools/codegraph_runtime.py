"""Inspect CodeGraph installation, project index, and existing service without starting it."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import BinaryIO


@dataclass(frozen=True)
class Readiness:
    ready: bool
    message: str


def run_command(arguments: list[str], target: Path, timeout: float) -> subprocess.CompletedProcess:
    return subprocess.run(
        arguments, cwd=target, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace',
        timeout=timeout, check=False,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
    )


def index_status(target: Path, executable: str) -> dict:
    result = run_command([executable, 'status', str(target), '--json'], target, 15)
    if result.returncode:
        raise ValueError('index status failed: ' + result.stderr.strip()[-1000:])
    status = json.loads(result.stdout)
    if not isinstance(status, dict) or status.get('initialized') is not True:
        raise ValueError('project index is not initialized')
    project_path = status.get('projectPath')
    if not isinstance(project_path, str) or not project_path:
        raise ValueError('index status has no valid project path')
    if Path(project_path).resolve() != target.resolve():
        raise ValueError('index belongs to another project')
    return status


def index_problem(status: dict) -> str:
    index = status.get('index')
    if not isinstance(index, dict) or index.get('state') != 'complete':
        return 'index is incomplete; complete CodeGraph indexing'
    if index.get('reindexRecommended'):
        return 'index needs rebuilding with the installed CodeGraph version'
    if index.get('pendingRefs') != 0:
        return 'index has unresolved references; synchronize CodeGraph'
    changes = status.get('pendingChanges')
    if not isinstance(changes, dict) or any(changes.get(key) != 0 for key in ('added', 'modified', 'removed')):
        return 'index has pending changes; synchronize CodeGraph'
    if status.get('worktreeMismatch'):
        return 'index belongs to another Git worktree'
    return ''


def _rpc(reader: BinaryIO, writer: BinaryIO, identity: int, method: str, params: dict) -> dict:
    writer.write((json.dumps({'jsonrpc': '2.0', 'id': identity, 'method': method, 'params': params}) + '\n').encode())
    writer.flush()
    for _ in range(64):
        line = reader.readline(1_048_577)
        if not line or len(line) > 1_048_576:
            raise ValueError('CodeGraph closed its connection or exceeded the response limit')
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError('invalid CodeGraph response')
        if value.get('id') == identity:
            if 'error' in value or not isinstance(value.get('result'), dict):
                raise ValueError('CodeGraph request failed: ' + str(value.get('error', 'invalid result')))
            return value['result']
    raise ValueError('CodeGraph did not answer the health request')


def verify_health(reader: BinaryIO, writer: BinaryIO, target: Path) -> None:
    _rpc(reader, writer, 1, 'initialize', {
        'protocolVersion': '2024-11-05', 'capabilities': {},
        'clientInfo': {'name': 'smartkit-readiness', 'version': '1'},
        'rootUri': target.resolve().as_uri(),
    })
    writer.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
    writer.flush()
    result = _rpc(reader, writer, 2, 'tools/call', {
        'name': 'codegraph_status', 'arguments': {'projectPath': str(target.resolve())},
    })
    if result.get('isError'):
        raise ValueError('CodeGraph health tool failed')
    content = result.get('content')
    if not isinstance(content, list):
        raise ValueError('CodeGraph health response has no content')
    text = '\n'.join(str(item.get('text', '')) for item in content if isinstance(item, dict))
    if '**CodeGraph Status**' not in text:
        raise ValueError('CodeGraph returned an unexpected health response')
    for marker in ('**Auto-sync disabled:**', '**Auto-sync recovering:**', '**Pending sync:**', '**Pending resolution:**'):
        if marker in text:
            detail = next((line.strip('- ') for line in text.split(marker, 1)[1].splitlines() if line.strip()), '')
            raise ValueError('CodeGraph is responding but automatic synchronization is not ready: ' + detail[:500])


def _probe(target: Path) -> None:
    """Connect only to an existing local daemon; the parent bounds all blocking I/O."""
    record_path = target / '.codegraph/daemon.pid'
    if record_path.is_symlink() or record_path.stat().st_size > 4096:
        raise ValueError('unsafe CodeGraph daemon record')
    record = json.loads(record_path.read_text(encoding='utf-8'))
    endpoint = record.get('socketPath') if isinstance(record, dict) else None
    if not isinstance(endpoint, str):
        raise ValueError('CodeGraph daemon endpoint is missing')
    if os.name == 'nt':
        if not re.fullmatch(r'\\\\\.\\pipe\\codegraph-[0-9a-f]{16}', endpoint):
            raise ValueError('CodeGraph daemon endpoint is not a local CodeGraph pipe')
        with open(endpoint, 'r+b', buffering=0) as connection:
            _verify_daemon(connection, connection, target, record)
    else:
        import tempfile
        allowed = (target / '.codegraph/daemon.sock', Path(tempfile.gettempdir()) / Path(endpoint).name)
        if Path(endpoint) not in allowed or not re.fullmatch(r'(daemon|codegraph-[0-9a-f]{16})\.sock', Path(endpoint).name):
            raise ValueError('CodeGraph daemon endpoint is not a local CodeGraph socket')
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(4)
            connection.connect(endpoint)
            with connection.makefile('rwb', buffering=0) as stream:
                _verify_daemon(stream, stream, target, record)


def _verify_daemon(reader: BinaryIO, writer: BinaryIO, target: Path, record: dict) -> None:
    hello = json.loads(reader.readline(4097))
    pid = record.get('pid')
    if type(pid) is not int or pid <= 0 or not isinstance(hello, dict) or hello.get('pid') != pid or hello.get('protocol') != 1:
        raise ValueError('CodeGraph daemon identity does not match its record')
    verify_health(reader, writer, target)


def check(target: Path) -> Readiness:
    """Read current installation, index and live MCP health; never install or start."""
    target = target.resolve()
    executable = shutil.which('codegraph')
    if executable is None:
        return Readiness(False, 'CodeGraph is not installed or is not on PATH')
    if not (target / '.codegraph/codegraph.db').is_file():
        return Readiness(False, 'CodeGraph index is not initialized in this working tree')
    try:
        status = index_status(target, executable)
        problem = index_problem(status)
        if problem:
            return Readiness(False, problem)
        # A separate bounded process prevents an unresponsive Windows named pipe
        # from pinning a Hook thread; it only connects and cannot launch a daemon.
        result = run_command([sys.executable, str(Path(__file__).resolve()), '_probe', '--target', str(target)], target, 6)
        if result.returncode:
            return Readiness(False, 'CodeGraph is stopped or unhealthy: ' + result.stderr.strip()[-1500:])
        return Readiness(True, 'CodeGraph index is complete and its project MCP service responds')
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        return Readiness(False, 'CodeGraph readiness could not be verified: ' + str(error))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('check', '_probe'))
    parser.add_argument('--target', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.operation == '_probe':
            _probe(args.target)
            return 0
        result = check(args.target)
        print(json.dumps(asdict(result)))
        return 0 if result.ready else 1
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
