---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-18-1748-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-18-1748-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-18'
confidence: medium
title: Hermes Agent — Cross-Cutting Pattern Analysis (2026-05-17)
updated: '2026-06-15'
type: research
status: budding
---

# Hermes Agent — Cross-Cutting Pattern Analysis (2026-05-17)

**消化筆記**: aiuc1-q2-2026-detailed-changes, aiuc1-hermes-gap-analysis, docker-ai-governance-runtime-enforcement, mistle-wuphf-guardian-sandboxing, talos-governance-policy-wuphf-pipeline, everything-is-a-ralph-loop

跨 6 篇筆記的系統性連結分析，聚焦非顯然模式與具體可行動缺口。

---

## Cross-Cutting Theme 1: Credentialless Architecture 是當前最大盲點

**支援筆記**: docker-ai-governance-runtime-enforcement, mistle-wuphf-guardian-sandboxing, aiuc1-hermes-gap-analysis

### 分析

三篇筆記從不同方向指向同一個漏洞：Hermes 的 credential 處理是 post-hoc 而非前置過濾。

- **docker-ai-governance-runtime-enforcement** 定義了 credential governance 三維度：visibility control（session 只看到授權的 credential）、lifecycle scoping（session 期間有效）、exfiltration prevention（block 往外送）。三維全部缺失。
- **mistle-wuphf-guardian-sandboxing** 的 credentialless gateway 是實作範本：agent 永遠看不到 secret，gateway 在 egress 時才從 control plane 拿 credential 注入。這個架構讓 credential 洩漏在架構上不可能，而非靠 trust。
- **aiuc1-hermes-gap-analysis** 的 B005.2 對應缺口：目前的 `secret-leak-prevention` skill 只在 tool output 層做 regex scan，沒有 `pre_tool_use` 層的參數掃描，沒有 `before_llm_call` 層的訊息掃描。

顯然的連結（兩篇重複同一點）：WS-009 缺失由 aiuc1-hermes-gap-analysis 內部重複提到。不構成 cross-cutting pattern。

非顯然的是：docker-ai-governance-runtime-enforcement 的「agent 永遠不該看到 credential」與 mistle-wuphf-guardian-sandboxing 的「gateway injection」合起來是一個完整的 credentialless pattern，而 aiuc1-hermes-gap-analysis 只診斷症狀（無 formal 機制），沒有看到外部已經有成熟實作。

### 可行動下一步

在 tool gateway 層實作 `pre_tool_use` hook，針對 `write_file` 和 `patch` tool 的參數內容做 credential pattern scan（在 LLM response 變成 action 之前）。具體：

```python
# 目標：credential_leak_guard.py 新 skill
# 觸發時機：pre_tool_use event on write_file/patch
# 行為：
#   1. 掃描參數中的 credential patterns（API key, token, path secrets）
#   2. 若發現，block tool call，改寫日誌（不讓 credential 進 action log）
#   3. 回傳 blocking event 給 cognitive 層重構
```

---

## Cross-Cutting Theme 2: 工具限制是 Layer 1 但尚未 formalize

**支援筆記**: everything-is-a-ralph-loop, mistle-wuphf-guardian-sandboxing, aiuc1-hermes-gap-analysis

### 分析

Ralph philosophy 說「sitting on the loop」的核心是 engineer 不在 loop 裡面操作，WUPHF DM mode 只給 4 tools、exploration mode 限制 tool set 是這個原則的具體落地，aiuc1-hermes-gap-analysis 的 B domain 把「prevent unauthorized agent actions」列為最高優先 gap。

但三篇各自只描述一半：

- Ralph 是哲學，沒有實作細節
- WUPHF 展示了「限制 tool set」可行，但沒有延伸到 policy language
- aiuc1-hermes-gap-analysis 把 gap 對應到 WS-009，但只說「pending」沒有往前推進

cross-cutting 看出來的是：這三個 source 可以拼出一個從哲學到實作到合規的完整 storyboard，但目前的文件各自為政。特別是，Ralph 的「Monolithic > Microservices」與 WUPHF 的「per-agent scoped MCP」合在一起說的是同一件事：小攻擊面是共識，但 Hermes 的 tool scoping 只存在於 cron job config 的 `enabled_toolsets`，沒有独立 policy 文件。

### 可行動下一步

建立 `~/.hermes/policies/agent-capability.yaml`：定義探索 agent（exploration cron）只允許 `{web_search, web_extract, read_file, search_files}`，deny `terminal, write_file, patch, process`。格式參考 docker-ai-governance-runtime-enforcement 的 rule model（target + action，deny 優先）。這個 policy 是 WS-009 的實體化。

---

## Cross-Cutting Theme 3: Sub-Agent Logging 是 E015.2 的 immediate gap

**支援筆記**: aiuc1-q2-2026-detailed-changes, docker-ai-governance-runtime-enforcement, aiuc1-hermes-gap-analysis

### 分析

aiuc1-q2-2026-detailed-changes 識別出 E015.2（net new）：logging 必須覆蓋 tool calls + sub-agent actions + provenance metadata。aiuc1-hermes-gap-analysis 確認 Heartbeat 的 `action_log.json` 只有 action 層，sub-agent 層（`delegate_task`）的 traceability 是空白。docker-ai-governance-runtime-enforcement 的 MCP tool governance 的 audit trail 要求進一步確認：每個 MCP call 需要完整的 who/what/when/why 記錄。

非顯然之處：aiuc1-q2-2026-detailed-changes 單獨看是 changelog 抄寫，但配合 docker-ai-governance-runtime-enforcement 的 audit 要求，E015.2 不是一條普通的 changelog 條目，而是 AIUC-1 對整個 agent ecosystem 的 logging 架構要求。Hermes 目前只有心跳層的 action log，缺少：

1. sub-agent 的 tool call log（每個 `delegate_task` 內部的工具調用）
2. MCP-level 的 call record（若未來接入 MCP server）
3. provenance metadata（哪個 trigger 導致這次 action）

### 可行動下一步

擴展 `action_log.json` schema，加入 `sub_agents` 陣列欄位。Heartbeat 在呼叫 `delegate_task` 時，sub-agent 完成後必須寫入 `{sub_agent_id, tool_calls[], outcome, duration}`。格式參考 docker-ai-governance-runtime-enforcement 的 structured event format（user identity → session context → triggered rule）。

---

## Cross-Cutting Theme 4: 三層知識架構（Immutable / Wiki / Schema）Hermes 缺第一層

**支援筆記**: talos-governance-policy-wuphf-pipeline, everything-is-a-ralph-loop

### 分析

talos-governance-policy-wuphf-pipeline 的 L1/L2/L3 知識架構（WUPHF）：
- **L1**: Raw sources（immutable，`wiki/artifacts/`）— agent 不得修改原始攝取內容
- **L2**: Wiki（LLM-owned，可寫入）— 從 raw 加工而來的結構化知識
- **L3**: Schema（operational contract）— facts 的 promotion criteria

everything-is-a-ralph-loop 的「Progress lives in files and git」呼應 L1：Hermes 的 autonomous_notes、state JSON、comms repo 是分散式進度儲存的正確方向。

非顯然連結：WUPHF 明確指出 L1 immutable 是防止 agent self-reinforcement bias 的關鍵——如果 raw source 可以被覆寫，agent 會傾向於修改不符合自己假設的輸入。Hermes 的 autonomous_notes 目前同時承擔 L1 和 L2 的角色（raw source 也是 LLM 寫入層），沒有 immutability boundary。這是 self-modification 的隱性風險：沒有 immutable layer，agent 的輸入本身可以被自己污染。

Ralph 的 git-based progress 追蹤可以補上 L1：把 `autonomous_notes/` 視為 immutable append-only log，vault 的 `explorations/` 是 L2 wiki，skills 和 ISSUES.md 是 L3 schema。

### 可行動下一步

在 `~/.hermes/autonomous_notes/` 設定 git write protection（pre-commit hook 禁止 `git push -f`），並將笔记分为两类：
- `autonomous_notes/RAW/` — append-only，git revert 保護，agent 只能 append 不能 modify 或 delete
- `autonomous_notes/PROCESSED/` — 可修改，是 L2 的工作區

这样 LLM 的训练数据来源就有了 immutable 基础，防止 self-reinforcement drift。

---

## 總結

| Theme | Confidence | 行動優先級 |
|-------|------------|-----------|
| Credentialless gateway | medium | **P0** — 現有架構有 credential 洩漏可能 |
| Tool scoping formalize | medium | **P1** — WS-009 需要實體化 |
| Sub-agent logging | medium | **P1** — E015.2 即時合規缺口 |
| Immutable knowledge layer | low | **P2** — 長期風險，self-reinforcement drift |

前三個都可以在現有架構內用新 skill 或 schema 變更實作，無需架構重構。