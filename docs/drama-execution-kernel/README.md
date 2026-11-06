# DEK v1 指针（`scaena-skills`）

本仓是 `yeisme/scaena-skills` 独立仓库。做剧执行内核（Drama Execution Kernel, DEK v1）的**规范设计真源**在聚合仓 `yeisme/yeisme-agent-my-skills`：

- **总览与交接**：`https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/HANDOFF.md`
- **后续实现路线**：`https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/implementation-roadmap.md`
- 能力抽象（一个作用三类 kind）：`https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/capability-abstraction.md`
- 抽象设计：`https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/abstract-design.md`
- 执行单元设计：`https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/execution-units.md`
- C2 `scaena.draw_batch.v1`：`https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/contracts/draw-batch.v1.md`
- C3 `yeisme.replacement_bound.v1`：`https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/contracts/replacement-bound.v1.md`

本仓落地的 DEK skill：

| Skill | 职责 |
| --- | --- |
| `scaena-asset-draw-batch` | 确认清单批量抽卡、wave 依赖、统一回查、已选衍生快覆盖（C2）；已对齐 `GenerationCapability<image>` / `ApprovalWindow` / `retry_budget=2` |
| `scaena-bounded-replacement` | `identity_equal` 门、三类资产（image/video/audio）有界替换、失败受控修复（C3）；已对齐审批窗口与重试 |

`scaena-subject-asset-readiness` 继续独占单槽位门禁（cap、wave、human-only `select/freeze`、稳定性矩阵）；`scaena-production-operator` 继续独占生产操作，只新增技术替换 / 创意修改的分岔；`scaena-production-decision-handoff` 是 `FrozenRef` 链形状的落点。**不要在本仓复制或改写设计正文**，避免与聚合仓出现两份不同口径。

各 SKILL.md 里的设计链接使用绝对 URL，因此本仓被单独 clone 时仍可访问规范位置。
