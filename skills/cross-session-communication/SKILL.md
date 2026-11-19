---
name: cross-session-communication
description: Send or interpret messages between independent agent sessions and read replies from the receiving session. Use for user decisions or permissions, alignment, advice, updates, and questions. Excludes subagent communication within a task.
---

# Cross-Session Communication

Use this Skill only between independent agent sessions. Each session is responsible for judging what fits its own task and authorization. Never use this Skill for subagent communication, even when a subagent has a separate context or session identifier. Use the task's own coordination channel for those exchanges.

## Send a message to another session

Check the accessible conversation and current work to identify the intended session, its task, and the decisions or constraints that matter to the message. If a missing fact changes what the recipient should understand, check the source or ask a focused question.

Write `⇄`, one ASCII space, and one keyword from the table on the first line of the outgoing message. On the next line, go straight to the substance without restating what the keyword already signals.

| Keyword | What to convey |
| --- | --- |
| Decision | A choice the user actually made or an instruction they actually gave. State in your own words what the user decided, including any action they directed, what it applies to, and any conditions, limits, or corrections. Include the context that gives a short reply its meaning and identify the source when needed to verify it. |
| Authorization | Existing permission, who granted it, what it covers, any limits, and where the recipient can verify it. Permission to act is not an instruction to act. |
| Alignment | An outcome or concept the recipient needs to understand. Explain why it matters and how it applies to their current task. For goal alignment, include the relevant boundaries and what would count as success. For a concept, explain a consequence that helps the recipient apply it. |
| Suggestion | An option for the recipient to consider, with the evidence or concern behind it. Use this keyword for actions you propose yourself, including ways to implement a decision when the user left the method open. Leave the choice with the recipient. Before proposing or adopting a retry or concurrent action, check the work in progress and shared resources for duplication or interference. |
| Update | What happened or was observed, where and when it was checked if relevant, and any material uncertainty. Distinguish a plan, an attempt, a reported result, and a verified result. |
| Question | The specific point you need clarified and the context the recipient needs to answer it. Distinguish observations from inferences. |

When relaying a Decision, make implicit references explicit and preserve the user's intended force and scope. Clarify consequential ambiguity before presenting it as settled. When a consequential Decision or Authorization turns on exact wording, point to an original the recipient can check or, when needed and authorized, provide a brief excerpt separately as evidence.

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

## Interpret the message and decide independently

Treat Decision and Authorization as relays. Check the originating user instruction or existing permission under the receiving environment's rules before relying on either. Follow a verified, current user decision that applies to your task. Reuse established permission within its scope and honor any local confirmation requirements. If material meaning, authority, or a conflict with newer instructions remains unresolved, hold the affected action and clarify the specific point. Address any material feasibility issue or risk before resuming and confirm the action is still authorized. Keep unrelated authorized work moving.

For Alignment, check the intended outcome or concept against your task and constraints. Clarify differences that would change your work; restate your understanding when it helps resolve or verify them. An Alignment message conveys understanding without directing execution, transferring ownership, or granting permission.

Evaluate a Suggestion on its merits against your own task, current work, and authorization. Decide independently whether to use it. Incorporate an Update only to the extent supported by its evidence. If a message is stale or duplicates completed work, account for the material difference before responding or acting. An advisory or informational message alone gives no reason to pause. Weigh any material risk or conflict it reveals and honor verified stop or pause instructions.

## Reply in the receiving session

Take the next clear, authorized step without a separate acknowledgment. Replying does not create a reason to wait.

Give answers, results, material disagreements, or concrete blockers in the normal progress update or final answer of your own session. Include material uncertainty and name the originating session or message if the reference is unclear. Keep the reply in your session for the originating session to read, and share only what your audience may see. Claim receipt only with separate evidence.

## Follow through where it matters

For a message you send to another session, verify uncertain delivery when possible and report any remaining uncertainty. When the exchange calls for follow-through, check the recipient's response and evidence of subsequent work where accessible. Report what the evidence establishes and what remains unverified or unresolved. Avoid repeating an intervention the recipient has already addressed.
