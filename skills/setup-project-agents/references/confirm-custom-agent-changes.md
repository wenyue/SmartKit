# Confirm changes to custom Agents

Ask when a change would cross a model tier, materially increase cost, alter an explicit project choice, or require the user to settle a native source conflict or relocation. Also ask when the user needs to select a replacement for a known unusable model. Explain the affected Agent and path. Show the current and proposed values or locations, the behavior that each option would preserve, and the cost or operational effect that needs a decision. Recommend an option when the verified evidence supports it. Keep conflicting inputs intact while the choice is pending.

## Prompt

> The `<agent>` Agent currently uses `<current setting or path>`. <Reason a decision is needed>
>
> - **A. <First supported choice>.** <Effect on this Agent>
> - **B. <Second supported choice>.** <Effect on this Agent>
>
> You can reply **A** or **B**.

Offer only supported options. If the current model is known to be unusable and there is no established replacement, say what selection is needed and leave the affected Agent pending.
