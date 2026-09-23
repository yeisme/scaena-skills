# 路由与 provider-free preflight

进入付费 run/revise 前先完成本参考的 intake、profile 路由、PromptRepo 绑定与 preflight。整个 preflight 的 provider/owner 调用数必须为 0；durable write 只允许 source import 之后的业务步骤，preflight 本身零写入。

## Required intake facts

只问会改变结构或成本的最少事实；project 已有 accepted profile/direction snapshot 时复用 exact ref/digest，不重复提问：

- project/source/episode（一次一集；多集输入见下文 episode boundary）。
- format/profile，或足以确定 profile 的 accepted project fact。
- target duration、aspect、shot range（可来自 profile defaults）。
- exact Prompt template address（可用官方默认）。
- owner connection、exact `provider/model`、cost cap、attempts、fallbacks。
- execution host：local CLI 或 remote/API/MCP。
- exact episode boundary 与 owner capability input/output estimate。
- source classification（public/internal/confidential）、execution policy，以及 provider retention/training/region facts。

缺失且会改变分镜结构的 format/duration/aspect：返回 `needs_format_decision`，先走 `ai-drama-format-strategist` 或询问用户；不得只看剧本文风猜 profile。

## Profile routing

| Evidence | profile_id | Maturity |
| --- | --- | --- |
| accepted vertical short-drama project + 9:16/60-90s | `vertical-short-drama-v1` | first-support |
| explicit dialogue-preservation job | `dialogue-dense-v1` | exploratory |
| explicit manga/dynamic-comic storyboard | `manga-panel-v1` | exploratory |
| explicit 15-30s product/CTA microdrama | `ad-microdrama-v1` | exploratory |
| ambiguous/conflicting | none | `needs_format_decision` |

Scaena direction contract 还携带 `horizontal-short-drama-v1`、`anthology-episode-v1`、`comedy-sketch-v1`（均 exploratory）；同样只在用户明确给出 evidence 时使用。Exploratory profile 可运行 provider-free fixture/component；live run 前必须展示 maturity 并让用户确认实验性质。选择结果写入 receipt 的 `profile_id`/`profile_maturity`，并把对应 `--direction-profile` 传给 Scaena。

## PromptRepo compatibility mapping

默认 exact address：

```text
promptrepo://official/video/ai-drama-storyboard-breakdown@1.0.0?locale=en
```

语言约定：编译与投递只使用 en 模板；zh-CN 为人工审阅译文，不进入编译。

Legacy 入口：

```text
skill:scaena-storyboard-breakdown + version=1
```

`--instruction-profile`（默认 `skill:scaena-storyboard-breakdown`，`--instruction-profile-version` 默认 1）只是 compatibility ingress；命令优先使用 `--prompt-template '<exact address>'`。Skill 不读取、不复制、不缓存 Prompt body；receipt 只保留 snapshot ref/digest/locale/maturity。用户明确给出另一个 exact address 时，先 inspect/validate 并向用户展示 ref/digest/maturity，不静默替换为 latest，也不在 digest 漂移后继续执行。`--auctra-handoff-ref` 默认不可用（nil client）；opt-in file 模式见 Scaena `docs/protocols/auctra-bridge.md`。先 `scaena handoff auctra import --from <handoff.json> --confirm` 或配置 `storyboard_auctra` 后再用该 flag。

## Provider-free preflight（真实命令）

只引用当前真实存在的命令；先核实再使用：

```bash
scaena storyboard breakdown run --help
scaena storyboard breakdown watch --help
scaena storyboard breakdown diff --help
scaena storyboard breakdown show --help
scaena production status --project <project-path> --json
scaena prompt-asset repository doctor --json
scaena prompt-asset catalog inspect 'promptrepo://official/video/ai-drama-storyboard-breakdown@1.0.0?locale=en' --json
scaena prompt-asset catalog validate 'promptrepo://official/video/ai-drama-storyboard-breakdown@1.0.0?locale=en' --json
```

Preflight 输出这些 facts：source/profile/direction/prompt identity（ref/digest）、owner readiness（`scaena.storyboard_model.v1` capability state/verification/production_ready）、connection/config readiness、estimate 与 cost cap。`repository doctor` 与 `catalog inspect/validate` 的 envelope 自带 `provider_calls` 字段，必须为 0；catalog inspect 需返回 `ready=true` 与预期 digest/locale，validate 需无 blockers。

**capability_missing 规则：** 若 `run --help` 没有 `--foreground`，或 `watch`/`diff`/`show --view` 不存在，标记该便利能力缺失并使用当前真实 async `run`/`show` 路径；不得发明 flag、不得把设计文档中的目标命令当作已实现、不得伪造输出。help/status/doctor/inspect/validate 全部零 provider 调用、零 durable write（source import 除外）。

## Episode boundary 与 owner limits

付费执行前确认一集 exact episode 加上 Scaena readiness 给出的 segment/request/token/delivery/scene/shot limit estimate。遇到 `EPISODE_BOUNDARY_REQUIRED`、`OWNER_INPUT_LIMIT_EXCEEDED`、`OWNER_OUTPUT_LIMIT_EXCEEDED` 或超限 estimate 时：提供拆集、选择新 exact model、或调整明确 direction 的决策。不允许截断、隐式 chunk、跨集合并、循环提交或静默 fallback；multi-episode batch 是后续 Scaena orchestration surface，不用循环 shell 命令伪造 canonical batch state。

## Source classification 与 execution policy

Confidential source 需要先有匹配的 immutable execution policy：

```bash
scaena storyboard execution-policy create --project <project-path> --source-classification confidential --retention no_retention --training disallowed --region <allowed-region> --json
scaena storyboard execution-policy show --project <project-path> --json
```

Policy 与 provider retention/training/region 事实不匹配时返回 `DATA_POLICY_UNVERIFIED`/`DATA_POLICY_MISMATCH` blocker，并给出 connection-policy 更新或显式重新分类的 next action；不发送 source，不提供 generic "proceed anyway" 确认。Receipt 记录 `source_classification`、`execution_policy_ref`、data policy ref 与 retention_mode/training_usage/processing_regions/policy_expiry。

## Local foreground 与 remote/MCP async

Local verified runtime：

```bash
scaena storyboard breakdown run ... --foreground --timeout 10m --events
```

等待到 `review_required|failed|cancelled|WAIT_TIMEOUT`。超时后保留原 ref 并：

```bash
scaena storyboard breakdown watch <breakdown-ref> --project <project-path> --timeout <duration> --json
```

不新建 idempotency key、不 resubmit、不隐式 cancel。

Remote/API/MCP：调用 async run 拿到 breakdown ref 后走 `run -> status/resource -> review -> revise/patch -> status -> accept/reject/export`。宿主可管理 poll interval/notification，但 Skill 不在 tool call 里长时间阻塞，也不因等待而重新 submit；queued 不等于 generated candidate。

## Stable idempotency 与 approval packet

run/revise 前向用户呈现完整 packet：

```text
source_ref/digest + source_classification
direction_profile/ref/digest + duration/aspect/shot range
prompt template address/digest/locale/maturity
owner readiness/capability receipt
source classification + execution policy ref/digest
provider data policy ref/digest + retention/training/regions/expiry
connection_ref (not secret)
exact provider/model + fallbacks
max_attempts
max_cost_usd
write/cost effect
```

只有当前用户对已展示 packet 明确确认后才执行一次 mutation。“继续/看看/下一步”只算 read-only continuation 授权；除非当前消息明确批准已展示的 cost-bounded mutation，否则不得执行。Stable idempotency key 必须绑定同一 intent；`IDEMPOTENCY_CONFLICT` 后先比较 intent，不换 key 掩盖冲突。Confidential policy mismatch 不提供 generic bypass。
