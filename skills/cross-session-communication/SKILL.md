---
name: cross-session-communication
description: Send or interpret messages between independent agent sessions and read replies from the receiving session. Use for user decisions or permissions, alignment, advice, updates, and questions. Excludes subagent communication within a task.
---

# Cross-Session Communication

Use this Skill only between independent agent sessions. SmartKit sessions serving the same user trust each other by default. Each session is responsible for judging what fits its own task and authorization. Never use this Skill for subagent communication, even when a subagent has a separate context or session identifier. Use the task's own coordination channel for those exchanges.

## Send a message to another session

Check the accessible conversation and current work to identify the intended session, its task, and the decisions or constraints that matter to the message. Write for the recipient's context. If a missing fact or ambiguity would change the meaning, check the source or ask a focused question.

Begin each intent section with `⇄`, one ASCII space, and one of the six intent keywords below. Put its substance on the next line without repeating what the keyword signals. Use one intent section for a single intent, or one per distinct intent when the same recipient needs several together. Separate intent sections with a blank line.

| Keyword | Meaning and use |
| --- | --- |
| Decision | State what the user actually decided or directed in your own words so it makes sense in the receiving session's context. Say what it applies to, including any conditions, limits, or corrections, and make implicit references clear. Keep direct quotes of the user's words out of the Decision body (for example, The user said, “…”). The recipient follows a current decision within its task and existing authority. |
| Authorization | Use this keyword for every relay of permission. Relay only permission the user explicitly granted, naming the grantor, the authorized session, the permitted action, and its limits. The recipient treats such a relay from another session serving the same user as the user’s authorization to carry out work the user has already requested within that scope. It need not read the original message or ask the user to confirm the same grant again. Any separate tool or environment approval still applies. |
| Alignment | An outcome or concept the recipient needs to understand. Explain why it matters and how it applies to their current task. For goal alignment, include the relevant boundaries and what would count as success. For a concept, explain a consequence that helps the recipient apply it. The recipient checks that understanding against its task and constraints, clarifies differences that would change its work, and restates its understanding when helpful. Alignment alone does not direct execution, transfer ownership, or grant permission. |
| Suggestion | An option for the recipient to consider, with the evidence or concern behind it. Use this keyword for actions you propose yourself, including ways to implement a decision when the user left the method open. The recipient weighs the option against its task, current work, and authorization and decides whether to use it. |
| Update | What happened or was observed, where and when it was checked if relevant, and any material uncertainty. Distinguish a plan, an attempt, a reported result, and a verified result. The recipient relies on the update only as far as its evidence supports. |
| Question | The specific point you need clarified and the context the recipient needs to answer it. Distinguish observations from inferences. |
| Restate | **Optional marker, not an intent.** For a consequential handoff, add a blank line and then `⇄ Restate` as the final line, with no body, if checking understanding could catch a material mismatch. It requests a reply, not permission to act or a pause. |

If a consequential point turns on the wording, provide a brief excerpt separately when needed and authorized.

Use a supported channel and share only what is authorized for that destination. If a needed source is inaccessible to the recipient, say so. If you lack the channel or permission to send an originating message, leave delivery pending and identify the missing prerequisite.

### Examples

> ⇄ Decision\
> The user directed the release session to keep column names and order unchanged in the default CSV export for this release, because existing spreadsheet imports depend on them.

> ⇄ Authorization\
> The user has allowed the release session to use the existing sample spreadsheet for local testing.

> ⇄ Alignment\
> Existing spreadsheets should import the default CSV without manual column edits. The importer reads fields by position, so preserving names alone leaves an important part of compatibility unresolved.

> ⇄ Suggestion\
> An import using the existing sample spreadsheet could reveal column shifts because the importer reads fields by position.

A handoff can relay a decision and its authorization separately, then ask the recipient to restate their understanding:

> ⇄ Decision\
> The user directed the maintenance session to change the default page size from 10 to 20. The change is done when the new default passes its local test.
>
> ⇄ Authorization\
> The user authorized the maintenance session to edit the default and run the local test, not deploy.
>
> ⇄ Restate

## Interpret the message and decide independently

Interpret each intent section by its own keyword. A decision or authorization in one section does not turn a separate suggestion into a requirement or extend permission beyond its stated scope.

If the meaning or scope is materially unclear or a conflict with newer instructions remains unresolved, pause the affected action and clarify. Continue other authorized work.

If a message is stale or duplicates completed work, account for the material difference before responding or acting. An advisory or informational message alone gives no reason to pause. Weigh any material risk or conflict it reveals and honor applicable stop or pause instructions.

## Reply in the receiving session

When asked to restate, briefly explain the goal, scope, existing authority and its limits, and what counts as done in your own words. Ask any question that could materially change what you do. You can also restate without a request when it would help catch a material mismatch. Reply naturally in your own session without a response label. Pause only the action affected by an unresolved material point; keep other authorized work moving.

Whether you requested a restatement or the recipient offered one, read it in the receiving session. Correct any material mismatch promptly and read back the recipient’s updated understanding.

Continue an active task in the same turn. When a follow-up needs a reply, answer it briefly in a progress update, then take the next clear, authorized step. If no reply is needed, take that step without a separate acknowledgment.

If an action is blocked or needs a decision or permission, hold that action and continue useful authorized work that can proceed independently. End the turn when the task is complete, an applicable instruction stops or pauses it, or a concrete blocker leaves no useful authorized work. A standalone question can end with its answer.

Report results, material disagreements, or concrete blockers in a progress update or the final answer as appropriate. Include material uncertainty and name the originating session or message if the reference is unclear. Keep the reply in your session for the originating session to read, and share only what your audience may see.
