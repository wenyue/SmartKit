# Artifact Relationships

This supported public reference defines dependencies between Agent artifacts. Read it directly from the selected writer source; consultation does not invoke the writer's workflow. Apply these relationships with the artifact owner's accepted dependency scope and supported interfaces.

## What constitutes a dependency

An artifact depends on another when its instructions require that other's guidance, capability, result, or resources: invoking a Skill, delegating work to it, reading a specified section, or using its script are all dependencies. Point the edge from the artifact that needs something to the artifact supplying it. An operative body reference counts even when it asks only for a read rather than execution.

The unit is a Rule or Skill together with its owned resources. Reading its own references or composing its own workflow does not create a dependency between artifacts. Neither do attribution, the artifact being worked on, or a self-contained example whose needed material is supplied locally. Classify the reference by the behavior it requires, not its wording or link format.

For this dependency contract, **Rule** includes rule-led Skills, regardless of naming; **Skill** means an ordinary Skill, excluding rule-led Skills. This classification governs dependencies only. Instruction applicability, authority, and conflict precedence retain their existing owners and order.

## Separate responsibility from execution

When a Rule or Skill needs responsibility clarification in its body, use an unnumbered `## Responsibility boundaries` section immediately after the introduction and before other body sections. Use a two-column table headed `Artifact | Responsibility`, naming the current artifact first and then each relevant other owner. Link every artifact cell, including the current artifact, to its actual Rule file or Skill `SKILL.md` entry with a resolvable Markdown link. Omit the section when no boundary needs clarification. Simplified-Chinese mirrors use `## 职责分界` and `工件 | 职责` with the same structure.

Describe ownership and necessary conditions in the table, not instructions to read, invoke, or delegate. It may identify a peer or an upper-level caller as the owner of work outside the current artifact's scope. A boundary description creates no dependency when it neither performs nor delegates that work and needs none of the named artifact's content or availability. Keep redirect results and handoff steps in the operational body; they may carry facts already established while deciding the boundary.

For example, the boundary table may assign pure renames to a renaming Skill, while the workflow uses a design-vocabulary Skill to resolve an interface choice. Only the latter is a dependency. Moving an invocation or required read into the boundary section does not turn it into a boundary description.

## Keep policy independent and capability dependencies sparse

Rules do not depend on other Rules: each owns a clear policy boundary. They may depend on ordinary Skills. The limited exception is a project Rule that explicitly supplements or overrides an applicable Rule of its shared provider. Use that exception sparingly, state the condition and intended difference, and resolve conflicts through the existing precedence contract.

Skills may refer implicitly to independently applicable policy, such as following the project's code style. Required policy must have a supported loading route; its visibility in the current conversation is not a guarantee. Rely on that route rather than a direct Rule-file dependency. A general policy hint cannot stand in for an actual capability dependency, such as invoking a project Skill to prepare an environment.

Use Skill dependencies sparingly, where an upper-level Skill needs a distinct lower-level capability. Check each direct edge against the depending artifact's permitted scope, and keep the complete graph acyclic, directly and transitively. Supply caller context through inputs so a depended-on Skill remains correct for its supported callers; a reference to a possible caller is judged by the same dependency rules, not prohibited merely because it names one. These relationships establish direction without a global layer registry.

## Respect project and provider boundaries

A project Skill is above the ordinary Skills of its accepted shared provider and may depend on them or on other ordinary Skills provided by its project. Skills of other providers are outside that declared scope. Establish the provider and support from accepted ownership and provenance, not from the current working directory or installed plugins; unrelated artifacts retain their own owner's dependency scope.

A shared provider may explicitly expose selected project Skills as reverse-dependency extension interfaces. Those declared targets are visible to the provider as ordinary Skill dependencies and may themselves depend on other project Skills. This exception does not expose arbitrary project Skills or relax the global no-cycle constraint: trace edges through the extension and its dependencies back into the provider. The owning policy identifies the supported targets and how they are found.

## Keep access, availability, and authority distinct

Use another artifact through its supported entry or an explicitly supported public resource interface. Consulting a public resource creates a dependency on its owner without invoking its workflow; it grants neither permission to invoke a restricted Skill nor authority for its operations. Private resources require explicit owning-policy permission. Preserve the resource's owner, loading and failure requirements, and the consumer's task-specific inputs, outputs, permissions, and lifetime constraints.

Within the permitted scope, treat a Skill as available when the supported environment provides it with the depending artifact, through its accepted provider, or through the same project. Handle its failing result through ordinary result handling. A permitted extension that a project may or may not provide needs outcomes for both presence and absence: skip and report the omitted work when the outcome remains meaningful, or stop and identify the missing prerequisite when it is indispensable. Installation does not extend dependency permission or prove a successful result.

Other dependencies, such as command-line tools, MCP services, network access, credentials, and other environment capabilities, can be missing or fail in supported use. Check those the artifact uses, directly or through its resources, and state the outcome when one is unavailable or fails; a depended-on Skill owns the outcomes of its own. A capability visible in the current conversation does not prove it will be present in future use. Packaging and discovery establish neither new policy nor permission.

## Author coordinated sets in dependency order

Before writing a generated set of Skills, the coordinating caller establishes and supplies an order with dependencies before consumers. Each generated Skill may depend only on earlier Skills in that set. Apply the same order during upgrades, even when an older version of a later Skill already exists. Resolve a conflicting dependency by correcting responsibility allocation before dependent writing. The caller owns planning and execution of this order, whether authoring independently or through a setup workflow.
