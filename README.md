# Scaena Skills

Scaena 制作编排、主体资产就绪和视频转绘流程的开源 Skills 集合。

## Skills

- `scaena-production-operator`：可恢复的 plan/subject/produce/review/assemble/verify 生产阶段。
- `scaena-subject-asset-readiness`：角色、场景、道具、服装、风格和镜头绑定的生产前门禁。
- `scaena-video-transfer-orchestrator`：已有拆解视频的市场适配、参考资产、prompt provenance、canary 和生成交接。

## 验证

```bash
git clone https://github.com/yeisme/scaena-skills.git
cd scaena-skills
python3 scripts/validate_skills.py
```

示例命令使用 `$SCAENA_PROJECT`、`$SCAENA_REPO` 等显式占位变量，不绑定维护者机器路径。生产状态、资产 bytes、provider 凭据和 acceptance 仍由 Scaena 产品拥有。

## License

[MIT](LICENSE)
