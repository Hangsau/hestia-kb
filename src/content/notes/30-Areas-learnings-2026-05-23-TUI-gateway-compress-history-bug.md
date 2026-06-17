---
_slug: 30-Areas-learnings-2026-05-23-TUI-gateway-compress-history-bug
_vault_path: 30-Areas/learnings/2026-05-23-TUI-gateway-compress-history-bug.md
title: TUI Gateway 壓縮後記憶丢失 bug
created: '2026-05-24'
updated: '2026-06-15'
type: learning
tags: []
status: budding
---

# TUI Gateway 壓縮後記憶丢失 bug

**session**: `20260523_233035_6135f7`  
**source**: 深度程式碼追蹤（Hestia 分析）  
**type**: architecture-gap / bug-pattern  

---

## 問題描述

TUI gateway 的 context compression（上下文壓縮）存在**單輪內有效、跨輪次無效**的缺陷。

架構如下：

1. 訊息進入 → gateway 從 session entry 取出 `history`（存在記憶體 dict）當 `conversation_history` 傳給 agent
2. Agent 內部 `_compress_context()` 在該輪執行了壓縮，但只改變**這輪看到的 list**
3. **壓縮後的 list 並未寫回 session entry** → `session["history"]` 依然維持上一輪未壓縮的原始狀態
4. 下一輪來，conversation_history 又是從 session entry load 原始未壓縮版本
5. 結果：每輪 agent 做的壓縮白做，記憶體每次重啟都從未壓縮狀態開始

對比：一般 gateway（`gateway/run.py`）有獨立 `_compress_context` 函式處理寫回。

## PR #6464 LCM 的對應狀況

| 問題 | LCM 解法 | TUI gateway 缺口 |
|------|----------|-----------------|
| 跨 session 重啟後狀態丢失 | `rebuild_from_session()` / `to_session_metadata()` — 寫入 session JSON | 已有的 hook：`on_session_start/end()` |
| 單一 session 內每輪丢失壓縮狀態 | 不在 LCM 解決範圍 | 缺口明確存在 |

## 修復方向

TUI gateway 需要在 `_compress_context` 之後呼叫鉤子（`on_session_end` 或類似的 `write_history_back` 方法）將壓縮後的狀態寫回 session entry 的 `history` 欄位。具體實作待 investigation。

## 標誌症狀

- Session 內每輪 message count 持續上升而不压缩
- 觀察：`session["history"]` 在多輪後未變短
- 對比一般 gateway 行為可確認差異

## See Also

- [[heartbeat-competitive-landscape]] — LCM (Lossless Context Management) PR #6464 細節
- [[context-distiller]] — 本次 distill cycle 記錄