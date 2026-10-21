# Project Context

Scaffold the per-repo configuration that the engineering skills assume:

- **Issue tracker**: where issues live (GitHub by default; local markdown is also supported out of the box)
- **Triage labels**: the strings used for the five canonical triage roles
- **Domain docs**: where `GLOSSARY.md` and ADRs live, and the consumer rules for reading them

This prompt-driven workflow is a supported shared resource for the explicit Setup Matt Pocock Skills entry and an accepted initialization or upgrade operation of the user-invoked full Setup Project Agents workflow. Full Setup may enter this reference automatically when required context is missing, complete it before freezing its session, and continue in the same conversation. Restoration, local synchronization, and Rule-index-only operations do not enter this workflow.

The caller supplies the target repository and retains its configuration ownership and application boundaries. Treat paths below as project-relative destinations; inspect the business target for evidence and read existing content at the caller's supplied authoritative authoring destinations before drafting. Under Setup Project Agents, prepare edits through its established maintenance mode and canonical-input route, then apply them through that owner's supported route. This reference neither expands backup selections nor invokes either manual entry. If the reference or a required seed template is unavailable, report the missing resource and leave the dependent operation incomplete.

Explore, preserve accepted choices and existing content, resolve missing decisions, show the proposed edits, then write. Reading this reference alone supplies no authority to change project configuration.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config`: is this a GitHub repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root: does either exist? Is there already an `## Agent skills` section in either?
- `GLOSSARY.md` and `GLOSSARY-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories
- `docs/agents/`: does this skill's prior output already exist?
- `.scratch/`: a sign that a local-markdown issue tracker convention is already in use
- Is the `triage` skill installed? (a `triage` Skill folder alongside the containing `setup-matt-pocock-skills` directory, or `triage` in your available skills.) This decides whether Section B applies.
- Monorepo signals: a `pnpm-workspace.yaml`, a `workspaces` field in `package.json`, or a populated `packages/*` with its own `src/`. These are present only in a genuinely large multi-package repo; their absence means single-context, which is almost every repo.

Full Setup Project Agents requires SmartKit's bundled sibling `triage` Skill. If it is unavailable, report the incomplete plugin distribution and leave full Setup incomplete; the independent Matt entry can still omit triage configuration when that Skill is not installed.

### 2. Present findings and ask

Summarise what's present and what's missing. Retain tracker, label, and domain-layout choices already established by project records or accepted in the conversation, unless the user requested a change. Supplement missing files or entry references without regenerating valid existing documents. Resolve conflicting records with the user before changing them.

Take only unresolved sections in order, one section and one answer at a time. A known choice needs no repeated selection question; a new draft still follows step 3.

Lead each section with the recommended answer so the user can accept it in a word. Give a one-line explainer only when the choice genuinely branches; skip the section entirely when exploration already settled it (Section B when `triage` isn't installed, Section C when there's no monorepo).

**Section A: Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-tickets`, `triage`, and `to-spec` read from and write to it. They need to know whether to call `gh issue create`, write a markdown file under `.scratch/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.

Default posture: these skills were designed for GitHub. If a `git remote` points at GitHub, propose that. If a `git remote` points at GitLab (`gitlab.com` or a self-hosted host), propose GitLab. Otherwise (or if the user prefers), offer:

- **GitHub**: issues live in the repo's GitHub Issues (uses the `gh` CLI)
- **GitLab**: issues live in the repo's GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Local markdown**: issues live as files under `.scratch/<feature>/` in this repo (good for solo projects or repos without a remote)
- **Other** (Jira, Linear, etc.): ask the user to describe the workflow in one paragraph; the skill will record it as freeform prose

Record the choice in `docs/agents/issue-tracker.md`. For a new GitHub or GitLab document, keep the template's "PRs as a request surface" flag **off** without raising another question; a user who wants external PRs in the triage queue can flip the flag in the file later. Preserve an established value in an existing document.

**Section B: Triage label vocabulary.** Skip this section entirely if the `triage` skill isn't installed (exploration told you), since an uninstalled skill needs no labels.

If it is installed and no label choice is established, ask exactly one question:

> Do you want to keep the default triage labels? (recommended: **yes**)

The defaults are the five canonical roles, each label string equal to its name: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On **yes**, write them as-is. Only if the user says no, usually because their tracker already uses other names (e.g. `bug:triage` for `needs-triage`), collect the overrides so `triage` applies existing labels instead of creating duplicates.

**Section C: Domain docs.** Preserve an established layout. Otherwise default to **single-context** (one `GLOSSARY.md` + `docs/adr/` at the repo root). This fits almost every repo; include it in the draft without a separate layout question.

When no layout is established, offer **multi-context** (a root `GLOSSARY-MAP.md` pointing to per-context `GLOSSARY.md` files) only when exploration found monorepo signals. Then confirm which layout they want.

### 3. Confirm and edit

Show the user a draft of the new or changed content in:

- The `## Agent skills` block to add to whichever of `CLAUDE.md` / `AGENTS.md` is being edited (see step 4 for selection rules)
- The contents of `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, and `docs/agents/triage-labels.md` (the last only when `triage` is installed)

Let them edit and accept the draft before writing. Reuse acceptance of the same exact draft already given in the conversation; changed proposals need acceptance of their changed content. Leave valid existing content unchanged.

### 4. Write

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create; don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa); always edit the one that's already there.

If an `## Agent skills` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```

Include the `### Triage labels` sub-block and supplement `docs/agents/triage-labels.md` when `triage` is installed, using its established label choice or the answer from Section B. When it is not installed, omit new triage content and preserve any existing project content.

Write only the accepted new or changed content. Use the seed templates in the parent Skill directory as starting points for missing docs, preserving project-specific content in existing files:

- [issue-tracker-github.md](../issue-tracker-github.md): GitHub issue tracker
- [issue-tracker-gitlab.md](../issue-tracker-gitlab.md): GitLab issue tracker
- [issue-tracker-local.md](../issue-tracker-local.md): local-markdown issue tracker
- [triage-labels.md](../triage-labels.md): label mapping (only if `triage` is installed)
- [domain.md](../domain.md): domain doc consumer rules + layout

For a missing "other" issue tracker document, write `docs/agents/issue-tracker.md` from the user's description; retain accepted project-specific instructions when supplementing an existing document.

### 5. Done

Read back the affected entry block and docs. Confirm that references resolve, each applicable configuration file contains the accepted decisions, and surrounding project content was preserved. A missing resource, unresolved choice, or failed write leaves this workflow incomplete; report the failure and retained state rather than claiming readiness.

Return the established choices, changed and preserved paths, and any unresolved prerequisite to the caller. Full Setup Project Agents rechecks Matt readiness before continuing its own preflight; completing this reference does not establish completion of full Setup. The independent Matt entry supplies its own final user-facing completion report.
