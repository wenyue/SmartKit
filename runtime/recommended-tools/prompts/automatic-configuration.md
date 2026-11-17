Automatically execute only the listed configuration actions without asking for confirmation. These are policy-declared configuration writes; tool installation, upgrades, project setup, and login startup retain their own decisions.

The bundled maintenance runner is {maintenance_runner}. Its configuration actions for this check are: {action_text}.

Briefly tell the user which settings will be checked and changed if needed. Use the current Python interpreter and run each semicolon-separated action separately. The runner rechecks the effective setting before writing, preserves values already meeting the requirement, uses the user-layer version to reject concurrent changes, and verifies each result.

| Action result | Next action |
| --- | --- |
| `completed` | Configuration changed and requires a new session. Tell the user to start one, retain all pending steps, and verify the effective setting after the restart before advancing. |
| Already satisfied | No restart is needed for this action. |
| Failed or unverified | Report the result and keep the action unresolved. If detection failed, do not guess a value. |

After all actions and any required restart are verified, return control to the check sequence.
