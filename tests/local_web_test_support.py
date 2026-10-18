"""Run the real local host on a private test origin, including child processes."""
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


RUNTIME = Path(__file__).resolve().parents[1] / 'runtime'
sys.path.insert(0, str(RUNTIME))
import local_web
from local_web import http_server, service
from local_web.apps import comparisons


def isolate_local_web(test: unittest.TestCase, directory: Path) -> Path:
    """Patch parent modules and CLI children to use one disposable origin.

    Register server shutdown afterward so it precedes origin restoration.
    """
    with socket.socket() as candidate:
        candidate.bind((local_web.HOST, 0))
        port = candidate.getsockname()[1]
    origin = f'http://{local_web.HOST}:{port}'
    entry = directory / 'local_web_cli' / '__main__.py'
    entry.parent.mkdir()
    # Initialize the endpoint before imports; ensure/serve then relaunch this same entry.
    entry.write_text(
        'import sys\n'
        f'sys.path.insert(0, {str(RUNTIME)!r})\n'
        'import local_web\n'
        f'local_web.PORT = {port}\n'
        f'local_web.ORIGIN = {origin!r}\n'
        'from local_web import service\n'
        'service.__file__ = __file__\n'
        'from local_web.cli import main\n'
        'raise SystemExit(main())\n',
        encoding='utf-8',
    )
    for module in (local_web, http_server, service):
        patcher = patch.object(module, 'PORT', port)
        patcher.start()
        test.addCleanup(patcher.stop)
    for module in (local_web, http_server, service, comparisons):
        patcher = patch.object(module, 'ORIGIN', origin)
        patcher.start()
        test.addCleanup(patcher.stop)
    patcher = patch.object(service, '__file__', str(entry))
    patcher.start()
    test.addCleanup(patcher.stop)
    return entry
