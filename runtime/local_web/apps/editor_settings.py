"""Install the bundled VS Code bridge into an explicitly selected profile."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
from typing import List, Optional, Tuple
from urllib.parse import urlencode

from .presentation import page


EXTENSION_ID = "wenyue.smartkit-diff-bridge"
DEFAULT_PROFILE = "Default"
RUNTIME_DIR = Path(__file__).resolve().parents[1]
VSIX = RUNTIME_DIR / "smartkit-diff-bridge.vsix"
_INSTALL_LOCK = threading.Lock()


def find_vscode() -> Optional[Path]:
    for name in ("code", "code-insiders"):
        candidate = shutil.which(name)
        if candidate:
            path = Path(candidate)
            if sys.platform != "win32" or path.suffix.lower() == ".exe":
                return path
            # Invoke the executable directly so Windows never interprets user paths as batch commands.
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


def _version(value: str) -> Tuple[int, ...]:
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value):
        raise OSError("无法确认 Diff Bridge 的版本。")
    return tuple(int(part) for part in value.split("."))


def _windows_cli_entry(launcher: Path) -> Path:
    root = launcher.parent
    relative = Path("resources/app/out/cli.js")
    script = root / "bin" / ("code-insiders.cmd" if launcher.stem.lower().endswith("insiders") else "code.cmd")
    if script.is_file():
        # Updates can leave multiple commit directories. Use the one selected by the installed launcher.
        match = re.search(r'"%~dp0\.\.\\([0-9a-f]{10,40})\\resources\\app\\out\\cli\.js"',
                          script.read_text(encoding="utf-8-sig", errors="replace"), re.IGNORECASE)
        if match:
            relative = Path(match[1]) / relative
    entry = root / relative
    if not entry.is_file():
        raise OSError("找不到 VS Code 命令行入口。")
    return entry


def _code(launcher: Path, arguments: List[str], *, failure: str, timeout: int = 30) -> str:
    command = [str(launcher)]
    environment = dict(os.environ)
    environment.pop("ELECTRON_RUN_AS_NODE", None)
    if sys.platform == "win32":
        command.append(str(_windows_cli_entry(launcher)))
        environment.pop("VSCODE_DEV", None)
        environment["ELECTRON_RUN_AS_NODE"] = "1"
    try:
        result = subprocess.run(command + arguments, env=environment, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                encoding="utf-8", errors="replace", timeout=timeout, check=True)
    except subprocess.TimeoutExpired as error:
        raise OSError("VS Code 命令超时。请在 VS Code 中确认扩展状态后重试。") from error
    except (OSError, subprocess.CalledProcessError) as error:
        raise OSError(failure) from error
    return result.stdout


def installed_version(launcher: Path, profile: str = DEFAULT_PROFILE) -> Optional[str]:
    """Return the extension's version in the selected profile, or None after a successful absence check."""
    output = _code(launcher, ["--profile", profile, "--list-extensions", "--show-versions"],
                   failure="无法读取目标 VS Code 配置。请确认配置名称与当前仓库窗口一致。", timeout=5)
    for line in output.splitlines():
        identity, separator, version = line.strip().partition("@")
        if identity.lower() == EXTENSION_ID:
            if not separator:
                raise OSError("无法确认目标配置中 Diff Bridge 的版本。")
            _version(version)
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
        installed = installed_version(launcher, profile)
        if installed is not None and _version(installed) >= _version(bundled):
            return {"profile": profile, "version": installed, "status": "already-installed"}
        if not VSIX.is_file():
            raise OSError("当前 SmartKit 安装包缺少 Diff Bridge 的 VSIX。")
        _code(launcher, ["--profile", profile, "--install-extension", str(VSIX)],
              failure="VS Code 未完成安装。请检查该配置的扩展权限。")
        installed = installed_version(launcher, profile)
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
