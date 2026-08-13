# Scaena Skills 工作区说明

本仓库只维护 Scaena production、subject readiness 与 video transfer Agent Skills。

- Skill 只输出操作计划、门禁、证据和 handoff，不持有生产数据库或资产。
- 示例不得写死维护者的本机路径。
- 每个 Skill 必须包含 `SKILL.md` 与 `agents/openai.yaml`。
- 验证命令：`python3 scripts/validate_skills.py`。
