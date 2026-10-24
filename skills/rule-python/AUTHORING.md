# Authoring Decisions

## Keep type evidence separate from runtime guarantees

Retain the distinctions between annotations and validation, read-only interfaces and immutability, and assertions and production enforcement. These pairs look interchangeable in compact guidance but promise different runtime behavior. Likewise, typing an ambiguous branch must expose its existing meaning before any supported behavior change, rather than letting the checker choose the product contract.
