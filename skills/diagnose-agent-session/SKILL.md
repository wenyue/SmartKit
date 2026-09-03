---
name: diagnose-agent-session
description: Diagnose suspected abnormal token or API-equivalent cost consumption, model or tool activity, subagent coordination, waits, or incomplete calls in one current or completed agent session.
---

# Diagnose Agent Session

Diagnose one identified agent session at `turn`, `session`, or `both` scope. The owned wrapper
collects facts; the Agent supplies task context and the conclusion.

## Fix identity and scope

Resolve one client/session pair. Supported client identifiers are `codex`, `cursor`, and `copilot`,
where `copilot` means GitHub Copilot CLI. Session IDs contain only letters, digits, dot, underscore,
colon, and hyphen. `CODEX_THREAD_ID` supplies the current Codex identity only when both explicit
arguments are absent. Never infer identity from recency; never select the newest log.

`turn` means the final recorded turn in the immutable Codex snapshot: from its latest user-message
boundary through its last event. For a live session this is the invoking turn; for a completed
session it is that session's final recorded turn. This interface does not select another historical
turn. Stop before acquisition if the user requests one.

Use `both` unless the user explicitly requests `turn` or `session`. Stop before acquisition when
the pair is partial or missing, the client or ID is unsupported, or the platform has no supported
launcher. Report the exact prerequisite without substituting another session or scope.

Codex supports all three scopes. Cursor and GitHub Copilot CLI support whole-session Tokscale
evidence only: stop before acquisition for a `turn`-only request. For `both`, acquire the requested
whole-session evidence and report the turn scope as unsupported; do not present session evidence as
turn evidence.

## Authorize the evidence sources

The Codex profile reads the exact local session log. It holds the content only for this attempt and
reports no prompt, response, transcript, tool input, tool output, or credential content.

Whole-session usage and model evidence comes from the installed Tokscale provider. Before each
attempt that requests `session` evidence, confirm authorization for Tokscale to:

- scan the selected client's session records in the requested date window—or its available local
  history when no reliable bounds exist—to select the exact session, and read existing Tokscale
  identity state;
- access the pricing or provider endpoints used by that installed build; and
- read or write only the Tokscale-owned config and cache directories that build resolves on the
  current host.

The wrapper runs no login, sync, credential change, installation, telemetry configuration, or
remediation command. If required authentication or prior telemetry is absent, report that
prerequisite. Obtain separate authorization before the affected rerun; do not treat an earlier
diagnosis grant as continuing authority.

## Acquire the requested evidence

Resolve the directory containing this installed `SKILL.md` as `skill_root`. Choose 32 fresh random
bytes and encode them as exactly 64 lowercase hexadecimal characters for this attempt's acquisition
ID, then execute the owned wrapper once. The Codex profile checks tool-call records only for that
exact ID. Exactly one match excludes that call alone. Zero matches exclude nothing and report that
the current acquisition call was not observed. Multiple matches exclude nothing and report failed,
ambiguous self-call attribution. Historical acquisition IDs and unrelated or completed diagnosis
calls remain evidence.

Linux with `sh`:

```sh
skill_root='<absolute directory containing the installed SKILL.md>'
sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both --client <client> --session-id <id> --acquisition-id <64-lowercase-hex>
```

Windows with PowerShell:

```powershell
$skillRoot = '<absolute directory containing the installed SKILL.md>'
$wrapper = Join-Path $skillRoot 'scripts\task-metrics.ps1'
powershell -ExecutionPolicy Bypass -File $wrapper diagnose --scope both --client <client> --session-id <id> --acquisition-id <64-lowercase-hex>
```

Replace `both` only for an explicitly selected scope. The launchers resolve Python 3.10 or newer;
preserve their error when none is available. Preserve partial evidence from a failed or unavailable
surface instead of trying another telemetry command.

The Codex profile copies the exact local log before recording that source's cutoff and evaluates
only the immutable copy. The report states the selected session and turn start and end boundaries.
For `session` evidence, the wrapper separately records the resolved
Tokscale executable path and version, provider start and end, supported effect contract, and
validated JSON schema. It accepts client/session/model grouped rows for the exact pair; only Codex
also accepts the single `rollout-{session-id}` alias. Exact and aliased Codex rows together are an
ambiguous failure. Schema incompatibility is a failed provider, not a version guess. Provider
stdout and stderr remain withheld. The two source intervals are independent and do not form an
atomic snapshot.

Tokscale supplies whole-session usage and model activity. Cursor may require an existing valid
Tokscale Cursor identity and a previously completed, separately authorized sync. GitHub Copilot CLI
may require OTEL file export configured before the activity; absent past telemetry cannot be
reconstructed. The Codex local profile additionally supplies current-turn, tool, subagent, and wait
evidence. Cursor and Copilot have no such behavior integration in this wrapper.

## Interpret coverage before values

Preserve each requested capability's wrapper state:

- `available`: the named source and schema contain usable evidence;
- `unavailable`: no supported source or compatible evidence exists for this attempt;
- `failed`: an authorized acquisition or validation was attempted and failed.

Cover session usage, whole-session model activity, current-turn usage, current-turn model activity
and cost, tool calls, incomplete calls, subagent lifecycle, agent coordination, and waits according
to the selected scope. Give every behavior capability its `turn` or `session` identity; for `both`,
report both records instead of collapsing their states. Keep the last three behavior surfaces
separate. Codex `sub_agent_activity` records establish only their documented `started`,
`interacted`, and `interrupted` observations. An `interacted` event establishes neither completion
nor a wait. Coordination calls may establish observed task state; only `wait_agent` call/output
records establish waits. Unknown lifecycle kinds fail only the lifecycle surface. Tool output
envelopes may establish tool failures, but their content must never appear in the report.

This package has no owned turn-bounded model-activity or cost provider. Report both current-turn
capabilities as unsupported limitations. Do not present a rerun prerequisite unless a future
accepted contract adds a concrete owned source and invocation path.

Keep observation, inference, uncertainty, unavailable evidence, and failed acquisition visibly
separate. An incomplete call means a supported start lacked its matching completion in the
captured evidence. Waits, timeouts, repeats, and incomplete calls require task context before they
support a cause. Durations may overlap elapsed time, lifecycle counts are observed lower bounds,
and child-session tokens require a stable child mapping.

Treat all monetary values as `estimated API-equivalent cost`, never as a bill. Never persist or
reproduce prompts, responses, transcript content, tool inputs, tool outputs, or credentials.

## Conclude from coverage

Compare reliable observations with the requested task and applicable concurrency limits. Direct
knowledge of the current turn may interpret evidence only as an explicit inference. Token, call,
cost, and duration volume is descriptive and has no fixed abnormal threshold.

Choose exactly one conclusion:

- **Abnormal evidence observed** when reliable abnormal evidence exists, limited to its scope.
- **No abnormality observed** only when every relevant requested capability is sufficiently
  available and no abnormal signal exists.
- **Inconclusive** otherwise.

Session-usage coverage alone cannot establish behavior health, and missing behavior evidence
cannot support a healthy conclusion.

## Handoff

Return one report in this order: identity and requested scope; selected scope boundaries; harness
profile and each source's observation interval, resolved provider executable and version, and effect contract; capability
coverage with evidence or reason; requested-scope usage and estimated API-equivalent cost; turn,
model, tool, incomplete-call, lifecycle, coordination, and wait observations; observed problems;
unavailable evidence; failed
acquisition; uncertainty; causal interpretation; exactly one conclusion; limitations; recovery
prerequisites and whether each requires a separately authorized rerun or cannot recover past
evidence. Derive recovery only from a requested source that the wrapper attempted; an unsupported
or unrequested scope creates no provider recovery action. State provider facts once; do not copy one capability reason into the problem,
limitation, and recovery sections.

For a pre-wrapper stop or wrapper failure, retain that structure where evidence permits and name
the missing prerequisite and failed step. Diagnosis is complete only when identity and scope are
explicit, every requested capability has one state, reliable partial evidence is retained, source
boundaries remain distinct, no transcript content is reproduced, and the conclusion follows the
coverage rules.
