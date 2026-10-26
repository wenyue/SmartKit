"""Stable user-local bootstrap; the active plugin owns login behavior."""
from pathlib import Path
import json
import sys


def main() -> None:
    root = Path(__file__).resolve().parent
    config = json.loads((root.parent / "config.json").read_text(encoding="utf-8"))
    if config.get("localWeb", {}).get("autostart") is not True:
        return
    runtime = json.loads((root / "runtime.json").read_text(encoding="utf-8"))
    plugin = Path(runtime["plugin_root"])
    # A removed installation must not silently fall back to an arbitrary cached version.
    if not plugin.is_absolute() or not (plugin / ".claude-plugin/plugin.json").is_file():
        return
    sys.path.insert(0, str(plugin / "runtime"))
    from local_web.autostart import run_on_login
    run_on_login()


if __name__ == "__main__":
    main()
