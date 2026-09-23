# 生产编译器门禁（current）

分镜进入付费媒体生成前，使用 production compiler 投影而非工程日志。

- 目标镜头选择 Seedance 2.5 时，读取 `../scaena-production-operator/references/seedance-2-5-scaena-mapping.md`。方向确认必须包含镜头时长、reference/keyframe 用途、声音策略与 output 目标；但分镜阶段不写 Ark wire hint，也不因官方能力声明跳过后续 Bundle/preflight。

- `scaena storyboard breakdown board <breakdown-ref> --json`：第一屏只看一项决策、cost 摘要与最多 12 项异常。
- `scaena storyboard breakdown readiness <breakdown-ref> --json`：12 轴 readiness；`ready_for_generation` 才是付费生成准入，candidate `generation_ready` 仍只表示结构完整。未 accepted 的 ProductionGraph 永不 `ready_for_generation`。
- `scaena storyboard breakdown exceptions <breakdown-ref> --json`：按优先级排布的阻塞异常与 stale review refs。
- scoped range review：`scaena storyboard breakdown work review --breakdown <ref> --candidate <ref> --decision range_approved|changes_requested --start-segment N --end-segment M --actor user:operator --confirm --json`。range receipt 不等于整集 accept；整集 accept 仍是唯一 ProductionGraph 物化门。
- L3 autopilot：`scaena workflow simulate --automation-level L3_supervised_autopilot` 生成 exact plan digest 投影；付费执行前必须 human approve 同一 digest。
- 主体资产批次与稳定性认证见 `scaena-subject-asset-readiness` skill（`storyboard asset-batch *`、`asset stability *` 命令族）。

缺 audio intent、readiness blocker、cost envelope 未预留或 actor 非 human 时 fail closed；不要绕过这些门禁提交付费生成。
