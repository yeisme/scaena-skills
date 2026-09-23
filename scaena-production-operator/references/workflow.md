## Workflow

### 1. Inspect Before Mutating

Enter `agent/scaena`, read its `AGENTS.md`, and locate the project. Inspect the narrowest current state:

```bash
scaena doctor --agent
scaena board --project <project-path> --agent
scaena workflow status <workflow-run-ref> --project <project-path> --agent
scaena production graph show <production-graph-ref> --json
```

选视频模型前先离线区分「代码已适配」和「本机已配置」。缺凭据不得说成模型未适配；成功 list 也不等于 production-ready：

```bash
scaena video model list --json
scaena video model show --model <model-id> --json
scaena video auth list --json
scaena video health --model <model-id> --json
```

源码与协议文档还提供 `scaena video provider list`、`scaena video provider show --provider <id>` 和 `scaena video model choose`。若当前安装版本的 `scaena video --help` 没有这些子命令，记录 capability gap，改用已存在的 `video model list` / `video auth list` / `video health`，不要发明命令。

If a referenced command is unavailable in the installed version, run `scaena help` or the relevant command-group help and use the supported equivalent. Do not invent a replacement command or hand-write `.scaena` state.

### 2. Import The Canonical Auctra Handoff

Inspect before writing, then require explicit confirmation for import:

```bash
scaena handoff auctra inspect --project <project-path> --from <handoff-file> --json
scaena handoff auctra import --project <project-path> --from <handoff-file> --confirm --json
scaena handoff auctra show --project <project-path> <receipt-ref> --json
```

Accept only a valid `auctra.production_handoff.v1` producer package or an explicitly reported legacy compatibility projection. Verify the producer `canon_digest`; preserve `source_project_ref`, `source_revision`, scene/action/dialogue refs, and import receipt mappings. Import does not accept generated visuals, freeze subject identity, or authorize video execution.

Reject corpus items, semantic overlays, Pattern Lens evidence, dramatic recipes, holdout refs, raw video observations, or Studio client state as screenplay input. Those sources must first pass Auctra project linking, candidate generation, human review, and accepted screenplay export. Do not reconstruct missing canon inside Scaena.

#### 2A. Break Down And Confirm Storyboard Direction

Use `$scaena-storyboard-breakdown` and the installed command help:

```bash
scaena storyboard source import --help
scaena storyboard breakdown run --help
scaena storyboard breakdown show --help
scaena storyboard breakdown revise --help
scaena storyboard breakdown patch --help
scaena storyboard breakdown accept --help
scaena storyboard breakdown export --help
```

Before any paid image, video, or voice generation, explicitly present the story spine, per-shot beats, dialogue backbone, visual tone, and shot/episode duration contract to the current user. Require their confirmation. Use `revise` for structure, semantics, or source mapping; use typed `patch` only for supported local fields. Only an accepted breakdown may enter subject-card drawing or shot production.

### 3. Lock Brief And Timing

Confirm target duration, platform, aspect ratio, episode interpretation, canonical screenplay ref, scene/beat scope, and approval policy before image generation.

Calculate coverage from ProductionGraph shot durations. Treat `sum(shot.duration_seconds) < target_duration` as blocking even when every existing shot has an image. For a 180-second target, 10 five-second shots cover only 50 seconds.

Create or revise the production plan through Scaena commands and record the resulting refs. Do not treat `--episodes 3` as equivalent to a three-minute target.

### 4. Lock Subject Asset Foundation

Before any episode, shot, cover, keyframe, or motion generation, use `$scaena-subject-asset-readiness`.

Require accepted source facts, a frozen project style, frozen primary/secondary subject versions, required wardrobe/location/prop anchors, exact shot bindings, rights, and a current generation preflight. Legal filing/permission binding alone is insufficient.

If the installed Scaena version lacks readiness/freeze/preflight commands, report the capability gap and stop production generation. Do not use a successful `visual pack plan/render`, fixture accepted state, empty `reference_asset_refs`, or `--confirm` as a substitute.

Only `subject_candidate`, `subject_reference`, and `look_development` may proceed before freeze, and their outputs must remain non-production. Route candidate creation or correction to `$eikona-subject-asset-director`.

#### 4A. Run The Real Subject-Card Draw Loop

For every required character, style, recurring location, wardrobe, or story-critical prop slot, use Scaena's DrawSession commands:

```bash
scaena asset draw plan --project <project-path> --asset <asset-ref> --brief <brief-ref> --wave 1 --json
scaena asset draw start --project <project-path> --asset <asset-ref> --session <draw-session-ref> --json
scaena asset draw record --project <project-path> --asset <asset-ref> --session <draw-session-ref> --eikona-run <eikona-run-ref> --digest sha256:<64-hex> --json
scaena asset draw select --project <project-path> --asset <asset-ref> --candidate <candidate-ref> --action accept --actor <human-actor-ref> --reason "<reason>" --json
scaena asset draw freeze --project <project-path> --asset <asset-ref> --confirm --json
scaena asset draw status --project <project-path> --asset <asset-ref> --agent
```

Wave 1 locks identity/style; later waves use `--requires` for already frozen dependencies. One slot has one active session and a default cap of five candidates. `record` registers an existing Eikona run and does not call a provider. Candidate selection and freeze are human-only. Never hand-create candidate paths; use `scaena asset draw path`. Frozen subjects still require current generation preflight and exact shot bindings.

#### 4B. Upload Remote Reference Media

远程本机图片、视频或音频进入项目时，先发现 `scaena://upload/guide` 与会话管理能力：`createUploadSession`、`getUploadSession`、`completeUploadSession`、`abortUploadSession`。缺少 backing 时报告 `OWNER_UNAVAILABLE`，交回 Scaena owner 配置；不要伪造会话或改用服务端读取客户端路径。

按「选择本机文件 → MCP 创建会话 → 客户端 HTTP PUT 分片 → MCP complete → canonical upload ref → finalize / binding / admission」执行。会话只传 `file_name` 基名；字节走 `PUT /api/v1/projects/{project_id}/upload-sessions/{session_id}/parts/{part_number}`，带 `Content-Digest: sha256=<hex>` 和分片幂等键。`putUploadSessionPart` 的 `use_http` 表示 HTTP 数据面，禁止把媒体 base64 放入该旧动作的 MCP JSON；专用 input.upload_base64 的小文件例外见后文。已安装 CLI 的等价整文件流程为：

```bash
scaena upload file ./clip.mp4 --endpoint http://server:8080 --key-file /absolute/private/scaena.key --project project_01 --json
scaena upload session upload_session_xxx --endpoint http://server:8080 --key-file /absolute/private/scaena.key --project project_01 --agent
scaena upload abort upload_session_xxx --endpoint http://server:8080 --key-file /absolute/private/scaena.key --project project_01 --json
```

local 指 owner 服务端磁盘，不依赖 S3；既有 `platform storage` 对象存储流程保持独立，不混用 endpoint 或凭证。完成上传只确认传输校验，finalize 后仍为 `needs_review`；后续 rights、review、绑定与付费生成门独立生效，不自批或扩展 project/purpose 权限。

先读取 guide 的实际 `limits`，不要把默认值当成实例配置。项目默认预留 128 个会话、2 GiB，总量由同项目 actor 共享；完成上传继续占用配额。`QUOTA_EXCEEDED` 时放弃不再使用的未完成会话，或交回 owner 清理过期数据、调整限制；`OWNER_UNAVAILABLE` 的 503 表示处理容量或清理不可用，507 表示存储空间不足，恢复后查询会话并沿用原 key 重试。owner 主机可运行 `scaena-api upload gc --config /absolute/private/scaena-gateway.yaml --agent`，只回收过期或孤儿临时数据，不删除已完成上传。配置入口为 `scaena-api config set --help`；不要从远程客户端假定拥有 owner 主机配置权限。

恢复时先查会话，仅重传缺失片；`DIGEST_CONFLICT` 不盲目重试，先核对源文件；`CURSOR_EXPIRED` 新建会话；`ILLEGAL_TRANSITION` 查询终态；磁盘问题排除后使用原 key 重试同片。URL-only provider 返回 `PRODUCTION_NOT_READY` 时交回 owner 检查 delivery route 与实际可达性，不能仅凭上传成功声称 Provider 可用。输出只保留状态、refs 和恢复步骤，不暴露 grant、token 或私有路径。当前安装缺少这些命令时使用真实 help/discovery 并报告版本缺口。

### 5. Build Asset Budget

Budget reusable and per-shot requirements before generation:

- character identity, costume, expression, pose, and continuity variants;
- locations, establishing views, lighting/time variants, props, and rights;
- per-shot keyframes, motion clips, voice, music, SFX, subtitles, and transitions;
- provider attempts, cost ceiling, review batches, fallback, and reuse refs.

Use average shot duration only as a planning estimate. The hard gate is complete timeline coverage plus accepted requirements. Read [production-gates.md](references/production-gates.md) for the required gate matrix.

### 6. Freeze One Shot For Generation

The immutable single-shot lineage is:

```text
Auctra accepted scene spans
  -> Scaena ProductionGraph shot
  -> frozen ShotIntent
  -> frozen ShotGenerationSpec
  -> validated VideoGenerationInputBundle
  -> admitted VideoRun
  -> Aigora execution receipt
  -> Scaena pending-review asset + import receipt
```

`ShotIntent` owns narrative intent, timing, composition, action phases, camera, continuity, audio intent, and exact source refs. Audio intent must bind the versioned `ShotAudioIntent` plan/digest described by `$ai-drama-router`'s `references/shot-audio-intent-contract.md`; a free-text sound label is not sufficient. `ShotGenerationSpec` compiles that frozen intent against one capability/output contract. The spec must reference the intent digest; the bundle references both intent and spec digests. Never add the bundle digest back into the spec, which would create a digest cycle.

For Seedance 2.5, the spec/bundle also freezes provider-neutral task intent, reference roles/ordinals/counts, ratio/duration lock, output/audio policy and capability maturity. The Ark-only `omni_reference_task_type` is adapter-derived and must not appear as a caller-authored canonical field. A local descriptor, fixture, or provider-smoke receipt does not by itself establish `production_ready`.

Before video generation, require an explicit audio policy: `none | external_assets | video_native | replace_after_generation`. If the selected model can or may emit native audio and rights/sync/editability/review are not all known, default to `replace_after_generation`. Missing `ShotAudioIntent`, missing Sonora replacement route, or capability/audio-policy mismatch is a generation blocker.

Before owner execution require all of the following to match: project, ProductionGraph ref/version, shot ref, frozen intent ref/digest, frozen spec ref/digest, validated bundle ref/digest, capability ref/digest/maturity, task policy, duration/ratio/output/audio policy, exact subject/style/reference versions and ordinals, and a non-empty idempotency key.

The current first-support exposes these contracts through the Scaena SDK/application service and Studio `VideoRun` API. It does not yet publish a stable CLI command for freezing or compiling `ShotIntent`/`ShotGenerationSpec`. Do not invent one or hand-write persisted state. When validating an implementation or local canary, use the real focused checks:

```bash
export SCAENA_REPO=/path/to/scaena
cd "$SCAENA_REPO"
go test ./internal/application/studio -run 'ShotGenerationService|BindShotGenerationLineage' -count=1
go test ./tests/integration -run SingleShotAigoraUnknownAcceptReconcileLoop -count=1
```

### 7. Produce In Batches

Process one episode, scene group, or shot batch per session. Reuse accepted assets and skip completed nodes. Use Eikona through supported Scaena/Eikona API or SDK workflows; do not create provider scripts or service-side CLI fallbacks.

Inspect and bind production assets with commands such as:

```bash
scaena asset center --project <project-path> --agent
scaena character bible show --project <project-path> --character <character-ref> --json
scaena asset subject bind --graph <production-graph-ref> --character <character-ref> --filing <filing-id> --permission licensed --json
scaena visual pack plan --graph <production-graph-ref> --json
scaena shot board --project <project-path> --episode <episode-ref> --agent
```

`asset subject bind` only establishes filing/permission facts; it does not freeze visual identity. Generated Eikona artifacts become production assets only after import, exact frozen-version binding, rights checks, current preflight, and Scaena consistency review acceptance.

### 8. Review And Repair

Run quality and continuity checks before motion preview:

```bash
scaena quality check --graph <production-graph-ref> --json
scaena continuity check --project <project-path> --scope <episode-ref> --json
```

If blocked, load only the finding, affected refs, and repair action. Resume or repair instead of replaying the whole workflow:

```bash
scaena workflow resume <workflow-run-ref> --project <project-path> --json
scaena workflow repair plan --run <workflow-run-ref> --json
scaena workflow repair run --repair <repair-ref> --json
```

Never overwrite a canonical state with a hand-authored report. When report and projection disagree, treat CLI/application state and evidence refs as authoritative and record the drift as a finding.

Review picture and sound independently. A visual pass must not propagate to the native audio track. Register provider-native audio through Sonora as `video_native_audio`; keep it pending review or replacement-required until rights, sync confidence, dialogue/voice, editability and duration checks pass. When the plan says `replace_after_generation`, bind the returned Sonora voice/SFX/music/mix refs before assembly.

### 9. Preview Progressively

Run preview gates in order and stop on blockers:

```bash
scaena video motion-preview --graph <production-graph-ref> --mode probe --confirm --json
scaena video motion-preview --graph <production-graph-ref> --mode preview-batch --confirm --json
scaena video motion-preview --graph <production-graph-ref> --mode full-preview --confirm --budget-ok --quota-ok --json
```

Probe actual video and audio stream duration with `ffprobe`. Trimming a provider clip can leave a longer/shorter audio tail; re-check start, end, silence windows, dialogue/subtitle alignment and final mix duration after every cut. A fixture cut whose duration matches the target is not sufficient when its review is pending, motion clips are placeholders, timeline coverage is incomplete, or production export is blocked.

### 10. Assemble The Episode And Route Refinement

Read [episode-refinement-loop.md](references/episode-refinement-loop.md). Assemble only production-accepted segments:

```bash
scaena video episode-preview --project <project-path> --episode <episode-ref> --segment-asset <asset-1> --segment-duration-ms <ms-1> --output previews/<episode>.mp4 --confirm --json
scaena edit plan --project <project-path> --graph <workflow-graph-ref> --platform douyin --target-duration 75 --json
scaena edit timeline --project <project-path> --plan <edit-plan-ref> --variant fast-hook --json
scaena edit render --project <project-path> --timeline <timeline-ref> --profile preview --output previews/<episode>-cut.mp4 --confirm --json
scaena edit score --project <project-path> --cut <cut-ref> --json
scaena edit select --project <project-path> --cut <cut-ref> --json
```

Score only recommends. Human/owner acceptance still selects the cut and final mix. Classify every defect before repair:

- story, character, dialogue, causality, or hook → Auctra successor screenplay revision;
- storyboard structure/semantics/source mapping → breakdown revise; allowed local fields → typed patch;
- identity/style/wardrobe/location/prop → new DrawSession or derived Eikona candidate, then human select/freeze and preflight;
- shot action/camera/artifact → regenerate only the affected shot;
- dialogue/voice/Foley/music/sync/mix → Sonora/audio successor and independent review;
- pacing/subtitle/transition/mix balance → new Scaena timeline/cut;
- codec/checksum/manifest/package → Scaena delivery repair.

Run at most one bounded owner-specific repair for the same deterministic finding. Preserve original and successor refs. Current `enhance run` v1 is fixture-only; do not claim a real paid enhancement provider without a real command, receipt, and artifact lineage.

### 11. Export Only After Completion Gates

Plan before confirming:

```bash
scaena export package --project <project-path> --profile <profile> --to <output-path> --json
scaena export package --project <project-path> --profile <profile> --to <output-path> --confirm --json
```

Require zero blocking findings, accepted required assets, timeline and audio/subtitle alignment, playable preview, rights, manifest, checksums, and evidence refs. Fail closed when `production_allowed=false` or the command requests repair.

The installed command does not support `--dry-run`. Omitting `--confirm` is the draft plan/preflight form, but `--to` still writes a CLI-managed draft manifest; it is not a zero-write preview. Confirmed export creates a local package; neither action authorizes publish.

### 12. End The Session With Handoff

Do not carry the full conversation into the next stage. Return only the compact receipt plus the exact next command, expected effect, side-effect class, and stop condition. A new session must resume from refs rather than reread the full repository or provider output.

