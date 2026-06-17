---
_slug: 30-Areas-learnings-2026-05-23-1600-context-distiller
_vault_path: 30-Areas/learnings/2026-05-23-1600-context-distiller.md
tags:
- distillation
- context-distiller
- research
source: session review
created: '2026-05-23'
confidence: high
title: Distiller Findings — 2026-05-23 16:00 UTC+8
updated: '2026-06-15'
type: learning
status: budding
---

# Distiller Findings — 2026-05-23 16:00 UTC+8

## Session Coverage

覆盤 8 個 session（過去 4 小時）：
- `session_20260523_141943` — Forge/Preflight 架構研究（弱模型 planning vs coding 弱點分析）
- `session_20260523_142557` — Preflight triage.ts/patterns.ts/contracts.ts 實作細節解讀
- `session_20260523_151048/151119` — 重複請求（Forge agent prompts，repo 找錯）
- `session_20260523_151229` — 確認 repo 錯誤，重新研究 hermes-agent 實際內容
- `session_20260523_151355` — 游泳內容 GitHub 上傳問題諮詢
- `session_20260523_153856` — 自主 cron run（無用戶）
- `session_20260523_150505/150910` — 重複請求
- `session_20260523_131903/131956` — 自主研究探索

---

## 新發現

### 1. Forge/Preflight 可移植機制（高價值）

多 session 研究 Forge agent orchestration 和 Preflight triage system後，識別出以下可完全移植到 Hermes 的機械化機制：

| 機制 | 來源 | Hermes 實作位置 |
|------|------|-----------------|
| `validate` 工具（AST check、command execution、contract check） | Forge MCP | → `writing-plans` skill |
| `iteration_state` stagnation/oscillation detection | Forge MCP | → `writing-plans` retry logic |
| Phase-gated workflow（Plan → Review → Execute → Validate） | Forge | → `plan-review` → `implement` |
| `triage.ts` decision tree（5 級分類：trivial/clear/ambiguous/cross-service/multi-step） | Preflight | → 新的 `prompt-triage` skill |
| Correction pattern learning（JSONL + keyword clustering, ≥0.3 overlap） | Preflight patterns.ts | → `workspace-context` failure ledger |
| LanceDB timeline search schema（vector + SQL WHERE filtering） | Preflight | → vault lookup 替代方案 |
| 12-category scorecard | Preflight | → MiniMax prompt 品質評估 |

**核心洞察**：Forge/Preflight 把「需要強模型做的事」（planning、reviewing）和「純機械的事」（validation、state tracking、memory）分得很清楚。機械部分 Hermes 可以直接移植。

### 2. 新 failure mode：STATUS=DONE 但磁碟實體不存在

區別於既有「INDEX 飄移」模式：

| Pattern | INDEX 有 row | STATUS | 磁碟實體 |
|---------|-------------|--------|---------|
| 已知：INDEX 飄移 | ✅ | 任意 | ❌ |
| **新：Status Done 但檔案缺失** | ✅ | DONE | ❌ |

已在 `heartbeat-v2-autonomous-maintenance` skill 追蹤（WS-010 + otp_gate.py 案例）。

### 3. M6 Hermes 系統缺口已識別

`agent-core-concepts.md` 新增 Chapter M6：

| ID | 缺口名稱 | 嚴重性 |
|----|----------|--------|
| M6-1 | Heartbeat Rubin Score Loop 斷裂 | P0 |
| M6-2 | Sub-agent 審計追蹤空白（delegate_task traceability） | P0 |
| M6-3 | LoopTrap：自我終止可被遊戲 | P0 |
| M6-4 | L1/L2 知識邊界缺失 | P1 |
| M6-5 | Token budget 三維優化缺失 | P1 |
| M6-6 | BM25 re-rank 層缺失 | P1 |
| M6-7 | Architect/Executive 分離 | P1 |

### 4. 游泳文獻缺口

仰泳/蛙泳全章空白，待檢索：
- 仰泳：7 組關鍵字待輪替
- 蛙泳：待補充
- 蝶泳：划臂/呼吸/配合待補充

---

## Heartbeat 行為模式

本次窗口：`11 EVOLVE / 7 WORK / 2 REST`
系統偏重自主演化而非執行工作。

---

## 待追蹤

- [ ] M6-1：Heartbeat threshold-trigger circuit
- [ ] M6-2：sub-agent provenance log
- [ ] M6-3：heartbeat terminator 確定性停止條件
- [ ] M6-4：RAW/PROCESSED 雙層分離
- [ ] M6-6：vault lookup 加 BM25 re-rank
- [ ] 游泳：仰泳/蛙泳文獻檢索
- [ ] WS-010 / otp_gate.py 檔案缺失 issue