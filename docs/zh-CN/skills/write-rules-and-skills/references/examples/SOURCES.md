# 写作示例与讲解的来源

这些来源为教学案例提供参考；它们的领域政策没有纳入编写契约。阅读讲解所需的全部材料都已包含在本地。来源网址用于标明出处，并非运行时必须阅读的内容。

## Matt Pocock

来源：`mattpocock/skills`，`v1.2.3`。

https://github.com/mattpocock/skills

在来源发行版中阅读过的路径：

- `skills/engineering/diagnosing-bugs/SKILL.md`
- `skills/engineering/tdd/SKILL.md` 和 `tests.md`
- `skills/engineering/prototype/SKILL.md`
- `skills/engineering/codebase-design/SKILL.md`
- `skills/productivity/writing-for-agents/SKILL.md`

`elegant-procedure-led-skill.md` 将 `diagnosing-bugs` 中构造和简化反馈回路的思路，改编为范围更小、独立完整的复现任务。它重写措辞，去掉更广的诊断与修复流程，让执行受当前任务约束，而没有引入上游的全部阈值、门槛或工具选择。`writing-lessons.md` 讨论这项改编，以及 `tdd` 和 `prototype` 中成对示例和按问题组织内容的技巧。决策备忘录示例是原创教学材料，不是上游 Skill 的副本。

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

来源：Ponytail。

https://github.com/DietrichGebert/ponytail

上游版本：`e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156`。
来源路径：`skills/ponytail/SKILL.md`。

阅读的版本是 SmartKit 当前检出中具有权威性的改编版本，包含本地 `vendor/patches/ponytail/ponytail.patch` 变更。`writing-lessons.md` 引用了其开篇工作姿态和保护已确认要求的边界，并概述决策阶梯。它没有让 Ponytail 的编码政策成为其他工件的政策。

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
