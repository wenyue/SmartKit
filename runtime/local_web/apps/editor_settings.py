"""Install the bundled VS Code bridge into an explicitly selected profile."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
from typing import List, Optional, Tuple
from urllib.parse import urlencode

from .diff import find_vscode
from .presentation import page


EXTENSION_ID = "wenyue.smartkit-diff-bridge"
RUNTIME_DIR = Path(__file__).resolve().parents[1]
VSIX = RUNTIME_DIR / "smartkit-diff-bridge.vsix"
_INSTALL_LOCK = threading.Lock()


def _version(value: str) -> Tuple[int, ...]:
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value):
        raise OSError("无法确认 Diff Bridge 的版本。")
    return tuple(int(part) for part in value.split("."))


def _code(launcher: Path, arguments: List[str], *, failure: str) -> str:
    command = [str(launcher)]
    environment = dict(os.environ)
    environment.pop("ELECTRON_RUN_AS_NODE", None)
    if sys.platform == "win32":
        # Use the native executable and the same CLI entry as the Windows launcher.
        entry = launcher.parent / "resources" / "app" / "out" / "cli.js"
        if not entry.is_file():
            raise OSError("找不到 VS Code 命令行入口。")
        command.append(str(entry))
        environment["ELECTRON_RUN_AS_NODE"] = "1"
    try:
        result = subprocess.run(command + arguments, env=environment, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                encoding="utf-8", errors="replace", timeout=30, check=True)
    except subprocess.TimeoutExpired as error:
        raise OSError("VS Code 命令超时。请在 VS Code 中确认扩展状态后重试。") from error
    except (OSError, subprocess.CalledProcessError) as error:
        raise OSError(failure) from error
    return result.stdout


def _installed(launcher: Path, profile: str) -> Optional[str]:
    output = _code(launcher, ["--profile", profile, "--list-extensions", "--show-versions"],
                   failure="无法读取目标 VS Code 配置。请确认配置名称与当前仓库窗口一致。")
    for line in output.splitlines():
        identity, separator, version = line.strip().partition("@")
        if identity.lower() == EXTENSION_ID:
            if not separator:
                raise OSError("无法确认目标配置中 Diff Bridge 的版本。")
            return version
    return None


def install(profile: str) -> dict:
    """Return installation evidence for the selected profile; activation is a separate check."""
    profile = profile.strip()
    if not profile or len(profile) > 128 or profile.startswith("-") or not profile.isprintable():
        raise ValueError("请输入现有 VS Code 配置的名称。")
    launcher = find_vscode()
    if launcher is None:
        raise OSError("找不到 VS Code 桌面版。")
    bundled = json.loads((RUNTIME_DIR / "vscode" / "package.json").read_text(encoding="utf-8"))["version"]
    with _INSTALL_LOCK:
        installed = _installed(launcher, profile)
        if installed is not None and _version(installed) >= _version(bundled):
            return {"profile": profile, "version": installed, "status": "already-installed"}
        if not VSIX.is_file():
            raise OSError("当前 SmartKit 安装包缺少 Diff Bridge 的 VSIX。")
        _code(launcher, ["--profile", profile, "--install-extension", str(VSIX)],
              failure="VS Code 未完成安装。请检查该配置的扩展权限。")
        installed = _installed(launcher, profile)
        if installed is None or _version(installed) < _version(bundled):
            raise OSError("VS Code 返回后未能确认目标配置中的安装版本。")
        return {"profile": profile, "version": installed, "status": "installed"}


def render_settings(key: str) -> bytes:
    endpoint = json.dumps("/api/editor/install?" + urlencode({"key": key}))
    body = (
        '<h1>编辑器设置</h1>'
        '<p>安装 SmartKit Diff Bridge 后，VS Code 可以直接从 Git 历史打开对比左侧。</p>'
        '<section class="project-card"><h2>启用 Git 基线对比</h2>'
        '<p class="message">填写仓库窗口当前使用的 VS Code 配置名。默认配置请填 Default。</p>'
        '<form id="bridge-install"><label for="profile">目标 VS Code 配置</label> '
        '<input id="profile" name="profile" required maxlength="128" placeholder="例如 OtakuRoom">'
        '<div class="actions"><button class="button primary" type="submit">安装或更新 Diff Bridge</button></div>'
        '</form><p id="result" class="message" role="status" aria-live="polite"></p></section>'
        '<script>const form=document.getElementById("bridge-install");'
        'const profile=document.getElementById("profile");const button=form.querySelector("button");'
        'const status=document.getElementById("result");'
        'form.addEventListener("submit",async event=>{event.preventDefault();'
        'if(button.disabled)return;button.disabled=true;profile.disabled=true;status.textContent="正在检查并安装…";'
        'try{const response=await fetch(' + endpoint + '+"&profile="+encodeURIComponent(profile.value),'
        '{method:"POST",credentials:"omit"});const result=await response.json();'
        'status.textContent=response.ok?'
        'result.profile+(result.status==="installed"?" 已安装 ":" 已有 ")+result.version+'
        '"。请聚焦该仓库的 VS Code 窗口并重开原 diff 链接验证。若仍使用临时文件，请重载该窗口后重试。":'
        'result.message;}catch(error){status.textContent="安装结果未确认，请检查 VS Code 扩展列表。";}'
        'finally{profile.disabled=false;button.disabled=false;}});</script>'
    )
    return page("编辑器设置", body, label="编辑器设置", compact=True)
