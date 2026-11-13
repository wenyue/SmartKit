# Identity and Security

Use this reference for authentication, authorization, integrity checks, security fallback, and diagnostics containing credentials or private payloads.

## Recover without weakening the boundary

Distinguish missing or expired authentication from a refused permission, invalid identity or integrity evidence, and failure to perform the check. Refreshing an expired credential may be supported recovery; it does not grant permission for a forbidden operation. A failed or unavailable authorization check must not become permission to proceed.

Use the accepted sign-in, renewal, or reauthorization path within the established identity and scope. Keep attempts bounded and retain the failed operation's outcome when renewal only restores future access. Replaying the original request also needs the external-operation replay conditions; a new session does not prove the earlier request had no effects.

After deferred authorization work, verify that the principal, session, resource, and grants still match the operation when changes could invalidate its authorization. Use the owner's existing synchronization or binding mechanism. Reject obsolete results rather than applying them to a replacement identity. Do not bypass integrity validation or broaden grants as a fallback for an operational failure.

Treat clearing invalid credentials or session metadata as a persistence decision as well: establish loss authority, recreation, and the capability unavailable until then. Avoid unrelated data loss or forced identity changes when direct failure with a supported sign-in action fulfills the contract.

## Preserve useful evidence without exposing private data

Filter credentials, tokens, keys, and needless private information from logs, public errors, telemetry, and user feedback. Error objects, cause chains, request URLs, decoder messages, and captured payloads can themselves contain secrets; filtering only added context fields is insufficient.

Retain useful structural facts, operation identity safe for its audience, failure category, and available stacks when raw payloads cannot be disclosed. Preserve any fuller evidence only through an established authorized diagnostic channel and its retention contract. Public feedback may need less detail than private diagnostics; neither should expose another principal's data to explain a refusal.

Verify denied and unavailable-check paths, stale identity after an asynchronous gap, failed renewal, and diagnostic redaction where they affect the changed boundary. Successful recovery must preserve the same security conditions as ordinary success.
