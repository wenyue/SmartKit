# Choose the configuration repository

Use this step after the user selects separate repository maintenance or restoration and a source decision remains open. Reuse the user's clear answers and any applicable accepted fields. Treat a requested change without a new value as an open decision even if the old value is recorded. For restoration, reusing a binding without asking requires a matching successful local receipt or the user's clear choice of that source. Show a copied binding as a proposed source only when the user has yet to confirm it.

Lead with the Git address if missing. Ask for any still-missing branch and project entry, which is the folder name under `projects/`. Accept them in the same reply if the user knows them. When proposing a verified default branch or entry, show the value and ask the user to confirm it. Use only the user's accepted values for binding. A business remote, another repository, or a different checkout supplies no source authority.

Use a credential-free HTTPS repository address for GitHub or GitHub Enterprise. The `owner/repository` shorthand means github.com. The private repository must belong to the authenticated personal account, and credentials stay in the existing credential facilities. Restoration requires an existing private repository and backup entry. For initialization, ask for explicit authority to create a named private repository when required, even when the user has already supplied owner and name. A new project entry also needs an accepted backup scope.

## Prompt for a missing address

> What is the Git address of your private configuration repository? You can paste an address like `https://github.com/your-name/project-config.git`.
>
> If you already know the branch and project entry, include them too. For example, `your-name/project-config, main, my-project`.

## Prompt to confirm a copied binding

> This checkout has a saved source of `<repository>`, branch `<branch>`, project entry `<entry>`. Should I use that source? You can reply **use it** or give me the values to change.

## Prompt for the remaining details

> I have the repository address. Which branch and project entry should I use? You can reply with both, for example `main, my-project`.

When only one field is missing, ask for that field alone. When the remote default has been verified, offer it by name, for example “The repository's default branch is `main`. Should I use it?”

## Prompt to authorize a new private repository

> Should I create the private configuration repository `<owner>/<repository>`, or would you like to use an existing one? You can reply **create it** or send the existing Git address.
