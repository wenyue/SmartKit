# Identity and Security

## Recover without weakening the boundary

Distinguish missing or expired authentication, denied permission, invalid identity or integrity evidence, and failure to perform a check. Credential renewal does not grant a forbidden permission; a failed or unavailable authorization check must not permit the operation. Keep ordinary security conditions in force during recovery, without bypassing integrity validation or broadening grants.

Use the accepted sign-in, renewal, or reauthorization path within the established identity and scope. Renewal that restores future access does not complete the failed operation. Apply replay guidance before resending it; a new session does not erase earlier effects.

After deferred authorization work, verify that the principal, session, resource, and grants still authorize the operation when changes could invalidate them. Use existing synchronization or binding, and reject obsolete results rather than applying them to a replacement identity.

Apply persistence guidance before clearing credentials or session metadata. Avoid unrelated data loss or forced identity changes when direct failure with a supported sign-in action fulfills the contract.

## Preserve useful evidence without exposing private data

Filter credentials, tokens, keys, and needless private information from logs, public errors, telemetry, and feedback. Error objects, cause chains, URLs, decoder messages, and captured payloads may themselves contain secrets; filtering added context alone is insufficient.

Retain useful structural facts, audience-safe operation identity, failure category, and available stacks. Fuller evidence needs an established authorized diagnostic channel and retention contract. Public feedback may need less detail than private diagnostics; neither should expose another principal's data to explain a refusal.
