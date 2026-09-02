# 分镜 review、连续性与决策门禁

只在 candidate 已进入 `review_required`，或准备 revise、patch、accept、reject、export 时读取本参考。

## 决策顺序

固定按以下顺序推进，不跳级：

```text
run
  -> safe summary
  -> direction summary
  -> findings
  -> shots
  -> explicit dialogue/prompt detail only when needed
  -> director + continuity assessment
  -> revise or typed patch when blocked
  -> reload current head / diff
  -> human accept or reject
  -> optional export/handoff
```

每次 successor 都会改变 current candidate 和 breakdown version。任何 decision 前都重新读取 refs/version/digest；不能从聊天记录、旧截图或上一次输出推断 current head。选择读取面时：`--view summary` 看 safe summary，`--view findings` 看逐条 finding，`--view shots` 看镜头表；`--include-dialogue`/`--include-prompt`/`--view prompts` 只在用户显式要求核对时使用。

## Review matrix

至少检查以下维度，并保留 finding code、target refs、结论和下一动作：

| Dimension | Pass 条件 | Block/repair |
| --- | --- | --- |
| source coverage | mapped spans 可回到同一 source ref/version/digest；无未解释缺口 | Agent revise source mapping |
| scene/shot structure | 顺序、身份、时长和一镜一 prompt mapping 完整 | Agent revise；不要 patch structural fields |
| directing | 每镜有叙事功能，景别/角度/运镜/节奏可解释 | 用 `$ai-drama-director` 形成 bounded revision instruction |
| continuity | 人物、服装、道具、空间、时间、动作方向、光线、声音、字幕可从 refs 复核 | 用 `$ai-drama-continuity-supervisor` 形成 finding/repair proposal |
| duration | shot durations 为正，episode 总时长符合当前合同 | typed duration patch 或 Agent revise |
| dialogue/prompt | literal content 只在显式 detail/export 中读取，prompt 与 shot 一一对应 | Agent revise；禁止直接 patch dialogue/prompt body |
| privacy | summary/evidence 只有 refs/digests/counts/findings | 停止并记录 redaction blocker |

`warn` 可以由人决定是否继续；`block`、`unknown`、`stale` 都不能 accept，也不提供 accept 作为 allowed action。

## Revise 与 patch

- Agent revise 会调用 Scaena 进程内 `StoryboardModelRuntime`，必须重新确认模型、cost cap、expected version 和 idempotency key；structure、shot add/remove/reorder、source/dialogue mapping、Prompt mapping、entity/continuity 大改、profile/direction 变更都走 revise。
- Typed patch 是本地 immutable successor，不调用模型；只允许 Skill 主文件列出的九类字段。
- 一个请求中多个 patch field 必须 all-or-nothing。任一 field/path 无效时，不得把剩余字段拆成隐式部分成功。
- 每次 revise/patch 后重新读取 current head 并 diff（`show` + `diff --from-candidate/--to-candidate`），不继续使用旧 head。

## Accept

Accept 前必须先向当前用户呈现完整 direction review：

- story spine（故事脊柱）；
- 逐镜 beat 与 dramatic purpose；
- dialogue spine 与保留情况；
- visual baseline/camera language；
- duration contract 与实际 shot total；
- coverage、blocking/warning findings；
- current candidate ref/version/digest 与 source identity。

同时满足：

1. breakdown state 是 `review_required`；
2. candidate 是 current head；
3. expected breakdown version 精确匹配；
4. candidate digest/source identity 未变化；
5. coverage 和 findings 无 blocker（无 block、无 unknown、无 stale）；
6. actor 是明确的人类身份；
7. 当前用户明确批准 materialization；
8. idempotency key 对应同一 accept intent。

Skill、model、provider 或 runtime 的成功本身不构成 accept 条件；不因 candidate 结构有效而自动 accept 或触发下游生成。Accept 成功回执应包含 acceptance receipt ref 和 ProductionGraph ref。重复同 intent 只接受幂等 replay，不得二次物化。

## Reject

Reject 同样要求 current head、expected version、人类批准和稳定 idempotency key。Reject 不得创建或更新 canonical Scene/Shot；若发现 materializer 被调用，按实现缺陷停止。

## Export 与 downstream 独立 gate

Accept、reject、export 是三个独立 gate，各自需要当前明确批准。Export 可以用于 review candidate 或 accepted candidate，但不改变 acceptance state。确认 format、project-relative output、overwrite 决策和 sensitivity。CSV 单元格必须防公式注入；输出必须带 manifest/checksum，且 evidence 不含对白或 prompt 正文。

Accepted storyboard 到图片/视频/音频生成是更后的 paid production gate：必须再次展示已接受的分镜方向并取得授权；本 Skill 不调用 Eikona 或其他生成 provider，也不因 accept 而自动开始 concept image。

## Typed failure handling

- `EXPECTED_VERSION_MISMATCH` / `CANDIDATE_NOT_HEAD`：重新读取 current head，向用户展示 drift；不自动重试 mutation。
- `BLOCKING_FINDINGS`：展示 finding 摘要和 target refs，选择 revise/patch/reject。
- `IDEMPOTENCY_CONFLICT`：比较 intent；同 intent 修正 payload/key 使用，真新 intent 才由用户批准新 key。
- `OWNER_UNAVAILABLE` / `SOURCE_BODY_UNAVAILABLE`：停止，不降级为 fixture/local fake。
- `COST_CAP_REQUIRED` / `COST_CAP_EXCEEDED`：停止并请求新的明确成本决定。
- `INVALID_PATCH_PATH`：保持 parent digest 不变，改用支持字段或 Agent revise。
- `EXPORT_TARGET_EXISTS` / `EXPORT_PATH_FORBIDDEN`：不覆盖、不换目录逃逸；请求合法路径或明确 overwrite。
- `WAIT_TIMEOUT`：watch 原 ref；ambiguous owner outcome 先 read-only reconcile，不重放 mutation。
