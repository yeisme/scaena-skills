# Scaena Skills

Scaena 分镜拆解、主体抽卡、逐镜生产、整集拼接、精修、交付和视频转绘流程的开源 Skills 集合。

## Skills

- `scaena-production-operator`：从 accepted screenplay 到 storyboard、subject draw、produce、review、assemble、refine、delivery 和 export 的可恢复生产阶段。
- `scaena-storyboard-breakdown`：Auctra 剧本 handoff 的 source import、分镜拆解、revise/patch、方向确认和 accepted breakdown。
- `scaena-subject-asset-readiness`：角色、场景、道具、服装、风格的 DrawSession 抽卡、human-only 选卡/冻结和镜头绑定/preflight 门禁。
- `scaena-video-transfer-orchestrator`：已有拆解视频的市场适配、参考资产、prompt provenance、canary 和生成交接。
- `scaena-local-video-operator`：无项目个人 quick 视频；进入项目必须显式 capture 到 pending review。选模型先跑 `scaena video model list`，再 `video auth list` / `video health`；缺凭据不等于未适配。
- `scaena-production-decision-handoff`：消费已确认的漫剧 DecisionBrief，读取 storyboard/readiness/session，并只生成零调用 simulation 或显式 skill-plan handoff。

## 原创漫剧成片链路

```text
Auctra accepted screenplay handoff
→ storyboard breakdown + current-user direction confirmation
→ asset dependency waves
→ Eikona candidates
→ Scaena draw record / human select / freeze
→ exact shot generation lineage
→ visual + audio + continuity + production acceptance
→ episode preview + edit timeline variants + cut selection
→ owner-routed bounded refinement
→ delivery review + checksummed export package
```

抽卡合同见 `scaena-subject-asset-readiness/references/candidate-draw-workflow.md`；拼接与精修合同见 `scaena-production-operator/references/episode-refinement-loop.md`。当前 `enhance run` v1 是 fixture-only；未注册的整集 workflow goal 和真实付费 enhancement 不得描述为已实现。

Seedance 2.5 的 Scaena 字段/门禁映射见
`scaena-production-operator/references/seedance-2-5-scaena-mapping.md`。官方事实仍由
AI drama 的 `ai-drama-router/references/seedance-2-5-capability-profile.md` 单一维护；
Scaena Skills 只根据当前 model descriptor、capability snapshot、Bundle 和 evidence
判断 `contract_declared | local_fixture_verified | provider_canary_verified |
production_ready`，不把 1080p/MOV、50 引用或原生音频的文档声明当作本地已实现。

## 验证

```bash
git clone https://github.com/yeisme/scaena-skills.git
cd scaena-skills
python3 scripts/validate_skills.py
```

示例命令使用 `$SCAENA_PROJECT`、`$SCAENA_REPO` 等显式占位变量，不绑定维护者机器路径。生产状态、资产 bytes、provider 凭据和 acceptance 仍由 Scaena 产品拥有。

## License

[MIT](LICENSE)
