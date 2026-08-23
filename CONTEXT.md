# SmartKit

SmartKit distributes reusable agent capabilities while preserving each target repository's
ownership of its project-specific agent configuration.

## Language

**Harness（宿主）**:
An agent host application, such as Codex, Cursor, or GitHub Copilot, that loads and executes
SmartKit capabilities through its native interfaces.
_Avoid_: Platform, operating system, runtime

**Platform（平台）**:
An operating-system family, such as Windows, Linux, or macOS, on which a Harness and SmartKit run.
_Avoid_: Harness, agent host

**Harness Adaptation（宿主适配）**:
A plugin-private, Harness-scoped Rule that maps shared SmartKit actions to one Harness's native
tools, capabilities, lifecycle semantics, constraints, and missing-capability fallbacks.
_Avoid_: Platform adaptation, duplicated workflow policy

**Instruction Governance（指令治理）**:
The shared policy that defines Rule strength and precedence, Skill authority and overlap, and
semantic conflict resolution.
_Avoid_: Rule configuration, Skill Governance, workflow routing

**Third-Party Skill Policy（第三方技能政策）**:
SmartKit-owned behavioral constraints applied to Skills supplied by third-party plugins or external
sources without modifying their upstream content.
_Avoid_: Upstream Skill patch, project Skill policy, Skill Governance

**Workspace Policy（工作区政策）**:
The shared policy that selects the current workspace or a Task Worktree and governs local Git state,
commit authority, and remote actions independently of any Skill workflow.
_Avoid_: Skill configuration, worktree Skill, repository setup

**Plugin MCP（插件 MCP）**:
An MCP server distributed with the SmartKit plugin and made available through each supported
host's plugin integration.
_Avoid_: Global MCP, shared project MCP

**Project MCP（项目 MCP）**:
An MCP server declared by a target repository as canonical project configuration and rendered by
setup into the native configuration of each enabled host.
_Avoid_: Plugin MCP, hard-coded project template

**MCP Adapter（MCP 适配器）**:
A host-native MCP configuration generated from a canonical Plugin MCP or Project MCP declaration.
_Avoid_: MCP source, handwritten harness copy

**Managed Asset（托管资产）**:
A project file, directory tree, or structured field that setup may update or delete because its
identity and current digest are recorded in the SmartKit Ownership Manifest.
_Avoid_: User-owned asset, inferred-by-name asset

**SmartKit Ownership Manifest（SmartKit 所有权清单）**:
A target repository record of resolved external sources, digest-bearing managed assets, and
non-owned seeded documents.
_Avoid_: External Skill lock, Project MCP lock, migration ledger

**Configured MCP（配置型 MCP）**:
An MCP capability delivered as host configuration while its server remains owned by an external
package, remote service, or project runtime; SmartKit does not copy the server implementation merely
to distribute the configuration.
_Avoid_: Vendored MCP, installed MCP

**Vendored Plugin Skill（内置插件技能）**:
A third-party Skill reviewed, licensed, locked, and copied into SmartKit before release because the
supported plugin hosts load Skills from plugin-local paths and do not share a remote Skill dependency
contract.
_Avoid_: Referenced Skill, runtime-fetched Skill

**Static MCP Readiness（静态 MCP 就绪性）**:
The configuration and local prerequisites that can be checked without starting an MCP server,
probing a remote endpoint, triggering authentication, or requiring an application runtime to be live.
_Avoid_: MCP health, live MCP availability

**Daily Project Check Gate（每日项目检查门控）**:
The first step of the automatic check pipeline, allowing at most one evaluation per canonical project
root, Harness, and local calendar day regardless of the number or outcome of downstream checks.
_Avoid_: Global daily check, per-check throttle, session throttle

**MCP Readiness Profile（MCP 就绪性配置）**:
A typed, non-interactive static check set interpreted after the Daily Project Check Gate. Plugin MCP
declares it explicitly; Project MCP derives it from command paths and environment-variable names.
_Avoid_: MCP-specific Hook, arbitrary check script

### Authoring Evaluation

**Ordinary Artifact（普通工件）**:
A Rule or Skill used directly as policy or as a triggered job rather than as instructions for
authoring another Rule or Skill.
_Avoid_: Runtime artifact, generated target

**Generation Contract（生成契约）**:
A standalone instruction artifact that guides another Agent in authoring a complete future Rule or
Skill. The future target determines whether Rule or Skill semantics apply; the contract itself uses
static walkthrough, while a real target is reviewed later as an Ordinary Artifact.
_Avoid_: Generated target, generator fixture

**Qualification Campaign（资格认定活动）**:
One bounded application of the Acceptance Standard across the representative canary classes needed
to qualify the SmartKit authoring workflow.
_Avoid_: Separate acceptance standard, full rewrite, canary cycle

**Acceptance Standard（验收标准）**:
The single quality contract every authored Rule, Skill, or Generation Contract must satisfy through
evidence-backed authoring, machine validation, fresh semantic review, risk-matched acceptance, and
explicit handoff.
_Avoid_: Qualification-only gate, ordinary acceptance

**Acceptance Portfolio（验收组合）**:
The artifact-specific cases, evidence contexts, executable checks, static walkthroughs, and
regression defects used to demonstrate that one candidate satisfies the Acceptance Standard.
_Avoid_: Acceptance level, alternate standard

**Canary Candidate（金丝雀候选项）**:
One independently evaluated version of a representative Ordinary Artifact or Generation Contract
in a Qualification Campaign.
_Avoid_: Candidate bundle, whole-campaign version

**Candidate Revision（候选修订版）**:
The complete current content state of one authored candidate. Validation, Review, and Acceptance
evidence applies only while that state is unchanged; it does not require a copied tree.
_Avoid_: Revision directory, inherited verdict

**Frozen Canary（冻结金丝雀）**:
A Canary Candidate whose own machine validation, semantic review, and representative acceptance
have passed and whose evidence has not been invalidated.
_Avoid_: Approved campaign, immutable file

**Adoption Gate（采用门控）**:
The all-or-none boundary that permits repository adoption only after every required Canary Candidate
has passed its own gates.
_Avoid_: Campaign restart, per-canary writeback

**Correction Loop（修正循环）**:
The authoring cycle that applies all current uniquely forced findings, reruns invalidated gates, and
continues while each revision makes progress toward a passing Candidate Revision.
_Avoid_: User-confirmed retry, fixed correction budget, one-finding patch

**Fresh Reviewer（新审查者）**:
An Agent that did not author the Candidate Revision it evaluates. A generation contract and a real
target created later default to different Fresh Reviewers, receive separate reviews, and do not
inherit verdicts.
_Avoid_: Author self-review, inherited reviewer

**Acceptance Runner（验收执行者）**:
An isolated fresh Agent that applies one Ordinary Artifact to one representative task using only
the candidate's runtime-visible content, the task, and its required context or tools. The Runner
does not receive the semantic ledger, expected result, diff, author reasoning, review findings, or
prior case output; the Fresh Reviewer judges its observable result.
_Avoid_: Acceptance reviewer, prepared-answer agent, paper walkthrough

**Behavior Control（行为对照）**:
One isolated run before authoring that uses the previously accepted artifact for a rewrite or no
candidate for a new artifact. Use it only when a proposed instruction's sole supported purpose is
to change default Agent behavior and no observed failure already establishes that need.
_Avoid_: Mandatory baseline, repeated sampling, generation target

**Candidate Review（候选审查）**:
One bounded task in which a Fresh Reviewer performs Semantic Review first, then judges the
candidate's Acceptance Portfolio from isolated Acceptance Runner results or the Generation
Contract's static walkthrough, and returns a separate verdict for each gate.
_Avoid_: Review Board, combined verdict

**Regression Corpus（回归语料库）**:
The maintained set of minimal, previously demonstrated authoring defects replayed in later
Qualification Campaigns.
_Avoid_: Exhaustive scenario matrix, ad hoc mutants

**Review Packet（审查材料包）**:
The bounded evidence shared with the Fresh Reviewer for one candidate, excluding author reasoning,
suspected defects, intended fixes, and expected verdicts.
_Avoid_: Repository snapshot, author handoff

**Defect Card（缺陷卡片）**:
One minimal Regression Corpus case containing a supported input, one injected semantic defect, and
the review gate it should violate.
_Avoid_: Full broken candidate, string assertion

### Worktree Lifecycle

**Ticket Batch（工单批次）**:
A frozen dependency-ordered set of implementation tickets whose per-ticket Task Commits are
accumulated, reviewed, and delivered as one scope.
_Avoid_: Ticket queue, combined task, batch commit

**Batch Worktree（批次工作树）**:
A named isolated linked worktree whose branch accumulates the ordered Task Commits for one Ticket
Batch while the delivery target remains unchanged.
_Avoid_: Ticket worktree, base checkout, shared worktree

**Task Worktree（任务工作树）**:
A named, isolated linked worktree whose branch and local state belong exclusively to one accepted
implementation task.
_Avoid_: Worktree, base checkout, shared worktree

**Checkpoint Commit（检查点提交）**:
A provisional commit that preserves a recoverable implementation state within a Task Worktree and
is not part of the promised final history.
_Avoid_: Final commit, Task Commit

**Task Commit（任务提交）**:
A single delivery-history commit that consolidates one accepted task's Checkpoint Commits. In a
Ticket Batch it remains staged until the whole batch passes review and verification.
_Avoid_: Checkpoint Commit, squash commit

**Batch Review Commit（批次审查提交）**:
The optional final Task Commit that consolidates fixes produced by the whole-batch review without
rewriting the preceding per-ticket Task Commits.
_Avoid_: Ticket Task Commit, amended ticket commit, review checkpoint

**Staged Ticket（已暂存工单）**:
A Ticket whose Task Commit has been appended to its Batch Worktree but whose batch has not yet been
delivered to the final target. It remains claimed and is not completed.
_Avoid_: Delivered Ticket, completed Ticket, merged Ticket

**Batch Delivery（批次交付）**:
The verified fast-forward of a reviewed Ticket Batch's ordered Task Commit range and optional Batch
Review Commit to its unchanged final target.
_Avoid_: Ticket staging, tracker completion, batch merge

**Ticket Completion（工单完成）**:
The tracker transition performed by the Ticket Batch controller after Batch Delivery is proven.
_Avoid_: Ticket staging, Task Commit creation, Git cleanup

**Finalization Contract（收尾契约）**:
The closed, mode-discriminated interface by which a caller supplies Git identities, evidence,
history, target, recovery, cleanup, and authorization policy to `finish-worktree`.
_Avoid_: Tracker contract, generic parameter bag, Ticket Batch orchestration

**Already Delivered（已交付）**:
A terminal state in which the selected target is proven to contain the complete accepted task
result, so no Task Commit or delivery mutation is needed.
_Avoid_: Empty Task Commit, no diff
