"""Map feature routes to HTTP while enforcing the local host's access boundaries."""
from __future__ import annotations

import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import mimetypes
import os
import socket
import time
from urllib.parse import parse_qs, unquote, urlsplit

from . import HOST, PORT, ORIGIN, SERVICE_SCHEMA
from . import artifacts
from .apps import diff, status


class WebHandler(BaseHTTPRequestHandler):
    server_version = "SmartKitLocalWeb/1"

    def log_message(self, format: str, *args: object) -> None:
        # Targets contain private paths and status-page credentials.
        pass

    def respond(self, code: int, body: bytes, content_type: str = "text/plain; charset=utf-8", *, preview: bool = False, interactive: bool = False) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        if preview:
            policy = "sandbox allow-scripts; default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:; connect-src 'none'"
        elif interactive:
            policy = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'"
        else:
            policy = "default-src 'none'; style-src 'unsafe-inline'"
        self.send_header("Content-Security-Policy", policy + "; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def json(self, code: int, value: object) -> None:
        self.respond(code, json.dumps(value, ensure_ascii=True).encode("utf-8"), "application/json; charset=utf-8")

    def allowed_host(self) -> bool:
        return (self.headers.get("Host") == HOST + ":" + str(PORT)
                and self.headers.get("Origin") in (None, ORIGIN))

    def private_access(self, query: str) -> bool:
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            return False
        authorization = self.headers.get("Authorization", "")
        supplied = authorization[7:] if authorization.startswith("Bearer ") else ""
        if not supplied:
            keys = parse_qs(query).get("key", [])
            supplied = keys[0] if len(keys) == 1 else ""
        return hmac.compare_digest(supplied.encode("utf-8"), self.server.web_state["key"].encode("ascii"))

    def do_GET(self) -> None:
        if not self.allowed_host():
            self.respond(403, b"Forbidden")
            return
        if len(self.path) > 32768:
            self.respond(414, b"URL too long")
            return
        parsed = urlsplit(self.path)
        try:
            path = unquote(parsed.path, errors="strict")
            if "\\" in path or any(ord(c) < 32 for c in path) or ".." in path.split("/"):
                self.respond(404, b"Not found")
                return
            if path in ("/diff", "/diff/html"):
                try:
                    target = diff.target_from_query(parsed.query)
                except ValueError as error:
                    self.respond(400, str(error).encode("utf-8"))
                    return
                # An untrusted preview can navigate, despite its blocked fetch access.
                automatic = (self.headers.get("Sec-Fetch-User") == "?1"
                             or self.headers.get("Sec-Fetch-Site") in ("none", "same-origin"))
                page = diff.render_page(target, html_only=path.endswith("/html"), automatic=automatic)
                if page.redirect:
                    self.send_response(303)
                    self.send_header("Location", page.redirect)
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Referrer-Policy", "no-referrer")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                self.respond(200, page.content, "text/html; charset=utf-8", interactive=path == "/diff")
                return
            if path.startswith("/preview/"):
                parts = path.split("/", 3)
                if len(parts) != 4:
                    self.respond(404, b"Not found")
                    return
                artifact = artifacts.load_artifact(parts[2])
                if artifact is None or not artifact.published:
                    self.respond(404, b"Preview unavailable")
                    return
                if time.time() >= artifact.expires_at:
                    self.respond(410, "此产物已超过保留期，请重新生成。".encode("utf-8"))
                    return
                name = artifacts.filename(parts[3])
                entry = artifact.files.get(name)
                if entry is None or not entry.public:
                    self.respond(404, b"Not found")
                    return
                try:
                    content = artifacts.read_file(entry)
                except ValueError:
                    self.respond(409, b"Captured preview changed; regenerate it")
                    return
                mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
                self.respond(200, content, mime + ("; charset=utf-8" if mime.startswith("text/") else ""), preview=True)
                return
            if not self.private_access(parsed.query):
                self.respond(403, b"Private SmartKit page: use the URL returned by the local host CLI")
                return
            state = self.server.web_state
            if path == "/api/service/health":
                self.json(200, {"schema": SERVICE_SCHEMA, "pid": os.getpid(), "mode": state["mode"],
                                "artifact_cache_schema": artifacts.SCHEMA})
                return
            parts = path.strip("/").split("/")
            api = parts[0] == "api"
            if api:
                parts = parts[1:]
            if len(parts) not in (1, 2) or parts[0] not in ("readiness", "setup"):
                self.respond(404, b"Not found")
                return
            if state["mode"] != "applications":
                self.respond(404, b"Permanent applications are not enabled")
                return
            data = status.application_data(parts[0], parts[1] if len(parts) == 2 else "")
            if api:
                self.json(200, data)
            else:
                self.respond(200, status.render_application(parts[0], state["key"], data), "text/html; charset=utf-8")
        except FileNotFoundError:
            self.respond(404, "比较或记录不可用；请检查仓库路径、Git 基线及所属功能的记录。".encode("utf-8"))
        except (OSError, ValueError) as error:
            # Reads cannot repair evidence; retain it and make this operation's failure visible.
            logging.getLogger("smartkit.local_web").error("Local page read failed: %s", error)
            self.respond(409, ("无法读取比较或记录：" + str(error)).encode("utf-8"))

    def do_POST(self) -> None:
        if (not self.allowed_host() or self.headers.get("Origin") != ORIGIN
                or self.headers.get("Sec-Fetch-Site") not in (None, "same-origin")):
            self.json(403, {"message": "Forbidden"})
            return
        if self.headers.get("Transfer-Encoding") or self.headers.get("Content-Length", "0") != "0":
            self.close_connection = True
            self.json(400, {"message": "The launch operation takes URL parameters only"})
            return
        parsed = urlsplit(self.path)
        if parsed.path != "/api/diff/open":
            self.json(404, {"message": "Not found"})
            return
        if len(self.path) > 32768:
            self.json(414, {"message": "URL too long"})
            return
        try:
            target = diff.target_from_query(parsed.query)
        except ValueError as error:
            self.json(400, {"message": str(error)})
            return
        try:
            self.json(200, diff.open_editor(target))
        except (OSError, ValueError) as error:
            self.json(409, {"message": "无法打开比较：" + str(error)})


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
        logging.getLogger("smartkit.local_web").exception("Local host request failed")
