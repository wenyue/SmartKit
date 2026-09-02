---
name: create-worktree
description: Use when state-changing repository work requires an isolated linked Git worktree for parallel execution, workflow isolation, or protection of the current checkout.
---

# Create Worktree

Return one evidence-bound `ready` or `non-ready` handoff for an authorized isolated linked Git
worktree. Select the caller's fixed Create or Reuse mode, preserve the canonical checkout and all
unrelated state, establish the target, run only authorized target-owned preparation, and report the
terminal boundary.

The caller or owning workflow fixes the implementation scope, immutable base, mode-specific target
identity, lifecycle owners, and mutation grants. The Controller validates and executes that request
and owns the readiness judgment. Keep these owners distinct:

- `scope_owner`: owns the accepted implementation scope;
- `creation_owner`: the accountable actor authorized to invoke creation and own first-attempt
  recovery;
- `integration_owner`: owns later integration; and
- `cleanup_owner`: owns later cleanup.

Observing or recording an owner grants no mutation authority. This Skill owns no implementation,
commit, completed-change verification, integration, tracking, cleanup, publication, or other
downstream effect.

## Fix the request and preservation boundary

Before selection, require the owning workflow's authoritative:

- accepted scope and `scope_owner`;
- exact canonical base checkout, named base branch, and `immutable_base` commit OID and tree;
- Create or Reuse choice and its selecting owner;
- immutable requested worktree branch;
- for Create, a lowercase-hyphenated slug;
- for Reuse, the exact selected worktree and every caller-fixed value consumed by **Reuse
  identity** below;
- `creation_owner`, `integration_owner`, and `cleanup_owner`; and
- exact grants for every possible mutation.

Prove that the canonical checkout is attached to the named base branch at `immutable_base`. Resolve
and freeze `canonical_root` as that checkout's lexical and effective physical root and
`git_common_root` as its resolved Git common directory. After selecting the target, freeze
`selected_root` as distinct lexical-path and effective-physical-destination fields. For an absent
Create target, project the effective destination from the resolved nearest existing ancestor and
reprove it after creation. A current tip, convention, or discovered worktree never replaces a
requested value. The Controller may derive the Create branch once from a verified repository
convention, falling back to `worktree/<slug>`, only when the caller delegated that derivation;
freeze it before selection.

Use these named predicates throughout the run:

- **Create identity:** `selected_root`, registration, requested and observed named branch/ref
  relationship, `HEAD`, and current commit tree exactly match the request; the ref and `HEAD`
  resolve to `immutable_base`, and the tree equals its tree.
- **Reuse identity:** `selected_root`, registration, requested and observed named branch/ref
  relationship, `HEAD`, and current commit tree exactly match the caller-frozen
  `expected_current_head` and `expected_current_tree`; complete local state matches its per-item
  ownership and allowed scope; `creation_owner` lifecycle evidence and the required
  `immutable_base` lineage or range are proved.
- **Preservation census:** the target or partial artifact and its lexical/effective destination;
  the canonical checkout's branch, `HEAD`, commit tree, index, staged, unstaged, untracked,
  ignored, file-type, mode, and symlink state; the complete registered-worktree and local-branch
  sets; durable refs, configuration, hooks, and worktree administration under `git_common_root`;
  every declared effect target and observable actual filesystem, external, or persistent effect;
  and a mapping of every delta to one owner and exact grant.
- **Readiness snapshot:** the terminal mode-specific identity proof plus the complete target local
  state, bound to the terminal preservation census and its observation boundary.

Capture the initial preservation census before mutation. For Reuse, prove and snapshot its identity
before any target-owned command. Every pre-existing deviation must have one owner and belong to the
accepted scope; ambiguity is `non-ready`. Later censuses admit only separately authorized,
identified effects: the exact Create resources, an authorized guard repair, and declared setup or
baseline effects. Evidence records authority; it does not create it.

**Complete when:** every fixed value and owner is proved, every possible mutation has an exact
grant, and the initial census can distinguish allowed effects from user or unrelated state.

## Select and establish exactly one target

### Reuse

Reuse only the exact current linked worktree selected by the owning workflow for this scope. Prove
its identity; do not substitute, adopt, reset, clean, or repair another worktree.

If `selected_root` is inside `canonical_root`, freeze the exact overlapping subtree and its
pre-state so later comparisons can distinguish target-owned effects from surrounding canonical-
checkout state. Otherwise prove external Reuse explicitly.

After the applicable guard gate, reprove the Reuse identity and preservation census. Reuse permits
no new registration or branch. For contained Reuse, also reprove the frozen overlap and
canonical-root guard; for external Reuse, reprove no overlap and guard inapplicability. Any
mismatch, unexpected delta, or incomplete observation is `non-ready`.

**Reuse is established when:** its identity, preservation census, and applicable guard all pass.
Otherwise terminalize `non-ready`. An established Reuse proceeds directly to target preparation.

### Create

Map the slug to `<canonical_root>/.worktrees/<slug>` and freeze that lexical path as
`selected_root.lexical`. Resolve its nearest existing ancestor and prove that
`selected_root.effective` stays within the effective `canonical_root` without ambiguous traversal,
symlink, junction, or reparse escape. Require the path to be absent from the filesystem and
registered worktrees; prove the frozen requested branch syntactically valid and absent from local
branches and registered worktrees. Discover the host's current physical-path and filesystem/reparse
behavior at use; unavailable, ambiguous, or failed resolution is `non-ready` before mutation.

Before creation, require one exact grant naming the lexical and effective path, branch creation,
worktree registration, and corresponding administrative changes under `git_common_root`, bound to
the nominated `creation_owner`.

### Local guard

Require `canonical_root`'s effective, repository-relative `.worktrees/` ignore rule for Create and
for Reuse beneath that directory. Verify the selected path with
`git -C <canonical_root> check-ignore -v <selected-root-relative-path>`. A global or Git-info
exclude is insufficient. Repair only `<canonical_root>/.gitignore`, and only with separate
project-owned authority for the smallest distinguishable edit that preserves existing local state.
External Reuse records the guard as inapplicable and receives no repair authority.

### Create attempt

Creation is observation-gated, not serialized. Use no portable or global lock, lease, atomic guard,
or other coordination dependency. The host-native capability or Git fallback
`creation_mechanism` must reject creation-time path, branch, and registration conflicts. A race may
produce a failed attempt or a successful-looking creation whose later census is `non-ready`; it
must never produce `ready` on relevant drift.

Discover the native capability and Git fallback at use, recording unavailable or failed paths. For
each attempt, use the native capability when available, otherwise the Git fallback. Immediately
before invocation, re-observe and pass the fixed request and owners, immutable base, canonical-
checkout preservation, destination containment and path absence, branch validity and absence,
registration absence, exact grants, `creation_owner` authority, frozen mechanism availability, and
guard proof. Stop before invocation on drift or incomplete evidence. The fallback uses:

```text
git -C <canonical_root> worktree add -b <requested-branch> <selected_root.lexical> <immutable_base_oid>
```

The nominated `creation_owner` is accountable for each invocation and stays within its exact grant;
the mechanism is not an owner. One invocation is one attempt. Immediately after every attempt,
including failure or interruption, capture the complete preservation census and observe every
Create identity field. Classify an unsuccessful invocation against the narrow recovery gate below
before requiring complete Create identity; only its unchanged-state or exact attempt-owned partial-
effect cases are exempt from terminal identity failure. Any relevant drift; creation-time path,
branch, or registration conflict; unexpected or out-of-scope effect; incomplete evidence; or any
identity or invariant failure outside that exception ends Create and the whole handoff `non-ready`.
None permits retry or later readiness, even if the condition later disappears.

Only when none of those terminal conditions occurred may the first unsuccessful invocation be
retry-eligible. Its census must prove either unchanged state after a clean creator failure or
solely an exact attempt-owned partial effect containing no user work. Remove such a partial effect
only under a separate exact cleanup grant bound to `creation_owner`. Re-observe cleanup or proved
absence, repeat every Create gate, and retry at most once. Otherwise retain the artifact and stop.
Retain every second-failure artifact. Any ambiguous, user-owned, unexplained, or incompletely
observed effect is retained and ends Create.

For a successful-looking attempt, reprove the Create identity and preservation census. Create
permits only its exact granted delta.

**Create is established when:** its identity, immediate and post-attempt preservation censuses,
and every creation or guard effect pass. Otherwise terminalize `non-ready`.

## Prepare the target within declared effect envelopes

Target-owned `worktree-environment-setup` and the repository-declared baseline are dependencies;
their declarations own commands and meaning, while the caller or owning workflow owns permission
for their effects.

Before executing either dependency, inspect its current declaration and freeze its command and
effect envelope, including every filesystem target, durable Git common-state change, and external
or persistent effect. Freeze its invocation binding as either a working directory of exactly
`selected_root.effective` or an explicit repository-target argument resolving there. Immediately
before every invocation, verify that binding. An unavailable, ambiguous, or mismatched binding,
including `canonical_root` or another root, is `non-ready` before execution. Prove the dependency
non-mutating or require explicit authority for every declared class and exact target. Bind the
granting owner and allowed local-state addition to this selected worktree. Missing, ambiguous,
unowned, or unauthorized envelopes are `non-ready` before execution. Re-read environment-owned
declarations at use; do not cache them here.

Run setup first when present. Proven absence is ready-compatible. A failed, stopped, interrupted,
unexpected, or non-ready setup ends preparation before the baseline.

Run the declared baseline only after setup is ready or absent. Record its exact commands and
result. A pass is ready-compatible. A failure is ready-compatible only when the user explicitly
accepts that exact observed failure; proven absence requires explicit acceptance from the user or
owning workflow. Acceptance grants no mutation authority. Do not invent a baseline or substitute
completed-change verification.

After every setup or baseline disposition—including success, failure, interruption, or a
conclusively absent, unavailable, missing, moved, or unreadable target—capture the preservation
census and compare it with the dependency's immediately preceding mode-specific identity and
preservation census and its frozen envelope. Preserve partial evidence. Any unavailable,
unauthorized, unexplained, out-of-envelope, or incompletely observed state is `non-ready`.

**Complete when:** setup and baseline have exact terminal dispositions and the census proves every
declared or actual effect completely observed, envelope-matched, owned, and authorized.

## Terminalize and hand off

Before every exit, capture the preservation census and report incomplete observations rather than
inferring state. For Create, allow only the verified selected subtree and exact granted resource
deltas. For contained Reuse, hold the frozen overlapping-subtree boundary constant. Use the
preservation census to compare its contents and deltas with the frozen pre-state, ownership, exact
grants, and explicit envelopes; admit only matching effects and preserve everything outside it.
External Reuse has no overlap exception. An early exit still closes every observable comparison.

Return `ready` only when all of these are proved:

- the fixed request and lifecycle owners match exactly;
- every initial, immediate pre-attempt, post-attempt, preparation, and terminal preservation census
  passes; no terminal race occurred; and any first-attempt recovery passed its narrow gate and was
  re-observed;
- the applicable ignore guard passes or external Reuse is proved inapplicable;
- the mode-specific identity passes after all preparation, with authorized preparation state only
  inside the preservation and effect envelopes;
- setup is absent or returned ready;
- the baseline passed or its exact failure or absence has the required explicit acceptance; and
- every final deviation is within the accepted scope and an authorized allowed-state envelope.

Every other exit is `non-ready`. Except for the single authorized first-attempt recovery, retain the
worktree and residual state.

Return a compact mechanical handoff containing:

- status and exact reason; accepted scope and `scope_owner`;
- mode, the three roots, `immutable_base`, and the complete readiness snapshot;
- the initial and final preservation censuses and every boundary comparison; for every Create
  attempt, its immediate gates, owner, mechanism, result, census, authorized deltas, cleanup
  evidence, and retry disposition;
- all lifecycle owners; the selecting owner for mode; the derivation source and delegating owner
  for branch derivation, if any; and the source and granting owner for Create effects and guard
  repair;
- guard applicability, proof, repair, and actual effect;
- setup and baseline declarations, commands, bindings, envelopes, authorities, results,
  acceptance, actual effects, and effect-comparison verdicts;
- every terminal census, its completeness, retained evidence, ownership map, and envelope
  comparison; and
- for `non-ready`, the exact failed boundary and observation, retained or residual state, next
  owner, and one exact next action.

Use exact observations. Use `not-selected`, `not-created`, or `not-run` only before that boundary;
`unavailable` only for genuinely unobservable values; and `unverified` only while an attempted gate
remains incomplete. A conclusively inapplicable or absent step records its exact reason and effects.
A `ready` handoff has no marker in a mandatory field.

A consumer may admit the target only by rechecking the exact mode-specific readiness snapshot
immediately before its first consume or mutation; any mismatch or `non-ready` blocks consumption.
Later authorized target commits or local changes invalidate that snapshot without retroactively
changing this run's result. Continuation or recovery requires a fresh Reuse handoff against a
caller-frozen current snapshot. Any downstream finalizer independently applies its owner contract
to the then-current target identity, required review and verification, and immutable-base lineage.
No handoff content grants new authority.
