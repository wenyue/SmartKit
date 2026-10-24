# Authoring Decisions

## Follow identity instead of spelling

Keep discovery tied to a confirmed symbol or tracked path and its supported binding evidence. Broad text replacement can silently rename unrelated homonyms, while lexical search alone can miss dynamic, generated, cross-language, or case-sensitive path uses. The workflow permits different discovery tools but fixes what their evidence must establish.

## Keep compatibility and correction choices distinct

An externally observed name needs an accepted compatibility decision before writing. Once identity, behavior, scope, and compatibility are settled, routine repairs such as qualification or an import alias can use engineering judgment. Conflating these choices either invents compatibility policy or forces unnecessary approvals for equivalent local methods.
