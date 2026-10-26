"""Login choices, native ownership, and daily confirmation without real user changes."""
from contextlib import ExitStack
from datetime import datetime, timedelta
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_web import autostart, service, storage

WINDOWS = sys.platform == "win32"


class LoginRegistrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="smartkit-login ' $ % ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.state = self.root / "state/smartkit/local-web"
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.dict(os.environ, {
            "LOCALAPPDATA": str(self.root / "local"), "APPDATA": str(self.root / "roaming"),
            "XDG_CONFIG_HOME": str(self.root / "config"),
        }))
        self.stack.enter_context(mock.patch.object(storage, "state_dir", lambda: self.state))
        self.stack.enter_context(mock.patch.object(autostart.sys, "platform", "linux"))
        self.stack.enter_context(mock.patch.object(autostart, "_select_backend", return_value="xdg"))

    def test_inspection_and_missing_choice_do_not_create_state_or_registration(self):
        status = autostart.inspect_status()
        self.assertIsNone(status.preference)
        self.assertEqual(status.state, "unconfigured")
        self.assertFalse(self.state.exists())
        self.assertFalse(autostart._registration("xdg").exists())

    def test_explicit_refusal_is_persistent_and_does_not_register(self):
        status = autostart.configure(False)
        self.assertFalse(status.preference)
        self.assertEqual(status.state, "disabled")
        self.assertFalse(autostart._registration("xdg").exists())
        self.assertFalse(autostart._record_path().exists())

    def test_enable_verifies_then_disable_removes_only_owned_files(self):
        storage.prepare_state()
        storage.write_json(autostart._config_path(), {"other": 7, "localWeb": {"other": 8}})
        self.assertEqual(autostart.configure(True).state, "installed")
        native = autostart._registration("xdg")
        text = native.read_text()
        self.assertIn("Terminal=false", text)
        self.assertIn("launcher.py", text)
        self.assertIn("%%", text)
        self.assertNotIn("1.2.25", text)
        foreign = native.parent / "another-app.desktop"
        foreign.write_text("user data")
        autostart.configure(False)
        self.assertFalse(native.exists())
        self.assertEqual(foreign.read_text(), "user data")
        self.assertEqual(storage.read_json(autostart._config_path()),
                         {"other": 7, "localWeb": {"other": 8, "autostart": False}})

    def test_linux_native_command_formats_preserve_literal_special_characters(self):
        # Golden strings follow systemd.service and Desktop Entry Exec syntax,
        # including the desktop string decoding layer before argument decoding.
        launcher = PurePosixPath('/a ${USER} %s `x`/launcher.py')
        executable = '/opt/Python $v %s/bin/python'
        with mock.patch.object(autostart.sys, 'executable', executable), \
                mock.patch.object(autostart, '_command'):
            for backend, key, expected in (
                ('systemd', 'ExecStart=', r'":/opt/Python $v %%s/bin/python" "-B" "/a ${USER} %%s `x`/launcher.py"'),
                ('xdg', 'Exec=', r'"/opt/Python \\$v %%s/bin/python" "-B" "/a \\${USER} %%s \\`x\\`/launcher.py"'),
            ):
                with self.subTest(backend=backend):
                    target = self.root / (backend + '.conf')
                    autostart._register(backend, target, launcher)
                    actual = next(line[len(key):] for line in target.read_text().splitlines()
                                  if line.startswith(key))
                    self.assertEqual(actual, expected)

    def test_linux_native_command_rejects_line_injection(self):
        with self.assertRaisesRegex(ValueError, 'newlines'):
            autostart._register('xdg', self.root / 'invalid.desktop', Path('/tmp/a\nHidden=true'))
        self.assertFalse((self.root / 'invalid.desktop').exists())

    def test_another_user_has_separate_preference_and_native_files(self):
        autostart.configure(True)
        first = autostart._registration("xdg")
        with mock.patch.object(storage, "state_dir", return_value=self.root / "user2/smartkit/local-web"), \
                mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root / "user2-config")}):
            self.assertIsNone(autostart.preference())
            self.assertFalse(autostart._registration("xdg").exists())
            autostart.configure(False)
        self.assertTrue(autostart.preference())
        self.assertTrue(first.exists())

    def test_foreign_or_modified_native_file_is_preserved(self):
        native = autostart._registration("xdg")
        native.parent.mkdir(parents=True)
        native.write_text("not SmartKit's entry")
        with self.assertRaisesRegex(ValueError, "preserved"):
            autostart.configure(True)
        self.assertEqual(native.read_text(), "not SmartKit's entry")
        self.assertTrue(autostart.preference())

    def test_refusal_reports_unowned_entries_and_preserves_every_native_backend(self):
        for backend in ('xdg', 'systemd', 'windows'):
            with self.subTest(backend=backend), mock.patch.object(
                    autostart.sys, 'platform', 'win32' if backend == 'windows' else 'linux'):
                native = autostart._registration(backend)
                native.parent.mkdir(parents=True, exist_ok=True)
                native.write_text('unknown user entry')
                with self.assertRaisesRegex(ValueError, 'preserved'):
                    autostart.configure(False)
                self.assertFalse(autostart.preference())
                self.assertEqual(native.read_text(), 'unknown user entry')
                status = autostart.inspect_status()
                self.assertEqual(status.state, 'modified')
                self.assertIn(str(native), status.message)
                self.assertFalse(autostart._record_path().exists())
                native.unlink()

    def test_modified_owned_file_is_not_repaired_by_hook_or_deleted(self):
        autostart.configure(True)
        native = autostart._registration("xdg")
        native.write_text("user modified")
        autostart.refresh_runtime()
        with self.assertRaisesRegex(ValueError, "preserved"):
            autostart.configure(False)
        self.assertEqual(native.read_text(), "user modified")
        self.assertFalse(autostart.preference())

    def test_failed_registration_retains_choice_and_partial_ownership_for_retry(self):
        with mock.patch.object(autostart, "_register", side_effect=OSError("native registration denied")):
            with self.assertRaisesRegex(OSError, "denied"):
                autostart.configure(True)
        self.assertTrue(autostart.preference())
        self.assertEqual(autostart.inspect_status().state, "incomplete")
        self.assertEqual(autostart.configure(True).state, "installed")

    def test_failed_native_registration_with_all_files_present_stays_incomplete(self):
        def fail_after_creating_entry(backend, target, launcher):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('partial native registration')
            raise OSError('native save did not complete')
        with mock.patch.object(autostart, '_register', side_effect=fail_after_creating_entry):
            with self.assertRaisesRegex(OSError, 'did not complete'):
                autostart.configure(True)
        self.assertTrue(all(path.exists() for path in autostart._paths('xdg').values()))
        self.assertEqual(autostart.inspect_status().state, 'incomplete')
        autostart.refresh_runtime()
        self.assertEqual(autostart.inspect_status().state, 'incomplete')
        self.assertEqual(autostart.configure(True).state, 'installed')

    def test_failed_registration_can_be_disabled_without_unknown_file_cleanup(self):
        with mock.patch.object(autostart, "_register", side_effect=OSError("denied")):
            with self.assertRaises(OSError):
                autostart.configure(True)
        self.assertEqual(autostart.configure(False).state, "disabled")
        self.assertFalse(autostart._record_path().exists())

    def test_native_and_partial_record_failures_both_reach_cli_diagnostics(self):
        from local_web import cli
        write = storage.write_json
        def fail_record(path, value):
            if path == autostart._record_path() and value.get('digests'):
                raise PermissionError('ownership denied')
            write(path, value)
        with mock.patch.object(autostart, '_register', side_effect=OSError('native denied')), \
                mock.patch.object(storage, 'write_json', side_effect=fail_record), \
                mock.patch('sys.stderr', new_callable=io.StringIO) as errors:
            self.assertEqual(cli.main(['autostart', 'enable']), 1)
        self.assertIn('native denied', errors.getvalue())
        self.assertIn('ownership denied', errors.getvalue())
        self.assertTrue(autostart.preference())
        self.assertTrue(autostart._paths('xdg')['launcher'].exists())
        self.assertEqual(autostart.inspect_status().state, 'incomplete')

    def test_invalid_user_configuration_is_preserved(self):
        storage.prepare_state()
        path = autostart._config_path()
        path.write_text('{"localWeb":{"autostart":"yes"}}')
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            autostart.configure(True)
        self.assertEqual(path.read_bytes(), before)

    def test_invalid_ownership_cannot_delete_native_or_user_files(self):
        autostart.configure(True)
        native = autostart._registration('xdg')
        original = native.read_bytes()
        record = autostart._record()
        invalid_records = (
            {**record, 'schema': True},
            {**record, 'digests': {**record['digests'], 'other': '0' * 64}},
            {**record, 'digests': {**record['digests'], 'registration': 'not a hash'}},
        )
        for invalid in invalid_records:
            with self.subTest(record=invalid):
                storage.write_json(autostart._record_path(), invalid)
                before = autostart._record_path().read_bytes()
                with self.assertRaisesRegex(ValueError, 'ownership record'):
                    autostart.configure(False)
                self.assertEqual(native.read_bytes(), original)
                self.assertEqual(autostart._record_path().read_bytes(), before)

    def test_runtime_pointer_upgrades_without_replacing_entry_and_never_downgrades(self):
        with mock.patch.object(autostart, "_runtime", return_value={"plugin_root": "/old", "version": "1.2.24"}):
            autostart.configure(True)
        native = autostart._registration("xdg")
        original = native.read_bytes()
        newer = {"plugin_root": "/new", "version": "1.2.26"}
        with mock.patch.object(autostart, "_runtime", return_value=newer):
            autostart.refresh_runtime()
        self.assertEqual(storage.read_json(autostart._paths("xdg")["runtime"]), newer)
        with mock.patch.object(autostart, "_runtime", return_value={"plugin_root": "/old", "version": "1.2.25"}):
            autostart.refresh_runtime()
        self.assertEqual(storage.read_json(autostart._paths("xdg")["runtime"]), newer)
        self.assertEqual(native.read_bytes(), original)
        self.assertEqual(autostart.inspect_status().state, "installed")

    def test_cli_status_is_read_only_and_does_not_start_the_host(self):
        from local_web import cli
        output = io.StringIO()
        with mock.patch('sys.stdout', output), mock.patch.object(service, "ensure_service") as ensure:
            self.assertEqual(cli.main(["autostart", "status"]), 0)
        value = json.loads(output.getvalue())
        self.assertEqual(value["state"], "unconfigured")
        self.assertNotIn("key", value)
        ensure.assert_not_called()
        self.assertFalse(self.state.exists())

    def test_broken_login_configuration_does_not_block_session_host_recovery(self):
        from local_web import cli
        with mock.patch.object(autostart, 'refresh_runtime', side_effect=ValueError('invalid preference')), \
                mock.patch.object(service, 'hook_project', return_value='status pages') as hook, \
                mock.patch('sys.stdout', new_callable=io.StringIO) as output, \
                mock.patch('sys.stderr', new_callable=io.StringIO) as errors:
            self.assertEqual(cli.main(['hook', '--harness', 'codex']), 0)
        hook.assert_called_once_with('codex')
        self.assertIn('status pages', output.getvalue())
        self.assertIn('invalid preference', errors.getvalue())

    def test_bootstrap_exits_when_disabled_or_plugin_removed(self):
        autostart.configure(True)
        launcher = autostart._paths("xdg")["launcher"]
        autostart._save_preference(False)
        result = subprocess.run([sys.executable, "-B", str(launcher)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        autostart._save_preference(True)
        storage.write_json(autostart._paths("xdg")["runtime"],
                           {"plugin_root": str(self.root / "removed-plugin"), "version": "1.2.25"})
        result = subprocess.run([sys.executable, "-B", str(launcher)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def _systemd(self):
        enabled = [False]
        def run(arguments):
            if "enable" in arguments:
                enabled[0] = True
            if "disable" in arguments:
                enabled[0] = False
            if "is-enabled" in arguments:
                return subprocess.CompletedProcess(arguments, 0 if enabled[0] else 1,
                                                   "enabled\n" if enabled[0] else "disabled\n", "")
            return subprocess.CompletedProcess(arguments, 0, "", "")
        self.stack.enter_context(mock.patch.object(autostart, "_select_backend", return_value="systemd"))
        runner = self.stack.enter_context(mock.patch.object(autostart, "_run", side_effect=run))
        return enabled, runner

    def test_systemd_registers_without_starting_or_stopping_current_host(self):
        enabled, runner = self._systemd()
        with mock.patch.object(service, "ensure_service") as ensure, mock.patch.object(service, "stop_service") as stop:
            self.assertEqual(autostart.configure(True).state, "installed")
            unit = autostart._registration("systemd").read_text()
            self.assertIn("Type=simple", unit)
            self.assertNotIn("ensure", unit)
            self.assertNotIn("--now", str(runner.call_args_list))
            ensure.assert_not_called()
            autostart.configure(False)
            stop.assert_not_called()
        self.assertFalse(enabled[0])

    def test_system_disabled_entry_is_not_reenabled_during_pointer_refresh(self):
        enabled, runner = self._systemd()
        autostart.configure(True)
        pointer = autostart._paths("systemd")["runtime"].read_bytes()
        enabled[0] = False
        runner.reset_mock()
        autostart.refresh_runtime()
        self.assertEqual(autostart.inspect_status().state, "disabled-in-system")
        self.assertFalse(any("enable" in call.args[0] for call in runner.call_args_list))
        self.assertEqual(autostart._paths("systemd")["runtime"].read_bytes(), pointer)

    def test_systemd_login_runs_foreground_without_spawning_detached_host(self):
        self._systemd()
        autostart.configure(True)
        with mock.patch.object(service, "load_state", return_value=None), \
                mock.patch.object(service, "port_available", return_value=True), \
                mock.patch.object(service, "serve") as serve, \
                mock.patch.object(service, "ensure_service") as ensure:
            autostart.run_on_login()
            serve.assert_called_once_with()
            ensure.assert_not_called()

    def test_login_reuses_existing_authenticated_host(self):
        self._systemd()
        autostart.configure(True)
        with mock.patch.object(service, "load_state", return_value={"key": "existing"}), \
                mock.patch.object(service, "health", return_value={"pid": 42}), \
                mock.patch.object(service, "serve") as serve:
            autostart.run_on_login()
            serve.assert_not_called()

    @unittest.skipUnless(WINDOWS, "Windows shortcut acceptance")
    def test_windows_creates_and_removes_a_real_shortcut_in_temporary_user_startup(self):
        with mock.patch.object(autostart.sys, "platform", "win32"), \
                mock.patch.object(autostart, "_select_backend", return_value="windows"):
            self.assertEqual(autostart.configure(True).state, "installed")
            native = autostart._registration("windows")
            self.assertGreater(native.stat().st_size, 0)
            self.assertTrue(str(native).startswith(str(self.root)))
            escaped = str(native).replace("'", "''")
            script = ("$link=(New-Object -ComObject WScript.Shell).CreateShortcut('" + escaped
                      + "'); @{target=$link.TargetPath; arguments=$link.Arguments} | ConvertTo-Json -Compress")
            result = autostart._run(['powershell', '-NoProfile', '-NonInteractive', '-Command', script])
            self.assertEqual(result.returncode, 0, result.stderr)
            shortcut = json.loads(result.stdout)
            self.assertEqual(Path(shortcut['target']), Path(sys.executable).with_name('pythonw.exe'))
            self.assertEqual(shortcut['arguments'], subprocess.list2cmdline(
                ['-B', str(autostart._paths('windows')['launcher'])]))
            self.assertEqual(autostart.configure(False).state, "disabled")
            self.assertFalse(native.exists())


class BackendDiscoveryTests(unittest.TestCase):
    def test_linux_prefers_working_user_systemd_and_falls_back_to_desktop(self):
        with mock.patch.object(autostart.sys, 'platform', 'linux'), \
                mock.patch.dict(os.environ, {'XDG_CURRENT_DESKTOP': 'GNOME', 'DESKTOP_SESSION': ''}), \
                mock.patch.object(autostart.shutil, 'which', return_value='/usr/bin/systemctl'), \
                mock.patch.object(autostart, '_run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, '', '')
            self.assertEqual(autostart._select_backend(), 'systemd')
            run.return_value = subprocess.CompletedProcess([], 1, '', 'no user bus')
            self.assertEqual(autostart._select_backend(), 'xdg')
            run.side_effect = TimeoutError('user manager unresponsive')
            self.assertEqual(autostart._select_backend(), 'xdg')

    def test_linux_without_user_manager_or_desktop_is_unsupported(self):
        with mock.patch.object(autostart.sys, 'platform', 'linux'), \
                mock.patch.dict(os.environ, {'XDG_CURRENT_DESKTOP': '', 'DESKTOP_SESSION': ''}), \
                mock.patch.object(autostart.shutil, 'which', return_value=None):
            self.assertIsNone(autostart._select_backend())


class DailyConsentTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / "runtime/recommended-tools/check_recommended_tools.py"
        spec = importlib.util.spec_from_file_location("autostart_daily_checker", path)
        self.checker = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.checker
        spec.loader.exec_module(self.checker)

    def test_undecided_choice_is_detected_only_inside_project_daily_gate(self):
        c = self.checker
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            for name, value in {"load_policy": {"tools": []}, "check_policy": [],
                                "check_config_requirements": [], "check_mcp_readiness": [],
                                "check_setup_migrations": [], "check_smartkit_version": [],
                                "remove_duplicate_user_mcp": [],
                                "_start_latest_smartkit_version_fetch": lambda: None}.items():
                stack.enter_context(mock.patch.object(c, name, return_value=value))
            inspector = stack.enter_context(mock.patch.object(autostart, "inspect_status", return_value=
                autostart.AutostartStatus(True, None, "unconfigured", "windows")))
            day = datetime(2026, 10, 26)
            def check(project, when=day):
                return c._run_daily_hook("codex", root / "policy.json", root / "cache", when,
                                         project_root=root / project)
            first = check("one")
            self.assertEqual([f.code for f in first.findings], ["local-web-autostart-choice"])
            self.assertTrue(first.requires_user_prompt)
            self.assertFalse(check("one").ran)
            self.assertEqual(inspector.call_count, 1)
            check("two")
            self.assertEqual(inspector.call_count, 2)
            inspector.return_value = autostart.AutostartStatus(True, False, "disabled", None)
            self.assertFalse(check("one", day + timedelta(days=1)).requires_user_prompt)

    def test_unsupported_or_changed_registration_is_reported_without_another_choice(self):
        for status in (autostart.AutostartStatus(False, None, "unsupported", None, "no user mechanism"),
                       autostart.AutostartStatus(True, True, "disabled-in-system", "systemd", "user disabled"),
                       autostart.AutostartStatus(True, False, "modified", "xdg", "unowned entry")):
            with self.subTest(status=status), mock.patch.object(autostart, "inspect_status", return_value=status):
                findings = tuple(self.checker.check_local_web_autostart())
                self.assertTrue(findings)
                self.assertFalse(self.checker.HookResult(True, findings).requires_user_prompt)

    def test_native_and_agent_messages_offer_one_lettered_question_and_wait(self):
        c = self.checker
        choice = c.Finding("local-web-autostart-choice", "Local Web", "undecided", "ask",
                           "local-web", "autostart", "choose")
        result = c.HookResult(True, (choice,))
        for harness in ("codex", "cursor", "copilot", "qoder"):
            rendered = c.render_hook_result(result, harness, delivery="context")
            value = json.loads(rendered)
            context = value.get("additionalContext", value.get("additional_context", ""))
            if harness in ("codex", "qoder"):
                context = value["hookSpecificOutput"]["additionalContext"]
                message = value["systemMessage"]
                self.assertEqual(message.count("❓ **Q1**"), 1)
                self.assertIn("A．", message)
                self.assertIn("B．", message)
                self.assertNotIn("C．", message)
            self.assertIn("autostart enable", context)
            self.assertIn("autostart disable", context)
            self.assertIn("no later option and no default", context)
            self.assertIn("Pause the original task", context)
            self.assertIn("B must be persisted", context)

    def test_public_hook_loads_all_prompts_and_delivers_startup_choice(self):
        c = self.checker
        choice = c.Finding('local-web-autostart-choice', 'Local Web', 'undecided', 'ask',
                           'local-web', 'autostart', 'choose')
        with mock.patch.object(c, 'run_hook', return_value=c.HookResult(True, (choice,))) as run, \
                mock.patch.object(c, 'record_readiness_snapshot') as record, \
                mock.patch.object(c, 'load_user_shell_path'), \
                mock.patch('sys.stdout', new_callable=io.StringIO) as output, \
                mock.patch('sys.stderr', new_callable=io.StringIO) as errors:
            self.assertEqual(c.main(['hook', '--harness', 'codex']), 0)
        run.assert_called_once()
        self.assertFalse(record.call_args.args[0].internal_error)
        self.assertEqual(errors.getvalue(), '')
        value = json.loads(output.getvalue())
        self.assertIn('是否启用登录自启动', value['systemMessage'])
        self.assertIn('autostart disable', value['hookSpecificOutput']['additionalContext'])

    def test_update_question_precedes_independent_login_question(self):
        c = self.checker
        findings = (c.Finding("smartkit-outdated", "SmartKit", "new release", "update"),
                    c.Finding("local-web-autostart-choice", "Local Web", "undecided", "ask",
                              "local-web", "autostart", "choose"))
        result = json.loads(c.render_hook_result(c.HookResult(True, findings), "codex"))
        self.assertIn("更新与维护", result["systemMessage"])
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertLess(context.index("All reported readiness"), context.index("login-startup preference"))
        self.assertIn("one independent question per reply", context)
        self.assertIn("❓ **Q2**", context)
        self.assertIn("finish any pending check questions", context)


if __name__ == "__main__":
    unittest.main()
