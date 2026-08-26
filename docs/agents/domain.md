# Context Documents

This page is nonnormative explanatory guidance. The applicable project Rule owns context-document
use, evidence, and exceptions; accepted ADRs own their recorded decisions.

## Conversational role

Context documents are unstable, nonnormative conversational glossaries. Their policy-governed role
is helping an Agent interpret or explain language while communicating directly with a user. A root
`CONTEXT.md`, entries linked from `CONTEXT-MAP.md`, and files under `contexts/` are examples of this
material. Their absence simply means that no conversational glossary is available.

## Evidence boundary

Under the governing project Rule, context documents are not normative evidence, terminology
authority, validation or Acceptance input, or a dependency for Rules, Skills, Setup Authoring
Contracts, code, tests, schemas, or configuration. Durable meaning instead comes from an independent
accepted source such as a user decision, Issue, Spec, ADR, governing contract, or observable
implementation evidence.

## Maintenance and ADR relationship

Maintenance can keep a context document internally coherent without promoting it into a normative
source. Accepted ADR authority comes from the repository's decision-record contract rather than a
context-document link. Any conflict is therefore evaluated under the governing project Rule and
the accepted ADR, not this guide.
