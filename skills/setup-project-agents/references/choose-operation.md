# Choose the operation

Ask when the user has invoked Setup without choosing an operation. Start with one sentence about usable local configuration and any established backup. Offer the choices that fit the evidence.

| Finding | Choices to show | Recommendation |
| --- | --- | --- |
| Local configuration is usable, including in a fresh checkout | **A. Check this project's setup.** For an established source, offer **B. Restore from a configuration backup.** When there is only a proposed or unverified source, offer **B. Check whether my backup can be restored.** | A. Apply only required migrations, retain the maintenance choice, and complete the first OpenWiki if needed. |
| Local configuration is missing or unusable and a confirmed source has a backup for this project | **A. Restore the existing backup.** **B. Initialize this project.** | A. The user's configuration is available to reuse. |
| Local configuration is missing or unusable and the backup source is unknown or unconfirmed | **A. Initialize this project.** **B. Check whether my backup can be restored.** | A when the evidence supports initialization. B starts source confirmation and still needs an existing backup. |

Explain that full setup covers project configuration, local CodeGraph, and the first OpenWiki. For restoration, explain that the backup is applied to this project and can add, replace, or remove files after review. If available, show the affected paths from the local snapshot and identify them as local evidence. When inspection leaves an uncertain source, say what is unverified and defer source confirmation until the restoration route is selected. Recommend only a route the available evidence supports. An operation choice settles only the operation.

## Prompt for an unconfigured project with no known backup

> How would you like to set up `<project>`? <What the inspection found about this project's configuration and any backup>
>
> - **A. Initialize this project (recommended).** Set up its configuration, CodeGraph, and first OpenWiki.
> - **B. Use a backup you already have.** I'll ask where to find it, then show what restoring it would change.
>
> You can reply **A** or **B**.
