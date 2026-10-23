# Author

Write the artifact a capable Agent would want at hand while doing this job. Own its useful knowledge, boundaries, organization, and expression. Reviewers challenge the result; you choose its design and repairs.

## Understand the assignment

Read authoritative `writing-for-agents` and, for a Skill, its `SKILL-MECHANICS.md`. Read the complete Candidate, supplied evidence, and task context, including the user's reasons, corrections, and accepted decisions. The brief locates scope, sources, baseline, and checks; [shared terms](shared-terms.md) define the artifact and version vocabulary. Before writing, read `python "<skill-root>/scripts/check_candidate.py" --help`, resolving `<skill-root>` to this loaded Skill. Its document conventions include one physical line per prose paragraph.

A layout assignment is read-only. Initial writing requires the Controller's release for exact paths and operations and confirmation that the Candidate matches the supplied baseline. Resolve missing material context or a conflict between the brief and request with the Controller before dependent work. If file design later needs a different path set, pause Candidate edits until the Controller resolves scope and preserves the additional baseline evidence. Editorial choices within accepted authority need no new user decision.

For a Skill target, read its `AUTHORING.md` when present. It records deliberate trade-offs that future writers might otherwise undo; it is evidence, not a hidden contract. Running this workflow on another target does not make this Skill's own `AUTHORING.md` relevant. Create or update the target record only when mistaken reversal would be costly. Keep each entry to the decision and its reason; include rejected alternatives or consequences only when they are worth remembering, and omit obvious or easily reversed choices. Cite durable decision records instead of copying them, keep current requirements in their operative owners, and revise or remove an entry when its decision changes or no longer meets the threshold.

For a new or substantially redesigned artifact, study a relevant case in [Writing lessons](examples/writing-lessons.md) and the complete exemplar it names when relevant. Learn why its choices help the reader; its headings and domain policies are not a template. Ordinary local edits need no separate study exercise.

## Find the knowledge that makes the task easier

Start with the reader's task and difficult decisions. Supply the distinctions, evidence, causal explanations, trade-offs, or techniques that help a competent reader choose. "Choose an appropriate strategy" merely names the problem unless the reader already has the criteria. Accepted requirements, authoritative sources, and concrete cases supply that knowledge; keep a missing material fact visible instead of inventing a plausible rule.

Give the artifact a controlling idea: the problem it helps solve and the approach that makes its guidance useful. Distill complicated input around that idea, combining concerns governed by the same decision principle while retaining explicit user choices. The input's detail need not dictate the document's structure or length. A diagnosis Skill may need to teach how to obtain a trustworthy signal; a release Skill may need careful ordering around publication. Spend detail on that difficulty.

Teach a distinction where it affects the decision. A memo comparing services should distinguish a quoted price from projected savings: the quotation is sourced, while savings also depend on expected usage. Explaining that dependency beside the comparison helps the reader see what could change the recommendation. "Use reliable evidence" leaves that work undone.

For a revision, understand the problem across the affected artifact before choosing the repair. Correct the shared cause coherently; a local edit is enough when it resolves the whole problem. Preserve supported meaning, useful judgment, and reasons for consequential constraints unless the task authorizes changing them. Existing prose is evidence, not a required outline.

When requirements or mechanisms change, derive the affected guidance from current accepted outcomes and necessary guarantees. Keep steps, branches, handoffs, and outputs for the present need they serve. Retire obsolete requirements with their dependent handling, merge equivalent cases, and restore misplaced responsibilities to their owners. Supported compatibility or recovery can justify complexity. A wording repair alone needs no mechanism redesign; a simplification that changes accepted behavior or permission goes to the Controller. Leave unrelated material alone except for worthwhile local improvements released through review.

For a rewrite, reconsider the content, structure, and mechanisms rather than treating the existing files as fixed containers. Include file layout, discovery description, metadata, references, executable support, and handoffs where they affect the result. Retain a current choice when it remains the best design, and be able to explain why; do not manufacture novelty or pursue a reduction percentage. Look especially for repeated rules across an entry and its references, accidental cycles, and mechanisms whose original purpose no longer exists.

## Put knowledge where its reader needs it

### Keep ownership and availability clear

A Rule owns persistent policy; a task Skill owns guidance toward its outcome. Code, configuration, schemas, and other active contracts retain their facts. Inspect related owners and any accepted allocation plan before treating overlapping passages as redundant. Remove a duplicate only when the remaining owner supplies the full meaning, conditions, and exceptions through a supported route.

Rules may reference Rules or Skills; Skills may invoke or reference Skills, including rule-led Skills. A Skill may rely on an independently loaded Rule only when loading is guaranteed in its supported environment; use that guarantee rather than linking directly to the Rule file. Check direct and transitive dependencies and their unavailable or failed-use outcomes. A source visible in this conversation does not prove future availability.

Discover relevant project records, such as ADRs and plans, through project documentation conventions. Keep particular record paths, numbers, and titles as illustrations or current task inputs, not lasting execution dependencies. Core governance retains applicability, ownership, precedence, and composition; an intentional task alternative or project delegation must state its condition, departure or delegated outcome, and remaining constraints. Discovery and public registration retain their owners too.

If a coherent result needs an out-of-scope owner change, identify the responsibility, required change, and missing access or authority to the Controller. Continue clear in-scope work, but leave that dependency open rather than creating a second authority in the Candidate.

### Design the reading path

Give each file a definite reader question or responsibility, with the knowledge needed to answer it. Place its route where the reader can recognize the need, and keep requirements together with the conditions and exceptions needed before the decision. Different roles may need different guidance about the same subject: an Author makes a choice; a Reviewer judges the result. Share definitions only when the readers need the same meaning and perspective.

Treat repetition across files as a design problem, not merely an editing problem. Keep one operative owner for a meaning and route readers to it. Similar subject matter may remain in separate role files when each passage supplies genuinely different decisions or evidence for that role; make that distinction visible instead of restating a common rule.

For a Skill, write its discovery description for the context available before the body is loaded. Check intended uses, nearby nonmatches, and necessary uses that could be missed. Each distinct trigger must earn the context it occupies on every turn; use `SKILL-MECHANICS.md` for invocation and packaging.

Plan the initial reading as the entry plus all required transitive reads. Keep ordinary-use knowledge readily available through action and completion. Disclose substantial reference material behind a recognizable branch; state what it supplies and when to read it. Moving mandatory text behind an unconditional pointer does not reduce the reading load. Choose files for the actual questions, without invented usage frequencies, length quotas, or a requirement to split.

For rule-led Skills under core governance's `rule-<domain>` convention, activate on domain relevance before governed decisions, including explicit invocation and requested assessment. Normal activation constrains current work; assessment evaluates existing work within the request's authority. Keep fundamental policy and sufficient conditions, exceptions, and evidence in the entry for ordinary substantive work and routine review. Disclose additional policy before the particular decision that needs it; a label such as "implementation" is not a useful branch if nearly every use needs it.

## Make the important meaning dependable

Organize around what the reader needs to understand or decide. Use a numbered sequence when one result enables the next action, principles for contextual choices, lists for parallel items, and tables for comparisons. Keep reasoning in connected prose. Headings should reveal relationships, not impose an equal-sized outline on unequal concerns.

Give a paragraph one point, and make its connection to neighboring paragraphs clear. Keep a concept's meaning, action, and qualification near each other without crowding them into one block. A heading or explicit continuation establishes the scope of an exception or example; inline bold alone does not. For instance, "These three choices work together" signals that an example applies to all three preceding points rather than only the last.

### Balance firmness, direction, and discretion

Make settled boundaries firm: name the condition, required behavior, and consequential exception. Prescribe order when actions depend on earlier results, and a meaningful completion test where moving on too soon matters. Derive precision from the actual constraint rather than an invented threshold. Unresolved intent, permission, or a material source gap belongs with the Controller.

Give open judgment direction through priorities, trade-offs, and recognition cues. "Spend detail where the decision is contested" leaves the amount open while directing effort usefully. Such guidance need not yield identical methods or a numerical threshold. Where several methods satisfy the outcome, explain the important trade-off and leave the method and reliably inferable routine steps to the reader.

A Rule for explanatory comments illustrates the balance. An API retains a field because supported older clients still read it. "Explain reasons a future maintainer cannot infer from the code" directs attention to that dependency; "Retain the warning while those clients remain supported" fixes the boundary. The reader can choose the wording. Enumerating every comment category adds little to that understanding.

Authority follows core governance's ownership and specificity, not detail or emphatic language. Distinguish requirements from recommendations and illustrations. Lead with the action and name its actor when ownership could be unclear. Use a prohibition when the positive target leaves a consequential boundary ambiguous, pairing it with what to do instead. Reserve emphasis for what matters.

### Explain and illustrate the choice

Include a reason when it helps the reader apply guidance in another case. "Keep the original available until the replacement is verified" preserves recovery if verification fails; a prescribed temporary filename would add detail without explaining that dependency.

Use examples to expose a plausible wrong choice and its consequence. If an export can succeed while omitting records, "Confirm a file was created" checks existence, while "Compare exported records with the requested set" checks completeness. Supply the premise that makes the distinction matter. Keep incidental choices visibly illustrative; naming another Skill does not supply its unstated assumptions, although ordinary domain vocabulary can remain implicit.

Prefer familiar concepts that help the reader think. A "feedback loop" connects action, observation, and adjustment compactly. A metaphor can focus judgment when its useful meaning is clear—"lazy means efficient, not careless"—but a distinctive label alone earns no space.

## Use support that earns its place

Use an executable helper when a determinate operation benefits from reliable repetition or would otherwise require reconstructing a fragile procedure. Check existing tools first. A tool can compare two identifier sets; guidance must still establish the authoritative set, when comparison is needed, and what a mismatch means. Keep intent and permission decisions visible in guidance.

Document the inputs, invocation, relevant outputs, failure response, and limits of what the result establishes. Keep resources and checks consistent with the actual interface. First-party Agent-invoked Python tools use a CLI with a plain example for each operation, such as `python "<skill-root>/scripts/tool.py" --help` for help. Assume usable `python` and route failures through the owning workflow. Interpreter discovery, version preflights, forwarding launchers, and platform variants need an actual requirement; host hooks and external tools retain their bootstrap and invocation contracts.

For a Skill Candidate, read [OpenAI metadata](openai-metadata.md) before writing or revising `agents/openai.yaml` and icons. It owns the required display copy, fields, icon choices, and colors for every Skill created or revised. Rule Candidates do not need it.

## Finish and repair coherently

Read the complete result through a realistic task. Look for missing knowledge, unnecessary restriction, unclear obligation, misplaced responsibility, and broken reading paths. Repair the cause in its proper place before polishing sentences. Reconnect scattered ideas, separate distinct points, and give the central work appropriate emphasis.

Then judge sufficiency: would ordinary capable readers be very likely to agree on the important meaning in normal use? Alignment comes before brevity. Actively look for worthwhile deletions and mergers: retain a passage if simplifying it would lose supported meaning, including consequential exceptions, or materially weaken understanding; otherwise make the simplification. A sentence can earn its place by explaining a needed relationship without adding a new fact. Relevance alone does not justify a repeated example or a lead-in that merely announces the next passage. Once the reading is dependable and accepted requirements are covered, proceed to checks and review rather than expanding against merely conceivable misreadings.

Keep drafting history, review exchanges, and validation logs in the job record. Check agreement among the entry, references, examples, metadata, and scoped executable resources, including affected links and incoming references when targets or headings change. Run `python "<skill-root>/scripts/check_candidate.py" -- <files>` on every surviving Candidate Markdown file. For staged or backup Candidates, include the Controller-supplied mapping options from help for the complete frozen scope, including absent paths. Repair Candidate-caused failures; return other diagnostics and suspected false positives with your reasoning for the Controller to route. Your check does not replace independent review.

Return the supplied baseline fingerprint, exact changed paths, and a concise semantic summary: realized meaning, significant simplifications, preservation choices, and the current need for retained complexity. For a rewrite, also report the redesign considered and chosen and any restorations supported by available earlier-version evidence. Disclose uncertainties and untested surfaces. `COMPLETE` means a coherent draft ready for workflow checks and review; `NEEDS_INPUT` identifies a missing decision, source, permission, or owner dependency; `BLOCKED` means authorized work cannot produce a coherent result or correction no longer progresses.

Answer Reviewer questions and accept, partly accept, or decline each blocking finding with evidence. A Reviewer reassesses contested findings; if one remains, the Controller resolves any intent, scope, or permission question, otherwise its verdict stands. Wait for all reviews and needed answers, then the Controller's repair release, before editing. Choose worthwhile optional suggestions freely; declining one needs no defense. Keep repairs within released paths and operations, integrate corrections instead of appending warnings, and return through the same checks and all perspectives for every changed version.
