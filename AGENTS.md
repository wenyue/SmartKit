# Project Agent Entry

## Project rules

Apply SmartKit plugin Rules for shared precedence. Keep project Rule policy in the files listed below.

### Required rules

Before starting a task, ensure the complete applicable content of every Rule below is available. Reuse content already in context while it remains current. Read missing content, including after compaction, and refresh affected content when there is evidence of a change.

- `.agents/rules/project-policy.md`
- `.agents/rules/self-hosting-authority.md`
- `.agents/rules/structure.md`

## Agent skills

### Issue tracker

Issues and specifications are tracked in this repository's GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the five default canonical triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

This repository uses a multi-context layout: `GLOSSARY-MAP.md` points to glossaries under `contexts/`, and shared architectural decisions live in `docs/adr/`. See `docs/agents/domain.md`.

<!-- OPENWIKI:START -->

## OpenWiki

This repository has a generated `openwiki/` evidence index. It is optional just-in-time context, not required startup reading.

- Do not enumerate, preload, or search wikis at task start. Use retrieval when the user asks for it, when unfamiliar architecture or dependency behavior materially affects the task, or when source inspection leaves an important uncertainty. Stop once the question is grounded.
- When those conditions apply and OpenWiki retrieval tools are available, use `openwiki_search` for just-in-time context and `openwiki_read` for the relevant complete sections. If search returns `workspace_required`, ask which listed workspace to use and retry with its ID.
- Use `openwiki_list_workspaces` or `openwiki_list_wikis` when workspace membership itself needs to be discovered.
- If the retrieval tools are unavailable, read `openwiki/quickstart.md` and follow its links to the relevant pages.
- Treat source code and tests as authoritative. A brief's unknowns and review items are verification gaps, not automatic requirements.
- Prefer the narrowest quiet validation that proves the changed behavior. Preserve complete failure output.

Use the repository's documented maintenance process to refresh generated pages after source changes. Check its configuration and completed runs before relying on automatic updates. Do not hand-edit generated OpenWiki pages unless explicitly asked; prefer updating source code/docs and letting OpenWiki regenerate.

<!-- OPENWIKI:END -->
