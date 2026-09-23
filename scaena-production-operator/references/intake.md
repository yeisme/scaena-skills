## Quick 产物进入生产（quick capture gate）

用户工作区的 quick 视频要进入项目时，走显式 capture，而不是移动文件：

1. capture 前 checksum/readability/rights inspection 必须通过；失败零写（`QUICK_CANDIDATE_*` 稳定码）。
2. capture 只写 `pending_review` candidate；candidate accepted ≠ shot accepted，两级独立人工决策。
3. native audio 单独 review（`audio=off` 豁免）；blocking findings 或 unresolved rights 一律阻断 export（fail closed）。
4. quick/candidate 来源 refs 只有在 explicit review→freeze→shot binding 之后才能进入 production input bundle；含 quick/candidate 成员的 bundle 只能按 candidate mode 提交，不放宽 gate。

随手视频（无项目、个人预览）不路由本 Skill，走 `scaena-local-video-operator`；本 Skill 只处理做剧生产。

## Single-file multitransport intake

For a client file, discover `scaena://input/capabilities` and the installed execute schemas. Use `input.prepare` with purpose `production_input` and one stable idempotency key. Prefer executable `object_storage` through the transient HTTP `POST /input-requests/{id}/transfer` plan, then `http_put`; a user may select/preview a file on the one-time page. Only when explicitly advertised, a client program may encode a file up to the owner's inline limit (default 4 MiB) for `input.upload_base64` with file name, MIME, size, SHA-256 and `data_base64`. The dedicated MCP envelope permits 6 MiB; ordinary/legacy actions retain their original limits. Never ask the model to produce or echo base64.

Call `input.complete` after transfer; repeated completion returns the original receipt. Query `input.status` before retry/switch, wait for active writers, and reuse the request. A failed auth, MIME, digest, permission or capacity check cannot be bypassed by switching transport. Keep temporary plans/grants/signatures and file bytes out of logs and notes. An object-store PUT receives only its required signed headers, never the MCP bearer or owner grant. Upload readiness does not approve generation, transcription, rights or canonical acceptance. Owner configuration is documented in the product's `docs/mcp-input-intake.md`; missing object storage does not disable separately configured HTTP/base64.
