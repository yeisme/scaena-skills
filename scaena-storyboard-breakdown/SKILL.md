---
name: scaena-storyboard-breakdown
description: Use when 用户需要把单集剧本导入 Scaena，通过进程内 StoryboardModelRuntime 生成分镜，审阅 scene/shot candidate，执行有界 revise 或 typed patch，人工 accept/reject，并在无前端条件下导出 CSV、JSON 或 Markdown。
---

# Scaena 剧本分镜拆解

把一集文字剧本转成可追溯、可审阅、可修订的 whole-episode 分镜候选。Scaena 拥有 source、进程内模型执行、breakdown、candidate、acceptance、ProductionGraph 和 export 状态。不要手写 Scaena 数据库、`.scaena` 状态、manifest 或 receipt。

## 输入

- Scaena project、episode ref，以及 `.txt`、`.md`、`.fountain`、stdin、existing source ref 或 accepted Auctra handoff。
- 已配置的 `storyboard_model.*` runtime、`connection_ref`、精确 slash-form `provider/model`、最大尝试次数和成本上限。
- 可选的 current breakdown/candidate refs、expected version、修订目标和导出格式。

不要选择、读取或保存 provider credential。连接凭据由 Scaena 的本地 credential/config 边界管理；缺少连接或 runtime readiness 时返回 blocker。

## 输出

默认返回紧凑 receipt：

```text
status=<ok|blocked|failed|requires_action>
source_ref=<ref>
source_digest=<digest>
breakdown_ref=<ref>
breakdown_version=<version>
state=<state>
candidate_ref=<ref|none>
candidate_version=<version|none>
candidate_digest=<digest|none>
scene_count=<count>
shot_count=<count>
duration_ms=<milliseconds>
coverage_ratio=<ratio>
finding_count=<count>
blocking=<true|false>
prompt_pack_ref=<ref|none>
allowed_actions=<actions>
next_command=<real command|none>
evidence_refs=<refs>
```

Receipt、日志和 handoff 只保留 refs、versions、digests、counts、finding 摘要与 allowed actions，不复制剧本正文、逐字对白、reviewable prompt、model options、provider payload、credential、隐藏提示或完整模型推理。

## 工作流

### 1. 检查真实能力

进入 Scaena owner 项目并读取其 `AGENTS.md`。先检查已安装命令，不根据文档猜测不存在的 flag：

```bash
scaena storyboard --help
scaena storyboard source import --help
scaena storyboard breakdown run --help
scaena storyboard breakdown show --help
```

若 CLI/MCP inventory 不含本 Skill 使用的命令或 tool，返回 `capability_missing`。旧 `scaena storyboard board|split` 是 fixture-only compatibility surface，不能替代本工作流，也不能据此报告 production-ready。

### 2. 接纳一份精确 source

一次只选一种 ingress：

```bash
scaena storyboard source import --project <project-path> --episode <episode-ref> --from <script.fountain> --json
scaena storyboard source import --project <project-path> --episode <episode-ref> --from - --json
scaena storyboard source import --project <project-path> --episode <episode-ref> --source-ref <source-ref> --json
scaena storyboard source import --project <project-path> --episode <episode-ref> --auctra-handoff-ref <handoff-ref> --json
```

Source 上限是 1 MiB。不要把 absolute local path 写入 receipt；stdin/file body 只在 admission 时瞬时读取。MCP 调用 `scaena.storyboard.source_import` 必须携带 `approved=true` 和稳定 `idempotency_key`。剧本正文优先用 CLI file/stdin ingress；不要把大正文粘贴进对话或证据。

### 3. 运行有成本上限的分镜拆解

先向用户展示 source ref/digest、模型、fallback、最大尝试次数、成本上限和写入影响，再取得明确确认：

```bash
scaena storyboard breakdown run \
  --project <project-path> \
  --episode <episode-ref> \
  --source-ref <source-ref> \
  --connection <connection-ref> \
  --model <provider/model> \
  --max-attempts 2 \
  --max-cost-usd <amount> \
  --idempotency-key <stable-key> \
  --confirm \
  --events
```

Fallback model 必须由用户或既有 policy 显式提供；不要静默换模型。runtime unavailable、contract mismatch、cost cap、invalid delivery 或 repair exhausted 都要 fail closed，不生成本地伪候选。

MCP 对应 `scaena.storyboard.breakdown_run`。所有 mutation 都要 `approved=true` 和 `idempotency_key`；revise、patch、accept、reject 还必须携带 positive `expected_version`。

### 4. 先看 safe summary，再逐步展开

```bash
scaena storyboard breakdown show <breakdown-ref> --project <project-path> --agent
scaena storyboard breakdown show <breakdown-ref> --project <project-path> --candidate <candidate-ref> --json
```

只有用户明确需要核对对白或生图提示词时，才读取：

```bash
scaena storyboard breakdown show <breakdown-ref> --project <project-path> --candidate <candidate-ref> --include-dialogue --json
scaena storyboard breakdown show <breakdown-ref> --project <project-path> --candidate <candidate-ref> --include-prompt --json
```

MCP 默认读取 `scaena://storyboard-breakdown/{breakdown_ref}` 或 `scaena://storyboard-candidate/{candidate_ref}`；只有显式 prompt review 才读取 `scaena://storyboard-prompt-pack/{prompt_pack_ref}`。即使读取了正文，也不要把它复制进 routine receipt。

### 5. 审阅并选择 revise 或 patch

用 `$ai-drama-director` 检查观众信息、人物行动、调度、景别、角度、运镜、节奏和声音意图；它只提供 directing decision，不写 Scaena 状态。选择运镜时先查 Scaena 内置模板，不要手写平行词表：

```bash
scaena preset camera-move list --intent 发现真相 --json
scaena preset camera-move show push-in --json
```

`prompt_template` 只作可审阅骨架；patch 仍使用 canonical `camera_movement`（`slow_push_in`、`dolly_in`、`handheld` 等）。用 `$ai-drama-continuity-supervisor` 检查人物、服装、道具、空间、时间、动作方向、光线、声音和字幕连续性；`unknown` 或 `stale` 不能当 pass。

- 结构、镜头拆分、source/dialogue mapping 或 prompt mapping 要变化：使用 Agent revise。
- 只改 `dramatic_purpose`、`action_summary`、`shot_size`、`camera_angle`、`camera_movement`、`duration_ms`、`voice_over`、`sfx`、`continuity_notes`：使用 typed patch。
- 不允许 patch identity、order、source span、dialogue 或 prompt body。

```bash
scaena storyboard breakdown revise <breakdown-ref> --project <project-path> --candidate <candidate-ref> --target <scene-or-shot-ref> --instruction <bounded-instruction> --connection <connection-ref> --model <provider/model> --max-cost-usd <amount> --expected-version <version> --idempotency-key <stable-key> --confirm --events

scaena storyboard breakdown patch <breakdown-ref> --project <project-path> --candidate <candidate-ref> --shot <shot-ref> --set camera_movement=slow_push_in --set duration_ms=4200 --expected-version <version> --json
```

每次 revise/patch 都创建 immutable successor；完成后重新读取 current head，不能继续操作旧 candidate。

### 6. 人工 accept 或 reject

执行前读取 [review-and-acceptance.md](references/review-and-acceptance.md)。只有 current head、expected version 匹配、无 blocking findings 且当前用户明确批准时才能 accept：

```bash
scaena storyboard breakdown accept <breakdown-ref> --project <project-path> --candidate <candidate-ref> --expected-version <version> --actor <human-actor-ref> --idempotency-key <stable-key> --confirm --json
```

Accept 才物化 ProductionGraph/Scene/Shot。模型、Agent 或 runtime receipt 不得 self-accept。

Reject 也需要当前用户明确批准，但必须保持 canonical Scene/Shot 零写入：

```bash
scaena storyboard breakdown reject <breakdown-ref> --project <project-path> --candidate <candidate-ref> --expected-version <version> --actor <human-actor-ref> --idempotency-key <stable-key> --confirm --json
```

### 7. 明确确认后导出

CSV、JSON、Markdown 可用于人工审阅或下游交接；导出本身不等于 accept，也不等于 production-ready：

```bash
scaena storyboard breakdown export <breakdown-ref> --project <project-path> --candidate <candidate-ref> --format csv --output exports/storyboards/<name>.csv --idempotency-key <stable-key> --confirm --json
```

覆盖已有普通文件必须再得到明确授权并使用 `--overwrite`。不得绕过 path、symlink、formula-injection 或 checksum 门禁。MCP 对应 `scaena.storyboard.breakdown_export`；导出结果通过 `scaena://storyboard-export/{export_ref}` 读取。

## 边界

- 只调用真实 Scaena CLI、HTTP application surface 或列出的 MCP tools/resources。
- 不直接调用模型 provider SDK，不调用外部模型服务 CLI fallback，不持有 credential。
- 不手写 SQLite、GORM rows、CAS、job、candidate、ProductionGraph、manifest、receipt 或 evidence metadata。
- 不因命令 exit zero、candidate 存在、export 成功或 fixture-only command 可用而声称 production-ready。
- 不自动提高成本、重放有歧义的 mutation、替换 idempotency key、覆盖文件、accept、reject 或扩大项目 scope。

## 验证

- Default read、CLI JSON、HTTP 和 MCP 必须保持同一 refs/state/version/digest/counts/findings/actions/error codes。
- `EXPECTED_VERSION_MISMATCH` 后重新读取 current head；不要自动把 expected version 改成最新值并重试。
- `IDEMPOTENCY_CONFLICT` 表示同 key 的 intent 发生变化；不要用新 key 隐藏冲突，先确认用户是否真的发起新 intent。
- `BLOCKING_FINDINGS` 后只允许 review、revise、patch、reject 或 export review copy，不允许 accept。
- 保留 redacted evidence 和真实 error code，不保存 raw source、prompt 或 provider payload。

## 生产编译器门禁（current）

分镜进入付费媒体生成前，使用 production compiler 投影而非工程日志：

- `scaena storyboard breakdown board <breakdown-ref> --json`：第一屏只看一项
  决策、cost 摘要与最多 12 项异常。
- `scaena storyboard breakdown readiness <breakdown-ref> --json`：12 轴 readiness；
  `ready_for_generation` 才是付费生成准入，candidate `generation_ready` 仍只表示
  结构完整。未 accepted 的 ProductionGraph 永不 ready_for_generation。
- `scaena storyboard breakdown exceptions <breakdown-ref> --json`：按优先级排布
  的阻塞异常与 stale review refs。
- scoped range review：`scaena storyboard breakdown work review --breakdown <ref>
  --candidate <ref> --decision range_approved|changes_requested --start-segment N
  --end-segment M --actor user:operator --confirm --json`。range receipt 不等于
  整集 accept；整集 accept 仍是唯一 ProductionGraph 物化门。
- L3 autopilot：`scaena workflow simulate --automation-level L3_supervised_autopilot`
  生成 exact plan digest 投影；付费执行前必须 human approve 同一 digest。
- 主体资产批次与稳定性认证见 `scaena-storyboard-subject-asset-readiness` skill
  （`storyboard asset-batch *`、`asset stability *` 命令族）。

缺 audio intent、readiness blocker、cost envelope 未预留或 actor 非 human 时
fail closed；不要绕过这些门禁提交付费生成。
