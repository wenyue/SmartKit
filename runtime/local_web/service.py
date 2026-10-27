"""Coordinate one authenticated local host, independently of request handling."""
from __future__ import annotations

import contextlib
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import re
import secrets
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Dict, Iterator, Optional
import urllib.request
from urllib.parse import quote

from . import HOST, PORT, ORIGIN, SERVICE_SCHEMA
from . import artifacts
from .storage import prepare_cache, prepare_state, read_json, redirected, state_dir, write_json
from .apps.status import hook_page_links, record_project

START_TIMEOUT = 8.0
CLEANUP_INTERVAL = 60.0
PLUGIN_MANIFEST = Path(__file__).resolve().parents[2] / ".claude-plugin/plugin.json"
_SEMVER = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)


def _version_key(value: object) -> tuple:
    """Order SemVer releases and prereleases; build metadata has no precedence."""
    if not isinstance(value, str) or _SEMVER.fullmatch(value) is None:
        raise ValueError("local host plugin version must be a semantic version")
    release, _, prerelease = value.split("+", 1)[0].partition("-")
    identifiers = tuple((0, int(part)) if part.isdigit() else (1, part)
                        for part in prerelease.split(".") if part)
    return tuple(int(part) for part in release.split(".")), not prerelease, identifiers


def _installed_version() -> str:
    manifest = read_json(PLUGIN_MANIFEST)
    version = manifest.get("version") if isinstance(manifest, dict) else None
    _version_key(version)
    return version


def load_state() -> Optional[dict]:
    try:
        state = read_json(state_dir() / "service.json")
    except FileNotFoundError:
        return None
    if (not isinstance(state, dict) or set(state) != {"schema", "port", "key", "mode", "pid"}
            or state["schema"] != SERVICE_SCHEMA or type(state["port"]) is not int or state["port"] != PORT
            or not isinstance(state["key"], str) or len(state["key"]) != 64
            or any(c not in "0123456789abcdef" for c in state["key"])
            or state["mode"] not in ("applications", "previews")
            or type(state["pid"]) is not int or state["pid"] < 0):
        raise ValueError("invalid local host state; preserve service.json for diagnosis")
    return state


@contextlib.contextmanager
def start_lock(*, deadline: Optional[float] = None) -> Iterator[None]:
    if deadline is None:
        deadline = time.monotonic() + START_TIMEOUT
    path = prepare_state() / "start.lock"
    if redirected(path):
        raise ValueError("local host startup lock redirects")
    descriptor = os.open(str(path), os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, "r+b") as stream:
        if os.name == "nt":
            import msvcrt
            # Windows permits locking past EOF; writing a marker races another owner.

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
                    raise TimeoutError("another local host startup still holds the lock")
                time.sleep(0.05)
            except OSError as error:
                # Native Windows reports lock contention with EACCES.
                if os.name != "nt" or error.errno != 13 or time.monotonic() >= deadline:
                    raise
                time.sleep(0.05)
        try:
            yield
        finally:
            release()


def service_info(state: dict) -> dict:
    return {"origin": ORIGIN, "pid": state["pid"], "mode": state["mode"],
            "apps": {feature: ORIGIN + "/" + feature + "/?key=" + state["key"]
                     for feature in ("readiness", "setup")}}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def health(state: dict) -> Optional[dict]:
    request = urllib.request.Request(ORIGIN + "/api/service/health",
                                     headers={"Authorization": "Bearer " + state["key"]})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=0.4) as response:
            value = json.loads(response.read(8192).decode("utf-8"))
        if (isinstance(value, dict) and value.get("schema") == SERVICE_SCHEMA
                and value.get("artifact_cache_schema") == artifacts.SCHEMA
                and type(value.get("pid")) is int and value["pid"] > 0
                and value.get("mode") in ("applications", "previews")):
            return value
    except (OSError, ValueError):
        return None
    return None


def port_available() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        if os.name == "nt":
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind((HOST, PORT))
        except OSError:
            return False
        return True


def ensure_service(mode: str = "applications") -> dict:
    """Return a verified fixed-origin host; an unknown port owner is never stopped.

    Native failures may leave a child host running, but never return an unverified
    URL. Older and legacy authenticated peers are replaced while retaining their
    credential and mode; newer compatible peers are reused. Invalid versions fail
    before replacement. Preview callers cannot downgrade an application host.
    """
    if mode not in ("applications", "previews"):
        raise ValueError("unknown local host mode")
    deadline = time.monotonic() + START_TIMEOUT
    required_version = _version_key(_installed_version())
    with start_lock(deadline=deadline):
        prepare_cache()
        cleanup_artifacts()
        if time.monotonic() >= deadline:
            raise TimeoutError("local host startup deadline expired")
        state = load_state()
        running = health(state) if state else None
        if running:
            state["pid"] = running["pid"]
            state["mode"] = ("applications" if "applications" in (mode, state["mode"], running["mode"])
                             else "previews")
            if "plugin_version" not in running or _version_key(running["plugin_version"]) < required_version:
                _stop_owned(state, running, deadline=min(deadline, time.monotonic() + 4))
                state["pid"] = 0
            else:
                write_json(state_dir() / "service.json", state)
                while running["mode"] != state["mode"]:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("local host did not activate permanent applications")
                    time.sleep(0.05)
                    running = health(state)
                    if running is None:
                        raise OSError("local host stopped during mode activation")
                return service_info(state)
        else:
            state = {"schema": SERVICE_SCHEMA, "port": PORT, "key": secrets.token_hex(32), "mode": mode, "pid": 0}
        if not port_available():
            raise OSError("127.0.0.1:47821 is occupied by an unverified process; it was not stopped")
        if time.monotonic() >= deadline:
            raise TimeoutError("local host startup deadline expired")
        write_json(state_dir() / "service.json", state)
        log_path = state_dir() / "server.log"
        if redirected(log_path):
            raise ValueError("local host log redirects")
        descriptor = os.open(str(log_path), os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "wb") as log:
            options = {"start_new_session": True} if os.name != "nt" else {
                "creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
            process = subprocess.Popen([sys.executable, "-B", str(Path(__file__).with_name("__main__.py")), "serve"],
                                       stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                       cwd=str(state_dir()), close_fds=True, **options)
        try:
            while time.monotonic() < deadline:
                current = load_state()
                running = health(current) if current else None
                if (running and running["pid"] == process.pid and "plugin_version" in running
                        and _version_key(running["plugin_version"]) >= required_version):
                    current["pid"] = running["pid"]
                    threading.Thread(target=process.wait, daemon=True).start()
                    return service_info(current)
                if process.poll() is not None:
                    raise OSError("SmartKit local host startup failed; inspect " + str(log_path))
                time.sleep(0.05)
            raise TimeoutError("SmartKit local host startup timed out; inspect " + str(log_path))
        except BaseException:
            # Only our child is eligible for cleanup after any readiness failure or cancellation.
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired as error:
                    threading.Thread(target=process.wait, daemon=True).start()
                    raise TimeoutError("local host startup failed and its child did not stop; inspect " + str(log_path)) from error
            raise


def cleanup_artifacts() -> None:
    artifacts.cleanup_expired()


def publish_artifact(identity: str) -> Dict[str, str]:
    """Publish declared files without renewing expiry; failed delivery retains the group."""
    info = ensure_service()
    artifact = artifacts.mark_published(identity)
    return {name: info["origin"] + "/preview/" + identity + "/" + quote(name, safe="/")
            for name, entry in artifact.files.items() if entry.public}


def stop_service() -> bool:
    """Stop only a live authenticated instance; an unknown port owner remains untouched."""
    with start_lock():
        state = load_state()
        running = health(state) if state else None
        if not running:
            if not port_available():
                raise OSError("refusing to stop an unverified process on the local host port")
            return False
        _stop_owned(state, running, deadline=time.monotonic() + 4)
        return True


def _stop_owned(state: dict, running: dict, *, deadline: float) -> None:
    """Stop an authenticated peer while the caller holds the startup lock."""
    if time.monotonic() >= deadline:
        raise TimeoutError("local host stop deadline expired")
    try:
        os.kill(running["pid"], signal.SIGTERM)
    except ProcessLookupError:
        # The authenticated peer may exit between its health response and SIGTERM.
        pass
    # A missed health response alone does not prove the listener has closed.
    while health(state) is not None or not port_available():
        if time.monotonic() >= deadline:
            raise TimeoutError("verified local host did not release its port")
        time.sleep(0.05)


def serve() -> None:
    from .http_server import WebServer, WebHandler

    plugin_version = _installed_version()
    state = load_state()
    if state is None:
        raise ValueError("start the local host through ensure, not serve")
    logger = logging.getLogger("smartkit.local_web")
    handler = RotatingFileHandler(str(state_dir() / "requests.log"), maxBytes=131072, backupCount=1, encoding="utf-8")
    logger.addHandler(handler)
    try:
        with WebServer((HOST, PORT), WebHandler) as server:
            state["pid"] = os.getpid()
            write_json(state_dir() / "service.json", state)
            server.web_state = state
            # Keep this outside service.json: legacy callers reject extra state fields.
            server.plugin_version = plugin_version
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
                    raise ValueError("local host state changed unexpectedly")
                state["mode"] = current["mode"]
                if time.monotonic() >= next_cleanup:
                    try:
                        cleanup_artifacts()
                    except (OSError, ValueError):
                        # Cleanup owns reporting; reads and future cleanup remain available.
                        logger.exception("Artifact cleanup failed; prior removals may remain effective")
                    next_cleanup = time.monotonic() + CLEANUP_INTERVAL
                if (state["mode"] == "previews" and time.monotonic() - started > 10
                        and not artifacts.has_unexpired_artifacts(time.time())):
                    break
                server.handle_request()
    finally:
        logger.removeHandler(handler)
        handler.close()


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
