# Scaena 主体候选抽卡流程

## 状态机

```text
planned
→ drawing
→ candidate_review
→ selected
→ frozen
```

DrawSession 是 Scaena 生产资格流程，不是 provider job。Eikona 生成图片并拥有 run/artifact；Scaena 只登记 refs、digest、候选顺序、人工选择和冻结状态。

## 不变量

- 每个 asset slot 同时最多一个 active DrawSession。
- 默认 session 上限为 5 个候选；记录第 6 个候选必须失败并进入 exhausted。修 brief 后新建 session，不扩大隐藏 retry。
- `record` 只登记既有 Eikona run 和 sha256 digest，owner/provider call count 必须为零。
- `select` 与 `freeze` 是 human-only；Agent 不能伪造 human actor。
- `selected`/`frozen` 不等于 production-admitted、shot-accepted、production-accepted 或 export-ready。
- 候选路径由 Scaena 分配；Agent 不手建或重命名结构化目录。
- source/rights、originality、similarity、preflight 和 continuity blocker 不能被高分候选或 `--confirm` 覆盖。

## 依赖波次

| Wave | 典型 slot | 进入条件 |
| --- | --- | --- |
| 1 | 主角 identity、project style | accepted source/brief、rights、originality decision |
| 2 | 三视图、表情、姿态、发型/服装派生 | Wave 1 对应 slot 已 frozen |
| 3 | recurring location、story-critical prop、wardrobe variant | 依赖主体/style 已 frozen |
| 4+ | shot-specific derived candidate | `--requires` 中的所有上游 refs 已 frozen |

不要用 background exception 放行 named、close-up、recurring 或 continuity-relevant subject。

## 命令流程

### 1. 计划

```bash
scaena asset draw plan \
  --project <project-path> \
  --asset <asset-ref> \
  --brief <brief-ref> \
  --wave 1 \
  --json
```

后续波次按 installed help 增加 `--requires <frozen-slot-ref>`。plan 必须返回 session ref、cap、wave、dependencies、canonical path policy 和 blocker。

### 2. 开始

```bash
scaena asset draw start \
  --project <project-path> \
  --asset <asset-ref> \
  --session <draw-session-ref> \
  --json
```

### 3. 通过 Eikona 生成

Eikona 默认模型使用 canonical ref：

```bash
eikona generate <visual-brief> \
  --model openai/gpt-5.4-image-2 \
  --json
```

保存 Eikona run ref、artifact ref、sha256 digest、model ref、source refs、rights/provenance 和 redacted evidence。

### 4. 登记候选

```bash
scaena asset draw record \
  --project <project-path> \
  --asset <asset-ref> \
  --session <draw-session-ref> \
  --eikona-run <eikona-run-ref> \
  --digest sha256:<64-hex> \
  --json
```

查询 Scaena 分配的标准路径：

```bash
scaena asset draw path \
  --project <project-path> \
  --asset <asset-ref> \
  --seq <n> \
  --agent
```

标准形态为 `assets/<asset-id>/draws/<seq>/candidate.png`，但路径必须以命令返回为准。

### 5. 人工选卡

```bash
scaena asset draw select \
  --project <project-path> \
  --asset <asset-ref> \
  --candidate <candidate-ref> \
  --action accept \
  --actor <human-actor-ref> \
  --reason "<reason>" \
  --json
```

拒绝、要求重画或比较候选时使用 installed help 支持的 typed action；不得删除历史候选或覆盖其 digest。

### 6. 人工冻结

```bash
scaena asset draw freeze \
  --project <project-path> \
  --asset <asset-ref> \
  --confirm \
  --json
```

### 7. 状态与交接

```bash
scaena asset draw status \
  --project <project-path> \
  --asset <asset-ref> \
  --agent
```

返回：

```text
asset_ref
draw_session_ref
state
wave
candidate_count
candidate_cap
selected_candidate_ref
frozen_subject_version_ref
dependency_refs
blocking_codes
generation_preflight_ref
next_command
evidence_refs
```

## 从冻结到生产准入

冻结完成后仍必须运行主体 readiness 和 generation preflight，固定：

```text
generation_preflight_ref/digest
subject_version_bindings
reference_asset_version_refs
style_pack_version_ref
requirement_version_refs
expected_graph_version
```

任一输入变化都会使 preflight stale。submit 前必须再次检查；不能自动改绑到“最新版本”。
