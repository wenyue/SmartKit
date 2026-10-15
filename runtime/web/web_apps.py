"""Read-only views of owner-produced readiness observations and setup evidence."""
from __future__ import annotations

import html
import sys
import time
from pathlib import Path
from typing import Dict, List, Mapping
from urllib.parse import quote

from web_store import project_records


SOURCE_ROOT = Path(__file__).resolve().parents[2]


def hook_page_links(project: Path, harness: str, urls: Mapping[str, str]) -> Dict[str, str]:
    """Offer existing status views for recorded findings, without another check."""
    selected = {}
    for record in project_records():
        if record["project"] != str(project.resolve()) or record["harness"] != harness:
            continue
        observation = record.get("readiness")
        if observation is None or observation["status"] not in ("findings", "failed"):
            continue
        selected["最近一次就绪检查详情"] = urls["readiness"]
        if any(item["code"] == "setup-required" for item in observation["findings"]):
            selected["项目设置与迁移状态"] = urls["setup"]
    return selected


def setup_snapshot(project: Path) -> dict:
    """Use the setup owner's readers; never run setup, synchronization, or tool checks."""
    scripts = SOURCE_ROOT / "skills/setup-project-agents/scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from agents_setup.catalog import load_catalog
    from agents_setup.migrations import SetupStatus, applicable_migrations, project_setup_version
    from agents_setup.models import ContractError
    from agents_setup.project import ProjectError

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
    nav = '<a href="/apps/readiness/' + access + '">就绪检查</a> · <a href="/apps/setup/' + access + '">项目设置</a>'
    rows = []
    for project in data["projects"]:
        identity = html.escape(project["project"])
        if feature == "readiness":
            observation = project["readiness"]
            status = {"passed": "检查通过", "findings": "存在待处理发现", "failed": "检查失败", "unavailable": "证据不可用"}.get(observation.get("status"), "证据不可用")
            captured = observation.get("captured_at")
            stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(captured)) if isinstance(captured, (int, float)) else "未知"
            parts = ['<h3>' + html.escape(status) + '</h3><p>宿主：' + html.escape(project["harness"]) + '；采集时间：' + stamp + '</p>']
            if observation.get("message"):
                parts.append('<p>' + html.escape(str(observation["message"])) + '</p>')
            parts.append('<ul>')
            for finding in observation.get("findings", []):
                parts.append('<li><strong>' + html.escape(str(finding.get("tool", ""))) + '</strong>：' + html.escape(str(finding.get("message", ""))) + '<br>' + html.escape(str(finding.get("guidance", ""))) + '</li>')
            parts.append('</ul>')
            body = "".join(parts)
        else:
            setup = project["setup"]
            status = {"uninitialized": "尚未初始化", "baseline-required": "缺少已完成设置的版本基线", "initialized": "已有设置基线", "failed": "状态读取失败"}.get(setup["status"], setup["status"])
            body = '<h3>' + html.escape(status) + '</h3>'
            if setup["status"] == "failed":
                body += '<p>' + html.escape(setup["message"]) + '</p>'
            else:
                body += '<p>成功设置版本：' + html.escape(setup["setup_version"] or "未建立") + '；插件版本：' + html.escape(setup["plugin_version"]) + '</p>'
                guides = setup["migrations"]
                if guides:
                    label = "声明的必要迁移" if setup["status"] == "initialized" else "可供设置流程评估的迁移声明"
                    body += '<p>' + label + '：</p><ul>' + "".join('<li>' + html.escape(item["version"] + " — " + item["guide"]) + '</li>' for item in guides) + '</ul>'
                else:
                    body += '<p>当前没有适用的迁移声明。</p>'
        rows.append('<section><h2>' + identity + '</h2>' + body + '</section>')
    empty = '<p>尚无项目记录。启动或恢复项目中的 Agent 会话后刷新此页。</p>'
    return ('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>' + title + '</title>'
            '<style>body{font:15px system-ui;max-width:1100px;margin:30px auto;padding:0 20px;color:#202124}section{border:1px solid #ccd3db;border-radius:8px;padding:18px;margin:18px 0}h2{font-size:18px;overflow-wrap:anywhere}li{margin:10px 0}a{color:#245ec7}</style>'
            '<nav>' + nav + '</nav><h1>' + title + '</h1><p>只读视图。刷新仅重新读取记录，不运行检查、安装、修复或迁移。检查发现已显示不等于已修复；静态 MCP 就绪不等于运行健康。</p>'
            + ("".join(rows) or empty) + '</html>').encode("utf-8")
