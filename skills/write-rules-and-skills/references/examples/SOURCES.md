# Sources for the Writing Examples and Lessons

These sources inform the teaching cases; their domain policies are not incorporated into the
authoring contract. All material needed to read the lessons is included locally. The source URLs
identify provenance and are not runtime reading requirements.

## Matt Pocock

Source: `mattpocock/skills`, `v1.2.3`.

https://github.com/mattpocock/skills

Source paths inspected in the source distribution:

- `skills/engineering/diagnosing-bugs/SKILL.md`
- `skills/engineering/tdd/SKILL.md` and `tests.md`
- `skills/engineering/prototype/SKILL.md`
- `skills/engineering/codebase-design/SKILL.md`
- `skills/productivity/writing-for-agents/SKILL.md`

`elegant-procedure-led-skill.md` adapts the feedback-loop construction and simplification ideas
from `diagnosing-bugs` into a narrower, standalone reproduction task. It changes wording, removes
the broader diagnosis/fix workflow, and retains task-bound execution rather than importing all
upstream thresholds, gates, or tool choices. `writing-lessons.md` discusses that adaptation and the
paired-example and question-led organization techniques in `tdd` and `prototype`. The decision-memo
example is original teaching material, not an upstream Skill copy.

```text
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## DietrichGebert

Source: Ponytail.

https://github.com/DietrichGebert/ponytail

Upstream revision: `e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156`.
Source path: `skills/ponytail/SKILL.md`.

Inspected version: SmartKit's checkout-authoritative adaptation of that source, including the
local `vendor/patches/ponytail/ponytail.patch` changes. `writing-lessons.md` quotes its opening posture
and confirmed-requirements boundary and summarizes its decision ladder. It does not establish
Ponytail's coding policies for other artifacts.

```text
MIT License

Copyright (c) 2026 DietrichGebert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
