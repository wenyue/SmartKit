# Quality 与 Correctness 审查合同

本合同负责 Quality 与 Correctness 判断、finding、coverage 证明和裁决。穷尽检查证据与完整 Candidate，同时独立选择普通遍历和质询方法。

Reviews 负责下述准确的 Quality 与 Correctness 拓扑和视角；Role Runtime 负责身份的新鲜度、持续、重新打开与终止。所有 Reviewer 均为只读，彼此独立且独立于 Author。他们检查所提供指纹上的完整 Candidate，并可在授权内发现反证。他们返回有支持的 finding，而不是偏好或替换文本。

只有真正非阻塞的观察超出 Reviewer 的视角或裁决权威时，才将其分类为 deferred surface。它既不是 finding，也不是证明，不改变当前裁决。可能阻塞的跨视角问题不能延后：返回一项非语义检查请求，只包含 Candidate 位置、目标所属视角与指纹，不包含推理、评估或结论。该请求既不是 finding 也不是证据；在所属视角独立检查该位置前，证明不能关闭。只有 Role Runtime 负责传输、身份处理与保留；不存在语义同级通信边。

## Quality

Quality 恰好有两名 Reviewer。

### Q1：当前状态质量

Q1 负责完整当前 Candidate 的信息架构、经济性、语言和执行可用性。把每份资源和每条重要路径作为一个 package 检查。

判断加载与首次需要时的披露、位置与共同定位、语义归属、重复、散落、陈旧缓存、膨胀、维护接缝、术语、力度、歧义、分支可见性、权威、依赖、可观察完成、受阻、失败、恢复与停止出口。寻找能够保留受支持行为的最小结构与措辞。后果性复杂度不是经济性缺陷。

Q1 只提出当前状态主张。不能仅凭 baseline 差异推断回归。
当有支持的 Q1 finding 确立了实质性膨胀时，修正会调用 Author 的停写、报告与用户确认 Gate，而不是普通自主修复。

### Q2：变更完整性

Q2 负责 baseline-to-current Change Integrity。检查完整 baseline、完整当前 Candidate、可读 delta、已接受保留约束和 Author Change Summary。

判断每项删除、改写、移动、合并和新增是否保留有支持含义，是否产生无关 churn、丢失限定或上下文、降低加载或共同定位质量、产生由变更造成的碎片化或重复，或者造成清晰度、可用性或可维护性回归。baseline 与 Author summary 可以定位和解释变更，但没有治理权威；finding 必须有已接受证据和当前有支持的缺陷。

Q2 还检查判断每项 delta 所需的未变当前上下文。如果某项关注只能由当前状态支持，则超出 Q2 裁决范围，并遵循上述跨视角路径。

### Quality 返回

每名 Reviewer 都返回一份简洁的全 Candidate coverage 证明，其中指出：

- 已检查的全部 Candidate 路径；
- 在完整 Candidate 上应用的视角；对于 Q2，还包括完整 baseline-to-current 变更；
- 有支持的 finding；以及
- 未测试、不确定、无法访问或有意排除的表面。

不要求逐行清单、economy-unit 记录、不透明 coverage 标识、资源行 schema 或机械 coverage manifest。

只有不再有自己负责的 critical 或 material finding，且自己负责的每项 advisory 都已有 Author 处置时，Quality Reviewer 才通过。Q1 或 Q2 视角内的每项有支持主张（包括 advisory）都是 Evaluation 下的 finding，不能延后。只有 Q1 与 Q2 各自独立地在同一指纹上 PASS，Quality 才通过。修复后，两名 Reviewer 根据 Role Runtime 的身份生命周期复查完整 Candidate。

## Correctness

Correctness 恰好有一名独立 Reviewer。它在完整 Candidate 上结合三项职责：

- Spec Fidelity and Semantic Integrity：在已接受权威与 Candidate 之间双向追踪每项已接受义务、处置、实际生效的承诺、Owner、适用条件、依赖和证据路径。
- Preservation and Regression Integrity：把 baseline 含义与完整 delta 追踪到已接受的当前结果；检测未经授权的语义丢失、弱化、无支持处置，或加载与适用性破坏。
- Critical Behavioral Integrity：遍历每条关键路径和代表性路径，包括实质不同的同时触发条件、决策、依赖、权限、外部影响、验证、失败、恢复、路径中途停止和可观察出口。

只有 Quality 在同一指纹上达到当前关闭后，Controller 才启动 Correctness。该关闭状态是启动 Gate metadata，不是 Correctness 证据；不会把任何 Quality 裁决或工作提供给 Reviewer。Reviewer 根据已接受义务、baseline、delta、代表性路径与治理证据，独立检查完整 Candidate。

Correctness 只返回 critical blocker，并为每项 blocker 写明不可容忍场景和有界修复方向。非 critical 改进超出其裁决范围，遵循 deferred-surface 路径。

其返回包含 PASS 或 BLOCKED、当前指纹、critical blocker、一份简洁证明，说明三项职责已覆盖完整已接受义务集合、baseline/delta 和代表性路径，以及每个未测试、不确定、无法访问或被排除的表面。PASS 要求不存在 critical blocker。修复后，Correctness 阶段根据 Role Runtime 的身份生命周期，在新指纹上重复完整的组合审查。
