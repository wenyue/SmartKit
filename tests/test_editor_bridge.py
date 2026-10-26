"""Exercise the optional editor bridge without opening or modifying the real editor."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_web import editor_bridge


class EditorBridgeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        patcher = patch.object(editor_bridge, "state_dir", return_value=self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.repo = self.root / "repo 中文"
        self.after = self.repo / "a.dart"
        self.token = "a" * 64

    def advertise(self, port, **extra):
        (self.root / "vscode-bridge.json").write_text(
            json.dumps(dict(protocol=1, port=port, token=self.token, **extra)), encoding="utf-8")

    def serve(self, result, status=200):
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_POST(self):
                owner.received = (self.path, self.headers.get("Authorization"),
                    json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                if result is None:
                    self.connection.shutdown(2)
                    self.connection.close()
                    return
                self.send_response(status)
                self.end_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.advertise(server.server_port)

    def test_missing_bridge_declines_without_creating_state(self):
        self.assertFalse(editor_bridge.open_registered_diff(self.repo, "git:/base", self.after))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_registered_window_confirms_the_actual_open(self):
        self.serve({"status": "opened"})
        self.assertTrue(editor_bridge.open_registered_diff(self.repo, "git:/base", self.after))
        self.assertEqual(self.received, ("/diff", "Bearer " + self.token, {
            "repo": self.repo.as_uri(), "before": "git:/base", "after": self.after.as_uri(),
        }))

    def test_window_can_explicitly_decline_without_opening(self):
        self.serve({"status": "fallback"})
        self.assertFalse(editor_bridge.open_registered_diff(self.repo, "git:/base", self.after))

    def test_lost_reply_is_not_a_safe_editor_retry(self):
        self.serve(None)
        with self.assertRaisesRegex(OSError, "result is unknown"):
            editor_bridge.open_registered_diff(self.repo, "git:/base", self.after)

    def test_failed_editor_and_unknown_responses_are_not_safe_retries(self):
        for result, status in [({"status": "failed"}, 500), ({"status": "future-result"}, 200)]:
            with self.subTest(result=result):
                self.serve(result, status)
                with self.assertRaises(ValueError):
                    editor_bridge.open_registered_diff(self.repo, "git:/base", self.after)

    def test_malformed_descriptor_is_not_contacted(self):
        for protocol, port in [(1, True), (True, 12345), (2, 12345)]:
            with self.subTest(protocol=protocol, port=port):
                (self.root / "vscode-bridge.json").write_text(
                    json.dumps({"protocol": protocol, "port": port, "token": self.token}), encoding="utf-8")
                with patch.object(editor_bridge.http.client, "HTTPConnection") as connection:
                    self.assertFalse(editor_bridge.open_registered_diff(self.repo, "git:/base", self.after))
                connection.assert_not_called()

    def test_unreadable_or_invalid_discovery_does_not_send_a_request(self):
        for failure in [PermissionError("descriptor unavailable"), ValueError("invalid descriptor")]:
            with self.subTest(failure=failure), patch.object(editor_bridge, "read_json", side_effect=failure):
                self.assertFalse(editor_bridge.open_registered_diff(self.repo, "git:/base", self.after))

    def test_closed_listener_is_not_a_sent_editor_request(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
        port = server.server_port
        server.server_close()
        self.advertise(port)
        self.assertFalse(editor_bridge.open_registered_diff(self.repo, "git:/base", self.after))

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for the VS Code bridge tests")
    def test_window_side_contract(self):
        result = subprocess.run(
            [shutil.which("node"), "--test", str(ROOT / "tests/test_vscode_diff_bridge.cjs")],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
