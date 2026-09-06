"""Exercise public Python CLIs on each runtime in the CI matrix."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY_POINTS = (
    'runtime/rules/dispatch.py',
    'runtime/recommended-tools/check_recommended_tools.py',
    'runtime/recommended-tools/maintain_recommended_tools.py',
    'skills/write-rules-and-skills/scripts/candidate_evidence.py',
    'skills/diagnose-agent-session/scripts/timing.py',
    'skills/finish-worktree/scripts/worktree_evidence.py',
    'skills/finish-worktree/scripts/worktree_transfer.py',
    'skills/finish-worktree/scripts/consolidate_worktree_history.py',
    'skills/setup-project-agents/scripts/workflow.py',
    'scripts/sync_agent_adapters.py',
    'scripts/sync_cursor_rule_adapters.py',
    'scripts/sync_mcp_adapters.py',
    'scripts/sync_plugin_version.py',
    'scripts/update_external_skills.py',
)


class PythonEntryPointTests(unittest.TestCase):
    def test_public_help_runs_outside_the_repository(self):
        with tempfile.TemporaryDirectory(prefix='python CLI caller ') as caller:
            for relative in ENTRY_POINTS:
                with self.subTest(entry=relative):
                    result = subprocess.run(
                        [sys.executable, '-B', str(ROOT / relative), '--help'],
                        cwd=caller, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('usage:', result.stdout.lower())


if __name__ == '__main__':
    unittest.main()
