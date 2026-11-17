# Confirm the OpenWiki backup

Use this step when repository-mode OpenWiki needs a backup file selection that has yet to be accepted. Explain that the backup plan already covers the complete `openwiki/` tree and any `.openwikiignore`. For each proposed changed `AGENTS.md` or existing `CLAUDE.md` at the Git root, show the exact path and review the complete file before asking to include it. The accepted selection covers complete file contents. Use the maintenance contract for permission, plan verification and publication.

## Prompt

> The OpenWiki backup will include `openwiki/` and the project’s Wiki ignore file if present. Should it also include the full `<Git-root entry file>`?
>
> - **A. Include it.** Future restores of this backup can apply the entire file.
> - **B. Keep the Wiki backup scope.** Leave this additional file out.
>
> You can reply **A** or **B**.

If there are multiple eligible additions, list the exact paths and accept a clear selection. Retain the accepted file scope and exact plan for the guarded save.
