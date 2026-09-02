---
name: diagnose-agent-session
description: Diagnose suspected abnormal token or API-equivalent cost consumption, model or tool activity, subagent coordination, waits, or incomplete calls in one stable agent session.
---

# Diagnose Agent Session

Diagnose one stable snapshot of an identified agent session; the session may be current or
completed. The requested scope is `turn`, `session`, or `both`. This Skill authorizes read-only
observation and reporting. Treat remediation, login, synchronization, exporter configuration, or
any other state change as a separate action requiring its own authorization.

## Fix identity and scope

Resolve one supported client and stable session ID as a pair. The wrapper's supported clients are
`codex`, `cursor`, and `copilot`, where `copilot` means GitHub Copilot CLI. An explicit pair may
identify a current or completed session. `CODEX_THREAD_ID` supplies only the identity of the current
Codex thread and may supply the pair only when both arguments are omitted. It does not identify
another or a completed session. Never infer an identity from recency; never select the newest log.

Use `both` unless the user explicitly requests `turn` or `session`. Stop before acquisition when
the pair is partial or missing, the client is unsupported, or the platform has no supported
launcher; report the exact prerequisite rather than substituting another session or scope.

## Acquire one factual record

Resolve the directory containing this installed `SKILL.md` as the Skill root and invoke its owned
wrapper with the fixed identity and scope. Keep this invocation shape so the wrapper can exclude
its own call from activity evidence.

Linux with `sh`:

```sh
skill_root='<absolute directory containing the installed SKILL.md>'
sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both --client <client> --session-id <id>
```

Windows with PowerShell:

```powershell
$skillRoot = '<absolute directory containing the installed SKILL.md>'
$wrapper = Join-Path $skillRoot 'scripts\task-metrics.ps1'
powershell -ExecutionPolicy Bypass -File $wrapper diagnose --scope both --client <client> --session-id <id>
```

Replace `both` only for an explicitly selected scope. Execute one wrapper attempt. The wrapper
resolves Python 3.10 or newer; preserve its explicit error when no supported Python is available.
Do not replace failed acquisition with a different telemetry command, inferred value, login, sync,
or configuration change.

The wrapper first completes its Tokscale attempt and acquires immutable Codex local-log content,
then records one UTC snapshot cutoff and evaluates only that content through the cutoff. No source
acquisition occurs after the reported cutoff. Its output, including partial output and errors, is
the factual evidence record.

Tokscale evidence requires client filtering, client/session/model grouping, and the normalized
fields accepted by the wrapper. Missing or incompatible capability is failed acquisition, not a
version inference. Match Cursor and Copilot session IDs exactly. For Codex usage only, the wrapper
also accepts the single `rollout-{session-id}` alias and rejects duplicate or competing aliases;
this does not relax exact Codex local-log discovery.

Cursor usage can be unavailable until a valid prior Tokscale login and completed sync. Copilot
usage can be unavailable when OTEL file export was not configured before the activity; past
telemetry cannot be reconstructed. State these as recovery prerequisites or unrecoverable gaps,
respectively, without performing them.

## Read the evidence contract

For every requested capability, preserve the wrapper's exact state:

- `available`: the record contains usable evidence;
- `unavailable`: the source or integration exposes no usable evidence for this snapshot;
- `failed`: acquisition or validation was attempted and failed, with the observed cause.

Cover session usage, model activity, current turn, tool calls, incomplete calls, subagent lifecycle
and coordination, and waits. Tokscale supplies whole-session usage and model activity. The Codex
profile additionally derives behavior evidence from its exact local log. Cursor and Copilot
currently report those behavior surfaces unavailable in this diagnostic profile; that is not a
claim about every capability those harnesses may expose. Preserve reliable evidence when another
capability is unavailable or failed.

Keep observation, inference, uncertainty, unavailable evidence, and failed acquisition visibly
separate. The wrapper report is observation, not a health verdict. An incomplete call means a
start lacked a matching completion in captured evidence by the cutoff; a wait, timeout, repeated
call, or incomplete call needs task context before it supports a cause. Summed model and tool
durations may overlap elapsed time. Lifecycle counts are observed lower bounds, and child-session
tokens are attributable only through a stable child mapping.

Treat all monetary values as `estimated API-equivalent cost`, never as a bill. Do not persist or
reproduce prompts, responses, transcript content, tool inputs, tool outputs, or credentials.

## Conclude from coverage

Compare reliable observations with the requested task, expected work, and applicable concurrency
limits. Use direct knowledge of the current turn only as interpretation and label resulting causal
claims as inference. Preserve uncertainty; never fill an evidence gap. Token, call, cost, and
duration volume is descriptive and has no fixed abnormal threshold.

Choose exactly one conclusion:

- **Abnormal evidence observed** when any reliable abnormal evidence exists, limited to the scope
  that evidence establishes.
- **No abnormality observed** only when every relevant requested capability is sufficiently
  available and no abnormal signal exists.
- **Inconclusive** otherwise.

Session-usage coverage alone cannot establish behavior health, and missing behavior evidence
cannot support a healthy conclusion.

## Handoff

Return one report in this order: stable identity and requested scope; harness profile and snapshot
cutoff; capability coverage with evidence or reason; whole-session usage and estimated
API-equivalent cost; turn, model, tool, incomplete-call, subagent, and wait observations; problems,
unavailable evidence, failed acquisition, and uncertainty; causal interpretation; exactly one
three-state conclusion; limitations; recovery prerequisites and whether each requires a separately
authorized rerun or cannot recover past evidence.

For a pre-wrapper stop or wrapper-level failure, retain that structure where evidence permits and
name the missing prerequisite and failed step. Diagnosis is complete only when the stable identity
and scope are explicit, every requested capability has one of the three states, all reliable
partial evidence is retained, and the conclusion follows the coverage rules.
