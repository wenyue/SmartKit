# Unify Local Hosting and Open Live Review Diffs

Status: Accepted

Date: 2026-10-16

Human reviews need convenient editor diffs while showing subsequent local edits, and the shared hosting code now mixes process, HTTP, storage, and feature responsibilities. Unify the local runtime and use self-contained diff URLs that compare a fixed Git baseline with the current worktree, preferring VS Code and retaining GitHub and HTML fallbacks.

This decision replaces [ADR 0018](0018-share-a-local-http-service-for-smartkit-pages-and-artifacts.md)'s runtime layout, dynamic addressing, route families, fixed-snapshot display links, and historical preview compatibility. Its other ownership, preservation, and feature access boundaries remain applicable.

## Unified runtime and address

Merge `runtime/web` and `runtime/artifacts` under `runtime/local_web`, with one supported CLI and resource entry point. Keep process coordination, HTTP/security, storage, fixed Preview Artifacts, and concrete application features in focused internal modules. Add feature behavior through those modules; the existing status pages and new diff feature justify this organization without a general plugin framework. Diff interpretation and rendering remain owned by the human-review feature, independently of the generic storage and HTTP implementation.

Use the fixed origin `http://127.0.0.1:47821` for simpler addressing and stable links. Reuse a compatible, authenticated SmartKit instance; refuse an unknown process occupying the port. Instance verification remains required before stopping a process. Existing Hooks and CLI operations start or restore the service; an ordinary HTTP click cannot start a stopped host, and this change adds no operating-system startup registration. A producer operation returns the complete usable URL without a separate Agent port query.

Creating private temporary artifacts remains independent of starting HTTP or publishing files. Fixed Preview Artifacts retain declared public files, private-by-default contents, integrity checks, and owner-defined retention. Project observations and setup source state keep their separate ownership and lifetimes.

## Self-contained URLs

Use these feature routes beneath the fixed origin:

| Route | Meaning |
| --- | --- |
| `/diff` | Try the editor, then follow the diff fallback policy. |
| `/diff/html` | Render the local comparison directly as HTML. |
| `/preview/<id>/<file>` | Read a declared file from a fixed Preview Artifact. |
| `/readiness/<project-id>` | Read the project's recorded readiness view. |
| `/setup/<project-id>` | Read the project's setup view. |

Agents supply one batch object to the unified command: an absolute repository worktree root as a search entry, an optional default before baseline, optional complete PR identity, and a nonempty file list. Each file supplies its unique ID and target path; its title defaults to that path, and an explicit file baseline overrides the batch baseline. At least one baseline must be explicit for each file. Baselines can describe the index captured alongside a local review snapshot, an existing blob, a fixed before commit, or explicit absence; an optional per-file before path handles renames. PR identity groups the PR-owning GitHub repository, positive PR number, and full reviewed head commit. All effective PR baselines must be fixed rather than the mutable index. Different repositories or PRs use separate batches.

The module constructs each file's HTTPS GitHub Files changed URL from that identity instead of accepting an Agent-selected complete URL. It supplies GitHub's default `diff-` fragment using SHA-256 of the current UTF-8 file path, including the new path for a rename; `base_path` selects only the before content. An optional per-file fragment overrides that default with an already-observed real diff anchor. Link generation performs no network lookups. It owns Git validation, baseline resolution, worktree discovery, URL encoding, and viewer selection. Agents need no separate worktree search, per-file blob lookup, or additional GitHub visit just to prepare links. Per-file results contain `id`, `title`, `url`, and `markdown`; both link representations target the same localhost `/diff` entry. Viewer-specific destinations belong to the local module's browser pages and responses, so report generation cannot choose a direct GitHub or HTML link in place of editor-first dispatch. The batch object is the only accepted input shape; no legacy localhost-link compatibility is maintained.

Bound local diff URLs carry `repo`, `path`, and `base`, plus an optional `github` fallback. `repo` identifies the selected absolute worktree root; `base` is `blob:<full-object-id>` or `absent`. A bound commit baseline also retains its fixed `base_commit` and optional historical `base_path` as a native-editor locator; the blob remains authoritative. Index snapshots retain that locator only when their blob matches the fixed HEAD commit captured during link generation. Blob-only links use file comparison without searching history for a commit. For PR context, the module finds existing live checkouts matching the fixed reviewed head: one is bound automatically; multiple require a page selection; none or unavailable local comparison data uses GitHub. Unresolved URLs retain `head`, the fixed baseline descriptor, and optional `base_path` to make this decision without a registry. A fixed commit descriptor is immutable; mutable index, `HEAD`, and branch names never appear in returned URLs. Selected URLs discard discovery fields so later local edits or commits do not trigger reselection.

Diff URLs have no registration ID, signature, signing key, or per-link record. Their local paths are visible to anyone holding the URL. The diff endpoint accepts validated, self-contained unsigned comparisons rather than claiming that a link was previously issued. Service-control authentication and other features' private access remain separate responsibilities.

Diff links have no seven-day expiry and survive service restarts without a per-instance lookup or link credential. They remain usable only while the referenced worktree and Git object remain available. A URL does not retain a Git object against garbage collection; an unavailable object is reported as an unavailable baseline, never replaced by the latest content or an empty baseline. Only already-existing Git objects and an explicit absent baseline are supported: link creation does not write new objects, fetch, clone, or persist arbitrary before bytes. Ordinary Preview Artifact retention is unchanged.

## Current comparison and opening behavior

Every local display compares the fixed baseline against the URL's current target path. HTML reads the on-disk worktree; VS Code opens the real file and may display an existing unsaved editor buffer. Bind the URL to that path; when the worktree still exists but the file has disappeared, show deletion. A renamed file needs a new link. A missing repository or a failed read is not interpreted as deletion. The link does not follow renames or substitute the review-time after snapshot.

When a local comparison is available, try the installed VS Code desktop launcher with `--diff`. Prefer a native `git:` URI when the retained fixed commit and historical path still identify the pinned blob. Decline native positioning when the historical path redirects, replacement refs are present, or a configured text converter could change the baseline. Otherwise materialize the fixed blob as a temporary file. Use the actual worktree file when present and materialize only absent sides as empty files, without creating a missing worktree file. Native dispatch uses `--file-uri=<URI>` arguments so Windows Chromium does not discard standalone URLs. Temporary execution files have their own cleanup lifecycle and do not become a link registry or a retained baseline guarantee.

Choose one editor mode before launching; an inapplicable native locator selects file comparison rather than a web viewer. This requires no additional VS Code extension or retry mechanism. The built-in Git provider must be enabled and able to identify the repository for native resources. Editor-internal loading errors remain visible in VS Code and do not trigger an automatic relaunch.

If VS Code is unavailable or explicitly fails to launch, use the generated GitHub Files changed URL when PR context is present; otherwise render HTML from the current local comparison. Automatic and manual GitHub navigation replace the current tab's page rather than opening another tab. After a successfully dispatched launch request, attempt to close the current tab with the standard `window.close()` API. Browser policy may refuse; in that case keep the launch status and manual GitHub/HTML fallback controls. Dispatch and automatic closing do not prove that the editor displayed the diff. The module routes PR context without a corresponding local checkout to GitHub; the Agent need not determine checkout availability. It never fetches, switches branches, or creates worktrees for display. GitHub is the accepted exception to current-worktree display and may show the remote PR version. If neither a local comparison nor a GitHub fallback is available, report the unavailable comparison rather than fabricating a diff.

HTTP GET only displays content. Editor launch uses a protected same-origin POST, with loopback/Host/Origin checks and protection against framing or speculative navigation triggering a launch. Validate the worktree, relative target, object type, and actual file containment. Request parameters cannot select an executable or supply arbitrary command arguments. Keep untrusted preview scripts isolated from trusted feature operations; URL signing is not part of this design.

## Compatibility and review evidence

Update all source consumers, resource metadata, Hooks, launchers, help, Rules, and Skills together. Retire the old CLI paths, cache readers, registrations, and URL compatibility rather than preserving an old-version interface or mixed-version service protocol. Old preview caches need not remain readable. This does not authorize deletion of project configuration, setup ownership records, readiness observations, canonical documents, or unrelated files.

The display change does not relax review-action evidence. Retain the reviewed snapshots needed for report examples, `pass` staging checks, PR Viewed version checks, and re-review. Later worktree edits appearing in a diff are not automatically reviewed or authorized for staging, publishing, or PR operations.
