# Writing Lessons

These cases explain choices in finished guidance. Read the case that addresses your writing
difficulty, including its complete exemplar where named. The quoted passages and examples are
illustrations, not additional policy for the artifact you are writing. Their topics, headings,
length, and voice are not templates. Adapt the underlying choice to the reader's actual task.

Source identities, adaptation notes, and retained license notices are in [SOURCES.md](SOURCES.md).
The excerpts and local examples supply the teaching material; reading upstream is not required.

## Combine direction with a firm boundary

Ponytail opens with a posture:

> You are a lazy senior developer. Lazy means efficient, not careless.

It then gives a decision ladder: question the need, look for an existing solution, consider the
standard library and native platform, and only then write the minimum code that works. The posture
and ladder reinforce each other. "Lazy" makes an ordinary concern memorable; the ladder shows where
to look for less work. Neither needs to enumerate every future programming problem.

Ponytail applies that simplification advice within a settled boundary:

> Preserve confirmed requirements and observable behavior. Discuss and wait for the user's decision
> before reducing a confirmed feature, changing visible behavior, or introducing an important cost
> tradeoff.

The lesson is the combination. The reader has direction for open choices and a definite boundary
where that direction could be over-applied. Turning the posture into dozens of mandatory checks
would lose its range; leaving only the posture would invite a reduced result. The persona earns
its place by focusing a useful habit. It is not a reason to add a persona to every Rule.

For a self-contained policy case, read [Generated Files](elegant-rule.md). Its strong requirement is
agreement between owned sources and generated output. It leaves the generator and verification
method with the repository because those facts vary. The Rule is definite about the result without
pretending to know each environment.

[Documentation Links](elegant-rule-led-skill/example.md) shows the same policy role in a model-invoked
rule-led Skill entry, with deeper knowledge disclosed for actual target changes. The entry is
presented here as ordinary Markdown teaching material so it remains part of this lesson rather
than becoming an independently discoverable Skill.

## Spend detail on the part that needs judgment

In Matt Pocock's diagnosing-bugs Skill, the most developed part is obtaining a feedback loop that
can expose the reported bug. It supplies ways to construct a loop, ways to tighten it, and a way to
recognize a usable signal. The other phases can consume that signal; without it, a tidy sequence of
phases would offer little help. The emphatic direction to spend disproportionate effort there has
a specific object and a causal reason.

Read [Reproduce a Symptom](elegant-procedure-led-skill.md), a shorter adaptation of that part. Notice
where it is exact: run the reproduction, distinguish the reported failure from a setup error, and
rerun after simplification. Those actions connect the result to evidence. Notice where it leaves
room: choose a test, request, command, or harness according to the symptom. The choice is open, but
the examples explain what makes one choice better than another.

"Make the loop faster" and "make the loop reliable" could conflict. The intermittent-failure
paragraph and the race example preserve the reason for the loop while guiding optimization. A
universal runtime cutoff would look more precise while being less faithful to the task. This
adaptation does not reproduce the upstream diagnosis workflow or import all of its gates.

## Teach a distinction through a pair of cases

In Matt Pocock's TDD examples, checkout is the public operation. One test checks whether its
internal payment service was called; another checks whether a valid cart produces a confirmed
checkout result. The latter checks what the caller receives. A refactor could replace the payment
helper while preserving that result, making the first test fail without a behavior regression.
The contrast teaches what "test behavior" means, beyond the incidental API names.

Apply that technique to the [Decision Memo](elegant-principle-led-skill.md). Two plausible instructions
about an uncertain cost comparison illustrate a useful choice:

> Score each service for price, reliability, and ease of migration, then recommend the highest total.

> Compare the differences that could change the decision. If a lower price depends on forecast
> usage, show when that advantage disappears; if migration is hard to reverse, give that uncertainty
> more weight in the explanation.

The first is useful when agreed scales and weights already express the decision-maker's priorities.
Without those, its precision can hide arbitrary judgments. The second names evidence and trade-offs
while allowing a table, calculation, or prose. It guides work that cannot yet be reduced to a score.
The better choice depends on the task, not on a universal preference for prose over numbers.

The complete exemplar also puts evidence, inference, and assumption beside a single price example.
That makes their relationship visible: a sourced input does not make every conclusion drawn from it
certain. A good example supplies a distinction the reader can use elsewhere; commentary should make
clear which details carry it.

## Let the reader's question shape the document

Matt Pocock's prototype Skill separates two questions: whether a state model works as intended,
and what an interface should look like. For the first, an interactive walkthrough lets the user
exercise transitions and see what state follows each action. For the second, switchable interface
variations let the user compare appearances. The questions need different artifacts and knowledge,
so the entry helps select a branch before loading its details. The split is useful because of the
work being done, not because a Skill should have a certain number of files.

Compare the two complete exemplars above. A decision memo is organized around choosing and
explaining; its writer can discover a missing assumption while drafting any section. A reproduction
has necessary order: simplification is informative only after a failure has been observed, and
the handoff depends on what was actually run. Numbering fits the latter relationship. Adding phases
to the memo would not create an equivalent dependency.

Paragraphs can separate questions even when no new branch or file is needed. Under "Make it useful
to run again," the reproduction exemplar first explains what can be removed, then how to validate a
removal, then how to treat intermittent failures. They belong under the same heading, but each
paragraph gives the reader a distinct concern to consider. Combining them into one block would
obscure those changes of focus without reducing the knowledge the reader needs.

Both examples retain room for ordinary skill. They specify enough to expose the hard choices and
recognize the intended result, then let the reader supply routine method. Their usefulness does not
come from maximizing either detail or brevity.
