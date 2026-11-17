# Choose the maintenance mode

Ask when inspection reports `selection_required` and the user has not chosen a mode, or when the user requests a mode switch without naming the new mode. Present all three choices together. Map A to `local`, B to `local-only`, and C to `repository`. Missing maintenance information can also occur in an existing project. On a requested switch, explain its concrete effect on the established source and target. If the planned scope contains tracked paths, identify them and tell the user that B and C leave those files tracked.

Reserve the Git address for [Choose the configuration repository](choose-configuration-repository.md) after the user chooses C. A repository-mode result includes a scoped commit and normal push following local success unless the user requests a local result. The maintenance contract governs actual publication and existing tracked files.

## Prompt

> Where should `<project>` keep its configuration?
>
> - **A. With the project.** Keep the files here so you can version them with the project.
> - **B. On this machine only.** Keep the files here and exclude the configuration paths from this project's Git locally.
> - **C. In a separate private GitHub repository.** Keep a backup there and exclude the local configuration paths from this project's Git. After setup succeeds, I'll commit and push the agreed backup unless you ask to keep the result local.
>
> You can reply **A**, **B**, or **C**.
