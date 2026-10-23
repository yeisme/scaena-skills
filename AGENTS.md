# Scaena Skills 工作区说明

## Race 检测执行限制

Agent 在任何阶段都不得主动运行 race 检测，也不得通过子 Agent、Skill、CI、验收、发布、聚合任务或脚本间接触发。只有当前人类用户明确、强烈要求执行 race 时，才允许在指定范围内运行一次；失败、超时、中断均不得自动重试，后续运行必须取得新的同等明确要求。一般的“测试、验收、修复、发布、跑全部检查”不构成授权。

Race 不属于默认验收或完成门禁；未运行不得阻塞交付，也不得声称已经通过。执行聚合命令前检查其依赖，移除或跳过 race 阶段，继续普通测试、静态检查和构建。本规则取代本文件及 Skills、OpenSpec、历史计划、文档中的自动或强制 race 要求；它们不能作为执行授权。


本仓库只维护 Scaena production、subject readiness 与 video transfer Agent Skills。

- Skill 只输出操作计划、门禁、证据和 handoff，不持有生产数据库或资产。
- 示例不得写死维护者的本机路径。
- 每个 Skill 必须包含 `SKILL.md` 与 `agents/openai.yaml`。
- 验证命令：`python3 scripts/validate_skills.py`。
