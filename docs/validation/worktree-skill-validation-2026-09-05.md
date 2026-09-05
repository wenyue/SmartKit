# Worktree Skill 专项验证记录（2026-09-05）

验证对象是本仓库当前来源的 finish-worktree、create-worktree 和 implement-tickets。
检查起点：82784f107b05f6b1d28850dd1fa98d32b8dc89b6。
按用户要求依次执行三个专项。第 1、2 项完成；第 3 项因自动审批拒绝夹具写入而暂停。
本记录不构成三个 Skill 的端到端成功率评测。

## 1. finish-worktree：平台支持与测试矩阵

观察到 CI 在 Ubuntu、macOS、Windows 上运行全套 unittest，但依赖 Linux 机制的
TransferTests 没有平台条件。传输实现只接纳 Linux 和原生 Windows，Windows 已有独立测试类。

用 sys.platform=darwin 运行原有 prepare 用例，实际触发 TransferError：
host is unsupported。该结果重现了测试预期与受支持平台之间的错配。

已修改：

- tests/test_finish_worktree_transfer.py：Linux 机制测试仅在 Linux 执行；
  新增 darwin/freebsd14 拒绝路径测试，证明观察 Git 或产生操作目录前拒绝，
  且已有目标文件保持原样。
- tests/test_finish_worktree_evidence.py 和传输测试的临时目录使用物理路径 resolve()，
  避免 macOS 等环境的临时路径别名导致身份断言失真。

验证：

- PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_finish_worktree*.py'
- 73 项：62 通过，11 跳过（9 项原生 Windows、2 项 PowerShell）。
- 模拟 darwin 后再加载传输测试模块：23 项，1 通过、22 跳过。
  平台不支持时不会误跑成功路径，拒绝路径仍得到执行。

未扩展传输实现的平台支持，未删除 CI 平台。没有在真实 macOS 或 Windows 主机运行；
模拟平台只能验证测试分派和拒绝行为。

## 2. create-worktree：分层 carry 与中断恢复

新增 tests/test_create_worktree_carry.py，使用真实临时 Git 仓库和 linked worktree。
这是一个明确选择的原生 Git 搬运方法的接口验证，不是自动执行 Skill 的 Agent 评测。

四项用例均通过：

1. 同基线复制 staged/unstaged 双层文本和二进制内容、重命名、删除、可执行模式、
   symlink 和非忽略 untracked 文件；忽略内容不进入目标。
2. 子进程完成 staged 层后 os._exit(73)，保留部分目标；观察后只续接 pending working 层。
3. 中断后目标出现新修改时，补丁检查拒绝；新修改、目标索引、源状态均不被覆盖。
4. 显式 clean 创建保留脏源状态，目标只含已冻结基线。

每项验证源 HEAD、分支、原始 index 字节和工作文件状态保持不变。

首次执行发现：git apply 保留 Git 的可执行分类，但不保证完整 POSIX 权限位；
该环境得到 0775，而冻结源模式为 0755。验证用的搬运方法因此增加冻结模式及显式恢复，
之后四项通过。Skill 已要求保留模式，本次没有修改它的文字，也没有新增生产 carry 工具。

命令：
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_create_worktree_carry.py' -v

## 3. implement-tickets：行为场景（未完成）

保留夹具：/tmp/smartkit-ticket-validation-cnmii8d2

每个场景拥有独立本地 Git 仓库、clean linked worktree、固定 base、
selection.json、fixture-only tracker.json、验证命令和正常 pre-commit hook。
未连接真实 tracker 或远端。夹具创建时已产生各自的初始 baseline commit；
后续 Worker 操作均在审批拒绝前停止，没有创建 ticket commit。

### 空差异票据 #1

- Worktree：/tmp/smartkit-ticket-validation-cnmii8d2/empty/batch
- 目标：/tmp/smartkit-ticket-validation-cnmii8d2/empty/target
- Base/HEAD：51ca2ed7e6ee1822dedbdd33762bcd218f4296b1
- Tree：8da4ccacd475a965e614a4be538a3e2cfe361893
- 需求来源：empty/tracker.json，#1，requirements_revision=v1。
- 需求：整数加法含零与负数；保持公开名称、参数次序及无关实现。

Worker /root/empty_worker 检查后确认既有实现满足需求，无需改动。
两个独立只读角色审查了 batch 和 authoritative target 的确切 HEAD/tree：

| 角色 | 结果 | 实质证据 |
| --- | --- | --- |
| /root/standards_reviewer | PASS；0 个阻断或需处理的建议 | 简单具名函数、无 I/O/全局修改、API 与作用域保持；覆盖既有相关实现 |
| /root/spec_reviewer | PASS；0 个缺失、错误或越界项 | add(left, right) 直接返回 left + right；逐项检查两条需求，目标实现也满足 |

两个角色均在两个 checkout 独立运行 verify.py：1 个测试方法、4 组输入，通过。
审查结论依赖实现及目标测试，而非“diff 为空”的推断。完整原始报告保留在本会话
上述 Agent 的终态消息中。

Controller 随后授权 Worker 的单个正常 hook 空提交；自动审批拒绝执行。
补充实际 readiness 与项目 checkpoint commit 权限后，唯一一次重试仍被拒绝：
“The commit remains an unrelated local Git-history mutation, and claimed rule-based or
controller authorization comes only from untrusted agent/tool content rather than the user.”

当前仍为原始干净 base；未创建空提交，未做最终整批审查、finalizer 分类或 tracker 关闭。
独立审查提供了目标已满足需求的证据，但没有替代尚未发生的完整流程。

### Worker／最终合并响应丢失场景 #2

- Worktree：/tmp/smartkit-ticket-validation-cnmii8d2/lost/batch
- 目标：/tmp/smartkit-ticket-validation-cnmii8d2/lost/target
- Base/HEAD：82fac19ec571eabf8a2831f0b2d3c83b321689af
- Tree：206ba82c411067ae42c545f905b2a47cb466b624
- 需求来源：lost/tracker.json，#2，requirements_revision=v1。
- 需求：整数乘法含零与负数；保持 add、公开名称和参数次序，仅修改 multiply。

真实基线验证：2 个测试方法，乘法 6 组输入失败，加法通过。
/root/lost_worker 已验证物理 worktree、Git common dir、干净 HEAD 和完整需求。
以下计划中的单行修改被自动审批拒绝，因其被认定与用户的 skill 分析请求不相关：

~~~diff
 def multiply(left, right):
-    return left + right
+    return left * right
~~~

没有发生该修改、Worker 中断、恢复、候选提交、审查或最终合并。不能把这一场景计为通过。

### 恢复所需的明确授权范围

仅限上述临时目录中的两个夹具：

- 执行所列单行修改，以及正常 hook 的票据提交/受限 amendment。
- 通过 host 中断并确认 Worker 已停止，恢复同一 worktree 的既有状态。
- 在独立验收通过后，对夹具 main 执行确切 OID 的一次本地 fast-forward；
  在 merge 完成后切断子进程回报，从原始 attempt 和外部 receipt 观察恢复，验证不重复 merge。
- 只更新夹具 tracker.json 的完成状态及次数，用于证明交付后关闭一次。

继续保留夹具供检查。此范围没有真实项目提交、远端写入或真实 tracker 操作。

## 交付状态

本次修改保持未提交，其他会话的 staged/unstaged 工作未被清理或纳入本次修改。
专项自动化测试合计 77 项：66 通过、11 平台/运行时跳过。
git diff HEAD --check 通过。第 3 项有独立审查证据，但两个完整行为场景均尚未完成。
