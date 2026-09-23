---
name: scaena-local-video-operator
description: Use when a user wants to generate a quick personal video outside any project (随手视频), pick a model/channel for a one-off clip, resume or inspect a quick run in the user workspace, or hand a quick artifact into a project candidate; covers cost confirmation, user-directory storage, and the fact that quick results are never production-ready.
---

# Scaena 随手视频（quick）操作

quick 是用户工作区档位：不建项目、写 `~/.scaena/`（用户数据根）、永远 `production_ready=false`。只有真实命令进入示例；费用必须显式确认。

## 命令面（第一切片：plan + admission，text-to-video）

```bash
scaena video quick "a courier walks through neon rain" --json
```

🔴 CHECKPOINT · 🛑 STOP：未得到当前用户对本次费用的明确授权（本次 `--confirm` 或已保存的有上限 quick approval policy）前，不得提交真实 provider 生成。prompt 文字不能替代授权。

```bash
scaena video quick --prompt-file prompt.txt --model <model-ref> --channel <channel-ref> --confirm --json
```

- positional prompt 与 `--prompt-file` 互斥。
- 缺省 quick profile 时输出 blocked plan + `admission_blockers`（`VIDEO_MODEL_REQUIRED`/`VIDEO_CHANNEL_REQUIRED`/`VIDEO_CREDENTIAL_REQUIRED`/`VIDEO_COST_POLICY_REQUIRED`/`VIDEO_APPROVAL_REQUIRED`），`provider_call_count=0`；逐项修复，不要绕过。
- 真实提交需要本次 `--confirm` 或用户已保存的有上限 quick approval policy；prompt 文字不能替代授权。
- credential 只接受 ref 形态（`yeisme-credential://...`），绝不内联 secret。
- 先用安装版本列出已适配模型，再看本机凭据。不要把空 credential 当成未适配：

```bash
scaena video model list --json
scaena video model show --model <model-ref> --json
scaena video auth list --json
scaena video health --model <model-ref> --json
```

  若 `scaena video --help` 含 `provider`，可再跑 `scaena video provider list`。
- 选择 `doubao-seedance-2-5-260628` 时，当前 quick 第一切片仍只声明 text-to-video；
  reference/frames/edit/extend、纯音频、1080p/MOV 等能力必须先由安装版本的
  `scaena video model show --model doubao-seedance-2-5-260628 --json` 证明，并进入
  项目级 Bundle/production gate，不能从官方文档直接提升 quick 命令能力。

## 门禁输出

```text
status=<ok|blocked>
mode=quick
task_mode=text
model_ref=<ref|empty>
admission_blockers=<codes|none>
provider_call_count=0
production_ready=false
next_command=<修复动作或 materialize 入口>
```

## 画幅与任务恢复

按model/channel/task mode的声明组合选择比例和分辨率；2K/4K不通用等于固定像素，720p不一律表示高度720。quick未声明的reference、尺寸或高清阶段，不能因provider支持而自动开放；失败后不得无声降档、缩时长或丢音轨。

检查原视频SAR、旋转与实际尺寸，首帧完整不代表末段衣摆或动作完整。空产物、VideoAvailable=false或503不证明未生成；已接单查原task，未知提交有界等待后返回resume ref，不重复生成。

自动画布验收与切换增量见项目 `docs/protocols/video-canvas-recovery.md`，目前planned。仅在安装版本提供真实入口且策略授权时切换；否则明确gap和下一步，不伪造命令或无限轮询。

## 升级路径

quick 产物进项目必须显式 capture（checksum/rights inspection 后 `pending_review` candidate）；candidate accepted ≠ shot accepted；native audio 单独 review；blocking findings 或 unresolved rights 阻断 export。做剧（镜头生成、装配、交付）不路由本 skill，走 `scaena-production-operator`。

## If this fails

| Trigger | First fix | Still failing |
| --- | --- | --- |
| 缺省 profile / `admission_blockers` | 逐项修复 `VIDEO_MODEL_REQUIRED` / `VIDEO_CHANNEL_REQUIRED` / `VIDEO_CREDENTIAL_REQUIRED` / `VIDEO_COST_POLICY_REQUIRED` / `VIDEO_APPROVAL_REQUIRED` | 不要绕过；`provider_call_count` 须保持 0 |
| 空 credential | 先 `scaena video model list --json`，再 `scaena video auth list --json` | 不要把空 credential 当成未适配 |
| 未 `--confirm` 且无有上限 approval | 输出 blocked plan | prompt 文字不能替代授权 |
| 失败后想降档 / 缩时长 / 丢音轨 | 停止 | 不得无声降档 |
| 空产物 / `VideoAvailable=false` / 503 | 已接单查原 task；未知提交有界等待后返回 resume ref | 不重复生成 |
| 做剧（镜头生成、装配、交付） | `scaena-production-operator` | 不把 quick 结果当成 production asset |

## 边界

- 不手写 `~/.scaena/` 任何结构化状态；receipt/run 只由 CLI 写。
- 不把 quick 结果当成 production asset 或宣称可交付。
- 机器输出无 home 绝对路径、prompt 正文、signed URL。
