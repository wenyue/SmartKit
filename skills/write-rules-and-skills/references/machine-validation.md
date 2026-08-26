# Machine Validation

Run Machine Validation after Quality Review when deterministic evidence is applicable. Applicability
includes changed schemas or metadata, references or owned resources, scripts or script-like fixed
flows, and sufficiently concrete or complex procedure, tool, permission, filesystem, state, or
external-effect behavior. Broad judgment guidance and high-confidence simple steps need no special
execution check; record `NOT_REQUIRED` instead of inventing one.

Select checks from the affected owners and surfaces: frontmatter or schema validation, registration
and metadata consistency, reference and resource existence, scripts, generated adapters, formatting,
and repository tests. Machine checks prove structure and observable execution, not natural-language
meaning.

Immediately before every machine execution, the Controller computes the Candidate Fingerprint;
immediately after it returns, the Controller recomputes and compares the fingerprint before using
its result. Any unauthorized or unattributable Candidate change stops the workflow. Preserve the
changed state for reporting; do not revert or conceal it. Use a targeted diff only when the compact
fingerprints and available operation records cannot attribute the change.

For every command, retain the exact command, final exit, and relevant output. On failure, send that
evidence and a bounded Repair Scope to the persistent Author. The Author edits the candidate but
does not run the checks. Every Author change creates a new Candidate Version. Use its changed paths,
Author Change Summary, and before-and-after fingerprints to decide which prior machine results the
change can affect. Rerun the failed check and every invalidated or dependent check. Reuse a prior
result only when the change cannot affect what it proves. Continue until every applicable machine
check has PASS evidence for the same Candidate Version.

After all machine checks pass for that Candidate Version, apply the common Revision Impact Decision
to earlier Quality evidence. Stop as no progress when the same failure survives two repair rounds
without a new supported approach.
