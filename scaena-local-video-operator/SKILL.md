---
name: scaena-local-video-operator
description: Use when a user wants to generate a quick personal video outside any project (随手视频), pick a model/channel for a one-off clip, resume or inspect a quick run in the user workspace, or hand a quick artifact into a project candidate; covers cost confirmation, user-directory storage, and the fact that quick results are never production-ready.
---

# Scaena 随手视频（quick）操作

quick 是用户工作区档位：不建项目、写 `~/.scaena/`（用户数据根）、永远 `production_ready=false`。只有真实命令进入示例；费用必须显式确认。

## 命令面（第一切片：plan + admission，text-to-video）

```bash
scaena video quick "a courier walks through neon rain" --json
scaena video quick --prompt-file prompt.txt --model <model-ref> --channel <channel-ref> --confirm --json
```

- positional prompt 与 `--prompt-file` 互斥。
- 缺省 quick profile 时输出 blocked plan + `admission_blockers`（`VIDEO_MODEL_REQUIRED`/`VIDEO_CHANNEL_REQUIRED`/`VIDEO_CREDENTIAL_REQUIRED`/`VIDEO_COST_POLICY_REQUIRED`/`VIDEO_APPROVAL_REQUIRED`），`provider_call_count=0`；逐项修复，不要绕过。
- 真实提交需要本次 `--confirm` 或用户已保存的有上限 quick approval policy；prompt 文字不能替代授权。
- credential 只接受 ref 形态（`yeisme-credential://...`），绝不内联 secret。
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

## 升级路径

quick 产物进项目必须显式 capture（checksum/rights inspection 后 `pending_review` candidate）；candidate accepted ≠ shot accepted；native audio 单独 review；blocking findings 或 unresolved rights 阻断 export。做剧（镜头生成、装配、交付）不路由本 skill，走 `scaena-production-operator`。

## 边界

- 不手写 `~/.scaena/` 任何结构化状态；receipt/run 只由 CLI 写。
- 不把 quick 结果当成 production asset 或宣称可交付。
- 机器输出无 home 绝对路径、prompt 正文、signed URL。
