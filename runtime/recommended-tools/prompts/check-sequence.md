## Run the supplied steps in order

Apply only the supplied steps: automatic configuration, readiness maintenance, then login startup. Handle any separately supplied authorized project-configuration synchronization afterward under its own contract. Each step owns its choices, authorization, actions, and completion condition; approval for one step does not authorize another.

Keep the original task paused while required check steps are incomplete. When a step directs continuation of the original task, return here first if later steps remain. A daily check record limits detection frequency; it proves neither consent nor completion.

## Resolve each decision once

Use the supplied question as a presentation template in the conversation language. Explain the actual findings, effects, recommendation, and reason. Ask one independent question per reply in an ordinary message, without a Harness elicitation tool. Keep update and login choices separate, and reuse applicable explicit authorization.

- Process an answer to a question already presented by the Harness without asking it again.
- Start at Q1 and number questions when actually asked, including questions within maintenance or synchronization. Replace <next> with the next number; automatic steps receive no question numbers.
- For an unresolved decision, end this turn after requesting consent and wait for a subsequent explicit answer. Silence, a closed window, and clarification questions are not selections. Answer clarifications while retaining the pending question.

## Advance or resume from the actual result

| Current step | Next action |
| --- | --- |
| Its completion condition is met | Continue to the next supplied step. |
| The step permits deferral and the user explicitly defers remaining work | Retain those findings as unresolved and continue as that step directs. Deferral is not a repair. |
| Manual action, a failed operation, or a required restart remains pending | Keep the step incomplete; follow its action or recovery instructions before advancing. |

When waiting or resuming, preserve completed actions, pending steps, the current question, and the original task in the conversation. After an update or restart, resolve commands from the currently loaded plugin and recheck the pending step's state before acting.

When the loaded installation changes or these instructions are no longer in context, reload this sequence from `runtime/recommended-tools/prompts/check-sequence.md` and the applicable step from `runtime/recommended-tools/prompts/automatic-configuration.md`, `runtime/recommended-tools/prompts/readiness-consent.md`, or `runtime/local_web/prompts/autostart-consent.md`, relative to that installation's plugin_root resource. All currently needed step instructions are supplied together; user replies do not require another session Hook.

After all supplied steps are settled, continue the original task, retaining any explicitly deferred findings as unresolved.
