# Complete project context

Read this after Setup establishes the maintenance source and reports missing project context. Inspect the business target for project decisions and the authoritative authoring location for existing content. Both local modes author in the project. Repository mode authors in the selected source entry and applies accepted changes through the maintenance route. Resolve any backup-scope addition through [Confirm configuration changes](confirm-configuration-changes.md). Full setup requires the bundled `triage` Skill. Report a missing copy as an incomplete plugin distribution and leave dependent setup pending.

## Link existing project documents

Use this route when `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, and `docs/agents/domain.md` already exist as regular, non-symlink files, and their content is valid and consistent. Use the established project-root `CLAUDE.md` or `AGENTS.md` entry. Where only the existing file convention determines the path, prefer `CLAUDE.md` when present and then `AGENTS.md`. If neither exists, use the filename already established for this purpose by the user or project convention. The configured Rule-index destination does not decide this filename. If the context entry is still undecided or conflicts with the selected maintenance mode, ask about that choice before writing.

Once the entry and write authority are established, add the missing links so the first live `## Agent skills` section in that regular, non-symlink entry file contains all three exact paths above. Preserve all existing valid text and other sections. Verify that the links resolve. Report the resulting entry and links in the handoff. Use this route only when the work consists of adding links and can preserve custom text and project conventions.

> I found the existing project documentation. Where should its links go?
>
> - **A. `AGENTS.md`.** <Effect in this project>
> - **B. `CLAUDE.md`.** <Effect in this project>
>
> You can reply with the filename you prefer.

Use that format only when both named alternatives are available and the entry choice is genuinely unresolved. For a specific conflict, name the actual path, the conflict, and the supported way forward.

## Resolve or author project decisions

For missing or conflicting project decisions or substantive content changes, read and follow the complete shared reference at `<skill-root>/../setup-matt-pocock-skills/references/project-context.md`. Use the reference directly. Supply the authoritative paths and the required triage configuration. Reuse established decisions, ask about each unresolved decision in the reference's order, and obtain its required draft acceptance before writing. A missing resource or declined write leaves the prerequisite incomplete.

> The project already defines <established decisions>. I need your choice about <specific unresolved decision>.
>
> <Available choices and their immediate effect>
>
> Reply with the option you prefer.

When the shared workflow calls for draft acceptance, identify the exact path and proposed content and ask for acceptance or edits.
