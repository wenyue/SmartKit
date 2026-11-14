"""Prepare CodeGraph installation, index, and service for an authorized full setup."""
from __future__ import annotations

import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parents[3] / 'runtime/recommended-tools'
if str(_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_RUNTIME))

from codegraph_runtime import Readiness, check, index_status, index_problem, run_command, verify_health


def _start_and_verify(target: Path, executable: str) -> None:
    messages: queue.Queue = queue.Queue()
    deadline = time.monotonic() + 30
    with subprocess.Popen(
        [executable, 'serve', '--mcp', '--path', str(target)], cwd=target,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
    ) as process:
        def collect() -> None:
            assert process.stdout is not None
            for _ in range(64):
                line = process.stdout.readline(1_048_577)
                messages.put(line)
                if not line or len(line) > 1_048_576:
                    break

        threading.Thread(target=collect, daemon=True).start()
        # Drain bounded diagnostics concurrently so a verbose startup cannot
        # deadlock before the MCP response. Keep only the tail for failures.
        diagnostics = bytearray()

        def drain() -> None:
            assert process.stderr is not None
            while True:
                chunk = process.stderr.read(1024)
                if not chunk:
                    break
                diagnostics.extend(chunk)
                del diagnostics[:-4096]

        threading.Thread(target=drain, daemon=True).start()

        class Replies:
            def readline(self, limit: int) -> bytes:
                try:
                    return messages.get(timeout=max(0, deadline - time.monotonic()))
                except queue.Empty as error:
                    raise ValueError('CodeGraph startup timed out: ' + diagnostics.decode('utf-8', errors='replace')) from error

        try:
            assert process.stdin is not None
            verify_health(Replies(), process.stdin, target)
        finally:
            if process.stdin:
                process.stdin.close()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)


def setup(target: Path, harness: str, *, approved: bool) -> Readiness:
    """Install when absent, prepare the local index, and verify a real MCP query."""
    if not approved:
        raise ValueError('CodeGraph setup requires authorization for installation, indexing and startup')
    target = target.resolve(strict=True)
    executable = shutil.which('codegraph')
    if executable is None:
        # Capture installer output so the public setup command keeps JSON stdout.
        result = run_command([
            sys.executable, str(Path(__file__).with_name('maintain_recommended_tools.py')),
            'apply', '--harness', harness, '--tool', 'codegraph', '--action', 'install', '--approved',
        ], target, 1200)
        if result.returncode:
            raise ValueError('CodeGraph installation did not complete: ' + (result.stderr or result.stdout).strip()[-1500:])
        executable = shutil.which('codegraph')
        if executable is None:
            raise ValueError('CodeGraph was installed but PATH must be refreshed before setup can continue')
    database = target / '.codegraph/codegraph.db'
    if not database.is_file():
        action = 'init'
    else:
        status = index_status(target, executable)
        index = status.get('index', {})
        if not isinstance(index, dict) or index.get('state') != 'complete' or index.get('reindexRecommended') or status.get('worktreeMismatch'):
            raise ValueError('Existing CodeGraph index needs repair or rebuilding; preserve it and resolve before continuing')
        action = 'sync' if index_problem(status) else None
    if action:
        result = run_command([executable, action, str(target)], target, 1200)
        if result.returncode:
            raise ValueError('CodeGraph ' + action + ' failed: ' + result.stderr.strip()[-1500:])
    readiness = check(target)
    if not readiness.ready:
        _start_and_verify(target, executable)
        readiness = check(target)
    if not readiness.ready:
        raise ValueError(readiness.message)
    return readiness
