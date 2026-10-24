# Authoring Decisions

## Separate structural judgment from contract decisions

Keep the workflow bounded to one established pressure and preserve supported behavior. Ordinary choice among sound internal repairs does not require a new design decision, but a missing behavior or authority premise cannot be resolved by picking an implementation. This distinction avoids both unnecessary approval loops and accidental product changes disguised as refactoring.

## Distinguish pre-write stops from post-write failure

Retain the precedence of Failure after writing. A later scope, evidence, or check problem leaves changed state to account for; calling it only Blocked or Redirected would hide that recovery obligation. The workflow deliberately grants no rollback authority.
