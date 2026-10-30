# Completion Helper

Use this helper after the Skill's preparation has established a ready, reviewable completion. It supports a verified github.com PR in its selected local branch: Viewed recording alone, or a new commit and normal push followed by Viewed. It can reuse already committed outgoing content. Amendment, force/lease publication, mirrored push remotes, detached workspaces, unresolved Git operations, special index flags, and changed submodule/directory entries use the Skill's existing manual workflow.

## Keep judgment and permission with the Agent

The helper checks frozen identities, content, ancestry, and readbacks. Before execution, the Agent must establish successful required checks for the whole commit/publication, resolve findings and re-reviews, verify whole-file coverage for every selected Viewed path, disclose all outstanding paths and outgoing commits, and obtain the selected action's authorization. Account for mixed provenance and partially staged content under the Skill. A `plan_id` identifies prepared effects; passing it to a command does not grant permission.

Retain evidence of those decisions in stable readable files outside the worktree. The helper hashes their bytes and stops if they change or disappear. These references are evidence bindings, not a substitute for assessing their meaning or rerunning invalidated checks. For Viewed-only completion, establish that preserved local differences do not invalidate the fixed review or its dependencies.

## Prepare a frozen plan

Requirements are Python 3.8+, Git, authenticated GitHub CLI (`gh`), access to the PR and source branch, and the existing prepared worktree. The current GitHub viewer must match the reviewed viewer. The helper uses `gh api` against github.com; unavailable authentication, tools, permissions, source objects, or readbacks leave completion incomplete. It does not install tools, fetch, synchronize, or choose another workspace.

Resolve `<skill-root>` to this actual loaded Skill directory, independently of the target working directory. Read its interface first:

```text
python "<skill-root>/scripts/complete_review.py" --help
```

Write a JSON request using full commit IDs and the exact selected local branch. `pull_request` names the PR-owning repository; the helper obtains the source repository and ref from GitHub, including forks. `viewed_paths` contains the complete selected eligible set, including earlier displayed groups when finishing. `evidence` names the stable files supporting readiness, full-file coverage, disclosed scope, and authorization.

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

Use `mode` `viewed-only` and omit `remote` and `message` when publication is unnecessary. That mode requires local HEAD at the pinned PR head and preserves the frozen index and worktree differences. Set `requires_amend` when recorded review actions require amendment; preparation refuses it so the existing amendment/lease workflow remains in control. A false or omitted value must reflect the actual recorded actions.

Choose a new private state directory outside the worktree, using the owning artifact lifecycle. The directory holds the sole recovery evidence until completion and must remain available; keep it private and do not publish it. The helper creates it with owner-only POSIX permissions; on Windows retain it under an account-private directory with appropriate inherited access controls.

```text
python "<skill-root>/scripts/complete_review.py" prepare --input "/private/request.json" --state "/private/completion-state"
```

Preparation saves `plan.json`, original index bytes, tracked binary diffs, changed working-file bytes or symlink targets, the intended complete tree, outgoing ancestry and delta, full GitHub file pagination, and evidence digests. For publication it stages into an isolated index, runs native Git clean filters, and may add Git objects; it preserves the real index, branch, HEAD, and working contents, then verifies they stayed unchanged. Inspect the saved inventory and logs when disclosing scope; the compact stdout counts do not replace that disclosure.

Review the plan's exact paths, full outgoing commit list and delta, final content, PR source/viewer/version, and selected Viewed set against the prepared action. Obtain or reuse authorization only for those same effects. Preparation cannot establish review quality, provenance consent, dependency validity, or authorization by itself.

## Execute and resume the selected action

Once the action is authorized, pass the returned `plan_id` unchanged:

```text
python "<skill-root>/scripts/complete_review.py" run --state "/private/completion-state" --confirm "<plan_id>"
```

The command locks this operation, revalidates the prepared state, stages the full disclosed final content when needed, and runs normal commit hooks. It verifies the intended tree and parent, outgoing ancestry and source ref at the verified push destination, performs only a normal scoped push when needed without automatic tag or submodule publication, and reads back the source ref, PR version and published commit/tree. It then marks only selected paths still awaiting Viewed and reads back every selected path and the unchanged PR version. Existing commits, published heads, and Viewed results are verified before reuse. No empty commit is created.

Stdout is one compact JSON summary with status, version/counts, plan/progress locations, and the full log directory. Every Git/gh command retains stdout, stderr, arguments, process identity, exit status and duration in private logs; failures are not hidden by the summary. The helper preserves partial effects, does not roll back, and does not advance review progress. Exit `0` means the requested readbacks completed; `1` means incomplete, `2` is CLI usage error, and `130` is interrupted. Inspect the result and account for residual effects before reporting completion.

After interruption or a lost response, rerun the same `run` command with the same state and plan ID. It first inspects actual local and remote state: an expected commit needs its checked tree and parent, a push needs source-ref and PR readbacks, and Viewed needs current per-path state. It resumes only missing effects, including after partial Viewed recording. Its native lock releases when the process exits; after any failure occurring once a subprocess starts, it waits for the owned Git/gh child to stop before releasing that lock.

Changed content, branch, evidence, viewer, source, base/head, or publication scope—including detected hook-caused changes—stops the dependent action. Preserve the operation and its evidence, refresh the affected inventory/checks/re-review and any necessary consent, then use a newly prepared plan only when those changed effects are settled. A preparation that created private state retains that diagnostic directory after failure; inspect it before choosing a new state directory. Missing readbacks or uncertain live subprocess state remain incomplete; do not delete locks, reset the worktree, repeat writes speculatively, or substitute ordinary continue.
