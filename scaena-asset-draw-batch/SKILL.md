---
name: scaena-asset-draw-batch
description: Use when producing a confirmed list of Scaena subject assets in one batch, recovering a draw batch, applying dependency waves, protecting a project template digest, or overwriting an already selected derived view without a new generation. Use for 批量抽卡、PRODUCE_CONFIRMED、wave/requires、统一回查、衍生候选快覆盖; do not decide single-slot readiness, auto-select candidates, freeze slots, or call providers from Scaena.
---

# Scaena 抽卡批量与快覆盖

本 Skill 管理「一批抽卡怎么被并发执行、回查与覆盖」。单槽位是否可冻结、是否 `production_admitted` 仍归 `scaena-subject-asset-readiness`；Eikona 独占生成与 artifact 真源。

**能力层**：抽卡的图片生成统一走 `GenerationCapability<image>.invoke()`，CLI / MCP / HTTP 只是 `GenerationBinding`，resolver 自动选 `executable` binding，**不询问 `cli|mcp`**；一次 `ApprovalWindow` 覆盖本批全自动，可重试错误在 `retry_budget=2` 内自动重试，理由与次数写 `GenerationReceipt.binding_ref` / `retry_used`。详见聚合仓 `docs/drama-execution-kernel/capability-abstraction.md`。

## 与现有 Skill 的分工

| 职责 | owner |
| --- | --- |
| 单 slot 就绪、cap、wave 依赖、human-only `select/freeze`、稳定性矩阵 | `scaena-subject-asset-readiness` |
| 一批的冻结清单、并发调度、统一回查、写入预算、快覆盖 | 本 Skill |
| 生成图片、run/artifact、path-free handoff | `cli/eikona` |

## 真实命令链

```bash
scaena asset draw plan --project <p> --asset <slot> --brief <brief-ref> --wave 1 --json
scaena asset draw start --project <p> --asset <slot> --session <draw-session-ref> --json
eikona generate --prompt-ref <id> --purpose subject_candidate --model openai/gpt-image-2.5-sunburst --agent
eikona events tail <run_id> --json
scaena asset draw record --project <p> --asset <slot> --session <draw-session-ref> --eikona-run <run-ref> --digest sha256:<64-hex> --json
scaena asset draw select --project <p> --asset <slot> --candidate <ref> --action accept --actor <human> --reason "<reason>" --json
scaena asset draw freeze --project <p> --asset <slot> --confirm --json
scaena asset draw status --project <p> --asset <slot> --agent
```

`record` 只登记 `run_ref + sha256`，零 provider 调用；bytes 不进 Scaena。`selected / frozen` 不等于 `production-admitted`、`shot-accepted` 或 `export-ready`。

## 输入 / 输出

- 输入：`creative.owner-handoff.v0.1`、已确认 slots、`GenerationIntent`（`FrozenRef` + typed controls + `template_digest`）、`ApprovalWindow`（`capability_kinds=[image]` / `count` / `cost_ceiling` / `retry_budget=2`）、`ProductionGraph ref/version`、写入预算。
- 输出：`scaena.draw_batch.v1` 的 `batch_ref` + 逐项 `GenerationReceipt`（含 `binding_ref` / `retry_used` / `event_cursor`）+ 结果分类（新生成 / 旧图复用 / 已绑定 / 在途 / 失败 / 待决 / 缺图）。**结构化批次文件由 Scaena CLI 产出，agent 不手写**。

## 不变量

1. 一次冻结清单 → 依赖波次调度 → **先落盘再发送** → 一批提交后统一回查。
2. `wave > 1` 必须声明 `--requires <frozen-slot-ref>` 且上游全 `frozen`；同 slot 一个 active session；不同 slot 可并行，同 slot 串行。
3. `image_concurrency` 只表示本地派发上限（1–100，默认 1），不承诺服务端等量并行；写入预算在调用前计入，失败也消耗；只读回查分账、不忙轮询。
4. `template_digest` 绑定项目模板固定正文，展开词漂移在发送前拒绝。
5. 不预造 imageId、不自动选候选、不自动覆盖主图、不自动冻结；`candidate → selected → frozen` 每步 human decision。
6. `COMPLETED` 只表示本批已列节点完成，不等于全剧零遗漏、美术验收或 `production_admitted`。
7. UNKNOWN / 在途只 `reconcile` 只读查询，且**不消耗 `retry_budget`**；确认失败不自动付费重试。
8. 可重试错误（瞬时网络 / 5xx / 429 / 超时且 `mutationAttempted=false` / `binding=unavailable` 换另一个 executable binding）在 `retry_budget=2` 内自动重试，每次保持同一 `action_id` + `idempotency_key` + `intent_digest` + `approval_ref`；已 `ACCEPTED` / 业务·权限·语义拒绝 / 创意输入变化禁止重试；耗尽交 `needs_decision`。
9. 一张 `ApprovalWindow` 覆盖整批全自动；越界（超 `count` / `cost_ceiling` / `template_digest` 漂移 / 新 kind）必须重新审批；付费生成仍按动作留独立凭证。
10. `planned / readonly / unavailable` binding 一律 fail-closed；换 binding 不增加权限、不重复审批。

## Identity-equal 快路径

命中「候选已生成完成 + 用户已选定 + 只覆盖既有衍生视图」时，走 [C2 快路径](https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/contracts/draw-batch.v1.md)：沿用同一 `entryId` / slot，复制写前证据为不可变快照，逐项校验 `template_digest` / 母图 / 别名 / 集数 / 旧图 / 新图 digest，再交给 `scaena-bounded-replacement` 执行 EU-09。任一漂移整批停止；技术覆盖完成不等于新增审美结论；旧图不自动删除。

任一创意字段变化（模型 / 正文 / 时长 / 造型语义）→ 退回完整链，新 `idempotency_key`。

## 边界

- 不调用 provider、不读 Eikona 人类可读输出、不手写 `.scaena` 状态或抽卡 ledger；
- 不把成功命令、图片数量、Eikona feedback、Auctra acceptance、legacy `approved` 或相似度总分当成生产就绪；
- 不为每个项目新写专用执行器；复用 `scaena workflow status/resume` 与 `asset draw` 现有入口。
- 不询问 `cli|mcp|both` 作为流程分支；不把入口差异写进批次计划；不自动扩大 `retry_budget` 或审批范围。

## 验证

```bash
scaena asset draw status --project <p> --asset <slot> --agent
scaena workflow status <workflow-run-ref> --project <p> --agent
```

## 按需引用

- 能力抽象与审批窗口：[https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/capability-abstraction.md](https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/capability-abstraction.md)
- 能力调用合同：`ai-drama-skills` 的 `ai-drama-action-receipt/references/capability-invocation.md`
- C2 合同：[https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/contracts/draw-batch.v1.md](https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/contracts/draw-batch.v1.md)
- EU-02/03/04：[https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/execution-units.md](https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/execution-units.md)
