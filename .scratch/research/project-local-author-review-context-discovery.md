# Context Discovery for Project-Local Rule and Skill Authoring

Date: 2026-08-24

## Research question

For a project-local Rule or Skill, should a Controller delegate repository discovery to separate
Project Explorer agents and then give the Author and Reviewers only curated, frozen evidence? Or
should role-fresh Authors and Reviewers inspect the local repository themselves?

This note does not assume that the proposed Explorer design is better. It compares the alternatives
against primary local contracts, official agent documentation, first-party implementation reports,
and original research papers. No source located evaluates this exact Rule/Skill-authoring workflow,
so the recommendation below is an evidence-weighted design judgment, not a directly replicated
experimental result.

## Bottom line

**A Controller-curated, closed evidence packet should not be the default for project-local
authoring or review.** It is useful as a context-reduction technique, but as the only evidence path
it creates a single information bottleneck: the Author cannot adapt discovery to questions that
arise while drafting, and the Reviewer cannot detect that the Controller or Explorer omitted a
material repository fact. Freezing an incomplete packet makes the omission reproducible; it does
not make the review complete.

The evidence favors a **hybrid design**:

- Keep the Controller responsible for accepted intent, authority, scope, role separation,
  candidate freezing, and orchestration.
- Let optional, short-lived Project Explorers perform broad or expensive read-heavy discovery and
  return source-linked leads or durable evidence artifacts. They are accelerators, not exclusive
  evidence gatekeepers.
- Give the role-fresh Author read-only repository access for project-local work. Supply seed
  evidence and canonical entry points, but allow the Author to inspect underlying sources and
  pursue missing facts as drafting reveals them. Do not require the Author to produce a separate
  proof report.
- Give every role-fresh Reviewer independent read-only access to the same frozen repository state.
  A Reviewer may receive canonical entry points as non-exclusive seeds, but should not be limited
  to the Author's or Controller's evidence selection.
- Preserve review reproducibility by freezing both the candidate and the project evidence state,
  requiring file/command citations, and invalidating the verdict if either state changes.
- Reserve closed Context Packets and source-project exclusion for shared portability qualification,
  where independence from project-local facts is itself the property being proved.

This conclusion is strongest for Reviewers. For a very small and fully specified project-local
artifact, a curated packet can be sufficient for the Author, but an independent Reviewer still
needs a way to challenge packet completeness.

## What the current repository establishes

The present design is not neutral. [ADR 0008](../../docs/adr/0008-probe-qualified-soft-isolation.md)
requires every semantic Author, Pruner, Reviewer, and Acceptance Runner to be soft-isolated,
tool-free by default, and supplied with all semantic input through one Controller-selected Context
Packet. Missing context causes a fresh role to be launched with a complete replacement packet.
The public [write-rules-and-skills Skill](../../skills/write-rules-and-skills/SKILL.md) implements
that decision: the Controller may discover project facts, but semantic roles receive explicit
packets and no workspace discovery. The
[Semantic Review contract](../../skills/write-rules-and-skills/references/semantic-review.md)
explicitly gives the Reviewer no tools or workspace paths.

The local evidence for ADR 0008 is narrower than this policy. Its recorded experiments establish
what fresh Codex subagents did and did not receive as ambient context. They support a launch-time
isolation claim. They do **not** compare the quality, completeness, cost, or latency of
Controller-curated packets with project-aware Authors and Reviewers that independently inspect a
read-only repository.

The domain model already separates **Role-fresh Agent** from **Soft-isolated Agent** in
[Authoring Evaluation](../../contexts/authoring-evaluation/CONTEXT.md). Role freshness prevents an
Agent from evaluating its own work; soft isolation additionally excludes source-project context.
That distinction matters: project-local authoring intentionally depends on source-project facts,
whereas shared portability qualification must prove independence from them.

[ADR 0002](../../docs/adr/0002-unified-rule-and-skill-acceptance.md) also recognizes that a
project-local artifact may need repository Rules, configuration, files, or commands as behavioral
evidence. The current closed-packet rule therefore introduces an indirect evidence path for the
class whose semantics are inherently local.

## Evidence from agent systems and research

### Evidence for separate exploration and curated context

Official OpenAI documentation says subagent workflows are particularly useful for codebase
exploration, move noisy exploration and test output away from the main thread, and return distilled
results instead of raw intermediate output. It recommends parallel agents for read-heavy work such
as exploration, tests, triage, and summarization, while warning that each subagent performs its own
model and tool work and therefore increases token use
([OpenAI, “Subagents”](https://learn.chatgpt.com/docs/agent-configuration/subagents)).

OpenAI's Multi-agent guide similarly says bounded subagents provide focused contexts, parallel
exploration can reduce wall-clock time, and comparing independent findings can improve coverage.
It lists exploring separate parts of a large codebase as a good decomposition, but says multi-agent
work is less useful when the task follows one ordered dependency chain
([OpenAI, “Multi-agent”](https://developers.openai.com/api/docs/guides/responses-multi-agent)).
An Explorer-to-Author pipeline is such a dependency chain unless multiple exploration domains are
large enough to justify parallelism.

Anthropic's production research system uses an orchestrator-worker architecture in which tool-using
subagents explore independently and act as intelligent filters. Anthropic reports large gains on
its breadth-first internal research evaluation and major latency reductions from parallel search.
That is credible evidence that separate Explorers can improve broad discovery, but it is evidence
from web research rather than project-local Rule/Skill authoring
([Anthropic, “How we built our multi-agent research system”](https://www.anthropic.com/engineering/multi-agent-research-system)).

Long-context research also supports context reduction as a real concern. *Lost in the Middle*
found that model performance can degrade when relevant information is embedded in the middle of a
long context, including for models designed for long contexts
([Liu et al., 2023](https://arxiv.org/abs/2307.03172)). This supports selective loading and bounded
search. It does not establish that a Controller should be the sole selector, nor that a compact but
incomplete packet is preferable to adaptive repository access.

Finally, *Agentless* shows that a staged localization, repair, and validation pipeline can be both
effective and inexpensive on SWE-bench Lite
([Xia et al., 2024](https://arxiv.org/abs/2407.01489)). This is evidence against assuming that an
autonomous tool-using Author is always necessary. It is not evidence that a single localization
result is sufficient for independent semantic review, and the benchmark concerns program repair,
not instruction authoring.

### Evidence against an exclusive Explorer-to-packet bottleneck

The same Anthropic implementation report identifies the information-transfer problem explicitly:
multi-stage subagent summaries can create a “game of telephone.” Anthropic recommends allowing
specialized agents to persist their outputs directly and pass references rather than forcing all
content through coordinator summaries, because this reduces information loss and token-copying
overhead
([Anthropic, “How we built our multi-agent research system”](https://www.anthropic.com/engineering/multi-agent-research-system)).
That failure mode maps directly to `Explorer -> Controller selection -> Context Packet -> Author or
Reviewer`.

OpenAI's Multi-agent guide says comparing **independent findings** improves coverage, and its Codex
documentation gives a project review example with separate agents for security, code quality,
bugs, races, test flakiness, and maintainability
([OpenAI, “Multi-agent”](https://developers.openai.com/api/docs/guides/responses-multi-agent);
[OpenAI, “Subagents”](https://learn.chatgpt.com/docs/agent-configuration/subagents)). If all those
Reviewers receive the same exclusive evidence selection, their judgments may be independent but
their discovery failures are correlated. They cannot find an omitted file or conflicting local
Rule that none of them can access.

Original software-agent research establishes that direct repository interaction is a viable and
material capability rather than incidental noise. SWE-agent's agent-computer interface was designed
to let an Agent navigate whole repositories, inspect and edit files, and execute tests; its authors
report substantial gains over non-interactive language-model baselines
([Yang et al., 2024](https://arxiv.org/abs/2405.15793)). This does not prove that every Author should
perform unlimited exploration, but it weakens the premise that semantic roles must be tool-free to
remain effective.

The incompleteness problem is also deductive, independent of model quality. A Reviewer restricted
to a finite Controller-selected packet can evaluate whether the candidate matches that packet, but
cannot distinguish “the project contains no contrary evidence” from “contrary evidence was omitted
from the packet.” A second Reviewer with the same packet does not repair that blind spot. Only an
independent evidence path, an exhaustively generated evidence set with a validated completeness
property, or direct access to the frozen source can do so.

Multi-agent debate research reports factuality and reasoning improvements when multiple model
instances first produce and then challenge answers
([Du et al., 2023](https://arxiv.org/abs/2305.14325)). Its tasks are not repository review, so it
should not be treated as direct validation. It does, however, align with the official OpenAI
recommendation to compare independent findings rather than share one upstream selection failure.

## Dimension-by-dimension comparison

| Dimension | Exclusive Explorers + curated packet | Author/Reviewer direct repository inspection | Evidence-weighted judgment |
| --- | --- | --- | --- |
| Factual completeness | Parallel Explorers can cover broad, predeclared domains well. Completeness still depends on decomposition and handoff. | Each role can adapt its search to questions discovered during drafting or review. Independent trajectories can reveal different facts. | Direct or hybrid is safer. Exclusive curation is acceptable only when the evidence universe is demonstrably bounded and complete. |
| Information bottleneck and loss | Adds at least one semantic compression boundary, often two when the Controller reselects Explorer output. `CONTEXT_REQUIRED` loops expose the bottleneck after work has already paused. | Removes the mandatory handoff and lets the role inspect primary local sources. Raw exploration can pollute context. | Use seed evidence and bounded read-only tools, not a closed summary-only packet. Persist references or exact excerpts when Explorers are used. |
| Bias and review independence | Reviewer is independent of the Author's reasoning, but not independent of the Controller's evidence selection. Multiple Reviewers inherit correlated omissions. | A role-fresh Reviewer can independently choose evidence while remaining blind to author reasoning and prior findings. | Role freshness plus independent discovery is the stronger review boundary for project-local work. |
| Reproducibility and frozen-candidate validity | Easy to replay the same packet, assuming the packet is retained. Current workflow intentionally does not persist it. A frozen packet can be consistently incomplete. | Discovery can vary, but the evidence universe can be frozen as a repository snapshot or full content digest; each finding can cite exact paths and commands. | Reproducibility does not require evidence preselection. Freeze project state and record sources. Git commits are content snapshots with tree identities ([Git documentation](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)); an equivalent digest is needed for uncommitted authorized state. |
| Workload and latency | Adds Explorer launches, Controller synthesis, packet construction, and potentially repeated supplement/relaunch cycles. Parallelism helps only when discovery splits cleanly. | Repeats some discovery between Author and Reviewers and can consume more role tokens, but removes sequential handoffs. | Hybridize: optional parallel Explorers for expensive breadth, direct role access for adaptive gaps and independent checking. Measure rather than assume a latency win. |
| Failure modes | Bad task decomposition, missing sources, lossy summaries, stale citations, Controller confirmation bias, correlated Reviewer blind spots, and false confidence from a reproducible packet. | Context pollution, wandering search, duplicate effort, inconsistent repository state, accidental writes, and temptation to inspect author history or unrelated material. | The direct risks have concrete controls: fresh roles, read-only tools, bounded scope, frozen state, source citations, and stop conditions. The exclusive-packet omission cannot be detected from inside the packet. |

## Recommended project-local workflow

### 1. Controller owns the contract, not all facts

The Controller should establish accepted intent, preserved semantics, non-goals, owner boundaries,
permitted paths, applicable project instructions, success conditions, and the exact project state
to be evaluated. It should identify known canonical entry points, but it should not claim that its
initial evidence selection is complete unless a deterministic mechanism actually proves that.

### 2. Explorers are optional evidence accelerators

Start Project Explorers only when discovery is broad, naturally divisible, expensive, or produces
noisy output that would overload a semantic role. Split them by evidence domain—for example command
entry points, loading/distribution, existing policy ownership, or executable validation seams.

Explorer output should contain exact paths, symbols, commands, relevant excerpts, observed results,
and unresolved questions. Prefer a source-linked evidence artifact over a prose-only summary. The
Author and Reviewers must be able to inspect the cited primary source; an Explorer result is a lead,
not an authority.

### 3. Author is role-fresh and project-aware

Launch a role-fresh Author without inherited parent turns or Controller reasoning. Give it the
accepted contract, current candidate and owned resources, target map, applicable authoring
guidance, and seed evidence. Allow read-only repository discovery. The Author's output remains the
complete Rule/Skill replacement; do not turn it into an auditor that must produce a separate
proof dossier. A compact source list in the handoff may support orchestration, but is not part of
the runtime artifact.

If the repository is tiny and the accepted source already contains all material local facts, the
Controller may provide a bounded packet and omit open discovery for efficiency. This is an
optimization justified by a bounded evidence universe, not the definition of project-local
authoring.

### 4. Reviewers get an independent evidence path

Freeze writes, then launch new role-fresh Reviewers for moderately sized, non-overlapping aspects
such as semantic fidelity, Agent executability, and necessity/ownership. Give each Reviewer the
same accepted intent and candidate revision, but not author reasoning, intended fixes, prior
findings, or a claim that seed evidence is exhaustive.

Reviewers should have read-only access to the same frozen project state and must cite every source
that supports a blocking finding. They may use canonical source pointers as seeds, but must be free
to search outside them. This preserves both role independence and evidence independence.

### 5. Freeze the evidence universe, not only the packet

Semantic Review should bind its verdict to:

- the complete candidate content identity;
- the repository commit/tree identity plus an exact representation or digest of authorized
  staged, unstaged, and untracked evidence when relevant;
- applicable project Rule and Skill versions;
- cited file contents and observed command results; and
- explicitly untested surfaces.

Any candidate or material project-evidence change invalidates affected verdicts. This provides a
stronger reproducibility claim than replaying an unpersisted Context Packet because it records the
actual evidence universe against which direct discovery ran.

### 6. Keep execution validation separate

Real script or procedure acceptance still needs an isolated, authorized execution environment.
Repository read access for semantic authoring/review does not authorize writes or external effects.
Execution isolation, role freshness, and shared portability isolation remain three different
controls.

## Where closed Context Packets still belong

Closed packets are appropriate when the question is intentionally **context exclusion** rather
than local correctness. The project-private
[write-shared-rules-and-skills Skill](../../.agents/skills/write-shared-rules-and-skills/SKILL.md)
must prove that a shared artifact does not depend on source-project-only facts. There, allowing an
Author or Reviewer to search the source repository would contaminate the portability proof. A
closed, declared dependency closure and a soft-isolation probe are aligned with the objective.

For the public project-local workflow, the default should instead be ordinary role freshness plus
read-only project access. The public Skill need not know the term Soft Isolation. A more-specific
shared workflow can impose closed packets and stricter no-discovery roles while reusing the common
authoring, review, correction, and acceptance contracts.

## Confidence and unresolved evidence

Confidence is **moderate**, not high. The architectural argument is strong because an exclusive
packet has an unavoidable omission-detection limit, and official agent guidance explicitly favors
independent codebase exploration. However, there is no controlled study of these two designs for
project-local Rule/Skill authoring. The external empirical evidence comes from web research,
software repair, long-context retrieval, and general multi-agent evaluation.

Before replacing ADR 0008's project-local branch, run a small comparative Qualification Campaign
on representative artifacts:

1. Use the same frozen project states, accepted intents, model, reasoning effort, and acceptance
   cases.
2. Compare (a) closed Explorer-curated packets, (b) direct role discovery, and (c) the recommended
   hybrid.
3. Include a narrow Rule, a repository-tooling Rule, a judgment-led Skill, and a script-bearing or
   procedure-led Skill.
4. Measure factual omissions and inventions, defects found uniquely by Reviewers, false-positive
   findings, `CONTEXT_REQUIRED` events, correction rounds, final acceptance results, tokens, and
   wall-clock time.
5. Seed at least one hidden but applicable local fact outside the obvious entry points. A review
   design that cannot discover it has failed the completeness test even if it reproduces its packet
   perfectly.

Unless that comparison shows otherwise, the safest default is: **optional Explorers for breadth,
project-aware Authors for adaptive drafting, and independently project-aware Reviewers for
falsification.**
