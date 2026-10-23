## Seedance 提示词与请求调试

使用 Seedance 2.5 前先读取
`../scaena-production-operator/references/seedance-2-5-scaena-mapping.md`。先离线列出已适配模型与本机凭据，再由当前安装版本确认
task mode、reference role/count、ratio/duration lock、resolution/output/audio 与 maturity：

```bash
scaena video model list --json
scaena video auth list --json
scaena video model describe --model doubao-seedance-2-5-260628 --json
```

`video model list` 证明本地 descriptor 已注册，不证明凭据、配额或 production_ready。若安装版本还有 `scaena video provider list`，用它看 Provider 聚合；没有则不要发明该命令。

官方文档列出的 50 引用、纯音频、多语言原生音频、1080p、MOV、edit/extend/frames
可以进入合同和离线 fixture 计划，但本地 descriptor 未投影或没有真实 canary/review 时
只能返回 `capability_missing`/`needs_contract`/`production_ready=false`。Ark 的
`omni_reference_task_type` 由 adapter 从 provider-neutral task policy 推导；不要把它写进
prompt、bundle 或 handoff。

### 文件优先与时间戳分段

长提示词必须优先保存为项目内的普通 Markdown/text 文件，再通过现有 `--prompt-file` 入口加载。目录按 Eikona 的 owner/asset-type/collection 语义组织：

```text
prompts/scaena/video-transfer/<episode>-<shot-or-chunk>/prompts/01-<direction>.md
```

一个文件只对应一个 shot/chunk，或一个已经明确审核通过的 merged chunk。文件只放会发送给 Seedance 的自然语言；model、task、URL、credential、审批状态、训练授权和 source absolute range 不得写进 prompt body。

当片段包含多个动作阶段时，必须把时间戳直接写成独立块，方便人看：

```text
00:00:00.000 --> 00:00:01.600
女主快速接近教室门，保留原片机位、背景、构图和匆忙步频。

---

00:00:01.600 --> 00:00:03.200
女主握住教室门把手并向下压，动作连续，门和道具位置不变。

---

00:00:03.200 --> 00:00:04.800
女主推开教室门进入，保留快迟到的节奏和原片结束构图。
```

时间必须是当前 provider clip 的相对时间：首段从零开始，按顺序无 gap/overlap，末段等于 clip duration。源视频绝对时间由 shot/chunk binding 保存。详细规则读取 [references/prompt-corpus-and-timeline.md](references/prompt-corpus-and-timeline.md)。

以下是当前已验证的 legacy Tokenspace Seedance 2.0 转绘提交命令，不是 Seedance 2.5
Ark 的请求模板：

```bash
export SCAENA_PROJECT=/path/to/scaena-project
scaena video generate \
  --project "$SCAENA_PROJECT" \
  --model doubao-seedance-2-0-260128 \
  --bundle <bundle-ref> \
  --media-profile <storage-profile> \
  --prompt-file prompts/scaena/video-transfer/E001-001/prompts/01-source-locked.md \
  --draw 1 \
  --candidate-only \
  --json
```

提交后必须用 `video task prompt --verify-prompt-file` 校验 hash。Prompt corpus 当前只完成设计：正文可保存在用户项目文件中，但训练晋级必须等待 Scaena corpus CLI 落地，并满足人工 accepted、rights allowed、`training_use=allowed` 和清洗无 blocker。不得因为 provider task 成功就声称可训练。

当用户问“最终提示词是什么”“最终 prompt 有没有被改”“到底上传了哪些图”“为什么多出一个角色”时，不能只复述一句自然语言，也不能输出 raw provider payload。先用紧凑的 prompt provenance 查询；只有问题涉及媒体绑定或参数时才升级到完整请求结构：

```bash
scaena video task prompt \
  --project "$SCAENA_PROJECT" \
  --model doubao-seedance-2-0-260128 \
  --task <task-id> \
  --agent
```

`--agent` 只给 task、prompt revision、capture status、source、digest prefix、字节数、delivery、transform 和本地文件校验，避免浪费上下文；它不重复展开安全 `data`。如需核对操作者手上的文件，追加 `--verify-prompt-file prompts/scaena/video-transfer/E001-001/prompts/01-source-locked.md`，只返回 `matched|mismatched|unavailable|not_requested`，绝不回显正文或路径。需要 media ordering、asset refs 或 body 参数时，再运行：

```bash
scaena video task debug \
  --project "$SCAENA_PROJECT" \
  --model doubao-seedance-2-0-260128 \
  --task <task-id> \
  --json
```

1. **来源**：`prompt.source`、digest、byte_count。若是 `prompt_file`，正文由操作者在自己的文件中查看；Scaena 不回显或持久化正文。默认交互只报告 digest prefix；只有显式 `--json` 才包含完整安全摘要。
2. **Scaena 变换**：Tokenspace mixed-reference 路径是 `delivery=verbatim`、`scaena_transform=identity`。这表示 CLI 文本原样装入 `ModelGenerateInput.Prompt`，没有隐式人物、镜头或风格附加词。
3. **wire content 顺序**：固定 `text → reference_video → reference_image...`。内部 `character_identity` 仅在 adapter 边界映射成 wire `reference_image`；`content[]` 的 asset refs 是判断错误角色是否被上传的唯一证据。
4. **安全参数**：model、duration、ratio、resolution、audio、API surface 和 filing 是否存在。正文、签名 URL、object key、credential、raw body 均不可输出。
5. **结果边界**：正确 prompt / binding 只证明输入契约；Seedance 是采样模型，不能证明手部、门把手、人物数量或帧级连续性。只有审核 mask 加源帧 pixel-lock composite 的蒙版外差分为零，才能证明原场景/物品/字幕保留。

Seedance 2.5 的请求排查按 task policy、media ordinal/count、ratio/duration lock、
output/audio policy 和 maturity 顺序进行。若当前 `video task prompt/debug` 尚未为 Ark
发布同等账本投影，返回 capability gap；不要拿 Tokenspace 的固定 wire 顺序或 filing
字段推断 Ark body。

对于快照上线前的任务，明确报告 `capture_status=not_captured`，只用冻结 bundle 和确定性 adapter 规则说明已知 media order；不得臆造历史 prompt 或参数。完整方法见 [references/seedance-request-debug.md](references/seedance-request-debug.md)。

