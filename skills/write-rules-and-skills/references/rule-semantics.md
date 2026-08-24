# Rule

A Rule owns one persistent policy. This reference applies to the candidate itself.

## Establish the Policy Frame

Resolve the Rule's class, owner and strength, scope and applicability, observable
predicate-to-outcome mappings, exceptions, precedence, and ownership boundaries from accepted
intent, the active Rule schema, and governing evidence. Together these form its Policy Frame.
Every applicable field needs one supported value; omit a field only when evidence proves that it
cannot change the policy.

## Write one policy

- Lead with the governing policy. Co-locate each predicate with its required outcome and exception.
- Keep every requirement in the narrowest Rule that owns it; do not duplicate or silently override
  a more-specific Rule.
- Use observable predicates and outcomes. For each threshold, overlap, range, exception, and
  exclusion, reject its nearest false positive and false negative without relying on an undefined
  label.
- Keep ordered execution procedure in a Skill.
- Leave discoverable environment facts in their active owner. Keep rationale and decision history
  in their documentation owner unless they change how the policy applies.
- Use headings for stable policy regions or real applicability branches, lists for peer
  requirements, and tables only for exact mappings or repeated-field comparisons.

## Review and accept Rule semantics

Semantic Review reconstructs every applicable field and condition-to-outcome mapping from the
candidate and evidence. Fail an implicit field, unsupported inapplicability, invented predicate,
duplicated owner, unstated override, or case where the same facts produce two outcomes or no
outcome.

Select only the highest-risk relevant cases:

- an included or applicable case and its nearest excluded or inapplicable case;
- an affected threshold, range, overlap, exception, or owner boundary; and
- a precedence or conflict combination when another Rule can change the result.

Apply the common Acceptance Runner protocol at the real policy seam and require an observable
decision or action; explaining what the Rule says is not application.
