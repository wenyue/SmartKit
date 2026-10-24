# Return for Review

Combine task changes with one checkout's working files, before or after review. Preserve target HEAD and the complete index exactly, including existing staged content. This is a handoff for acceptance, not integration. Formal review is required only by independent project/caller policy or an expressly selected history operation.

## Prepare the combined result

Keep three inputs distinct:

| Input | Meaning |
| --- | --- |
| **B** | Immutable shared baseline commit/tree from which task changes are measured. |
| **S** | Task result selected for this handoff: exact contents, absence, types and modes. |
| **W** | Target's actual working files, including committed evolution and local changes. |

S may include attributable staged, unstaged and untracked work without committing or changing the source index. Exclude unrelated work; unresolved ownership or baseline returns to the implementation workflow while both sides remain retained. Transfer **B → S**, not the whole source checkout. Neither target HEAD nor index represents W, and current target HEAD cannot simply replace B.

Where W equals B, use S. Preserve target-only edits and include identical edits once. For overlapping text, use `git merge-file -p` on temporary files with W as local, B as ancestor and S as incoming. Inspect even a clean merge for semantic compatibility. Settle every output before writing to the target. Ask about unresolved conflicts or ambiguous intent; retain both sides while resolving them. Delete/modify cases, complex renames and binary overlap need an explicit resolution. Regeneration stays with its deterministic owner and requires accepted authority.

## Preserve the exact input and output snapshots

Coordinate writers for preparation and application. Create an external operation directory outside both worktrees and their Git directories. Retain readable `before/` and `after/` trees containing only affected relative paths: before holds W and after holds the combined result. Missing files represent absence; record the affected path list so deletion and an omitted input are distinguishable. Copy bytes and intended modes without filters or line-ending conversion, and verify the copies. Capture target branch/HEAD and the complete raw index, including any split-index dependency, without refreshing it. Record source identity and the selected S state for the final comparison.

Use ordinary regular files in real directories. Check both ends of renames and affected ancestors; keep Git administrative paths, nested repositories, symlinks and file aliases outside the operation. Preserve existing permissions. Git patches encode executable mode, not all permissions or metadata: check the native operation's behavior for the actual files and platform before using it. For example, explicit Windows ACLs or POSIX extended attributes may not survive file replacement. Use a verified preserving native method for such files, or stop the affected transfer. Readable backups alone do not prove those attributes can be restored.

## Choose a transfer method that preserves bytes and permissions

Use native file operations that preserve the admitted permissions, with an expected-absence check for creation and an exact pre-state check before replacement or deletion. A working-file Git patch is one option for ordinary files. Check applicable Git attributes first: filters, text conversion, `ident` and `working-tree-encoding` can transform bytes even without staging. Use direct byte-preserving file operations instead when those transformations or unrepresented permission changes apply.

For the patch option, disable line-ending conversion during generation and application so external `core.autocrlf` settings cannot normalize the snapshot bytes. From the operation directory capture stdout as a binary-safe patch file outside both trees:

```text
git -c core.autocrlf=false diff --no-index --binary --no-renames --no-ext-diff --no-textconv --no-color --src-prefix=a/ --dst-prefix=b/ -- before after
```

Exit 1 means differences were found; exit 0 means no changes. Other failures stop preparation. Inspect the patch's exact path set and outputs, including additions and deletions. The two named snapshot directories add one path component, so run in the physical target checkout:

```text
git -c core.autocrlf=false apply -p2 --check --whitespace=nowarn <absolute-patch-file>
git -c core.autocrlf=false apply -p2 --whitespace=nowarn <absolute-patch-file>
```

## Recheck the prepared state, apply, and verify

Before applying, compare every affected target path with before, verify source S and the captured HEAD/index are unchanged, and confirm backups and outputs still match preparation. Patch checking alone is insufficient: context matching can tolerate later edits. Apply only while the coordinated write window still holds. Use working-file-only application; `--index`, `--cached` and `--3way` change the index contract, while `--reject` permits partial application. An empty patch needs no write.

Verify exact combined contents, absence and permissions, unchanged target HEAD/complete index, preserved source and any outside state the chosen operation could affect. Run relevant non-mutating checks on the combined target. Fixing, formatting or generation requires separate express authority. A complete transfer followed by failed checks remains a reviewable result with failure evidence; do not restore it merely to erase that result.

## Handle interruption and retain until accepted

On failure, drift or a missing response, stop and establish whether the original process ended. Inspect actual files against before and after; retain the patch, backups, source and failure details. There is no automatic retry or rollback. Complete or restore only attributable changes after checking current contents and permissions; later edits or ambiguous partial writes require resolution before another write. Recovery must preserve HEAD/index and unrelated work too.

Report source, target and backup locations, preservation and verification results, and the next review or acceptance action. Retain the source worktree, branch, prepared inputs and backups until the user accepts the transfer. Delegated acceptance must trace to the user's authority; cleanup ownership alone does not grant it. After acceptance, removal still needs the entry's cleanup conditions. Identical changes already at the target do not convert this handoff into delivery.
