# Authoring Decisions

## Keep the outcome routes separate

Publication, fast-forward integration, working-file transfer, retention, and discard have different acceptance and loss boundaries. The entry chooses a route and shares interruption/cleanup policy; each reference owns the effect-specific procedure. A failed route must not silently become another destination.

## Transfer the change against its original baseline

Return for review keeps B, S, and W distinct and preserves the target's complete index. Replacing B with the target's current HEAD or copying the whole source would either lose target evolution or transfer unrelated work. The explicit three-way model earns its detail because this route must combine work without committing or integrating it.

## Preserve recovery before changing history

Consolidation builds on detached HEAD, uses normal hooks, and updates the branch with its expected old OID only after verification. These steps protect the original branch from hook failures or concurrent movement. Delivery, cleanup, and recovery remain independently observable so a partial failure cannot cause a duplicate integration.
