# 抽卡批量合同要点

完整字段见 [C2](https://github.com/yeisme/yeisme-agent-my-skills/blob/main/docs/drama-execution-kernel/contracts/draw-batch.v1.md)。本文只保留执行时的硬约束。

## 现有门禁不得放松

- `scaena asset draw plan` 返回 session ref、cap、wave、dependencies、canonical path policy 与 blocker。
- 目录合同：候选路径只能来自 `scaena asset draw path`；`selected` / `frozen` 指针由 CLI 写，agent 不得自建 `redesign-vN` 之类自由目录。
- `record` 需要 `sha256:<64-hex>` digest，缺失 fail-closed；Eikona run ref + digest 是唯一 lineage，零 provider 调用。
- `select` 需要 `--actor <human>`；`freeze` 需要 `--confirm`；自动冻结在状态机上不可达。
- `frozen` 槽位才是视频生成资产准入的合法上游；`production_admitted` 还需要稳定性矩阵（多场景静帧 + 至少两条抽卡视频）与人工准入。

## 波次规则

| wave | 内容 | 前置 |
| --- | --- | --- |
| 1 | 身份 / 风格锚点 | 无 |
| 2 | 三视图、表情、姿态、发型 / 服装派生 | wave 1 对应 slot 已 `frozen` |
| 3 | recurring location、story-critical prop、wardrobe variant | 主体 / style 已 `frozen` |
| 4+ | shot-specific derived candidate | `--requires` 中所有上游 refs 已 `frozen` |

单 slot 同一时刻只允许一个 active session；并发开启 fail-closed 并指向现有 session。`exhausted` 分支必须修订 brief 后 replan。

## 批次调度

- 先读取已有清单及未完成状态；启动本批时取得一次完整平台库存与项目模板快照，沿用已定风格 / 模型，不为每个 slot 重选模板。
- 已有合格冻结计划原样使用；不创建项目专用执行器。
- 已审来源自动校验通过即消费；未审来源列 `sourceExceptions`，不自动派发重新抽取 / 复核。
- 一批提交后统一回查；已完成生成交回实际稳定 id，再由设计职责冻结绑定。
- 缺证据、身份冲突、失败或 UNKNOWN 只阻断相关节点及其下游；无关合格项继续。
- 进程中断且子状态缺失时只能核对，不自动重发；一个节点每轮最多调用一次。

## 进度报告口径

分别报告「新生成 / 旧图复用 / 已绑定 / 在途 / 失败 / 待决 / 缺图」。源码复核数量、文件数量、壳数量不是出图进度；不得用未测并发估计承诺耗时。

## 快覆盖前置

- 来源必须是已验证完成的独立衍生生成阶段；
- 所选 `imageId` 同时存在于生成结果与当前完整主体详情，状态为完成；
- 当前母图仍等于生成请求冻结的母图；
- 衍生 ID、别名、集数与原请求完全一致；
- 用户授权原文完整保存；
- 任一漂移整批停止，不留下可执行输出。
