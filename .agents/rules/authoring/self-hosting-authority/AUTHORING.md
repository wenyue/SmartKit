# Authoring Decisions

## Select each artifact independently

Self-hosting chooses the checkout copy of an applicable artifact; it does not create a bundle that displaces other Rules or Skills. Keeping source choice separate from composition prevents a local writer Skill from accidentally suppressing independently applicable policy.

## Treat failed reads as evidence gaps

A missing checkout source permits the installed fallback, while an unreadable source may contain newer policy. Collapsing those cases would silently execute an older contract precisely when the authoritative one cannot be checked.
