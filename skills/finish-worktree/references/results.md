# Public Results

Read this before returning any outcome. Callers such as `implement-tickets` depend on these field
names and values. Report the selected route, `status`, `classification`, `causal_boundary`,
`history_result`, `outcome_result` and `cleanup_result`.

Each phase result includes its state and supporting evidence or residuals. Supply exact relevant
identities, heads/trees or snapshots, verification/review bindings when applicable, publication,
retained locations and the next owner/action. Bound the detail to what establishes the result and
allows continuation.

## Describe each phase

| Phase state | Meaning |
| --- | --- |
| `not-started` | The phase was never entered; identify the earlier causal boundary. |
| `inapplicable` | The selected route and history policy do not require this phase. |
| `stopped` | A prerequisite or guard rejected the attempt, and complete observation proves it effect-free. |
| `failed` | An effect occurred or remains ambiguous, or required post-effect proof failed. |
| `proven` | History or outcome has its route-specific positive proof. |
| `complete` | Cleanup gives every lifecycle item an authorized removed, retained or delegated disposition. |

Before route readiness, rejection produces `status: stopped` and `causal_boundary: preflight`.
Required phases remain `not-started`; inherently unused history is `inapplicable`. Once a phase is
entered, overall status follows its causal `stopped` or `failed` state until the incomplete work is
resolved. A failed history attempt leaves outcome and cleanup `not-started`. Keep the original
attempt and causal result when recording recovery or subsequent completion.

Overall `status: complete` requires a proven outcome and completed cleanup. A command's exit code
cannot alone establish these phase states. If an earlier child changed state, a later effect-free
guard rejection still leaves that phase partially effected and `failed`.

## Preserve the strongest proven result

Start classification at `no positive result`. History proof supports `history finalized`; a proven
handoff supports `non-integrating handoff`. Only proven local integration or **Already Delivered**
supports `authoritative delivery`. Proven discard uses `explicit discard`.

A later stop or failure cannot erase or upgrade an independently proven fact. A push alone is
residual publication, not a proven PR outcome. Retention during failure preserves residuals; it does
not by itself prove the chosen outcome or complete the run. Conversely, authoritative delivery
survives failed cleanup so a caller can continue legitimate post-delivery work without integrating
again.

The following combinations illustrate the contract. Phase columns list history, outcome and cleanup
in that order.

| Situation | Status | Classification | Phase states |
| --- | --- | --- | --- |
| Dirty unfinished work intentionally retained | `complete` | `non-integrating handoff` | `inapplicable`, `proven`, `complete` |
| Changes transferred, source and backup retained | `complete` | `non-integrating handoff` | `inapplicable`, `proven`, `complete` |
| Review missing before publication readiness | `stopped` | `no positive result` | `not-started`, `not-started`, `not-started` |
| Target moved after history proof, before outcome effects | `stopped` | `history finalized` | `proven`, `stopped`, `not-started` |
| Push proven, PR creation failed | `failed` | `history finalized` | `proven`, `failed`, `not-started` |
| PR proven, retained lifecycle items handed off | `complete` | `non-integrating handoff` | `proven`, `proven`, `complete` |
| Delivery proven, cleanup removal failed | `failed` | `authoritative delivery` | `proven`, `proven`, `failed` |
| Transfer partly applied, restore guarded or unavailable | `failed` | `no positive result` | `inapplicable`, `failed`, `not-started` |
| Exact authorized discard complete | `complete` | `explicit discard` | `inapplicable`, `proven`, `complete` |
