---
name: scaena-storyboard-breakdown
description: Use when 用户需要把单集剧本导入 Scaena，通过进程内 StoryboardModelRuntime 生成分镜，审阅 scene/shot candidate，执行有界 revise 或 typed patch，人工 accept/reject，并在无前端条件下导出 CSV、JSON 或 Markdown。
---

# Scaena 剧本分镜拆解

把一集文字剧本转成可追溯、可审阅、可修订的 whole-episode 分镜候选。本 Skill 是 host adapter（operation Skill）：负责意图路由、方向 profile 选择、immutable PromptRepo 模板绑定、调用真实 Scaena CLI/MCP、呈现结果并保留全部成本与 canonical 门禁。Scaena 拥有 source、进程内模型执行、breakdown、candidate、acceptance、ProductionGraph 和 export 状态；模型与 provider 执行属于 Dramaturge。不要手写 Scaena 数据库、`.scaena` 状态、manifest 或 receipt，也不要创建第二个分镜 writer Skill。

## DramaRoutePlan（路由计划）

Intake 完成后先输出最小 route plan（`ai-drama.route-plan.v1` 语义）：

```text
phase=director_plan
medium=short_drama
primary_skill=ai-drama-director
compatible_skill=ai-drama-continuity-supervisor
artifact=storyboard_candidate
artifact_disposition=candidate
acceptance_state=unreviewed
canonical_owner=production_owner
owner_binding=scaena
```

- 本 Skill 自身不进入 `primary_skill`，不与 `ai-drama-director` 竞争 artifact ownership；它只通过 owner action/next action 调用 Scaena。
- `compatible_skill` 最多一个 continuity constraint。`$ai-drama-director` 提供 directing decision，`$ai-drama-continuity-supervisor` 提供 continuity finding；两者都不写 Scaena 状态。
- format/duration/aspect 缺失或冲突且会改变分镜结构时，route plan 返回 `needs_format_decision`，先走 `ai-drama-format-strategist` 路径或询问用户，不让模型只凭剧本文风猜 profile。
- 输入含多集或 whole-episode estimate 超出当前 owner capability 时，只提供拆集、换 exact model 或调整明确 direction 的决策，不截断、不隐式 chunk、不跨集合并、不静默 fallback。

## 输入

- Scaena project、episode ref，以及 `.txt`、`.md`、`.fountain`、stdin、existing source ref 或 accepted Auctra handoff；一次只处理一集。
- 已接受的 format/profile 事实：竖屏短剧、对话密集、漫剧分镜或广告微短剧，以及 target duration、aspect、shot range（可来自 profile defaults）。
- exact Prompt 模板地址：默认官方 PromptRepo address，或用户明确给出的另一个 exact address；legacy `skill:scaena-storyboard-breakdown` version 1 只作兼容入口。
- 已配置的 `storyboard_model.*` runtime、`connection_ref`、精确 slash-form `provider/model`、最大尝试次数和成本上限。
- source classification 与 execution policy，以及 provider retention/training/region 事实。
- execution host：local CLI（verified foreground）或 remote/API/MCP。
- 可选的 current breakdown/candidate refs、expected version、修订目标和导出格式。

不要选择、读取或保存 provider credential。连接凭据由 Scaena 的本地 credential/config 边界管理；缺少连接或 runtime readiness 时返回 blocker。

## 输出

默认返回紧凑 refs-first receipt。routine 输出不包含 raw source、literal dialogue、Prompt body、provider options、provider payload、credential、Authorization、private path、tool args 或 full chain-of-thought：

```text
status=<ok|blocked|failed|requires_action>
route_status=<ready|needs_format_decision|capability_missing|blocked>
profile_id=<id>
profile_maturity=<first-support|exploratory>
source_ref=<ref>
source_digest=<digest>
source_classification=<public|internal|confidential>
execution_policy_ref=<ref|none>
direction_ref=<ref|none>
direction_digest=<digest|none>
prompt_snapshot_ref=<ref|none>
prompt_digest=<digest|none>
owner_readiness=<backed|disabled|unverified|unavailable>
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
allowed_actions=<actions>
next_command=<real command|none>
evidence_refs=<refs>
```

用户显式要求核对对白或提示词时可展示领域内容，但 explicit detail 与 routine receipt 分离，final receipt 仍保持上面的 safe projection。

## 工作流

### 1. Provider-free preflight

执行 [routing-and-preflight.md](references/routing-and-preflight.md)：用真实 `--help`/status/doctor/catalog 命令核实 CLI 能力、owner readiness、PromptRepo address、source/profile/direction identity 与 whole-episode estimate，provider/owner 调用数为 0。设计文档里的目标命令不得冒充当前可运行命令；未实现的 flag/命令返回 `capability_missing` 并回退当前真实 async 路径。

### 2. 接纳一份精确 source

一次只选一种 ingress：

```bash
scaena storyboard source import --project <project-path> --episode <episode-ref> --from <script.fountain> --json
scaena storyboard source import --project <project-path> --episode <episode-ref> --from - --json
scaena storyboard source import --project <project-path> --episode <episode-ref> --source-ref <source-ref> --json
scaena storyboard source import --project <project-path> --episode <episode-ref> --auctra-handoff-ref <handoff-ref> --json
```

Source 上限是 1 MiB。不要把 absolute local path 写入 receipt；stdin/file body 只在 admission 时瞬时读取。MCP 调用 `scaena.storyboard.source_import` 必须携带 `approved=true` 和稳定 `idempotency_key`。剧本正文优先用 CLI file/stdin ingress；不要把大正文粘贴进对话或证据。

### 3. 展示 approval packet 并取得一次当前明确授权

付费 run/revise 前向用户展示完整 packet（source identity/classification、execution policy、direction、Prompt snapshot、owner readiness、provider data policy、connection ref、exact model、fallbacks、attempts、cost cap、write/cost effect），见 routing-and-preflight.md。“继续”“看看”“下一步”只允许 read-only status/watch/review，不得跨越 cost 或 canonical/export gate；confidential source 的 policy mismatch 不能用 generic bypass 绕过。

### 4. 运行有成本上限的分镜拆解

local verified runtime 优先 foreground；remote/API/MCP 保持 async。两条路径都以同一个已授权 packet 为准：

```bash
scaena storyboard breakdown run \
  --project <project-path> \
  --episode <episode-ref> \
  --source-ref <source-ref> \
  --connection <connection-ref> \
  --model <provider/model> \
  --prompt-template 'promptrepo://official/video/ai-drama-storyboard-breakdown@1.0.0?locale=zh-CN' \
  --direction-profile vertical-short-drama-v1 \
  --execution-policy <policy-ref> \
  --max-attempts 2 \
  --max-cost-usd <amount> \
  --idempotency-key <stable-key> \
  --confirm \
  --foreground --timeout 10m --events
```

- `--foreground` 只在 preflight 证实可用时使用；超时返回 `WAIT_TIMEOUT` 后保留原 ref 并 `watch`，不新建 idempotency key、不 resubmit、不隐式 cancel。
- remote/MCP 路径去掉 `--foreground`，用 `run -> status/resource` 轮询；MCP tool 不长时间阻塞，queued 不等于 generated candidate。
- `--instruction-profile skill:scaena-storyboard-breakdown --instruction-profile-version 1` 是 legacy 兼容入口；优先 `--prompt-template` exact address，不读取、不复制 Prompt body。
- Fallback model 必须由用户或既有 policy 显式提供；不要静默换模型、换 key 或提高预算。runtime unavailable、contract mismatch、cost cap、invalid delivery 或 repair exhausted 都要 fail closed，不生成本地伪候选。

MCP 对应 `scaena.storyboard.breakdown_run`。所有 mutation 都要 `approved=true` 和 `idempotency_key`；revise、patch、accept、reject 还必须携带 positive `expected_version`。

### 5. Review loop：safe summary 到 explicit detail

执行 [review-and-acceptance.md](references/review-and-acceptance.md) 的固定顺序：safe summary -> direction summary -> findings -> shots -> explicit detail（仅显式需要时）-> director/continuity assessment -> revise/patch -> reload/diff -> human accept/reject -> optional export。

```bash
scaena storyboard breakdown show <breakdown-ref> --project <project-path> --view summary --agent
scaena storyboard breakdown show <breakdown-ref> --project <project-path> --view findings --candidate <candidate-ref> --json
scaena storyboard breakdown watch <breakdown-ref> --project <project-path> --timeout 5m --json
scaena storyboard breakdown diff <breakdown-ref> --project <project-path> --from-candidate <old-ref> --to-candidate <new-ref> --json
```

只有用户明确核对对白或生图提示词时，才读取 `--include-dialogue`/`--include-prompt` 或 `--view prompts`。MCP 默认读取 `scaena://storyboard-breakdown/{breakdown_ref}` 或 `scaena://storyboard-candidate/{candidate_ref}`；即使读取了正文，也不要把它复制进 routine receipt。

### 6. 审阅并选择 revise 或 patch

用 `$ai-drama-director` 检查观众信息、人物行动、调度、景别、角度、运镜、节奏和声音意图；它只提供 directing decision，不写 Scaena 状态。选择运镜时先查 Scaena 内置模板，不要手写平行词表：

```bash
scaena preset camera-move list --intent 发现真相 --json
scaena preset camera-move show push-in --json
```

`prompt_template` 只作可审阅骨架；patch 仍使用 canonical `camera_movement`（`slow_push_in`、`dolly_in`、`handheld` 等）。用 `$ai-drama-continuity-supervisor` 检查人物、服装、道具、空间、时间、动作方向、光线、声音和字幕连续性；`unknown` 或 `stale` 不能当 pass。

- 结构、镜头拆分、source/dialogue mapping、Prompt mapping、entity/continuity 或 profile/direction 变化：使用 Agent revise。
- 只改 `dramatic_purpose`、`action_summary`、`shot_size`、`camera_angle`、`camera_movement`、`duration_ms`、`voice_over`、`sfx`、`continuity_notes`：使用 typed patch。
- 不允许 patch identity、order、source span、dialogue 或 prompt body。

```bash
scaena storyboard breakdown revise <breakdown-ref> --project <project-path> --candidate <candidate-ref> --target <scene-or-shot-ref> --instruction <bounded-instruction> --connection <connection-ref> --model <provider/model> --max-cost-usd <amount> --expected-version <version> --idempotency-key <stable-key> --confirm --events

scaena storyboard breakdown patch <breakdown-ref> --project <project-path> --candidate <candidate-ref> --shot <shot-ref> --set camera_movement=slow_push_in --set duration_ms=4200 --expected-version <version> --json
```

每次 revise/patch 都创建 immutable successor；完成后重新读取 current head 并 diff，不能继续操作旧 candidate。Typed patch 是本地 successor，不调用 owner/provider。

### 7. 人工 accept 或 reject

执行前读取 [review-and-acceptance.md](references/review-and-acceptance.md)。只有 current head、expected version 匹配、无 blocking/stale/unknown findings、已呈现完整 direction review 且当前用户明确批准 materialization 时才能 accept：

```bash
scaena storyboard breakdown accept <breakdown-ref> --project <project-path> --candidate <candidate-ref> --expected-version <version> --actor <human-actor-ref> --idempotency-key <stable-key> --confirm --json
```

Accept 才物化 ProductionGraph/Scene/Shot。模型、Agent、Skill 或 runtime receipt 不得 self-accept；Skill/model/provider success 也不触发 accept 或任何 Eikona 调用。

Reject 也需要当前用户明确批准，但必须保持 canonical Scene/Shot 零写入：

```bash
scaena storyboard breakdown reject <breakdown-ref> --project <project-path> --candidate <candidate-ref> --expected-version <version> --actor <human-actor-ref> --idempotency-key <stable-key> --confirm --json
```

### 8. 明确确认后导出；downstream 是独立 gate

CSV、JSON、Markdown 可用于人工审阅或下游交接；导出本身不等于 accept，也不等于 production-ready：

```bash
scaena storyboard breakdown export <breakdown-ref> --project <project-path> --candidate <candidate-ref> --format csv --output exports/storyboards/<name>.csv --idempotency-key <stable-key> --confirm --json
```

覆盖已有普通文件必须再得到明确授权并使用 `--overwrite`。不得绕过 path、symlink、formula-injection 或 checksum 门禁。MCP 对应 `scaena.storyboard.breakdown_export`；导出结果通过 `scaena://storyboard-export/{export_ref}` 读取。Accept 后可选 export 或 shot-planning handoff；批量出图/视频是新 paid downstream stage，必须再次展示已接受方向并获授权；本 Skill 不调用 Eikona。

## 失败路由

每个 typed code/state 只映射到明确 read-only next action，不允许隐式 mutation（换 key、换 model、提高 budget、取 latest source/Prompt）：

| Code/state | Skill action |
| --- | --- |
| `needs_format_decision` | 获取 format/duration/aspect 或走 format-strategy，不 run |
| `capability_missing` | 记录缺失 flag/命令，回退当前真实 async 路径，不伪造输出 |
| `PROMPT_BINDING_MISSING\|STALE\|CONFLICT` | inspect/sync/select exact address，不 provider call |
| `OWNER_CAPABILITY_UNVERIFIED\|OWNER_UNAVAILABLE` | doctor/config/handoff，不 fake candidate |
| `DATA_POLICY_UNVERIFIED\|DATA_POLICY_MISMATCH` | 更新 connection policy 或显式重新分类，不发送 source |
| `OWNER_INPUT_LIMIT_EXCEEDED\|OWNER_OUTPUT_LIMIT_EXCEEDED\|EPISODE_BOUNDARY_REQUIRED` | 拆集/新 direction/exact model 决策，不 truncate/chunk/fallback |
| `COST_CAP_REQUIRED\|COST_CAP_EXCEEDED\|COST_CAP_MISSING` | 请求新的明确成本决定，不提高 cap |
| `WAIT_TIMEOUT` | watch 原 ref，不 resubmit |
| `OWNER_TIMEOUT\|OWNER_ACCEPTANCE_UNKNOWN` 等 ambiguous outcome | reconcile：read-only status/watch 对账，不重放 mutation |
| `SEMANTIC_PLAN_SCHEMA_INVALID\|SEMANTIC_PLAN_FORBIDDEN_FIELD\|REPAIR_EXHAUSTED` | 显示 typed findings，停止或新 human-approved revise |
| `EXPECTED_VERSION_MISMATCH\|CANDIDATE_NOT_HEAD` | reload/diff current head，呈现 drift，不自动重试 |
| `BLOCKING_FINDINGS` | revise/patch/reject/export review copy，不 accept |
| `IDEMPOTENCY_CONFLICT` | 比较 intent，用户确认真新 intent 后才 new key |

模糊错误不得通过重提任务掩盖；保留真实 error code 与 redacted evidence。

## 边界

- 只调用真实 Scaena CLI、HTTP application surface 或列出的 MCP tools/resources；preflight 只用真实存在的命令。
- 不直接调用模型 provider SDK，不调用外部模型服务 CLI fallback，不持有 credential，不把 Prompt 正文复制进 Skill 输出。
- 不手写 SQLite、GORM rows、CAS、job、candidate、ProductionGraph、manifest、receipt 或 evidence metadata。
- 不因命令 exit zero、candidate 存在、export 成功或 fixture-only command 可用而声称 production-ready。
- 不自动提高成本、重放有歧义的 mutation、替换 idempotency key、覆盖文件、accept、reject、扩大项目 scope 或触发下游生成。
- 不把 `skill:scaena-storyboard-breakdown` 之外的未验证地址当作默认；不静默替换为 latest。

## 验证

- Default read、CLI JSON、HTTP 和 MCP 必须保持同一 refs/state/version/digest/counts/findings/actions/error codes。
- `EXPECTED_VERSION_MISMATCH` 后重新读取 current head；不要自动把 expected version 改成最新值并重试。
- `IDEMPOTENCY_CONFLICT` 表示同 key 的 intent 发生变化；不要用新 key 隐藏冲突，先确认用户是否真的发起新 intent。
- `BLOCKING_FINDINGS` 后只允许 review、revise、patch、reject 或 export review copy，不允许 accept。
- 保留 redacted evidence 和真实 error code，不保存 raw source、prompt 或 provider payload。

## 生产编译器门禁（current）

分镜进入付费媒体生成前，使用 production compiler 投影而非工程日志：

- 目标镜头选择 Seedance 2.5 时，读取 `../scaena-production-operator/references/seedance-2-5-scaena-mapping.md`。方向确认必须包含镜头时长、reference/keyframe 用途、声音策略与 output 目标；但分镜阶段不写 Ark wire hint，也不因官方能力声明跳过后续 Bundle/preflight。

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
