"""Current-user URI registration and desktop launching for SmartKit."""
from __future__ import annotations

import ctypes
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal, Mapping, Sequence


Ownership = Literal['absent', 'owned', 'foreign']
DESKTOP_ID = 'smartkit-deep-links.desktop'
BUNDLE_ID = 'com.wenyue.smartkit.links'
REGISTRY_KEY = r'Software\Classes\smartkit'
USER_CHOICE_KEY = r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\smartkit\UserChoice'


def _xdg_path(name: str, default: Path) -> Path:
    value = Path(os.environ.get(name, str(default)))
    return value if value.is_absolute() else default


def data_root() -> Path:
    if sys.platform == 'win32':
        return Path(os.environ['LOCALAPPDATA']) / 'SmartKit' / 'DeepLinks'
    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'SmartKit' / 'DeepLinks'
    return _xdg_path('XDG_DATA_HOME', Path.home() / '.local/share') / 'smartkit/deep-links'


def desktop_environment() -> dict[str, str]:
    """Recover only desktop connection variables when a local Hook lacks them."""
    environment = dict(os.environ)
    if sys.platform != 'linux' or environment.get('DISPLAY') or environment.get('WAYLAND_DISPLAY'):
        return environment
    keys = {'DISPLAY', 'WAYLAND_DISPLAY', 'XAUTHORITY', 'XDG_RUNTIME_DIR',
            'DBUS_SESSION_BUS_ADDRESS', 'XDG_SESSION_TYPE', 'XDG_CURRENT_DESKTOP'}
    for process in Path('/proc').glob('[0-9]*'):
        try:
            if process.stat().st_uid != os.getuid():
                continue
            if (process / 'comm').read_text().strip() not in {
                'gnome-shell', 'plasmashell', 'xfce4-session', 'sway', 'weston',
            }:
                continue
            entries = (process / 'environ').read_bytes().split(b'\0')
        except (OSError, UnicodeError):
            continue
        for entry in entries:
            key, separator, value = entry.partition(b'=')
            name = key.decode('utf-8', errors='replace')
            if separator and name in keys:
                environment[name] = value.decode('utf-8', errors='replace')
        if environment.get('DISPLAY') or environment.get('WAYLAND_DISPLAY'):
            break
    return environment


def desktop_available(environment: Mapping[str, str]) -> bool:
    if environment.get('CI', '').lower() in {'1', 'true', 'yes'}:
        return False
    if sys.platform == 'linux':
        return bool(environment.get('DISPLAY') or environment.get('WAYLAND_DISPLAY'))
    return sys.platform in {'win32', 'darwin'}


def _run(arguments: Sequence[str], *, environment: Mapping[str, str] | None = None) -> str:
    result = subprocess.run(list(arguments), env=environment, check=True,
                            capture_output=True, text=True, timeout=15)
    return result.stdout.strip()


def desktop_file() -> Path:
    root = _xdg_path('XDG_DATA_HOME', Path.home() / '.local/share')
    return root / 'applications' / DESKTOP_ID


def _desktop_quote(value: str) -> str:
    # Desktop Entry Exec has its own quoting rules, separate from shell quoting.
    if '\n' in value or '\r' in value:
        raise ValueError('desktop command paths must not contain line breaks')
    escaped = value.replace('\\', '\\\\\\\\').replace('"', '\\\\"')
    escaped = escaped.replace('`', '\\\\`').replace('$', '\\\\$').replace('%', '%%')
    return '"' + escaped + '"'


def linux_entry(interpreter: Path, archive: Path) -> str:
    command = ' '.join(_desktop_quote(str(path)) for path in (interpreter, archive))
    return ('[Desktop Entry]\nType=Application\nName=SmartKit Links\n'
            'NoDisplay=true\nTerminal=false\nX-SmartKit-Owner=smartkit\n'
            'MimeType=x-scheme-handler/smartkit;\n'
            f'Exec={command} open %u\n')


def windows_command(interpreter: Path, archive: Path) -> str:
    command = subprocess.list2cmdline([str(interpreter), str(archive), 'open'])
    return command + ' "%1"'


def _mac_handler() -> str:
    core = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
    launch = ctypes.CDLL('/System/Library/Frameworks/CoreServices.framework/CoreServices')
    core.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
    core.CFStringCreateWithCString.restype = ctypes.c_void_p
    core.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint32]
    core.CFStringGetCString.restype = ctypes.c_bool
    core.CFRelease.argtypes = [ctypes.c_void_p]
    launch.LSCopyDefaultHandlerForURLScheme.argtypes = [ctypes.c_void_p]
    launch.LSCopyDefaultHandlerForURLScheme.restype = ctypes.c_void_p
    scheme = core.CFStringCreateWithCString(None, b'smartkit', 0x08000100)
    handler = None
    try:
        handler = launch.LSCopyDefaultHandlerForURLScheme(scheme)
        if not handler:
            return ''
        buffer = ctypes.create_string_buffer(1024)
        if not core.CFStringGetCString(handler, buffer, len(buffer), 0x08000100):
            raise OSError('cannot read the macOS scheme association')
        return buffer.value.decode('utf-8')
    finally:
        if handler:
            core.CFRelease(handler)
        core.CFRelease(scheme)


def ownership(environment: Mapping[str, str]) -> Ownership:
    """Inspect the effective association before changing any user configuration."""
    if sys.platform == 'win32':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, USER_CHOICE_KEY) as key:
                selected = winreg.QueryValueEx(key, 'ProgId')[0]
                if not isinstance(selected, str) or selected.lower() != 'smartkit':
                    return 'foreign'
        except FileNotFoundError:
            pass
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY) as key:
                try:
                    owner = winreg.QueryValueEx(key, 'SmartKitOwner')[0]
                except FileNotFoundError:
                    owner = ''
                return 'owned' if owner == 'smartkit' else 'foreign'
        except FileNotFoundError:
            # HKCR includes machine associations: avoid overriding another handler.
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'smartkit'):
                    return 'foreign'
            except FileNotFoundError:
                return 'absent'
    if sys.platform == 'darwin':
        selected = _mac_handler()
        return 'owned' if selected == BUNDLE_ID else ('foreign' if selected else 'absent')
    if sys.platform != 'linux':
        raise OSError('this operating system has no SmartKit protocol adapter')
    selected = _run(['xdg-mime', 'query', 'default', 'x-scheme-handler/smartkit'],
                    environment=environment)
    entry = desktop_file()
    if selected and selected != DESKTOP_ID:
        return 'foreign'
    if entry.exists() or entry.is_symlink():
        if entry.is_symlink() or 'X-SmartKit-Owner=smartkit\n' not in entry.read_text():
            return 'foreign'
    return 'owned' if selected == DESKTOP_ID else 'absent'


def registration_matches(interpreter: Path, archive: Path, environment: Mapping[str, str]) -> bool:
    if ownership(environment) != 'owned':
        return False
    if sys.platform == 'win32':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY + r'\shell\open\command') as key:
                return winreg.QueryValueEx(key, '')[0] == windows_command(interpreter, archive)
        except FileNotFoundError:
            return False
    if sys.platform == 'darwin':
        app = Path.home() / 'Applications' / 'SmartKit Links.app'
        info = app / 'Contents/Info.plist'
        return info.is_file() and plistlib.loads(info.read_bytes()).get('SmartKitCommand') == windows_command(interpreter, archive)
    entry = desktop_file()
    return entry.is_file() and entry.read_text() == linux_entry(interpreter, archive)


def register(interpreter: Path, archive: Path, environment: Mapping[str, str]) -> None:
    if ownership(environment) == 'foreign':
        raise FileExistsError('smartkit:// is already associated with another application')
    if sys.platform == 'win32':
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY) as key:
            for name, value in {'': 'URL:SmartKit Protocol', 'URL Protocol': '',
                                'SmartKitOwner': 'smartkit'}.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY + r'\shell\open\command') as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, windows_command(interpreter, archive))
        _notify_windows_association()
    elif sys.platform == 'darwin':
        import shlex
        app = Path.home() / 'Applications' / 'SmartKit Links.app'
        if app.exists():
            info = app / 'Contents/Info.plist'
            if not info.is_file() or plistlib.loads(info.read_bytes()).get('CFBundleIdentifier') != BUNDLE_ID:
                raise FileExistsError('the SmartKit application path already contains an unrelated application')
        app.parent.mkdir(parents=True, exist_ok=True)
        command = shlex.join([str(interpreter), str(archive), 'open'])
        literal = command.replace('\\', '\\\\').replace('"', '\\"')
        source = f'on open location theURL\n do shell script "{literal} " & quoted form of theURL\nend open location\n'
        _run(['osacompile', '-o', str(app), '-e', source])
        info_path = app / 'Contents/Info.plist'
        info = plistlib.loads(info_path.read_bytes())
        info.update(CFBundleIdentifier=BUNDLE_ID, LSUIElement=True,
                    SmartKitCommand=windows_command(interpreter, archive),
                    CFBundleURLTypes=[{'CFBundleURLName': BUNDLE_ID,
                                       'CFBundleURLSchemes': ['smartkit'], 'CFBundleTypeRole': 'Viewer'}])
        info_path.write_bytes(plistlib.dumps(info))
        _run(['/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister',
              '-f', str(app)])
    else:
        entry = desktop_file()
        entry.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix='.smartkit-', suffix='.desktop', dir=entry.parent)
        temporary = Path(name)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
                output.write(linux_entry(interpreter, archive))
            os.chmod(temporary, 0o644)
            os.replace(temporary, entry)
        finally:
            if temporary.exists():
                temporary.unlink()
        _run(['xdg-mime', 'default', DESKTOP_ID, 'x-scheme-handler/smartkit'], environment=environment)
    if not registration_matches(interpreter, archive, environment):
        raise OSError('the desktop did not accept the SmartKit protocol association')


def unregister(environment: Mapping[str, str]) -> None:
    """Remove only the association and launcher still owned by SmartKit."""
    selected = ownership(environment)
    if sys.platform == 'win32':
        if selected != 'owned':
            return
        import winreg
        for suffix in (r'\shell\open\command', r'\shell\open', r'\shell', ''):
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY + suffix)
        _notify_windows_association()
    elif sys.platform == 'darwin':
        app = Path.home() / 'Applications' / 'SmartKit Links.app'
        if app.exists() and plistlib.loads((app / 'Contents/Info.plist').read_bytes()).get('CFBundleIdentifier') == BUNDLE_ID:
            _run(['/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister',
                  '-u', str(app)])
            shutil.rmtree(app)
    else:
        entry = desktop_file()
        if entry.is_file() and not entry.is_symlink() and 'X-SmartKit-Owner=smartkit\n' in entry.read_text():
            entry.unlink()
        config = _xdg_path('XDG_CONFIG_HOME', Path.home() / '.config')
        directories = (config, desktop_file().parent)
        names = ['mimeapps.list']
        for desktop in environment.get('XDG_CURRENT_DESKTOP', '').lower().split(':'):
            if desktop and all(character.isalnum() or character == '-' for character in desktop):
                names.append(desktop + '-mimeapps.list')
        for directory in directories:
            for name in names:
                _remove_linux_association(directory / name)
        if selected == 'owned' and ownership(environment) == 'owned':
            raise OSError('the desktop still resolves the removed SmartKit handler')


def _remove_linux_association(path: Path) -> None:
    if not path.is_file() or path.is_symlink():
        return
    original = path.read_bytes()
    text = original.decode('utf-8')
    lines = []
    section = ''
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith('['):
            section = stripped
        key, separator, values = line.partition('=')
        if (section in {'[Default Applications]', '[Added Associations]'}
                and separator and key.strip() == 'x-scheme-handler/smartkit'):
            entries = [value for value in values.strip().split(';') if value]
            if DESKTOP_ID in entries:
                retained = [value for value in entries if value != DESKTOP_ID]
                if retained:
                    newline = '\r\n' if line.endswith('\r\n') else '\n'
                    lines.append(key + '=' + ';'.join(retained) + ';' + newline)
                continue
        lines.append(line)
    updated = ''.join(lines).encode('utf-8')
    if updated != original:
        descriptor, name = tempfile.mkstemp(prefix='.smartkit-', dir=path.parent)
        temporary = Path(name)
        try:
            with os.fdopen(descriptor, 'wb') as output:
                output.write(updated)
            os.chmod(temporary, path.stat().st_mode & 0o777)
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()


def _notify_windows_association() -> None:
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)


def open_file(path: Path, environment: Mapping[str, str]) -> None:
    if sys.platform == 'win32':
        os.startfile(str(path))
    elif sys.platform == 'darwin':
        _run(['open', str(path)], environment=environment)
    else:
        _run(['xdg-open', path.as_uri()], environment=environment)


def notify_failure(message: str) -> None:
    if sys.platform == 'win32':
        ctypes.windll.user32.MessageBoxW(None, message, 'SmartKit Links', 0x10)
    elif shutil.which('notify-send'):
        _run(['notify-send', 'SmartKit Links', message], environment=desktop_environment())
