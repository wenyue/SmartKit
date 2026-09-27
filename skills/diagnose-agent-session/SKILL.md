---
name: diagnose-agent-session
description: Diagnose suspected abnormal token use, cost, or execution in one current or completed agent session.
---

# Diagnose Agent Session

Diagnose one exact client/session pair using the least evidence sufficient for the question. The
owned wrapper collects bounded observations; the Agent relates them to the task and decides what
conclusion they support. High usage, a long wait or a failed acquisition does not by itself establish
abnormal session behavior.

Keep the report to metadata and derived observations. Never reproduce prompts, responses,
transcripts, tool inputs, tool outputs or credentials. This boundary applies to failure explanations
as well as successful evidence.

## Establish the target and useful scope

Resolve the client and session together. Supported clients are `codex`, `cursor` and `copilot`, where
`copilot` means GitHub Copilot CLI. Session IDs contain only letters, digits, dot, underscore, colon
and hyphen. When both explicit arguments are absent, `CODEX_THREAD_ID` may supply the current Codex
identity. A partial or invalid explicit pair cannot fall back to that ambient identity; never select
the newest log or substitute a convenient session.

Choose `turn`, `session` or `both` for the diagnostic question. Use `both` when the question spans
turn and session, or their comparison can resolve a material causal uncertainty. If the request
provides no basis for a narrower choice, use `both`. Within the acquired scope, analyze only the
capabilities material to the question, including those needed to distinguish a material alternative
cause. Expand that analysis when an observation exposes a new material uncertainty, not merely
because another metric is available.

`turn` means the final recorded turn of the selected Codex session's immutable snapshot: its latest
user-message boundary through its last event. For a diagnosis of the current live session, this is
the invoking turn as recorded; for a completed session, it is the final recorded turn. There is no
interface for selecting an earlier historical turn.

| Client | Supported acquisition |
| --- | --- |
| Codex | `turn`, `session` or `both`, with local-log turn and behavior evidence and whole-session Tokscale evidence when requested. |
| Cursor or GitHub Copilot CLI | Whole-session Tokscale evidence. A `turn` request stops before acquisition; `both` acquires session evidence and marks the turn unsupported. Neither client has behavior integration in this wrapper. |

Stop before acquisition for a missing, partial or unsupported identity, an invalid session ID, or a
request for another historical turn. State the exact prerequisite without changing the requested
identity or presenting whole-session evidence as turn evidence.

## Establish authority for this acquisition

The Codex profile reads the exact local session log. It retains private content only within this
attempt and reports no such content. Whole-session usage, model activity and estimated cost come
from the installed Tokscale provider, whose acquisition has a different effect boundary.

Before each attempt that requests session evidence, confirm authority for that installation to:

- Scan the selected client's records in the requested date window, or its available local history
  when reliable bounds are unavailable, to select the exact session and read existing Tokscale
  identity state.
- Access the pricing or provider endpoints used by the installed build.
- Read or write only the Tokscale-owned config and cache directories that build resolves on this
  host.

A previous diagnosis grant is not continuing authority. The wrapper performs no login, sync,
credential change, installation, telemetry configuration or remediation. Missing authentication or
prior telemetry is a separate prerequisite; obtain separate authorization before an affected rerun
or any work to supply it.

Cursor may depend on an existing valid Tokscale Cursor identity and a previously completed,
separately authorized sync. Copilot CLI may depend on OTEL file export configured before the
activity; telemetry that was never recorded cannot be reconstructed. These are possible source
prerequisites, not diagnoses to infer from an empty result. A missing matching row alone establishes
neither a missing sync nor missing OTEL history.

## Acquire once and preserve each source's boundary

Resolve the directory of the loaded `SKILL.md` as `<skill-root>`. The CLI can be inspected without
acquiring session evidence:

```text
python "<skill-root>/scripts/timing.py" diagnose --help
```

Generate 32 fresh random bytes and encode them as exactly 64 lowercase hexadecimal characters.
Pass this acquisition ID to the owned wrapper once, with the selected scope and identity:

```text
python "<skill-root>/scripts/timing.py" diagnose --scope both --client "<client>" --session-id "<id>" --acquisition-id "<64-lowercase-hex>"
```

Replace `both` with the selected narrower scope. The Codex profile uses this exact ID to identify the
current acquisition in tool-call records. Exactly one match excludes that call alone. Zero matches
exclude nothing and report that the acquisition call was not observed. Multiple matches exclude
nothing and report failed, ambiguous self-call attribution. Historical IDs and unrelated or
completed diagnosis calls remain evidence.

### Codex observations

The profile copies the exact local log before recording its cutoff and then reads only the immutable
copy. Preserve that source's interval and acquisition state. For turn evidence, identify the session
and the actual turn start/end boundaries. The local profile supplies turn usage and tool, subagent
and wait observations. The wrapper can also retain supported Codex token totals when Tokscale
whole-session evidence is missing or fails; this does not supply the absent model or cost evidence
or erase the provider failure.

### Tokscale observations

Record the resolved Tokscale executable path and version, provider start/end, supported effect
contract and validated JSON schema. Accept grouped client/session/model rows for the exact pair.
Codex alone may use the single `rollout-{session-id}` alias; exact and aliased rows together are
ambiguous and fail attribution. An incompatible schema is a provider failure, not a reason to guess
a version. Provider stdout and stderr remain withheld.

The Codex and Tokscale acquisitions do not form an atomic snapshot. Keep their immutable observations,
intervals, effects and failures distinct even when the wrapper presents them in one report. If a
source is unavailable or fails, retain supported partial evidence instead of trying another telemetry
command. If the wrapper itself cannot run, report that failed step and the exact missing capability;
do not invent an equivalent acquisition route.

## Determine what the evidence can answer

For each selected capability, use exactly one wrapper state and its source-specific reason:

| State | Meaning |
| --- | --- |
| `available` | The named source and schema supply usable evidence. |
| `unavailable` | This attempt has no supported source or compatible evidence. |
| `failed` | Authorized acquisition or validation was attempted and failed. |

The exposed capabilities cover session usage, whole-session model activity and cost, current-turn
usage, current-turn model activity and cost, tool calls, incomplete calls, subagent lifecycle, agent
coordination and waits. Selection follows the diagnostic question and its material causal
dependencies. Give each selected behavior capability its `turn` or `session` identity; at `both`
scope, keep separate records wherever both matter.

This package has no owned turn-bounded model-activity or cost provider. If either capability matters,
state that unsupported limitation. A rerun cannot supply it without a future accepted contract that
provides an owned source and invocation path.

Preserve facts, inferences, uncertainty and unavailable or failed coverage separately for every
selected capability. A source failure may coexist with useful observations from another source or
unaffected capability. For noncritical gaps, narrow the analysis to supported evidence and name what
remains untested. Do not broaden acquisition or declare every capability failed merely to make the
report uniform.

### Interpret behavior without inventing events

Lifecycle, coordination and waits answer different questions. Codex `sub_agent_activity` establishes
its documented `started`, `interacted` and `interrupted` observations. `interacted` proves neither
completion nor waiting. Coordination call/output records can establish observed task state; only
`wait_agent` call/output records establish waits. An unknown lifecycle kind fails that capability
alone. Tool-output envelopes can establish failures, but their private content stays out of the
report.

An incomplete call has a supported start without a matching completion in the captured evidence.
It is not automatically a stuck call. Waits, timeouts, repeated calls and incomplete calls need task
context before supporting a cause. Summed durations can overlap elapsed time, lifecycle counts are
observed lower bounds, and child-session tokens need a stable child mapping before attribution.

Compare reliable observations with the task and applicable concurrency limits. Direct knowledge of
the current turn may inform the interpretation as an explicit inference. Token, call, cost and
duration volume is descriptive; there is no fixed abnormal threshold. Label every monetary value
`estimated API-equivalent cost`, never a bill.

## Reach one bounded conclusion

Choose exactly one conclusion at the narrowest scope supported by the evidence:

| Conclusion | Required basis |
| --- | --- |
| **Abnormal evidence observed** | Reliable evidence establishes abnormality; limit the claim to its proven scope. |
| **No abnormality observed** | Every capability material to the stated conclusion is sufficiently available, with no abnormal signal. |
| **Inconclusive** | Missing, failed or conflicting evidence leaves material uncertainty about the requested diagnosis. |

Whole-session usage alone cannot establish behavior health. Missing behavior evidence cannot support
a healthy-behavior conclusion. Likewise, an acquisition timeout is evidence about acquisition until
task-relevant observations support a claim about the session itself.

## Hand off the diagnosis and necessary recovery

Return one structured report beginning with client/session identity, requested and selected scope,
actual boundaries, harness profile and every used source's interval and effect contract. Then give
the selected capabilities and their scope/state/reason, relevant usage and estimated API-equivalent
cost, material observations and causal inferences, uncertainty or failed evidence, and exactly one
conclusion with the untested surfaces that limit it. Include the resolved provider executable and
version when attempted or when its identity affects interpretation or recovery.

Derive actionable recovery prerequisites only from a requested source the wrapper attempted and an
observed failure or missing prerequisite. Unsupported, unrequested or noncritical capabilities create no provider
recovery action. For example, an observed provider execution/schema failure concerns that installed
provider; it does not establish a need to log in, sync or configure telemetry. Retain the exact
client/session pair and source boundary for any authorized rerun.

State each fact once, where it helps the reader decide what follows, rather than repeating it as a
problem, limitation and recovery step. A pre-wrapper stop or wrapper failure still uses this
structure wherever evidence permits, naming the missing prerequisite and failed step.

The diagnosis is complete when identity and scope are explicit, every selected capability has one
state, reliable partial evidence is retained, source boundaries remain distinct, private content is
absent and the conclusion respects coverage without implying that untested behavior was examined.
