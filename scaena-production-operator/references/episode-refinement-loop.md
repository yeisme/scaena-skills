# Scaena 整集拼接与精修循环

## 目的

将已通过逐镜 production acceptance 的片段装配为整集候选，分类缺陷，并把修复路由回真正 owner。精修必须产生 successor refs 和 evidence，不能覆盖 accepted source、selected asset 或最终成片。

## 拼接与选版

### 整集预览

```bash
scaena video episode-preview \
  --project <project-path> \
  --episode <episode-ref> \
  --segment-asset <asset-1> \
  --segment-duration-ms <ms-1> \
  --segment-asset <asset-2> \
  --segment-duration-ms <ms-2> \
  --output previews/<episode>.mp4 \
  --confirm \
  --json
```

所有 segment 必须已通过 production acceptance，顺序与 duration 必须来自 current ProductionGraph。Preview 成功不等于 cut selected 或 delivery ready。

### Timeline variants

```bash
scaena edit plan \
  --project <project-path> \
  --graph <workflow-graph-ref> \
  --platform douyin \
  --target-duration 75 \
  --json

scaena edit timeline \
  --project <project-path> \
  --plan <edit-plan-ref> \
  --variant fast-hook \
  --json

scaena edit render \
  --project <project-path> \
  --timeline <timeline-ref> \
  --profile preview \
  --output previews/<episode>-cut.mp4 \
  --confirm \
  --json

scaena edit score --project <project-path> --cut <cut-ref> --json
scaena edit select --project <project-path> --cut <cut-ref> --json
```

可以生成有界的多个 timeline variant；自动 score 只产生 recommendation。最终 cut、字幕和 mix 必须显式选择/接受。

## 缺陷分类

| finding | Owner | successor 动作 | stale 范围 |
| --- | --- | --- | --- |
| `story_causality`、`character_motivation`、`dialogue`、`hook` | Auctra | 新 scratch/rewrite candidate → review → accepted revision → 新 handoff | 受影响 scene/shot 及后代 |
| `storyboard_structure`、`semantic_mapping`、`source_mapping` | Scaena storyboard | `breakdown revise` | 受影响 breakdown/shot |
| `shot_field`、`duration`、`allowed_mapping` | Scaena storyboard | typed `breakdown patch` | 精确受影响节点 |
| `identity_drift`、`style_drift`、`wardrobe`、`location`、`prop` | Scaena asset + Eikona | 新 draw/derived candidate → human select/freeze → preflight | 绑定旧 version 的镜头 |
| `shot_action`、`camera`、`composition`、`video_artifact` | Scaena generation | 只重生成失败 shot | 单镜及其装配后代 |
| `dialogue_audio`、`voice`、`foley`、`music`、`sync`、`mix` | Sonora/audio owner | replacement asset/mix revision → independent audio review | 使用旧 audio/mix 的后代 |
| `pacing`、`subtitle`、`transition`、`mix_balance` | Scaena edit | 新 timeline/cut → render/score/select | edit/delivery/export |
| `resolution`、`denoise`、`interpolation`、`visual_enhance` | Scaena enhance | 只对 selected candidate 创建 successor | 对应 media/cut |
| `codec`、`checksum`、`manifest`、`package` | Scaena delivery/export | technical repair | package only |
| `originality`、`rights`、`identity_leak`、`similarity` | 对应创作/资产 Owner + rights review | 新原创 candidate 或移除未授权素材 | 所有依赖风险素材的后代 |

不得用剪辑掩盖故事 canon 缺陷，不得用重新生成视频掩盖主体版本错误，也不得用 package repair 修改创作内容。

## 有界修复

每个 finding 保存：

```text
finding_ref
finding_code
severity
affected_refs[]
owner
repair_action
attempt
cost_delta
successor_refs[]
evidence_refs[]
status
```

同一个确定性 finding 默认只运行一次 owner-specific repair。仍失败时：

1. 保留原候选、successor、receipt 和最小失败 evidence；
2. 返回 typed blocker 与精确 stale descendants；
3. 给出扩大成本、改变 brief、回上游 canon 或放弃该候选的选项；
4. 未得到新决策前停止，不无限 reroll。

Transient owner/network failure 可以按既定 retry policy 使用同一 idempotency key 重试；`unknown_accept` 必须先查询原 owner receipt，不能重复提交。

## Enhance 当前边界

先检查真实命令面：

```bash
scaena enhance --help
scaena enhance plan --help
scaena enhance run --help
scaena enhance show --help
```

当前 v1 `enhance run` 仅允许 fixture 驱动的确定性验证，不代表付费 provider 已接通。没有真实 provider command、receipt 和 artifact lineage 时：

- 可以生成 enhance plan；
- 可以运行 fixture canary；
- 不得把结果描述为真实超分、重绘、去噪或插帧生产；
- 返回 `enhance_provider_unavailable`，由 owning implementation change 补齐。

## Delivery 与导出

不带 `--confirm` 的 `export package` 用于 draft 计划/预检；当前命令不支持 `--dry-run`。Draft `--to` 会由 CLI 写入 manifest，因此不是零写入预览：

```bash
scaena export package \
  --project <project-path> \
  --profile douyin \
  --to <output-path> \
  --json

scaena export package \
  --project <project-path> \
  --profile douyin \
  --to <output-path> \
  --confirm \
  --json
```

Export 前必须验证 selected cut、final mix、subtitle alignment、continuity、originality/rights、manifest、codec、duration、checksums、provenance 和 zero blocking findings。Export 生成本地 package，不自动发布。

## 完成回执

```text
status
episode_ref
episode_preview_ref
edit_plan_ref
selected_timeline_ref
selected_cut_ref
final_mix_ref
refinement_findings[]
repair_receipts[]
delivery_review_ref
export_plan_ref
export_receipt_ref
manifest_ref
checksum_refs[]
blocking_findings[]
next_command
evidence_refs[]
```
