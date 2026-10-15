#!/usr/bin/env python
"""Shared per-user local HTTP service; no web request performs maintenance.

Publishers create a shared cached artifact, then explicitly publish its ID. Native OSError/ValueError failures remain failures: startup may
have left a healthy shared service running, but no URL is returned on failure.
The registry never publishes raw snapshots, manifests, or undeclared siblings.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import hmac
import json
import logging
from logging.handlers import RotatingFileHandler
import mimetypes
import os
import secrets
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Iterator, Optional
from urllib.parse import parse_qs, quote, unquote, urlsplit

# Importing from a Skill must resolve this plugin copy, not the caller's cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "artifacts"))
import artifact_cache
import web_store
import web_apps
from web_store import (RETENTION_SECONDS, artifact_dir, cache_dir, captured_file, clean_artifact_records,
                           has_unexpired_artifacts, load_artifact, prepare_cache,
                           prepare_state, public_name, read_json, record_project,
                           redirected, state_dir, write_json)
from web_apps import application_data, hook_page_links, render_application

for dependency, location in ((artifact_cache, Path(__file__).resolve().parents[1] / "artifacts/artifact_cache.py"),
                             (web_store, Path(__file__).resolve().with_name("web_store.py")),
                             (web_apps, Path(__file__).resolve().with_name("web_apps.py"))):
    if not location.is_file() or Path(dependency.__file__).resolve() != location:
        raise ImportError("shared web dependency is not from the loaded plugin: " + str(location))

# Serialized identities remain unchanged by this source-path rename.
SERVICE_SCHEMA = "smartkit.preview-service/v1"
START_TIMEOUT = 8.0
CLEANUP_INTERVAL = 60.0


def load_state() -> Optional[dict]:
    try:
        state = read_json(state_dir() / "service.json")
    except FileNotFoundError:
        return None
    if (not isinstance(state, dict) or set(state) != {"schema", "port", "key", "mode", "pid"}
            or state["schema"] != SERVICE_SCHEMA or type(state["port"]) is not int or not 0 <= state["port"] <= 65535
            or not isinstance(state["key"], str) or len(state["key"]) != 64
            or any(c not in "0123456789abcdef" for c in state["key"])
            or state["mode"] not in ("applications", "previews")
            or type(state["pid"]) is not int or state["pid"] < 0):
        raise ValueError("invalid shared web service state; preserve service.json for diagnosis")
    return state


@contextlib.contextmanager
def start_lock() -> Iterator[None]:
    path = prepare_state() / "start.lock"
    if redirected(path):
        raise ValueError("web service startup lock redirects")
    descriptor = os.open(str(path), os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, "r+b") as stream:
        deadline = time.monotonic() + START_TIMEOUT
        if os.name == "nt":
            import msvcrt
            if not path.stat().st_size:
                stream.write(b"0")
                stream.flush()
            def acquire() -> None:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            def release() -> None:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            def acquire() -> None:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            def release() -> None:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        while True:
            try:
                acquire()
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("another web service startup still holds the lock")
                time.sleep(0.05)
            except OSError as error:
                # Windows reports contention with EACCES, unlike flock's EAGAIN.
                if os.name != "nt" or error.errno != 13 or time.monotonic() >= deadline:
                    raise
                time.sleep(0.05)
        try:
            yield
        finally:
            release()


def origin(state: dict) -> str:
    return "http://127.0.0.1:" + str(state["port"])


def service_info(state: dict) -> dict:
    return {"origin": origin(state), "pid": state["pid"], "mode": state["mode"],
            "apps": {feature: origin(state) + "/apps/" + feature + "/?key=" + state["key"]
                     for feature in ("readiness", "setup")}}


def health(state: dict) -> Optional[dict]:
    if not state["port"]:
        return None
    request = urllib.request.Request(origin(state) + "/api/service/health",
                                     headers={"Authorization": "Bearer " + state["key"]})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=0.4) as response:
            value = json.loads(response.read(8192).decode("utf-8"))
        if (isinstance(value, dict) and value.get("schema") == SERVICE_SCHEMA
                and type(value.get("pid")) is int and value["pid"] > 0
                and value.get("mode") in ("applications", "previews")):
            return value
    except (OSError, ValueError):
        return None
    return None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        if os.name == "nt":
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            return False
        return True


def ensure_service(mode: str = "applications") -> dict:
    """Reuse a verified live server or start one on an OS-assigned free port.

    Saved addresses discover a live instance; each new process gets a new port
    allocation and private credential. Old URLs may stop working after restart.
    Invalid state and startup failures propagate native failures; an occupied
    last-known port never prevents a new start or authorizes stopping its owner.
    Applications mode is permanent; preview-only callers never downgrade it.
    """
    if mode not in ("applications", "previews"):
        raise ValueError("unknown web service mode")
    with start_lock():
        prepare_cache()
        artifact_dir()
        cleanup_artifacts()
        state = load_state()
        if state is None:
            state = {"schema": SERVICE_SCHEMA, "port": 0, "key": secrets.token_hex(32), "mode": mode, "pid": 0}
        running = health(state)
        if running and running.get("artifact_cache_schema") == artifact_cache.SCHEMA:
            state["pid"] = running["pid"]
            if mode == "applications":
                state["mode"] = mode
            write_json(state_dir() / "service.json", state)
            if running["mode"] != state["mode"]:
                deadline = time.monotonic() + START_TIMEOUT
                while time.monotonic() < deadline:
                    observed = health(state)
                    if observed and observed["pid"] == state["pid"] and observed["mode"] == state["mode"]:
                        break
                    time.sleep(0.05)
                else:
                    raise TimeoutError("web service did not activate permanent applications")
            return service_info(state)
        if mode == "applications":
            state["mode"] = mode
        state["port"] = 0
        state["key"] = secrets.token_hex(32)
        state["pid"] = 0
        write_json(state_dir() / "service.json", state)
        log_path = state_dir() / "server.log"
        if redirected(log_path):
            raise ValueError("web service log redirects")
        descriptor = os.open(str(log_path), os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "wb") as log:
            options = {"start_new_session": True} if os.name != "nt" else {
                "creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
            process = subprocess.Popen([sys.executable, "-B", str(Path(__file__).resolve()), "serve"],
                                       stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                       cwd=str(state_dir()), close_fds=True, **options)
        deadline = time.monotonic() + START_TIMEOUT
        while time.monotonic() < deadline:
            current = load_state()
            running = health(current) if current else None
            if running and running["pid"] == process.pid:
                # A long-lived importing publisher still owns child reaping, not shutdown.
                threading.Thread(target=process.wait, daemon=True).start()
                return service_info(current)
            if process.poll() is not None:
                raise OSError("SmartKit web service startup failed; inspect " + str(log_path))
            time.sleep(0.05)
        # This PID was created here, unlike an unverified PID from saved state.
        process.terminate()
        process.wait(timeout=3)
        raise TimeoutError("SmartKit web service startup timed out; inspect " + str(log_path))


def cleanup_artifacts() -> None:
    """Trigger owner cleanup outside page reads; retain diagnostics and partial effects."""
    artifact_cache.cleanup_expired()
    clean_artifact_records(time.time())


def publish_artifact(identity: str) -> Dict[str, str]:
    """Return current URLs for declared public files, without renewing cache expiry.

    Cache creation is separate and remains complete if delivery fails. Native
    OSError/ValueError failures may leave a service or publication mark in place.
    """
    info = ensure_service()
    artifact = artifact_cache.mark_published(identity)
    return {name: info["origin"] + "/artifacts/" + identity + "/" + quote(name, safe="/")
            for name, entry in artifact.files.items() if entry.public}


def stop_service() -> bool:
    """Stop only the authenticated instance; leave last-known discovery state."""
    with start_lock():
        state = load_state()
        if state is None:
            return False
        running = health(state)
        if not running:
            if state["port"] and not port_available(state["port"]):
                raise OSError("refusing to stop an unverified process on the web service port")
            return False
        os.kill(running["pid"], signal.SIGTERM)
        deadline = time.monotonic() + 4
        while health(state):
            if time.monotonic() >= deadline:
                raise TimeoutError("verified web service process did not stop")
            time.sleep(0.05)
        return True


class WebHandler(BaseHTTPRequestHandler):
    server_version = "SmartKitWeb/1"

    def log_message(self, format: str, *args: object) -> None:
        # Access URLs contain capabilities; do not persist request targets or keys.
        pass

    def respond(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8", *, artifact: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        policy = "sandbox allow-scripts; default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:; connect-src 'none'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'" if artifact else "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
        self.send_header("Content-Security-Policy", policy)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        state = self.server.web_state
        own_origin = origin(state)
        if (self.headers.get("Host") != "127.0.0.1:" + str(state["port"])
                or self.headers.get("Origin") not in (None, own_origin)
                or self.headers.get("Sec-Fetch-Site") == "cross-site" and self.path.startswith(("/apps/", "/api/"))):
            self.respond(403, b"Forbidden")
            return
        parsed = urlsplit(self.path)
        try:
            path = unquote(parsed.path, errors="strict")
            if "\\" in path or any(ord(c) < 32 for c in path) or ".." in path.split("/"):
                self.respond(404, b"Not found")
                return
            if path.startswith("/artifacts/"):
                parts = path.split("/", 3)
                if len(parts) != 4:
                    self.respond(404, b"Not found")
                    return
                cached = artifact_cache.load_artifact(parts[2])
                record = load_artifact(parts[2]) if cached is None else None
                if cached is None and record is None or cached is not None and not cached.published:
                    self.respond(404, b"Artifact unavailable or expired")
                    return
                expires = cached.expires_at if cached is not None else record["created_at"] + RETENTION_SECONDS
                if time.time() >= expires:
                    self.respond(410, "此产物已超过保留期，请重新生成。".encode("utf-8"))
                    return
                name = public_name(parts[3])
                if cached is not None:
                    entry = cached.files.get(name)
                    if entry is None or not entry.public:
                        self.respond(404, b"Not found")
                        return
                    try:
                        content = artifact_cache.read_file(entry)
                    except ValueError:
                        self.respond(409, b"Captured artifact changed; regenerate preview")
                        return
                else:
                    if name not in record["files"]:
                        self.respond(404, b"Not found")
                        return
                    entry = record["files"][name]
                    content = captured_file(Path(entry["path"]))
                    if hashlib.sha256(content).hexdigest() != entry["sha256"]:
                        self.respond(409, b"Captured artifact changed; regenerate preview")
                        return
                mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
                self.respond(200, content, mime + ("; charset=utf-8" if mime.startswith("text/") else ""), artifact=True)
                return
            query = parse_qs(parsed.query)
            authorization = self.headers.get("Authorization", "")
            supplied = authorization[7:] if authorization.startswith("Bearer ") else ""
            if not supplied:
                keys = query.get("key", [])
                supplied = keys[0] if len(keys) == 1 else ""
            if not hmac.compare_digest(supplied.encode("utf-8"), state["key"].encode("ascii")):
                self.respond(403, b"Private SmartKit page: open the URL returned by web_service.py ensure")
                return
            if path == "/api/service/health":
                value = {"schema": SERVICE_SCHEMA, "pid": os.getpid(), "mode": state["mode"],
                         "artifact_cache_schema": artifact_cache.SCHEMA}
                self.respond(200, json.dumps(value).encode("utf-8"), "application/json; charset=utf-8")
                return
            parts = path.strip("/").split("/")
            if len(parts) != 2 or parts[0] not in ("apps", "api") or parts[1] not in ("readiness", "setup"):
                self.respond(404, b"Not found")
                return
            if state["mode"] != "applications":
                self.respond(404, b"Permanent applications are not enabled")
                return
            project_ids = query.get("project", [""])
            if len(project_ids) != 1:
                raise ValueError("one project id is required")
            data = application_data(parts[1], project_ids[0])
            if parts[0] == "api":
                self.respond(200, json.dumps(data, ensure_ascii=True).encode("utf-8"), "application/json; charset=utf-8")
            else:
                self.respond(200, render_application(parts[1], state["key"], data), "text/html; charset=utf-8")
        except FileNotFoundError:
            self.respond(404, b"Captured data unavailable; regenerate preview or run the owning hook")
        except (OSError, ValueError) as error:
            # This read boundary cannot repair cached evidence; preserve it and report failure.
            logging.getLogger("smartkit.web").error("Web service read failed: %s", error)
            self.respond(500, b"Web service data could not be read; inspect SmartKit server.log")


class WebServer(ThreadingHTTPServer):
    allow_reuse_address = os.name != "nt"

    def server_bind(self) -> None:
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(2)
        return connection, address

    def handle_error(self, request: object, client_address: object) -> None:
        logging.getLogger("smartkit.web").exception("Web service request failed")


def serve() -> None:
    state = load_state()
    if state is None:
        raise ValueError("start the service through ensure, not serve")
    logger = logging.getLogger("smartkit.web")
    logger.addHandler(RotatingFileHandler(str(state_dir() / "requests.log"), maxBytes=131072, backupCount=1, encoding="utf-8"))
    with WebServer(("127.0.0.1", 0), WebHandler) as server:
        state["port"] = server.server_port
        state["pid"] = os.getpid()
        write_json(state_dir() / "service.json", state)
        server.web_state = state
        server.timeout = 0.5
        stopping = False
        def stop(signum: int, frame: object) -> None:
            nonlocal stopping
            stopping = True
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        started = time.monotonic()
        next_cleanup = started + CLEANUP_INTERVAL
        while not stopping:
            current = load_state()
            if current is None or current["key"] != state["key"] or current["pid"] != os.getpid():
                raise ValueError("web service state changed unexpectedly")
            state["mode"] = current["mode"]
            if time.monotonic() >= next_cleanup:
                try:
                    cleanup_artifacts()
                except (OSError, ValueError):
                    # Background cleanup owns reporting; page delivery and future cleanup remain available.
                    logger.exception("Artifact cleanup failed; prior removals may remain effective")
                next_cleanup = time.monotonic() + CLEANUP_INTERVAL
            if (state["mode"] == "previews" and time.monotonic() - started > 10
                    and not artifact_cache.has_unexpired_artifacts(time.time())
                    and not has_unexpired_artifacts(time.time())):
                break
            server.handle_request()


def hook_project(harness: str) -> str:
    content = sys.stdin.read()
    payload = json.loads(content) if content.strip() else {}
    if not isinstance(payload, dict):
        raise ValueError("hook input must be a JSON object")
    project = payload.get("cwd") or payload.get("project_dir") or payload.get("workspaceRoot")
    if project is None and isinstance(payload.get("workspace_roots"), list) and payload["workspace_roots"]:
        project = payload["workspace_roots"][0]
    if project is not None and not isinstance(project, str):
        raise ValueError("hook project path must be a string")
    target = Path(project) if project else Path.cwd()
    record_project(target, harness)
    info = ensure_service()
    links = hook_page_links(target, harness, info["apps"])
    if not links:
        return ""
    return "这些是本机私有的只读状态页；查看详情不会执行修复：\n" + "\n".join(
        "- [" + title + "](" + url + ")" for title, url in links.items())


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manage SmartKit's per-user loopback HTTP service and private status pages.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''ensure starts/reuses a loopback service and returns origin, pid, mode and apps URLs.
Every new process binds port0; healthy live instances keep their current address.
Readiness shows the last complete owner-produced check. Setup shows the current
initialization/version/migration state. Use these pages to inspect findings or
setup/upgrade status. Page reads run no checks, acquisition, repair or maintenance.
Private app URLs contain credentials; keep them private. status starts no process.
stop ends the shared service only when that outcome is requested, not per chat.
Publish only a shared-cache artifact with explicitly declared public files. Raw
snapshots and undeclared files remain private. Publication can leave a healthy
service or mark after failure; preserve diagnostics and the cache artifact ID.
After restart, publish the same retained ID again to refresh URLs without
recapturing contents or extending expires_at. Old full URLs may become stale.
HTTP refuses expired artifacts immediately. Startup, new cache creation and a
60-second service loop trigger owner cleanup. Offline expiry is cleaned next
startup. Permanent pages and project source records have separate lifetimes.
There is no URL-click startup, login registration or continuous watchdog.
Examples (<plugin-root> is the actual loaded installation):
  python "<plugin-root>/runtime/web/web_service.py" ensure
  python "<plugin-root>/runtime/web/web_service.py" status
  python "<plugin-root>/runtime/web/web_service.py" publish --id artifact-ID
  python "<plugin-root>/runtime/web/web_service.py" stop
  python "<plugin-root>/runtime/web/web_service.py" ensure --mode previews
''')
    commands = parser.add_subparsers(dest="command", required=True)
    ensure = commands.add_parser("ensure", help="Start/reuse the service and print its origin and private app URLs.")
    ensure.add_argument("--mode", choices=("applications", "previews"), default="applications")
    commands.add_parser("status", help="Read authenticated live service status without starting it.")
    commands.add_parser("stop", help="Stop the authenticated service; next startup allocates a free port.")
    publish = commands.add_parser("publish", help="Publish or refresh declared public files from one retained cache ID.")
    publish.add_argument("--id", required=True)
    commands.add_parser("serve", help=argparse.SUPPRESS)
    hook = commands.add_parser("hook", help="Record a project and ensure the service from a session-start hook.")
    hook.add_argument("--harness", required=True, choices=("codex", "cursor", "copilot", "qoder"))
    args = parser.parse_args(argv)
    try:
        if args.command == "ensure":
            print(json.dumps(ensure_service(args.mode), ensure_ascii=True))
        elif args.command == "status":
            state = load_state()
            running = health(state) if state else None
            print(json.dumps({"running": bool(running), "service": service_info(state) if running else None}))
        elif args.command == "stop":
            print(json.dumps({"stopped": stop_service()}))
        elif args.command == "publish":
            print(json.dumps(publish_artifact(args.id), ensure_ascii=True))
        elif args.command == "hook":
            context = hook_project(args.harness)
            if context:
                if args.harness in ("codex", "qoder"):
                    output = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}
                elif args.harness == "cursor":
                    output = {"additional_context": context}
                else:
                    output = {"additionalContext": context}
                print(json.dumps(output, ensure_ascii=True))
        else:
            serve()
        return 0
    except (OSError, ValueError) as error:
        print("SmartKit HTTP service failed: " + str(error), file=sys.stderr)
        return 0 if args.command == "hook" else 1


if __name__ == "__main__":
    raise SystemExit(main())
