# 像素锁定转绘生产经验

该参考用于“原场景完全保留、只替换审核角色区域”的真人视频转绘。Scaena 是生产状态 owner，Eikona 是角色视觉 run/artifact owner；技能只路由 refs、门禁与下一动作。

## 已验证的最小链路

```text
真实 MP4 显式登记进 Scaena CAS
  -> 2–5 秒 ShotChunkMap
  -> Eikona 角色 candidate run
  -> typed handoff / stage / apply
  -> Scaena SubjectVersion 人工冻结
  -> CharacterMaskTrack 生成与人工审核
  -> immutable TransferEpisodeManifest
  -> zero-call admission 与成本确认
  -> 一次 provider task
  -> 源帧底图上的像素锁定合成
  -> 蒙版外逐帧差异必须为零
```

## 可复用的实测结论

- 用 2–5 秒 sentinel shot 验证主体、动作、构图和结束状态，再决定是否扩大批次。
- Eikona 生成成功只产生 `candidate_only` artifact，不等于 Scaena 已冻结 SubjectVersion。
- 蒙版漏检必须通过带固定模型摘要和 `supersedes_mask_track_ref` 的派生轨迹修复；不得覆盖旧轨迹或伪装为通过。
- 修复后应比较逐帧摘要和蒙版外 decoded pixel diff，证明未授权区域没有变化。
- 角色版本未冻结、蒙版未人工接受、成本未确认时，provider call count 必须保持为零。

## 容易误判的信号

| 信号 | 正确含义 | 禁止推导 |
| --- | --- | --- |
| Eikona run `succeeded` | provider artifact 已写入 Eikona evidence | Scaena subject 已冻结 |
| `assets apply` 成功 | 候选文件已落入项目路径 | 候选已被生产接受 |
| 蒙版生成覆盖 120 帧 | 媒体规格和轨迹存在 | 人体边界完整且可合成 |
| local animatic 可播放 | 构图/时间轴候选可审阅 | Seedance 角色转绘已完成 |
| dry-run/preflight 成功 | owner call 前合同可用 | 允许付费提交 |
| provider task 成功 | 生成候选可导入 | 蒙版外像素自动保持不变 |

## 必须 fail closed 的不足

1. Eikona model ref 必须规范化为 `openai/gpt-image-2.5-sunburst`；双 provider 前缀或空 original ref 不能进入 Scaena handoff。
2. Scaena 必须有公开的 subject freeze、mask accept/reject 和 derived correction 操作；缺少命令时返回 capability blocker，不手写 SQLite/JSON。
3. 蒙版修复必须引用 base track、correction model/digest、提示摘要、输出 digest 和 supersedes ref。
4. 首镜头 manifest 必须固定 source/chunk/subject/style/mask/model/channel/attempt budget；任何引用漂移后重新 admission，不能自动使用“最新”。
5. 超时只查询原 provider task；同一 idempotency identity 不得重复 POST。
6. 只有确定性合成器和 decoded pixel diff 能证明“蒙版外零变化”；提示词不能证明。

## 操作检查

先用真实命令查看当前能力：

```bash
scaena video transfer --help
scaena video transfer mask-track --help
scaena video transfer manifest create --help
export SCAENA_PROJECT=/path/to/scaena-project
scaena asset verify --project "$SCAENA_PROJECT" --json
eikona inspect <run-id> --brief --agent
```

Eikona 候选进入项目必须经过 typed handoff：

```bash
eikona assets handoff img_02ad1bd225be --agent
eikona assets stage img_02ad1bd225be --to outputs/characters/korea-v3/candidates/yoon-ha-eun.png --agent
eikona assets apply img_02ad1bd225be --project current --to outputs/characters/korea-v3/candidates/yoon-ha-eun.png --yes --agent
```

若 `scaena video transfer manifest create` 返回 `SUBJECT_VERSION_NOT_FROZEN`，保持 provider call count 为零，并回到 Scaena subject readiness；不要把 Eikona handle 或普通 asset ref 直接填成 frozen character version。
