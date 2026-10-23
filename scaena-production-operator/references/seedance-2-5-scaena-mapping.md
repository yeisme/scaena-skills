# Seedance 2.5 → Scaena 合同映射

本页只维护 Scaena 字段与门禁映射。官方能力事实由 AI drama 的
`ai-drama-router/references/seedance-2-5-capability-profile.md` 统一维护；如果该
参考包在当前宿主不可用，以 Scaena 当前 `model show` 投影为实现真源，并返回
`needs_contract`，不要复制或猜测 provider 手册。

## 输入映射

| 做剧事实 | Scaena 合同 |
| --- | --- |
| 模式 | `ShotGenerationSpec` / Bundle 的 provider-neutral `task_policy` |
| 引用用途与顺序 | Visual/Video reference bindings 的 role、ordinal、ref/digest |
| 时长与画幅锁定 | capability snapshot 的 duration/ratio policy |
| 分辨率与容器 | capability/output policy；1080p/MOV 要有当前实现与成本 evidence |
| 原生/参考音频 | `ShotAudioIntent` + `AudioInputBinding`；默认 `replace_after_generation` |
| 能力证据 | capability ref/digest + maturity：contract/fixture/canary/production |

Ark 的 `omni_reference_task_type` 不进入 `ShotIntent`、`ShotAudioIntent` 或
`VideoInputBundle` 的 provider-neutral canonical 字段。官方 Ark adapter 只能从已
验证的 task policy 推导 wire hint；不匹配在 credential lookup 前 zero-call 阻断。

## 模式门禁

- `text`：bundle 不含媒体。
- `reference`：至少一个非 first/last 引用；引用总数/分项上限来自 capability snapshot。
- `frames`：只允许 first/last frame，ratio 为 `adaptive`。
- `edit`：必须有 reference video，ratio 为 `adaptive`，duration 为 `-1`。
- `extend`：必须有 reference video，ratio 为 `adaptive`。

## Readiness

```text
contract_declared
local_fixture_verified
provider_canary_verified
production_ready
```

`model show`、offline fixture 或 provider-smoke 只能证明其对应层。只有已验证
Bundle、CAS/rights、主体/连续性、独立音频 review、人工选择和 production
acceptance 全部 current，才可投影 `production_ready`。

## 当前能力检查

```bash
scaena video model describe --model doubao-seedance-2-5-260628 --json
scaena video health --model doubao-seedance-2-5-260628 --json
```

未投影 reference_audio、1080p、MOV、task lock 或 maturity 的安装版本，只能返回
`capability_missing`/`needs_contract`。Skill 不得因此手写 Bundle、私塞 provider hint
或把官方文档当作本地实现证据。

