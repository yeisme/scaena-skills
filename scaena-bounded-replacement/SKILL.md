---
name: scaena-bounded-replacement
description: Use when replacing a shot video, reference audio or derived asset, previewing which shots and packages a replacement affects, or repairing a failed video submission without a second paid attempt. Use for 视频资产替换、音频技术替换、identity_equal 判定、失败视频受控修复、共享 claim、eikona rollback; do not redesign prompts, change models or durations under a repair authorization, or mark technical rollback as acceptance.
---

# Scaena 有界资产替换与失败修复

本 Skill 把「改音频、改正文、补复核」三个互不绑定的步骤，收敛为**一个绑定替换任务**，并给出失败视频原样重提的唯一路径。核心收益是远程断线后不产生第二次付费提交。

## 判定门：`identity_equal`

判定输入直接复用 `scaena-production-operator/references/workflow.md:140` 的执行前校验列表，不新增规则：

```
project, ProductionGraph ref/version, shot ref,
frozen intent ref/digest, frozen spec ref/digest, validated bundle ref/digest,
capability ref/digest/maturity, task policy,
duration / ratio / output / audio policy,
exact subject / style / reference versions and ordinals,
non-empty idempotency key
```

补充字段：`speaker` / `character subject` / `voice timbre` / `original audio source` / `dialogue text` / `mention` / `model` / `channel`。

| 结果 | 路径 |
| --- | --- |
| 全部相等 | **技术替换**：EU-09，跳过创意复核与全量回归 |
| 任一创意字段变化 | **新创作批**：退回 EU-06，新 `idempotency_key` 与新用户授权；禁止借「原样重提」授权 |
| 字段缺失 / provenance 不全 | `TERMINAL_REJECTED`，报具体缺口，不猜默认值 |

完整门定义见 [references/identity-equal-gate.md](references/identity-equal-gate.md) 与 [C3](https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/contracts/replacement-bound.v1.md)。

## 真实命令

```bash
eikona assets stage <handle> --to <path> --json
eikona assets handoff <asset_handle> --agent
eikona replace <artifact_id> --project current --to <path> --yes --json
eikona rollback <replacement_id> --json
scaena workflow repair plan --run <run-ref> --json
scaena workflow repair run --repair <repair-ref> --json
scaena workflow resume <run-ref> --project <p> --json
```

`eikona rollback` 校验当前文件 hash，不覆盖后续用户编辑。`scaena production graph describe <graph-ref> --json` 用于替换前反向查询受影响 shot / package。

## 输入 / 输出

- 输入：`old_ref` / `new_ref`、三份实际媒体字节摘要（旧媒体 / 新媒体 / 原始音源）、`field_plan` / `audio_plan`、`claim_key`、原 `submission_ref` 与用户明确授权原文。
- 输出：`yeisme.replacement_bound.v1` 的 `bound_ref`、`identity_equal_verdict`、`replacement_id`、权威回读结果。**结构化绑定文件由 owner CLI 产出，agent 不手写**。

## 不变量

1. 一个 `bound_ref` 绑定旧包 / 新包 / provenance / field_plan / audio_plan / claim_key；不得拆成互不绑定的独立步骤。
2. 先验证 `identity_equal` → 替换 → 权威回读；字段结果 `UNKNOWN` 时停止且不重投。
3. 技术替换完成后才刷新技术证据；技术证据刷新不制造新的语义复核结论。
4. 中断用原 `recovery_ref` 恢复，不创建新任务绕过旧状态。
5. **失败视频受控修复**：只有返回 ID 全部终态 `FAILED` + 实时回读仍 `FAILED` + 原配置逐字段全等才允许原样重提；`claim_key` 防并发重投；只补「已预留未发送」，不产生新派发；新失败以其新返回 ID 建下一轮证据。
6. `unknown_accept` 不换幂等键、不换模型、不创建替代任务；已受理后只 `reconcile` 原任务。
7. `eikona rollback` 是技术回滚，**不等于验收通过 / 备案完成 / 生产接受**；`permission` 仍为 `handoff_candidate`，`replacement_status` 不越级。
8. 不删除历史候选或其 digest；不覆盖后续用户编辑。

## 边界

- 不改提示词、不换模型、不压缩时长、不换渠道；这些属于新创作批；
- 不调用 provider、不手写 `.scaena` / manifest / receipt；
- 不把「失败退出码」当失败证据；成功 / 活动 / 未知的目标不进入自动失败队列；
- 不把备案通过说成供应商不再拦截；模型拒绝内容仍需依据原错误判断。

## 验证

```bash
scaena workflow status <run-ref> --project <p> --agent
eikona replace <artifact_id> --project current --to <path> --yes --json
eikona rollback <replacement_id> --json
```

## 按需引用

- C3 合同：[https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/contracts/replacement-bound.v1.md](https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/contracts/replacement-bound.v1.md)
- EU-09 / EU-31：[https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/execution-units.md](https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/execution-units.md)
