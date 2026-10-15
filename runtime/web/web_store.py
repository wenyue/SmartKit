"""Own web discovery, project observations, and reads of previously delivered artifact records."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "artifacts"))
from artifact_cache import redirected, user_cache_dir
import artifact_cache

_cache_source = Path(__file__).resolve().parents[1] / "artifacts/artifact_cache.py"
if not _cache_source.is_file() or Path(artifact_cache.__file__).resolve() != _cache_source:
    raise ImportError("shared artifact cache is not from the loaded plugin: " + str(_cache_source))


# Previously registered records have this original fixed lifetime; new artifacts own expires_at.
RETENTION_SECONDS = 7 * 24 * 60 * 60
# Persisted schemas and namespaces remain unchanged by the runtime rename.
ARTIFACT_SCHEMA = "smartkit.preview-artifact/v1"
PROJECT_SCHEMA = "smartkit.preview-project/v1"
ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,79}")


def cache_dir() -> Path:
    return user_cache_dir() / "smartkit/preview"


def state_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library/Application Support"
    else:
        configured = Path(os.environ.get("LOCALAPPDATA" if os.name == "nt" else "XDG_STATE_HOME", ""))
        base = configured if configured.is_absolute() else Path.home() / ("AppData/Local" if os.name == "nt" else ".local/state")
    return base.resolve() / "smartkit/preview"


def safe_namespace(root: Path, base: Path) -> None:
    """Allow an explicitly relocated base, but reject redirects inside our namespace."""
    root.relative_to(base)
    current = base
    for part in root.relative_to(base).parts:
        current /= part
        if redirected(current):
            raise ValueError("web service namespace redirects through a link or reparse point: " + str(current))
        current.mkdir(mode=0o700, exist_ok=True)


def prepare_cache() -> Path:
    base = user_cache_dir()
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    safe_namespace(cache_dir(), base)
    return cache_dir()


def prepare_state() -> Path:
    root = state_dir()
    base = root.parent.parent
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    safe_namespace(root, base)
    return root


def read_json(path: Path) -> object:
    if redirected(path):
        raise ValueError("web service metadata must not redirect: " + str(path))
    return json.loads(path.read_bytes().decode("utf-8"))


def write_json(path: Path, value: object, *, create_only: bool = False) -> None:
    if redirected(path):
        raise ValueError("web service metadata must not redirect: " + str(path))
    descriptor, temporary = tempfile.mkstemp(prefix=".pending-", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(json.dumps(value, ensure_ascii=True, indent=2).encode("utf-8"))
        if create_only:
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def public_name(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or any(ord(c) < 32 for c in value):
        raise ValueError("invalid artifact filename")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("artifact filenames must be confined relative paths")
    return value


def captured_file(path: Path) -> bytes:
    """Only cache-contained regular files may become public; inspect every path component."""
    base = user_cache_dir() / "smartkit"
    path = path.absolute()
    try:
        relative = path.relative_to(base)
    except ValueError as error:
        raise ValueError("published files must be captured under the SmartKit user cache") from error
    if ".." in relative.parts:
        raise ValueError("published file escapes the SmartKit cache")
    current = base
    for part in relative.parts:
        if redirected(current):
            raise ValueError("published file path redirects: " + str(current))
        current /= part
    if redirected(current) or not current.is_file():
        raise ValueError("published file is not a regular captured file: " + str(current))
    return current.read_bytes()


def artifact_record(value: object, identity: str) -> Optional[dict]:
    if not isinstance(value, dict) or set(value) != {"schema", "id", "created_at", "files"}:
        return None
    created = value["created_at"]
    if (value["schema"] != ARTIFACT_SCHEMA or value["id"] != identity or ID_PATTERN.fullmatch(identity) is None
            or type(created) not in (int, float)):
        return None
    try:
        if not math.isfinite(created) or created <= 0:
            return None
    except OverflowError:
        return None
    files = value["files"]
    if not isinstance(files, dict) or not files:
        return None
    for name, item in files.items():
        try:
            public_name(name)
        except ValueError:
            return None
        if (not isinstance(item, dict) or set(item) != {"path", "sha256"}
                or not isinstance(item["path"], str) or not Path(item["path"]).is_absolute()
                or not isinstance(item["sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is None):
            return None
    return value


def artifact_dir() -> Path:
    root = prepare_cache() / "artifacts"
    safe_namespace(root, user_cache_dir())
    return root


def clean_artifact_records(now: float) -> None:
    """Expire historical registry records; shared cache cleanup also covers their recognized payloads."""
    for path in artifact_dir().glob("*.json"):
        if redirected(path) or not path.is_file():
            continue
        try:
            record = artifact_record(read_json(path), path.stem)
        except (OSError, ValueError):
            continue
        if record is not None and now - record["created_at"] >= RETENTION_SECONDS:
            path.unlink()



def load_artifact(identity: str) -> Optional[dict]:
    if ID_PATTERN.fullmatch(identity) is None:
        return None
    path = cache_dir() / "artifacts" / (identity + ".json")
    if redirected(path.parent):
        raise ValueError("artifact registry redirects")
    try:
        return artifact_record(read_json(path), identity)
    except FileNotFoundError:
        return None


def has_unexpired_artifacts(now: float) -> bool:
    for path in (cache_dir() / "artifacts").glob("*.json"):
        try:
            record = artifact_record(read_json(path), path.stem)
        except (OSError, ValueError):
            continue
        if record is not None and now - record["created_at"] < RETENTION_SECONDS:
            return True
    return False


def record_project(project: Path, harness: str, readiness: Optional[dict] = None) -> None:
    """Persist the latest owner-produced observation, never acquire evidence here."""
    if harness not in ("codex", "cursor", "copilot", "qoder"):
        raise ValueError("unknown web service harness")
    project = project.resolve(strict=True)
    identity = hashlib.sha256(os.path.normcase(str(project)).encode("utf-8")).hexdigest()
    root = prepare_cache() / "projects"
    safe_namespace(root, user_cache_dir())
    path = root / (identity + "-" + harness + ".json")
    existing = None
    if path.exists():
        existing = read_json(path)
        validate_project(existing, path.name)
        if readiness is None:
            return
    record = {"schema": PROJECT_SCHEMA, "id": identity, "project": str(project), "harness": harness,
              "observed_at": time.time(), "readiness": readiness if readiness is not None else (existing or {}).get("readiness")}
    validate_project(record, path.name)
    try:
        write_json(path, record, create_only=readiness is None)
    except FileExistsError:
        if readiness is not None:
            raise
        validate_project(read_json(path), path.name)


def validate_project(value: object, filename: str) -> None:
    if (not isinstance(value, dict) or set(value) != {"schema", "id", "project", "harness", "observed_at", "readiness"}
            or value.get("schema") != PROJECT_SCHEMA or not isinstance(value.get("project"), str)
            or not Path(value["project"]).is_absolute() or value.get("harness") not in ("codex", "cursor", "copilot", "qoder")
            or value.get("id") != hashlib.sha256(os.path.normcase(value["project"]).encode("utf-8")).hexdigest()
            or filename != value["id"] + "-" + value["harness"] + ".json"
            or type(value.get("observed_at")) not in (int, float) or not 0 < value["observed_at"] < 32503680000):
        raise ValueError("invalid web service project record: " + filename)
    observation = value["readiness"]
    if observation is None:
        return
    if (not isinstance(observation, dict) or set(observation) != {"status", "captured_at", "message", "findings"}
            or observation["status"] not in ("passed", "findings", "failed")
            or type(observation["captured_at"]) not in (int, float) or not 0 < observation["captured_at"] < 32503680000
            or not isinstance(observation["message"], str) or not isinstance(observation["findings"], list)):
        raise ValueError("invalid readiness snapshot: " + filename)
    for finding in observation["findings"]:
        if (not isinstance(finding, dict) or set(finding) != {"code", "tool", "message", "guidance"}
                or not all(isinstance(item, str) for item in finding.values())):
            raise ValueError("invalid readiness finding: " + filename)


def project_records() -> list:
    root = cache_dir() / "projects"
    if not root.exists():
        return []
    if redirected(root):
        raise ValueError("project registry redirects")
    records = []
    for path in sorted(root.glob("*.json")):
        value = read_json(path)
        validate_project(value, path.name)
        records.append(value)
    return records
