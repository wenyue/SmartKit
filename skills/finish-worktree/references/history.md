# History Preparation

Before publication, local integration or requested consolidation, establish the accepted scope,
immutable base, complete task-owned commit range, source branch and HEAD/tree, and intended
destination. Required checks must pass and blocker-free formal review must cover that exact accepted
state. Missing evidence, unresolved blockers or task changes outside those commits go back to the
implementation workflow. This Skill consumes acceptance rather than conducting review. Unrelated
local state may remain when the selected operation cannot affect it and preservation can be verified.

## Keep the accepted history

Preserve commits by default. Once current HEAD/tree matches the accepted state and every commit in
the range belongs to the scope, publish or integrate that HEAD. Already published commits can be
used when compatible with the selected outcome. Finalization does not authorize synchronizing a
diverged branch or changing accepted content.

First check whether the authoritative target already contains every accepted effect. Ancestry can
prove delivery of the exact accepted range. Otherwise require unambiguous equivalent-change evidence
for the whole scope, with checks and acceptance bound to the exact target HEAD/tree; obtain this
from the implementation workflow. An empty diff, similar message, PR or tracker state alone is
insufficient. Proven delivery avoids an unnecessary rewrite, push or integration.

If the target or source moves, reassess the facts needed for the selected operation. Return changed
content or invalid acceptance to the implementation workflow; retain valid earlier results instead
of silently accepting a different result.

## Consolidate only when authorized

Consolidation needs an explicit user request or project requirement and commit authority. The range
must be wholly task-owned, unpublished and unrelied upon; the exact target must be its ancestor and
the source clean under `git status --porcelain=v1 -z`. Use normal repository commit hooks.

Record the original branch, HEAD/tree and exact target outside the source worktree. Create a unique,
expected-absent recovery ref pointing to the original HEAD with `git update-ref <backup-ref> <old-oid> ""`.
An empty expected old value requires the ref to be absent. Keep this ref until recovery no longer
needs the original history.

Build the candidate on detached HEAD so a failed hook leaves the original branch intact. Run each
command only after its predecessor succeeds, in the source worktree:

```text
git switch --detach <old-oid>
git reset --soft <exact-target-oid>
git commit --file <external-message-file>
```

Use an owned message file and ordinary commit hooks. If the staged diff is empty, stop rather than
creating an empty delivery commit. Verify the candidate has the target as its sole parent, the exact
accepted tree and a clean checkout. A hook changing contents requires renewed checks and acceptance;
retain its changes instead of resetting them away. Identical content allows reuse of content review,
but rerun checks that depend on commit identity or hooks.

Only after those checks, move the original branch using
`git update-ref <original-branch-ref> <candidate-oid> <old-oid>`, then switch back to it and verify
branch, HEAD/tree and clean state. A changed branch rejects the update instead of replacing someone
else's work. On any failure or interruption, inspect HEAD, branch, index and working files before
continuing; retain the candidate, backup ref and message for manual recovery. Do not reset or retry
blindly. Remove recovery items only under the entry's cleanup conditions.
