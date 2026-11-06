# identity_equal 判定门与失败修复

## 判定字段集

直接复用 `scaena-production-operator/references/workflow.md:140`：

> Before owner execution require all of the following to match: project, ProductionGraph ref/version, shot ref, frozen intent ref/digest, frozen spec ref/digest, validated bundle ref/digest, capability ref/digest/maturity, task policy, duration/ratio/output/audio policy, exact subject/style/reference versions and ordinals, and a non-empty idempotency key.

替换任务额外固定：

| 类别 | 字段 |
| --- | --- |
| 声音身份 | `speaker`、`character subject`、`voice timbre`、`original audio source` |
| 正文语义 | `dialogue text`、`mention`、`prompt text` |
| 生成配置 | `model`、`channel`、`duration`、`ratio`、`reference roles/ordinals/counts` |
| 来源证明 | 旧媒体 / 新媒体 / 原始音源三份实际字节 `sha256` |

只要声音身份、正文语义或生成配置任一变化 → `equal: false`，退回完整创作链。三份 provenance 只证明技术同源关系，**不决定说话人、音色或对白**。

## 绑定任务顺序

1. 冻结 `old_ref` / `new_ref` / `provenance_sha256[3]` / `field_plan` / `audio_plan` / `claim_key` / `recovery_ref`。
2. 证明 `identity_equal`（逐字段，不靠文件名或 hash 相同推断）。
3. 执行固定替换：`eikona assets stage` → `eikona assets handoff --agent` → `eikona replace ... --yes --json`。
4. 权威回读：衍生 ID / 别名 / 集数不变、`imageId` 等于选定候选、母图不变、`replacement_status: applied`、`binding_digest` 一致。
5. 回读一致后才刷新技术证据；技术证据明确记录「未执行新的语义复核」。
6. `UNKNOWN` → 停止，用原 `recovery_ref` 只读恢复，不重投。

## 失败视频受控修复

进入条件（全部满足）：

- 返回 ID 全部为终态 `FAILED`；
- 用 `reconcile` 实时回读，原 ID 当前仍全部 `FAILED`；
- 原模型 / 渠道 / 分辨率 / 比例 / 正文 / 素材 / 音频 / 时长 / 数量 / 策略字段逐项全等；
- 用户原样重提授权原文完整保留（不删引号、不忽略尾文）。

执行：

- `scaena workflow repair plan --run <run-ref> --json` 生成候选，跳过成功 / 处理中 / 未知；
- `scaena workflow repair run --repair <repair-ref> --json` 单次受控调用；
- `claim_key = (project, episode, shot, 原失败 videoId)` 作为共享登记，换 run-dir / state 不能变成另一次派发；
- 只有「已预留、尚未领取」且原进程已退出、无 state / result 时，才允许 `--continue-not-sent` 语义续行；
- 已受理或结果未知停止，不新增无证据自动解锁；
- 新请求自身失败时，以其**新返回的失败 ID** 建立下一轮证据，保留此前全部记录。

禁止：成功 / 活动 / 未知目标进入自动失败队列；混合成功与失败候选的部分重投；把失败退出码本身当失败证据；借重提授权换模型、改正文、改时长。

## 影响面预览

替换前用 `scaena production graph describe <graph-ref> --json` 列出受影响的 shot / package / release plan，作为 `bound_ref` 必填字段。这一步只查询，不改 ProductionGraph。

## 回滚语义

`eikona rollback <replacement_id> --json`：

- 校验当前文件 hash，不覆盖后续用户编辑；
- 恢复项目文件并更新 replacement record；
- **不产生** `REVIEWED` / `PRODUCTION_ADMITTED` / `EXPORT_READY`；
- `eikona.asset_handoff.v2` 的 `permission` 仍为 `handoff_candidate`，`feedback_status` / `replacement_status` 独立记录。

## 验收口径

- 非 `FAILED` 或配置漂移 → 拒绝重提；
- 并发两个入口对同一 `claim_key` 最多一个进入提交；
- `equal: false` → 新 `idempotency_key` + 新授权；
- 回滚后不出现 `production_ready`；
- 不删除历史候选 / digest，不覆盖后续用户编辑。
