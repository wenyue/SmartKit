"""Explicit, current-user login registration for the local web host."""
from __future__ import annotations

from dataclasses import dataclass
import errno
import hashlib
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time
from typing import Literal

from . import service, storage


Backend = Literal["windows", "systemd", "xdg"]
RegistrationState = Literal["unsupported", "disabled", "unconfigured", "missing", "incomplete",
                            "modified", "disabled-in-system", "installed"]


@dataclass(frozen=True)
class AutostartStatus:
    supported: bool
    preference: bool | None
    state: RegistrationState
    backend: Backend | None
    message: str = ""


def _config_path() -> Path:
    return storage.state_dir() / "config.json"


def preference() -> bool | None:
    try:
        value = storage.read_json(_config_path())
    except FileNotFoundError:
        return None
    if not isinstance(value, dict) or not isinstance(value.get("localWeb", {}), dict):
        raise ValueError("invalid local Web user configuration; it was preserved")
    result = value.get("localWeb", {}).get("autostart")
    if result is not None and type(result) is not bool:
        raise ValueError("localWeb.autostart must be a boolean or absent")
    return result


def _save_preference(enabled: bool) -> None:
    storage.prepare_state()
    try:
        value = storage.read_json(_config_path())
    except FileNotFoundError:
        value = {}
    preference()  # Validate before preserving unrelated user settings.
    value.setdefault("localWeb", {})["autostart"] = enabled
    storage.write_json(_config_path(), value)


def _run(arguments: list[str]) -> subprocess.CompletedProcess:
    options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    try:
        return subprocess.run(arguments, capture_output=True, text=True, timeout=10, **options)
    except subprocess.TimeoutExpired as error:
        raise TimeoutError("login registration command timed out") from error


def _command(arguments: list[str]) -> None:
    result = _run(arguments)
    if result.returncode:
        raise OSError("login registration failed: " + (result.stderr.strip() or result.stdout.strip()))


def _select_backend() -> Backend | None:
    if sys.platform == "win32":
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        return "windows" if pythonw.is_file() and shutil.which("powershell") else None
    if sys.platform.startswith("linux"):
        if shutil.which("systemctl"):
            try:
                if _run(["systemctl", "--user", "show-environment"]).returncode == 0:
                    return "systemd"
            except (OSError, subprocess.TimeoutExpired):
                pass  # A desktop registration can work without a user service manager.
        if os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION"):
            return "xdg"
    return None


def _registration(backend: Backend) -> Path:
    if backend == "windows":
        configured = Path(os.environ.get("APPDATA", ""))
        base = configured if configured.is_absolute() else Path.home() / "AppData/Roaming"
        return base / "Microsoft/Windows/Start Menu/Programs/Startup/SmartKit Local Web.lnk"
    configured = Path(os.environ.get("XDG_CONFIG_HOME", ""))
    base = configured if configured.is_absolute() else Path.home() / ".config"
    if backend == "systemd":
        return base / "systemd/user/smartkit-local-web.service"
    if backend == "xdg":
        return base / "autostart/smartkit-local-web.desktop"
    raise ValueError("unknown login registration backend")


def _startup_dir() -> Path:
    path = storage.state_dir() / "startup"
    if storage.redirected(path):
        raise ValueError("login namespace redirects; it was preserved")
    return path


def _record_path() -> Path:
    return _startup_dir() / "installation.json"


def _paths(backend: Backend) -> dict[str, Path]:
    return {"registration": _registration(backend),
            "launcher": _startup_dir() / "launcher.py",
            "runtime": _startup_dir() / "runtime.json"}


def _digest(path: Path) -> str:
    if storage.redirected(path):
        raise ValueError("login registration redirects; preserve it: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record() -> dict | None:
    try:
        value = storage.read_json(_record_path())
    except FileNotFoundError:
        return None
    if (not isinstance(value, dict) or set(value) != {"schema", "backend", "digests", "complete"}
            or type(value["schema"]) is not int or value["schema"] != 1 or value["backend"] not in ("windows", "systemd", "xdg")
            or type(value["complete"]) is not bool or not isinstance(value["digests"], dict)
            or not set(value["digests"]).issubset({"registration", "launcher", "runtime"})
            or any(not isinstance(v, str) or len(v) != 64
                   or any(c not in "0123456789abcdef" for c in v)
                   for v in value["digests"].values())):
        raise ValueError("invalid login registration ownership record; it was preserved")
    if (value["backend"] == "windows") != (sys.platform == "win32"):
        raise ValueError("login registration belongs to another operating system")
    return value


def inspect_status() -> AutostartStatus:
    selected = preference()
    record = _record()
    if record is None:
        if selected is False:
            return AutostartStatus(True, False, "disabled", None)
        backend = _select_backend()
        if backend is None:
            return AutostartStatus(False, selected, "unsupported", None,
                                   "No supported current-user login mechanism is available.")
        state = "unconfigured" if selected is None else "missing"
        return AutostartStatus(True, selected, state, backend)
    backend = record["backend"]
    for name, path in _paths(backend).items():
        if name not in record["digests"]:
            return AutostartStatus(True, selected, "incomplete", backend, "Login registration did not complete.")
        try:
            if _digest(path) != record["digests"][name]:
                return AutostartStatus(True, selected, "modified", backend,
                                       "A managed login file changed; it was preserved: " + str(path))
        except FileNotFoundError:
            return AutostartStatus(True, selected, "missing", backend,
                                   "A managed login file is missing: " + str(path))
    if not record["complete"]:
        return AutostartStatus(True, selected, "incomplete", backend, "Login registration did not complete.")
    if backend == "systemd":
        result = _run(["systemctl", "--user", "is-enabled", "smartkit-local-web.service"])
        if result.returncode or result.stdout.strip() != "enabled":
            return AutostartStatus(True, selected, "disabled-in-system", backend,
                                   "The user service is disabled or masked; no repair was attempted.")
    return AutostartStatus(True, selected, "installed", backend)


def _runtime() -> dict:
    root = Path(__file__).resolve().parents[2]
    return {"plugin_root": str(root), "version": service._installed_version()}


def _quote(value: str, backend: Backend) -> str:
    if any(character in value for character in ("\0", "\r", "\n")):
        raise ValueError("login command paths must not contain NUL or newlines")
    quoted = value.replace('\\', '\\\\').replace('"', '\\"')
    if backend == "systemd":
        quoted = quoted.replace('\t', '\\t')
    else:
        # Desktop Entry string escapes are decoded before Exec argument escapes.
        quoted = quoted.replace('`', '\\`').replace('$', '\\$').replace('\\', '\\\\')
    return '"' + quoted.replace('%', '%%') + '"'


def _register(backend: Backend, target: Path, launcher: Path) -> None:
    if storage.redirected(target.parent):
        raise ValueError("login registration directory redirects: " + str(target.parent))
    target.parent.mkdir(parents=True, exist_ok=True)
    if backend == "windows":
        def literal(value: str) -> str:
            return "'" + value.replace("'", "''") + "'"
        pythonw = str(Path(sys.executable).with_name("pythonw.exe"))
        arguments = subprocess.list2cmdline(["-B", str(launcher)])
        script = ("$ErrorActionPreference='Stop'; $shell=New-Object -ComObject WScript.Shell; "
                  "$link=$shell.CreateShortcut(" + literal(str(target)) + "); "
                  "$link.TargetPath=" + literal(pythonw) + "; $link.Arguments=" + literal(arguments)
                  + "; $link.WindowStyle=7; $link.Save()")
        _command([shutil.which("powershell") or "powershell", "-NoProfile", "-NonInteractive", "-Command", script])
    else:
        executable = sys.executable
        if backend == "systemd":
            # Disable systemd environment expansion; every path is already literal.
            executable = ":" + executable
        elif "=" in executable:
            raise ValueError("Desktop Entry executable paths must not contain '='")
        command = " ".join(_quote(value, backend) for value in (executable, "-B", str(launcher)))
        if backend == "systemd":
            content = ("[Unit]\nDescription=SmartKit local Web (current user)\n\n[Service]\nType=simple\n"
                       "ExecStart=" + command + "\n\n[Install]\nWantedBy=default.target\n")
        else:
            content = ("[Desktop Entry]\nType=Application\nName=SmartKit Local Web\nTerminal=false\nExec="
                       + command + "\n")
        target.write_text(content, encoding="utf-8")
    if backend == "systemd":
        _command(["systemctl", "--user", "daemon-reload"])
        # Register for the next login; do not interrupt the host shared by current chats.
        _command(["systemctl", "--user", "enable", "smartkit-local-web.service"])


def configure(enabled: bool) -> AutostartStatus:
    """Apply an explicit choice; modified or unowned native files are preserved.

    A failed registration retains the user's choice and reports failure. Disabling
    changes future login behavior without stopping the host used by active chats.
    """
    if type(enabled) is not bool:
        raise ValueError("the login choice must be boolean")
    with service.start_lock():
        _save_preference(enabled)
        record = _record()
        status = inspect_status()
        backend = record["backend"] if record else status.backend
        paths = _paths(backend) if backend else {}
        for name, path in paths.items():
            if path.exists() or storage.redirected(path):
                if record is None or name not in record["digests"] or _digest(path) != record["digests"][name]:
                    raise ValueError("unowned or modified login file was preserved: " + str(path))
        if not enabled:
            if record is not None:
                if backend == "systemd":
                    _command(["systemctl", "--user", "disable", "smartkit-local-web.service"])
                for name, path in paths.items():
                    if name in record["digests"] and path.exists():
                        path.unlink()
                _record_path().unlink()
                if backend == "systemd":
                    _command(["systemctl", "--user", "daemon-reload"])
            return inspect_status()
        if not status.supported:
            raise OSError(status.message)
        target = _registration(backend)
        startup = _startup_dir()
        startup.mkdir(mode=0o700, exist_ok=True)
        record = record or {"schema": 1, "backend": backend, "digests": {}}
        record["complete"] = False
        storage.write_json(_record_path(), record)
        complete = False
        try:
            paths["launcher"].write_bytes(Path(__file__).with_name("startup_launcher.py").read_bytes())
            storage.write_json(paths["runtime"], _runtime())
            _register(backend, target, paths["launcher"])
            complete = True
        finally:
            # Retain partial ownership so failed native registration can be inspected.
            primary = sys.exc_info()[1]
            try:
                digests = {name: _digest(path) for name, path in paths.items() if path.is_file()}
                storage.write_json(_record_path(), {"schema": 1, "backend": backend, "digests": digests,
                                                    "complete": complete})
            except (OSError, ValueError) as error:
                if isinstance(primary, (OSError, ValueError)):
                    raise OSError("Login registration failed: " + str(primary)
                                  + "; partial ownership could not be recorded: " + str(error)
                                  + ". Existing files were preserved.") from error
                raise
        status = inspect_status()
        if status.state != "installed":
            raise OSError("login registration was not verified: " + status.message)
        return status


def refresh_runtime() -> None:
    """Refresh only the owned runtime pointer; never recreate an OS-disabled entry."""
    if preference() is not True or inspect_status().state != "installed":
        return
    with service.start_lock():
        if inspect_status().state != "installed":
            return
        record = _record()
        runtime = _paths(record["backend"])["runtime"]
        previous = storage.read_json(runtime)
        current = _runtime()
        if service._version_key(previous["version"]) > service._version_key(current["version"]):
            return
        if previous != current:
            storage.write_json(runtime, current)
            record["digests"]["runtime"] = _digest(runtime)
            storage.write_json(_record_path(), record)


def run_on_login() -> None:
    """Use the approved user's registration; systemd owns the foreground process."""
    status = inspect_status()
    if status.preference is not True or status.state != "installed":
        return
    if status.backend != "systemd":
        service.ensure_service()
        return
    with service.start_lock():
        state = service.load_state()
        if state and service.health(state):
            return
        if not service.port_available():
            raise OSError("local Web port is occupied by an unverified process")
        if state is None:
            state = {"schema": service.SERVICE_SCHEMA, "port": service.PORT,
                     "key": secrets.token_hex(32), "mode": "applications", "pid": 0}
        state["mode"] = "applications"
        storage.write_json(storage.state_dir() / "service.json", state)
    try:
        service.serve()
    except OSError as error:
        if error.errno != errno.EADDRINUSE:
            raise
        # A concurrent session may have acquired the one listener after the check.
        deadline = time.monotonic() + service.START_TIMEOUT
        while time.monotonic() < deadline:
            state = service.load_state()
            if state and service.health(state):
                return
            time.sleep(0.05)
        raise
