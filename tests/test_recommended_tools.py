"""Contracts for recommended-tool policies and non-mutating Hooks."""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = (
    REPO_ROOT / 'runtime' / 'recommended-tools'
    / 'check_recommended_tools.py'
)
MAINTAINER_PATH = (
    REPO_ROOT / 'runtime' / 'recommended-tools'
    / 'maintain_recommended_tools.py'
)
POLICY_ROOT = REPO_ROOT / 'policies' / 'recommended-tools'
RECOMMENDED_TOOL_POLICIES = POLICY_ROOT


def load_checker():
    spec = importlib.util.spec_from_file_location('task8_check_recommended_tools', CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load checker: {CHECKER_PATH}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_recommended_tool_checker_module():
    return load_checker()


def load_maintainer():
    spec = importlib.util.spec_from_file_location('task8_maintain_recommended_tools', MAINTAINER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load maintainer: {MAINTAINER_PATH}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RecommendedToolPolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()

    def test_plugin_policies_are_centralized_and_codex_checks_only_effective_multi_agent(self):
        expected = {
            'codex': {'codex', 'codegraph', 'tokscale'},
            'cursor': {'cursor-agent', 'codegraph', 'tokscale'},
            'copilot': {'copilot', 'codegraph', 'tokscale'},
        }
        for harness, tool_ids in expected.items():
            with self.subTest(harness=harness):
                policy = json.loads((POLICY_ROOT / f'{harness}.json').read_text(encoding='utf-8'))
                self.assertEqual(policy['harness'], harness)
                self.assertEqual({tool['id'] for tool in policy['tools']}, tool_ids)
                self.assertNotIn('hooks', json.dumps(policy).lower())
                self.assertEqual(
                    [item['id'] for item in policy.get('required_values', [])],
                    ['multi_agent'] if harness == 'codex' else [],
                )
                self.assertEqual(
                    [item['id'] for item in policy.get('config_requirements', [])],
                    ['parallel_agent_capacity'] if harness == 'codex' else [],
                )
                self.assertEqual(
                    [item['id'] for item in policy.get('manual_session_actions', [])],
                    ['fleet_mode'] if harness == 'copilot' else [],
                )

    def test_default_policy_path_resolves_plugin_root_policy(self):
        self.assertEqual(
            self.checker.default_policy_path('codex'),
            POLICY_ROOT / 'codex.json',
        )

    def test_codex_readiness_hook_timeout_remains_thirty_seconds(self):
        manifest = json.loads(
            (REPO_ROOT / 'hooks' / 'codex.json').read_text(encoding='utf-8')
        )
        readiness_hook = manifest['hooks']['SessionStart'][0]['hooks'][0]

        self.assertEqual(readiness_hook['timeout'], 30)

    def test_hook_mode_does_not_call_maintenance_runner(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            policy = Path(temp_dir) / 'codex.json'
            policy.write_text('{"harness": "codex", "tools": []}\n', encoding='utf-8')
            maintenance_runner = mock.Mock(side_effect=AssertionError('Hooks must not mutate tools'))
            with mock.patch.object(self.checker, 'check_policy', return_value=[]):
                with mock.patch.object(self.checker.subprocess, 'run', maintenance_runner):
                    result = self.checker.run_hook(
                        'codex', policy, policy.parent / 'cache', datetime(2026, 8, 4), force=True,
                    )
            self.assertTrue(result.ran)
            maintenance_runner.assert_not_called()


class RecommendedToolCheckerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_recommended_tool_checker_module()

    def test_version_comparison_is_strict_and_suffix_tolerant(self):
        cases = (
            ('0.144.4', '0.144.0', True),
            ('0.144.0', '0.144.0', False),
            ('0.143.99', '0.144.0', False),
            ('2026.01.28-fd13201', '2026.01.27', True),
            ('1.0.59+build.7', '1.0.58', True),
            ('6.0.0-rc.1', '6.0.0', False),
        )
        for installed, target, expected in cases:
            with self.subTest(installed=installed, target=target):
                self.assertIs(
                    self.checker.is_strictly_greater(installed, target),
                    expected,
                )
        with self.assertRaises(ValueError):
            self.checker.parse_version('unknown')

    def test_harness_policies_keep_all_thresholds_out_of_python(self):
        policies = RECOMMENDED_TOOL_POLICIES
        expected = {
            'codex': {
                'codex': '0.144.0',
                'codegraph': '1.4.1',
                'tokscale': '4.6.1',
            },
            'cursor': {
                'cursor-agent': '2026.01.27',
                'codegraph': '1.4.1',
                'tokscale': '4.6.1',
            },
            'copilot': {
                'copilot': '1.0.58',
                'codegraph': '1.4.1',
                'tokscale': '4.6.1',
            },
        }
        for harness, targets in expected.items():
            policy = json.loads((policies / f'{harness}.json').read_text(encoding='utf-8'))
            self.assertEqual(policy['harness'], harness)
            self.assertEqual(
                {tool['id']: tool['target_version'] for tool in policy['tools']},
                targets,
            )
        codex_policy = json.loads((policies / 'codex.json').read_text(encoding='utf-8'))
        self.assertEqual(
            [requirement['id'] for requirement in codex_policy['required_values']],
            ['multi_agent'],
        )
        self.assertEqual(codex_policy['required_values'][0]['expected'], 'true')
        requirement = codex_policy['config_requirements'][0]
        self.assertEqual(requirement['minimum_total_threads'], 6)
        self.assertEqual(requirement['primary_threads'], 1)
        self.assertEqual(
            requirement['maintenance']['write_key_path'],
            'agents.max_concurrent_threads_per_session',
        )
        self.assertEqual(requirement['maintenance']['write_value'], 5)
        self.assertEqual(
            codex_policy['required_values'][0]['maintenance'],
            {
                'kind': 'config-write',
                'write_key_path': 'features.multi_agent',
                'write_value': True,
            },
        )

    def test_cursor_version_gate_owns_default_subagent_availability(self):
        policy = json.loads(
            (POLICY_ROOT / 'cursor.json').read_text(encoding='utf-8')
        )
        cursor = next(tool for tool in policy['tools'] if tool['id'] == 'cursor-agent')

        self.assertIn('default parallel subagent support', cursor['install'])
        self.assertIn('default parallel subagent capability', cursor['upgrade'])
        self.assertNotIn('config_requirements', policy)

    def test_copilot_fleet_support_produces_an_approved_manual_session_action(self):
        checker = self.checker
        policy = json.loads(
            (POLICY_ROOT / 'copilot.json').read_text(encoding='utf-8')
        )
        policy['tools'] = []

        with mock.patch.object(checker, 'run_detector', return_value='/fleet'):
            findings = checker.check_policy(policy)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, 'manual-session-action')
        self.assertEqual(findings[0].target_id, 'fleet_mode')
        self.assertEqual(findings[0].action, 'configure')
        self.assertIn('parallel subagents', findings[0].message)

    def test_policy_guidance_describes_actions_without_exposing_commands(self):
        forbidden = (
            'npm install',
            'codex plugin add',
            'copilot plugin install',
            'copilot plugin update',
            'copilot update',
            'agent update',
            'codegraph upgrade',
        )
        for policy_path in sorted(POLICY_ROOT.glob('*.json')):
            policy = json.loads(policy_path.read_text(encoding='utf-8'))
            for tool in policy['tools']:
                guidance = f'{tool["install"]}\n{tool["upgrade"]}'.lower()
                for command in forbidden:
                    with self.subTest(
                        harness=policy['harness'],
                        tool=tool['id'],
                        command=command,
                    ):
                        self.assertNotIn(command, guidance)

    def test_command_manifest_and_json_item_detectors_are_data_driven(self):
        checker = self.checker
        command_detector = {
            'kind': 'command-regex',
            'command': ['example', '--version'],
            'pattern': r'version ([0-9.]+)',
        }
        process = mock.Mock()
        process.stdout = io.BytesIO(b'example version 2.4.1\n')
        process.wait.return_value = 0
        with mock.patch.object(checker.subprocess, 'Popen', return_value=process) as popen:
            self.assertEqual(checker.run_detector(command_detector), '2.4.1')
        popen.assert_called_once()
        process.wait.assert_called_once_with(timeout=5)
        self.assertIs(popen.call_args.kwargs['stderr'], checker.subprocess.STDOUT)

        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / 'plugin.json'
            manifest.write_text('{"metadata": {"version": "6.1.1"}}\n', encoding='utf-8')
            detector = {
                'kind': 'json-manifest-glob',
                'glob': str(manifest),
                'json_path': 'metadata.version',
            }
            self.assertEqual(checker.run_detector(detector), '6.1.1')

        installed_plugins = {
            'installed': [
                {
                    'pluginId': 'superpowers@openai-curated',
                    'version': '6.2.0',
                    'installed': True,
                }
            ]
        }
        json_process = mock.Mock()
        json_process.stdout = io.BytesIO(
            b'WARNING: unable to create PATH aliases\n'
            + json.dumps(installed_plugins).encode('utf-8')
        )
        json_process.wait.return_value = 0
        detector = {
            'kind': 'json-command-item',
            'command': ['codex', 'plugin', 'list', '--json'],
            'items_path': 'installed',
            'match_path': 'pluginId',
            'match_value': 'superpowers@openai-curated',
            'value_path': 'version',
        }
        with mock.patch.object(checker.subprocess, 'Popen', return_value=json_process):
            self.assertEqual(checker.run_detector(detector), '6.2.0')

        installed_plugins['installed'][0]['pluginId'] = 'github@openai-curated'
        missing_process = mock.Mock()
        missing_process.stdout = io.BytesIO(json.dumps(installed_plugins).encode('utf-8'))
        missing_process.wait.return_value = 0
        with mock.patch.object(checker.subprocess, 'Popen', return_value=missing_process):
            self.assertIsNone(checker.run_detector(detector))

    def test_json_item_detector_uses_manifest_version_for_opaque_marketplace_revision(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / 'plugin.json'
            manifest.write_text('{"version":"6.2.0"}\n', encoding='utf-8')
            installed_plugins = {
                'installed': [{
                    'pluginId': 'superpowers@openai-curated',
                    'version': 'bd2122cb',
                    'installed': True,
                    'enabled': True,
                }]
            }
            process = mock.Mock()
            process.stdout = io.BytesIO(json.dumps(installed_plugins).encode('utf-8'))
            process.wait.return_value = 0
            detector = {
                'kind': 'json-command-item',
                'command': ['codex', 'plugin', 'list', '--json'],
                'items_path': 'installed',
                'match_path': 'pluginId',
                'match_value': 'superpowers@openai-curated',
                'value_path': 'version',
                'fallback_manifest_glob': str(manifest),
                'fallback_manifest_json_path': 'version',
            }

            with mock.patch.object(checker.subprocess, 'Popen', return_value=process):
                self.assertEqual(checker.run_detector(detector), '6.2.0')

    def test_command_detector_resolves_path_entry_before_python_subprocess(self):
        checker = self.checker
        process = mock.Mock()
        process.stdout = io.BytesIO(b'example version 2.4.1\n')
        process.wait.return_value = 0
        resolved = 'C:/npm/example.cmd'

        with mock.patch.object(shutil, 'which', return_value=resolved) as which:
            with mock.patch.object(checker.subprocess, 'Popen', return_value=process) as popen:
                self.assertEqual(
                    checker._run_command(['example', '--version'], 5),
                    'example version 2.4.1\n',
                )

        which.assert_called_once_with('example')
        self.assertEqual(popen.call_args.args[0], [resolved, '--version'])

    def test_policy_findings_distinguish_missing_equal_and_unreadable(self):
        policy = {
            'harness': 'test',
            'tools': [
                {
                    'id': 'missing',
                    'name': 'Missing Tool',
                    'target_version': '1.0.0',
                    'comparison': '>',
                    'detectors': [{'kind': 'command-regex', 'command': ['missing']}],
                    'install': 'install missing',
                    'upgrade': 'upgrade missing',
                },
                {
                    'id': 'equal',
                    'name': 'Equal Tool',
                    'target_version': '2.0.0',
                    'comparison': '>',
                    'detectors': [{'kind': 'fixed', 'value': '2.0.0'}],
                    'install': 'install equal',
                    'upgrade': 'upgrade equal',
                },
                {
                    'id': 'bad',
                    'name': 'Bad Tool',
                    'target_version': '3.0.0',
                    'comparison': '>',
                    'detectors': [{'kind': 'fixed', 'value': 'unknown'}],
                    'install': 'install bad',
                    'upgrade': 'upgrade bad',
                },
            ],
        }

        findings = self.checker.check_policy(policy)

        self.assertEqual(
            [finding.code for finding in findings],
            ['tool-missing', 'version-not-greater', 'version-unreadable'],
        )
        self.assertEqual(
            [(finding.code, finding.tool, finding.guidance) for finding in findings],
            [
                ('tool-missing', 'Missing Tool', 'install missing'),
                ('version-not-greater', 'Equal Tool', 'upgrade equal'),
                ('version-unreadable', 'Bad Tool', 'upgrade bad'),
            ],
        )

    def test_policy_checks_required_effective_values(self):
        checker = self.checker
        base_requirement = {
            'id': 'multi_agent',
            'name': 'Codex multi-agent',
            'expected': 'true',
            'guidance': 'Enable multi-agent and start a new session.',
        }

        matching = checker.check_policy(
            {
                'harness': 'codex',
                'tools': [],
                'required_values': [
                    {
                        **base_requirement,
                        'detectors': [{'kind': 'fixed', 'value': 'true'}],
                    }
                ],
            }
        )
        mismatching = checker.check_policy(
            {
                'harness': 'codex',
                'tools': [],
                'required_values': [
                    {
                        **base_requirement,
                        'detectors': [{'kind': 'fixed', 'value': 'false'}],
                    }
                ],
            }
        )

        self.assertEqual(matching, [])
        self.assertEqual(len(mismatching), 1)
        self.assertEqual(mismatching[0].code, 'required-value-mismatch')
        self.assertEqual(
            mismatching[0].message,
            'is false; it must be true for this project',
        )

    def test_config_requirement_prompts_for_low_or_unset_total_capacity(self):
        checker = self.checker
        policy = json.loads(
            (POLICY_ROOT / 'codex.json').read_text(encoding='utf-8')
        )
        cases = (
            {'agents': {'max_concurrent_threads_per_session': 3}},
            {'agents': {'max_threads': 4}},
            {'agents': None},
        )
        for initial_config in cases:
            with self.subTest(initial_config=initial_config):
                calls = []

                def rpc(method, params):
                    calls.append((method, params))
                    return {'config': initial_config}

                findings = checker.check_config_requirements(
                    policy,
                    Path('/project'),
                    rpc=rpc,
                )

                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].code, 'required-value-mismatch')
                self.assertEqual(findings[0].target_id, 'parallel_agent_capacity')
                self.assertEqual(findings[0].action, 'configure')
                self.assertIn('at least 6 concurrent agents', findings[0].message)
                self.assertEqual(
                    [method for method, _params in calls],
                    ['config/read'],
                )

    def test_config_requirement_preserves_sufficient_capacity(self):
        checker = self.checker
        policy = json.loads(
            (POLICY_ROOT / 'codex.json').read_text(encoding='utf-8')
        )
        calls = []

        def rpc(method, params):
            calls.append((method, params))
            return {
                'config': {
                    'agents': {'max_concurrent_threads_per_session': 5}
                }
            }

        findings = checker.check_config_requirements(
            policy,
            Path('/project'),
            rpc=rpc,
        )

        self.assertEqual(findings, [])
        self.assertEqual([method for method, _params in calls], ['config/read'])

    def test_config_requirement_is_checked_when_multi_agent_is_unavailable(self):
        checker = self.checker
        policy = json.loads(
            (POLICY_ROOT / 'codex.json').read_text(encoding='utf-8')
        )
        rpc = mock.Mock(return_value={
            'config': {'agents': {'max_concurrent_threads_per_session': 3}},
        })
        findings = checker.check_config_requirements(
            policy,
            Path('/project'),
            rpc=rpc,
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].target_id, 'parallel_agent_capacity')
        rpc.assert_called_once()

    def test_config_requirement_reports_nonblocking_failure(self):
        checker = self.checker
        policy = json.loads(
            (POLICY_ROOT / 'codex.json').read_text(encoding='utf-8')
        )

        findings = checker.check_config_requirements(
            policy,
            Path('/project'),
            rpc=mock.Mock(side_effect=checker.DetectorError('private detail')),
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, 'detector-error')
        self.assertNotIn('private detail', checker.render_findings(findings))

    def test_codex_config_rpc_client_initializes_and_reuses_one_process(self):
        checker = self.checker
        process = mock.Mock()
        process.stdin = io.BytesIO()
        process.stdout = io.BytesIO(
            b'{"id":0,"result":{"userAgent":"codex"}}\n'
            b'{"method":"remoteControl/status/changed","params":{}}\n'
            b'{"id":1,"result":{"config":{"agents":null}}}\n'
            b'{"id":2,"result":{}}\n'
        )
        process.wait.return_value = 0

        with mock.patch.object(shutil, 'which', return_value='/bin/codex'), \
                mock.patch.object(
                    checker.subprocess, 'Popen', return_value=process
                ) as popen:
            with checker._CodexConfigRpcClient(Path('/project')) as client:
                read = client.request('config/read', {'includeLayers': False})
                written = client.request(
                    'config/value/write',
                    {
                        'keyPath': 'agents.max_concurrent_threads_per_session',
                        'value': 5,
                        'mergeStrategy': 'upsert',
                    },
                )

        self.assertEqual(read, {'config': {'agents': None}})
        self.assertEqual(written, {})
        popen.assert_called_once()
        self.assertEqual(popen.call_args.args[0], ['/bin/codex', 'app-server'])

    def test_detector_timeout_is_retryable_and_equal_differs_from_lower(self):
        checker = self.checker
        tool = {
            'id': 'example',
            'name': 'Example Tool',
            'target_version': '2.0.0',
            'comparison': '>',
            'detectors': [{'kind': 'command-regex', 'command': ['example']}],
            'install': 'install it',
            'upgrade': 'upgrade it',
        }
        timed_out_process = mock.Mock()
        timed_out_process.stdout = io.BytesIO(b'')
        timed_out_process.wait.side_effect = (
            checker.subprocess.TimeoutExpired(['example'], 5),
            1,
        )
        with mock.patch.object(
            checker.subprocess,
            'Popen',
            return_value=timed_out_process,
        ):
            timeout = checker.check_policy({'harness': 'test', 'tools': [tool]})
        equal = checker.check_policy(
            {
                'harness': 'test',
                'tools': [{**tool, 'detectors': [{'kind': 'fixed', 'value': '2.0.0'}]}],
            }
        )
        lower = checker.check_policy(
            {
                'harness': 'test',
                'tools': [{**tool, 'detectors': [{'kind': 'fixed', 'value': '1.9.9'}]}],
            }
        )

        self.assertEqual(timeout[0].code, 'detector-error')
        self.assertEqual(equal[0].code, 'version-not-greater')
        self.assertEqual(lower[0].code, 'version-not-greater')

    def test_command_detector_terminates_when_output_exceeds_limit(self):
        checker = self.checker
        process = mock.Mock()
        process.stdout = io.BytesIO(b'x' * (checker._MAX_COMMAND_OUTPUT + 1))
        process.wait.return_value = 0
        with mock.patch.object(checker.subprocess, 'Popen', return_value=process):
            with self.assertRaises(checker.DetectorError):
                checker.run_detector(
                    {
                        'kind': 'command-regex',
                        'command': ['example', '--version'],
                    }
                )

        process.kill.assert_called()

    def test_daily_state_is_independent_per_project_and_harness(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cache = root / 'cache'
            first_project = root / 'first-project'
            second_project = root / 'second-project'
            first_project.mkdir()
            second_project.mkdir()
            (first_project / '.git').mkdir()
            (second_project / '.git').mkdir()
            codex_policy = first_project / 'codex.json'
            other_codex_policy = second_project / 'codex.json'
            cursor_policy = first_project / 'cursor.json'
            codex_policy.write_text('{"harness":"codex","tools":[]}\n', encoding='utf-8')
            other_codex_policy.write_text(
                '{"harness":"codex","tools":[]}\n', encoding='utf-8'
            )
            cursor_policy.write_text('{"harness":"cursor","tools":[]}\n', encoding='utf-8')
            calls = []

            def evaluator(policy):
                calls.append(policy['harness'])
                return []

            today = datetime(2026, 7, 21, 9, tzinfo=timezone.utc)
            first = checker.run_hook(
                'codex', codex_policy, cache, today,
                project_root=first_project, evaluator=evaluator,
            )
            second = checker.run_hook(
                'codex', codex_policy, cache, today,
                project_root=first_project, evaluator=evaluator,
            )
            other_project = checker.run_hook(
                'codex', other_codex_policy, cache, today,
                project_root=second_project, evaluator=evaluator,
            )
            cursor = checker.run_hook(
                'cursor', cursor_policy, cache, today,
                project_root=first_project, evaluator=evaluator,
            )

            self.assertTrue(first.ran)
            self.assertFalse(second.ran)
            self.assertTrue(other_project.ran)
            self.assertTrue(cursor.ran)
            self.assertEqual(calls, ['codex', 'codex', 'cursor'])

    def test_project_root_prefers_agent_config_then_git_then_current_directory(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repository = root / 'repository'
            nested_project = repository / 'packages' / 'app'
            working_directory = nested_project / 'lib'
            working_directory.mkdir(parents=True)
            (repository / '.git').mkdir()
            (nested_project / '.agents').mkdir()
            (nested_project / '.agents' / 'config.json').write_text(
                '{}\n', encoding='utf-8'
            )

            self.assertEqual(
                checker.resolve_project_root(working_directory),
                nested_project.resolve(),
            )
            (nested_project / '.agents' / 'config.json').unlink()
            self.assertEqual(
                checker.resolve_project_root(working_directory),
                repository.resolve(),
            )

        with mock.patch.object(Path, 'exists', return_value=False), mock.patch.object(
            Path, 'is_file', return_value=False
        ):
            current = Path('/synthetic/project/subdirectory')
            self.assertEqual(checker.resolve_project_root(current), current.resolve())

    def test_mcp_readiness_aggregates_typed_plugin_and_project_checks(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry = root / 'registry.json'
            registry.write_text(json.dumps({
                'servers': [{
                    'id': 'playwright', 'harnesses': ['codex'],
                    'readiness': {'checks': [
                        {'kind': 'runtime-version', 'runtime': 'node', 'minimum': '18.0.0'},
                        {'kind': 'command-exists', 'command': 'npx'},
                    ]},
                }],
            }), encoding='utf-8')
            config = root / '.agents/config.json'
            config.parent.mkdir()
            config.write_text(json.dumps({
                'mcp': [
                    {
                        'id': 'inspector', 'harnesses': ['codex'],
                        'command': 'cache/inspector.exe',
                    },
                    {
                        'id': 'private', 'harnesses': ['codex'],
                        'command': 'private-mcp', 'env': ['MCP_TOKEN'],
                    },
                    {
                        'id': 'sentry', 'harnesses': ['codex'],
                        'url': 'https://mcp.sentry.dev/mcp',
                    },
                ],
            }), encoding='utf-8')

            with mock.patch.object(checker, 'run_detector', return_value='17.9.0'), \
                    mock.patch.object(checker.shutil, 'which', return_value=None), \
                    mock.patch.dict(checker.os.environ, {}, clear=True):
                findings = checker.check_mcp_readiness('codex', root, registry)

            self.assertEqual(
                [finding.code for finding in findings],
                [
                    'mcp-version-too-old',
                    'mcp-prerequisite-missing',
                    'mcp-prerequisite-missing',
                    'mcp-prerequisite-missing',
                    'mcp-prerequisite-missing',
                ],
            )
            self.assertNotIn('sentry MCP', [finding.tool for finding in findings])

    def test_mcp_readiness_filters_harnesses_and_rejects_unsafe_profiles(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry = root / 'registry.json'
            registry.write_text(json.dumps({
                'servers': [{
                    'id': 'playwright', 'harnesses': ['codex', 'cursor'],
                    'readiness': {'checks': []},
                }],
            }), encoding='utf-8')
            config = root / '.agents/config.json'
            config.parent.mkdir()
            config.write_text(json.dumps({
                'mcp': [{
                    'id': 'inspector', 'harnesses': ['cursor'],
                    'command': 'cache/inspector.exe',
                }, {
                    'id': 'unsafe', 'harnesses': ['codex'],
                    'readiness': {'checks': [
                        {'kind': 'shell', 'command': 'echo unsafe'},
                        {'kind': 'environment-variable', 'name': 'MISSING_TOKEN'},
                    ]},
                }],
            }), encoding='utf-8')

            with mock.patch.dict(checker.os.environ, {}, clear=True):
                codex = checker.check_mcp_readiness('codex', root, registry)
                cursor = checker.check_mcp_readiness('cursor', root, registry)

            self.assertEqual(
                [finding.code for finding in codex],
                ['detector-error'],
            )
            self.assertEqual(
                [(finding.tool, finding.code) for finding in cursor],
                [('inspector MCP', 'mcp-prerequisite-missing')],
            )

    def test_project_mcp_readiness_uses_effective_host_and_os_overrides(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry = root / 'registry.json'
            registry.write_text(json.dumps({'servers': []}), encoding='utf-8')
            config = root / '.agents/config.json'
            config.parent.mkdir()
            config.write_text(json.dumps({
                'mcp': [{
                    'id': 'inspector',
                    'command': 'python3',
                    'overrides': [{
                        'when': {
                            'harnesses': ['cursor'],
                            'operatingSystems': ['windows'],
                        },
                        'set': {
                            'command': '${workspaceFolder}/cache/inspector.exe',
                            'env': ['INSPECTOR_TOKEN'],
                        },
                    }],
                }],
            }), encoding='utf-8')

            with mock.patch.object(checker.shutil, 'which', return_value='/usr/bin/python3'), \
                    mock.patch.object(checker, '_current_operating_system', return_value='windows'), \
                    mock.patch.dict(checker.os.environ, {}, clear=True):
                codex = checker.check_mcp_readiness('codex', root, registry)
                cursor = checker.check_mcp_readiness('cursor', root, registry)

            self.assertEqual(codex, [])
            self.assertEqual(
                [finding.code for finding in cursor],
                ['mcp-prerequisite-missing', 'mcp-prerequisite-missing'],
            )
            with mock.patch.object(checker.shutil, 'which', return_value='/usr/bin/python3'), \
                    mock.patch.object(checker, '_current_operating_system', return_value='linux'):
                self.assertEqual(checker.check_mcp_readiness('cursor', root, registry), [])

    def test_plugin_and_project_mcp_share_readiness_selection_and_inference(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry = root / 'registry.json'
            registry.write_text(json.dumps({
                'servers': [{
                    'id': 'plugin-auto',
                    'harnesses': ['codex', 'cursor'],
                    'command': 'plugin-mcp',
                }, {
                    'id': 'plugin-custom',
                    'harnesses': ['codex'],
                    'command': 'ignored-plugin-command',
                    'readiness': {
                        'harnesses': ['codex'],
                        'operatingSystems': ['windows'],
                        'checks': [
                            {'kind': 'environment-variable', 'name': 'PLUGIN_TOKEN'},
                        ],
                    },
                }],
            }), encoding='utf-8')
            config = root / '.agents/config.json'
            config.parent.mkdir()
            config.write_text(json.dumps({
                'mcp': [{
                    'id': 'project-auto',
                    'harnesses': ['codex', 'cursor'],
                    'command': 'project-mcp',
                    'env': ['PROJECT_TOKEN'],
                }, {
                    'id': 'project-custom',
                    'harnesses': ['codex'],
                    'command': 'ignored-project-command',
                    'readiness': {
                        'harnesses': ['codex'],
                        'operatingSystems': ['windows'],
                        'checks': [
                            {'kind': 'command-exists', 'command': 'custom-check'},
                        ],
                    },
                }],
            }), encoding='utf-8')

            with mock.patch.object(
                checker, '_current_operating_system', return_value='windows'
            ):
                plugin = checker._mcp_servers_from_registry(registry, 'codex')
                project = checker._mcp_servers_from_project(root, 'codex')

            self.assertEqual(plugin, [{
                'id': 'plugin-auto',
                'readiness': {
                    'checks': [{'kind': 'command-exists', 'command': 'plugin-mcp'}]
                },
            }, {
                'id': 'plugin-custom',
                'readiness': {
                    'checks': [
                        {'kind': 'environment-variable', 'name': 'PLUGIN_TOKEN'}
                    ]
                },
            }])
            self.assertEqual(project, [{
                'id': 'project-auto',
                'readiness': {'checks': [
                    {'kind': 'command-exists', 'command': 'project-mcp'},
                    {'kind': 'environment-variable', 'name': 'PROJECT_TOKEN'},
                ]},
            }, {
                'id': 'project-custom',
                'readiness': {
                    'checks': [{'kind': 'command-exists', 'command': 'custom-check'}]
                },
            }])

            with mock.patch.object(
                checker, '_current_operating_system', return_value='linux'
            ):
                self.assertEqual(
                    [server['id'] for server in checker._mcp_servers_from_registry(
                        registry, 'codex'
                    )],
                    ['plugin-auto'],
                )
                self.assertEqual(
                    [server['id'] for server in checker._mcp_servers_from_project(
                        root, 'codex'
                    )],
                    ['project-auto'],
                )

    def test_default_daily_runner_combines_tool_and_mcp_findings_once(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = root / 'project'
            project.mkdir()
            (project / '.git').mkdir()
            policy = root / 'codex.json'
            policy.write_text('{"harness":"codex","tools":[]}\n', encoding='utf-8')
            tool_finding = checker.Finding('tool-missing', 'tool', 'missing', 'install')
            mcp_finding = checker.Finding(
                'mcp-prerequisite-missing', 'MCP', 'missing', 'install'
            )

            with mock.patch.object(checker, 'check_policy', return_value=[tool_finding]) \
                    as tool_check, mock.patch.object(
                        checker, 'check_mcp_readiness', return_value=[mcp_finding]
                    ) as mcp_check:
                first = checker.run_hook(
                    'codex', policy, root / 'cache',
                    datetime(2026, 8, 10, 10), project_root=project,
                )
                second = checker.run_hook(
                    'codex', policy, root / 'cache',
                    datetime(2026, 8, 10, 11), project_root=project,
                )

            self.assertEqual(first.findings, (tool_finding, mcp_finding))
            self.assertFalse(second.ran)
            tool_check.assert_called_once()
            mcp_check.assert_called_once()

    def test_daily_state_ignores_policy_change_but_allows_force_and_next_day(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            policy_path = root / 'codex.json'
            cache = root / 'cache'
            policy_path.write_text('{"harness":"codex","tools":[]}\n', encoding='utf-8')
            calls = []

            def evaluator(policy):
                calls.append(policy)
                return []

            day = datetime(2026, 7, 21, 9)
            checker.run_hook('codex', policy_path, cache, day, evaluator=evaluator)
            policy_path.write_text('{"harness":"codex","tools":[],"revision":2}\n', encoding='utf-8')
            changed = checker.run_hook('codex', policy_path, cache, day, evaluator=evaluator)
            forced = checker.run_hook(
                'codex', policy_path, cache, day, force=True, evaluator=evaluator
            )
            next_day = checker.run_hook(
                'codex', policy_path, cache, day + timedelta(days=1), evaluator=evaluator
            )

            self.assertFalse(changed.ran)
            self.assertTrue(forced.ran)
            self.assertTrue(next_day.ran)
            self.assertEqual(len(calls), 3)

    def test_findings_prompt_the_user_only_once_per_day(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            policy_path = root / 'codex.json'
            cache = root / 'cache'
            policy_path.write_text('{"harness":"codex","tools":[]}\n', encoding='utf-8')
            calls = []
            finding = checker.Finding(
                'tool-missing',
                'Example Tool',
                'is missing',
                'Install it.',
            )

            def missing(_policy):
                calls.append(True)
                return [finding]

            day = datetime(2026, 7, 21, 9)
            first = checker.run_hook(
                'codex', policy_path, cache, day, evaluator=missing
            )
            repeated = checker.run_hook(
                'codex', policy_path, cache, day, evaluator=missing
            )

            self.assertTrue(first.ran)
            self.assertFalse(repeated.ran)
            self.assertTrue(first.requires_user_prompt)
            self.assertFalse(repeated.requires_user_prompt)
            self.assertEqual(repeated.findings, ())
            self.assertEqual(len(calls), 1)

            next_day = checker.run_hook(
                'codex',
                policy_path,
                cache,
                day + timedelta(days=1),
                evaluator=missing,
            )

            self.assertTrue(next_day.ran)
            self.assertEqual(len(calls), 2)

    def test_hook_internal_failure_is_non_blocking_and_cached_for_the_day(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            policy_path = root / 'codex.json'
            policy_path.write_text('{"harness":"codex","tools":[]}\n', encoding='utf-8')

            def fail(_policy):
                raise RuntimeError('secret detector output')

            first = checker.run_hook('codex', policy_path, root / 'cache', evaluator=fail)
            second = checker.run_hook('codex', policy_path, root / 'cache', evaluator=fail)

            self.assertTrue(first.ran)
            self.assertFalse(second.ran)
            self.assertTrue(first.internal_error)
            rendered = json.loads(checker.render_hook_result(first, 'codex'))
            self.assertEqual(set(rendered), {'continue', 'systemMessage'})
            self.assertIs(rendered['continue'], True)

            cursor = json.loads(checker.render_hook_result(first, 'cursor'))
            self.assertEqual(cursor, {'continue': True})

    def test_detector_error_finding_is_cached_for_the_day(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            policy_path = root / 'codex.json'
            policy_path.write_text('{"harness":"codex","tools":[]}\n', encoding='utf-8')
            calls = []

            def detector_error(_policy):
                calls.append(True)
                return [
                    checker.Finding(
                        'detector-error',
                        'Example Tool',
                        'version detection failed',
                        'Retry later.',
                    )
                ]

            first = checker.run_hook(
                'codex', policy_path, root / 'cache', evaluator=detector_error
            )
            second = checker.run_hook(
                'codex', policy_path, root / 'cache', evaluator=detector_error
            )

            self.assertTrue(first.ran)
            self.assertFalse(second.ran)
            self.assertFalse(first.requires_user_prompt)
            self.assertEqual(len(calls), 1)

    def test_hook_output_uses_each_harness_native_shape(self):
        checker = self.checker
        result = checker.HookResult(
            True,
            (
                checker.Finding(
                    'tool-missing',
                    'Example Tool',
                    'is missing',
                    'Install it.',
                ),
            ),
        )

        codex = json.loads(checker.render_hook_result(result, 'codex'))
        cursor = json.loads(checker.render_hook_result(result, 'cursor'))
        copilot = json.loads(checker.render_hook_result(result, 'copilot'))

        self.assertEqual(
            set(codex),
            {'continue', 'systemMessage', 'hookSpecificOutput'},
        )
        self.assertIs(codex['continue'], True)
        self.assertIsInstance(codex['systemMessage'], str)
        self.assertEqual(
            set(codex['hookSpecificOutput']),
            {'hookEventName', 'additionalContext'},
        )
        self.assertEqual(
            codex['hookSpecificOutput']['hookEventName'],
            'SessionStart',
        )
        self.assertIsInstance(
            codex['hookSpecificOutput']['additionalContext'],
            str,
        )
        self.assertEqual(set(cursor), {'continue', 'user_message'})
        self.assertIs(cursor['continue'], False)
        self.assertIsInstance(cursor['user_message'], str)
        self.assertEqual(set(copilot), {'additionalContext'})
        self.assertIsInstance(copilot['additionalContext'], str)
        self.assertEqual(
            checker.render_hook_result(checker.HookResult(False), 'codex'),
            '',
        )

    def test_config_findings_request_one_consent_and_map_to_separate_actions(self):
        checker = self.checker
        result = checker.HookResult(
            True,
            (
                checker.Finding(
                    'required-value-mismatch',
                    'Codex multi-agent',
                    'is false; it must be true',
                    'Enable it and start a new session.',
                    'setting',
                    'multi_agent',
                    'configure',
                ),
                checker.Finding(
                    'required-value-mismatch',
                    'Codex parallel-agent capacity',
                    'allows 4 concurrent agents; it must allow at least 6',
                    'Raise the setting and start a new session.',
                    'setting',
                    'parallel_agent_capacity',
                    'configure',
                ),
            ),
        )

        rendered = json.loads(checker.render_hook_result(result, 'codex'))

        self.assertEqual(
            set(rendered),
            {'continue', 'systemMessage', 'hookSpecificOutput'},
        )
        self.assertIs(rendered['continue'], True)
        self.assertIn('at least 6', rendered['systemMessage'])
        self.assertIn('require approval', rendered['systemMessage'])
        context = rendered['hookSpecificOutput']['additionalContext']
        self.assertIn('--setting multi_agent', context)
        self.assertIn('configure --harness codex', context)
        self.assertIn('--setting parallel_agent_capacity', context)
        self.assertIn('--approved', context)

    def test_copilot_fleet_action_waits_for_consent_before_exposing_slash_command(self):
        checker = self.checker
        result = checker.HookResult(
            True,
            (
                checker.Finding(
                    'manual-session-action',
                    'GitHub Copilot fleet mode',
                    'requires explicit activation for parallel subagents in this session',
                    'Enable fleet mode in the current session after approval.',
                    'setting',
                    'fleet_mode',
                    'configure',
                ),
            ),
        )

        context = json.loads(
            checker.render_hook_result(result, 'copilot')
        )['additionalContext']

        self.assertIn('configure --harness copilot --setting fleet_mode', context)
        self.assertNotIn('Run /fleet', context)
        self.assertIn('manual action required', context)

    def test_cursor_context_delivery_instructs_headless_agent(self):
        checker = self.checker
        result = checker.HookResult(
            True,
            (
                checker.Finding(
                    'tool-missing',
                    'Example Tool',
                    'is missing',
                    'Install it.',
                    'tool',
                    'example',
                    'install',
                ),
            ),
        )

        rendered = json.loads(
            checker.render_hook_result(
                result,
                'cursor',
                delivery='context',
            )
        )

        self.assertEqual(set(rendered), {'additional_context'})
        message = rendered['additional_context']
        self.assertIn('Example Tool', message)
        self.assertIn('End this turn after requesting consent', message)
        self.assertIn('maintain_recommended_tools.py', message)

    def test_blocking_hook_outputs_request_consent_without_showing_commands(self):
        checker = self.checker
        result = checker.HookResult(
            True,
            (
                checker.Finding(
                    'tool-missing',
                    'Example Tool',
                    'is missing',
                    'Install it.',
                    'tool',
                    'example',
                    'install',
                ),
            ),
        )

        messages = (
            json.loads(checker.render_hook_result(result, 'codex'))['systemMessage'],
            json.loads(checker.render_hook_result(result, 'cursor'))['user_message'],
        )

        for message in messages:
            self.assertIn('Example Tool', message)
            self.assertIn('Reply with the names', message)
            self.assertNotIn('maintain_recommended_tools.py', message)
            self.assertNotIn('--approved', message)

    def test_agent_context_instructs_codex_and_copilot_to_request_consent_and_stop(self):
        checker = self.checker
        result = checker.HookResult(
            True,
            (
                checker.Finding(
                    'tool-missing',
                    'Example Tool',
                    'is missing',
                    'Install it.',
                    'tool',
                    'example',
                    'install',
                ),
            ),
        )

        messages = (
            json.loads(checker.render_hook_result(result, 'codex'))[
                'hookSpecificOutput'
            ]['additionalContext'],
            json.loads(checker.render_hook_result(result, 'copilot'))[
                'additionalContext'
            ],
        )

        for message in messages:
            self.assertIn(
                'Tell the user which tools or settings need a change and ask whether',
                message,
            )
            self.assertIn(
                'If the user explicitly declines all listed readiness actions',
                message,
            )
            self.assertIn('continue the original task', message)
            self.assertIn('End this turn after requesting consent', message)
            self.assertIn('Do not show the underlying maintenance commands', message)
            self.assertIn('maintain_recommended_tools.py', message)
            self.assertIn('--tool example --action install --approved', message)
            self.assertIn('plugin Hook support, not an exposed Skill', message)
        self.assertIn(
            'the named tool is a Codex plugin',
            messages[0],
        )
        self.assertIn('use an available Codex plugin-management tool', messages[0])

    def test_live_lock_suppresses_duplicate_and_stale_lock_is_reclaimed(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cache = root / 'cache'
            cache.mkdir()
            policy_path = root / 'codex.json'
            policy_path.write_text('{"harness":"codex","tools":[]}\n', encoding='utf-8')
            project = root / 'project'
            project.mkdir()
            (project / '.git').mkdir()
            project_cache = cache / checker._project_cache_key(project)
            project_cache.mkdir()
            lock = project_cache / 'codex.lock'
            lock.write_text('live\n', encoding='utf-8')
            calls = []

            busy = checker.run_hook(
                'codex', policy_path, cache, project_root=project,
                evaluator=lambda policy: calls.append(policy) or [],
            )
            old = time.time() - 1_000
            os.utime(lock, (old, old))
            reclaimed = checker.run_hook(
                'codex', policy_path, cache, project_root=project,
                evaluator=lambda policy: calls.append(policy) or [],
            )

            self.assertFalse(busy.ran)
            self.assertTrue(reclaimed.ran)
            self.assertEqual(len(calls), 1)
            self.assertFalse(lock.exists())

    def test_malformed_state_runs_once_and_unwritable_gate_skips_checks(self):
        checker = self.checker
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            policy_path = root / 'codex.json'
            policy_path.write_text('{"harness":"codex","tools":[]}\n', encoding='utf-8')
            cache = root / 'cache'
            project = root / 'project'
            project.mkdir()
            (project / '.git').mkdir()
            project_cache = cache / checker._project_cache_key(project)
            project_cache.mkdir(parents=True)
            (project_cache / 'codex.json').write_text('{bad', encoding='utf-8')
            calls = []

            malformed = checker.run_hook(
                'codex', policy_path, cache, project_root=project,
                evaluator=lambda policy: calls.append(policy) or [],
            )
            cache_file = root / 'not-a-directory'
            cache_file.write_text('occupied\n', encoding='utf-8')
            uncached = checker.run_hook(
                'codex', policy_path, cache_file, project_root=project,
                evaluator=lambda policy: calls.append(policy) or [],
            )

            self.assertTrue(malformed.ran)
            self.assertFalse(uncached.ran)
            self.assertTrue(uncached.internal_error)
            self.assertEqual(len(calls), 1)


class PythonLauncherContractTest(unittest.TestCase):
    launchers = (
        REPO_ROOT / 'runtime/recommended-tools/check_recommended_tools.sh',
        REPO_ROOT / 'runtime/rules/dispatch.sh',
        REPO_ROOT / 'runtime/recommended-tools/check_recommended_tools.ps1',
        REPO_ROOT / 'runtime/rules/dispatch.ps1',
    )

    def test_launchers_share_the_bounded_python_contract(self):
        failure = (
            'ERROR: Python 3.8 or newer is required; '
            'checked python.'
        )
        for launcher in self.launchers:
            with self.subTest(launcher=launcher.relative_to(REPO_ROOT).as_posix()):
                content = launcher.read_text(encoding='utf-8')
                self.assertIn(failure, content)
                self.assertIn("sys.version_info < (3, 8)", content)
                if launcher.suffix == '.sh':
                    self.assertIn('command -v python', content)
                else:
                    self.assertIn("Get-Command python -CommandType Application", content)
                    self.assertIn('catch {', content)
                self.assertNotIn('python3', content)
                self.assertNotIn('uv python find', content)
                self.assertNotIn('Get-Command py ', content)

    @unittest.skipUnless(os.name == 'nt', 'requires Windows PowerShell')
    def test_powershell_launchers_forward_to_compatible_python(self):
        powershell = shutil.which('powershell') or shutil.which('pwsh')
        if not powershell:
            self.skipTest('PowerShell executable is unavailable')

        for launcher in self.launchers:
            if launcher.suffix != '.ps1':
                continue
            with self.subTest(launcher=launcher.relative_to(REPO_ROOT).as_posix()):
                completed = subprocess.run(
                    [
                        powershell,
                        '-NoProfile',
                        '-ExecutionPolicy',
                        'Bypass',
                        '-Command',
                        f"& '{launcher}' --help",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertIn('usage:', completed.stdout.lower())

    @unittest.skipUnless(os.name == 'posix', 'requires a POSIX shell')
    def test_rule_launcher_uses_python_without_probing_python3(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            executable_root = Path(temp_dir)
            (executable_root / 'python3').write_text(
                '#!/bin/sh\n: > "$DECOY_MARKER"\nexit 1\n', encoding='utf-8'
            )
            (executable_root / 'python3').chmod(0o755)
            (executable_root / 'python').symlink_to(sys.executable)
            dirname = shutil.which('dirname')
            self.assertIsNotNone(dirname)
            (executable_root / 'dirname').symlink_to(dirname)
            environment = dict(os.environ)
            environment['PATH'] = str(executable_root)
            environment['DECOY_MARKER'] = str(executable_root / 'decoy-used')

            completed = subprocess.run(
                ('/bin/sh', str(REPO_ROOT / 'runtime/rules/dispatch.sh'), '--help'),
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )

            self.assertFalse((executable_root / 'decoy-used').exists())

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('usage:', completed.stdout.lower())

    @unittest.skipUnless(os.name == 'posix', 'requires a POSIX shell')
    def test_readiness_hook_reports_missing_python_through_host_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            executable_root = Path(temp_dir)
            dirname = shutil.which('dirname')
            self.assertIsNotNone(dirname)
            (executable_root / 'dirname').symlink_to(dirname)
            for name in ('python3', 'python'):
                candidate = executable_root / name
                candidate.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
                candidate.chmod(0o755)
            environment = dict(os.environ)
            environment['PATH'] = str(executable_root)

            completed = subprocess.run(
                (
                    '/bin/sh',
                    str(REPO_ROOT / 'runtime/recommended-tools/check_recommended_tools.sh'),
                    'hook', '--harness', 'codex',
                ),
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(
            json.loads(completed.stdout),
            {
                'continue': True,
                'systemMessage': (
                    'ERROR: Python 3.8 or newer is required; '
                    'checked python.'
                ),
            },
        )
        self.assertIn('ERROR: Python 3.8 or newer is required', completed.stderr)

    def test_host_launchers_require_python_and_preserve_exit_contracts(self):
        powershell = shutil.which('powershell') or shutil.which('pwsh')
        host_launchers = []
        for launcher in self.launchers:
            if launcher.suffix == '.sh' and os.name == 'posix':
                host_launchers.append((launcher, ['/bin/sh', str(launcher)]))
            elif launcher.suffix == '.ps1' and powershell:
                host_launchers.append((launcher, [powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(launcher)]))
        if not host_launchers:
            self.skipTest('no supported host shell')
        failure = 'ERROR: Python 3.8 or newer is required; checked python.'
        for launcher, command in host_launchers:
            for availability in ('missing', 'incompatible', 'compatible'):
                with self.subTest(launcher=launcher.name, availability=availability):
                    with tempfile.TemporaryDirectory(prefix='python hook ') as temp_dir:
                        root = Path(temp_dir)
                        suffix = '.cmd' if os.name == 'nt' else ''
                        decoy = root / ('python3' + suffix)
                        marker = root / 'decoy-used'
                        if os.name == 'nt':
                            decoy.write_text('@echo decoy>"%DECOY_MARKER%"\n@exit /b 0\n')
                        else:
                            decoy.write_text('#!/bin/sh\n: > "$DECOY_MARKER"\nexit 0\n')
                            decoy.chmod(0o755)
                            dirname = shutil.which('dirname')
                            self.assertIsNotNone(dirname)
                            (root / 'dirname').symlink_to(dirname)
                        if availability != 'missing':
                            candidate = root / ('python' + suffix)
                            probe_exit = 0 if availability == 'compatible' else 1
                            if os.name == 'nt':
                                candidate.write_text(
                                    '@echo off\n'
                                    'if "%~1"=="-c" (\n'
                                    '  echo probe-noise\n'
                                    f'  exit /b {probe_exit}\n'
                                    ')\n'
                                    'echo forwarded\nexit /b 7\n'
                                )
                            else:
                                candidate.write_text(
                                    '#!/bin/sh\n'
                                    'if [ "$1" = "-c" ]; then\n'
                                    f'  echo probe-noise; exit {probe_exit}\n'
                                    'fi\n'
                                    'echo forwarded\nexit 7\n'
                                )
                                candidate.chmod(0o755)
                        environment = dict(os.environ, PATH=str(root), DECOY_MARKER=str(marker))
                        result = subprocess.run(command + ['--help'], env=environment, cwd=root,
                                                capture_output=True, text=True)
                        self.assertFalse(marker.exists())
                        self.assertNotIn('probe-noise', result.stdout + result.stderr)
                        if availability == 'compatible':
                            self.assertEqual(result.returncode, 7, result.stderr)
                            self.assertEqual(result.stdout.strip(), 'forwarded')
                        else:
                            self.assertEqual(result.returncode, 2, result.stderr)
                            self.assertEqual(result.stdout, '')
                            self.assertEqual(result.stderr.strip(), failure)
                        if launcher.stem == 'check_recommended_tools':
                            result = subprocess.run(command + ['hook', '--harness', 'codex'],
                                                    env=environment, cwd=root, capture_output=True, text=True)
                            self.assertEqual(result.returncode, 0, result.stderr)
                            if availability == 'compatible':
                                self.assertEqual(result.stdout.strip(), 'forwarded')
                            else:
                                self.assertEqual(json.loads(result.stdout),
                                                 {'continue': True, 'systemMessage': failure})


class RecommendedToolMaintainerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maintainer = load_maintainer()

    def test_every_recommended_tool_has_install_and_upgrade_handling(self):
        for policy_path in sorted(POLICY_ROOT.glob('*.json')):
            policy = json.loads(policy_path.read_text(encoding='utf-8'))
            harness = policy['harness']
            for tool in policy['tools']:
                for action in ('install', 'upgrade'):
                    with self.subTest(harness=harness, tool=tool['id'], action=action):
                        recipe = self.maintainer.resolve_recipe(harness, tool['id'], action)
                        self.assertTrue(recipe.command or recipe.manual_guidance)
                        self.assertFalse(recipe.command and recipe.manual_guidance)


    def test_maintenance_requires_consent_before_execution(self):
        executor = mock.Mock()

        with self.assertRaises(self.maintainer.ApprovalRequired):
            self.maintainer.apply_maintenance(
                'codex',
                'codegraph',
                'install',
                approved=False,
                executor=executor,
            )

        executor.assert_not_called()

    def test_configuration_requires_consent_before_write(self):
        rpc = mock.Mock(side_effect=AssertionError('configuration must remain unchanged'))

        with self.assertRaises(self.maintainer.ApprovalRequired):
            self.maintainer.configure_setting(
                'codex',
                'parallel_agent_capacity',
                approved=False,
                rpc=rpc,
            )

        rpc.assert_not_called()

    def test_approved_copilot_fleet_action_returns_current_session_instruction(self):
        rpc = mock.Mock(side_effect=AssertionError('manual action must not write config'))
        with mock.patch.object(
            self.maintainer.checker,
            '_manual_session_action_available',
            return_value=True,
        ):
            result = self.maintainer.configure_setting(
                'copilot',
                'fleet_mode',
                approved=True,
                rpc=rpc,
            )

        self.assertEqual(result.status, 'manual-action-required')
        self.assertIn('Run /fleet', result.detail)
        self.assertIn('current Copilot CLI session', result.detail)
        rpc.assert_not_called()

    def test_approved_capacity_configuration_writes_five_and_verifies_six_total(self):
        effective = [{'agents': {'max_threads': 3}}]
        calls = []

        def rpc(method, params):
            calls.append((method, params))
            if method == 'config/value/write':
                effective[0] = {
                    'agents': {
                        'max_concurrent_threads_per_session': params['value'],
                    }
                }
                return {}
            return {'config': effective[0]}

        result = self.maintainer.configure_setting(
            'codex',
            'parallel_agent_capacity',
            approved=True,
            project_root=REPO_ROOT,
            rpc=rpc,
        )

        self.assertEqual(result.status, 'completed')
        self.assertEqual(
            calls[1],
            (
                'config/value/write',
                {
                    'keyPath': 'agents.max_concurrent_threads_per_session',
                    'value': 5,
                    'mergeStrategy': 'upsert',
                },
            ),
        )
        self.assertEqual(
            [method for method, _params in calls],
            ['config/read', 'config/value/write', 'config/read'],
        )

    def test_approved_multi_agent_configuration_uses_policy_write(self):
        rpc = mock.Mock(return_value={})
        with mock.patch.object(
            self.maintainer,
            '_configuration_required',
            side_effect=(True, False),
        ):
            result = self.maintainer.configure_setting(
                'codex',
                'multi_agent',
                approved=True,
                project_root=REPO_ROOT,
                rpc=rpc,
            )

        self.assertEqual(result.status, 'completed')
        rpc.assert_called_once_with(
            'config/value/write',
            {
                'keyPath': 'features.multi_agent',
                'value': True,
                'mergeStrategy': 'upsert',
            },
        )

    def test_configure_cli_dispatches_only_with_approved_marker(self):
        completed = self.maintainer.MaintenanceResult(
            'codex',
            'parallel_agent_capacity',
            'Codex parallel-agent capacity',
            'configure',
            'completed',
        )
        with mock.patch.object(
            self.maintainer,
            'configure_setting',
            return_value=completed,
        ) as configure, mock.patch('builtins.print'):
            exit_code = self.maintainer.main([
                'configure',
                '--harness',
                'codex',
                '--setting',
                'parallel_agent_capacity',
                '--approved',
            ])

        self.assertEqual(exit_code, 0)
        configure.assert_called_once_with(
            'codex',
            'parallel_agent_capacity',
            approved=True,
            policy_path=None,
        )

    def test_approved_maintenance_executes_allowlisted_recipe_and_hides_command(self):
        executor = mock.Mock(return_value=mock.Mock(returncode=0))
        with mock.patch.object(
            self.maintainer,
            'required_action',
            side_effect=('upgrade', None),
        ):
            result = self.maintainer.apply_maintenance(
                'codex',
                'codegraph',
                'upgrade',
                approved=True,
                executor=executor,
            )

        self.assertEqual(result.status, 'completed')
        executor.assert_called_once_with(
            ['codegraph', 'upgrade'],
            check=False,
        )
        rendered = self.maintainer.render_result(result)
        self.assertIn('CodeGraph', rendered)
        self.assertIn('upgrade completed', rendered)
        self.assertNotIn('codegraph upgrade', rendered)

    def test_retired_plugin_is_not_a_supported_maintenance_target(self):
        for harness in ('codex', 'cursor', 'copilot'):
            with self.subTest(harness=harness):
                with self.assertRaises(self.maintainer.MaintenanceError):
                    self.maintainer.resolve_recipe(harness, 'superpowers', 'install')

    def test_manual_recipe_returns_manual_action_without_execution(self):
        executor = mock.Mock()
        with mock.patch.object(self.maintainer, 'required_action', return_value='install'):
            result = self.maintainer.apply_maintenance(
                'cursor',
                'cursor-agent',
                'install',
                approved=True,
                executor=executor,
            )

        self.assertEqual(result.status, 'manual-action-required')
        self.assertIn('official Cursor distribution', result.detail)
        executor.assert_not_called()


if __name__ == '__main__':
    unittest.main()
