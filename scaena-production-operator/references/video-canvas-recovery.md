# 视频画幅与错误恢复

适用于比例、分辨率、衣摆/动作出画、分阶段高清输出和任务恢复。设计源是Scaena项目 `docs/protocols/video-canvas-recovery.md` 及 `openspec/changes/scaena-video-canvas-recovery-v1/`；新自动恢复与VideoCanvasCheck仍planned。

## 先发现真实能力

```bash
scaena video --help
scaena video model list --json
scaena video model show --model <model-ref> --json
scaena video auth list --json
```

检查model/channel/APISurface/task mode/生成阶段。独立比例与分辨率列表不保证组合可用，fixture_verified不证明线上可用。HTTP/MCP、quick与项目生产有独立scope；不能从CLI支持推断远程任务已开放同参数。无CLI时用已注册MCP search/schema/resources。

## 冻结画布和镜头

分开记录硬比例、精确像素/原生档位、时长、FPS、音频、参考角色、首尾帧与构图时间区间。2K/4K不通用等于固定像素；adaptive按操作合同选输入，默认横幅不得覆盖明确竖幅。高清若需要额外regenerate/upscale，展示阶段、费用和lineage，不默认收费追加。

## 复核原片

读取实际编码尺寸、SAR、旋转、显示比例、帧率和时长；派生补边/裁切/超分不能冒充原视频达标。检查首尾、切点、动作关键PTS，抽样记录覆盖与盲区，首帧完整不能证明全片完整。区分衣物遮脚、主体运动出画、预览或导出裁切；依冻结镜头要求复核，特写不套全身规则，失败后也不能改意图放行。

## 有界恢复

新自动恢复合同尚未实现；安装版本没有入口时返回capability gap和候选建议，不伪造命令或声称已切换。

入口可用后，仅可信未提交/未生成允许根策略内切换；本地无文件、503、VideoAvailable=false或lease过期不够。已接单查原任务、已生成恢复下载、超分失败只恢复该阶段。未知提交有限等待后返回resume ref，不重复生成；其他独立工作可在预算内继续。

优先同型号合法通道；跨模型须allowlist，保留引用、音轨、时长、task mode、画幅和execution owner。沿用single-child retry/CAS/late-result fence；策略内授权持续有效，不反复确认相同范围，越界需指出具体差异。无查单或切换合同就返回明确unavailable/unresolved，而非持续轮询。

quick仍production_ready=false；experiment、candidate accepted、shot accepted不同。技能只消费owner状态，不手写receipt/metadata；本地测试不替代真实canary或人工生产验收。
