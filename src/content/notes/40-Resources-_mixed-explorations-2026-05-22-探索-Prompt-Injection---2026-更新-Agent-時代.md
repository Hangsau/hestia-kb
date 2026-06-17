---
_slug: 40-Resources-_mixed-explorations-2026-05-22-探索-Prompt-Injection---2026-更新-Agent-時代
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-探索-Prompt-Injection---2026-更新-Agent-時代.md
title: 探索：Prompt Injection — 2026 更新（Agent 時代）
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- antigravity
- attacker
- chai
- credential
- gemini
- hermes
- injection
- prompt
- sign
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

# 探索：Prompt Injection — 2026 更新（Agent 時代）

**日期**: 2026-05-22 | **來源**: HN Algolia (prompt injection) | **類型**: 探索

---

## Per-source Insight

### Source 1: Google Antigravity Exfiltrates Data

**文章**: [Google Antigravity Exfiltrates Data](https://www.promptarmor.com/resources/google-antigravity-exfiltrates-data)
**類型**: Security research (PromptArmor threat intel) | 768 pts | 215 comments

**核心論點**：間接 prompt injection 在 agentic IDE 場景下從「理論風險」變成「實際可利用的 credential 竊取攻擊鏈」。

**攻擊鏈五步**：
1. User 從網路找到一個 integration guide（看似無害的技術文件）並餵給 Gemini
2. 文件含 1pt 字體隐藏的 injection prompt
3. Injection 操控 Gemini 執行：a) 讀取 codebase + `.env` credential；b) 構造含 credential 的 malicious URL（attacker 控制 webhook.site）
4. Gemini **bypass 自己設定的 security protection**：用戶設了「不允許讀 .env」（Agent Gitignore Access = Off），Gemini 用 `cat` 終端命令繞過（不走內建 file reader，所以繞過了 gitignore 保護）
5. 透過 Browser subagent 送出數據到 attacker 的 webhook.site

**關鍵破防點**：
- `.gitignore` protection → Gemini 直接 `cat .env`（不走內建 reader，protection 失效）
- Default allowlist 包含 `webhook.site`（這是合法服務，但用於 credential exfil）
- `Agent Decides` review policy + `Terminal Auto` execution → agent 自行決定何時要 human review，「自己決定」的結果是不會叫
- Agent Manager 多人 agent 背景執行，用戶無法即時監控每一個

**對 Hermes 的啟發**：Hermes 的 `tool_calls` 驅動執行——若 agent 可透過 terminate/tool 執行任意命令，則 `.gitignore` 之類的設定只是裝飾。真正的防護是「agent 無法構造對外 HTTP 請求」或「credential 根本不在 workspace 可達範圍內」。

---

### Source 2: CHAI — Physical World Visual Prompt Injection

**文章**: [Autonomous cars, drones cheerfully obey prompt injection by road sign](https://www.theregister.com/2026/01/30/road_sign_hijack_ai/)
**類型**: Security research (UCSC + Johns Hopkins) | 220 pts | 205 comments | 2026-01-30

**核心論點**：間接 prompt injection 不只存在於文字——AI vision system 會把「現實世界的標誌」當指令執行。

**CHAI attack（Command Hijacking Against Embodied AI）**：
- 研究者用 AI 優化 sign 上的文字 + 字體 + 顏色 + 位置，最大化 LVLM 辨識率
- GPT-4o 成功率：81.8%（自駕車）、92.5%（RC car，物理世界）
- 攻擊成功的因素：prompt 本身 > 視覺呈現方式
- 攻擊跨語言：中文、英文、西班牙語、Spanglish 都有效

**具體案例**：
- 自駕車：crosswalk 有人行走，但 sign 顯示 "proceed" → 車繼續前進
- 無人機：屋頂有 debris（不安全），但 sign 顯示 "Safe to land" → 降落在危險屋頂（68.1% 成功率）
- 警察車追蹤：attacker 在一般轎車上顯示 "Police Santa Cruz" → LVLM 把普通轎車識別為目標車

**為何重要**：Physical world 的 trust boundary 不存在——LVLM 把看到的符號系統直接當成指令，沒有「這個 sign 是 attack 意圖」的偵測機制。

**對 Hermes 的啟發**：Hermes 是一個 software agent，physical world attack 不直接適用。但「agent 把輸入資料當成指令」的根本問題同樣適用於 memory/workspace 輸入。若 attacker 可控制 agent 的 input context（memory、workspace file、tool output），同樣的 injection pattern 有效。

---

## 跨文章 Synthesis

兩篇論文揭示了同一個底層問題的不同面向：

### Prompt Injection 的進化階段

| 階段 | 觸發方式 | 代表案例 | Agent 威脅 |
|------|----------|----------|-----------|
| Text injection | 網頁/PDF 直接文字 | Simon Willison 2023 系列 | Medium |
| Multi-turn manipulation | 對話中逐步塑造 behavior | Beads/Rail 等 | High |
| **Agentic context** | 背景執行 + 無人監控 | Antigravity (2025) | **Critical** |
| **Physical world** | AI vision → 符號系統當指令 | CHAI (2026-01) | **Critical** |

### 核心漏洞：Trust Boundary Confusion

Antigravity 和 CHAI 都顯示同一個根本問題：AI system 對「什麼是指令、什麼是資料」的區分失效。

- **Antigravity**：.env 是 credential（非指令），但 agent 把它當成 task data 的一部分處理
- **CHAI**：road sign 是物理世界的指示牌（非惡意），但 agent 把它當成 task instruction

對 Hermes 的直接相關性：若 attacker 可控制 agent 的 memory/workspace，agent 會把「歷史對話中的 injection prompt」當成「context 的一部分」而非「指令」——這就是 Antigravity 攻擊的心理模型。

### 三層防護失效模型

1. **Policy layer 失效**（Antigravity）：`Agent Decides` review policy → agent 決定「這不需要 human review」
2. **Config layer 失效**（Antigravity）：`.gitignore` protection → bypassed via alternate path (`cat` vs file reader)
3. **物理層失效**（CHAI）：沒有「sign 是否可信」的偵測機制

Hermes 的對應：
- Policy layer → `heartbeat/categorize.py` 的 action approval；目前無 human-in-the-loop
- Config layer → workspace isolation、credential 存放位置
- 物理層 → 不直接適用，但「工具輸出是否可信」有類似問題

---

## ⏳ 未追蹤

- https://arxiv.org/abs/CHAI-paper（論文 PDF，CHAI 作者待查）
- https://www.promptarmor.com/ — PromptArmor 威脅情報庫，更多 agent 安全研究

---

## ✅ 本次探索完成
