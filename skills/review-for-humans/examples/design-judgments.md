# Design Judgments from Different Evidence

These fictional cases concern changes whose mechanisms look defensible until their requirements and costs are examined. Each starts with the facts available to that reviewer; the conclusions are not interchangeable between cases.

## An extra snapshot around an existing transaction

An inventory update needs atomic visibility. The reviewer verifies that the existing library transaction already supplies it and that every caller uses that transaction. The PR adds a second snapshot owner around the same writes; its fault-injection tests pass, but it supplies no additional supported guarantee.

The report can judge the behavior reasonable while offering **Optional improvement**: remove the duplicate snapshot layer and retain the existing transaction. The reviewed caller paths establish that the simpler alternative preserves the contract, and the second state owner explains the maintenance benefit. Passing the new tests establishes the tested behavior, not a requirement for the added layer.

## A parser rejects values without a confirmed policy change

A configuration parser now rejects a previously accepted value. Its rejection tests pass, but the task and caller records do not establish that the accepted input contract changed. The reviewer can verify the new rejection path while remaining unable to judge whether rejecting that value is correct.

The reasonableness verdict is **Uncertain**. The report names the disputed input and missing contract decision, then warns about the compatibility consequence. It proposes neither removal nor retention as an established Fix or Optimize remedy. A tidy adapter does not resolve the missing policy, and the missing correctness basis remains a limit on advancement.

## A bound for allocation controlled by an untrusted peer

A peer-supplied length reaches an allocation without a library limit. The service has a confirmed availability requirement, and the reviewer traces a request that can exhaust memory. The PR adds a bound at the parsing boundary and reports invalid lengths through the existing error path.

The observed path and requirement support **Reasonable** without a prior production incident. The single boundary check can also support **Elegant** when it keeps validation with the parser and adds no second state owner. This case has a concrete trust-boundary risk; the unresolved parser-policy case above does not establish an equivalent need merely by having rejection tests.

## Callback ordering is confirmed, but the coordinator's rationale is missing

M12 preserves a confirmed callback-ordering contract but introduces ambient context and deferred callbacks. The source and relevant checks establish ordering and failure behavior. They do not establish why this mechanism was chosen or whether its structural cost was accepted. Pass was already selected, and the rest of the delivery prerequisites are satisfied.

The affected item's judgment and closing excerpts read:

> ⚖️ **Reasonable** · The changed path preserves the confirmed ordering and failure behavior.\
> 🎨 **Uncertain** · Ambient context makes callback ownership harder to follow; the missing design constraints and trade-off decision prevent a confident judgment about whether this complexity is necessary or can safely be simplified.

⚠️ M12's callback ownership is harder to follow, while the mechanism's justification and acceptance remain unknown. This is an unresolved elegance concern, not a supported optimization proposal.

The Agent continues the selected delivery with that warning. It has no evidence-backed remedy to add to Optimize and no unrelated observation to turn into an O item. The confirmed callback contract and completed checks distinguish this case from the parser's missing correctness basis.

### Design context arrives later

If the user supplies the earlier decision accepting this mechanism for a confirmed constraint, the reviewer records that constraint and retained cost. Approval does not itself establish elegance or require another request to optimize the same accepted burden.

If instead the reviewer establishes a simpler implementation that preserves the confirmed contract with worthwhile benefit, and no earlier decision declined it, the report can offer **Optional improvement** with the concrete remedy. The new evidence changes the confidence of that proposal; the earlier uncertainty was not permission to implement it.
