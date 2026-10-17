"""Human-review comparisons addressed entirely by URL parameters."""
from __future__ import annotations

import difflib
from dataclasses import replace
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Sequence
from urllib.parse import quote, urlsplit, urlunsplit

from .. import artifacts
from ..storage import prepare_state, redirected
from .presentation import icon, page
from .comparisons import (Comparison, Target, git, github_pr_url, pin_baseline, read_comparison, resolve_targets,
                          target_from_fields, target_from_query, validate_base)


class DiffPage(NamedTuple):
    content: bytes
    redirect: Optional[str] = None


def render_choices(target: Target, choices: Sequence[Target], *, html_only: bool = False) -> bytes:
    entries = ''.join('<li><a href="' + html.escape(choice.url(html_only=html_only), quote=True)
                      + '">' + html.escape(str(choice.repo)) + '</a></li>' for choice in choices)
    github = ('<p><a href="' + html.escape(target.github, quote=True) + '">查看 GitHub PR diff</a></p>') if target.github else ''
    return ('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>选择工作区</title>'
            '<style>body{font:16px system-ui;max-width:900px;margin:40px auto;padding:0 20px;overflow-wrap:anywhere}li{margin:16px 0}</style>'
            '<h1>' + html.escape(target.path) + '</h1><p>找到多个对应评审提交的工作区，请选择要查看的工作区。各工作区可能有不同的本地编辑。</p><ul>'
            + entries + '</ul>' + github + '</html>').encode('utf-8')


def render_page(target: Target, *, html_only: bool = False, automatic: bool = True) -> DiffPage:
    if target.head or target.base.startswith("commit:"):
        resolution = resolve_targets(target)
        if not resolution.targets:
            return DiffPage(b"", target.github)
        if len(resolution.targets) > 1:
            return DiffPage(render_choices(target, resolution.targets, html_only=html_only))
        target = resolution.targets[0]
    content = render_diff(read_comparison(target)) if html_only else render_open_page(target, automatic=automatic)
    return DiffPage(content)



def links(batch: object) -> List[Dict[str, str]]:
    """Validate a complete batch, then ensure one host without persisting link records."""
    if (not isinstance(batch, dict) or not {"repo", "files"} <= set(batch)
            or set(batch) - {"repo", "base", "pr", "files"}):
        raise ValueError("diff input needs repo, files, and optional base/pr context")
    entries = batch["files"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("files must be a nonempty JSON array")
    if "base" in batch:
        validate_base(batch["base"])
    pr = batch.get("pr")
    if "pr" in batch and (not isinstance(pr, dict) or set(pr) != {"repository", "number", "head"}):
        raise ValueError("pr needs exactly repository, number, and the fixed reviewed head")
    github = github_pr_url(pr["repository"], pr["number"]) if pr is not None else None
    results = []  # type: List[Dict[str, str]]
    identities = set()
    for entry in entries:
        if (not isinstance(entry, dict) or not {"id", "path"} <= set(entry)
                or set(entry) - {"id", "path", "title", "base", "base_path", "github_anchor"}):
            raise ValueError("file needs id, path, and optional title/base/base_path/github_anchor")
        identity, title = entry["id"], entry.get("title", entry["path"])
        if not all(isinstance(value, str) and value and not any(ord(c) < 32 for c in value) for value in (identity, title)):
            raise ValueError("diff id and title must be nonempty single lines")
        if identity in identities:
            raise ValueError("duplicate diff id")
        identities.add(identity)
        fields = {"repo": batch["repo"], "path": entry["path"], "base": entry.get("base", batch.get("base"))}
        validate_base(fields["base"])
        if "base_path" in entry:
            fields["base_path"] = entry["base_path"]
        if pr is not None:
            fields.update(github=github, head=pr["head"])
        if "github_anchor" in entry:
            anchor = entry["github_anchor"]
            if pr is None or not isinstance(anchor, str) or re.fullmatch(r"diff-[A-Za-z0-9_-]+", anchor) is None:
                raise ValueError("github_anchor needs PR context and an observed diff- fragment without #")
            fields["github"] += "#" + anchor
        target = target_from_fields(fields)
        if target.github and "github_anchor" not in entry:
            # GitHub's file fragment hashes the current UTF-8 path, not base_path.
            target = replace(target, github=target.github + "#diff-" + hashlib.sha256(target.path.encode("utf-8")).hexdigest())
        resolution = resolve_targets(target)
        if len(resolution.targets) == 1:
            target = resolution.targets[0]
        label = re.sub(r"([\\`*\[\]])", r"\\\1", html.escape(title, quote=False)).replace("_", "&#95;")
        result = {"id": identity, "title": title, "url": target.url(),
                  "markdown": "[" + label + "](" + target.url() + ")"}
        results.append(result)
    from ..service import ensure_service
    ensure_service()
    return results


def describe(content: Optional[bytes]) -> str:
    if content is None:
        return "不存在"
    crlf = content.count(b"\r\n")
    ending = "有末尾换行" if content.endswith((b"\n", b"\r")) else "无末尾换行"
    return "%d 字节；CRLF %d，LF %d，CR %d；%s" % (
        len(content), crlf, content.count(b"\n") - crlf, content.count(b"\r") - crlf, ending)


def render_diff(comparison: Comparison) -> bytes:
    before = comparison.before.decode("utf-8") if comparison.before is not None else ""
    after = comparison.after.decode("utf-8") if comparison.after is not None else ""
    table = difflib.HtmlDiff(tabsize=4, wrapcolumn=120).make_table(
        before.splitlines(), after.splitlines(), fromdesc="评审基线", todesc="当前工作区", context=False)
    newline_note = ("<p>仅换行符或文件末尾换行发生变化。</p>"
                    if before != after and before.splitlines() == after.splitlines() else "")
    title = html.escape(comparison.target.path)
    return ("<!doctype html><html lang=\"zh-CN\"><meta charset=\"utf-8\">"
            "<title>" + title + " · Diff</title>"
            "<style>body{font:14px system-ui;margin:24px;background:#fafafa;color:#202124}"
            "h1{font-size:20px}table.diff{border-collapse:collapse;width:100%;font:13px monospace}"
            "td,th{padding:3px 8px;vertical-align:top}.diff_header{background:#e8ebef}"
            ".diff_add{background:#d6f5dd}.diff_sub{background:#ffd9d9}"
            ".diff_chg{background:#fff0b3}.diff_next{background:#eee}a{color:#245ec7}</style>"
            "<h1>" + title + "</h1><p>固定评审基线 → 当前工作区</p>"
            "<p>评审基线：" + describe(comparison.before) + "<br>当前工作区：" + describe(comparison.after)
            + "</p>" + newline_note + "<div style=\"overflow:auto\">" + table + "</div></html>").encode("utf-8")


def render_open_page(target: Target, *, automatic: bool = True) -> bytes:
    github = ('<a class="github-link" href="' + html.escape(target.github, quote=True) + '">'
              + icon("external") + '查看 GitHub PR diff</a>') if target.github else ""
    endpoint = "/api/diff/open?" + target.query()
    encoded = json.dumps(endpoint).replace("<", "\\u003c")
    initial = "正在尝试打开 VS Code…" if automatic else "点击按钮尝试打开 VS Code，或选择网页 diff。"
    body = ('<div id="opening"' + (' class="is-opening"' if automatic else '') + '>'
            '<div class="opening-heading"><span class="spinner" aria-hidden="true"'
            + ('' if automatic else ' hidden') + '></span><h1 id="opening-title">'
            + ('正在打开 VS Code' if automatic else '打开文件对比') + '</h1></div>'
            '<p id="status" class="opening-status" role="status" aria-live="polite">' + initial + '</p>'
            '<div class="file-context">' + icon("file") + '<div><p class="file-path">'
            + html.escape(target.path) + '</p><p class="project-name">' + html.escape(target.repo.name)
            + '</p></div></div><div class="actions"><button id="open" class="button primary" type="button">'
            '<span class="spinner" aria-hidden="true" hidden></span><span id="open-label">打开 VS Code</span></button>'
            '<a class="button" href="' + html.escape(target.url(html_only=True), quote=True) + '">'
            + icon("browser") + '在网页中查看</a></div>' + github
            + '<footer class="closing-note">' + icon("info") + '<div><p>请求发出后将尝试自动关闭本页。</p>'
            '<p>若页面未关闭，可使用上方网页入口查看。</p></div></footer></div>'
            '<script>const automatic=' + ('true' if automatic else 'false') + ';let started=false;async function openDiff(){if(started||document.prerendering||document.visibilityState!=="visible"||window.top!==window.self)return;started=true;document.getElementById("open").disabled=true;'
            'document.getElementById("opening").classList.add("is-opening");document.querySelectorAll(".spinner").forEach(item=>item.hidden=false);document.getElementById("open-label").textContent="正在打开…";document.getElementById("opening-title").textContent="正在打开 VS Code";'
            'try{const response=await fetch(' + encoded + ',{method:"POST",credentials:"omit"});const result=await response.json();'
            'document.getElementById("status").textContent=result.message;'
            'if(response.ok&&result.url)location.replace(result.url);'
            'else if(response.ok&&result.viewer==="vscode"){document.getElementById("opening-title").textContent="已发送打开请求";document.getElementById("open-label").textContent="已发送请求";window.close();}'
            'else{document.getElementById("opening-title").textContent="打开请求未完成";document.getElementById("open-label").textContent="请求未完成";}'
            '}catch(error){document.getElementById("status").textContent="启动请求未完成，请使用下方入口查看 diff。";document.getElementById("opening-title").textContent="打开请求未完成";document.getElementById("open-label").textContent="请求未完成";}'
            'finally{document.getElementById("opening").classList.remove("is-opening");document.querySelectorAll(".spinner").forEach(item=>item.hidden=true);}}'
            'document.getElementById("open").addEventListener("click",openDiff);if(automatic){document.addEventListener("prerenderingchange",openDiff);document.addEventListener("visibilitychange",openDiff);openDiff();}</script>')
    return page("打开 Diff", body, label="文件对比", compact=True)


def find_vscode() -> Optional[Path]:
    for name in ("code", "code-insiders"):
        candidate = shutil.which(name)
        if candidate:
            path = Path(candidate)
            if sys.platform != "win32" or path.suffix.lower() == ".exe":
                return path
            # Avoid passing user paths through Windows batch-file interpretation.
            for executable in ("Code.exe", "Code - Insiders.exe"):
                native = path.parent.parent / executable
                if native.is_file():
                    return native
    if sys.platform == "win32":
        for variable in ("LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)"):
            value = os.environ.get(variable)
            if value:
                root = Path(value) / ("Programs" if variable == "LOCALAPPDATA" else "")
                for directory, executable in (("Microsoft VS Code", "Code.exe"), ("Microsoft VS Code Insiders", "Code - Insiders.exe")):
                    native = root / directory / executable
                    if native.is_file():
                        return native
    elif sys.platform == "darwin":
        for root in (Path("/Applications"), Path.home() / "Applications"):
            for name in ("Visual Studio Code", "Visual Studio Code - Insiders"):
                native = root / (name + ".app") / "Contents/Resources/app/bin/code"
                if native.is_file():
                    return native
    return None


def git_base_uri(comparison: Comparison) -> Optional[str]:
    """Use the built-in Git provider only when it reproduces the pinned blob."""
    target = comparison.target
    if not target.base_commit or comparison.before is None:
        return None
    name = target.base_path or target.path
    try:
        history = target.repo.resolve(strict=True)
        for part in name.split("/"):
            history /= part
            if redirected(history):
                return None
        committed = pin_baseline(replace(target, base="commit:" + target.base_commit, base_commit=None))
        if committed.base != target.base or git(target.repo, "replace", "-l").strip():
            return None
        attributes = git(target.repo, "check-attr", "-z", "diff", "--", name).split(b"\0")
        if len(attributes) != 4 or attributes[1] != b"diff":
            return None
        driver = os.fsdecode(attributes[2])
        # VS Code runs textconv; keep converters and their cache writes off the fixed-blob path.
        if driver not in ("unspecified", "set", "unset") and git(
                target.repo, "config", "--get", "--default", "", "diff." + driver + ".textconv").strip():
            return None
    except (OSError, ValueError):
        return None
    query = quote(json.dumps({"path": str(history), "ref": target.base_commit}, ensure_ascii=False), safe="")
    return urlunsplit(("git", "", urlsplit(history.as_uri()).path, query, ""))


def open_editor(target: Target) -> Dict[str, str]:
    """Dispatch a fixed launcher, or return the contracted GitHub/HTML fallback."""
    if target.head or target.base.startswith("commit:"):
        resolution = resolve_targets(target)
        if not resolution.targets:
            return {"viewer": "web", "url": target.github, "message": resolution.message + "正在打开 GitHub diff。"}
        if len(resolution.targets) > 1:
            return {"viewer": "web", "url": target.url(), "message": "请选择要查看的工作区。"}
        target = resolution.targets[0]
    fallback = target.github or target.url(html_only=True)
    try:
        comparison = read_comparison(target)
    except (OSError, ValueError) as error:
        if target.github:
            return {"viewer": "web", "url": target.github, "message": "本地比较不可用，转到 GitHub：" + str(error)}
        raise
    launcher = find_vscode()
    if launcher is None:
        return {"viewer": "web", "url": fallback, "message": "未找到 VS Code，正在打开网页 diff。"}
    suffix = Path(target.path).suffix
    try:
        before_uri = git_base_uri(comparison)
        payloads = {}  # type: Dict[str, bytes]
        if before_uri is None:
            payloads["before" + suffix] = comparison.before or b""
        if comparison.after is None:
            payloads["after" + suffix] = b""
        after = comparison.worktree_file
        if payloads:
            captured = artifacts.create_artifact(payloads)
            if before_uri is None:
                before = captured.files["before" + suffix].path
            if comparison.after is None:
                after = captured.files["after" + suffix].path
        if before_uri is None:
            arguments = [str(before), str(after)]
        else:
            # Windows Chromium filters standalone URL arguments before VS Code parses them.
            arguments = ["--file-uri=" + before_uri, "--file-uri=" + after.as_uri()]
        environment = dict(os.environ)
        environment.pop("ELECTRON_RUN_AS_NODE", None)
        log_path = prepare_state() / "vscode-launch.log"
        if redirected(log_path):
            raise ValueError("editor launch log redirects")
        descriptor = os.open(str(log_path), os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "wb") as log:
            process = subprocess.Popen([str(launcher), "--reuse-window", "--diff"] + arguments,
                                       env=environment, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                       start_new_session=True)
            try:
                status = process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                status = None
                threading.Thread(target=process.wait, daemon=True).start()
        if status not in (None, 0):
            raise OSError("VS Code launcher exited with status " + str(status))
    except (OSError, ValueError) as error:
        return {"viewer": "web", "url": fallback, "message": "VS Code 启动失败，正在打开网页 diff：" + str(error)}
    return {"viewer": "vscode", "message": "已向 VS Code 发送 diff 请求；如果未显示，请使用下方网页入口。"}
