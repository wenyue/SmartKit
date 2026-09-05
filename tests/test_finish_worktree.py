import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/finish-worktree/scripts/consolidate_worktree_history.py"
SHELL_LAUNCHER = SCRIPT.with_suffix(".sh")
POWERSHELL_LAUNCHER = SCRIPT.with_suffix(".ps1")
PYTHON_ERROR = (
    "ERROR: Python 3.10 or newer is required; checked python3, then python."
)


def git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


class FinishWorktreeHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.root = root
        self.base = root / "base"
        self.task = root / "task"
        self.marker = root / "pre-commit-ran"
        self.message = root / "message.txt"

        git(root, "init", "--quiet", "--initial-branch=main", str(self.base))
        git(self.base, "config", "user.name", "SmartKit Test")
        git(self.base, "config", "user.email", "smartkit@example.invalid")
        (self.base / "artifact.txt").write_text("base\n", encoding="utf-8")
        git(self.base, "add", "artifact.txt")
        git(self.base, "commit", "--quiet", "-m", "base")
        self.target = git(self.base, "rev-parse", "HEAD")
        git(self.base, "worktree", "add", "--quiet", "-b", "task", str(self.task))

        (self.task / "artifact.txt").write_text("checkpoint one\n", encoding="utf-8")
        git(self.task, "commit", "--quiet", "-am", "checkpoint one")
        (self.task / "artifact.txt").write_text("checkpoint two\n", encoding="utf-8")
        git(self.task, "commit", "--quiet", "-am", "review fix")
        self.checkpoint_head = git(self.task, "rev-parse", "HEAD")
        self.checkpoint_tree = git(self.task, "rev-parse", "HEAD^{tree}")
        self.message.write_text("feat: deliver task\n", encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def install_hook(self, exit_code: int) -> None:
        hooks = Path(git(self.task, "rev-parse", "--git-common-dir")) / "hooks"
        if not hooks.is_absolute():
            hooks = (self.task / hooks).resolve()
        hook = hooks / "pre-commit"
        hook.write_text(
            f"#!/bin/sh\nprintf ran > '{self.marker}'\nexit {exit_code}\n",
            encoding="utf-8",
        )
        hook.chmod(hook.stat().st_mode | 0o111)

    def run_script(
        self, recovery_ref: str, target: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repository",
                str(self.task),
                "--target",
                target or self.target,
                "--message-file",
                str(self.message),
                "--recovery-ref",
                recovery_ref,
            ],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "GIT_CONFIG_NOSYSTEM": "1"},
        )

    def test_consolidates_checkpoints_through_normal_commit_hooks(self):
        self.install_hook(0)
        recovery_ref = "refs/smartkit/recovery/task/success"

        result = self.run_script(recovery_ref)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        delivery_commit = payload["delivery_commit"]
        self.assertTrue(self.marker.exists())
        self.assertEqual(git(self.task, "symbolic-ref", "--short", "HEAD"), "task")
        self.assertEqual(git(self.task, "rev-list", "--count", "main..task"), "1")
        self.assertEqual(git(self.task, "show", "-s", "--format=%P", delivery_commit), self.target)
        self.assertEqual(git(self.task, "rev-parse", f"{delivery_commit}^{{tree}}"), self.checkpoint_tree)
        self.assertEqual(git(self.task, "rev-parse", recovery_ref), self.checkpoint_head)
        self.assertEqual(git(self.task, "status", "--porcelain"), "")

    def test_rejected_hook_restores_task_branch_and_retains_recovery(self):
        self.install_hook(1)
        recovery_ref = "refs/smartkit/recovery/task/rejected"

        result = self.run_script(recovery_ref)

        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.marker.exists())
        self.assertEqual(git(self.task, "symbolic-ref", "--short", "HEAD"), "task")
        self.assertEqual(git(self.task, "rev-parse", "HEAD"), self.checkpoint_head)
        self.assertEqual(git(self.task, "rev-parse", recovery_ref), self.checkpoint_head)
        self.assertEqual(git(self.task, "status", "--porcelain"), "")

    def test_existing_recovery_ref_is_rejected_without_mutating_task(self):
        recovery_ref = "refs/smartkit/recovery/task/existing"
        git(self.task, "update-ref", recovery_ref, self.checkpoint_head)

        result = self.run_script(recovery_ref)

        self.assertEqual(result.returncode, 1)
        self.assertIn("recovery ref already exists", result.stderr)
        self.assertEqual(git(self.task, "symbolic-ref", "--short", "HEAD"), "task")
        self.assertEqual(git(self.task, "rev-parse", "HEAD"), self.checkpoint_head)
        self.assertEqual(git(self.task, "rev-parse", recovery_ref), self.checkpoint_head)
        self.assertEqual(git(self.task, "status", "--porcelain"), "")

    def test_recovery_ref_outside_namespace_is_rejected_before_effect(self):
        recovery_ref = "refs/recovery/task/wrong-namespace"
        refs_before = git(self.task, "for-each-ref", "--format=%(refname):%(objectname)")

        result = self.run_script(recovery_ref)

        self.assertEqual(result.returncode, 1)
        self.assertIn("recovery ref must start with refs/smartkit/recovery/", result.stderr)
        self.assertEqual(
            git(self.task, "for-each-ref", "--format=%(refname):%(objectname)"),
            refs_before,
        )
        self.assertEqual(git(self.task, "symbolic-ref", "--short", "HEAD"), "task")
        self.assertEqual(git(self.task, "rev-parse", "HEAD"), self.checkpoint_head)
        self.assertEqual(git(self.task, "status", "--porcelain"), "")

    def test_candidate_ref_creation_failure_does_not_claim_it_was_retained(self):
        recovery_ref = "refs/smartkit/recovery/task/candidate-collision"
        candidate_ref = f"{recovery_ref}-candidate"
        git(self.task, "update-ref", candidate_ref, self.target)

        result = self.run_script(recovery_ref)

        self.assertEqual(result.returncode, 1)
        self.assertIn("recovery ref already exists", result.stderr)
        self.assertIn(candidate_ref, result.stderr)
        self.assertNotIn(f"candidate retained at {candidate_ref}", result.stderr)
        self.assertEqual(git(self.task, "symbolic-ref", "--short", "HEAD"), "task")
        self.assertEqual(git(self.task, "rev-parse", "HEAD"), self.checkpoint_head)
        self.assertNotEqual(subprocess.run(
            ["git", "-C", str(self.task), "show-ref", "--verify", "--quiet", recovery_ref],
            check=False,
        ).returncode, 0)
        self.assertEqual(git(self.task, "rev-parse", candidate_ref), self.target)
        self.assertEqual(git(self.task, "status", "--porcelain"), "")

    def test_equal_target_is_rejected_without_creating_empty_commit(self):
        recovery_ref = "refs/smartkit/recovery/task/already-delivered"

        result = self.run_script(recovery_ref, target=self.checkpoint_head)

        self.assertEqual(result.returncode, 1)
        self.assertIn("checkpoint HEAD equals the delivery target", result.stderr)
        self.assertEqual(git(self.task, "symbolic-ref", "--short", "HEAD"), "task")
        self.assertEqual(git(self.task, "rev-parse", "HEAD"), self.checkpoint_head)
        self.assertNotEqual(
            subprocess.run(
                ["git", "-C", str(self.task), "show-ref", "--verify", "--quiet", recovery_ref],
                check=False,
            ).returncode,
            0,
        )
        self.assertEqual(git(self.task, "status", "--porcelain"), "")


    def test_hook_edit_is_retained_when_checkout_recovery_would_change_state(self):
        self.install_hook(1)
        hooks = Path(git(self.task, "rev-parse", "--git-common-dir")) / "hooks"
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\nprintf 'hook edit\\n' > artifact.txt\nexit 1\n")
        result = self.run_script("refs/smartkit/recovery/task/hook-edit")
        self.assertEqual(result.returncode, 1)
        self.assertIn("checkout recovery stopped", result.stderr)
        self.assertEqual((self.task / "artifact.txt").read_text(), "hook edit\n")
        self.assertEqual(git(self.task, "rev-parse", "refs/heads/task"), self.checkpoint_head)
        self.assertEqual(git(self.task, "rev-parse", "HEAD"), self.target)

    def test_dirty_source_rejects_history_before_recovery_ref_creation(self):
        (self.task / "unfinished.txt").write_text("unfinished\n")
        refs_before = git(self.task, "for-each-ref", "--format=%(refname):%(objectname)")
        result = self.run_script("refs/smartkit/recovery/task/dirty")
        self.assertEqual(result.returncode, 1)
        self.assertIn("source worktree is not clean", result.stderr)
        self.assertEqual(git(self.task, "for-each-ref", "--format=%(refname):%(objectname)"), refs_before)
        self.assertEqual((self.task / "unfinished.txt").read_text(), "unfinished\n")

class FinishWorktreeLauncherTests(unittest.TestCase):
    @staticmethod
    def write_command(directory: Path, name: str, body: str) -> None:
        command = directory / name
        command.write_text("#!/bin/sh\n" + body, encoding="utf-8")
        command.chmod(0o755)

    @unittest.skipUnless(os.name == "posix", "requires a POSIX shell")
    def test_shell_launcher_checks_python3_then_python_and_forwards_arguments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            command_dir = Path(temp_dir)
            trace = command_dir / "trace"
            self.write_command(
                command_dir,
                "python3",
                'printf \'python3:%s\\n\' "$1" >> "$TRACE"\nexit 1\n',
            )
            self.write_command(
                command_dir,
                "python",
                'printf \'python:%s\\n\' "$1" >> "$TRACE"\n'
                'if [ "$1" = "-c" ]; then exit 0; fi\n'
                'printf \'argument:%s\\n\' "$2" "$3" >> "$TRACE"\n'
                'exit 7\n',
            )
            environment = {
                **os.environ,
                "PATH": str(command_dir),
                "TRACE": str(trace),
            }

            completed = subprocess.run(
                ("/bin/sh", str(SHELL_LAUNCHER), "--sentinel", "value"),
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=environment,
            )

            self.assertEqual(completed.returncode, 7)
            self.assertEqual(
                trace.read_text(encoding="utf-8").splitlines(),
                [
                    "python3:-c",
                    "python:-c",
                    f"python:{SCRIPT}",
                    "argument:--sentinel",
                    "argument:value",
                ],
            )

    @unittest.skipUnless(os.name == "posix", "requires a POSIX shell")
    def test_shell_launcher_reports_exact_error_when_both_candidates_fail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            command_dir = Path(temp_dir)
            for name in ("python3", "python"):
                self.write_command(
                    command_dir,
                    name,
                    "printf 'probe stdout\\n'\n"
                    "printf 'probe stderr\\n' >&2\n"
                    "exit 1\n",
                )

            completed = subprocess.run(
                ("/bin/sh", str(SHELL_LAUNCHER), "--help"),
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PATH": str(command_dir)},
            )

            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(completed.stderr.strip(), PYTHON_ERROR)

    def test_powershell_launcher_has_the_same_bounded_candidate_contract(self):
        wrapper = POWERSHELL_LAUNCHER.read_text(encoding="utf-8")

        self.assertIn("@('python3', 'python')", wrapper)
        self.assertIn("sys.version_info < (3, 10)", wrapper)
        self.assertIn("*> $null", wrapper)
        self.assertIn("$LASTEXITCODE = $null", wrapper)
        self.assertIn("try {", wrapper)
        self.assertIn("catch {", wrapper)
        self.assertIn(
            "$probeSucceeded = $null -ne $LASTEXITCODE -and $LASTEXITCODE -eq 0",
            wrapper,
        )
        self.assertIn(PYTHON_ERROR, wrapper)
        self.assertIn("exit 2", wrapper)
        self.assertNotIn("py -3", wrapper)
        self.assertNotIn("python3.*", wrapper)
        self.assertNotIn("uv python", wrapper)


if __name__ == "__main__":
    unittest.main()
