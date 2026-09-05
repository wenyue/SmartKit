#!/usr/bin/env python3
"""Apply one approved recommended-tool maintenance action."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import check_recommended_tools as checker  # noqa: E402


class MaintenanceError(RuntimeError):
    """Raised when an approved maintenance action cannot be applied safely."""


class ApprovalRequired(MaintenanceError):
    """Raised when the caller has not recorded explicit user consent."""


@dataclass(frozen=True)
class Recipe:
    tool_name: str
    command: tuple[str, ...] | None = None
    manual_guidance: str | None = None


@dataclass(frozen=True)
class MaintenanceResult:
    harness: str
    tool_id: str
    tool_name: str
    action: str
    status: str
    detail: str = ''


_COMMON_RECIPES = {
    'codegraph': {
        'install': Recipe(
            'CodeGraph',
            command=('npm', 'install', '--global', '@colbymchenry/codegraph@latest'),
        ),
        'upgrade': Recipe('CodeGraph', command=('codegraph', 'upgrade')),
    },
    'tokscale': {
        'install': Recipe(
            'Tokscale',
            command=('npm', 'install', '--global', 'tokscale@latest'),
        ),
        'upgrade': Recipe(
            'Tokscale',
            command=('npm', 'install', '--global', 'tokscale@latest'),
        ),
    },
}

_HARNESS_RECIPES = {
    'codex': {
        'codex': {
            'install': Recipe(
                'Codex CLI',
                manual_guidance='Install Codex CLI from the official OpenAI distribution.',
            ),
            'upgrade': Recipe('Codex CLI', command=('codex', 'update')),
        },
    },
    'cursor': {
        'cursor-agent': {
            'install': Recipe(
                'Cursor Agent CLI',
                manual_guidance='Install Cursor Agent CLI from the official Cursor distribution.',
            ),
            'upgrade': Recipe('Cursor Agent CLI', command=('agent', 'update')),
        },
    },
    'copilot': {
        'copilot': {
            'install': Recipe(
                'GitHub Copilot CLI',
                manual_guidance=(
                    'Install GitHub Copilot CLI from the official GitHub distribution.'
                ),
            ),
            'upgrade': Recipe('GitHub Copilot CLI', command=('copilot', 'update')),
        },
    },
    'qoder': {},
}


def resolve_recipe(harness: str, tool_id: str, action: str) -> Recipe:
    if action not in {'install', 'upgrade'}:
        raise MaintenanceError('maintenance action must be install or upgrade')
    recipes = _HARNESS_RECIPES.get(harness)
    if recipes is None:
        raise MaintenanceError('unsupported harness')
    tool_recipes = recipes.get(tool_id) or _COMMON_RECIPES.get(tool_id)
    if tool_recipes is None or action not in tool_recipes:
        raise MaintenanceError('unsupported recommended tool')
    return tool_recipes[action]


def _tool_policy(harness: str, tool_id: str, policy_path: Path | None) -> dict:
    path = policy_path or checker.default_policy_path(harness)
    policy = checker.load_policy(path, harness)
    for raw_tool in policy['tools']:
        tool = checker._validate_tool(raw_tool)
        if tool['id'] == tool_id:
            return tool
    raise MaintenanceError('recommended tool is not present in the selected policy')


def _configuration_policy(
    harness: str,
    setting_id: str,
    policy_path: Path | None,
) -> tuple[str, dict[str, Any]]:
    path = policy_path or checker.default_policy_path(harness)
    policy = checker.load_policy(path, harness)
    for raw_requirement in policy.get('required_values', []):
        requirement = checker._validate_required_value(raw_requirement)
        if requirement['id'] == setting_id and requirement.get('maintenance'):
            return 'required-value', requirement
    for raw_requirement in policy.get('config_requirements', []):
        requirement = checker._validate_config_requirement(raw_requirement)
        if requirement['id'] == setting_id:
            return 'minimum-threads', requirement
    for raw_action in policy.get('manual_session_actions', []):
        action = checker._validate_manual_session_action(raw_action)
        if action['id'] == setting_id:
            return 'manual-session', action
    raise MaintenanceError('configuration setting is not present in the selected policy')


def _configuration_required(
    kind: str,
    requirement: dict[str, Any],
    project_root: Path,
    request: Callable[[str, dict[str, Any]], dict[str, Any]],
) -> bool:
    if kind == 'required-value':
        findings = checker._check_required_values({
            'required_values': [requirement],
        })
        if not findings:
            return False
        if findings[0].code == 'detector-error':
            raise MaintenanceError('configuration state could not be determined safely')
        return True
    response = request(
        'config/read',
        {'includeLayers': False, 'cwd': str(project_root)},
    )
    spawned = checker._effective_spawned_threads(
        response,
        requirement['read_key_paths'],
    )
    target = requirement['minimum_total_threads'] - requirement['primary_threads']
    return spawned is None or spawned < target


def required_action(
    harness: str,
    tool_id: str,
    policy_path: Path | None = None,
) -> str | None:
    tool = _tool_policy(harness, tool_id, policy_path)
    findings = checker.check_policy({'harness': harness, 'tools': [tool]})
    if not findings:
        return None
    code = findings[0].code
    if code == 'tool-missing':
        return 'install'
    if code in {'version-not-greater', 'version-unreadable'}:
        return 'upgrade'
    raise MaintenanceError('recommended-tool state could not be determined safely')


def apply_maintenance(
    harness: str,
    tool_id: str,
    action: str,
    *,
    approved: bool,
    policy_path: Path | None = None,
    executor: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> MaintenanceResult:
    if not approved:
        raise ApprovalRequired('user consent is required before maintenance')
    recipe = resolve_recipe(harness, tool_id, action)
    current_action = required_action(harness, tool_id, policy_path)
    if current_action is None:
        return MaintenanceResult(
            harness,
            tool_id,
            recipe.tool_name,
            action,
            'already-satisfied',
        )
    if current_action != action:
        raise MaintenanceError('requested action does not match the current tool state')
    if recipe.manual_guidance:
        return MaintenanceResult(
            harness,
            tool_id,
            recipe.tool_name,
            action,
            'manual-action-required',
            recipe.manual_guidance,
        )
    assert recipe.command is not None
    try:
        completed = executor(list(recipe.command), check=False)
    except OSError:
        return MaintenanceResult(
            harness,
            tool_id,
            recipe.tool_name,
            action,
            'failed',
        )
    if completed.returncode != 0:
        return MaintenanceResult(
            harness,
            tool_id,
            recipe.tool_name,
            action,
            'failed',
        )
    if required_action(harness, tool_id, policy_path) is not None:
        return MaintenanceResult(
            harness,
            tool_id,
            recipe.tool_name,
            action,
            'verification-failed',
        )
    return MaintenanceResult(
        harness,
        tool_id,
        recipe.tool_name,
        action,
        'completed',
    )


def configure_setting(
    harness: str,
    setting_id: str,
    *,
    approved: bool,
    policy_path: Path | None = None,
    project_root: Path | None = None,
    rpc: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
) -> MaintenanceResult:
    if not approved:
        raise ApprovalRequired('user consent is required before maintenance')
    kind, requirement = _configuration_policy(harness, setting_id, policy_path)
    maintenance = requirement['maintenance']
    if kind == 'manual-session':
        if not checker._manual_session_action_available(requirement):
            raise MaintenanceError('manual session action is unavailable')
        return MaintenanceResult(
            harness,
            setting_id,
            requirement['name'],
            'configure',
            'manual-action-required',
            maintenance['instruction'],
        )
    if harness != 'codex':
        raise MaintenanceError('configuration maintenance is unsupported for this harness')
    project_root = checker.resolve_project_root(project_root)

    def apply(request: Callable[[str, dict[str, Any]], dict[str, Any]]) -> MaintenanceResult:
        if not _configuration_required(kind, requirement, project_root, request):
            return MaintenanceResult(
                harness,
                setting_id,
                requirement['name'],
                'configure',
                'already-satisfied',
            )
        request(
            'config/value/write',
            {
                'keyPath': maintenance['write_key_path'],
                'value': maintenance['write_value'],
                'mergeStrategy': 'upsert',
            },
        )
        if _configuration_required(kind, requirement, project_root, request):
            return MaintenanceResult(
                harness,
                setting_id,
                requirement['name'],
                'configure',
                'verification-failed',
            )
        return MaintenanceResult(
            harness,
            setting_id,
            requirement['name'],
            'configure',
            'completed',
        )

    try:
        if rpc is not None:
            return apply(rpc)
        with checker._CodexConfigRpcClient(project_root) as client:
            return apply(client.request)
    except (checker.PolicyError, checker.DetectorError, OSError) as error:
        raise MaintenanceError('configuration maintenance failed') from error


def render_result(result: MaintenanceResult) -> str:
    action_name = {
        'install': 'installation',
        'upgrade': 'upgrade',
        'configure': 'configuration',
    }[result.action]
    prefix = f'[smartkit] {result.tool_name}'
    if result.status == 'completed':
        return f'{prefix}: {action_name} completed.'
    if result.status == 'already-satisfied':
        return f'{prefix}: already satisfies the recommendation.'
    if result.status == 'manual-action-required':
        return f'{prefix}: manual action required. {result.detail}'
    if result.status == 'verification-failed':
        return f'{prefix}: {action_name} ran, but verification still reports a finding.'
    return f'{prefix}: {action_name} failed.'


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    apply = subparsers.add_parser('apply')
    apply.add_argument('--harness', required=True, choices=('codex', 'cursor', 'copilot', 'qoder'))
    apply.add_argument('--tool', required=True)
    apply.add_argument('--action', required=True, choices=('install', 'upgrade'))
    apply.add_argument('--approved', action='store_true')
    apply.add_argument('--policy', type=Path)
    configure = subparsers.add_parser('configure')
    configure.add_argument(
        '--harness',
        required=True,
        choices=('codex', 'copilot'),
    )
    configure.add_argument('--setting', required=True)
    configure.add_argument('--approved', action='store_true')
    configure.add_argument('--policy', type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == 'apply':
            result = apply_maintenance(
                args.harness,
                args.tool,
                args.action,
                approved=args.approved,
                policy_path=args.policy,
            )
        else:
            result = configure_setting(
                args.harness,
                args.setting,
                approved=args.approved,
                policy_path=args.policy,
            )
    except ApprovalRequired:
        print('[smartkit] User consent is required before maintenance.', file=sys.stderr)
        return 2
    except (MaintenanceError, checker.PolicyError):
        print('[smartkit] Maintenance could not proceed safely.', file=sys.stderr)
        return 2
    print(render_result(result))
    if result.status in {'completed', 'already-satisfied'}:
        return 0
    if result.status == 'manual-action-required':
        return 3
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
