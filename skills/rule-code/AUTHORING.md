# Authoring Decisions

## Judge extraction by production responsibility

Keep extraction guidance centered on the total cost of understanding and changing production behavior. A caller-length target or a wish to test private code directly would turn that judgment into pressure to add interfaces without a production responsibility. The examples identify useful reasons without making a closed catalog of permitted designs.

## Keep suppression approval specific

Retain the exact diagnostic, scope, and necessity as the unit of suppression approval. General implementation approval cannot establish that a particular warning may be hidden; combining these decisions would weaken the user's control over diagnostic coverage.
