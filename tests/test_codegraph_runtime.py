from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SUPPORT = ROOT / 'runtime/recommended-tools'
sys.path.insert(0, str(SUPPORT))
SETUP = ROOT / 'skills/setup-project-agents/scripts'
sys.path.insert(0, str(SETUP))
import codegraph_setup as setup
import codegraph_runtime as runtime
import check_recommended_tools as checker


def status(target: Path) -> dict:
    return {
        'initialized': True, 'projectPath': str(target), 'worktreeMismatch': None,
        'pendingChanges': {'added': 0, 'modified': 0, 'removed': 0},
        'index': {'state': 'complete', 'pendingRefs': 0, 'reindexRecommended': False},
    }


def completed(output: str = '', code: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess([], code, stdout=output, stderr='diagnostic' if code else '')


class CodeGraphRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.target = Path(self.temporary.name).resolve()
        self.data = self.target / '.codegraph'
        self.data.mkdir()

    def index(self):
        (self.data / 'codegraph.db').write_bytes(b'existing index')

    def test_tracked_ignore_directory_does_not_mean_initialized(self):
        (self.data / '.gitignore').write_text('*\n!.gitignore\n')
        with mock.patch.object(runtime.shutil, 'which', return_value='codegraph'), \
             mock.patch.object(runtime, 'run_command') as run:
            result = runtime.check(self.target)
        self.assertFalse(result.ready)
        self.assertIn('not initialized', result.message)
        run.assert_not_called()

    def test_check_requires_installation_without_installing_it(self):
        with mock.patch.object(runtime.shutil, 'which', return_value=None):
            result = runtime.check(self.target)
        self.assertFalse(result.ready)
        self.assertIn('not installed', result.message)

    def test_check_combines_index_and_existing_daemon_response(self):
        self.index()
        with mock.patch.object(runtime.shutil, 'which', return_value='codegraph'), \
             mock.patch.object(runtime, 'run_command', side_effect=[completed(json.dumps(status(self.target))), completed()]) as run:
            self.assertTrue(runtime.check(self.target).ready)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.args[0][2], '_probe')
        self.assertNotIn('serve', str(run.call_args_list))

    def test_check_detects_incomplete_stale_or_wrong_worktree_indexes(self):
        self.index()
        scenarios = [
            {'index': {'state': 'partial'}},
            {'index': {'state': 'complete', 'reindexRecommended': True}},
            {'index': {'state': 'complete', 'pendingRefs': 2}},
            {'pendingChanges': {'added': 1, 'modified': 0, 'removed': 0}},
            {'worktreeMismatch': {'indexRoot': '/another'}},
            {'projectPath': str(self.target / 'another')},
            {'projectPath': 7},
        ]
        for changed in scenarios:
            with self.subTest(changed=changed), \
                 mock.patch.object(runtime.shutil, 'which', return_value='codegraph'), \
                 mock.patch.object(runtime, 'run_command', return_value=completed(json.dumps({**status(self.target), **changed}))):
                self.assertFalse(runtime.check(self.target).ready)

    def test_stopped_or_hung_daemon_is_not_ready(self):
        self.index()
        for failure in (completed(code=1), subprocess.TimeoutExpired('probe', 6)):
            with self.subTest(failure=failure), \
                 mock.patch.object(runtime.shutil, 'which', return_value='codegraph'), \
                 mock.patch.object(runtime, 'run_command', side_effect=[completed(json.dumps(status(self.target))), failure]):
                self.assertFalse(runtime.check(self.target).ready)

    def test_actual_health_response_and_degraded_watcher(self):
        for marker in ('', '**Auto-sync disabled:**', '**Auto-sync recovering:**', '**Pending sync:**', '**Pending resolution:**'):
            text, expected = '**CodeGraph Status**\n' + marker, not marker
            replies = io.BytesIO(('\n'.join(json.dumps(item) for item in [
                {'id': 1, 'result': {}},
                {'id': 2, 'result': {'content': [{'type': 'text', 'text': text}]}},
            ]) + '\n').encode())
            output = io.BytesIO()
            if expected:
                runtime.verify_health(replies, output, self.target)
                sent = [json.loads(line) for line in output.getvalue().splitlines()]
                self.assertEqual(sent[-1]['params']['arguments']['projectPath'], str(self.target))
            else:
                with self.assertRaisesRegex(ValueError, 'synchronization'):
                    runtime.verify_health(replies, output, self.target)

    def test_probe_refuses_mismatched_daemon_identity(self):
        with self.assertRaisesRegex(ValueError, 'identity'):
            runtime._verify_daemon(io.BytesIO(b'{"pid": 2, "protocol":1}\n'), io.BytesIO(), self.target, {'pid': 3})

    def test_setup_requires_authority_before_any_effect(self):
        with mock.patch.object(setup.shutil, 'which') as which:
            with self.assertRaisesRegex(ValueError, 'authorization'):
                setup.setup(self.target, 'codex', approved=False)
        which.assert_not_called()

    def test_setup_installs_initializes_starts_and_verifies(self):
        with mock.patch.object(setup.shutil, 'which', side_effect=[None, 'codegraph']), \
             mock.patch.object(setup, 'run_command', return_value=completed()) as run, \
             mock.patch.object(setup, 'check', side_effect=[setup.Readiness(False, 'stopped'), setup.Readiness(True, 'ready')]), \
             mock.patch.object(setup, '_start_and_verify') as start:
            self.assertTrue(setup.setup(self.target, 'codex', approved=True).ready)
        self.assertEqual(run.call_args_list[0].args[0], [
            sys.executable, str(SETUP / 'maintain_recommended_tools.py'),
            'apply', '--harness', 'codex', '--tool', 'codegraph', '--action', 'install', '--approved',
        ])
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.args[0], ['codegraph', 'init', str(self.target)])
        start.assert_called_once()

    def test_setup_reuses_healthy_index_and_service(self):
        self.index()
        with mock.patch.object(setup.shutil, 'which', return_value='codegraph'), \
             mock.patch.object(setup, 'index_status', return_value=status(self.target)), \
             mock.patch.object(setup, 'check', return_value=setup.Readiness(True, 'ready')), \
             mock.patch.object(setup, 'run_command') as run, \
             mock.patch.object(setup, '_start_and_verify') as start:
            self.assertTrue(setup.setup(self.target, 'codex', approved=True).ready)
        run.assert_not_called()
        start.assert_not_called()
        self.assertEqual((self.data / 'codegraph.db').read_bytes(), b'existing index')

    def test_setup_reports_installer_refusal_through_its_failure_contract(self):
        with mock.patch.object(setup.shutil, 'which', return_value=None), \
             mock.patch.object(setup, 'run_command', return_value=completed(code=1)) as run:
            with self.assertRaisesRegex(ValueError, 'installation did not complete: diagnostic'):
                setup.setup(self.target, 'codex', approved=True)
        run.assert_called_once()

    def test_setup_syncs_changes_without_replacing_existing_index(self):
        self.index()
        document = status(self.target)
        document['pendingChanges']['modified'] = 1
        with mock.patch.object(setup.shutil, 'which', return_value='codegraph'), \
             mock.patch.object(setup, 'index_status', return_value=document), \
             mock.patch.object(setup, 'run_command', return_value=completed()) as run, \
             mock.patch.object(setup, 'check', return_value=setup.Readiness(True, 'ready')):
            setup.setup(self.target, 'codex', approved=True)
        self.assertEqual(run.call_args.args[0][1], 'sync')

    def test_setup_preserves_incomplete_existing_index(self):
        self.index()
        document = status(self.target)
        for changed in ({'index': {'state': 'partial'}}, {'index': None}, {'worktreeMismatch': {'indexRoot': '/another'}}):
            with self.subTest(changed=changed), \
                 mock.patch.object(setup.shutil, 'which', return_value='codegraph'), \
                 mock.patch.object(setup, 'index_status', return_value={**document, **changed}), \
                 mock.patch.object(setup, 'run_command') as run:
                with self.assertRaisesRegex(ValueError, 'preserve'):
                    setup.setup(self.target, 'codex', approved=True)
            run.assert_not_called()
        self.assertEqual((self.data / 'codegraph.db').read_bytes(), b'existing index')

    def test_setup_reports_initialization_failure_without_starting(self):
        with mock.patch.object(setup.shutil, 'which', return_value='codegraph'), \
             mock.patch.object(setup, 'run_command', return_value=completed(code=1)), \
             mock.patch.object(setup, '_start_and_verify') as start:
            with self.assertRaisesRegex(ValueError, 'init failed'):
                setup.setup(self.target, 'codex', approved=True)
        start.assert_not_called()

    def test_real_stdio_startup_probe_and_failed_query_cleanup(self):
        program = self.target / 'mcp server.py'
        original_popen = subprocess.Popen
        for is_error in (False, True):
            program.write_text(
                'import json, sys\n'
                'for line in sys.stdin:\n'
                '    request = json.loads(line)\n'
                '    if "id" not in request: continue\n'
                '    result = {} if request["method"] == "initialize" else '
                + repr({'isError': is_error, 'content': [{'type': 'text', 'text': '**CodeGraph Status**'}]}) + '\n'
                '    print(json.dumps({"id":request["id"],"result":result}), flush=True)\n',
                encoding='utf-8',
            )
            processes = []

            def launch(arguments, **kwargs):
                process = original_popen([sys.executable, str(program)], **kwargs)
                processes.append(process)
                return process

            with mock.patch.object(setup.subprocess, 'Popen', side_effect=launch):
                if is_error:
                    with self.assertRaisesRegex(ValueError, 'health tool failed'):
                        setup._start_and_verify(self.target, 'fake-codegraph')
                else:
                    setup._start_and_verify(self.target, 'fake-codegraph')
            self.assertTrue(all(process.poll() is not None for process in processes))

    def test_public_setup_command_requires_existing_authorization(self):
        result = subprocess.run([
            sys.executable, str(ROOT / 'skills/setup-project-agents/scripts/workflow.py'),
            'setup-codegraph', '--target', str(self.target), '--harness', 'codex',
        ], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('authorization', result.stderr)
        self.assertFalse((self.data / 'codegraph.db').exists())


class CodeGraphSessionTest(unittest.TestCase):
    def test_codegraph_reminder_survives_unrelated_daily_check_failure(self):
        with mock.patch.object(checker, '_run_daily_hook', return_value=checker.HookResult(True, internal_error=True)), \
             mock.patch.object(checker, 'check_project_codegraph', return_value=('CodeGraph stopped',)):
            result = checker.run_hook('codex', Path('unused'), project_root=ROOT)
        rendered = json.loads(checker.render_hook_result(result, 'codex'))
        self.assertTrue(rendered['continue'])
        self.assertIn('could not complete', rendered['systemMessage'])
        self.assertIn('CodeGraph stopped', rendered['systemMessage'])

    def test_runtime_check_runs_again_when_daily_gate_is_cached(self):
        with mock.patch.object(checker, 'check_project_configuration', return_value=((), '')), \
             mock.patch.object(checker, '_run_daily_hook', return_value=checker.HookResult(False)), \
             mock.patch.object(checker, 'check_project_codegraph', side_effect=[(), ('CodeGraph stopped',)]) as check:
            first = checker.run_hook('codex', Path('unused'), project_root=ROOT)
            second = checker.run_hook('codex', Path('unused'), project_root=ROOT)
        self.assertEqual(check.call_count, 2)
        self.assertEqual(first.notices, ())
        rendered = json.loads(checker.render_hook_result(second, 'codex'))
        self.assertTrue(rendered['continue'])
        self.assertIn('CodeGraph stopped', rendered['systemMessage'])
        self.assertFalse(second.requires_user_prompt)

    def test_non_smartkit_project_never_requests_installation(self):
        with tempfile.TemporaryDirectory() as directory, \
             mock.patch.object(runtime, 'check') as check:
            self.assertEqual(checker.check_project_codegraph(Path(directory), 'codex'), ())
        check.assert_not_called()


class HookMonitorTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which('sh'), 'POSIX shell is unavailable')
    def test_shell_uses_python_clock_when_date_has_no_nanoseconds(self):
        script = (ROOT / 'runtime/hook-monitor/monitor.sh').as_posix()
        command = (
            "date() { printf '%s\\n' '1700000000N'; }; "
            "python() { printf '%s\\n' 1000000000; }; "
            "smartkit_hook_name=test; . '" + script + "'; "
            "python() { printf '%s\\n' 1300000000; }; "
            "printf '%s\\n' '{\"continue\":true}'; exit 7"
        )
        result = subprocess.run(['sh', '-c', command], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'continue': True})
        self.assertIn('300 ms', result.stderr)

    @unittest.skipUnless(shutil.which('sh'), 'POSIX shell is unavailable')
    def test_shell_warning_threshold_preserves_json_and_failure_status(self):
        script = (ROOT / 'runtime/hook-monitor/monitor.sh').as_posix()
        for nanoseconds, warning in [(200_000_000, False), (200_000_001, True)]:
            with self.subTest(nanoseconds=nanoseconds):
                command = (
                    "date() { printf '%s\\n' " + str(1_000_000_000 + nanoseconds) + "; }; "
                    "smartkit_hook_name=test; . '" + script + "'; "
                    "smartkit_hook_started_ns=1000000000; printf '%s\\n' '{\"continue\":true}'; exit 7"
                )
                result = subprocess.run(['sh', '-c', command], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 7, result.stderr)
                self.assertEqual(json.loads(result.stdout), {'continue': True})
                self.assertEqual('WARNING' in result.stderr, warning)

    @unittest.skipUnless(shutil.which('powershell') or shutil.which('pwsh'), 'PowerShell is unavailable')
    def test_powershell_warning_does_not_change_exit_or_json(self):
        shell = shutil.which('powershell') or shutil.which('pwsh')
        script = str(ROOT / 'runtime/hook-monitor/monitor.ps1').replace("'", "''")
        command = (
            ". '" + script + "'; $timer=[Diagnostics.Stopwatch]::StartNew(); "
            "try { Start-Sleep -Milliseconds 250; Write-Output '{\"continue\":true}'; exit 7 } "
            "finally { Write-SmartKitHookDuration -Name test -Timer $timer }"
        )
        result = subprocess.run([shell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'continue': True})
        self.assertIn('WARNING', result.stderr)


if __name__ == '__main__':
    unittest.main()
