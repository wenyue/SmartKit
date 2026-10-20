"""Read-only views of owner-produced readiness observations and setup evidence."""
from __future__ import annotations

import html
import sys
import time
from pathlib import Path
from typing import Dict, List, Mapping, Optional
from urllib.parse import quote

import hashlib
import os
from ..storage import user_cache_dir, safe_namespace, redirected, read_json, write_json
from .presentation import icon, page


SOURCE_ROOT = Path(__file__).resolve().parents[3]
PROJECT_SCHEMA = "smartkit.preview-project/v1"

def cache_dir() -> Path:
    # Project observations are independently owned, not disposable preview data.
    return user_cache_dir() / "smartkit/preview"

def prepare_cache() -> Path:
    base = user_cache_dir()
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    safe_namespace(cache_dir(), base)
    return cache_dir()


def hook_page_links(project: Path, harness: str, urls: Mapping[str, str]) -> Dict[str, str]:
    """Offer existing status views for recorded findings, without another check."""
    selected = {}
    for record in project_records():
        if record["project"] != str(project.resolve()) or record["harness"] != harness:
            continue
        observation = record.get("readiness")
        if observation is None or observation["status"] not in ("findings", "failed"):
            continue
        selected["最近一次就绪检查详情"] = urls["readiness"].replace("/?", "/" + record["id"] + "?")
        if any(item["code"] == "setup-required" for item in observation["findings"]):
            selected["项目设置与迁移状态"] = urls["setup"].replace("/?", "/" + record["id"] + "?")
    return selected


def setup_snapshot(project: Path) -> dict:
    """Read project evidence without running setup, synchronization, or tool checks."""
    runtime = SOURCE_ROOT / "runtime"
    if str(runtime) not in sys.path:
        sys.path.insert(0, str(runtime))
    from project_state.migrations import SetupStatus, applicable_migrations, project_setup_version
    from project_state.catalog import load_catalog
    from project_state.models import ContractError
    from project_state.paths import ProjectError

    try:
        if not project.is_dir():
            raise ValueError("project directory is unavailable")
        status = project_setup_version(project, SOURCE_ROOT)
        baseline = None if isinstance(status, SetupStatus) else status.version
        migrations = applicable_migrations(SOURCE_ROOT, baseline)
        return {"status": status.value if isinstance(status, SetupStatus) else "initialized",
                "setup_version": baseline, "plugin_version": load_catalog(SOURCE_ROOT).plugin_version,
                "migrations": [{"version": item.version, "guide": item.guide} for item in migrations]}
    except (OSError, ValueError, ContractError, ProjectError) as error:
        return {"status": "failed", "message": str(error)}


def application_data(feature: str, project_id: str = "") -> dict:
    records = project_records()
    if project_id:
        records = [record for record in records if record["id"] == project_id]
        if not records:
            raise FileNotFoundError("project has not been registered by a SmartKit Hook")
    projects = []  # type: List[dict]
    if feature == "readiness":
        for record in records:
            observation = record.get("readiness")
            if observation is None:
                observation = {"status": "unavailable", "message": "尚无完整检查快照；每日关口的日期记录不能证明检查通过。"}
            projects.append({"id": record["id"], "project": record["project"], "harness": record["harness"],
                             "readiness": observation})
    elif feature == "setup":
        seen = set()
        for record in records:
            if record["id"] in seen:
                continue
            seen.add(record["id"])
            projects.append({"id": record["id"], "project": record["project"],
                             "setup": setup_snapshot(Path(record["project"]))})
    else:
        raise FileNotFoundError("unknown SmartKit application")
    return {"feature": feature, "read_at": time.time(), "projects": projects}


def render_application(feature: str, key: str, data: dict) -> bytes:
    title = "项目就绪状态" if feature == "readiness" else "项目设置状态"
    access = "?key=" + quote(key, safe="")
    nav = '<nav class="tabs" aria-label="项目状态">' + ''.join(
        '<a href="/' + name + '/' + access + '"' + (' aria-current="page"' if name == feature else '')
        + '>' + text + '</a>' for name, text in (("readiness", "就绪检查"), ("setup", "项目设置"))) + '</nav>'
    rows = []
    for project in data["projects"]:
        identity = html.escape(project["project"])
        if feature == "readiness":
            observation = project["readiness"]
            status = {"passed": "检查通过", "findings": "存在待处理发现", "failed": "检查失败", "unavailable": "证据不可用"}.get(observation.get("status"), "证据不可用")
            tone, symbol = {"passed": ("success", "check"), "findings": ("warning", "warning"),
                            "failed": ("danger", "warning")}.get(observation.get("status"), ("muted", "info"))
            captured = observation.get("captured_at")
            stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(captured)) if isinstance(captured, (int, float)) else "未知"
            parts = ['<p class="metadata"><span>宿主：' + html.escape(project["harness"])
                     + '</span><span>采集时间：' + stamp + '</span></p>']
            if observation.get("message"):
                parts.append('<p class="message">' + html.escape(str(observation["message"])) + '</p>')
            parts.append('<ul class="findings">')
            for finding in observation.get("findings", []):
                parts.append('<li class="finding"><h3>' + html.escape(str(finding.get("tool", "")))
                             + '</h3><p>' + html.escape(str(finding.get("message", "")))
                             + '</p><p class="guidance">' + html.escape(str(finding.get("guidance", ""))) + '</p></li>')
            parts.append('</ul>')
            body = "".join(parts)
        else:
            setup = project["setup"]
            status = {"uninitialized": "尚未初始化", "baseline-required": "缺少已完成设置的版本基线", "initialized": "已有设置基线", "failed": "状态读取失败"}.get(setup["status"], setup["status"])
            tone, symbol = {"initialized": ("info", "info"), "failed": ("danger", "warning"),
                            "baseline-required": ("warning", "warning")}.get(setup["status"], ("muted", "info"))
            body = ''
            if setup["status"] == "failed":
                body += '<p class="message">' + html.escape(setup["message"]) + '</p>'
            else:
                body += ('<dl class="versions"><div><dt>成功设置版本</dt><dd class="mono">'
                         + html.escape(setup["setup_version"] or "未建立")
                         + '</dd></div><div><dt>插件版本</dt><dd class="mono">'
                         + html.escape(setup["plugin_version"]) + '</dd></div></dl>')
                guides = setup["migrations"]
                if guides:
                    label = "声明的必要迁移" if setup["status"] == "initialized" else "可供设置流程评估的迁移声明"
                    body += ('<p class="migration-label">' + icon("warning") + label
                             + '</p><ul class="migrations">' + "".join('<li><span>' + html.escape(item["version"])
                             + '</span><span>' + html.escape(item["guide"]) + '</span></li>' for item in guides) + '</ul>')
                else:
                    body += '<p class="message">当前没有适用的迁移声明。</p>'
        rows.append('<section class="project-card"><div class="project-heading"><h2>' + identity
                    + '</h2><span class="badge ' + tone + '">' + icon(symbol) + html.escape(status)
                    + '</span></div>' + body + '</section>')
    empty = '<p class="empty">尚无项目记录。启动或恢复项目中的 Agent 会话后刷新此页。</p>'
    body = ('<h1>' + title + '</h1><aside class="notice">' + icon("info")
            + '<div><p>只读视图。刷新仅重新读取记录，不运行检查、安装、修复或迁移。</p>'
            '<p>检查发现已显示不等于已修复；静态 MCP 就绪不等于运行健康。</p></div></aside>'
            + ("".join(rows) or empty))
    return page(title, body, label="项目状态", navigation=nav)


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
