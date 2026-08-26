# 分镜 review、连续性与决策门禁

只在 candidate 已进入 `review_required`，或准备 revise、patch、accept、reject、export 时读取本参考。

## 决策顺序

```text
run
  -> safe summary
  -> explicit candidate detail when needed
  -> director review
  -> continuity review
  -> revise or typed patch when blocked
  -> reload current head
  -> human accept or reject
  -> optional export/handoff
```

每次 successor 都会改变 current candidate 和 breakdown version。任何 decision 前都重新读取 refs/version/digest；不能从聊天记录、旧截图或上一次输出推断 current head。

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

`warn` 可以由人决定是否继续；`block`、`unknown`、`stale` 都不能 accept。

## Revise 与 patch

- Agent revise 会调用 Dramaturge，必须重新确认模型、cost cap、expected version 和 idempotency key。
- Typed patch 是本地 immutable successor，不调用 owner；只允许 Skill 主文件列出的九类字段。
- 一个请求中多个 patch field 必须 all-or-nothing。任一 field/path 无效时，不得把剩余字段拆成隐式部分成功。

## Accept

Accept 前同时满足：

1. breakdown state 是 `review_required`；
2. candidate 是 current head；
3. expected breakdown version 精确匹配；
4. candidate digest/source identity 未变化；
5. coverage 和 findings 无 blocker；
6. actor 是明确的人类身份；
7. 当前用户明确批准 materialization；
8. idempotency key 对应同一 accept intent。

Accept 成功回执应包含 acceptance receipt ref 和 ProductionGraph ref。重复同 intent 只接受幂等 replay，不得二次物化。

## Reject

Reject 同样要求 current head、expected version、人类批准和稳定 idempotency key。Reject 不得创建或更新 canonical Scene/Shot；若发现 materializer 被调用，按实现缺陷停止。

## Export

Export 可以用于 review candidate 或 accepted candidate，但不改变 acceptance state。确认 format、project-relative output、overwrite 决策和 sensitivity。CSV 单元格必须防公式注入；输出必须带 manifest/checksum，且 evidence 不含对白或 prompt 正文。

## Typed failure handling

- `EXPECTED_VERSION_MISMATCH` / `CANDIDATE_NOT_HEAD`：重新读取 current head，向用户展示 drift；不自动重试 mutation。
- `BLOCKING_FINDINGS`：展示 finding 摘要和 target refs，选择 revise/patch/reject。
- `IDEMPOTENCY_CONFLICT`：比较 intent；同 intent 修正 payload/key 使用，真新 intent 才由用户批准新 key。
- `OWNER_UNAVAILABLE` / `SOURCE_BODY_UNAVAILABLE`：停止，不降级为 fixture/local fake。
- `COST_CAP_REQUIRED` / `COST_CAP_EXCEEDED`：停止并请求新的明确成本决定。
- `INVALID_PATCH_PATH`：保持 parent digest 不变，改用支持字段或 Agent revise。
- `EXPORT_TARGET_EXISTS` / `EXPORT_PATH_FORBIDDEN`：不覆盖、不换目录逃逸；请求合法路径或明确 overwrite。
