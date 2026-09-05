# Public Results

Preserve this vocabulary for callers such as `implement-tickets`. Return the selected route,
`status`, `classification`, `causal_boundary`, `history_result`, `outcome_result`, and
`cleanup_result`. Each phase result carries its state and the evidence/residuals needed to justify
it. Include identities, exact relevant heads/trees or snapshots, verification/review binding when
applicable, publication, retained locations and next owner/action. Keep unrelated detail bounded.

| Phase state | Meaning |
| --- | --- |
| `not-started` | The phase was never entered; name the causal earlier boundary. |
| `inapplicable` | This route and history policy do not require the phase. |
| `stopped` | A prerequisite or guard rejected the phase attempt and complete observation proves it effect-free. |
| `failed` | An effect occurred or remains ambiguous, or required post-effect proof failed. |
| `proven` | History or outcome has its route-specific positive proof. |
| `complete` | Cleanup gives every lifecycle item an authorized removed, retained or delegated disposition. |

Overall `status: complete` requires a proven outcome and completed cleanup. Before route readiness,
a rejection is `status: stopped` at `causal_boundary: preflight`; required phases remain
`not-started`, while inherently unused history is `inapplicable`. After phase entry, overall status
is the causal phase's `stopped` or `failed` until its incomplete work is resolved. A failed history
attempt leaves outcome and cleanup `not-started`. Preserve the original attempt and its causal result
when recording recovery or a later completion.

Classification is the strongest independently proven fact. Start with `no positive result`.
History proof adds `history finalized`; a proven handoff adds `non-integrating handoff`; only
proven local integration or **Already Delivered** adds `authoritative delivery`. Proven discard
uses `explicit discard`. A phase stop/failure cannot erase or upgrade an earlier positive fact.
A push alone remains residual publication rather than a proven PR outcome.

Representative legal results (phase columns are history, outcome, cleanup):

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

These combinations describe causal phases, not just the last command's exit code. If one child
already changed state, a later effect-free rejection within that phase is still a failed partial
phase. Retention during a failure is residual preservation; it does not by itself prove the selected
outcome or complete the run. Conversely, cleanup failure after delivery retains authoritative
delivery so its caller can continue legitimate post-delivery work without repeating integration.
