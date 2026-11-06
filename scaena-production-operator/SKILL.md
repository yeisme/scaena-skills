---
name: scaena-production-operator
description: Use when planning, running, resuming, repairing, reviewing, assembling, refining, exporting, or verifying a Scaena short-drama or comic-drama production from accepted Auctra screenplay through storyboard breakdown, subject-card DrawSessions, frozen assets, accepted shots, episode preview, timeline variants, defect-routed refinement, delivery review, and export package.
---

# Scaena Production Operator

## 资源发现

分镜模型先 `scaena model provider list --agent`，从 `fact.provider.N.id` 选真实 id，再 `scaena model provider describe <provider-id> --agent`；身份摘要用 `get`。缺参/未知 id 的恢复动作来自 envelope，不能猜表格或把 0 connections 当成任意 id 有效。先确认安装版支持 canonical 路径，缺失时报告版本差异。视频目录继续使用已发布的 flag 形式。Tab 安装使用 `scaena completion install zsh --yes`，诊断使用 `scaena completion doctor zsh --agent`；不修改 rc。

Operate Scaena as a staged production system. Do not equate generated files, fixture duration, or successful commands with a production-ready episode.

## 统一模型入口与后台渠道选择

用户按模型生成且允许跨渠道时，优先读取 `scaena://video-tasks/guide` 的 `model_routing` 和 bindings。若运行版本提供该能力，调用 `createVideoProviderTask` 时填写 `model`、`duration_seconds`、`resolution`、`ratio`，不传 `binding_id`；模型 ID 和参数必须来自实时能力发现。服务按配置权重筛选兼容绑定，真实选定渠道以返回的 binding_id/channel 为准。一个可用绑定不等于跨渠道生产分流已经验收。

固定渠道/只走官方的用户要求继续使用明确 binding_id，不进入混合渠道池。不要同时传 model 与 binding_id。旧运行版本没有 model_routing 时沿用实际 schema，不发送不存在的字段。

保留原创建幂等键及 submission_ref；后台改权重/新增渠道后重复创建仍读取原任务。已受理或未知受理不能换渠道重提；reconcile 查询原路由。参考图复用原 upload，备案和人物授权继续逐渠道校验，不能因为模型名相同就跳过。


官方 MiniMax/Wan3/Seedance 路由、默认绑定、错误恢复：`references/official-routing.md`。

## 必读参考

- 比例、分辨率、视频底部/动作出画及错误切换：[video-canvas-recovery.md](references/video-canvas-recovery.md)。新自动恢复合同为planned，先发现安装版本的真实入口。

- 生产阶段、owner 和 gate： [production-gates.md](references/production-gates.md)。
- 整集拼接、timeline 选版、缺陷分类、有界精修和 export： [episode-refinement-loop.md](references/episode-refinement-loop.md)。
- 主体抽卡、依赖波次、human-only select/freeze：`$scaena-subject-asset-readiness` 的 `references/candidate-draw-workflow.md`。
- Seedance 2.5 task policy、capability maturity 与 Bundle/adapter 边界：[seedance-2-5-scaena-mapping.md](references/seedance-2-5-scaena-mapping.md)。
- 官方 MiniMax/Wan3/Seedance 路由与错误恢复：[official-routing.md](references/official-routing.md)。
- 12 步命令细节：[workflow.md](references/workflow.md)。
- Quick capture 与单文件 intake：[intake.md](references/intake.md)。

## Inputs

- Project path and source screenplay or existing `resume_ref`.
- Target duration, platform, aspect ratio, episode scope, quality tier, cost ceiling, and external-side-effect policy.
- Existing ProductionGraph, accepted asset, quality, preview, timeline, export, and evidence refs.

## Output

Return a compact stage receipt:

```text
status
stage
run_ref
target_duration
covered_duration
accepted_refs
failed_refs
blocking_findings
originality_decision_ref
subject_readiness
draw_session_refs
frozen_subject_version_refs
generation_preflight_ref
shot_intent_ref
shot_audio_intent_ref
shot_audio_intent_digest
provider_audio_policy
video_task_policy_ref
video_capability_maturity
shot_generation_spec_ref
video_input_bundle_ref
video_run_ref
aigora_job_ref
import_receipt_ref
review_state
audio_review_state
final_mix_ref
episode_preview_ref
edit_plan_ref
selected_timeline_ref
selected_cut_ref
refinement_findings
repair_receipts
delivery_review_ref
export_receipt_ref
next_command
resume_ref
evidence_refs
```

Use `--agent` for routine inspection and handoff. Use `--json` only when exact nested fields are required. Never paste raw provider payloads, full logs, hidden prompts, private tool arguments, or full chain-of-thought into the conversation.


## Workflow

Follow `references/workflow.md`. Outline only:

1. Inspect before mutating (`scaena doctor` / board / graph). Do not invent missing CLI verbs.
2. Import canonical Auctra handoff with `--confirm`. Import does not freeze subjects or authorize video.
3. Confirm storyboard direction with the current user before paid generation.
4. Lock brief and timing. `sum(shot.duration) < target` is blocking.
5. Lock subject foundation via `$scaena-subject-asset-readiness`; DrawSession select/freeze is human-only.
6. Freeze one-shot lineage: ShotIntent → ShotGenerationSpec → VideoGenerationInputBundle. Do not invent a freeze CLI.
7. Produce in batches; `asset subject bind` is not visual freeze.
8. Review picture and sound independently; resume/repair instead of replaying.
9. Preview progressively; probe real duration with `ffprobe`.
10. Assemble only accepted segments; classify defects to the owning successor.
11. Export only after completion gates; omitting `--confirm` is not a zero-write preview.
12. End with the compact receipt and `resume_ref`.

Quick capture and file intake: `references/intake.md`.

## Boundaries

- Keep Scaena as the short-drama production truth; do not reimplement ProductionGraph or acceptance in Studio Backend skills.
- Keep Eikona as visual run/artifact truth; do not call provider SDKs directly.
- Keep Auctra source acceptance, Eikona candidate feedback, Scaena subject freeze, and Scaena shot acceptance as separate decisions.
- Treat Aigora `unknown_accept` as “observe/reconcile the original execution”, never as permission to submit again.
- Treat an Aigora success receipt as a safe external artifact reference in Phase 0. It becomes a Scaena `pending_review` projection, not an accepted production asset and not proof that bytes were copied into CAS.
- Do not generate Scaena production visuals without a current passed generation preflight.
- Do not bypass the current-user storyboard-direction confirmation before paid image, video, or voice generation.
- Do not treat renaming, face/color swaps, synonym rewrites, frozen subjects, high quality scores, or successful export as proof of originality or rights clearance.
- Do not overwrite an accepted source, selected candidate, timeline, cut, mix, or export during refinement; create successor refs and preserve lineage.
- Do not claim completion from file counts, fixture success, or command exit zero alone.
- Do not publish, spend externally, delete, or batch mutate without explicit authority.
- Do not edit `.scaena` structured files, SQLite rows, manifests, receipts, or evidence metadata by hand.

## Validation

Native Video channels are `kie` and `openrouter`, with exact channel-specific model IDs. Inspect `scaena://video-tasks/guide` and binding capabilities before creation; no automatic channel/model fallback or paid replay. Use latest executable contracts only; historical is query/reconcile-only, unverified tools remain unavailable. Catalog, provider, credential, model and pricing readiness are separate. Unknown outcome keeps the original task ID and idempotency binding. Native polling is implemented; third-party callback ingress and catalog-only edit/upscale/lip-sync entries must not be described as executable. Local fixtures, health checks and catalog presence do not prove a live image/video delivery. Read owner protocol support tables before selecting references, duration, resolution, ratio, audio or seed.

- Verify subject readiness/frozen versions/preflight first, then ProductionGraph duration and requirements, quality/continuity findings, preview media duration, review state, and export readiness independently.
- Treat a production request with missing reference/style/preflight facts as a blocking defect even if a command returns success.
- Preserve integration evidence under `temp/integration-test-runs/<run-id>/` with redaction and original exit codes.
- For the single-shot Aigora canary, keep `owner.aigora_video_canary_enabled=false` by default. Validate an explicit local/service config with `scaena-production-worker config validate --config <path>`; never place credentials in tracked config or evidence.
- Run `task test:integration` for the six-piece evidence bundle before promoting beyond first-support.
- Prefer focused project commands; do not run root-wide scans or read both generated skill mirrors.

## If this fails

| Trigger | First fix | Still failing |
| --- | --- | --- |
| Missing command in installed CLI | `scaena help`; record capability gap | Do not invent verbs or hand-write `.scaena` |
| `outcome_unknown` / unknown accept | Keep original idempotency + `submission_ref`; reconcile | Do not switch model or recreate |
| Credential missing | Report config gap | Not “model not adapted” |
| Shot images exist but duration short | Coverage vs target duration is blocking | `--episodes 3` ≠ three minutes |
| Paid gen before storyboard confirm | Stop; present spine/beats to the user | Do not treat fixture success as production |
| DrawSession without human select | Human-only accept/freeze | Do not invent candidate paths |
| Aigora success treated as accepted asset | `pending_review` only | Bytes in CAS require import + review |
| Export with blocking findings | Fail closed | Draft `--to` still writes a managed manifest |

## 执行内核接入（DEK v1）

`defect-routed refinement` 与失败重提按「技术替换 vs 创意修改」分岔，交 `scaena-bounded-replacement`：

- 只有 `identity_equal`（复用本文执行前校验列表：`project / ProductionGraph / shot / frozen intent / spec / bundle / capability / task policy / duration / ratio / audio / subject / style / reference versions / ordinals / idempotency key`，另加 speaker / timbre / original audio source / dialogue / model / channel）全部相等，才允许技术替换并跳过创意复核；
- 任一创意字段变化 → 退回完整创作批，新 `idempotency_key` 与新授权，禁止借「原样重提」授权换模型、改正文或改时长；
- 失败视频只在原返回 ID 终态 `FAILED`、实时回读仍 `FAILED`、原配置逐字段全等时原样重提，共享 `claim_key` 防并发重投；
- `unknown_accept` 保持原幂等键与 `submission_ref`，只 `reconcile`，与本文既有规则一致；
- 状态词汇与恢复决策统一引用 `ai-drama-action-receipt`。

完整 EU 目录与 C3 合同见 `https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/execution-units.md`。本 Skill 仍是 Scaena 生产的唯一操作 owner，不因接入 DEK 新增第二条写入路线。
