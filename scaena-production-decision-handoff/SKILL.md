---
name: scaena-production-decision-handoff
description: Use when a confirmed manga-drama creative.decision-brief.v0.1 must read Scaena storyboard or production facts, compile a zero-call simulation, or explicitly apply an existing production skill plan without accepting assets or starting paid generation.
---

# Scaena 生产决策交接

Scaena 是 storyboard、ProductionGraph、生产 review、readiness、session 和 delivery 的 canonical owner。本 Skill 只消费已确认 brief，读取 owner projection，并生成 `creative.owner-handoff.v0.1`。

## 输入

- 已确认 brief 及 `source_digest`。
- Scaena project path。
- 可选 breakdown/candidate/session/episode refs。
- 当前意图：读取生产事实、生成零调用 simulation，或显式应用已存在的 skill plan。

缺少 project/ref、brief confirmation 或真实 capability 时返回 `needs_input`/`needs_contract`。

## 只读阶段

按现有 refs 运行最小命令：

```bash
scaena storyboard breakdown board <breakdown-ref> --project <project-path> --json
scaena storyboard breakdown readiness <breakdown-ref> --project <project-path> --json
scaena storyboard breakdown exceptions <breakdown-ref> --project <project-path> --json
scaena production session inspect <session-ref> --project <project-path> --json
scaena production session skill-plan inspect <session-ref> --project <project-path> --json
```

不要读取 `.scaena` 私有文件、数据库或工程日志替代 CLI/API projection。unknown/stale/partial/pending review 不能当 pass。

## 零调用 simulation

用户确认 DecisionBrief 后，默认下一步只能是 simulation/preflight：

```bash
scaena workflow simulate \
  --goal shortdrama.episode-production \
  --project <project-path> \
  --automation-level L2_assisted \
  --json
```

simulation 必须保持 provider call 为零，并展示步骤、风险、approval、cost 和 blocker。使用 Seedance 2.5 时还必须展示 task policy ref/digest、reference role/count、ratio/duration/output/audio policy 与 capability maturity；完整映射见 `../scaena-production-operator/references/seedance-2-5-scaena-mapping.md`。缺 accepted Auctra source、方向确认、audio intent、rights 或 readiness 时 fail closed。

## 显式应用 skill plan

只有用户再次明确要求应用已经 inspect 的同一 session/plan 时，才允许：

```bash
scaena production session skill-plan apply \
  <session-ref> \
  --project <project-path> \
  --confirm \
  --json
```

应用 skill plan 不等于执行付费生成或接受资产。plan digest、expected version 或 allowed action 已 stale 时，不自动刷新并重试。

## 输出与边界

返回 `creative.owner-handoff.v0.1`，列出 source digest、project ref、allowed actions、next command、mutation 和 confirmation 状态。

- 不执行付费生成、分镜 accept/reject、主体选择/冻结、production acceptance、batch expansion、export 或 publish。
- Auctra story/canon handoff 未完成时，不进入 Scaena production simulation。
- 不保存 raw source、prompt、provider payload、credential、signed URL、私有路径或完整思维链。
