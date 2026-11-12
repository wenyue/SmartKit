# SmartKit dependency policy

This reference supplies SmartKit-specific dependency policy for this repository's authoring and maintenance workflows. Apply it with [Artifact Relationships](../../../../skills/write-rules-and-skills/references/artifact-relationships.md), whose Rule classification includes rule-led Skills and whose Skill dependencies mean ordinary Skills. Establish SmartKit ownership or accepted project support from qualified provenance; current installation and working directory do not bring unrelated artifacts into scope.

## Select the permitted scope

| Artifact | Permitted direct ordinary Skill dependencies |
| --- | --- |
| Shared SmartKit Rule or Skill | Skills bundled with SmartKit, including bundled third-party snapshots, and Blueprint Target Skills through the extension route below. |
| This repository's project-local Skill under `.agents/skills/` | SmartKit's bundled Skills and this repository's provided project Skills. |
| Skill authored for another SmartKit-enabled project | SmartKit's bundled Skills and that project's provided Skills. |

Other plugins' Skills are outside these scopes. A project's Rules may sparingly supplement or override applicable SmartKit Rules under the common relationship contract; this does not change instruction precedence.

Project Skills consume SmartKit through Skill entries and explicitly supported public interfaces. Only this repository's project-local Skills under `.agents/skills/` may depend directly on SmartKit-private resources. Declared, bundled public resources retain their supported interfaces and are not private merely because a Skill owns them.

## Expose project behavior through Blueprint Target Skills

A Blueprint Target Skill is a project-owned ordinary Skill authored from a SmartKit Setup Authoring Blueprint and found by its fixed name. These targets are SmartKit's declared reverse-dependency interfaces: a shared SmartKit artifact may reference them like ordinary bundled Skills, while other project Skills remain outside its direct dependency scope. A target may depend on other ordinary Skills in its project as well as permitted SmartKit Skills; the complete graph through those dependencies must remain acyclic.

Unlike bundled dependencies, a target may be absent. Apply the common presence, absence, and failing-result contract; when an indispensable target is absent, point to project setup as the route to provide it. This policy does not prescribe a detection mechanism. Caller-supplied inputs carry context, and actual references are evaluated as dependencies rather than rejected merely for naming a possible caller. Authoring and acceptance instructions remain distinct from the target's runtime behavior.

Supply these SmartKit-specific requirements as qualified owner input to the public writer. Keep common relationship definitions with its public reference and target-specific meaning with the blueprint; neither the public writer nor a target project needs access to this repository-local workflow.
