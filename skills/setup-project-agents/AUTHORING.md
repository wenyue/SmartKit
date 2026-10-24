# Authoring Decisions

## Keep full setup, restoration, and synchronization separate

These routes can produce similar-looking files but establish different results. Full setup reassesses project guidance and Agents and prepares CodeGraph; restoration preserves accepted backup bytes; local synchronization renders established inputs. A copied setup marker or converged configuration cannot substitute for full setup success. Operation selection therefore stays ahead of route-specific prerequisites.

## Treat local usability and backup identity as independent facts

A fresh checkout may contain useful configuration while its copied repository binding still lacks a successful local receipt. Treating the copied binding as authority would select an unconfirmed source; treating it as unusable configuration would force unnecessary restoration or initialization. The two-question selection preserves both distinctions.

## Let writers own individual artifacts and Setup own the set

Every blueprint request receives its own public-writer Candidate and complete review. Setup supplies allocation and dependency order, then reconciles the combined result and mapped links before registration. Individual passes cannot prove combined coverage, while direct controller repairs would break their accepted fingerprints and Author ownership.

## Freeze setup inputs while allowing runtime-only refresh

Setup-relevant source or target drift requires cancellation and a new session, even when a separate task authorized the edit. CodeGraph runtime state remains outside that freeze so an idle-exited daemon can be refreshed before the first finish attempt. The boundary avoids both silently changing the accepted input and needlessly restarting for transient runtime state.

## Record success only after terminal cleanup

The final setup-version update follows successful private-session cleanup and uses guarded writes. Retain separate source-save, target-apply, cleanup, version-update, and publication outcomes: they can fail independently across filesystems, and recovery must neither erase saved source work nor claim an atomic rollback that did not occur.
