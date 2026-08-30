import ast
import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]

TIMING_SCRIPT = (
    REPO_ROOT
    / 'skills'
    / 'diagnose-agent-session'
    / 'scripts'
    / 'timing.py'
)


def load_timing_module():
    spec = importlib.util.spec_from_file_location('diagnose_agent_session', TIMING_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load timing script: {TIMING_SCRIPT}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DiagnoseAgentSessionTest(unittest.TestCase):
    def setUp(self):
        self.timing = load_timing_module()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.codex_home = Path(self.temp_dir.name) / '.codex'
        self.captured_at = datetime(2026, 7, 21, 12, tzinfo=timezone.utc)

    def write_token_count(self, session_id='session-main'):
        path = self.codex_home / 'sessions' / f'rollout-{session_id}.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'event_msg',
                'payload': {
                    'type': 'token_count',
                    'info': {
                        'total_token_usage': {
                            'input_tokens': 80,
                            'cached_input_tokens': 20,
                            'cache_write_input_tokens': 0,
                            'output_tokens': 10,
                            'reasoning_output_tokens': 2,
                            'total_tokens': 90,
                        }
                    },
                },
            },
            {
                'timestamp': '2026-07-21T12:00:00Z',
                'type': 'event_msg',
                'payload': {
                    'type': 'token_count',
                    'info': {
                        'total_token_usage': {
                            'input_tokens': 100,
                            'cached_input_tokens': 30,
                            'cache_write_input_tokens': 10,
                            'output_tokens': 20,
                            'reasoning_output_tokens': 5,
                            'total_tokens': 120,
                        }
                    },
                },
            },
        ]
        path.write_text('\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8')

    def write_tool_calls(self, session_id='session-main'):
        path = self.codex_home / 'sessions' / f'rollout-{session_id}.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'spawn-1',
                    'name': 'collaboration.spawn_agent',
                    'input': '{"task_name":"worker"}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call_output',
                    'call_id': 'spawn-1',
                    'output': '{"agent_id":"agent-1","nickname":"Worker"}',
                },
            },
            {
                'timestamp': '2026-07-21T11:01:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'wait-1',
                    'name': 'wait_agent',
                    'arguments': '{"timeout_ms":300000}',
                },
            },
            {
                'timestamp': '2026-07-21T11:01:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'wait-1',
                    'output': '{"status":{"agent-1":{"completed":"done"}},"timed_out":false}',
                },
            },
            {
                'timestamp': '2026-07-21T11:02:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'pending-1',
                    'name': 'functions.exec',
                    'input': '{}',
                },
            },
        ]
        path.write_text('\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8')

    def write_turn_tokens(self, session_id='session-main'):
        path = self.codex_home / 'sessions' / f'rollout-{session_id}.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T10:00:00Z',
                'type': 'event_msg',
                'payload': {
                    'type': 'token_count',
                    'info': {
                        'total_token_usage': {
                            'input_tokens': 100,
                            'cached_input_tokens': 30,
                            'cache_write_input_tokens': 10,
                            'output_tokens': 20,
                            'reasoning_output_tokens': 5,
                        }
                    },
                },
            },
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {'type': 'message', 'role': 'user', 'content': []},
            },
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'event_msg',
                'payload': {'type': 'user_message', 'message': 'redacted'},
            },
            {
                'timestamp': '2026-07-21T12:00:00Z',
                'type': 'event_msg',
                'payload': {
                    'type': 'token_count',
                    'info': {
                        'total_token_usage': {
                            'input_tokens': 160,
                            'cached_input_tokens': 50,
                            'cache_write_input_tokens': 10,
                            'output_tokens': 40,
                            'reasoning_output_tokens': 10,
                        }
                    },
                },
            },
        ]
        path.write_text('\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8')

    def write_wait_timeouts_and_failure(self, session_id='session-main'):
        path = self.codex_home / 'sessions' / f'rollout-{session_id}.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'spawn-1',
                    'name': 'spawn_agent',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'spawn-1',
                    'output': '{"agent_id":"agent-1"}',
                },
            },
        ]
        for index in (1, 2):
            events.extend(
                [
                    {
                        'timestamp': f'2026-07-21T11:0{index}:00Z',
                        'type': 'response_item',
                        'payload': {
                            'type': 'function_call',
                            'call_id': f'wait-{index}',
                            'name': 'wait_agent',
                            'arguments': '{"targets":["agent-1"],"timeout_ms":300000}',
                        },
                    },
                    {
                        'timestamp': f'2026-07-21T11:0{index}:30Z',
                        'type': 'response_item',
                        'payload': {
                            'type': 'function_call_output',
                            'call_id': f'wait-{index}',
                            'output': '{"status":{},"timed_out":true}',
                        },
                    },
                ]
            )
        events.extend(
            [
                {
                    'timestamp': '2026-07-21T11:03:00Z',
                    'type': 'response_item',
                    'payload': {
                        'type': 'function_call',
                        'call_id': 'shell-1',
                        'name': 'shell_command',
                        'arguments': '{}',
                    },
                },
                {
                    'timestamp': '2026-07-21T11:03:01Z',
                    'type': 'response_item',
                    'payload': {
                        'type': 'function_call_output',
                        'call_id': 'shell-1',
                        'output': 'Script failed\nExit code: 1',
                    },
                },
            ]
        )
        path.write_text('\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8')

    def usage_row(self):
        return {
            'client': 'codex',
            'sessionId': 'session-main',
            'provider': 'openai',
            'model': 'gpt-test',
            'input': 60,
            'cacheRead': 30,
            'cacheWrite': 10,
            'output': 15,
            'reasoning': 5,
            'messageCount': 2,
            'cost': 0.25,
            'performance': {
                'totalDurationMs': 2000,
                'timedTokens': 120,
                'sampleCount': 2,
            },
        }

    def assert_tokscale_row_failure(
        self,
        row,
        error_pattern,
        expected_cause,
        *,
        capture_client='cursor',
    ):
        def runner(command, **kwargs):
            return self.timing.subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({'entries': [row]}),
                stderr='',
            )

        with self.assertRaisesRegex(
            self.timing.UsageError, error_pattern
        ) as caught:
            self.timing.capture_tokscale_snapshot(
                capture_client, None, None, runner=runner
            )
        usage = self.timing.build_session_usage(
            'cursor',
            'session-main',
            self.captured_at,
            tokscale_rows=[],
            snapshot_error=str(caught.exception),
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity(
                self.timing._profile_behavior_reason('cursor')
            ),
            None,
            selected_scope='session',
        )
        capabilities = {
            capability['name']: capability for capability in report['capabilities']
        }

        self.assertEqual(
            usage['collection'],
            {'outcome': 'failed', 'cause': expected_cause},
        )
        self.assertEqual(capabilities['session usage']['status'], 'failed')
        self.assertEqual(capabilities['model activity']['status'], 'failed')
        self.assertIn(
            'Resolve the reported Tokscale collection failure',
            report['recovery_prerequisites'][0],
        )

    def test_parser_exposes_only_diagnose_command(self):
        parser = self.timing.build_parser()
        command_choices = next(
            action.choices
            for action in parser._actions
            if isinstance(getattr(action, 'choices', None), dict)
        )
        self.assertEqual(set(command_choices), {'diagnose'})

        args = parser.parse_args(
            ['diagnose', '--client', 'codex', '--session-id', 'session-main']
        )

        self.assertEqual(args.command, 'diagnose')
        self.assertEqual(args.client, 'codex')
        self.assertEqual(args.session_id, 'session-main')
        self.assertEqual(args.scope, 'both')

    def test_public_job_supports_python_3_10(self):
        ast.parse(TIMING_SCRIPT.read_text(encoding='utf-8'), feature_version=(3, 10))
        public_files = [
            TIMING_SCRIPT,
            TIMING_SCRIPT.with_name('task-metrics.ps1'),
            TIMING_SCRIPT.with_name('task-metrics.sh'),
            REPO_ROOT / 'skills' / 'diagnose-agent-session' / 'SKILL.md',
        ]
        for path in public_files:
            text = path.read_text(encoding='utf-8')
            self.assertIn('3.10', text, path)
            self.assertNotIn('3.11', text, path)

    def test_skill_defines_current_thread_identity_and_snapshot_cutoff(self):
        skill = (
            REPO_ROOT / 'skills' / 'diagnose-agent-session' / 'SKILL.md'
        ).read_text(encoding='utf-8')

        normalized_skill = ' '.join(skill.split())

        self.assertIn('session may be current or completed', normalized_skill)
        self.assertIn('identity of the current Codex thread', normalized_skill)
        self.assertIn(
            'wrapper first completes its Tokscale attempt and acquires immutable '
            'Codex local-log content',
            normalized_skill,
        )
        self.assertIn(
            'No source acquisition occurs after the reported cutoff', normalized_skill
        )
        self.assertIn('never select the newest log', normalized_skill)

    def test_windows_resolves_tokscale_cmd_for_python_subprocess(self):
        resolved = self.timing.tokscale_executable(
            os_name='nt',
            which=lambda name: 'C:/npm/tokscale.cmd' if name == 'tokscale.cmd' else None,
        )

        self.assertEqual(resolved, 'C:/npm/tokscale.cmd')

    def test_tokscale_snapshot_supports_cursor_without_date_bounds(self):
        calls = []

        def runner(command, **kwargs):
            calls.append((command, kwargs))
            return self.timing.subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({'entries': []}),
                stderr='',
            )

        result = self.timing.capture_tokscale_snapshot(
            'cursor', None, None, runner=runner
        )

        self.assertEqual(result, [])
        self.assertIn('cursor', calls[0][0])
        self.assertNotIn('--since', calls[0][0])
        self.assertNotIn('--until', calls[0][0])

    def test_tokscale_snapshot_rejects_a_row_for_another_client(self):
        row = self.usage_row()
        row['client'] = 'copilot'

        def runner(command, **kwargs):
            return self.timing.subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({'entries': [row]}),
                stderr='',
            )

        with self.assertRaisesRegex(
            self.timing.UsageError,
            'Tokscale JSON for client cursor contains a row for client copilot',
        ) as caught:
            self.timing.capture_tokscale_snapshot(
                'cursor', None, None, runner=runner
            )
        usage = self.timing.build_session_usage(
            'cursor',
            'session-main',
            self.captured_at,
            tokscale_rows=[],
            snapshot_error=str(caught.exception),
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity(
                self.timing._profile_behavior_reason('cursor')
            ),
            None,
            selected_scope='session',
        )
        capabilities = {
            item['name']: item for item in report['capabilities']
        }

        self.assertEqual(usage['collection']['outcome'], 'failed')
        self.assertEqual(capabilities['session usage']['status'], 'failed')
        self.assertEqual(capabilities['model activity']['status'], 'failed')
        self.assertIn(
            'Resolve the reported Tokscale collection failure',
            report['recovery_prerequisites'][0],
        )

        row['client'] = 'cursor'
        row['sessionId'] = 'another-cursor-session'
        self.assertEqual(
            self.timing.capture_tokscale_snapshot(
                'cursor', None, None, runner=runner
            ),
            [row],
        )

    def test_tokscale_quarantines_malformed_unrelated_session_rows(self):
        target = self.usage_row()
        target['client'] = 'cursor'
        unrelated = self.usage_row()
        unrelated.update(
            {
                'client': 'cursor',
                'sessionId': 'another-session',
                'input': 'not-numeric',
            }
        )

        def runner(command, **kwargs):
            return self.timing.subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({'entries': [target, unrelated]}),
                stderr='',
            )

        rows = self.timing.capture_tokscale_snapshot(
            'cursor',
            None,
            None,
            runner=runner,
            session_id='session-main',
        )
        usage = self.timing.build_session_usage(
            'cursor',
            'session-main',
            self.captured_at,
            tokscale_rows=rows,
        )

        self.assertEqual(rows, [target])
        self.assertEqual(usage['status'], 'available')
        self.assertEqual(usage['collection']['outcome'], 'succeeded')

        unrelated['sessionId'] = 'session-main'
        with self.assertRaisesRegex(
            self.timing.UsageError, 'Tokscale field input must be numeric'
        ):
            self.timing.capture_tokscale_snapshot(
                'cursor',
                None,
                None,
                runner=runner,
                session_id='session-main',
            )

    def test_reads_latest_codex_token_totals_without_message_content(self):
        self.write_token_count()

        result = self.timing.read_codex_token_totals('session-main', self.codex_home)

        self.assertEqual(
            result,
            {
                'input': 60,
                'cache_read': 30,
                'cache_write': 10,
                'output': 15,
                'reasoning': 5,
                'total_tokens': 120,
            },
        )

    def test_codex_session_bounds_cover_the_complete_log(self):
        self.write_token_count()

        result = self.timing.codex_session_bounds('session-main', self.codex_home)

        self.assertEqual(
            result,
            (
                datetime(2026, 7, 21, 11, tzinfo=timezone.utc),
                datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
            ),
        )

    def test_codex_local_log_matching_rejects_suffix_collisions(self):
        session_root = self.codex_home / 'sessions'
        session_root.mkdir(parents=True, exist_ok=True)
        collision = session_root / 'rollout-other-session-main.jsonl'
        collision.write_text('{}\n', encoding='utf-8')

        self.assertEqual(
            self.timing._codex_log_paths(self.codex_home, 'session-main'), []
        )

        exact = session_root / 'rollout-session-main.jsonl'
        exact.write_text('{}\n', encoding='utf-8')
        timestamped = (
            session_root
            / 'rollout-2026-07-21T11-00-00-session-main.jsonl'
        )
        timestamped.write_text('{}\n', encoding='utf-8')

        self.assertEqual(
            self.timing._codex_log_paths(self.codex_home, 'session-main'),
            sorted([exact, timestamped]),
        )

    def test_codex_snapshot_excludes_activity_after_captured_cutoff(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'event_msg',
                'payload': {'type': 'user_message'},
            },
            {
                'timestamp': '2026-07-21T12:00:01Z',
                'type': 'response_item',
                'payload': [],
            },
        ]
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n',
            encoding='utf-8',
        )

        snapshot = self.timing._load_codex_log_snapshot(
            'session-main', self.codex_home, captured_at=self.captured_at
        )
        activity = self.timing.analyze_codex_tool_activity(
            'session-main', snapshot=snapshot
        )

        self.assertEqual(len(snapshot['events']), 1)
        self.assertEqual(snapshot['acquisition']['outcome'], 'available')
        self.assertEqual(
            snapshot['captured_at'], self.captured_at.isoformat(timespec='microseconds')
        )
        self.assertEqual(activity['started_calls'], 0)

    def test_session_usage_prefers_tokscale_cost_when_available(self):
        result = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
            codex_home=self.codex_home,
        )

        self.assertEqual(result['status'], 'available')
        self.assertEqual(result['source'], 'tokscale')
        self.assertEqual(result['cost_status'], 'available')
        self.assertEqual(result['totals']['total_tokens'], 120)
        self.assertEqual(result['totals']['cost'], 0.25)
        self.assertEqual(result['totals']['message_count'], 2)
        self.assertEqual(result['totals']['model_activity_ms'], 2000)

    def test_session_usage_falls_back_to_tokens_when_tokscale_fails(self):
        self.write_token_count()

        result = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[],
            snapshot_error='Tokscale timed out.',
            codex_home=self.codex_home,
        )

        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['source'], 'codex-log')
        self.assertEqual(result['cost_status'], 'unavailable')
        self.assertEqual(result['totals']['total_tokens'], 120)
        self.assertIn('Tokscale timed out.', result['warnings'])
        report = self.timing.build_diagnostic_report(
            result,
            self.timing.unavailable_tool_activity('unavailable'),
            None,
            selected_scope='session',
        )
        self.assertEqual(report['scopes'][0]['tokens']['status'], 'partial')
        self.assertEqual(report['scopes'][0]['cost'], 'unavailable')
        self.assertIn('Tokscale timed out.', report['problems'])
        self.assertIn('unavailable', report['problems'])
        self.assertIn(
            'Resolve the reported Tokscale collection failure',
            report['recovery_prerequisites'][0],
        )

    def test_malformed_session_fallback_preserves_valid_tool_evidence_report(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'tool-1',
                    'name': 'exec',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'tool-1',
                    'output': 'ok',
                },
            },
            {
                'timestamp': '2026-07-21T12:00:00Z',
                'type': 'event_msg',
                'payload': {
                    'type': 'token_count',
                    'info': {
                        'total_token_usage': {
                            'input_tokens': True,
                            'output_tokens': 20,
                        }
                    },
                },
            },
        ]
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n',
            encoding='utf-8',
        )
        usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[],
            codex_home=self.codex_home,
        )
        activity = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )
        report = self.timing.build_diagnostic_report(
            usage,
            activity,
            self.timing.codex_session_bounds('session-main', self.codex_home),
            selected_scope='session',
        )
        capabilities = {
            capability['name']: capability for capability in report['capabilities']
        }
        rendered = self.timing.render_diagnostic_markdown(report)

        self.assertEqual(usage['status'], 'failed')
        self.assertEqual(
            usage['fallback'],
            {
                'outcome': 'failed',
                'cause': 'Tokscale field input_tokens must be numeric.',
            },
        )
        self.assertEqual(capabilities['session usage']['status'], 'failed')
        self.assertEqual(capabilities['model activity']['status'], 'unavailable')
        self.assertEqual(capabilities['tool calls']['status'], 'available')
        self.assertEqual(activity['completed_calls'], 1)
        self.assertIn('Tokscale field input_tokens must be numeric.', rendered)
        self.assertIn('Tool calls: 1 started, 1 completed', rendered)
        self.assertIn(
            'Repair or restore the exact Codex local session log token totals',
            report['recovery_prerequisites'][0],
        )

    def test_unreadable_session_token_fallback_is_structured_failed_usage(self):
        self.write_token_count()
        with mock.patch.object(
            Path,
            'read_text',
            side_effect=OSError('permission denied'),
        ):
            usage = self.timing.build_session_usage(
                'codex',
                'session-main',
                self.captured_at,
                tokscale_rows=[],
                codex_home=self.codex_home,
            )

        self.assertEqual(usage['status'], 'failed')
        self.assertEqual(
            usage['fallback'],
            {
                'outcome': 'failed',
                'cause': 'Codex log could not be read: permission denied',
            },
        )
        self.assertEqual(
            usage['warnings'],
            ['Codex log could not be read: permission denied'],
        )

    def test_tool_diagnostics_pair_calls_and_report_coordination(self):
        self.write_tool_calls()

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['completed_calls'], 2)
        self.assertEqual(result['incomplete_calls'], 1)
        self.assertEqual(result['observed_duration_ms'], 5000)
        self.assertEqual(result['coordination']['spawn_agent'], 1)
        self.assertEqual(result['coordination']['wait_agent'], 1)
        self.assertEqual(result['findings'], ['incomplete-tool-calls'])
        self.assertEqual(result['coordination']['spawn_successes'], 1)
        self.assertEqual(result['coordination']['completed_agents'], 1)
        self.assertEqual(result['coordination']['observed_peak_live_agents'], 1)
        self.assertEqual(
            result['tools'],
            [
                {
                    'name': 'exec',
                    'started': 1,
                    'completed': 0,
                    'failed': 0,
                    'incomplete': 1,
                    'duration_ms': 0,
                    'longest_ms': 0,
                },
                {
                    'name': 'spawn_agent',
                    'started': 1,
                    'completed': 1,
                    'failed': 0,
                    'incomplete': 0,
                    'duration_ms': 2000,
                    'longest_ms': 2000,
                },
                {
                    'name': 'wait_agent',
                    'started': 1,
                    'completed': 1,
                    'failed': 0,
                    'incomplete': 0,
                    'duration_ms': 3000,
                    'longest_ms': 3000,
                },
            ],
        )

    def test_spawn_aliases_reconcile_wait_and_list_identities(self):
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'spawn-1',
                    'name': 'spawn_agent',
                    'arguments': '{"task_name":"worker"}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'spawn-1',
                    'output': '{"agent_id":"uuid-1","task_name":"/root/worker"}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'wait-1',
                    'name': 'wait_agent',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'wait-1',
                    'output': '{"status":{"uuid-1":{"completed":"done"}},"timed_out":false}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:04Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'list-1',
                    'name': 'list_agents',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:05Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'list-1',
                    'output': '{"agents":[{"agent_name":"/root/worker","agent_status":{"completed":"done"}}]}',
                },
            },
        ]
        path = self.codex_home / 'sessions' / 'rollout-task-name-session.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8'
        )

        result = self.timing.analyze_codex_tool_activity(
            'task-name-session', self.codex_home
        )

        self.assertEqual(result['coordination']['spawn_successes'], 1)
        self.assertEqual(result['coordination']['completed_agents'], 1)
        self.assertEqual(result['coordination']['observed_peak_live_agents'], 1)
        self.assertEqual(result['coordination']['observed_live_agents_at_end'], 0)

    def test_current_turn_uses_latest_user_boundary_and_cumulative_delta(self):
        self.write_turn_tokens()

        bounds = self.timing.codex_current_turn_bounds(
            'session-main', self.codex_home
        )
        usage = self.timing.build_codex_turn_usage(
            'session-main', self.captured_at, bounds, self.codex_home
        )

        self.assertEqual(
            bounds,
            (
                datetime(2026, 7, 21, 11, tzinfo=timezone.utc),
                datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
            ),
        )
        self.assertEqual(
            usage['totals'],
            {
                'input': 40,
                'output': 15,
                'reasoning': 5,
                'cache_read': 20,
                'cache_write': 0,
                'total_tokens': 80,
                'cost': 0.0,
                'message_count': 0,
                'model_activity_ms': 0,
            },
        )

    def test_current_turn_read_failure_is_failed_with_actual_reason(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{}\n', encoding='utf-8')
        with mock.patch.object(
            Path,
            'read_text',
            side_effect=OSError('permission denied'),
        ):
            bounds, problems = self.timing._codex_current_turn_discovery(
                'session-main', self.codex_home
            )
        usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity('session not requested'),
            None,
            turn_usage=self.timing.build_codex_turn_usage(
                'session-main', self.captured_at, bounds, self.codex_home
            ),
            turn_activity=self.timing.unavailable_tool_activity(
                'Current-turn boundary was not found in the Codex log.'
            ),
            turn_bounds=bounds,
            turn_discovery_problems=problems,
            selected_scope='turn',
        )
        capabilities = {
            capability['name']: capability for capability in report['capabilities']
        }

        self.assertIsNone(bounds)
        self.assertEqual(
            problems,
            ['Codex log could not be read: permission denied'],
        )
        self.assertEqual(capabilities['current turn']['status'], 'failed')
        self.assertEqual(
            capabilities['current turn']['reason'],
            'Codex log could not be read: permission denied',
        )

    def test_current_turn_parse_failure_is_failed_not_missing_boundary(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('not-json\n', encoding='utf-8')

        bounds, problems = self.timing._codex_current_turn_discovery(
            'session-main', self.codex_home
        )
        usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.analyze_codex_tool_activity(
                'session-main', self.codex_home
            ),
            None,
            turn_usage=self.timing.build_codex_turn_usage(
                'session-main', self.captured_at, bounds, self.codex_home
            ),
            turn_activity=self.timing.unavailable_tool_activity(
                'Current-turn boundary was not found in the Codex log.'
            ),
            turn_bounds=bounds,
            turn_discovery_problems=problems,
            selected_scope='turn',
        )
        current_turn = next(
            capability
            for capability in report['capabilities']
            if capability['name'] == 'current turn'
        )

        self.assertIsNone(bounds)
        self.assertEqual(problems, ['1 Codex log line(s) were invalid.'])
        self.assertEqual(current_turn['status'], 'failed')
        self.assertEqual(current_turn['reason'], problems[0])
        self.assertIn(
            'Provide the exact Codex local log for the requested thread',
            report['recovery_prerequisites'][0],
        )

    def test_readable_current_turn_without_boundary_remains_unavailable(self):
        self.write_token_count()
        bounds, problems = self.timing._codex_current_turn_discovery(
            'session-main', self.codex_home
        )
        usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity('session not requested'),
            None,
            turn_usage=self.timing.build_codex_turn_usage(
                'session-main', self.captured_at, bounds, self.codex_home
            ),
            turn_activity=self.timing.unavailable_tool_activity(
                'Current-turn boundary was not found in the Codex log.'
            ),
            turn_bounds=bounds,
            turn_discovery_problems=problems,
            selected_scope='turn',
        )
        current_turn = next(
            capability
            for capability in report['capabilities']
            if capability['name'] == 'current turn'
        )

        self.assertIsNone(bounds)
        self.assertEqual(problems, [])
        self.assertIsNone(
            self.timing.codex_current_turn_bounds('session-main', self.codex_home)
        )
        self.assertEqual(current_turn['status'], 'unavailable')
        self.assertIn('boundary was not found', current_turn['reason'])

    def test_current_turn_token_failure_preserves_complete_report_evidence(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T10:00:00Z',
                'type': 'event_msg',
                'payload': {
                    'type': 'token_count',
                    'info': {
                        'total_token_usage': {
                            'input_tokens': 100,
                            'output_tokens': 20,
                        }
                    },
                },
            },
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'event_msg',
                'payload': {'type': 'user_message'},
            },
            {
                'timestamp': '2026-07-21T12:00:00Z',
                'type': 'event_msg',
                'payload': {
                    'type': 'token_count',
                    'info': {
                        'total_token_usage': {
                            'input_tokens': 90,
                            'output_tokens': 20,
                        }
                    },
                },
            },
        ]
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n',
            encoding='utf-8',
        )
        session_bounds = self.timing.codex_session_bounds(
            'session-main', self.codex_home
        )
        turn_bounds, discovery_problems = (
            self.timing._codex_current_turn_discovery(
                'session-main', self.codex_home
            )
        )
        session_usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
        )
        session_activity = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )
        turn_usage = self.timing._build_codex_turn_usage_evidence(
            'session-main', self.captured_at, turn_bounds, self.codex_home
        )
        turn_activity = self.timing.analyze_codex_tool_activity(
            'session-main',
            self.codex_home,
            turn_bounds[0],
            turn_bounds[1],
        )
        report = self.timing.build_diagnostic_report(
            session_usage,
            session_activity,
            session_bounds,
            turn_usage=turn_usage,
            turn_activity=turn_activity,
            turn_bounds=turn_bounds,
            turn_discovery_problems=discovery_problems,
            selected_scope='both',
        )
        capabilities = {
            capability['name']: capability for capability in report['capabilities']
        }
        rendered = self.timing.render_diagnostic_markdown(report)

        self.assertEqual(turn_usage['status'], 'failed')
        self.assertEqual(
            turn_usage['warnings'],
            ['Codex cumulative token counter decreased for input.'],
        )
        self.assertEqual(capabilities['current turn']['status'], 'failed')
        self.assertEqual(capabilities['session usage']['status'], 'available')
        self.assertEqual(capabilities['model activity']['status'], 'available')
        self.assertEqual(capabilities['tool calls']['status'], 'available')
        self.assertEqual(report['session_usage']['tokens']['status'], 'available')
        self.assertIn('120 total', rendered)
        self.assertIn('- Tokens: failed', rendered)
        self.assertIn(
            'Codex cumulative token counter decreased for input.',
            rendered,
        )

    def test_tool_failures_and_wait_timeouts_are_distinct_evidence(self):
        self.write_wait_timeouts_and_failure()

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['failed_calls'], 1)
        self.assertEqual(result['repeated_identical_calls'], 1)
        self.assertEqual(result['coordination']['wait_timeouts'], 2)
        self.assertEqual(result['coordination']['max_consecutive_wait_timeouts'], 2)
        self.assertEqual(result['coordination']['wait_without_observed_live_agent'], 0)
        self.assertIn('failed-tool-calls', result['findings'])

    def test_current_turn_inherits_observed_live_agent_from_prior_turn(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T10:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'spawn-1',
                    'name': 'spawn_agent',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T10:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'spawn-1',
                    'output': '{"agent_id":"agent-1"}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'event_msg',
                'payload': {'type': 'user_message'},
            },
            {
                'timestamp': '2026-07-21T11:01:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'wait-1',
                    'name': 'wait_agent',
                    'arguments': '{"targets":["agent-1"]}',
                },
            },
            {
                'timestamp': '2026-07-21T11:01:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'wait-1',
                    'output': '{"status":{"agent-1":{"completed":"done"}},"timed_out":false}',
                },
            },
        ]
        path.write_text('\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8')

        result = self.timing.analyze_codex_tool_activity(
            'session-main',
            self.codex_home,
            datetime(2026, 7, 21, 11, tzinfo=timezone.utc),
            datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
        )

        self.assertEqual(result['coordination']['wait_without_observed_live_agent'], 0)
        self.assertEqual(result['coordination']['observed_peak_live_agents'], 1)
        self.assertEqual(result['coordination']['completed_agents'], 1)

    def test_diagnostic_wrapper_does_not_report_itself_as_incomplete(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        windows_command = (
            "$skillRoot = 'C:\\installed\\diagnose-agent-session'; "
            "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
            'powershell -ExecutionPolicy Bypass -File $wrapper diagnose '
            '--scope both --client codex --session-id session-main'
        )
        linux_command = (
            "skill_root='/opt/installed/diagnose-agent-session'\n"
            'sh "$skill_root/scripts/task-metrics.sh" diagnose '
            '--scope both --client codex --session-id session-main'
        )
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'diagnose-1',
                    'name': 'exec',
                    'input': 'powershell -ExecutionPolicy Bypass -File C:/installed/diagnose-agent-session/scripts/task-metrics.ps1 diagnose --scope both',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'diagnose-2',
                    'name': 'exec',
                    'input': {
                        'command': 'sh /opt/skills/diagnose-agent-session/'
                        'scripts/task-metrics.sh diagnose --scope both'
                    },
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'diagnose-3',
                    'name': 'exec',
                    'input': {
                        'cmd': 'powershell.exe -File C:/skills/'
                        'diagnose-agent-session/scripts/task-metrics.ps1 '
                        'diagnose --scope both'
                    },
                },
            },
            {
                'timestamp': '2026-07-21T11:00:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'diagnose-4',
                    'name': 'functions.exec',
                    'input': (
                        'const r = await tools.exec_command('
                        f'{json.dumps({"cmd": windows_command})}); text(r.output);'
                    ),
                },
            },
            {
                'timestamp': '2026-07-21T11:00:04Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'diagnose-5',
                    'name': 'functions.exec',
                    'input': (
                        'const r = await tools.exec_command('
                        f'{json.dumps({"cmd": linux_command})}); text(r.output);'
                    ),
                },
            },
        ]
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8'
        )

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['started_calls'], 0)
        self.assertEqual(result['incomplete_calls'], 0)

    def test_self_call_envelope_must_be_complete_and_unambiguous(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        wrapper = (
            'sh /opt/diagnose-agent-session/scripts/task-metrics.sh diagnose '
            '--scope both --client codex --session-id session-main'
        )
        wrapper_json = json.dumps({'cmd': wrapper})
        canonical = (
            f'const r = await tools.exec_command({wrapper_json}); '
            'text(r.output);'
        )
        second_exec = (
            canonical
            + ' const x = await tools.exec_command('
            + json.dumps({'cmd': 'curl https://example.invalid'})
            + '); text(x.output);'
        )
        side_effect = canonical + ' notify("diagnostic complete");'
        duplicate_cmd = (
            'const r = await tools.exec_command('
            f'{{"cmd":{json.dumps(wrapper)},"cmd":{json.dumps(wrapper)}}}'
            '); text(r.output);'
        )
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'canonical',
                    'name': 'functions.exec',
                    'input': canonical,
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'second-exec',
                    'name': 'functions.exec',
                    'input': second_exec,
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call_output',
                    'call_id': 'second-exec',
                    'output': {'exit_code': 1},
                },
            },
            {
                'timestamp': '2026-07-21T11:00:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'side-effect',
                    'name': 'functions.exec',
                    'input': side_effect,
                },
            },
            {
                'timestamp': '2026-07-21T11:00:04Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'duplicate-cmd',
                    'name': 'functions.exec',
                    'input': duplicate_cmd,
                },
            },
            {
                'timestamp': '2026-07-21T11:00:05Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call_output',
                    'call_id': 'duplicate-cmd',
                    'output': {'exit_code': 0},
                },
            },
        ]
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n',
            encoding='utf-8',
        )

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(
            self.timing._shell_command(
                {'name': 'functions.exec', 'input': {'cmd': wrapper}}
            ),
            wrapper,
        )
        self.assertEqual(
            self.timing._shell_command(
                {'name': 'functions.exec', 'input': wrapper}
            ),
            wrapper,
        )
        self.assertIsNone(
            self.timing._shell_command(
                {
                    'name': 'functions.exec',
                    'input': {'cmd': wrapper, 'command': wrapper},
                }
            )
        )
        self.assertEqual(result['started_calls'], 3)
        self.assertEqual(result['completed_calls'], 2)
        self.assertEqual(result['failed_calls'], 1)
        self.assertEqual(result['incomplete_calls'], 1)
        self.assertIn('failed-tool-calls', result['findings'])
        self.assertIn('incomplete-tool-calls', result['findings'])
        self.assertNotIn('diagnostic complete', json.dumps(result))
        self.assertNotIn('example.invalid', json.dumps(result))

    def test_self_call_object_accepts_only_bounded_transport_fields(self):
        wrapper = (
            'sh /opt/diagnose-agent-session/scripts/task-metrics.sh diagnose '
            '--scope both'
        )
        canonical = (
            'const r = await tools.exec_command('
            f'{json.dumps({"cmd": wrapper})}); text(r.output);'
        )
        negatives = (
            {'cmd': wrapper, 'command': wrapper},
            {'cmd': wrapper, 'environment': {'SIDE_EFFECT': '1'}},
            json.dumps({'cmd': wrapper, 'yield_time_ms': 'soon'}),
            (
                'const r = await tools.exec_command('
                f'{json.dumps({"command": wrapper, "workdir": "/tmp"})}); '
                'text(r.output);'
            ),
            (
                'const r = await tools.exec_command('
                f'{json.dumps({"cmd": wrapper, "unknown": True})}); '
                'text(r.output);'
            ),
        )
        positives = (
            {'cmd': wrapper},
            {'command': wrapper},
            {'cmd': wrapper, 'shell': 'sh', 'login': False, 'workdir': '/tmp'},
            json.dumps({'cmd': wrapper}),
            json.dumps({'command': wrapper}),
            json.dumps({'cmd': wrapper, 'sandbox_permissions': 'use_default'}),
            (
                'const r = await tools.exec_command('
                f'{json.dumps({"cmd": wrapper, "shell": "sh"})}); '
                'text(r.output);'
            ),
            canonical,
            wrapper,
        )

        for value in positives:
            with self.subTest(value=value, expected='trusted'):
                self.assertEqual(
                    self.timing._shell_command(
                        {'name': 'functions.exec', 'input': value}
                    ),
                    wrapper,
                )
        for value in negatives:
            with self.subTest(value=value, expected='visible'):
                self.assertIsNone(
                    self.timing._shell_command(
                        {'name': 'functions.exec', 'input': value}
                    )
                )

        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'configured-wrapper',
                    'name': 'functions.exec',
                    'input': {'cmd': wrapper, 'shell': 'sh'},
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call_output',
                    'call_id': 'configured-wrapper',
                    'output': {'exit_code': 1},
                },
            },
        ]
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n',
            encoding='utf-8',
        )

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['started_calls'], 0)
        self.assertEqual(result['completed_calls'], 0)
        self.assertEqual(result['failed_calls'], 0)
        self.assertNotIn('failed-tool-calls', result['findings'])

    def test_inspecting_diagnostic_files_remains_visible(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        inspection_command = (
            'rg "skill_root=.*task-metrics.sh.*diagnose" '
            'skills/diagnose-agent-session'
        )
        lookalike_command = (
            "$skillRoot = 'C:\\installed\\diagnose-agent-session'; "
            "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics-copy.ps1'; "
            'powershell -File $wrapper diagnose --scope both'
        )
        unrelated_root_command = (
            "$skillRoot = 'C:\\installed\\another-skill'; "
            "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
            'powershell -File $wrapper diagnose --scope both'
        )
        chained_command = (
            "skill_root='/opt/installed/diagnose-agent-session'\n"
            'sh "$skill_root/scripts/task-metrics.sh" diagnose '
            '--scope both && echo done'
        )
        direct_prefixed_compound = (
            'powershell -Command Write-Output pre; powershell '
            '-ExecutionPolicy Bypass -File '
            'C:/installed/diagnose-agent-session/scripts/task-metrics.ps1 '
            'diagnose --scope both'
        )
        root_prefixed_compound = (
            "$skillRoot = 'C:\\installed\\diagnose-agent-session'; "
            "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
            'powershell -Command Write-Output pre; powershell '
            '-ExecutionPolicy Bypass -File $wrapper diagnose --scope both'
        )
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'inspect-1',
                    'name': 'exec',
                    'input': 'const r = await tools.shell_command({command:"rg \'powershell.exe -File skills/diagnose-agent-session/scripts/task-metrics.ps1 diagnose\' ."}); text(r);',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call_output',
                    'call_id': 'inspect-1',
                    'output': 'ok',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'inspect-2',
                    'name': 'functions.exec',
                    'input': (
                        'const r = await tools.exec_command('
                        f'{json.dumps({"cmd": inspection_command})}); text(r.output);'
                    ),
                },
            },
            {
                'timestamp': '2026-07-21T11:00:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'inspect-3',
                    'name': 'functions.exec',
                    'input': (
                        'const r = await tools.exec_command('
                        f'{json.dumps({"cmd": lookalike_command})}); text(r.output);'
                    ),
                },
            },
            {
                'timestamp': '2026-07-21T11:00:04Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'inspect-4',
                    'name': 'functions.exec',
                    'input': (
                        'const r = await tools.exec_command('
                        f'{json.dumps({"cmd": unrelated_root_command})}); '
                        'text(r.output);'
                    ),
                },
            },
            {
                'timestamp': '2026-07-21T11:00:05Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'inspect-5',
                    'name': 'functions.exec',
                    'input': (
                        'const r = await tools.exec_command('
                        f'{json.dumps({"cmd": chained_command})}); text(r.output);'
                    ),
                },
            },
            {
                'timestamp': '2026-07-21T11:00:06Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'inspect-6',
                    'name': 'functions.exec',
                    'input': (
                        'const r = await tools.exec_command('
                        f'{json.dumps({"cmd": direct_prefixed_compound})}); '
                        'text(r.output);'
                    ),
                },
            },
            {
                'timestamp': '2026-07-21T11:00:07Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'inspect-7',
                    'name': 'functions.exec',
                    'input': (
                        'const r = await tools.exec_command('
                        f'{json.dumps({"cmd": root_prefixed_compound})}); '
                        'text(r.output);'
                    ),
                },
            },
        ]
        path.write_text('\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8')

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['started_calls'], 7)
        self.assertEqual(result['completed_calls'], 1)
        self.assertEqual(result['incomplete_calls'], 6)

    def test_powershell_self_call_requires_safe_horizontal_tokens_and_path(self):
        positives = (
            (
                'powershell -ExecutionPolicy Bypass -File '
                '"C:/Program Files/diagnose-agent-session/scripts/task-metrics.ps1" '
                'diagnose --client codex --session-id session-main --scope both'
            ),
            (
                'powershell -ExecutionPolicy Bypass -File '
                '"C:/程序 Files (x86)/diagnose-agent-session/scripts/task-metrics.ps1" '
                'diagnose --client codex --session-id session-main --scope both'
            ),
        )
        negatives = (
            (
                'powershell\n-ExecutionPolicy Bypass -File '
                'C:/installed/diagnose-agent-session/scripts/task-metrics.ps1 '
                'diagnose --scope both'
            ),
            (
                "$skillRoot = 'C:\\installed\\diagnose-agent-session'; "
                "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
                'powershell\n-ExecutionPolicy Bypass -File $wrapper '
                'diagnose --scope both'
            ),
            (
                'powershell -File C:/prefix;C:/installed/'
                'diagnose-agent-session/scripts/task-metrics.ps1 '
                'diagnose --scope both'
            ),
            (
                'powershell -File "C:/prefix|C:/installed/'
                'diagnose-agent-session/scripts/task-metrics.ps1" '
                'diagnose --scope both'
            ),
        )

        for command in positives:
            with self.subTest(command=command, expected='trusted'):
                self.assertTrue(
                    self.timing._is_diagnostic_call(
                        {
                            'name': 'functions.exec',
                            'input': {
                                'cmd': command,
                                'shell': 'cmd.exe',
                                'workdir': 'C:/work',
                                'login': False,
                            },
                        }
                    )
                )
        for command in negatives:
            with self.subTest(command=command):
                self.assertFalse(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )

    def test_self_call_trust_requires_literals_paired_quotes_and_shell_assignment(self):
        negatives = (
            (
                'powershell -File "C:/$(Write-Output bad)/'
                'diagnose-agent-session/scripts/task-metrics.ps1" '
                'diagnose --scope both'
            ),
            (
                '$skillRoot = "C:\\$(Write-Output bad)\\'
                'diagnose-agent-session"; '
                "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
                'powershell -File $wrapper diagnose --scope both'
            ),
            (
                'powershell -File C:/installed/diagnose-agent-session/'
                'scripts/task-metrics.ps1 diagnose --session-id $(Get-Date)'
            ),
            (
                "$skillRoot = 'C:\\installed\\diagnose-agent-session'; "
                '$wrapper = Join-Path $skillRoot '
                "'scripts\\task-metrics.ps1\"; "
                'powershell -File $wrapper diagnose --scope both'
            ),
            (
                "skill_root='/opt/diagnose-agent-session\"\n"
                'sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both'
            ),
            (
                "skill_root='/opt/diagnose-agent-session'\n"
                'sh "$skill_root/scripts/task-metrics.sh\' diagnose --scope both'
            ),
            (
                "skill_root = '/opt/diagnose-agent-session'\n"
                'sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both'
            ),
        )

        for command in negatives:
            with self.subTest(command=command):
                self.assertFalse(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )

    def test_linux_self_call_trust_rejects_shell_substitution_fragments(self):
        negatives = (
            (
                'sh "/opt/$(pwd)/diagnose-agent-session/scripts/'
                'task-metrics.sh" diagnose --scope both'
            ),
            (
                'sh /opt/$HOME/diagnose-agent-session/scripts/'
                'task-metrics.sh diagnose --scope both'
            ),
            (
                'sh "/opt/`pwd`/diagnose-agent-session/scripts/'
                'task-metrics.sh" diagnose --scope both'
            ),
            (
                'skill_root="/opt/$(pwd)/diagnose-agent-session"\n'
                'sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both'
            ),
            (
                'skill_root="/opt/$HOME/diagnose-agent-session"\n'
                'sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both'
            ),
            (
                'skill_root="/opt/`pwd`/diagnose-agent-session"\n'
                'sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both'
            ),
            (
                'sh /opt/diagnose-agent-session/scripts/task-metrics.sh '
                'diagnose --session-id `date` --scope both'
            ),
        )

        for command in negatives:
            with self.subTest(command=command):
                self.assertFalse(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )

    def test_self_call_trust_rejects_shell_active_literal_metacharacters(self):
        negatives = (
            (
                'sh "/opt/*/diagnose-agent-session/scripts/task-metrics.sh" '
                'diagnose --scope both'
            ),
            (
                "skill_root='/opt/>/diagnose-agent-session'\n"
                'sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both'
            ),
            (
                'powershell -File "C:/?/diagnose-agent-session/scripts/'
                'task-metrics.ps1" diagnose --scope both'
            ),
            (
                "$skillRoot = 'C:\\{dynamic}\\diagnose-agent-session'; "
                "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
                'powershell -File $wrapper diagnose --scope both'
            ),
            (
                'sh /opt/diagnose-agent-session/scripts/task-metrics.sh '
                'diagnose --scope both --session-id session>capture.txt'
            ),
        )

        for command in negatives:
            with self.subTest(command=command):
                self.assertFalse(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )

    def test_self_call_literal_atoms_reject_ambiguous_path_and_session_syntax(self):
        positives = (
            (
                'sh "/opt/Smart Kit/diagnose-agent-session/scripts/'
                'task-metrics.sh" diagnose --session-id session-01 --scope both'
            ),
            (
                "$skillRoot = 'C:\\Smart Kit\\diagnose-agent-session'; "
                "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
                'powershell -ExecutionPolicy Bypass -File $wrapper '
                'diagnose --scope both --session-id session-01'
            ),
        )
        negatives = (
            'sh /opt/~/diagnose-agent-session/scripts/task-metrics.sh diagnose',
            'sh /opt/#note/diagnose-agent-session/scripts/task-metrics.sh diagnose',
            "sh /opt/'quoted'/diagnose-agent-session/scripts/task-metrics.sh diagnose",
            'sh /opt\\escaped/diagnose-agent-session/scripts/task-metrics.sh diagnose',
            (
                "skill_root='/opt/~/diagnose-agent-session'\n"
                'sh "$skill_root/scripts/task-metrics.sh" diagnose'
            ),
            (
                "skill_root='/opt\\escaped/diagnose-agent-session'\n"
                'sh "$skill_root/scripts/task-metrics.sh" diagnose'
            ),
            (
                "$skillRoot = 'C:\\#note\\diagnose-agent-session'; "
                "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
                'powershell -File $wrapper diagnose'
            ),
            (
                'powershell -File C:/~/diagnose-agent-session/scripts/'
                'task-metrics.ps1 diagnose'
            ),
            (
                'sh /opt/diagnose-agent-session/scripts/task-metrics.sh '
                'diagnose --session-id session#note'
            ),
            (
                'sh /opt/diagnose-agent-session/scripts/task-metrics.sh '
                'diagnose --session-id session~home'
            ),
            (
                'sh /opt/diagnose-agent-session/scripts/task-metrics.sh '
                'diagnose --session-id session\\escaped'
            ),
            (
                'powershell -File C:/installed/diagnose-agent-session/scripts/'
                'task-metrics.ps1 diagnose --session-id session"quoted'
            ),
        )

        for command in positives:
            with self.subTest(command=command):
                self.assertTrue(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )
        for command in negatives:
            with self.subTest(command=command):
                self.assertFalse(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )

    def test_self_call_trust_requires_absolute_wrapper_and_root_paths(self):
        positives = (
            'sh "/opt/Smart Kit/diagnose-agent-session/scripts/task-metrics.sh" '
            'diagnose --scope both',
            'powershell -File '
            '"C:/Smart Kit/diagnose-agent-session/scripts/task-metrics.ps1" '
            'diagnose --scope both',
            'powershell -File '
            '"\\\\server\\share\\diagnose-agent-session\\scripts\\task-metrics.ps1" '
            'diagnose --scope both',
            "skill_root='/opt/Smart Kit/diagnose-agent-session'\n"
            'sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both',
            "$skillRoot = 'C:\\Smart Kit\\diagnose-agent-session'; "
            "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
            'powershell -File $wrapper diagnose --scope both',
        )
        negatives = (
            'sh ./diagnose-agent-session/scripts/task-metrics.sh diagnose',
            'sh diagnose-agent-session/scripts/task-metrics.sh diagnose',
            'powershell -File .\\diagnose-agent-session\\scripts\\task-metrics.ps1 '
            'diagnose',
            'powershell -File diagnose-agent-session/scripts/task-metrics.ps1 '
            'diagnose',
            "skill_root='relative/diagnose-agent-session'\n"
            'sh "$skill_root/scripts/task-metrics.sh" diagnose',
            "$skillRoot = 'relative\\diagnose-agent-session'; "
            "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
            'powershell -File $wrapper diagnose',
        )

        for command in positives:
            with self.subTest(command=command):
                self.assertTrue(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )
        for command in negatives:
            with self.subTest(command=command):
                self.assertFalse(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )

    def test_self_call_skill_name_must_be_an_exact_path_segment(self):
        positives = (
            'sh /diagnose-agent-session/scripts/task-metrics.sh diagnose',
            'sh "/opt/Smart Kit/diagnose-agent-session/scripts/task-metrics.sh" '
            'diagnose --scope both',
            "skill_root='/diagnose-agent-session'\n"
            'sh "$skill_root/scripts/task-metrics.sh" diagnose',
            'powershell -File C:/diagnose-agent-session/scripts/'
            'task-metrics.ps1 diagnose',
            'powershell -File "\\\\server\\share\\diagnose-agent-session\\scripts\\'
            'task-metrics.ps1" diagnose',
            "$skillRoot = '\\\\server\\share\\diagnose-agent-session'; "
            "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
            'powershell -File $wrapper diagnose',
        )
        negatives = (
            'sh /opt/not-diagnose-agent-session/scripts/task-metrics.sh diagnose',
            "skill_root='/opt/not-diagnose-agent-session'\n"
            'sh "$skill_root/scripts/task-metrics.sh" diagnose',
            'powershell -File C:/opt/not-diagnose-agent-session/scripts/'
            'task-metrics.ps1 diagnose',
            "$skillRoot = 'C:\\opt\\not-diagnose-agent-session'; "
            "$wrapper = Join-Path $skillRoot 'scripts\\task-metrics.ps1'; "
            'powershell -File $wrapper diagnose',
        )

        for command in positives:
            with self.subTest(command=command):
                self.assertTrue(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )
        for command in negatives:
            with self.subTest(command=command):
                self.assertFalse(
                    self.timing._is_diagnostic_call(
                        {'name': 'functions.exec', 'input': {'cmd': command}}
                    )
                )

    def test_list_agents_updates_observed_lifecycle_lower_bounds(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T10:59:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'spawn-1',
                    'name': 'spawn_agent',
                    'arguments': '{"task_name":"worker"}',
                },
            },
            {
                'timestamp': '2026-07-21T10:59:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'spawn-1',
                    'output': '{"task_name":"/root/worker"}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'list-1',
                    'name': 'list_agents',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'list-1',
                    'output': json.dumps(
                        {
                            'agents': [
                                {
                                    'agent_name': '/root',
                                    'agent_status': {'running': 'root'},
                                },
                                {
                                    'agent_name': '/root/worker',
                                    'agent_status': {'running': 'working'},
                                },
                                {
                                    'agent_name': '/root/done',
                                    'agent_status': {'completed': 'done'},
                                },
                                {
                                    'agent_name': '/root/failed',
                                    'agent_status': {'failed': 'boom'},
                                },
                            ]
                        }
                    ),
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'list-2',
                    'name': 'list_agents',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'list-2',
                    'output': json.dumps(
                        {
                            'agents': [
                                {
                                    'agent_name': '/root',
                                    'agent_status': {'running': 'root'},
                                },
                                {
                                    'agent_name': '/root/worker',
                                    'agent_status': {'completed': 'done'},
                                },
                                {
                                    'agent_name': '/root/done',
                                    'agent_status': {'completed': 'done'},
                                },
                                {
                                    'agent_name': '/root/failed',
                                    'agent_status': {'failed': 'boom'},
                                },
                            ]
                        }
                    ),
                },
            },
            {
                'timestamp': '2026-07-21T11:01:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'wait-1',
                    'name': 'wait_agent',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:01:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'wait-1',
                    'output': '{"status":{},"timed_out":true}',
                },
            },
        ]
        path.write_text('\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8')

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['coordination']['observed_peak_live_agents'], 1)
        self.assertEqual(result['coordination']['completed_agents'], 2)
        self.assertEqual(result['coordination']['failed_agents'], 1)
        self.assertEqual(result['coordination']['observed_live_agents_at_end'], 0)
        self.assertEqual(result['coordination']['wait_without_observed_live_agent'], 1)

    def test_list_snapshot_clears_disappeared_spawned_agent(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'spawn-1',
                    'name': 'spawn_agent',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'spawn-1',
                    'output': '{"task_name":"/root/worker"}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'list-1',
                    'name': 'list_agents',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'list-1',
                    'output': '{"agents":[{"agent_name":"/root","agent_status":{"running":"root"}}]}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:04Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'wait-1',
                    'name': 'wait_agent',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:05Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'wait-1',
                    'output': '{"status":{},"timed_out":true}',
                },
            },
        ]
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8'
        )

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['coordination']['observed_peak_live_agents'], 1)
        self.assertEqual(result['coordination']['observed_live_agents_at_end'], 0)
        self.assertEqual(result['coordination']['wait_without_observed_live_agent'], 1)

    def test_terminal_agent_counts_union_wait_and_list_identities(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'wait-1',
                    'name': 'wait_agent',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'wait-1',
                    'output': json.dumps(
                        {
                            'status': {
                                '/root/wait-done': {'completed': 'done'},
                                '/root/wait-failed': {'failed': 'boom'},
                            },
                            'timed_out': False,
                        }
                    ),
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'list-1',
                    'name': 'list_agents',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'list-1',
                    'output': json.dumps(
                        {
                            'agents': [
                                {
                                    'agent_name': '/root/wait-done',
                                    'agent_status': {'completed': 'done'},
                                },
                                {
                                    'agent_name': '/root/wait-failed',
                                    'agent_status': {'failed': 'boom'},
                                },
                                {
                                    'agent_name': '/root/list-done',
                                    'agent_status': {'completed': 'done'},
                                },
                                {
                                    'agent_name': '/root/list-failed',
                                    'agent_status': {'failed': 'boom'},
                                },
                            ]
                        }
                    ),
                },
            },
        ]
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8'
        )

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['coordination']['completed_agents'], 2)
        self.assertEqual(result['coordination']['failed_agents'], 2)

    def test_current_turn_timeout_streak_excludes_prior_turns(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = []
        for index, minute in enumerate((0, 1), start=1):
            events.extend(
                [
                    {
                        'timestamp': f'2026-07-21T10:0{minute}:00Z',
                        'type': 'response_item',
                        'payload': {
                            'type': 'function_call',
                            'call_id': f'wait-{index}',
                            'name': 'wait_agent',
                            'arguments': '{}',
                        },
                    },
                    {
                        'timestamp': f'2026-07-21T10:0{minute}:01Z',
                        'type': 'response_item',
                        'payload': {
                            'type': 'function_call_output',
                            'call_id': f'wait-{index}',
                            'output': '{"status":{},"timed_out":true}',
                        },
                    },
                ]
            )
        events.append(
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'event_msg',
                'payload': {'type': 'user_message'},
            }
        )
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8'
        )

        result = self.timing.analyze_codex_tool_activity(
            'session-main',
            self.codex_home,
            datetime(2026, 7, 21, 11, tzinfo=timezone.utc),
            datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
        )

        self.assertEqual(result['coordination']['wait_agent'], 0)
        self.assertEqual(result['coordination']['wait_timeouts'], 0)
        self.assertEqual(result['coordination']['max_consecutive_wait_timeouts'], 0)

    def test_structured_tool_error_is_counted_without_persisting_output(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'exec-1',
                    'name': 'exec',
                    'input': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call_output',
                    'call_id': 'exec-1',
                    'output': [{'type': 'text', 'text': 'Script error:\nExit code: 1'}],
                },
            },
        ]
        path.write_text('\n'.join(json.dumps(event) for event in events) + '\n', encoding='utf-8')

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['failed_calls'], 1)
        self.assertNotIn('Script error', json.dumps(result))

    def test_nonzero_execution_exits_are_normalized_as_tool_failures(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        outputs = (
            {'exit_code': 1},
            {'exitCode': '2'},
            {'returncode': -1},
            {'return_code': 3.0},
            'Process exited with code 1',
            {'exit_code': 0},
            {'return_code': False},
            {'items_processed': 99},
            'Processed 12 items successfully',
        )
        events = []
        for index, output in enumerate(outputs):
            call_id = f'exec-{index}'
            events.extend(
                [
                    {
                        'timestamp': f'2026-07-21T11:00:{index * 2:02d}Z',
                        'type': 'response_item',
                        'payload': {
                            'type': 'custom_tool_call',
                            'call_id': call_id,
                            'name': 'exec',
                            'input': '{}',
                        },
                    },
                    {
                        'timestamp': f'2026-07-21T11:00:{index * 2 + 1:02d}Z',
                        'type': 'response_item',
                        'payload': {
                            'type': 'custom_tool_call_output',
                            'call_id': call_id,
                            'output': output,
                        },
                    },
                ]
            )
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n',
            encoding='utf-8',
        )

        result = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )

        self.assertEqual(result['completed_calls'], len(outputs))
        self.assertEqual(result['failed_calls'], 5)
        self.assertIn('failed-tool-calls', result['findings'])
        serialized = json.dumps(result)
        self.assertNotIn('Process exited with code 1', serialized)
        self.assertNotIn('items_processed', serialized)

    def test_outer_success_status_overrides_incidental_exit_text(self):
        successful = (
            {
                'exit_code': 0,
                'output': 'A child process exited with code 1 as expected.',
            },
            {'exit_code': 0, 'output': '{"exit_code": 1}'},
            {'status': 'completed', 'message': 'Process exited with code 1.'},
        )
        for output in successful:
            with self.subTest(output=output):
                self.assertFalse(self.timing._tool_failed(output))

        self.assertTrue(
            self.timing._tool_failed({'exit_code': 1, 'output': 'all good'})
        )
        self.assertTrue(self.timing._tool_failed('Process exited with code 1.'))

    def test_diagnostic_output_keeps_usage_and_tool_evidence_separate(self):
        usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
            codex_home=self.codex_home,
        )
        self.write_tool_calls()
        activity = self.timing.analyze_codex_tool_activity(
            'session-main', self.codex_home
        )
        report = self.timing.build_diagnostic_report(
            usage,
            activity,
            (
                datetime(2026, 7, 21, 11, tzinfo=timezone.utc),
                datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
            ),
            selected_scope='session',
        )

        rendered = self.timing.render_diagnostic_markdown(report)

        self.assertIn('### Agent Session Diagnostics', rendered)
        self.assertIn('120 total', rendered)
        self.assertIn('spawn_agent=1', rendered)
        self.assertIn('wait_agent=1', rendered)
        self.assertIn('whole session: incomplete-tool-calls', rendered)

    def test_session_usage_is_unavailable_only_when_both_sources_fail(self):
        result = self.timing.build_session_usage(
            'codex',
            'missing-session',
            self.captured_at,
            tokscale_rows=[],
            snapshot_error='Tokscale executable was not found.',
            codex_home=self.codex_home,
        )

        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['cost_status'], 'unavailable')
        self.assertEqual(result['totals']['total_tokens'], 0)

    def test_recovery_accumulates_tokscale_and_missing_codex_log_paths(self):
        usage = self.timing.build_session_usage(
            'codex',
            'missing-session',
            self.captured_at,
            tokscale_rows=[],
            snapshot_error='Tokscale executable was not found.',
            codex_home=self.codex_home,
        )
        activity = self.timing.analyze_codex_tool_activity(
            'missing-session', self.codex_home
        )
        report = self.timing.build_diagnostic_report(
            usage,
            activity,
            None,
            selected_scope='session',
        )

        self.assertEqual(len(report['recovery_prerequisites']), 2)
        self.assertIn(
            'Resolve the reported Tokscale collection failure',
            report['recovery_prerequisites'][0],
        )
        self.assertIn(
            'Provide the exact Codex local log for the requested thread',
            report['recovery_prerequisites'][1],
        )

    def test_no_event_activity_uses_the_public_unavailable_record_shape(self):
        result = self.timing.analyze_codex_tool_activity(
            'missing-session', self.codex_home
        )
        row = self.usage_row()
        row['sessionId'] = 'rollout-missing-session'
        usage = self.timing.build_session_usage(
            'codex',
            'missing-session',
            self.captured_at,
            tokscale_rows=[row],
        )
        report = self.timing.build_diagnostic_report(
            usage,
            result,
            None,
            selected_scope='session',
        )

        public_shape = self.timing.unavailable_tool_activity(
            'Codex log was not found.'
        )
        self.assertEqual(
            {key: result[key] for key in public_shape},
            public_shape,
        )
        self.assertEqual(
            result['acquisition'],
            {
                'outcome': 'unavailable',
                'causes': [
                    {
                        'kind': 'no-matching-log',
                        'message': 'Codex log was not found.',
                    }
                ],
            },
        )
        self.assertIn(
            'Provide the exact Codex local log for the requested thread',
            report['recovery_prerequisites'][0],
        )
        self.assertNotIn(
            'None identified',
            self.timing.render_diagnostic_markdown(report),
        )

    def test_codex_snapshot_structurally_distinguishes_acquisition_states(self):
        missing = self.timing._load_codex_log_snapshot(
            'missing-session', self.codex_home
        )
        malformed_path = (
            self.codex_home / 'sessions' / 'rollout-malformed-session.jsonl'
        )
        malformed_path.parent.mkdir(parents=True, exist_ok=True)
        malformed_path.write_text('not-json\n', encoding='utf-8')
        malformed = self.timing._load_codex_log_snapshot(
            'malformed-session', self.codex_home
        )

        self.assertEqual(missing['acquisition']['outcome'], 'unavailable')
        self.assertEqual(
            missing['acquisition']['causes'][0]['kind'], 'no-matching-log'
        )
        self.assertEqual(missing['warnings'], [])
        self.assertEqual(malformed['acquisition']['outcome'], 'failed')
        self.assertEqual(malformed['acquisition']['causes'][0]['kind'], 'malformed')
        self.assertEqual(
            malformed['warnings'], ['1 Codex log line(s) were invalid.']
        )

    def test_schema_incompatible_codex_lines_fail_surfaces_not_the_report(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        valid_events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'event_msg',
                'payload': {'type': 'user_message'},
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'event_msg',
                'payload': {
                    'type': 'token_count',
                    'info': {
                        'total_token_usage': {
                            'input_tokens': 10,
                            'output_tokens': 2,
                        }
                    },
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'tool-1',
                    'name': 'exec',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'tool-1',
                    'output': 'ok',
                },
            },
        ]
        incompatible = {
            'nonobject-event': [],
            'nonobject-payload': {
                'timestamp': '2026-07-21T10:59:00Z',
                'payload': [],
            },
            'nonobject-info': {
                'timestamp': '2026-07-21T10:59:00Z',
                'payload': {'type': 'token_count', 'info': []},
            },
            'nonobject-total': {
                'timestamp': '2026-07-21T10:59:00Z',
                'payload': {
                    'type': 'token_count',
                    'info': {'total_token_usage': []},
                },
            },
        }
        for name, incompatible_event in incompatible.items():
            with self.subTest(name=name):
                path.write_text(
                    '\n'.join(
                        json.dumps(event)
                        for event in [incompatible_event, *valid_events]
                    )
                    + '\n',
                    encoding='utf-8',
                )
                snapshot = self.timing._load_codex_log_snapshot(
                    'session-main', self.codex_home
                )
                bounds = self.timing.codex_session_bounds(
                    'session-main', snapshot=snapshot
                )
                turn_bounds, turn_problems = (
                    self.timing._codex_current_turn_discovery(
                        'session-main', snapshot=snapshot
                    )
                )
                usage = self.timing.build_session_usage(
                    'codex',
                    'session-main',
                    self.captured_at,
                    tokscale_rows=[self.usage_row()],
                    codex_snapshot=snapshot,
                )
                session_activity = self.timing.analyze_codex_tool_activity(
                    'session-main', snapshot=snapshot
                )
                turn_usage = self.timing._build_codex_turn_usage_evidence(
                    'session-main',
                    self.captured_at,
                    turn_bounds,
                    codex_snapshot=snapshot,
                )
                turn_activity = self.timing.analyze_codex_tool_activity(
                    'session-main',
                    started_at=turn_bounds[0],
                    ended_at=turn_bounds[1],
                    snapshot=snapshot,
                )
                report = self.timing.build_diagnostic_report(
                    usage,
                    session_activity,
                    bounds,
                    turn_usage=turn_usage,
                    turn_activity=turn_activity,
                    turn_bounds=turn_bounds,
                    turn_discovery_problems=turn_problems,
                    selected_scope='both',
                    codex_acquisition=snapshot['acquisition'],
                )
                capabilities = {
                    item['name']: item for item in report['capabilities']
                }

                self.assertEqual(snapshot['acquisition']['outcome'], 'failed')
                self.assertEqual(len(snapshot['events']), len(valid_events))
                self.assertEqual(usage['status'], 'available')
                self.assertEqual(session_activity['status'], 'failed')
                self.assertEqual(session_activity['completed_calls'], 1)
                self.assertEqual(turn_activity['status'], 'failed')
                self.assertEqual(turn_activity['completed_calls'], 1)
                self.assertEqual(capabilities['session usage']['status'], 'available')
                self.assertEqual(capabilities['model activity']['status'], 'available')
                self.assertEqual(capabilities['current turn']['status'], 'failed')
                self.assertEqual(capabilities['tool calls']['status'], 'failed')
                self.assertIn(
                    'Provide the exact Codex local log for the requested thread',
                    report['recovery_prerequisites'][0],
                )
                rendered = self.timing.render_diagnostic_markdown(report)
                self.assertIn('Observed tool calls: 1 started, 1 completed', rendered)

    def test_schema_invalid_tool_events_fail_without_losing_valid_events(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {
                'timestamp': '2026-07-21T11:00:00Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'good',
                    'name': 'exec',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:01Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'good',
                    'output': {'exit_code': 0},
                },
            },
            {
                'timestamp': '2026-07-21T11:00:02Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'name': 'exec',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:03Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'missing-output',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:04Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'duplicate',
                    'name': 'exec',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:05Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'duplicate',
                    'name': 'exec',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:06Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'duplicate',
                    'output': {'exit_code': 0},
                },
            },
            {
                'timestamp': '2026-07-21T11:00:07Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'orphan',
                    'output': {'exit_code': 0},
                },
            },
            {
                'timestamp': '2026-07-21T11:00:08Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call',
                    'call_id': 'mismatch-function',
                    'name': 'exec',
                    'arguments': '{}',
                },
            },
            {
                'timestamp': '2026-07-21T11:00:09Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call_output',
                    'call_id': 'mismatch-function',
                    'output': {'exit_code': 0},
                },
            },
            {
                'timestamp': '2026-07-21T11:00:10Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call',
                    'call_id': 'mismatch-custom',
                    'name': 'exec',
                    'input': {},
                },
            },
            {
                'timestamp': '2026-07-21T11:00:11Z',
                'type': 'response_item',
                'payload': {
                    'type': 'function_call_output',
                    'call_id': 'mismatch-custom',
                    'output': {'exit_code': 0},
                },
            },
            {
                'timestamp': '2026-07-21T11:00:12Z',
                'type': 'response_item',
                'payload': {
                    'type': 'custom_tool_call_output',
                    'call_id': 'mismatch-custom',
                    'output': {'exit_code': 0},
                },
            },
        ]
        path.write_text(
            '\n'.join(json.dumps(event) for event in events) + '\n',
            encoding='utf-8',
        )

        snapshot = self.timing._load_codex_log_snapshot(
            'session-main', self.codex_home
        )
        activity = self.timing.analyze_codex_tool_activity(
            'session-main', snapshot=snapshot
        )

        self.assertEqual(snapshot['acquisition']['outcome'], 'failed')
        self.assertEqual(len(snapshot['events']), 7)
        self.assertEqual(activity['status'], 'failed')
        self.assertEqual(activity['started_calls'], 4)
        self.assertEqual(activity['completed_calls'], 3)
        self.assertEqual(activity['incomplete_calls'], 1)

    def test_local_content_is_immutable_before_cutoff_is_recorded(self):
        path = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        valid_event = {
            'timestamp': '2026-07-21T11:00:00Z',
            'type': 'event_msg',
            'payload': {'type': 'user_message'},
        }
        path.write_text(json.dumps(valid_event) + '\n', encoding='utf-8')
        original_read_text = Path.read_text

        def read_then_append(path_object, *args, **kwargs):
            immutable_content = original_read_text(path_object, *args, **kwargs)
            path_object.write_text(
                immutable_content + 'concurrently-appended-malformed-line\n',
                encoding='utf-8',
            )
            return immutable_content

        with mock.patch.object(
            Path,
            'read_text',
            autospec=True,
            side_effect=read_then_append,
        ) as read_text:
            snapshot = self.timing._load_codex_log_snapshot(
                'session-main',
                self.codex_home,
                capture_cutoff_after_read=True,
            )

        self.assertEqual(read_text.call_count, 1)
        self.assertEqual(snapshot['acquisition']['outcome'], 'available')
        self.assertEqual(len(snapshot['events']), 1)
        self.assertIsNotNone(snapshot['captured_at'])
        self.assertIn(
            'concurrently-appended-malformed-line',
            path.read_text(encoding='utf-8'),
        )

    def test_multiple_codex_log_candidates_fail_without_read_or_aggregation(self):
        active = self.codex_home / 'sessions' / 'rollout-session-main.jsonl'
        archived = (
            self.codex_home
            / 'archived_sessions'
            / 'rollout-session-main.jsonl'
        )
        active.parent.mkdir(parents=True, exist_ok=True)
        archived.parent.mkdir(parents=True, exist_ok=True)
        for path, call_id in ((active, 'active-call'), (archived, 'archived-call')):
            path.write_text(
                json.dumps(
                    {
                        'timestamp': '2026-07-21T11:00:00Z',
                        'type': 'response_item',
                        'payload': {
                            'type': 'function_call',
                            'call_id': call_id,
                            'name': 'exec',
                            'arguments': '{}',
                        },
                    }
                )
                + '\n',
                encoding='utf-8',
            )

        with mock.patch.object(
            Path,
            'read_text',
            side_effect=AssertionError('ambiguous candidates must not be read'),
        ) as read_text:
            snapshot = self.timing._load_codex_log_snapshot(
                'session-main',
                self.codex_home,
                capture_cutoff_after_read=True,
            )

        usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
            codex_snapshot=snapshot,
        )
        activity = self.timing.analyze_codex_tool_activity(
            'session-main', snapshot=snapshot
        )
        turn_bounds, turn_problems = self.timing._codex_current_turn_discovery(
            'session-main', snapshot=snapshot
        )
        turn_usage = self.timing._build_codex_turn_usage_evidence(
            'session-main',
            self.captured_at,
            turn_bounds,
            codex_snapshot=snapshot,
        )
        turn_activity = self.timing.analyze_codex_tool_activity(
            'session-main', snapshot=snapshot
        )
        report = self.timing.build_diagnostic_report(
            usage,
            activity,
            None,
            turn_usage=turn_usage,
            turn_activity=turn_activity,
            turn_bounds=turn_bounds,
            turn_discovery_problems=turn_problems,
            selected_scope='both',
            codex_acquisition=snapshot['acquisition'],
        )
        capabilities = {
            item['name']: item for item in report['capabilities']
        }
        rendered = self.timing.render_diagnostic_markdown(report)

        self.assertEqual(read_text.call_count, 0)
        self.assertEqual(snapshot['events'], [])
        self.assertIsNotNone(snapshot['captured_at'])
        self.assertEqual(snapshot['acquisition']['outcome'], 'failed')
        self.assertEqual(
            snapshot['acquisition']['causes'][0]['kind'],
            'ambiguous-multiple-logs',
        )
        self.assertEqual(usage['status'], 'available')
        self.assertEqual(activity['status'], 'failed')
        self.assertEqual(activity['started_calls'], 0)
        self.assertEqual(capabilities['session usage']['status'], 'available')
        self.assertEqual(capabilities['model activity']['status'], 'available')
        self.assertEqual(capabilities['current turn']['status'], 'failed')
        self.assertEqual(capabilities['tool calls']['status'], 'failed')
        self.assertIn('120 total', rendered)
        self.assertIn('Multiple exact Codex log candidates were found', rendered)
        self.assertIn('local attribution is ambiguous', rendered)
        self.assertIn(
            'Provide the exact Codex local log for the requested thread',
            rendered,
        )

    def test_structured_acquisition_drives_fallback_and_recovery_not_warning_text(self):
        snapshot = {
            'events': [
                {
                    '_parsed_timestamp': self.captured_at,
                    'timestamp': '2026-07-21T12:00:00Z',
                    'type': 'event_msg',
                    'payload': {
                        'type': 'token_count',
                        'info': {
                            'total_token_usage': {
                                'input_tokens': 100,
                                'cached_input_tokens': 30,
                                'cache_write_input_tokens': 10,
                                'output_tokens': 20,
                                'reasoning_output_tokens': 5,
                            }
                        },
                    },
                }
            ],
            'warnings': ['Display wording without a status marker.'],
            'acquisition': {
                'outcome': 'failed',
                'causes': [
                    {
                        'kind': 'unreadable',
                        'message': 'Structured local-log acquisition failure.',
                    }
                ],
            },
        }
        usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[],
            codex_snapshot=snapshot,
        )
        activity = self.timing.analyze_codex_tool_activity(
            'session-main', snapshot=snapshot
        )
        tokscale_usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
            codex_snapshot=snapshot,
        )
        report = self.timing.build_diagnostic_report(
            tokscale_usage,
            activity,
            None,
            selected_scope='session',
            codex_acquisition=snapshot['acquisition'],
        )

        self.assertEqual(usage['status'], 'partial')
        self.assertEqual(usage['totals']['total_tokens'], 120)
        self.assertEqual(usage['fallback']['outcome'], 'failed')
        self.assertEqual(
            usage['fallback']['cause'],
            'Structured local-log acquisition failure.',
        )
        self.assertEqual(activity['status'], 'failed')
        self.assertIn(
            'Provide the exact Codex local log for the requested thread',
            report['recovery_prerequisites'][0],
        )

    def test_cursor_missing_session_reports_recoverable_tokscale_prerequisites(self):
        result = self.timing.build_session_usage(
            'cursor',
            'missing-session',
            self.captured_at,
            tokscale_rows=[],
        )

        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['collection']['outcome'], 'succeeded')
        self.assertIn('valid Tokscale login', result['warnings'][0])
        self.assertIn('completed sync', result['warnings'][0])

    def test_supported_clients_are_exact_and_unknown_client_is_observable(self):
        for client in ('codex', 'cursor', 'copilot'):
            self.assertEqual(
                self.timing.detect_current_session(client, 'stable-session'),
                (client, 'stable-session'),
            )

        with self.assertRaisesRegex(
            self.timing.UsageError, "Unsupported client 'claude'"
        ):
            self.timing.detect_current_session('claude', 'stable-session')
        with self.assertRaisesRegex(
            self.timing.UsageError, "Unsupported client 'Codex'"
        ):
            self.timing.detect_current_session('Codex', 'stable-session')

    def test_tokscale_session_aliases_are_client_specific_and_unambiguous(self):
        for client in ('codex', 'cursor', 'copilot'):
            with self.subTest(client=client, match='arbitrary-suffix'):
                self.assertFalse(
                    self.timing.session_id_matches(
                        client, 'other-target', 'target'
                    )
                )
            with self.subTest(client=client, match='exact'):
                self.assertTrue(
                    self.timing.session_id_matches(client, 'target', 'target')
                )
        self.assertTrue(
            self.timing.session_id_matches('codex', 'rollout-target', 'target')
        )
        self.assertFalse(
            self.timing.session_id_matches('cursor', 'rollout-target', 'target')
        )
        self.assertFalse(
            self.timing.session_id_matches('copilot', 'rollout-target', 'target')
        )

        canonical = self.usage_row()
        canonical['sessionId'] = 'rollout-session-main'
        codex_usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[canonical],
        )
        self.assertEqual(codex_usage['status'], 'available')

        exact = self.usage_row()
        alias = dict(exact)
        alias['sessionId'] = 'rollout-session-main'
        ambiguous = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[exact, alias],
            codex_home=self.codex_home,
        )
        self.assertEqual(ambiguous['collection']['outcome'], 'failed')
        self.assertIn('attribution is ambiguous', ambiguous['collection']['cause'])

        cursor_exact = exact | {'client': 'cursor'}
        duplicate = self.timing.build_session_usage(
            'cursor',
            'session-main',
            self.captured_at,
            tokscale_rows=[cursor_exact, dict(cursor_exact)],
        )
        self.assertEqual(duplicate['collection']['outcome'], 'failed')
        self.assertIn('duplicate rows', duplicate['collection']['cause'])

    def test_missing_identity_never_selects_a_newest_local_log(self):
        self.write_token_count('newest-looking-session')

        with mock.patch.dict(self.timing.os.environ, {}, clear=True):
            self.assertEqual(self.timing.detect_current_session(), (None, None))
            with self.assertRaisesRegex(
                self.timing.UsageError,
                'Client and session ID must be provided together',
            ):
                self.timing.detect_current_session('codex', None)

        with mock.patch.dict(
            self.timing.os.environ,
            {'CODEX_THREAD_ID': 'environment-session'},
            clear=True,
        ):
            self.assertEqual(
                self.timing.detect_current_session(),
                ('codex', 'environment-session'),
            )

    def test_tokscale_requires_normalized_grouped_fields(self):
        def runner(command, **kwargs):
            return self.timing.subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps(
                    {
                        'entries': [
                            {
                                'client': 'cursor',
                                'sessionId': 'stable-session',
                            }
                        ]
                    }
                ),
                stderr='',
            )

        with self.assertRaisesRegex(
            self.timing.UsageError, 'incompatible with session diagnostics'
        ):
            self.timing.capture_tokscale_snapshot(
                'cursor', None, None, runner=runner
            )

    def test_tokscale_numeric_normalization_failure_is_structured_failed_evidence(self):
        row = self.usage_row()
        row['client'] = 'cursor'
        row['input'] = True

        self.assert_tokscale_row_failure(
            row,
            'Tokscale field input must be numeric',
            'Tokscale field input must be numeric.',
        )

    def test_tokscale_fractional_integer_fields_are_failed_capabilities(self):
        cases = (
            ('input', 1.5),
            ('performance.totalDurationMs', -0.5),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                row = self.usage_row()
                row['client'] = 'cursor'
                if field == 'input':
                    row['input'] = value
                else:
                    row['performance']['totalDurationMs'] = value

                self.assert_tokscale_row_failure(
                    row,
                    f'Tokscale field {field} must be an integer',
                    f'Tokscale field {field} must be an integer.',
                )

    def test_tokscale_required_numeric_nulls_are_failed_capabilities(self):
        fields = ('input', 'cost', 'performance.totalDurationMs')
        for field in fields:
            with self.subTest(field=field):
                row = self.usage_row()
                row['client'] = 'cursor'
                if field == 'performance.totalDurationMs':
                    row['performance']['totalDurationMs'] = None
                else:
                    row[field] = None

                self.assert_tokscale_row_failure(
                    row,
                    f'Tokscale field {field} must not be null',
                    f'Tokscale field {field} must not be null.',
                )

    def test_tokscale_required_text_fields_are_failed_capabilities(self):
        for field in ('client', 'sessionId', 'model'):
            for value in (None, 7, ''):
                with self.subTest(field=field, value=value):
                    row = self.usage_row()
                    row[field] = value

                    self.assert_tokscale_row_failure(
                        row,
                        f'Tokscale field {field} must be a nonempty string',
                        f'Tokscale field {field} must be a nonempty string.',
                        capture_client='codex',
                    )

    def test_tokscale_provider_remains_optional(self):
        row = self.usage_row()
        row['provider'] = None

        normalized = self.timing.normalize_usage_row(row)

        self.assertEqual(normalized['provider'], '')

    def test_tokscale_session_id_alias_is_selected_and_validated(self):
        valid = self.usage_row()
        valid['sessionId'] = 'rollout-session-main'
        valid['session_id'] = valid.pop('sessionId')
        invalid = dict(valid)
        invalid['session_id'] = None

        self.assertEqual(
            self.timing.normalize_usage_row(valid)['session_id'],
            'rollout-session-main',
        )
        with self.assertRaisesRegex(
            self.timing.UsageError,
            'Tokscale field sessionId must be a nonempty string',
        ):
            self.timing.normalize_usage_row(invalid)

    def test_required_zero_and_optional_codex_token_fields_remain_valid(self):
        row = self.usage_row()
        for field in ('input', 'output', 'reasoning', 'cacheRead', 'cacheWrite'):
            row[field] = 0
        row['messageCount'] = 0
        row['cost'] = 0.0
        row['performance']['totalDurationMs'] = 0.0

        normalized = self.timing.normalize_usage_row(row)
        codex_totals = self.timing._normalize_codex_token_totals(
            {'input_tokens': 0, 'output_tokens': 0}
        )

        self.assertEqual(normalized['cost'], 0.0)
        self.assertEqual(normalized['model_activity_ms'], 0)
        self.assertEqual(codex_totals['total_tokens'], 0)
        self.assertEqual(codex_totals['cache_read'], 0)

    def test_tokscale_integral_float_fields_remain_valid(self):
        row = self.usage_row()
        row['client'] = 'cursor'
        row['input'] = 60.0
        row['performance']['totalDurationMs'] = 2000.0

        def runner(command, **kwargs):
            return self.timing.subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({'entries': [row]}),
                stderr='',
            )

        result = self.timing.capture_tokscale_snapshot(
            'cursor', None, None, runner=runner
        )

        self.assertEqual(result, [row])

    def test_tokscale_rejects_non_finite_cost_as_structured_failed_evidence(self):
        for value in (float('nan'), float('inf'), float('-inf')):
            with self.subTest(value=value):
                row = self.usage_row()
                row['client'] = 'cursor'
                row['cost'] = value

                self.assert_tokscale_row_failure(
                    row,
                    'Tokscale field cost must be finite',
                    'Tokscale field cost must be finite.',
                )

    def test_tokscale_rejects_infinite_integer_fields_as_failed_collection(self):
        cases = (
            ('input', float('inf')),
            ('input', float('-inf')),
            ('performance.totalDurationMs', float('inf')),
            ('performance.totalDurationMs', float('-inf')),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                row = self.usage_row()
                row['client'] = 'cursor'
                if field == 'input':
                    row['input'] = value
                else:
                    row['performance']['totalDurationMs'] = value

                self.assert_tokscale_row_failure(
                    row,
                    f'Tokscale field {field} must be finite',
                    f'Tokscale field {field} must be finite.',
                )

    def test_tokscale_numeric_strings_are_failed_collection_evidence(self):
        cases = (
            ('input', '10'),
            ('cost', '0.25'),
            ('performance.totalDurationMs', '2000'),
        )
        for field, value in cases:
            with self.subTest(field=field):
                row = self.usage_row()
                row['client'] = 'cursor'
                if field == 'performance.totalDurationMs':
                    row['performance']['totalDurationMs'] = value
                else:
                    row[field] = value

                self.assert_tokscale_row_failure(
                    row,
                    f'Tokscale field {field} must be numeric',
                    f'Tokscale field {field} must be numeric.',
                )

    def test_codex_profile_can_make_every_relevant_capability_available(self):
        self.write_turn_tokens()
        session_bounds = self.timing.codex_session_bounds(
            'session-main', self.codex_home
        )
        turn_bounds = self.timing.codex_current_turn_bounds(
            'session-main', self.codex_home
        )
        usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
            codex_home=self.codex_home,
        )
        turn_usage = self.timing.build_codex_turn_usage(
            'session-main', self.captured_at, turn_bounds, self.codex_home
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.analyze_codex_tool_activity(
                'session-main', self.codex_home
            ),
            session_bounds,
            turn_usage=turn_usage,
            turn_activity=self.timing.analyze_codex_tool_activity(
                'session-main',
                self.codex_home,
                turn_bounds[0],
                turn_bounds[1],
            ),
            turn_bounds=turn_bounds,
            selected_scope='both',
        )

        self.assertEqual(report['profile'], 'Codex')
        self.assertEqual(report['session_usage']['models'][0]['model'], 'gpt-test')
        self.assertTrue(
            all(
                capability['status'] == 'available'
                for capability in report['capabilities']
                if capability['relevant']
            )
        )

    def test_cursor_profile_preserves_usage_and_marks_behavior_unavailable(self):
        row = self.usage_row()
        row['client'] = 'cursor'
        usage = self.timing.build_session_usage(
            'cursor',
            'session-main',
            self.captured_at,
            tokscale_rows=[row],
        )
        unavailable = self.timing.unavailable_tool_activity(
            self.timing._profile_behavior_reason('cursor')
        )
        report = self.timing.build_diagnostic_report(
            usage,
            unavailable,
            None,
            selected_scope='both',
        )
        capabilities = {
            capability['name']: capability for capability in report['capabilities']
        }

        self.assertEqual(report['profile'], 'Cursor')
        self.assertEqual(capabilities['session usage']['status'], 'available')
        self.assertEqual(capabilities['model activity']['status'], 'available')
        self.assertEqual(capabilities['current turn']['status'], 'unavailable')
        self.assertEqual(capabilities['tool calls']['status'], 'unavailable')
        self.assertIn(
            'does not claim that the harness can never expose it',
            capabilities['tool calls']['reason'],
        )
        self.assertEqual(report['recovery_prerequisites'], [])

    def test_copilot_profile_reports_successful_usage_without_behavior_parity(self):
        row = self.usage_row()
        row['client'] = 'copilot'
        usage = self.timing.build_session_usage(
            'copilot',
            'session-main',
            self.captured_at,
            tokscale_rows=[row],
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity(
                self.timing._profile_behavior_reason('copilot')
            ),
            None,
            selected_scope='turn',
        )
        capabilities = {
            capability['name']: capability for capability in report['capabilities']
        }

        self.assertEqual(report['profile'], 'GitHub Copilot CLI')
        self.assertEqual(report['session_usage']['tokens']['status'], 'available')
        self.assertTrue(capabilities['current turn']['relevant'])
        self.assertEqual(capabilities['current turn']['status'], 'unavailable')
        self.assertEqual(capabilities['waits']['status'], 'unavailable')
        self.assertEqual(report['recovery_prerequisites'], [])

    def test_copilot_missing_otel_is_unrecoverable_for_completed_session(self):
        usage = self.timing.build_session_usage(
            'copilot',
            'completed-session',
            self.captured_at,
            tokscale_rows=[],
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity(
                self.timing._profile_behavior_reason('copilot')
            ),
            None,
            selected_scope='turn',
        )

        self.assertIn('pre-session OTEL file export', usage['warnings'][0])
        self.assertIn('cannot be recovered', usage['warnings'][0])
        self.assertEqual(usage['collection']['outcome'], 'succeeded')
        self.assertIn(
            'cannot regain missing usage and model-activity telemetry',
            report['recovery_prerequisites'][0],
        )

    def test_tokscale_failure_is_failed_capability_not_healthy_usage(self):
        usage = self.timing.build_session_usage(
            'cursor',
            'stable-session',
            self.captured_at,
            tokscale_rows=[],
            snapshot_error='Tokscale could not run for client cursor.',
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity(
                self.timing._profile_behavior_reason('cursor')
            ),
            None,
            selected_scope='session',
        )
        capabilities = {
            capability['name']: capability for capability in report['capabilities']
        }

        self.assertEqual(capabilities['session usage']['status'], 'failed')
        self.assertEqual(capabilities['model activity']['status'], 'failed')
        self.assertFalse(capabilities['current turn']['relevant'])
        self.assertIn(
            'Resolve the reported Tokscale collection failure',
            report['recovery_prerequisites'][0],
        )
        self.assertEqual(len(report['recovery_prerequisites']), 1)
        self.assertNotIn('login', report['recovery_prerequisites'][0].lower())
        self.assertNotIn('sync', report['recovery_prerequisites'][0].lower())

    def test_copilot_collection_failure_does_not_claim_missing_otel(self):
        usage = self.timing.build_session_usage(
            'copilot',
            'completed-session',
            self.captured_at,
            tokscale_rows=[],
            snapshot_error='Tokscale could not run for client copilot.',
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity(
                self.timing._profile_behavior_reason('copilot')
            ),
            None,
            selected_scope='session',
        )
        recovery = ' '.join(report['recovery_prerequisites']).lower()

        self.assertEqual(usage['collection']['outcome'], 'failed')
        self.assertEqual(len(report['recovery_prerequisites']), 1)
        self.assertIn('tokscale', recovery)
        self.assertNotIn('otel', recovery)
        self.assertNotIn('cannot regain', recovery)

    def test_codex_local_log_read_failure_marks_behavior_capabilities_failed(self):
        self.write_token_count()
        usage = self.timing.build_session_usage(
            'codex',
            'session-main',
            self.captured_at,
            tokscale_rows=[self.usage_row()],
        )
        with mock.patch.object(
            Path,
            'read_text',
            side_effect=OSError('permission denied'),
        ):
            activity = self.timing.analyze_codex_tool_activity(
                'session-main', self.codex_home
            )
        report = self.timing.build_diagnostic_report(
            usage,
            activity,
            None,
            selected_scope='session',
        )
        capabilities = {
            capability['name']: capability for capability in report['capabilities']
        }
        rendered = self.timing.render_diagnostic_markdown(report)

        self.assertEqual(activity['status'], 'failed')
        self.assertEqual(activity['acquisition']['outcome'], 'failed')
        self.assertEqual(
            activity['acquisition']['causes'][0]['kind'], 'unreadable'
        )
        self.assertEqual(capabilities['tool calls']['status'], 'failed')
        self.assertEqual(capabilities['incomplete calls']['status'], 'failed')
        self.assertEqual(
            capabilities['subagent lifecycle and coordination']['status'],
            'failed',
        )
        self.assertEqual(capabilities['waits']['status'], 'failed')
        self.assertIn(
            'Provide the exact Codex local log for the requested thread',
            report['recovery_prerequisites'][0],
        )
        self.assertIn(
            'Tool calls: failed — Codex log could not be read: permission denied',
            rendered,
        )
        self.assertIn(
            'Agent coordination: failed — Codex log could not be read: permission denied',
            rendered,
        )
        self.assertNotIn('- Tool calls: unavailable', rendered)

    def test_main_gates_codex_derivations_by_requested_scope(self):
        self.write_turn_tokens()
        environment = {'CODEX_HOME': str(self.codex_home)}

        with self.subTest(scope='session'):
            with mock.patch.dict(self.timing.os.environ, environment, clear=True), \
                 mock.patch.object(
                     self.timing,
                     'capture_tokscale_snapshot',
                     return_value=[self.usage_row()],
                 ), \
                 mock.patch.object(
                     self.timing,
                     '_codex_current_turn_discovery',
                     wraps=self.timing._codex_current_turn_discovery,
                 ) as turn_discovery, \
                 mock.patch.object(
                     self.timing,
                     '_build_codex_turn_usage_evidence',
                     wraps=self.timing._build_codex_turn_usage_evidence,
                 ) as turn_usage, \
                 mock.patch.object(
                     self.timing,
                     'analyze_codex_tool_activity',
                     wraps=self.timing.analyze_codex_tool_activity,
                 ) as activity, \
                 mock.patch('builtins.print'):
                result = self.timing.main(
                    [
                        'diagnose',
                        '--client',
                        'codex',
                        '--session-id',
                        'session-main',
                        '--scope',
                        'session',
                    ]
                )

            self.assertEqual(result, 0)
            turn_discovery.assert_not_called()
            turn_usage.assert_not_called()
            self.assertEqual(activity.call_count, 1)

        with self.subTest(scope='turn'):
            with mock.patch.dict(self.timing.os.environ, environment, clear=True), \
                 mock.patch.object(
                     self.timing,
                     'capture_tokscale_snapshot',
                     return_value=[self.usage_row()],
                 ), \
                 mock.patch.object(
                     self.timing,
                     'analyze_codex_tool_activity',
                     wraps=self.timing.analyze_codex_tool_activity,
                 ) as activity, \
                 mock.patch('builtins.print'):
                result = self.timing.main(
                    [
                        'diagnose',
                        '--client',
                        'codex',
                        '--session-id',
                        'session-main',
                        '--scope',
                        'turn',
                    ]
                )

            self.assertEqual(result, 0)
            self.assertEqual(activity.call_count, 1)
            self.assertEqual(
                activity.call_args.kwargs['started_at'],
                datetime(2026, 7, 21, 11, tzinfo=timezone.utc),
            )
            self.assertEqual(
                activity.call_args.kwargs['ended_at'],
                datetime(2026, 7, 21, 12, tzinfo=timezone.utc),
            )

    def test_main_reads_one_codex_snapshot_and_propagates_failure(self):
        self.write_token_count()
        environment = {'CODEX_HOME': str(self.codex_home)}
        order = []
        original_timestamp = self.timing._timestamp
        original_load_snapshot = self.timing._load_codex_log_snapshot

        def capture(*args, **kwargs):
            order.append('tokscale')
            return [self.usage_row()]

        def timestamp(now=None):
            if now is None:
                order.append('cutoff')
                return self.captured_at
            return original_timestamp(now)

        def load_snapshot(*args, **kwargs):
            order.append('codex-log')
            return original_load_snapshot(*args, **kwargs)

        with mock.patch.dict(self.timing.os.environ, environment, clear=True), \
             mock.patch.object(
                 self.timing,
                 '_timestamp',
                 side_effect=timestamp,
             ), \
             mock.patch.object(
                 self.timing,
                 '_load_codex_log_snapshot',
                 side_effect=load_snapshot,
             ) as load_snapshot, \
             mock.patch.object(
                 self.timing,
                 'capture_tokscale_snapshot',
                 side_effect=capture,
             ), \
             mock.patch.object(
                 Path,
                 'read_text',
                 side_effect=OSError('permission denied'),
             ) as read_text, \
             mock.patch('builtins.print') as output:
            result = self.timing.main(
                [
                    'diagnose',
                    '--client',
                    'codex',
                    '--session-id',
                    'session-main',
                    '--scope',
                    'both',
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(order[:3], ['tokscale', 'codex-log', 'cutoff'])
        self.assertTrue(
            load_snapshot.call_args.kwargs['capture_cutoff_after_read']
        )
        self.assertEqual(read_text.call_count, 1)
        rendered = output.call_args.args[0]
        self.assertIn('- current turn: failed (relevant)', rendered)
        self.assertIn('- tool calls: failed (relevant)', rendered)
        self.assertIn(
            'Tool calls: failed — Codex log could not be read: permission denied',
            rendered,
        )
        self.assertIn(
            'Provide the exact Codex local log for the requested thread',
            rendered,
        )
        self.assertNotIn('- Tool calls: unavailable', rendered)

    def test_markdown_rendering_contains_untrusted_values_on_one_safe_line(self):
        session_id = 'private-session\n#### Forged Heading'
        row = self.usage_row()
        row.update(
            {
                'client': 'cursor',
                'sessionId': session_id,
                'provider': 'openai*[x]\n# provider heading',
                'model': 'gpt-test\n#### Overall Conclusion\n- No abnormality observed',
            }
        )
        usage = self.timing.build_session_usage(
            'cursor',
            session_id,
            self.captured_at,
            tokscale_rows=[row],
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity(
                'Unavailable detail\n#### Forged Failure\n- Inconclusive'
            ),
            None,
            selected_scope='session',
        )

        rendered = self.timing.render_diagnostic_markdown(report)

        self.assertEqual(self.timing._markdown_text('ordinary text'), 'ordinary text')
        self.assertEqual(rendered.count('\n#### Overall Conclusion'), 1)
        self.assertNotIn('\n#### Forged Heading', rendered)
        self.assertNotIn('\n#### Forged Failure', rendered)
        self.assertNotIn('\n- No abnormality observed', rendered)
        self.assertNotIn('\n- Inconclusive', rendered)
        self.assertIn(r'openai\*\[x\]', rendered)
        self.assertIn(r'\#\#\#\# Forged Heading', rendered)

    def test_rendered_report_separates_facts_from_agent_judgment_and_content(self):
        row = self.usage_row()
        row['client'] = 'cursor'
        row['sessionId'] = 'private-session-id'
        usage = self.timing.build_session_usage(
            'cursor',
            'private-session-id',
            self.captured_at,
            tokscale_rows=[row],
        )
        report = self.timing.build_diagnostic_report(
            usage,
            self.timing.unavailable_tool_activity(
                self.timing._profile_behavior_reason('cursor')
            ),
            None,
            selected_scope='both',
        )
        rendered = self.timing.render_diagnostic_markdown(report)

        self.assertIn('#### Identity and Scope', rendered)
        self.assertIn(
            '- Snapshot cutoff (UTC): 2026-07-21T12:00:00.000000+00:00',
            rendered,
        )
        self.assertIn('#### Capability Coverage', rendered)
        self.assertIn('#### Session Usage and API-Equivalent Cost', rendered)
        self.assertIn('#### Overall Conclusion', rendered)
        self.assertIn('wrapper does not infer task health', rendered)
        self.assertNotIn('Abnormal evidence observed', rendered)
        self.assertNotIn('No abnormality observed', rendered)
        self.assertNotIn('Inconclusive', rendered)
        self.assertNotIn('prompt', json.dumps(report).lower())
        self.assertNotIn('response', json.dumps(report).lower())
        self.assertNotIn('tool inputs', rendered.lower())
        self.assertIn('Session usage coverage does not establish behavior health', rendered)


if __name__ == '__main__':
    unittest.main()
