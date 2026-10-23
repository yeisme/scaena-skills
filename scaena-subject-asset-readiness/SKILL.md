---
name: scaena-subject-asset-readiness
description: Use when planning, drawing, reviewing, selecting, freezing, or operating Scaena character, location, prop, wardrobe, style, storyboard, shot, episode, cover, or motion assets, especially for DrawSession candidate-card workflows, dependency waves, subject identity, reference assets, human-only selection/freeze, shot bindings, generation preflight, or consistency before production visual generation.
---

# Scaena 主体资产就绪门禁

先确定可复用主体资产，再允许剧集生产。不要把成功命令、图片数量、Eikona feedback、Auctra acceptance、legacy `approved` 或相似度总分当成 Scaena production readiness。

## 必读参考

- 使用真实 `scaena asset draw plan|start|record|select|freeze|status|path` 命令做候选抽卡、依赖波次和冻结时，读取 [candidate-draw-workflow.md](references/candidate-draw-workflow.md)。
- 应用主体、rights、binding 和 generation preflight 门禁时，读取 [readiness-gates.md](references/readiness-gates.md)。

## 输入

- Scaena project、ProductionGraph、episode/shot/requirement 或已有 `resume_ref`。
- 视觉用途：`subject_candidate`、`look_development`、`shot_visual`、`episode_visual`、`cover_visual` 或 `motion_visual`。
- 已知 Auctra source refs、Eikona artifacts、Scaena assets/versions/bindings/preflight/consistency refs。

## 输出

返回紧凑门禁结果：

```text
status=<ready|blocked|candidate_only|stale>
purpose=<purpose>
subject_readiness=<passed|blocked|unknown>
missing_subject_refs=<refs>
missing_slots=<subject/slot>
frozen_version_refs=<refs>
draw_session_ref=<ref|none>
draw_state=<state|none>
candidate_count=<n>
candidate_cap=<n>
generation_preflight_ref=<ref|none>
blocking_codes=<codes>
allowed_next_mode=<subject_candidate|look_development|production|none>
next_command=<real supported command>
evidence_refs=<refs>
```

## 工作流

### 1. 先识别 owner 和用途

- Auctra 负责 accepted story identity、canon facts 与 visual brief。
- Eikona 负责 provider run、artifact、feedback、assessment 与 visual memory。
- Scaena 负责 production subject version、human freeze、shot binding、generation admission、consistency review 与 correction lineage。

如果请求是 Scaena episode/shot/cover/motion production，必须继续执行本门禁。不要直接进入 storyboard director、prompt 编写或 provider generation。

### 2. 检查当前真实状态

进入 `agent/scaena`，读取本地 `AGENTS.md`，只使用已安装版本真实支持的命令。先检查 help，再读取最窄投影：

```bash
scaena help
scaena asset draw --help
scaena asset center --project <project-path> --agent
scaena character bible show --project <project-path> --character <character-ref> --json
scaena production graph describe <production-graph-ref> --json
scaena shot board --project <project-path> --episode <episode-ref> --agent
scaena visual pack plan --graph <production-graph-ref> --json
```

当前 first-support 已提供 `asset draw` 命令组。先按 [candidate-draw-workflow.md](references/candidate-draw-workflow.md) 使用其真实 help；若某个 readiness/freeze/binding/preflight 子命令在 installed version 不存在，返回 `capability_missing` 和 owning OpenSpec；不要编造命令或手写 `.scaena`/SQLite 状态。

### 3. 运行候选抽卡与依赖波次

先计划 Wave 1 identity/style，再生成和登记最多 5 个候选，最后由 human actor 选择并冻结：

```bash
scaena asset draw plan --project <project-path> --asset <asset-ref> --brief <brief-ref> --wave 1 --json
scaena asset draw start --project <project-path> --asset <asset-ref> --session <draw-session-ref> --json
scaena asset draw record --project <project-path> --asset <asset-ref> --session <draw-session-ref> --eikona-run <eikona-run-ref> --digest sha256:<64-hex> --json
scaena asset draw select --project <project-path> --asset <asset-ref> --candidate <candidate-ref> --action accept --actor <human-actor-ref> --reason "<reason>" --json
scaena asset draw freeze --project <project-path> --asset <asset-ref> --confirm --json
scaena asset draw status --project <project-path> --asset <asset-ref> --agent
```

`record` 只是 refs-only 登记，不调用 provider。每个 slot 同时只有一个 active session；默认第 6 个候选触发 exhausted，必须修 brief 后重开。Wave 2+ 通过 `--requires` 依赖已冻结 slot。human-only select/freeze 不得由 Agent 伪造；冻结后仍要通过 production readiness/preflight。

🔴 CHECKPOINT · 🛑 STOP：未得到当前 human actor 明确授权前，不得 `select`/`freeze`，不得 `asset-batch dispatch` 付费派发，不得把 Eikona candidate 写成 Scaena frozen。

### 4. 区分 bootstrap 与 production

- `subject_candidate`、`subject_reference`、`look_development`：可在 accepted source/rights 就绪后自举；产物只能进入 candidate review。
- `shot_visual`、`episode_visual`、`cover_visual`、`motion_visual`、production storyboard keyframe：必须有 current passed generation preflight。

当主体未冻结时，最多路由到 `$eikona-subject-asset-director` 生成可比较候选；不得把候选绑定到 episode/shot。

### 5. 应用主体门禁

读取 [readiness-gates.md](references/readiness-gates.md)。至少检查：

- accepted source version/digest；
- unique active frozen project style；
- required primary/secondary subject versions；
- wardrobe continuity variants；
- recurring location 与 story-critical prop anchors；
- rights/permission；
- exact shot bindings；
- model reference capability；
- capability maturity、task policy、reference media role/count、ratio/duration/output/audio policy；Seedance 2.5 映射见 `../scaena-production-operator/references/seedance-2-5-scaena-mapping.md`；
- current graph/binding/subject versions；
- blocking continuity findings。

任一 production-required fact 缺失时，返回第一组可操作 blockers，并把 `allowed_next_mode` 限制为 candidate/lookdev/repair。不要因为 `visual pack plan` 或旧 render 命令返回 success 就放行。

### 6. 把 fail-open 当成缺陷

以下任一情况都不是“可继续”：

- production visual request 的 `reference_asset_refs` 或 `style_pack_ref` 为空；
- named required subject 没有 frozen version；
- request 没有 `generation_preflight_ref` 或 preflight 已 stale；
- `--confirm` 是唯一生成前置条件；
- repository-test/direct ingest accepted 被当成 frozen；
- Eikona accepted candidate 被当成 Scaena production accepted；
- 机器一致性总分直接触发 accept。

发现上述行为时，停止 production generation，记录 bypass path、affected refs 和 owner-call risk。若任务是实现/修复，路由到 Scaena owning OpenSpec；若任务是操作，返回主体候选或 repair 的下一步。

### 7. 生产请求必须固定版本

只有 current passed preflight 才允许继续。确认 request 固定：

```text
generation_preflight_ref/digest
subject_version_bindings
reference_asset_version_refs
style_pack_version_ref
requirement_version_refs
expected_graph_version
```

这些版本随后必须进入同一条不可变执行链：`ShotIntent` 固定叙事与连续性意图，`ShotGenerationSpec` 固定 capability/output 解释，`VideoGenerationInputBundle` 固定实际输入版本。主体 preflight 是这条链的前置门禁，不是三种对象的替代品；三种对象也不能反过来替代主体冻结、rights 或一致性审阅。

如果 intent/spec/bundle 任一对象引用了“最新版本”、遗漏 frozen subject/style/reference version、与 ProductionGraph 版本不一致，或 digest 已 stale，则返回 `stale`/`blocked`，owner call count 必须为零。

模型官方支持 50 引用、纯音频、1080p 或 MOV 不能替代本地 capability snapshot。
主体/参考 binding 只放当前镜头需要的最小集合；数量虽未超 provider 上限但用途、ordinal、
rights 或 continuity 不明确时仍要阻断。

plan 与 submit 都要检查；submit 前状态变化必须返回 stale，不能自动换成“最新角色”。

### 8. 生成后回到一致性审阅

镜头产物默认进入 human consistency review。逐主体检查 identity、face/hair、silhouette、wardrobe、location layout、prop geometry、style、shot fit 与 rights。机器 assessment 只能分流；correction 创建 derived candidate，不覆盖 source asset。

### 9. 结束时给出可恢复 handoff

只返回 refs、blockers、allowed mode、下一条真实命令与 evidence。不要粘贴完整 canon、raw prompt、provider payload、embedding、private path、credential 或完整模型推理。

## 边界

- 不直接调用 provider SDK，不手写 Eikona/Scaena structured state。
- 不把 legal `SubjectBinding` 当作视觉身份冻结。
- 不让 background exception 覆盖 named/close-up/recurring/continuity-relevant subject。
- 不因用户要求“先出几张看看”而把 lookdev 伪装成 production asset。
- 不自动接受、冻结、改绑、批量重绘或写入 visual memory。
- 不手建 `assets/<asset-id>/draws/<seq>/candidate.png`；只使用 `asset draw path` 返回的标准路径。
- 不把 `selected`/`frozen` 当作 production-admitted、shot-accepted 或 export-ready。
- 不因 Aigora 返回成功回执而跳过 Scaena human consistency review；Phase 0 外部 artifact ref 只能进入 `pending_review`。

## If this fails

| Trigger | First fix | Still failing |
| --- | --- | --- |
| Production request missing frozen version / preflight | Return `blocked` with first blockers; `allowed_next_mode=candidate_only` | Do not generate episode/shot assets |
| Installed command missing | `capability_missing` + owning OpenSpec | Do not invent CLI or write `.scaena` |
| Eikona accepted / similarity score | Keep as candidate | Do not treat as Scaena frozen |
| 6th candidate exhausted | Repair brief; reopen session | Do not raise the cap silently |
| Stale graph/binding/digest | `stale`; owner call count = 0 | Do not swap in “latest character” |

## 验证

- 每个 production entrypoint 都必须有 bypass-negative evidence；blocked 时 owner call count 为零。
- exact test name 必须先用 `go test -list` 确认存在；宽泛或零命中 `-run` 不算证据。
- first-support 必须覆盖 restart、two-project isolation、stale preflight、correction lineage 和标准 integration evidence 六件套。

## 批次与稳定性认证（current）

分镜资产批次与稳定性认证命令族（2026-08-26 已实现）：

- 批次计划（零 provider 调用）：`scaena storyboard asset-batch plan --project .
  --breakdown <ref> --candidate <ref> --kind foundation_assets|shot_keyframes --json`；
  `review_candidate` 下 foundation 只标 provisional；`shot_keyframes` 要求 subject
  frozen + prompt ready + binding current，否则 blocked。
- 付费派发：`scaena storyboard asset-batch dispatch --plan <plan-ref> --max-cost-usd N
  --eikona-endpoint <url> --confirm --json`；partial 只重试失败子集：
  `retry --dispatch <ref> --failed-only --confirm`。owner 端点缺失即 fail closed。
- 采纳：`scaena storyboard asset-batch adopt --artifact-batch <ref> --plan <ref>
  --artifacts <ref,ref> --confirm --json`；只按 typed artifact ref/digest 的显式
  成功集合采纳，进入 pending review，不推断 frozen/tested/admitted。
- 稳定性认证：`scaena asset stability plan|run|status|verdict|certify`；verdict/
  certify 只接受 human actor；certificate pass 不自动 admission——admission 仍需
  人工 `apply`，且已认证主体必须有 current certificate（stale/digest 漂移阻断）。
