# Shared Terms

Shared meanings for discussing the artifact and its versions across authoring and review roles.

## Artifacts and Skill types

**Artifact:** one Rule or Skill.

**Rule:** persistent policy governing relevant work within its stated applicability. Its requirements
retain their applicability and ownership under core governance.

**Skill:** a named unit of Agent guidance exposed through the native Skill system. It may supply a
task method, shared knowledge, or policy through an entry and supporting resources.

**Task Skill:** guidance for performing a particular task or reaching an outcome. It supplies the
knowledge and method that task needs, with conflicts resolved under core governance.

**Rule-led Skill (Rule Skill):** policy for a domain or condition, exposed through native Skill
discovery under core governance's `rule-<domain>` convention. Its applicability supplies the domain
focus recognized by core governance's type precedence; it remains policy rather than a task workflow.

**Principle-led Skill:** a Skill organized around an outcome, principles, consequential constraints,
and completion conditions, leaving ordinary method to Agent judgment.

**Procedure-led Skill:** a Skill that prescribes steps or order because sequence or protocol
materially affects the result, correctness, safety, coordination, recovery, or external effects.

**Hybrid Skill:** a principle-led Skill with prescribed procedures for the parts whose order
materially matters.

These names describe different aspects. Task Skill and rule-led Skill distinguish task guidance
from policy; principle-led, procedure-led, and hybrid describe organization. A rule-led Skill may
contain principles and necessary procedures while remaining policy. The names imply neither
required headings nor a ranking of quality.

## Authoring versions

**Candidate:** the artifact and supporting resources inside this job's fixed scope.

**Baseline:** the complete pre-write state of those resources, retained throughout the job.

**Fingerprint:** an identifier for one complete Candidate state. Results on different fingerprints
describe different versions, even when the intended change is small. The identifier establishes
version identity, not semantic correctness.
