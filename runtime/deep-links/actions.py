"""Fixed-snapshot viewers shared by every SmartKit link producer."""
from __future__ import annotations

import difflib
import html
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Mapping

import registration


ARTIFACT_SUFFIXES = {'.html', '.htm', '.pdf', '.txt', '.md', '.svg', '.png', '.jpg', '.jpeg'}
VIEWERS = {'auto', 'vscode', 'web'}


@dataclass(frozen=True)
class Task:
    id: str
    action: Literal['diff', 'artifact']
    title: str
    before: Path | None = None
    after: Path | None = None
    path: Path | None = None
    viewer: Literal['auto', 'vscode', 'web'] = 'auto'


def prepare_task(item: Mapping[str, object], base: Path, viewer: str) -> Task:
    """Validate action-owned fields before a batch begins creating snapshots."""
    identity, action = item['id'], item.get('action', 'diff')
    if not isinstance(identity, str) or not isinstance(action, str) or action not in HANDLERS:
        raise ValueError('invalid task identity or action')
    allowed = {'id', 'action', 'title', 'before', 'after', 'viewer'} if action == 'diff' else {'id', 'action', 'title', 'path'}
    if set(item) - allowed:
        raise ValueError(f'unknown fields in task {identity}')

    def resolve(key: str) -> Path | None:
        value = item.get(key)
        if value is None:
            return None
        if not isinstance(value, str) or not value:
            raise ValueError(f'{key} must be a nonempty path or null')
        path = (base / value).resolve(strict=True)
        if not path.is_file():
            raise ValueError(f'{key} must be a file')
        return path

    before, after, path = resolve('before'), resolve('after'), resolve('path')
    if action == 'diff' and before is None and after is None:
        raise ValueError('a diff needs at least one existing side')
    if action == 'artifact' and (path is None or path.suffix.lower() not in ARTIFACT_SUFFIXES):
        raise ValueError('artifact must be a supported report, text, or image file')
    selected = item.get('viewer', viewer)
    if not isinstance(selected, str) or selected not in VIEWERS:
        raise ValueError('viewer must be auto, vscode, or web')
    title = item.get('title', (after or before or path).name)
    if not isinstance(title, str) or not title or '\n' in title or '\r' in title:
        raise ValueError('title must be a nonempty single line')
    return Task(identity, action, title, before, after, path, selected)


def _suffix(path: Path | None) -> str:
    suffix = path.suffix if path else ''
    if len(suffix) > 32 or any(character in suffix for character in '/\\\n\r'):
        raise ValueError('unsupported snapshot file extension')
    return suffix


def snapshot(folder: Path, task: Task) -> dict[str, str]:
    record = {'id': task.id, 'action': task.action, 'title': task.title}
    if task.action == 'diff':
        texts: list[str] = []
        for side, path in (('before', task.before), ('after', task.after)):
            content = path.read_bytes() if path else b''
            texts.append(content.decode('utf-8'))
            name = side + _suffix(path or task.after or task.before)
            (folder / name).write_bytes(content)
            record[side] = name
        record.update(viewer=task.viewer, preview='diff.html')
        (folder / 'diff.html').write_text(render_diff(*texts, task.title), encoding='utf-8')
    else:
        if task.path is None:
            raise ValueError('artifact path is required')
        name = 'artifact' + _suffix(task.path)
        shutil.copyfile(task.path, folder / name)
        record['preview'] = name
    return record


def validate_record(action: str, record: object) -> dict[str, str]:
    fields = {'id', 'action', 'title', 'before', 'after', 'viewer', 'preview'} if action == 'diff' else {'id', 'action', 'title', 'preview'}
    if (not isinstance(record, dict) or set(record) != fields
            or not all(isinstance(value, str) for value in record.values())
            or record.get('action') != action):
        raise ValueError('invalid task record; the stored snapshot was preserved')
    if action == 'diff':
        if record['viewer'] not in VIEWERS or record['preview'] != 'diff.html':
            raise ValueError('invalid stored diff viewer or preview')
    elif Path(record['preview']).suffix.lower() not in ARTIFACT_SUFFIXES:
        raise ValueError('unsupported stored artifact')
    return record


def render_diff(before: str, after: str, title: str) -> str:
    comparison = difflib.HtmlDiff(tabsize=4, wrapcolumn=120).make_table(
        before.splitlines(), after.splitlines(),
        fromdesc='修改前', todesc='修改后', context=False)
    newline_note = ('<p>仅换行符或文件末尾换行发生变化；前后快照保留原始字节。</p>'
                    if before != after and before.splitlines() == after.splitlines() else '')
    return ('<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
            f'<title>{html.escape(title)} · SmartKit Diff</title>'
            '<style>body{font:14px system-ui;margin:24px;background:#fafafa;color:#202124}'
            'h1{font-size:20px}table.diff{border-collapse:collapse;width:100%;font:13px monospace}'
            'td,th{padding:3px 8px;vertical-align:top}.diff_header{background:#e8ebef}'
            '.diff_add{background:#d6f5dd}.diff_sub{background:#ffd9d9}'
            '.diff_chg{background:#fff0b3}.diff_next{background:#eee}'
            'a{color:#245ec7}</style>'
            f'<h1>{html.escape(title)}</h1><p>固定快照 · 左侧修改前，右侧修改后</p>'
            f'{newline_note}<div style="overflow:auto">{comparison}</div></html>')


def find_vscode() -> Path | None:
    for name in ('code', 'code-insiders'):
        candidate = shutil.which(name)
        if candidate:
            path = Path(candidate)
            if sys.platform != 'win32' or path.suffix.lower() == '.exe':
                return path
            for executable in ('Code.exe', 'Code - Insiders.exe'):
                native = path.parent.parent / executable
                if native.is_file():
                    return native
    if sys.platform == 'win32':
        for base in ('LOCALAPPDATA', 'ProgramFiles', 'ProgramFiles(x86)'):
            value = os.environ.get(base)
            if value:
                root = Path(value) / ('Programs' if base == 'LOCALAPPDATA' else '')
                for directory, executable in (('Microsoft VS Code', 'Code.exe'),
                                               ('Microsoft VS Code Insiders', 'Code - Insiders.exe')):
                    path = root / directory / executable
                    if path.is_file():
                        return path
    elif sys.platform == 'darwin':
        for root in (Path('/Applications'), Path.home() / 'Applications'):
            for name in ('Visual Studio Code', 'Visual Studio Code - Insiders'):
                path = root / (name + '.app') / 'Contents/Resources/app/bin/code'
                if path.is_file():
                    return path
    return None


def open_diff(folder: Path, record: Mapping[str, str], environment: Mapping[str, str]) -> dict[str, str]:
    viewer = record['viewer']
    preview = folder / record['preview']
    warning = ''
    if viewer != 'web':
        launcher = find_vscode()
        if launcher is None:
            warning = '未找到 VS Code'
        else:
            command = [str(launcher), '--reuse-window', '--diff',
                       str(folder / record['before']), str(folder / record['after'])]
            launch_environment = dict(environment)
            # Native Electron launchers must open VS Code rather than inherit a host's Node mode.
            launch_environment.pop('ELECTRON_RUN_AS_NODE', None)
            try:
                with (folder / 'vscode-launch.log').open('wb') as log:
                    process = subprocess.Popen(command, env=launch_environment, stdin=subprocess.DEVNULL,
                                               stdout=log, stderr=log, start_new_session=True)
                    try:
                        status = process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        status = None
                if status not in (None, 0):
                    raise OSError(f'VS Code 启动进程退出，状态码 {status}')
                return {'viewer': 'vscode', 'message': '已向 VS Code 最近使用的窗口发送 diff 请求'}
            except OSError as error:
                warning = str(error)
        if viewer == 'vscode':
            # An explicit viewer choice remains visible even when a web recovery is offered.
            failure = folder / 'open-error.html'
            failure.write_text('<!doctype html><meta charset="utf-8"><title>SmartKit Links</title>'
                               f'<h1>无法打开 VS Code</h1><p>{html.escape(warning)}</p>'
                               f'<a href="{html.escape(preview.as_uri(), quote=True)}">查看网页 diff</a>',
                               encoding='utf-8')
            registration.open_file(failure, environment)
            raise OSError(warning + '; 已提供网页查看入口')
    registration.open_file(preview, environment)
    return {'viewer': 'web', 'message': '已发送网页 diff 打开请求', 'warning': warning}


def open_artifact(folder: Path, record: Mapping[str, str], environment: Mapping[str, str]) -> dict[str, str]:
    registration.open_file(folder / record['preview'], environment)
    return {'viewer': 'default', 'message': '已向系统默认查看器发送报告打开请求'}


HANDLERS = {'diff': open_diff, 'artifact': open_artifact}
