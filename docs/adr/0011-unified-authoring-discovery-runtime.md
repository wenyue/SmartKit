# Use One Authoring Discovery Runtime with Evidence Qualification

Status: Accepted

Date: 2026-08-28

## Context

ADR 0010 kept shared authoring behind a private soft-isolation Adapter, mandatory post-freeze
Probe, and restricted evidence environment. That reduced incidental source-project exposure, but
it also duplicated Role Launch policy, made relevant evidence available only through context
requests, and could not reliably exclude host-injected instructions, tools, MCP descriptions, or
hooks. The resulting attention boundary was costly while remaining behavioral rather than a hard
security boundary.

The accepted trade-off favors broader independent judgment with bounded discovery. Some additional
context and possible attention dispersion are the necessary cost of allowing Authors and Reviewers
to find counterevidence that a preselected packet may omit.

## Decision

Public, project-local, and shared Rule and Skill writing use one public Role Launch and discovery
runtime. Fresh Authors and Reviewers start from the supplied task, Candidate, and evidence, then
independently inspect additional repository or external material only for an applicable instruction
or concrete role need and within exact frozen grants. They do not proactively load unrelated
content or recursively follow ambient references merely because it is visible.

Visibility, discovery, tool availability, host injection, or peer transmission grants no evidence
authority. Authority continues to come only from the material's supported owner and provenance.
The private shared writer adds portability qualification, source-project evidence boundaries,
dependency closure, and representative-target obligations without replacing or adapting the
public runtime. Relevant source-project material, MCP and tool descriptions, hooks, and host
instructions may be inspected within grants, but unqualified source-project meaning cannot become
portable normative evidence.

Soft isolation, the mandatory Probe, Tool Boundary Record, `PROBE_FAILED`, and private Runner
restrictions are retired. `CONTEXT_REQUIRED` and `ACCESS_REQUIRED` remain exceptional bounded
fallbacks when a necessary fact or access cannot be obtained through the authorized discovery
runtime. Fresh identities, private independent review, precise operation grants, Role Boundary
Audit, Machine Validation, Executable Acceptance, correction, replay, and safe finalization remain.

## Consequences

The shared writer becomes a portability delta over the public writer rather than a second isolation
mode or Role Launch Interface. Author and Reviewer evidence sets may differ, increasing coverage
while accepting some attention cost and exposure to irrelevant or source-local material. Prompted
need-based discovery and owner/provenance qualification manage that risk without claiming an
isolation guarantee the host cannot provide.

This decision supersedes ADR 0010. ADRs 0008 through 0010 remain historical evidence and no longer
define current runtime policy.
