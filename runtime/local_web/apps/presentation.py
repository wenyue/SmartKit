"""Shared, self-contained presentation for the local application's pages."""
from __future__ import annotations

import html


ICONS = {
    "brand": '<path d="M3 2h7l4 4v13H3zM10 2v5h4M6 10h5M6 14h4"/><path d="M14 8h4l3 3v11H11v-3M18 8v4h3M15 15h3M15 18h3"/>',
    "file": '<path d="M5 2h9l5 5v15H5zM14 2v6h5M8 12h8M8 16h8"/>',
    "browser": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 9h20M6 6.5h.01M9 6.5h.01"/>',
    "external": '<path d="M14 3h7v7M21 3l-11 11M10 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m7 12 3 3 7-7"/>',
    "warning": '<path d="m12 3 10 18H2zM12 9v5M12 17h.01"/>',
}

STYLE = """
:root{color-scheme:dark;--bg:#090b0f;--surface:#13161d;--inset:#1b2029;--border:#2b3340;
--text:#f1f4f8;--muted:#a7b0bf;--blue:#5799ff;--green:#58d99a;--amber:#efbb58;--red:#ff9191}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--blue);text-underline-offset:4px}
a:hover{color:#9ac2ff}
a:focus-visible,button:focus-visible{outline:3px solid var(--blue);outline-offset:4px}
button,a{-webkit-tap-highlight-color:transparent}
.icon{width:22px;height:22px;flex:none;vertical-align:middle}
.shell{width:min(1120px,calc(100% - 64px));margin:36px auto 56px}
.masthead,.brand,.tabs,.project-heading,.badge,.actions,.button,.file-context,.notice{display:flex;align-items:center}
.masthead{justify-content:space-between;gap:24px;padding-bottom:24px;border-bottom:1px solid var(--border)}
.brand{gap:16px;white-space:nowrap}.brand>.icon{width:38px;height:38px;color:var(--blue)}
.brand strong{font-size:26px;letter-spacing:-.5px}.brand-label{border-left:1px solid var(--border);padding-left:22px;color:var(--muted);font-size:18px}
.tabs{border:1px solid var(--border);border-radius:9px;flex:none}
.tabs a{padding:9px 24px;border:1px solid transparent;border-radius:8px;text-decoration:none;color:var(--muted)}
.tabs a[aria-current=page]{color:var(--blue);background:#12213a;border-color:var(--blue)}
h1{font-size:30px;line-height:1.4;letter-spacing:-.5px;margin:28px 0 20px}
h2,h3,p{margin:0}h2{font-size:19px;line-height:1.5}h3{font-size:16px}
.notice{gap:18px;align-items:flex-start;border:1px solid var(--border);background:#10151e;padding:17px 22px;border-radius:10px;color:var(--muted);margin-bottom:20px}
.notice>.icon{color:var(--blue);margin-top:4px}.notice p+p{margin-top:4px;font-size:13px}
.project-card{border:1px solid var(--border);border-radius:14px;background:var(--surface);padding:24px 28px;margin-top:18px}
.project-heading{justify-content:space-between;align-items:flex-start;gap:20px}
.project-heading h2{font-family:ui-monospace,Consolas,monospace;overflow-wrap:anywhere;min-width:0}
.badge{gap:8px;border:1px solid currentColor;border-radius:7px;padding:5px 12px;flex:none;font-size:13px;line-height:1.5}
.badge .icon{width:18px;height:18px}.success{color:var(--green)}.warning{color:var(--amber)}.danger{color:var(--red)}.info{color:var(--blue)}.muted{color:var(--muted)}
.metadata{display:flex;flex-wrap:wrap;gap:6px 24px;margin-top:12px;color:var(--muted);font-size:14px}
.message{color:var(--muted);margin-top:14px;overflow-wrap:anywhere;white-space:pre-wrap}
.findings{list-style:none;margin:18px 0 0;padding:0;display:grid;gap:12px}
.finding{border:1px solid var(--border);border-radius:10px;background:#10151d;padding:18px 20px;overflow-wrap:anywhere}
.finding p{margin-top:5px;color:var(--muted);white-space:pre-wrap}.finding .guidance{font-size:13px}
.versions{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0 0}
.versions>div{display:flex;align-items:center;gap:18px;border:1px solid var(--border);border-radius:8px;background:#101720;padding:10px 16px;min-width:0}
.versions dt{color:var(--muted);font-size:13px}.versions dd{margin:0;border-left:1px solid var(--border);padding-left:18px;overflow-wrap:anywhere}
.mono{font-family:ui-monospace,Consolas,monospace}
.migration-label{display:flex;align-items:center;gap:9px;font-size:14px;margin-top:16px}
.migration-label .icon{width:18px;height:18px;color:var(--amber)}
.migrations{padding:0;margin:10px 0 0;list-style:none;border:1px solid var(--border);border-radius:8px;overflow:hidden;background:#101720}
.migrations li{display:grid;grid-template-columns:110px 1fr;font:13px/1.6 ui-monospace,Consolas,monospace}
.migrations li+li{border-top:1px solid var(--border)}.migrations span{padding:7px 16px;overflow-wrap:anywhere}
.migrations span+span{border-left:1px solid var(--border);color:var(--muted)}
.empty{color:var(--muted);padding:24px 0}
.compact{width:min(740px,calc(100% - 40px));margin:clamp(32px,14vh,160px) auto 48px;padding:34px;background:var(--surface);border:1px solid var(--border);border-radius:18px;box-shadow:0 16px 48px #0004}
.compact .masthead{padding-bottom:22px}.compact .brand-label{border:0;padding-left:0;font-size:16px}
.opening-heading{display:flex;align-items:center;gap:16px;margin:28px 0 12px}.opening-heading h1{margin:0;font-size:28px}
.spinner{display:inline-block;width:30px;height:30px;border:4px solid #354258;border-top-color:var(--blue);border-right-color:var(--blue);border-radius:50%;flex:none}
.is-opening .spinner{animation:spin 1s linear infinite}.spinner[hidden]{display:none}
@keyframes spin{to{transform:rotate(360deg)}}
.opening-status{color:var(--muted);min-height:26px;overflow-wrap:anywhere}
.file-context{gap:20px;padding:18px 22px;background:var(--inset);border:1px solid var(--border);border-radius:10px;margin:24px 0}
.file-context>.icon{color:var(--muted);width:27px;height:27px}.file-context>div{min-width:0}
.file-path{font:15px/1.6 ui-monospace,Consolas,monospace;overflow-wrap:anywhere}.project-name{font-size:13px;color:var(--muted);margin-top:2px;overflow-wrap:anywhere}
.actions{gap:16px}.button{justify-content:center;gap:10px;flex:1;padding:12px 18px;min-height:48px;border:1px solid var(--blue);border-radius:8px;color:var(--blue);background:transparent;font:inherit;text-decoration:none;cursor:pointer}
.button:hover{background:#152339;color:var(--blue)}.primary{background:#245ec7;color:#fff}.primary:hover{background:#2e6bd7;color:#fff}
.primary:disabled{background:#20375e;border-color:#20375e;color:#c3d5f1;cursor:default}.button .spinner{width:18px;height:18px;border-width:2px}
.github-link{display:inline-flex;align-items:center;gap:9px;margin-top:18px;text-decoration:none;font-size:14px}
.closing-note{display:flex;align-items:flex-start;gap:16px;border-top:1px solid var(--border);padding-top:22px;margin-top:26px;color:var(--muted);font-size:13px}
.closing-note>.icon{margin-top:2px}.closing-note p+p{margin-top:3px}
@media(max-width:640px){.shell{width:calc(100% - 32px);margin-top:20px}.masthead{align-items:flex-start;flex-direction:column;gap:18px}.brand{gap:12px}.brand strong{font-size:23px}.brand-label{padding-left:14px;font-size:16px}.tabs{width:100%}.tabs a{flex:1;text-align:center;padding:8px 12px}h1{font-size:25px}.notice{padding:14px;gap:12px}.project-card{padding:20px 16px}.project-heading{flex-direction:column;gap:12px}.project-heading h2{font-size:16px}.metadata{gap:4px 16px;font-size:13px}.versions{grid-template-columns:1fr}.versions>div{padding:9px 12px}.migrations li{grid-template-columns:76px 1fr}.migrations span{padding:8px 10px}.compact{width:calc(100% - 32px);margin:28px auto;padding:24px 20px}.compact .masthead{flex-direction:row}.opening-heading{gap:12px}.opening-heading h1{font-size:23px}.actions{flex-direction:column;align-items:stretch}.button{flex:auto}.file-context{padding:16px;gap:14px}.file-path{font-size:13px}}
@media(prefers-reduced-motion:reduce){.is-opening .spinner{animation:none}}
"""


def icon(name: str) -> str:
    return ('<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
            'focusable="false">' + ICONS[name] + '</svg>')


def page(title: str, body: str, *, label: str, navigation: str = "", compact: bool = False) -> bytes:
    """Frame trusted application markup; callers escape their dynamic content."""
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="color-scheme" content="dark"><title>' + html.escape(title) + '</title>'
            '<style>' + STYLE + '</style></head><body><main class="' + ('compact' if compact else 'shell') + '">'
            '<header class="masthead"><div class="brand">' + icon("brand")
            + '<strong>SmartKit</strong><span class="brand-label">' + html.escape(label)
            + '</span></div>' + navigation + '</header>' + body + '</main></body></html>').encode('utf-8')
