---
name: diagnose-agent-session
description: Diagnose suspected abnormal token or API-equivalent cost consumption, model or tool activity, subagent coordination, waits, or incomplete calls in one stable agent session.
---

# Diagnose Agent Session

Diagnose one stable snapshot of an identified agent session; the session may be current or
completed. A deterministic wrapper captures factual evidence; return to evidence-led judgment to
decide whether that evidence is abnormal in the task's context. The wrapper first completes its
Tokscale attempt and acquires immutable Codex local-log content, then records one UTC snapshot
cutoff and evaluates that content through the cutoff. No source acquisition occurs after the
reported cutoff. Keep no task receipt and read transcripts only during this diagnosis.

## Run the evidence wrapper

Resolve a supported client and stable session ID as a pair before invoking the wrapper. The exact
clients are `codex`, `cursor`, and `copilot`, where `copilot` means GitHub Copilot CLI. An unknown
client is unsupported. Codex may omit both identifiers only when `CODEX_THREAD_ID` supplies the
identity of the current Codex thread; infer no other identity and never select the newest log. An
explicit supported client/session pair may identify another stable session. If the pair remains
partial or missing, stop and request it.

Default to `--scope both`; use `turn` or `session` only when the user explicitly chooses it. Resolve
the directory containing this installed `SKILL.md` as the Skill root, then invoke its wrapper by a
path relative to that root. The public platforms are exactly:

- Linux with `sh`:

  ```sh
  skill_root='<absolute directory containing the installed SKILL.md>'
  sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both --client <client> --session-id <id>
  ```

- Windows with PowerShell:

  ```powershell
  $skillRoot = '<absolute directory containing the installed SKILL.md>'
  $wrapper = Join-Path $skillRoot 'scripts\task-metrics.ps1'
  powershell -ExecutionPolicy Bypass -File $wrapper diagnose --scope both --client <client> --session-id <id>
  ```

Stop before the wrapper on an unsupported platform. The wrapper owns resolving Python 3.10 or
newer; execute one wrapper attempt. If supported Python is unavailable, preserve that explicit
error and report Python 3.10+ as a recovery prerequisite. Only a sandbox-caused Tokscale failure
may be retried, once, after obtaining the approval required by the host and with the identical
command outside the sandbox.
The output after the permitted attempt or retry is the factual evidence record.

Tokscale must support client filtering, client/session/model grouping, and the normalized JSON
fields consumed by the wrapper; a missing or incompatible capability is explicit failed evidence,
not a version guess. Cursor usage may depend on a valid prior Tokscale login and completed sync.
The diagnostic neither reads nor stores credentials, logs in, or silently syncs; missing setup or
sync is a recoverable prerequisite. Copilot usage depends on OTEL file export configured before the
diagnosed activity; missing telemetry is an unrecoverable evidence gap for activity before the
snapshot cutoff.

## Evidence contract

Tokscale is the common source for whole-session usage and model activity. Label monetary figures
`estimated API-equivalent cost`; they are not bills. The Codex profile also reads the exact local
session log for current-turn, tool-call, incomplete-call, subagent lifecycle and coordination, and
wait evidence. Cursor and Copilot currently mark those behavior surfaces unavailable while
preserving any Tokscale usage; this describes the diagnostic profile, not what either harness can
ever expose. `both` and explicit `turn` still execute for those profiles and report current-turn
evidence unavailable without borrowing another profile.

Match Cursor and Copilot Tokscale session identity exactly. For Codex only, accept either the exact
session ID or its single `rollout-{session-id}` Tokscale alias, and reject duplicate or competing
aliases rather than aggregating ambiguous attribution. This Tokscale normalization is separate from
exact-session Codex local-log filename discovery and never authorizes selecting a newest log.

Require every capability entry to use exactly `available`, `unavailable`, or `failed`, with its
evidence or reason. At minimum cover session usage, model activity, current turn, tool calls,
incomplete calls, subagent lifecycle and coordination, and waits. Equal profile contracts do not
imply equal observed evidence. Preserve all available evidence when another surface fails.

The wrapper report is factual evidence, not a task-health verdict. Summed model and tool durations
can overlap the elapsed span, lifecycle counts are observed lower bounds, and child-session Token
use is attributable only through a stable child mapping. Persist no prompts, responses, transcript
content, tool inputs, or tool outputs.

## Judge the evidence

Compare reliable evidence with the task's expected work and applicable concurrency limits. Use
task context and direct knowledge of the current turn only to interpret evidence; never fill a
missing value. Token, call, cost, and duration volume is descriptive and has no fixed abnormal
threshold. Choose exactly one conclusion:

- **Abnormal evidence observed** when any reliable abnormal evidence exists, limited to the scope
  that evidence establishes.
- **No abnormality observed** only when every relevant requested capability is sufficiently
  available and no abnormal signal exists.
- **Inconclusive** otherwise.

Session-usage coverage does not establish behavior health. Missing behavior evidence cannot become
a healthy result.

## Handoff

Return one report in this order: identity and requested scope; harness profile; capability coverage;
whole-session usage and estimated API-equivalent cost; turn, tool, and coordination evidence;
problems and unavailable surfaces; the Agent-authored three-state overall conclusion; limitations;
and recovery prerequisites. For a pre-wrapper stop, retain the same structure where possible and
name the exact missing identity or platform prerequisite.
