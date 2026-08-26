# Project Contracts

Strength: `Mandatory`

Scope: Validity of changes to capability ownership, target installation, documentation, evaluation,
contract evolution, distribution, and hard dependency or exposure boundaries.

A project change is valid only while every affected capability has one canonical owner and every
derived, delivered, or installed surface remains inside the contracts below. `AGENTS.md` owns this
Rule's activation, and the Plugin Rule Configuration owns precedence. If current evidence cannot
select the required owner, route, or outcome, stop before modifying or delivering the affected
surface.

## Canonical Ownership and Delivery

- Treat each plugin capability registry and its declared source as canonical. Generated host
  adapters and delivery surfaces remain outputs of their declared synchronizer or renderer; they
  neither acquire policy ownership nor become independent edit points.
- Treat an MCP adapter as host configuration, never as a vendored server implementation.
- Treat lock-declared external Skill snapshots as updater-owned, pinned, read-only plugin
  capabilities. Their provenance, selected content, licenses, and integrity records remain in the
  external-source lock and its owning updater.
- The setup catalog owns target selection, generation and delivery routing, and managed
  configuration. Its blueprints and templates are generation inputs, not target runtime content or
  proxies for another workflow's outputs.
- The setup control plane owns setup mechanics; canonical target inputs or generated target content
  own target-specific policy.
- Deliver capabilities only by their declared direct-host or setup-managed route; a generated
  adapter grants no delivery authority, and setup-only adapters reach targets only through
  catalog-managed setup.

## Target Installation Ownership

- Preserve `.agents/` as the target installation root across public setup prompts, templates,
  manifests, scripts, and documentation.
- Treat target-owned Rules, Skills, Agent sources, and typed capability configuration as canonical
  project inputs. Setup may manage only catalog-selected public assets, declared generated outputs,
  wrappers, configured external Skill installations, and rendered structured fields; it must
  preserve canonical inputs, unrelated structured fields, sibling entries, and secret values.
- Use `.agents/smartkit.lock.json` as the sole authority for setup-managed files, trees, structured
  fields, and external-source metadata. The managed `## Project rules` section of `AGENTS.md` is the
  only compositional exception: replace that section through the next level-one or level-two
  heading while preserving all surrounding content and keeping the file outside whole-file
  ownership.
- On first adoption, claim only a missing target or one whose deterministic digest matches the
  desired content. On later runs, begin planning only after verifying every recorded asset digest;
  validate external-source metadata against the configured selection and validated snapshot. An
  unowned conflict or modified owned target stops the run before any target write.
- Setup may delete only a previously owned file, tree, or field, or a descendant of a previously
  owned tree, when it is absent from current desired state; historical names do not belong in the
  catalog.

## Exclusive and Private Owners

- `setup-matt-pocock-skills` exclusively owns Matt repository context, including its project
  documentation and entry-file pointer block. The project-agent setup workflow may verify that
  context exists and may read through and reproduce the unchanged pointer block only while
  preserving surrounding `AGENTS.md` content; its catalog, generation requests, renderers, and
  ownership manifest must not interpret, author, claim, or separately deliver Matt outputs.
- Keep recommended-tool Hook executables private under `runtime/recommended-tools/` and without a
  discoverable `SKILL.md`; keep their authoritative declarations under
  `policies/recommended-tools/`. Keep MCP readiness beside its Plugin or Project MCP declaration and
  interpret it through the same private runtime only after the project, host, and local-day gates
  pass. Setup must not copy these private runtime or policy assets into a target.
- Keep shared generation inputs under `setup-assets/` and the setup control plane under
  `skills/setup-project-agents/`. In production, only the recommended-tool Hook and maintenance
  pipeline consumes its private runtime and policies; the setup control plane consumes setup assets.
- Keep `write-setup-authoring-contracts`, `write-shared-rules-and-skills`, and
  `translate-agent-artifacts` project-private under `.agents/skills/`. The first exclusively authors
  setup blueprint contracts; the second exclusively owns source-context exclusion and portability
  qualification for shared SmartKit Rule and Skill candidates; the third exclusively updates
  required Simplified-Chinese documentation mirrors from final English sources. None enters plugin
  Skill registries, root plugin manifests, setup catalogs, or target installation.

## Documentation Contracts

- Keep `README.md` and `README.zh-CN.md` limited to public installation, configuration, use, and
  troubleshooting. Contributor workflows, release and generation mechanics, maintenance,
  architecture, validation internals, and implementation details remain with their project or code
  owners.
- Treat English first-party Rules and Skills as the sole canonical semantic sources. The project
  documentation owner selects which of them require mirrors. Each selected source at `<path>` maps
  to `docs/zh-CN/<path>`. After `write-rules-and-skills` completes for all affected sources, the
  hosting Agent invokes `translate-agent-artifacts` once to update the complete affected mirror set.
- Treat `docs/zh-CN/` as documentation only, never as a runtime source, plugin entry point, setup
  input, or target-installation asset.
- Translation preserves the English source's block and Markdown structure, literals, complete
  meaning, and emphasis while using plain, idiomatic Simplified Chinese. Translation content and
  readability checks remain normal documentation validation; they do not enter the English
  authoring workflow or executable Acceptance.
- Treat `.agents/rules/` as this repository's development-policy source. Keep this repository's
  `.agents/` content limited to local plugin configuration, Rules, and the three declared
  project-private Skills; it is not a generated target-project snapshot.
- Treat `CONTEXT.md` and `CONTEXT-MAP.md` as unstable, non-normative conversational glossaries.
  They may help interpret or explain language in direct user communication. The sole artifact
  exception is `translate-agent-artifacts`, which may consult `CONTEXT.md` as a nonnormative wording
  aid while treating final English as the only semantic source. Rules, Skills, Setup Authoring
  Contracts, code, tests, schemas, and configuration must not use context documents as evidence,
  terminology authority, validation or Acceptance input, or runtime dependency. Translation may
  not use them to add, change, disambiguate, or resolve English meaning. Every durable term requires
  an independent accepted source.

## Evidence and Acceptance

- Use machine checks for structured configuration, schemas, identifiers, registration and resource
  relationships, generated outputs, filesystem effects, state transitions, and process exits.
  Natural-language meaning and wording quality require whole-artifact Quality and Correctness
  Review and any required executable Acceptance. Prose snapshots, keyword checks, physical line
  wrapping, complete heading inventories, or similarity to an external exemplar are not semantic
  evidence.
- Give Correctness Reviewers the complete accepted user-decision context and every preserved
  obligation, including when the candidate changes an authoring or review standard. Use that same
  evidence basis in that case, and do not let a candidate redefine, narrow, or semantically weaken
  the requirements used to judge it. ADRs remain decision records rather than runtime policy.
- A material requirement or candidate change invalidates every earlier Quality, machine,
  Correctness, or Acceptance result that could depend on it. Return to the earliest invalidated
  passed stage; retain evidence only when the change cannot affect what it proves.

## Current Contract

- Implement, document, test, and validate only the current SmartKit-owned contract. Removing a
  path, identifier, schema, command, configuration field, or behavior removes its implementation,
  documentation, tests, and handling in the same change.
- Retired SmartKit-owned contracts receive no aliases, deprecated branches, migrations, shims,
  fallbacks, dual-read or dual-write behavior, or version translation. Former inputs are
  unsupported and may fail current validation; tests and documentation must not preserve them as
  executable or normative surfaces. Do not rewrite updater-owned external snapshots to enforce
  this policy; their upstream owner remains authoritative.
- Treat ownership checks, data-integrity checks, transactional rollback, and safe offline behavior
  as current correctness requirements, not compatibility mechanisms.

## Distribution and Dependency Direction

- Rules may name or invoke Skills. A Skill or Setup Authoring Contract may require the applicable
  project or repository policy for a governed concern, but it must discover that policy by concern
  rather than name, link to, or assume a specific Rule ID, title, path, or numbering.
  `setup-project-agents` and its owned implementation are the sole exception, limited to
  discovering, generating, preserving, and validating declared Rule targets.
- Distribution is one-way: target changes have no reverse path into plugin runtime assets,
  canonical sources, or documentation.
- Limit the recommended-tool runtime's production dependencies to its authoritative policy
  declarations, Plugin MCP registry, optional target capability configuration, and the Python
  standard library. Neither setup assets, private runtime or policy areas, nor Plugin Hooks may
  depend on plugin-discovered or vendored Skills.
- Catalog-managed external Skills enter targets only through setup.
- Plugin manifests expose declared public surfaces only.
