---
name: cross-session-communication
description: Send or interpret messages between independent agent sessions and read replies from the receiving session. Use for user decisions or permissions, alignment, advice, updates, and questions. Excludes subagent communication within a task.
---

# Cross-Session Communication

Use this Skill only between independent agent sessions. Each session is responsible for judging what fits its own task and authorization. Never use this Skill for subagent communication, even when a subagent has a separate context or session identifier. Use the task's own coordination channel for those exchanges.

## Send a message to another session

Check the accessible conversation and current work to identify the intended session, its task, and the decisions or constraints that matter to the message. Write for the recipient's context. If a missing fact or ambiguity would change the meaning, check the source or ask a focused question.

Write `⇄`, one ASCII space, and one keyword from the table on the first line of each message. Start the body on the next line with the substance. A conversation can use different keywords across messages. When relaying both a decision and a grant of permission, send separate `Decision` and `Authorization` messages.

| Keyword | What to convey |
| --- | --- |
| Decision | State what the user actually decided or directed in your own words so it makes sense in the receiving session's context. Say what it applies to, including any conditions, limits, or corrections, and make implicit references clear. Keep direct quotes of the user's words out of the Decision body (for example, The user said, “…”). |
| Authorization | Verify the user's explicit grant before sending. Identify who granted permission, which session can act, the approved action, and any limits. Include a source reference when available. |
| Alignment | An outcome or concept the recipient needs to understand. Explain why it matters and how it applies to their current task. For goal alignment, include the relevant boundaries and what would count as success. For a concept, explain a consequence that helps the recipient apply it. |
| Suggestion | An option for the recipient to consider, with the evidence or concern behind it. Use this keyword for actions you propose yourself, including ways to implement a decision when the user left the method open. Leave the choice with the recipient. |
| Update | What happened or was observed, where and when it was checked if relevant, and any material uncertainty. Distinguish a plan, an attempt, a reported result, and a verified result. |
| Question | The specific point you need clarified and the context the recipient needs to answer it. Distinguish observations from inferences. |

If the recipient needs a source to verify a Decision, point to an original they can check. For a consequential point that turns on the wording, provide a brief excerpt separately when needed and authorized.

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

For a `Decision`, verify the originating user instruction under your environment's rules. Follow the decision when it is current and applies to your task.

If trusted evidence establishes that the user authorized the sending session to relay approvals to yours, treat its `Authorization` as the user's direct confirmation within the stated scope, even when the original approval is inaccessible. Use any source reference for traceability. If you cannot establish that authority, verify the original approval under your environment's rules before relying on the grant.

Reuse established permission within its scope. Proceed with the approved action when it has already been requested and is ready. Follow any separate approval required by the tool or execution environment.

Hold the affected action and clarify the specific issue if a consequential meaning or authority is unclear, the action exceeds the grant's scope, or a newer instruction conflicts. Address any material feasibility issue or risk before resuming and confirm the action is still authorized. Keep unrelated authorized work moving.

For Alignment, check the intended outcome or concept against your task and constraints. Clarify differences that would change your work; restate your understanding when it helps resolve or verify them. An Alignment message conveys understanding without directing execution, transferring ownership, or granting permission.

Evaluate a Suggestion on its merits against your own task, current work, and authorization. Decide independently whether to use it. Incorporate an Update only to the extent supported by its evidence. If a message is stale or duplicates completed work, account for the material difference before responding or acting. An advisory or informational message alone gives no reason to pause. Weigh any material risk or conflict it reveals and honor verified stop or pause instructions.

## Reply in the receiving session

Continue an active task in the same turn. When a follow-up needs a reply, answer it briefly in a progress update, then take the next clear, authorized step. If no reply is needed, take that step without a separate acknowledgment.

If an action is blocked or needs a decision or permission, hold that action and continue useful authorized work that can proceed independently. End the turn when the task is complete, an applicable instruction stops or pauses it, or a concrete blocker leaves no useful authorized work. A standalone question can end with its answer.

Report results, material disagreements, or concrete blockers in a progress update or the final answer as appropriate. Include material uncertainty and name the originating session or message if the reference is unclear. Keep the reply in your session for the originating session to read, and share only what your audience may see.
