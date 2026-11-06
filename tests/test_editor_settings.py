"""Verify the shipped VSIX and profile-specific installation without modifying VS Code."""
import json
from io import StringIO
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from local_web.apps import editor_settings
from local_web import service


class EditorSettingsTests(unittest.TestCase):
    def setUp(self):
        self.launcher = Path("Code.exe")
        self.profile = "Otaku 中文"
        self.manifest = json.loads((editor_settings.RUNTIME_DIR / "vscode" / "package.json").read_text(encoding="utf-8"))
        self.version = self.manifest["version"]
        self.list_command = ["--profile", self.profile, "--list-extensions", "--show-versions"]
        self.install_command = ["--profile", self.profile, "--install-extension", str(editor_settings.VSIX)]

    def test_shipped_package_matches_canonical_extension(self):
        with ZipFile(editor_settings.VSIX) as archive:
            for name in ("extension.js", "package.json"):
                self.assertEqual(archive.read("extension/" + name),
                                 (editor_settings.RUNTIME_DIR / "vscode" / name).read_bytes())
        self.assertEqual(editor_settings.EXTENSION_ID, self.manifest["publisher"] + "." + self.manifest["name"])

    def test_install_and_update_read_back_the_selected_profile(self):
        for previous in ("", editor_settings.EXTENSION_ID + "@0.0.0\n"):
            with self.subTest(previous=previous), patch.object(editor_settings, "find_vscode", return_value=self.launcher), \
                    patch.object(editor_settings, "_code", side_effect=[previous, "", editor_settings.EXTENSION_ID + "@" + self.version]) as code:
                result = editor_settings.install(self.profile)
                self.assertEqual(result, {"status": "installed", "profile": self.profile, "version": self.version})
                self.assertEqual([call.args for call in code.call_args_list],
                                 [(self.launcher, args) for args in
                                  (self.list_command, self.install_command, self.list_command)])

    def test_equal_or_newer_installation_is_left_in_place(self):
        for version in (self.version, "999.0.0"):
            with self.subTest(version=version), patch.object(editor_settings, "find_vscode", return_value=self.launcher), \
                    patch.object(editor_settings, "_code", return_value=editor_settings.EXTENSION_ID + "@" + version) as code:
                self.assertEqual(editor_settings.install(self.profile)["status"], "already-installed")
                code.assert_called_once()

    def test_unknown_profile_never_reaches_installation(self):
        with patch.object(editor_settings, "find_vscode", return_value=self.launcher), \
                patch.object(editor_settings, "_code", side_effect=OSError("missing profile")) as code:
            with self.assertRaisesRegex(OSError, "missing profile"):
                editor_settings.install(self.profile)
            self.assertEqual(code.call_args.args, (self.launcher, self.list_command))
            code.assert_called_once()

    def test_unconfirmed_installation_is_reported_as_failure(self):
        with patch.object(editor_settings, "find_vscode", return_value=self.launcher), \
                patch.object(editor_settings, "_code", side_effect=["", "", ""]):
            with self.assertRaisesRegex(OSError, "未能确认"):
                editor_settings.install(self.profile)

    def test_profile_name_is_validated_before_starting_the_editor(self):
        with patch.object(editor_settings, "find_vscode") as find:
            for profile in ("", "--force", "unsafe\nargument", "x" * 129):
                with self.subTest(profile=profile), self.assertRaises(ValueError):
                    editor_settings.install(profile)
            find.assert_not_called()

    def test_windows_uses_the_native_executable_and_cli_entry(self):
        entry = Path("resources/app/out/cli.js")
        with patch.object(editor_settings.sys, "platform", "win32"), \
                patch.object(editor_settings, "_windows_cli_entry", return_value=entry), \
                patch.object(editor_settings.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout="listed")) as run:
            self.assertEqual(editor_settings._code(self.launcher, self.list_command, failure="failed"), "listed")
            self.assertEqual(run.call_args.args[0], [str(self.launcher), str(entry), *self.list_command])
            self.assertEqual(run.call_args.kwargs["env"]["ELECTRON_RUN_AS_NODE"], "1")

    def test_versioned_windows_layout_follows_the_installed_command(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "bin").mkdir()
            relative = Path("resources/app/out/cli.js")
            current = root / "123456789a" / relative
            for entry in (root / relative, current, root / "abcdef0123" / relative):
                entry.parent.mkdir(parents=True)
                entry.touch()
            script = root / "bin" / "code.cmd"
            script.write_text(r'"%~dp0..\Code.exe" "%~dp0..\123456789a\resources\app\out\cli.js" %*', encoding="utf-8")
            self.assertEqual(editor_settings._windows_cli_entry(root / "Code.exe"), current)
            script.unlink()
            self.assertEqual(editor_settings._windows_cli_entry(root / "Code.exe"), root / relative)

    def test_session_hook_prompts_when_vscode_is_available_without_bridge(self):
        editor_url = "http://127.0.0.1:47821/editor/?key=private"
        with patch.object(service.sys, "stdin", StringIO("{}")), patch.object(service, "record_project"), \
                patch.object(service, "hook_page_links", return_value={}), \
                patch.object(service, "ensure_service", return_value={"apps": {"editor": editor_url}}), \
                patch.object(editor_settings, "find_vscode", return_value=self.launcher) as find, \
                patch.object(editor_settings, "installed_version", return_value=None) as installed:
            notice = service.hook_project("codex")
            self.assertIn("缺少必装扩展", notice)
            self.assertIn(editor_url, notice)
            installed.assert_called_once_with(self.launcher)
            installed.return_value = self.version
            self.assertEqual(service.hook_project("codex"), "")
            find.return_value = None
            installed.reset_mock()
            self.assertEqual(service.hook_project("codex"), "")
            installed.assert_not_called()
