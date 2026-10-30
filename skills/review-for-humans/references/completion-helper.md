# Completion Helper

This guide owns CLI capabilities, inputs, evidence binding, and recovery mechanics. [Completion](completion.md) owns readiness, authorization, coverage, and conditional completion choices. The [Skill entry](../SKILL.md) owns ordinary conversation and review. Read the relevant owner before using the tool.

## Capabilities and prerequisites

The helper supports a verified github.com PR on its selected local branch: Viewed-only, or a new commit and normal push followed by Viewed. It can reuse committed outgoing content. Amendment/lease or force publication, mirrored push remotes, detached workspaces, unresolved Git operations, special index flags, and changed submodule/directory entries use Completion's manual workflow.

It requires Python 3.8+, Git, authenticated GitHub CLI (`gh`), PR/source access, prepared source objects, and readbacks. Viewer must match reviewed identity. It uses `gh api` against github.com, and does not install tools, fetch, synchronize, or select workspaces.

Resolve `<skill-root>` from the actual loaded Skill, independently of target working directory. Read the interface:

```text
python "<skill-root>/scripts/complete_review.py" --help
```

## Freeze the prepared action

Supply full commit IDs, exact local branch, complete eligible `viewed_paths`, and stable absolute evidence files outside the worktree supporting readiness, coverage, disclosed scope, and authorization. The helper hashes evidence bytes, not their meaning. A `plan_id` identifies effects; it grants no permission.

```json
{
  "repository": "/absolute/selected-worktree",
  "branch": "review-branch",
  "pull_request": "owner/repository",
  "number": 123,
  "base": "1111111111111111111111111111111111111111",
  "head": "2222222222222222222222222222222222222222",
  "viewer": "reviewer-login",
  "viewed_paths": ["src/feature.py"],
  "mode": "commit-push",
  "remote": "origin",
  "message": "Fix reviewed behavior",
  "requires_amend": false,
  "evidence": ["/absolute/private/review-and-checks.json"]
}
```

`pull_request` names the PR owner; source repository/ref come from GitHub, including forks. For `viewed-only` omit `remote`/`message`; local HEAD must match reviewed PR head and differences are frozen/preserved. Set `requires_amend` truthfully from recorded actions; preparation refuses it so manual amendment/lease stays in control.

Choose a new private state directory outside the worktree through the owning artifact lifecycle. Keep this sole recovery evidence available and unpublished. Creation uses owner-only POSIX permissions; on Windows use an account-private directory with suitable inherited access.

```text
python "<skill-root>/scripts/complete_review.py" prepare --input "/private/request.json" --state "/private/completion-state"
```

Preparation retains plan, original index bytes, tracked binary diffs, changed file bytes/symlink targets, intended complete tree, outgoing ancestry/delta, full PR pagination, and evidence digests. Publication preparation uses an isolated index/native clean filters and may add Git objects; it verifies real index/branch/HEAD/contents stayed unchanged. Inspect inventory/logs for scope disclosure; compact counts are insufficient.

## Execute or resume

After authorization for exact effects, reuse the returned `plan_id`:

```text
python "<skill-root>/scripts/complete_review.py" run --state "/private/completion-state" --confirm "<plan_id>"
```

The command locks/revalidates state, stages intended content when needed, runs normal hooks, and verifies tree/parent, outgoing ancestry, and source destination. It performs only normal scoped push when needed without automatic tag/submodule publication, verifies source-ref/PR version/published commit/tree, then marks remaining paths and reads back the full selected set and unchanged PR version. Existing effects are verified before reuse; no empty commit is created.

Stdout is compact JSON with status, version/counts, plan/progress paths, and private logs. Every Git/gh subprocess retains arguments, identity, stdout/stderr, exit status, and duration. Exit `0` means required readbacks completed; `1` incomplete, `2` usage error, `130` interrupted. Inspect failures/residue; the helper neither rolls back nor advances review progress.

After interruption/lost response run the same command with the same state/plan ID. It inspects effects and resumes missing work, including partial Viewed. Native locks release on process exit; after post-spawn failure the parent waits for its owned Git/gh child to stop before releasing the lock.

Changed content, branch, evidence, viewer, source, base/head, publication scope, or detected hook changes stop dependent effects. Preserve state, settle inventory/checks/re-review/consent through Completion and the Skill entry, then prepare a new plan only for settled changed effects. Failed preparation retains private diagnostics. Missing readbacks or uncertain subprocess state remain incomplete: do not delete locks, reset, repeat speculative writes, or substitute Continue.
