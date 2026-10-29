# Enable Explicit Current-User Login Startup for Local Web

Status: Accepted

Date: 2026-10-26

The fixed local origin introduced in [ADR 0019](0019-unify-local-hosting-and-open-live-review-diffs.md) keeps links stable, but links remain unavailable after login until a session Hook or producer restores the host. Add explicit current-user login startup so the shared host can be available before a chat begins. This extends the recovery-only startup scope in [ADR 0018](0018-share-a-local-http-service-for-smartkit-pages-and-artifacts.md) and ADR 0019; their service, access, and feature ownership boundaries remain applicable.

## User choice and authorization

Include the choice in the existing Daily Project Check Gate, scoped by canonical project root, Harness, and local calendar day. Complete automatic configuration and settle other update and maintenance decisions first, then ask one independent, numbered login-startup question in the conversation language, with A to enable, B to decline, and a recommendation with its reason. Ask one question per reply and wait for a subsequent explicit choice; there is no later or default option. Keeping the decisions separate prevents approval of maintenance from implicitly authorizing login startup.

`autostart status` is read-only. Execute `autostart enable` or `autostart disable` only with authorization for that choice, and persist either result in the current user's Local Web state directory at `config.json`, under `localWeb.autostart`. An absent value means undecided; a boolean records an explicit choice. The choice is user-wide so other projects do not ask again after it is saved, while each project's checks retain their existing daily gate. Other users' preferences and registrations remain independent.

## Prompt ownership and delivery

Keep one check-sequence prompt in `runtime/recommended-tools/prompts/` responsible for ordering, question numbering, waiting, and returning to the original task. The maintenance prompt owns its choices, approved actions, manual handling, and completion condition. The login-startup prompt lives with `runtime/local_web/prompts/` and owns its choice, state recheck, and registration verification. Merge the short maintenance-action and Codex fallback instructions into the maintenance prompt as conditional branches, so the whole operation can be understood in one place. Native Hook questions and Agent instructions consume the same question text rather than maintaining separate copies in Python and Markdown.

Select prompts from the current findings, validate required resources before recording notification, and deliver the required sequence and step instructions together. File boundaries express responsibilities without requiring another session Hook or file read after every user reply. Updates or restarts require resolving the loaded installation again and rechecking pending state. Keep continuation in the conversation and final preferences in their existing user-owned configuration; add no persistent workflow ledger. Existing CodeGraph reminders and opted-in configuration synchronization retain their separate triggers and contracts. Rule injection and compaction recovery remain independent of this sequence and of the daily check gate, so skipping a check never skips the applicable Rules.

## Registration and runtime ownership

Windows uses a shortcut in the current user's Startup directory and `pythonw.exe`. Linux prefers a working user systemd manager and otherwise uses XDG Autostart in a recognized desktop environment. If neither mechanism is available, report unsupported startup. Do not install a system service, elevate privileges, enable lingering, or change another user's configuration: availability after this user's login does not require machine-wide ownership.

Native entries invoke a stable launcher in the user's Local Web state directory, rather than embedding a versioned plugin entry directly. Supported session Hooks may refresh its verified, unchanged runtime pointer to the current or a newer plugin version, preserving upgrades without downgrading the pointer or recreating OS-disabled entries. A removed plugin installation makes the launcher exit; it does not search arbitrary cached versions. Configuration, owned files, and native registration are checked separately, because a saved preference is intent rather than proof of installation. System policy can still prevent login execution; successful registration does not establish that a later login has been observed.

## Failure, cleanup, and uninstall

An unsuccessful native registration remains incomplete even when all expected files exist. Preserve the explicit choice and partial file ownership so the user can explicitly retry enabling or disable and clean up. If recording partial ownership also fails, report both failures and preserve the files. Unknown or modified files are preserved and reported.

Disabling removes only recorded, unchanged native entries and helper files. It does not stop the Web process shared by active chats. Use `autostart disable` before uninstalling. A Harness with an uninstall callback may invoke that operation; without such a callback, automatic cleanup cannot be guaranteed. No cross-Harness uninstall event is assumed.

Native registration follows the respective [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) and [Desktop Entry Exec](https://specifications.freedesktop.org/desktop-entry/latest/exec-variables.html) command formats, with their separate escaping rules.
