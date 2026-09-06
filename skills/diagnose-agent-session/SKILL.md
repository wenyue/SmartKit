---
name: diagnose-agent-session
description: Diagnose suspected abnormal token or API-equivalent cost consumption, model or tool activity, subagent coordination, waits, or incomplete calls in one current or completed agent session.
---

# Diagnose Agent Session

Diagnose one identified agent session at `turn`, `session`, or `both` scope. The owned wrapper
collects bounded facts; the Agent relates them to the task and reaches the conclusion.

## Principles

- **Identity before evidence.** Analyze exactly one client/session pair. Never infer the target from
  recency or substitute a convenient session.
- **Least sufficient scope and analysis.** Acquire only the needed scope. From that evidence,
  interpret and report only material capabilities, expanding the analysis only when an observation
  exposes a material alternative cause.
- **Explicit source boundaries.** Keep each source's interval, effects, coverage, and failure state
  distinct. The Codex and Tokscale acquisitions do not form an atomic snapshot.
- **Observation before inference.** Preserve partial evidence and distinguish observed facts from
  task-dependent interpretation, uncertainty, and unavailable or failed coverage.
- **Privacy by construction.** Report metadata and derived observations, never prompts, responses,
  transcript content, tool inputs, tool outputs, or credentials.

## 1. Fix identity and scope

Resolve one client/session pair. Supported client identifiers are `codex`, `cursor`, and `copilot`;
`copilot` means GitHub Copilot CLI. A session ID may contain only letters, digits, dot, underscore,
colon, and hyphen. `CODEX_THREAD_ID` supplies the current Codex identity only when both explicit
arguments are absent; never select the newest log or otherwise infer identity from recency.

`turn` means the final recorded turn in the immutable Codex snapshot, from its latest user-message
boundary through its last event. In a live session, that is the invoking turn; in a completed
session, it is the session's final recorded turn. The interface cannot select another historical
turn.

Choose the least scope sufficient for the request. Use `both` only when the diagnosis spans the
current turn and whole session, or comparing them can resolve a material causal uncertainty. If the
request gives no basis for a narrower choice, use `both`.

Codex supports `turn`, `session`, and `both`. Cursor and GitHub Copilot CLI support only
whole-session Tokscale evidence. Stop before acquisition for a Cursor or Copilot `turn` request. For
`both`, acquire the requested session evidence and mark turn evidence unsupported; never present
session evidence as turn evidence.

Also stop before acquisition when the client/session pair is missing or partial, its client or ID is
unsupported, or another historical turn is requested.
Report the exact prerequisite without changing the identity or scope.

## 2. Authorize the sources

The Codex profile reads the exact local session log. It retains content only for this attempt and
does not report private content.

Whole-session usage and model evidence comes from the installed Tokscale provider. Before each
attempt that requests `session` evidence, confirm authorization for that installation to:

- scan the selected client's records in the requested date window—or its available local history
  when reliable bounds do not exist—to select the exact session and read existing Tokscale
  identity state;
- access the pricing or provider endpoints used by that installed build; and
- read or write only the Tokscale-owned config and cache directories that build resolves on the
  current host.

The wrapper performs no login, sync, credential change, installation, telemetry configuration, or
remediation. If authentication or prior telemetry is missing, report the prerequisite and obtain
separate authorization before any affected rerun. A previous diagnosis grant is not continuing
authority.

## 3. Acquire immutable evidence

Resolve the directory containing the loaded `SKILL.md` as `<skill-root>`. Generate 32 fresh random
bytes and encode them as exactly 64 lowercase hexadecimal characters. Pass that acquisition ID to
the owned wrapper once. The Codex profile matches only that exact ID against tool-call records:
Exactly one match excludes that call alone. Zero matches exclude nothing and report that the
current acquisition call was not observed. Multiple matches exclude nothing and report failed,
ambiguous self-call attribution. Historical IDs and unrelated or completed diagnosis calls remain
evidence.

```text
python "<skill-root>/scripts/timing.py" diagnose --scope both --client "<client>" --session-id "<id>" --acquisition-id "<64-lowercase-hex>"
```

Replace `both` with the selected narrower scope. When a surface is unavailable or fails, retain its
partial evidence instead of trying another telemetry command.

### Codex source

The profile copies the exact local log before recording that source's cutoff, then reads only the
immutable copy. For `turn`, the report identifies the selected session and its turn start and end
boundaries. Codex additionally supplies tool, subagent, and wait evidence.

### Tokscale source

The provider supplies whole-session usage and model activity. Record the resolved Tokscale
executable path and version, provider start and end, supported effect contract, and validated JSON
schema. Accept client/session/model grouped rows for the exact pair. Only Codex may also use the
single `rollout-{session-id}` alias; exact and aliased rows together are ambiguous and fail.
Incompatible schemas are provider failures, not invitations to guess a version. Provider stdout and
stderr remain withheld. The two source intervals are independent and do not form an atomic
snapshot.

Cursor may require an existing valid Tokscale Cursor identity and a previously completed,
separately authorized sync. GitHub Copilot CLI may require OTEL file export configured before the
activity; absent historical telemetry cannot be reconstructed. Cursor and Copilot have no behavior
integration in this wrapper.

## 4. Interpret coverage before values

Select every capability material to the diagnosis, including any supporting capability needed to
distinguish a material alternative cause. Expand the selection only when an observation reveals a
new material uncertainty. Give every selected capability exactly one wrapper state:

- `available`: its named source and schema contain usable evidence;
- `unavailable`: no supported source or compatible evidence exists for this attempt;
- `failed`: an authorized acquisition or validation was attempted and failed.

The wrapper exposes session usage, whole-session model activity, current-turn usage, current-turn
model activity and cost, tool calls, incomplete calls, subagent lifecycle, agent coordination, and
waits. Select the surfaces relevant to the request and their material causal dependencies, not all
surfaces merely because they exist. Give each selected behavior capability its `turn` or `session`
identity; at `both` scope, keep separate records when each matters.

Keep lifecycle, coordination, and waits separate. Codex `sub_agent_activity` records establish only
their documented `started`, `interacted`, and `interrupted` observations. `interacted` establishes
neither completion nor a wait. Coordination calls may establish observed task state, but only
`wait_agent` call/output records establish waits. An unknown lifecycle kind fails only that surface.
Tool output envelopes may establish tool failures, but their content must not enter the report.

This package has no owned turn-bounded model-activity or cost provider. If either capability is
selected, report it as an unsupported limitation; do not invent a rerun prerequisite without a
future accepted contract that supplies an owned source and invocation path.

Keep facts, inferences, uncertainty, unavailable evidence, and failed acquisition visibly separate
on every selected surface. An incomplete call is a supported start without its matching completion
in the captured evidence. Waits, timeouts, repeats, and incomplete calls require task context before
they can support a cause. Durations may overlap elapsed time, lifecycle counts are observed lower
bounds, and child-session tokens require a stable child mapping. If noncritical evidence is missing,
narrow the analysis to supported surfaces and name what remains untested; do not broaden acquisition
or turn the gap into a universal failure.

Treat every monetary value as `estimated API-equivalent cost`, never as a bill.

## 5. Reach one conclusion

Compare reliable observations with the requested task and applicable concurrency limits. Direct
knowledge of the current turn may inform interpretation only as an explicit inference. Token, call,
cost, and duration volume is descriptive; none has a fixed abnormal threshold.

Choose exactly one conclusion at the narrowest supported scope:

- **Abnormal evidence observed** when reliable abnormal evidence exists, limited to its scope.
- **No abnormality observed** only when every capability material to the stated conclusion is
  sufficiently available and no abnormal signal exists.
- **Inconclusive** when missing, failed, or conflicting evidence leaves material uncertainty about
  the requested diagnosis.

Session-usage coverage alone cannot establish behavior health. Missing behavior evidence cannot
support a healthy conclusion.

## 6. Hand off the diagnosis

Return one structured report. Start with the session identity, requested and selected scope, scope
boundaries, harness profile, and every used source's interval and effect contract. Then include only
what the diagnosis needs:

- each selected capability's scope, state, and reason;
- relevant usage and estimated API-equivalent cost;
- material observations, problems, missing or failed evidence, uncertainty, and causal inference;
- exactly one conclusion and the untested surfaces that limit it; and
- actionable recovery prerequisites.

Include the resolved Tokscale executable and version when that provider was attempted or its identity
affects interpretation or recovery. Derive recovery only from a requested source the wrapper
attempted. An unsupported, unrequested, or noncritical surface creates no provider recovery action.
State each fact once instead of repeating it as a problem, limitation, and recovery step.

For a pre-wrapper stop or wrapper failure, preserve this structure wherever evidence permits and
name the missing prerequisite and failed step. Diagnosis is complete only when identity and scope
are explicit, every selected capability has one state, reliable partial evidence is retained,
source boundaries remain distinct, no private content is reproduced, and the conclusion follows
the coverage rules without implying coverage of an untested surface.
