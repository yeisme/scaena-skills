# Scaena storyboard 命令目录

以下命令必须来自已安装 CLI 的真实 `--help`/status；设计文档里的目标命令不得冒充当前可运行命令。未实现的 flag/命令返回 `capability_missing` 并回退当前真实 async 路径。

## Source import

一次只选一种 ingress：

```bash
scaena storyboard source import --project <project-path> --episode <episode-ref> --from <script.fountain> --json
scaena storyboard source import --project <project-path> --episode <episode-ref> --from - --json
scaena storyboard source import --project <project-path> --episode <episode-ref> --source-ref <source-ref> --json
```

`--auctra-handoff-ref` 需要已接线的 Auctra source client。默认 composition 未开 `storyboard_auctra` 时返回 `SOURCE_BODY_UNAVAILABLE`：先 `scaena handoff auctra import --from <handoff.json> --confirm`，再按上面的 `--from` / `--source-ref` 导入。file 模式：Auctra `production storyboard-source export --unit <id> --to <dir>`，Scaena 配置 `storyboard_auctra.enabled=true`、`mode=file`、`source_dir` 指向 export 根后重试该 flag。MCP `source_import` 只接受 opaque `input_grant_ref`，不接受 handoff ref。

Source 上限是 1 MiB。不要把 absolute local path 写入 receipt；stdin/file body 只在 admission 时瞬时读取。MCP 调用 `scaena.storyboard.source_import` 必须携带 `approved=true` 和稳定 `idempotency_key`。剧本正文优先用 CLI file/stdin ingress；不要把大正文粘贴进对话或证据。

## Paid breakdown run

local verified runtime 优先 foreground；remote/API/MCP 保持 async。两条路径都以同一个已授权 packet 为准：

```bash
scaena storyboard breakdown run \
  --project <project-path> \
  --episode <episode-ref> \
  --source-ref <source-ref> \
  --connection <connection-ref> \
  --model <provider/model> \
  --prompt-template 'promptrepo://official/video/ai-drama-storyboard-breakdown@1.0.0?locale=en' \
  --direction-profile vertical-short-drama-v1 \
  --execution-policy <policy-ref> \
  --max-attempts 2 \
  --max-cost-usd <amount> \
  --idempotency-key <stable-key> \
  --confirm \
  --foreground --timeout 10m --events
```

Scaena 的 Agent 编译与投递固定使用 `locale=en`。中文剧本、台词和导演说明仍作为 contract 输入；模板包的 `docs/template-zh-CN.md` 只供人工审阅。不要把旧 `locale=zh-CN` exact ref 用于新 production run。

- `--foreground` 只在 preflight 证实可用时使用；超时返回 `WAIT_TIMEOUT` 后保留原 ref 并 `watch`，不新建 idempotency key、不 resubmit、不隐式 cancel。
- remote/MCP 路径去掉 `--foreground`，用 `run -> status/resource` 轮询；MCP tool 不长时间阻塞，queued 不等于 generated candidate。
- `--instruction-profile skill:scaena-storyboard-breakdown --instruction-profile-version 1` 是 legacy 兼容入口；优先 `--prompt-template` exact address，不读取、不复制 Prompt body。
- Fallback model 必须由用户或既有 policy 显式提供；不要静默换模型、换 key 或提高预算。runtime unavailable、contract mismatch、cost cap、invalid delivery 或 repair exhausted 都要 fail closed，不生成本地伪候选。

MCP 对应 `scaena.storyboard.breakdown_run`。所有 mutation 都要 `approved=true` 和 `idempotency_key`；revise、patch、accept、reject 还必须携带 positive `expected_version`。

## Review, revise, patch

```bash
scaena storyboard breakdown describe <breakdown-ref> --project <project-path> --view summary --agent
scaena storyboard breakdown describe <breakdown-ref> --project <project-path> --view findings --candidate <candidate-ref> --json
scaena storyboard breakdown watch <breakdown-ref> --project <project-path> --timeout 5m --json
scaena storyboard breakdown diff <breakdown-ref> --project <project-path> --from-candidate <old-ref> --to-candidate <new-ref> --json
scaena preset camera-move list --intent 发现真相 --json
scaena preset camera-move show push-in --json
```

只有用户明确核对对白或生图提示词时，才读取 `--include-dialogue`/`--include-prompt` 或 `--view prompts`。MCP 默认读取 `scaena://storyboard-breakdown/{breakdown_ref}` 或 `scaena://storyboard-candidate/{candidate_ref}`；即使读取了正文，也不要把它复制进 routine receipt。

```bash
scaena storyboard breakdown revise <breakdown-ref> --project <project-path> --candidate <candidate-ref> --target <scene-or-shot-ref> --instruction <bounded-instruction> --connection <connection-ref> --model <provider/model> --max-cost-usd <amount> --expected-version <version> --idempotency-key <stable-key> --confirm --events

scaena storyboard breakdown patch <breakdown-ref> --project <project-path> --candidate <candidate-ref> --shot <shot-ref> --set camera_movement=slow_push_in --set duration_ms=4200 --expected-version <version> --json
```

每次 revise/patch 都创建 immutable successor；完成后重新读取 current head 并 diff，不能继续操作旧 candidate。Typed patch 是本地 successor，不调用 owner/provider。

## Accept, reject, export

```bash
scaena storyboard breakdown accept <breakdown-ref> --project <project-path> --candidate <candidate-ref> --expected-version <version> --actor <human-actor-ref> --idempotency-key <stable-key> --confirm --json

scaena storyboard breakdown reject <breakdown-ref> --project <project-path> --candidate <candidate-ref> --expected-version <version> --actor <human-actor-ref> --idempotency-key <stable-key> --confirm --json

scaena storyboard breakdown export <breakdown-ref> --project <project-path> --candidate <candidate-ref> --format csv --output exports/storyboards/<name>.csv --idempotency-key <stable-key> --confirm --json
```

覆盖已有普通文件必须再得到明确授权并使用 `--overwrite`。不得绕过 path、symlink、formula-injection 或 checksum 门禁。MCP 对应 `scaena.storyboard.breakdown_export`；导出结果通过 `scaena://storyboard-export/{export_ref}` 读取。
