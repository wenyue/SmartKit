❓ **Q{question_number}** - **是否执行上述更新与维护？**：请确认上面列出的操作。
A．执行列出的操作。
B．不执行，保留未解决项，完成后续检查问题后继续原任务。
➡️ 推荐 A，以修复已报告的问题。

<!-- agent-only -->

Readiness findings that require a user decision use the same temporary pause, including required project setup or migration. Automatic configuration actions are handled in their separate preceding step. Tell the user which checks reported problems, their consequences and proposed actions. Execute only approved actions and leave explicitly deferred items unresolved. Do not show the underlying maintenance commands. If the user explicitly declines or defers all listed readiness actions, do not ask again about those actions or run maintenance; this step is settled with those findings unresolved. Deferral neither repairs them nor advances the successful project setup version.

The bundled internal maintenance runner is {maintenance_runner}. Its available actions for this check are: {action_text}. After consent, treat each semicolon-separated entry as a separate action and invoke only the entries the user approved. An empty action list authorizes no runner invocation; use each finding's owning workflow for actions not represented here. This bundled setup helper performs only the approved tool actions.

If the runner reports manual action required, relay its guidance and wait for confirmation without claiming completion. When the Harness is Codex and the named tool is a Codex plugin, use an available Codex plugin-management tool for that plugin; if unavailable, direct the user to the Codex Plugins interface. This step completes only after the approved work and any required manual action or restart are verified, or the user explicitly leaves the remaining work unresolved. Return control to the check sequence.
