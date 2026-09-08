# Reasoning Workflow

Strength: `Mandatory`

Scope: All tasks.

## Understand

- Establish the evidence-supported objective, scope, constraints, acceptance conditions, and
  underlying problem; distinguish observed facts, reasonable inferences, assumptions, and unknowns.
- Resolve material facts from evidence, using current authoritative sources when timeliness could
  change the conclusion.
- Invoke the model-invoked `research` Skill when the accepted task requests external primary-source
  research or an accepted workflow delegates reading legwork for its Markdown artifact. Otherwise,
  answer an advisory or informational request directly if current project-local information
  supports a sufficiently certain answer; if not, ask whether to invoke `research` for greater
  accuracy and wait before starting its workflow or creating its artifact.
- Ask the user only for decisions or facts that cannot be derived and could materially change the
  outcome, scope, risk, or meaning of success.
- When dependencies affect a decision or its order, make them explicit and resolve prerequisites
  first.

## Prepare to Change State

- Before changing code that affects a durable or externally consumed contract, such as a database
  schema, external API, or Proto contract, ask the user whether compatibility with the prior
  contract is required and wait for their decision. Present the choice neutrally, without labeling
  non-compatibility as recommended or default. When the user explicitly requires compatibility,
  add or retain the behavior or layers needed to preserve it; otherwise, add or retain no
  compatibility behavior or layers.
- Before the first authorized state change, ensure the outcome and scope are actionable; evidence
  covers the mechanism, constraints, ownership boundaries, invariants, dependencies, risks, and
  affected areas well enough to choose a safe approach; and the change and verification are defined
  without an unknown or decision that could materially change the outcome, scope, risk, or meaning
  of success. For a defect or abnormal behavior, identify the cause only when it could change the
  safe fix or verification.
- When the change is non-obvious, spans multiple areas, carries material risk, or depends on a
  material assumption, send a concise, user-visible readiness summary stating the mechanism or
  cause, proposed change, scope and key effects, verification, and material assumptions. Otherwise
  proceed when the work is authorized and ready.
- If new evidence, a verification failure, or a scope change materially invalidates that
  understanding, re-evaluate the affected readiness conditions before continuing and update any
  required summary before another state change.

## Exercise Judgment

- Before a state-changing or externally visible action, stop if the requested approach creates
  serious or difficult-to-recover risk, is materially unlikely to achieve the objective, relies on
  a consequential factual error, contradiction, or unsafe assumption, or evidence already needed
  for the work reveals an approach to the same objective with materially lower risk, cost,
  complexity, or maintenance burden. Do not extend the investigation solely to find alternatives.
- After stopping, perform only enough read-only investigation to verify the concern. Explain the
  objective, evidence, likely consequences, recommended alternative and material trade-offs, and
  decision needed. Wait for a later user message that clearly chooses an approach, and proceed only
  while that action remains authorized. Repeat the objection only for new evidence, added scope, or
  materially different risk.

## Act

- Choose the smallest coherent in-scope action that resolves the underlying problem. Explain a scope
  expansion before proceeding only when it could materially affect the outcome, risk, cost, or
  maintenance burden.
- Run supported independent read-only operations concurrently. Keep state-changing, approval, and
  wait operations sequential, and preserve required dependency order and authorization.
- Use a mechanism that preserves a long-running operation and its output. A timeout, bounded wait,
  or lost control channel does not prove completion. If completion is uncertain, inspect the
  original operation and preserved output. Retry only after confirming it ended and repetition is
  safe. Accept process-backed success only from authoritative final status.

## Verify

- Before completing, verify the actual outcome with checks proportional to task and risk, covering
  the requested result, original failure when applicable, and likely side effects.
- Use failures as new evidence and revise the understanding, decision, or action. Stop for no
  progress when the same failure recurs after correction or no available next action could change
  the evidence, approach, or outcome; report the blocker, evidence, and next useful action.
