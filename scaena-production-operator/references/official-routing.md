## 官方视频直连优先路由（MiniMax H3 / Wan3）

用户指定 MiniMax H3、Wan3 官方时，先走 Scaena 原生 `createVideoProviderTask`，不要求配置 Aigora，也不改走 `createVideoRun` / `createShotRun`。ProductionGraph 的 `VIDEO_OWNER_MISSING`、`owner_unavailable` 或 shot preflight 失败不能证明官方 Provider 生成失败。

Wan3 prompt 正文优化（分镜转 wan3.0 prompt、@图片N 指代、失败 case 归因修复）走 `$wan3-prompt-optimizer`；本 skill 只管渠道、绑定、提交与恢复，不代替 prompt 写法规则，也不把出片参数确认推给 prompt 层。

无 CLI 的已连接客户端：

1. `tools/list` 确认 `scaena.search` / `scaena.execute`；读取 `scaena://video-tasks/guide`。搜索 `MiniMax`、`Wan3` 或 `createVideoProviderTask`，关闭状态使用 `include_unavailable=true` 获取参数和原因，不能执行标记不可用的动作。
2. MiniMax 使用 `binding_id=minimax-h3-intl`，参考图走 `scaena://upload/guide` 的鉴权 HTTP 上传。完成后使用 `reference_upload_ref=upload:<upload_id>`；已有上传、场景、镜头应保留，不重复创建。Wan3 使用 `binding_id=wan3-dashscope-cn`；当前绑定是文生视频，不把图生视频请求自动改成文生视频。
3. 按 `input_schema` 填写 `production_scope=experiment`、真实确认和费用上限。MiniMax 图像还要求 `reference_rights_confirmed=true`。只有非人物图可省略 `subject_mode`；人物必须如实声明；MiniMax H3/Wan3 默认支持 synthetic_virtual_person，真人仍需有效 consent grant，不能伪装成非人物。新入口不要求 shot preflight，也不替代正式镜头晋级或成片审核。
4. 保留 submission_ref；`getVideoProviderTask` 只读台账，`reconcileVideoProviderTask` 查询原任务并回收。每次新观察用新的 reconcile 幂等键；unknown 不换创建键或模型重试。入库后用 `createArtifactAccessGrant` 下载，保持 pending_review / export blocked。
5. `global_disabled` / `binding_disabled` 是 Scaena owner 配置问题；费用、精确下载域名和服务凭据由 owner 配置，不让客户端安装 CLI 或提交 Provider Key。只将真实 Provider 请求失败称为 Provider 失败，配置/模拟测试/部署/真实生成分别报告。

### Seedance 2.5 官方入口

指定Seedance 2.5官方时，使用`seedance25-ark-text-480p`、`seedance25-ark-text-720p`或`seedance25-ark-text-1080p`，先读取实时guide检查enabled。官方最高1080p（10bit HEVC），不能叫2K。需独立Ark凭据，不能使用Wetoken Key；当前官方绑定可能因缺凭据保持关闭。原生MCP尚未接通Ark的HTTP/asset参考媒体交付，不得用现有data URL上传解析器提交图片或宣称首尾帧/edit/extend已就绪。不要自动替换为Wetoken或改用其他模型。

### 官方分辨率选择

MiniMax H3 原生 2K 使用 `binding_id=minimax-h3-intl-2k`；旧 `minimax-h3-intl` 是768P。Wan3 当前官方最高1080P，使用 `wan3-dashscope-cn-1080p`；不能伪称原生2K或在没有用户要求时自动增加超分步骤。先读实时 `scaena://video-tasks/guide` 确认这些绑定已启用。用精确 binding 而非未发布的 body resolution 参数；产物尺寸以真实媒体校验为准。

## 默认视频绑定与参考图

截至 2026-09-11，当前部署默认绑定为 `wetoken-seedance25`，已用既有 Eikona 图片完成 Seedance 2.5 参考图自动备案、视频生成和下载验收。运行状态仍以实时 guide 为准。可直接指定同一 binding 和 reference_upload_ref；不要把旧 MiniMax/Wan3 示例当作当前默认。

验收用参考图 HTTPS 存储入口为临时 tunnel，重启可能换域名。若图片上传再次阻塞，检查 owner 的固定 storage endpoint 配置，不重复创建未知生成任务。当前已入库的视频下载不依赖该参考图链接继续有效。

## 视频错误恢复与素材备案

先读 `scaena://video-tasks/guide` 的 binding.registration，再选择流程：MiniMax / Wan3 为 none，不加备案前置条件；Wetoken 为 channel_auto，由渠道自动注册；Ark 为 scaena_explicit，仅可执行的官方 transport 才能主动提交。纯文本不要求素材注册。自动备案不等于客户端本地文件已能交付；读取 reference_upload_supported。为 true 时，直接复用 reference_upload_ref，由 Scaena 按 binding 的 storage profile 上传私有对象并生成短期签名地址，不让 Agent 手工提供 URL。若 local_upload_blocked_reason 非空，保留原 upload 并说明传输阻塞，不反复上传。临时 HTTPS tunnel 只用于验收，长期生产需要固定存储入口。

错误中的 details / diagnostic 是已过滤的上游事实，explanation / actions 是 Scaena 建议。分别报告来源、阶段、错误码、是否已受理以及执行方；不把 owner 配置问题说成模型生成失败。outcome_unknown 不换幂等键、不换模型、不创建替代任务。已受理后调用 reconcileVideoProviderTask 轮询原任务；生成成功但入库失败只恢复交付。即使提交响应报错，只要微服务返回了可信原任务身份，仍保留 submission_ref 并查询该任务，不重复生成。

createProviderAssetRegistration 只建本地记录。主动流程使用 submitProviderAssetRegistration（binding_id、expected_version、稳定幂等键），再 reconcileProviderAssetRegistration 查询原注册，不能手工 transition 成 approved。远端引用必须与项目、素材摘要及 Provider 账户匹配，授权与素材备案分别验证。

当前官方真人素材需要本人认证、授权及素材接收，公开自动录入 API 尚未核验，默认远端动作不可执行。引导用户完成官方必要步骤：https://www.volcengine.com/docs/82379/2315856 。不要猜测第三方 CreateAsset 路径是官方接口，也不要把 fake transport 测试称为官方已上线。

