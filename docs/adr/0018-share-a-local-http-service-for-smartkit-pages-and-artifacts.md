# Share a Local HTTP Service for SmartKit Pages and Artifacts

Status: Accepted

Date: 2026-10-15

Local HTML file links have opened as source in the current Codex client, and its file-reference labels have exposed Markdown escapes. Generating a correct HTML file therefore does not establish a usable rendered preview. Use one user-local SmartKit HTTP service for generated previews and future application pages, sharing lifecycle management instead of introducing a separate server for every Skill. Verified fixed repository diff URLs remain preferable for human reviews; the HTTP service supplies the local HTML fallback.

## Address and feature ownership

Bind only to `127.0.0.1`. Every new server process binds port `0`, letting the operating system allocate an available port; reuse an already healthy shared process without reallocating its port. Keep one bounded last-known discovery record separate from expiring artifact data. That record locates and authenticates a live instance rather than reserving a future port. An occupied last-known port does not prevent startup and grants no permission to stop its owner. A new instance also receives a fresh private application credential. Startup and export helpers return the actual current origin and URLs; Agents use those return values rather than assuming a fixed address.

Full URLs are valid for the current instance and may stop working after restart or reboot. Publish the same retained cache identity again to obtain current artifact URLs. This changes neither the captured bytes nor the original deadline; do not recapture mutable source content to silently replace an earlier reviewed comparison. Application route paths remain stable while their full URLs use the discovered current origin.

Use these URL families beneath that origin:

| Route | Meaning |
| --- | --- |
| `/apps/<feature>/…` | An application-page route within the current origin, whose displayed data may change. |
| `/api/<feature>/…` | The corresponding feature's data interface. |
| `/artifacts/<random-id>/…` | Files belonging to one fixed, generated Preview Artifact. |

Each feature owns its content, data interpretation, acquisition authority, and failure meaning. The shared artifact cache owns temporary file groups and their lifetime; the web runtime owns HTTP delivery, explicit publication, and process coordination. Hosting an application does not authorize background collection, repository mutation, or exposing arbitrary disk paths. Publish only declared artifact files; retained raw review snapshots and internal metadata are not public by default. Shared routing must preserve feature access boundaries, including when an interactive generated artifact executes scripts.

## Shared temporary artifacts

Keep rendering with its feature. In particular, the human-review diff exporter remains in `review-for-humans`: it validates the selected comparison and renders HTML, then delegates storage and publication. A reusable cache needs no knowledge of Git, PRs, diff rendering, or the report's business meaning.

The cache stores complete groups under the platform user cache's `smartkit/artifacts/` namespace. Creation accepts a retention duration, defaulting to seven days, and fixes `created_at` and `expires_at` after payload creation succeeds. All files are private by default. A producer may declare particular files eligible for publication, but they become available over HTTP only after explicit publication. Private-only caching starts no HTTP service. Public HTML, private raw snapshots, and internal mapping expire and are physically removed as one group. Access, publication, and URL refresh never renew the deadline.

Core Workspace Policy supplies the default route for disposable temporary files without an overriding location or lifetime contract. An unspecified directory alone does not establish that a durable record may expire. Existing user, project, and Skill requirements for research, ADRs, lessons, prototype evidence, and earlier deletion of attempt-private material remain authoritative. Tools that already return a cached artifact or URL are not cached again.

The supported full plugin distributes the cache and web entry points. Rule delivery supplies their actual installation paths independently of the target repository. Core policy points to their CLI help; business Skills retain only their feature invocation and special requirements. Command usage, parameters, outputs, and failure effects belong in CLI help. This ADR records design and trade-offs, rather than becoming a required input for recurring Skill execution. There is no shared runtime README or additional cache Skill.

For example, a future token-usage page can use `/apps/token-usage/` and `/api/token-usage/…`, with an exported fixed report under `/artifacts/<random-id>/…`. These names illustrate the routing model; they do not declare an existing dashboard or authorize broader session acquisition.

## Recovery and retention

Harness session-start and resume Hooks call the same idempotent startup check used by artifact publishers. When unexpired previews or an enabled permanent application exist, the Hook restores or reuses one healthy service; the publisher verifies availability before returning current links. Startup must tolerate concurrent callers and outlive the Hook invocation. It is bounded recovery, not continuous supervision: after reboot, a supported Hook or publisher starts the service on a newly allocated port, rather than operating-system login registration or a URL click restoring an old full URL. Ending one chat does not stop a process shared by other chats.

HTTP refuses an artifact at its stored deadline even if physical deletion has not yet run. The shared cache cleans positively owned expired groups before creating another group; the existing web process triggers the same cleanup at startup and every 60 seconds while running. Page reads perform no maintenance. Expiry during shutdown is handled on the next startup or creation; deletion can lag by a cleanup cycle or an offline interval. Failed cleanup preserves diagnostics and completed removals, and blocks dependent creation rather than claiming success. Unknown, changed, damaged, or redirected groups are retained.

Previously delivered review exports and their registrations remain readable in their existing locations until their original seven-day deadlines; no content is recaptured, moved, or granted a new lifetime. A historical-format reader permits central cleanup to recognize those groups, but creates no new Skill-specific cache. Existing web discovery and project-observation namespaces remain unchanged. Retired deep-link snapshots are outside this deletion authority. Temporary artifact expiry grants no authority to delete canonical lessons, reports, prototypes, or a feature's source records.

For the initial preview-only use, keep the process available while unexpired artifacts remain and exit when none remain. Once a permanent application is enabled, keep the Hook-started process running until an explicit stop or system shutdown, without an idle timeout or dependence on temporary artifact expiry. This extends the preview-only lifetime to keep permanent pages available while the service runs; discover their current full URLs again after a restart. A permanent feature's source-data retention remains separately owned; seven-day preview expiry does not govern those records.

## Adoption

Implement and verify the shared delivery path first with human-review HTML diffs, including actual filename display and rendered navigation in the supported client. Existing architecture reports and self-contained logic prototypes are candidate artifact consumers. Prioritize readiness/setup status for the first permanent pages, consuming complete owner-produced result snapshots and read-only setup state rather than running collection or maintenance commands on page reads. The first session-diagnostics view should display results from completed, explicitly authorized diagnoses; initiating acquisition, continuous collection, and cross-session aggregation remain separate future decisions. Preserve each feature's current evidence, access, and operation contracts.

Readiness and setup are permanent read-only views, rendered on request rather than saved as expiring HTML artifacts. Readiness keeps the latest complete observation per project and Harness. Setup consumes its owner's current state. Session Hooks offer the relevant private page links when recorded readiness or setup-migration findings need inspection. Refreshing a page performs no check, acquisition, repair, setup, or migration. Their data retention remains with the corresponding feature, independently of temporary artifact retention.

The initial implementation provides the shared runtime, supported session Hooks, human-review HTML delivery, and readiness/setup pages. Earlier verification included a generated HTTP diff and its exact filename rendered by the Codex in-app browser. A native chat-link click, operating-system reboot, and Windows execution were not observed in that implementation session. Other feature-specific adoption candidates remain future work; adding a core default does not rewrite their explicit output or persistence contracts.
