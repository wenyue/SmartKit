# A Review Group with a Defect and Independent Observations

This fictional report shows the first and only main group of a PR review. Its paths, links, code excerpts, and evidence describe an invented file-upload application.

The PR #42 review compares `0123456` → `89abcde` and covers two production files eligible after excluding tests and previously Viewed files. A changed [test file](https://example.test/repo/blob/89abcde/tests/uploads/upload_controller.test.ts) provides evidence for per-file results and retrying one failed file. The selected worktree `/projects/uploader/.worktrees/pr-42` has its project dependencies installed and a clean Git status. The original checkout's branch, index, and local changes match their state before worktree creation.

## Change Overview

Suppose you upload three files and one fails. Until now, the application only told you that the batch had failed. Choosing Retry sent all three files again, including the two that had already succeeded.

This PR aims to show which files succeeded and which failed, then let you retry just the failed files. The files that already uploaded should stay in the results without being sent again.

---

📄 **[src/uploads/batch_upload.ts](http://127.0.0.1:47821/diff?example=upload-results)** · `+9 / −1`

**M1** · Modify | Return an outcome for each file

> ⏪ Uploading several files returns only whether the whole batch succeeded, so the [upload screen](http://127.0.0.1:47821/diff?example=upload-controller) cannot tell the user which files need another attempt.
>
> ⏩ `uploadFiles` returns one result per file, containing the file and its `uploaded` or `failed` status, so the screen can identify the successful uploads and the files to retry.

---

📄 **[src/uploads/upload_controller.ts](http://127.0.0.1:47821/diff?example=upload-controller)** · `+16 / −6`

**M2** · Modify | Show each file's upload result

> ⏪ When one file fails, the screen shows a failure message for the whole batch, leaving users to work out which files reached the server.
>
> ⏩ `runUploads` uses the [per-file outcomes](http://127.0.0.1:47821/diff?example=upload-results) to show whether each file it tried to upload succeeded or failed, keeping earlier successful rows when failed files are retried.

**M3** · Modify | Retry failed files without uploading successful ones again

> ⏪ If one file uploads and another fails, choosing Retry sends both again.
>
> ⏩ Retry now uses the recorded failures to choose what to upload.
>
> ❌ ⚖️ **Unreasonable** · **P2** · If two files fail, choosing Retry leaves the second file untouched. The handler uses `find`, which stops at the first failed result, even though the screen offers to retry all failed files.
>
> 💡 Collect all failed results, pass their files to `runUploads` together, and cover a batch with two failures in the retry checks.

**M4** · Add | Label the file picker so screen-reader users can identify it

**M5** · Delete | Retire the shortcut for resending the entire batch

> The shortcut resends successful uploads along with failures. Keyboard users can tab to the Retry button and press Enter to retry failed uploads.

**O1** · Reuse the existing upload-history ordering

> 🎨 **Optional improvement** · The `recentUploads` and `pinnedUploads` getters repeat the ordering from [upload history](https://example.test/repo/blob/0123456/src/uploads/upload_history.ts). Both getters and their callers match in the pinned base and head. The result display and retry paths use neither getter.
>
> 💡 Reuse the history comparator to preserve the current order and keep future ordering changes in one place.

---

📄 **[src/uploads/upload_history.ts](https://example.test/repo/blob/0123456/src/uploads/upload_history.ts#L25)**

**O2** · Reuse the existing file-size formatter

> 🎨 **Optional improvement** · `formatRecentSize` and `formatArchivedSize` each repeat the display rules in the [existing file-size formatter](https://example.test/repo/blob/0123456/src/files/format_size.ts). Both functions, their callers, and the shared formatter match in the pinned base and head. Per-file upload results and retrying do not use these history labels.
>
> 💡 Use the same formatter for both history labels so future changes to size units or rounding have one owner.

---

M3 remains unreasonable at P2 because one Retry action leaves some failed files unattempted when several failed. O1 and O2 are optional improvements to reuse the history comparator and file-size formatter so each display policy has one owner.

I inspected the retry handler and the changed test. The test sets up three files with one failure and checks that retrying sends only that file while retaining the successful rows. It does not cover two or more failures in the same batch. No tests or repair checks were run for this read-only review.

📊 **Reviewed 2 / 2 files, with 5 change items.**

- A. **Fix** (recommended): Make M3 retry every failed file, run required checks including the multiple-failure case, and show its dedicated re-review.
- B. **Optimize**: Apply O1 and O2 to reuse the comparator and file-size formatter, then check and re-review those changes.
- C. **Ignore**: Accept that one Retry action leaves other failed files unattempted under M3.

## Selecting Optimize while M3 is pending

Choosing B authorizes work on the two named observations. After their checks and re-review, M3 remains pending and main progress remains 2 / 2 files with 5 change items.

## When the user asks to explain M3

**User** · Walk me through M3. What would Retry send before and after this change, and what would the fix look like?

**M3** · Modify | Retry failed files without uploading successful ones again

> ⏪ Suppose you select `cover.jpg`, `map.png`, and `notes.txt`. Only `cover.jpg` uploads successfully. Choosing Retry sends all three files again because the old handler uses the original selection.
>
> ```typescript
> async function retryUploads() {
>   await runUploads(selectedFiles);
> }
> ```
>
> ⏩ The [revised handler](http://127.0.0.1:47821/diff?example=upload-controller) can read the [outcome for each file](http://127.0.0.1:47821/diff?example=upload-results). It skips the successful upload of `cover.jpg` when choosing what to retry.
>
> ```typescript
> async function retryUploads() {
>   const firstFailed = results.find(result => result.status === "failed");
>   if (firstFailed) await runUploads([firstFailed.file]);
> }
> ```
>
> ❌ ⚖️ **Unreasonable** · **P2** · When both `map.png` and `notes.txt` fail, choosing Retry sends only `map.png`. The call to `find` stops at that first match, so `notes.txt` never reaches `runUploads` on this attempt.
>
> 💡 This proposed fix collects every failed file and makes one upload call when the list has entries.
>
> ```typescript
> async function retryUploads() {
>   const failedFiles = results
>     .filter(result => result.status === "failed")
>     .map(result => result.file);
>
>   if (failedFiles.length > 0) {
>     await runUploads(failedFiles);
>   }
> }
> ```
>
> For this batch, a regression check should expect one upload call containing `map.png` and `notes.txt`, with `cover.jpg` still shown as uploaded.
