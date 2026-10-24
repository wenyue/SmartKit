# OpenAI Metadata

Write `agents/openai.yaml` so a person who understands their task but is unfamiliar with the Skill can recognize its purpose, choose it confidently, and begin a useful request. The display name establishes identity, the short description supplies selection cues, and the default prompt demonstrates a supported use.

For every Skill created or revised through this workflow, include nonempty `interface.display_name`, `interface.short_description`, `interface.default_prompt`, `interface.icon_small`, `interface.icon_large`, and `interface.brand_color`. These are this workflow's authoring conventions: the platform permits some of them to be optional. Metadata does not guarantee when a client displays or inserts a prompt, and a default prompt does not change invocation policy. The [OpenAI field documentation](https://learn.chatgpt.com/docs/build-skills#optional-metadata) and [metadata validation reference](https://developers.openai.com/plugins/deploy/submission-errors#skill-agent-metadata-errors) document the platform fields.

## Write copy that helps selection and use

Write `display_name` as a short, natural English title that mainly follows the Skill's own name, with an obvious correspondence between the two. Preserve proper-name tokens in their original form and an explicitly specified display title verbatim. Improve spacing and capitalization where useful; explain an abstract name through the description rather than inventing a different identity.

Write `short_description` in Simplified Chinese as exactly one concise sentence. Within that boundary, prioritize the task or result that helps the reader choose; add a useful occasion or distinction when it fits naturally. Ground the copy in actual supported behavior, rather than mechanically translating the title or listing internal roles and steps. When similar Skills could be confused, favor the difference that changes which one the user should select.

For example, two code-review Skills need different selection cues: “审查代码改动的逻辑、安全性和复杂度，找出影响实际使用的问题。” describes technical quality, while “检查代码改动是否符合项目规范和原始需求。” describes standards and specification alignment. The distinction helps selection without forcing every description to list all review dimensions.

Write `default_prompt` for every Skill, including Rule Skills and background helpers. Use a concise Simplified-Chinese request containing the literal `$` followed by the Skill's actual name, normally in one sentence. Express a typical supported task and leave unknown facts with the user: “使用 $write-rules-and-skills，将我提供的要求整理成一份可执行的 Agent 规则或技能。” demonstrates an authoring request without inventing its subject or requirements. For a Rule Skill or helper, express its supported application or assessment rather than inventing a separate user workflow. A prompt is a starting request, not a substitute for the Skill's instructions or required inputs.

## Give every Skill a usable icon

Choose the icon by the Skill's actual role. Rule Skills that supply domain policy may share a shield; other helpers normally not actively invoked by users may share a gear. Every other Skill needs a dedicated graphic related to its purpose, distinguishable by its shape rather than a recolored shared symbol. Determine these roles from the supported task and intended users; `allow_implicit_invocation` alone does not identify a background helper.

Use a uniform simple line style, transparent background, and self-contained SVG without external image or font dependencies. Keep the same motif in the small and large icons, with legible strokes and shapes at both sizes. A scalable SVG can serve both fields; separate variants may simplify detail for small displays while preserving the motif. Follow explicit project visual requirements when they supply a different style or palette.

Reuse an existing suitable asset when it meets these requirements; otherwise create one. This Skill packages reusable shields and gears at `assets/rule.svg` and `assets/background.svg`, relative to its own root. Copy the selected shared asset into the target Skill's own `assets/` directory. Keep dedicated icons there too, and point both icon fields to real local files using paths relative to the target Skill root, such as `./assets/icon.svg`, rather than to this authoring Skill, an installed cache, or a remote URL. Local copies keep independently distributed Skills complete.

When the required asset, source, or creation capability is unavailable, report the exact missing prerequisite to the Controller under the existing workflow. Mandatory icons cannot be silently omitted, replaced by nonexistent paths, or treated as complete while the dependency remains open.

## Use three colors consistently

Follow explicit project visual requirements where supplied; otherwise use this global default palette for `brand_color` and the icon's line color. Classify Rule Skills and background helpers first, then choose by the other Skill's primary purpose. A mixed-purpose Skill gets the color of its central job, rather than a new color for every secondary activity.

| Primary role or purpose | Color | Hex value |
| --- | --- | --- |
| Rule Skills and background helpers | Slate | `#64748B` |
| Understanding, research, planning, diagnosis, and review | Blue | `#2563EB` |
| Writing, creation, implementation, setup, maintenance, and publishing | Green | `#15803D` |

Colors provide coarse recognition, not invocation permissions or risk levels; dedicated shapes distinguish the individual Skills. Retain a consistent category across revisions unless the primary purpose or governing project requirements change.

## Preserve behavior and check the complete package

Revise display metadata and assets without discarding existing `policy`, `dependencies`, or unrelated and unknown fields. Preserve supported invocation settings and dependency declarations unless their change is independently authorized. Display copy must describe the Skill that exists, not imply capabilities or permissions that its body does not provide.

The following example shows the required fields for this authoring Skill; other Skills need their own copy, classification, and packaged asset:

```yaml
interface:
  display_name: "Write Rules and Skills"
  short_description: "设计、编写并验证一份可供 Agent 使用的规则或技能。"
  icon_small: "./assets/write-rules-and-skills.svg"
  icon_large: "./assets/write-rules-and-skills.svg"
  brand_color: "#15803D"
  default_prompt: "使用 $write-rules-and-skills，将我提供的要求整理成一份可执行的 Agent 规则或技能。"
```

Before handoff, check the complete package:

- **Metadata:** the YAML parses, all six required fields are nonempty strings, the default prompt names the actual Skill, and `brand_color` is a six-digit hexadecimal color.
- **Assets:** resolve each icon path from the target Skill root and confirm its packaged file opens. Inspect the artwork at small and large sizes for transparency, legibility, and an appropriate motif.
- **Copy:** read it against the Skill's actual behavior, checking the one-sentence description and useful starting request.

Run the owning workflow's required checks. Format checks alone do not establish copy quality or visual usefulness.
