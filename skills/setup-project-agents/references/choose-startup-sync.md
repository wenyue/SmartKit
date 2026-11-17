# Choose startup synchronization

Ask only in repository mode when neither a clear answer for this checkout nor a recorded preference settles the choice, or when the user requests a change and its new value is unclear. A matching successful receipt records an on or off preference. Without one, inspection may report `automatic: false` as its default. The proposed default is off. Keep the prompt separate from the current application decision. Enabling startup synchronization may apply proven repository-only changes after a valid binding and matching successful local receipt exist. Local-only changes prompt for a save or deferral. Changes on both sides or an unknown direction require a choice. Acceptance of a later save covers its scoped commit and normal push under the maintenance contract.

## Prompt

> Should this checkout check the configuration repository at startup?
>
> - **A. Enable startup sync.** Apply changes automatically when only the backup changed. Ask before uploading local changes or resolving differences on both sides.
> - **B. Keep it off (default).** You can still restore or save configuration manually.
>
> You can reply **A** or **B**.
