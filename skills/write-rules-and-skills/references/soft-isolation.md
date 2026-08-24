# Soft Isolation

This reference owns Soft-Isolation Probe qualification and Context Packet boundaries. Soft
isolation is a verified behavioral boundary, not a filesystem, process, or adversarial security
sandbox.

## Qualify the fresh-Agent launch

Run one disposable, tool-free Probe before the first Soft-isolated Agent in each top-level authoring
workflow. Do not reuse its result across parent runs or fresh-Agent launch mechanisms.

Before launch, place a random history control in parent-visible conversation without adding it to
the Probe prompt. Select exact questions whose answers exist only in each available source-project
Rule body, SmartKit global Rule body, Harness Rule body, and complete Skill body; keep their answers
out of the prompt. Also place a different random prompt control in the Probe prompt.

Start a fresh Agent with no inherited turns. Instruct it to use only initial context, call no tool,
read no file, perform no delegation, avoid inference, and return:

- the prompt control;
- the parent history control or `UNKNOWN`;
- each Rule- and Skill-body answer or `UNKNOWN`;
- whether entry-file content, Rule pointers, or Skill catalog metadata are visible; and
- whether it used a tool, file read, inference, or delegation.

`PASS` requires the exact prompt control, `UNKNOWN` for the history control and every available body
question, and no tool, file read, inference, or delegation. Entry-file content and its Rule or Skill
pointers, plus Skill catalog names, descriptions, or locations, may be visible; the Probe must not
follow those pointers or treat them as packet input. Any linked Rule body, complete Skill body,
unavailable fresh launch, malformed result, or other mismatch is `FAIL`. Stop and warn on `FAIL`;
never fall back to an ordinary Agent or a same-conversation prompt.

## Construct one Context Packet

A Context Packet contains the complete semantic input for one role:

- its single role, requested result, and output schema;
- accepted intent and the candidate content relevant to that role;
- selected evidence and the full text of every required Rule, Skill, or reference;
- explicit file contents and canonical target identities when the role authors content;
- allowed tools and paths only when the role's observable task requires them; and
- the applicable completion, stop, and failure outcomes.

Do not use workspace paths as substitutes for content. A tool-free Agent returns
`CONTEXT_REQUIRED` with the missing fact and its purpose when the packet is incomplete. The
controller may stop or start a new fresh Agent with a complete replacement packet; it does not add
material to the existing role conversation.

Keep packets and role results in active Agent context. Do not persist packet manifests, prompts,
attestations, ledgers, or verdict reports.

## Qualify exceptional tool access

An Acceptance Runner receives tools only when the candidate's observable contract cannot be tested
without them. Before that case, repeat the Probe with the same effective tool availability and a
task that requires only an explicitly supplied target. This tool-policy Probe may exercise only the
declared tools against that target; `PASS` requires it not to read or use undeclared context. A
failed or unverifiable tool-policy Probe stops the workflow.
