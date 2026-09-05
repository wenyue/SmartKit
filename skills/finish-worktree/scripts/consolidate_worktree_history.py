"""Consolidate a clean worktree branch into one hook-validated Delivery Commit."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


RECOVERY_PREFIX = "refs/smartkit/recovery/"


class ConsolidationError(RuntimeError):
    pass


def run_git(repository: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ConsolidationError(f"git {' '.join(args)} failed: {detail}")
    return result


def git_output(repository: Path, *args: str) -> str:
    return run_git(repository, *args).stdout.strip()


def require_clean(repository: Path) -> None:
    if run_git(repository, "status", "--porcelain=v1", "-z").stdout:
        raise ConsolidationError("source worktree is not clean")


def validate_recovery_ref(repository: Path, recovery_ref: str) -> None:
    if not recovery_ref.startswith(RECOVERY_PREFIX):
        raise ConsolidationError(f"recovery ref must start with {RECOVERY_PREFIX}")
    run_git(repository, "check-ref-format", recovery_ref)
    if run_git(repository, "show-ref", "--verify", "--quiet", recovery_ref, check=False).returncode == 0:
        raise ConsolidationError(f"recovery ref already exists: {recovery_ref}")


def restore_source_checkout(
    repository: Path,
    branch_name: str,
    old_head: str,
    branch_updated: bool,
    expected_head: str,
) -> str | None:
    try:
        if git_output(repository, "rev-parse", "HEAD^{commit}") != expected_head:
            return "checkout recovery stopped: HEAD moved"
        expected_branch = expected_head if branch_updated else old_head
        if git_output(repository, "rev-parse", f"refs/heads/{branch_name}") != expected_branch:
            return "checkout recovery stopped: source branch moved"
        if run_git(repository, "diff", "--quiet", check=False).returncode != 0 or run_git(
            repository, "diff", "--cached", "--quiet", old_head, check=False
        ).returncode != 0:
            return "checkout recovery stopped: index or working files changed"
        if not branch_updated:
            run_git(repository, "reset", "--soft", old_head)
        run_git(repository, "checkout", "--quiet", branch_name)
        return None
    except ConsolidationError as error:
        return str(error)


def consolidate(
    repository: Path,
    target: str,
    message_file: Path,
    recovery_ref: str,
) -> dict[str, str]:
    repository = repository.resolve()
    message_file = message_file.resolve()
    message = message_file.read_text(encoding="utf-8")
    if not message.strip():
        raise ConsolidationError("Delivery Commit message is empty")

    branch_ref = git_output(repository, "symbolic-ref", "-q", "HEAD")
    if not branch_ref.startswith("refs/heads/"):
        raise ConsolidationError("source worktree HEAD is detached")
    branch_name = branch_ref.removeprefix("refs/heads/")
    require_clean(repository)

    old_head = git_output(repository, "rev-parse", "HEAD^{commit}")
    target_head = git_output(repository, "rev-parse", f"{target}^{{commit}}")
    if old_head == target_head:
        raise ConsolidationError("checkpoint HEAD equals the delivery target")
    if run_git(
        repository, "merge-base", "--is-ancestor", target_head, old_head, check=False
    ).returncode != 0:
        raise ConsolidationError("delivery target is not an ancestor of checkpoint HEAD")

    validate_recovery_ref(repository, recovery_ref)
    validate_recovery_ref(repository, f"{recovery_ref}-candidate")
    old_tree = git_output(repository, "rev-parse", f"{old_head}^{{tree}}")
    run_git(repository, "update-ref", recovery_ref, old_head, "0" * len(old_head))

    branch_updated = False
    candidate_ref: str | None = None
    expected_head = old_head
    try:
        run_git(repository, "checkout", "--quiet", "--detach", old_head)
        run_git(repository, "reset", "--soft", target_head)
        expected_head = target_head
        if run_git(repository, "diff", "--cached", "--quiet", check=False).returncode == 0:
            raise ConsolidationError("checkpoint tree has no delivery change from target")

        run_git(repository, "commit", "--file", str(message_file))
        delivery_commit = git_output(repository, "rev-parse", "HEAD^{commit}")
        expected_head = delivery_commit
        new_candidate_ref = f"{recovery_ref}-candidate"
        run_git(repository, "update-ref", new_candidate_ref, delivery_commit, "0" * len(delivery_commit))
        candidate_ref = new_candidate_ref
        delivery_tree = git_output(repository, "rev-parse", f"{delivery_commit}^{{tree}}")
        parents = git_output(repository, "show", "-s", "--format=%P", delivery_commit).split()
        if parents != [target_head]:
            raise ConsolidationError("Delivery Commit does not have the target as sole parent")
        if delivery_tree != old_tree:
            raise ConsolidationError("Delivery Commit tree differs from source HEAD")

        require_clean(repository)
        run_git(repository, "update-ref", branch_ref, delivery_commit, old_head)
        branch_updated = True
        run_git(repository, "checkout", "--quiet", branch_name)
        require_clean(repository)
        if git_output(repository, "rev-parse", "HEAD^{commit}") != delivery_commit:
            raise ConsolidationError("source branch does not point to Delivery Commit")
        run_git(repository, "update-ref", "-d", candidate_ref, delivery_commit)
        return {
            "branch": branch_name,
            "checkpoint_head": old_head,
            "target": target_head,
            "delivery_commit": delivery_commit,
            "tree": delivery_tree,
            "recovery_ref": recovery_ref,
        }
    except (ConsolidationError, OSError) as error:
        recovery_error = restore_source_checkout(
            repository, branch_name, old_head, branch_updated, expected_head
        )
        detail = str(error)
        if candidate_ref is not None:
            detail += f"; candidate retained at {candidate_ref}"
        if recovery_error is not None:
            detail += f"; automatic checkout recovery failed: {recovery_error}"
        raise ConsolidationError(detail) from error


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--target", required=True)
    parser.add_argument("--message-file", required=True, type=Path)
    parser.add_argument(
        "--recovery-ref",
        required=True,
        help=f"expected-absent recovery ref under {RECOVERY_PREFIX}",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        result = consolidate(
            args.repository,
            args.target,
            args.message_file,
            args.recovery_ref,
        )
    except (ConsolidationError, OSError) as error:
        print(json.dumps({"status": "error", "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps({"status": "ok", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
