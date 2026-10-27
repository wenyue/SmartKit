❓ **Q{question_number}** - **是否启用登录自启动？**：是否让 SmartKit 本机 Web 服务在当前用户登录后后台启动？
A．启用，并保存选择。
B．不启用，并保存选择。
➡️ 推荐 A，减少服务未运行造成的本地链接不可用。

<!-- agent-only -->

The current-user login-startup preference was undecided when checked. On entering this step, run `autostart status` through the currently loaded local_web entry. The supplied entry is {entry}; after a plugin update or restart resolve it again from the loaded plugin's local_web resource. If a boolean preference is already saved, skip this question; report unexpected registration state without silently repairing it. If login startup is unsupported, report that and finish this step without requesting elevation or a system registration. A failed status check leaves the step incomplete.

If the supported preference remains undecided, offer only A/B, with no later option and no default. A authorizes `autostart enable`; B authorizes `autostart disable` to persist the refusal. Use the current Python interpreter and execute only the selected action. Do not register system-wide startup, elevate, enable lingering, or change another user's configuration. The preference and OS entries are user-isolated; detection uses the existing per-project, per-Harness daily gate rather than a new global gate.

Verify the returned preference and actual registration state. Successful enable requires preference true and installed registration; successful disable requires preference false and disabled registration. A saved preference alone does not establish success. B must be persisted before continuing. On failure, report its cause and preserve the choice and partial ownership for an explicit retry; leave the operation incomplete. After a verified choice, return control to the check sequence.
