---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-1000-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-1000-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-17'
confidence: medium
title: Enforcement 級別與 Self-Healing Pipeline： Reliability 的兩個座標軸
updated: '2026-06-15'
type: research
status: budding
---

# Enforcement 級別與 Self-Healing Pipeline： Reliability 的兩個座標軸

**消化筆記**: 2026-05-17-12-factor-agents-endless-toil-reliability, 2026-05-17-sandboxing-agent-linux-bubblewrap-kernel

（12-factor Agents 談 agent 架構層級的 reliability原則，Endless Toil 談程式碼層級的 code quality scanner，Sandboxing 談程序層級的 isolation。三篇從不同高度探測同一個問題：Hermes 的 failure 應對體系缺少哪些層次。）

---

## Cross-Cutting Theme 1: 三種 Enforcement 級別構成互補的 failure 防火牆

**支援筆記**: 2026-05-17-12-factor-agents-endless-toil-reliability, 2026-05-17-sandboxing-agent-linux-bubblewrap-kernel

### 分析

兩篇筆記從不同方向觸及同一個問題：Hermes 的 tool call 失敗時，系統在哪個層次應對？

12-factor Factor 8 的 interrupt point 在 tool selection ↔ invocation 之间——這是 **LLM 决策层**的 gate，在 LLM 決定呼叫什麼 tool 到 tool 真正執行之間插入 policy check。

Endless Toil 的 code quality scanner 卻是 **靜態分析層**——在程式碼寫入之前就攔截，不需要 LLM，純 regex + heuristic，零 token 成本。

bubblewrap/sandboxing 是 **程序執行層**的隔離——即使前面的判斷都通過，程序本身的 filesystem 可視範圍已被 kernel namespace 限制，agent 無法觸及不該觸及的檔案。

三層湊在一起形成一個 failure 等級表：

| 層次 | 失敗類型 | 對應解法 | 成本 |
|------|---------|---------|------|
| 靜態分析層 | Code quality smell（空 catch、debug leftover） | Endless Toil regex scanner | 零 |
| LLM 决策層 | 錯誤的 tool selection / 無效 self-heal spin-out | Factor 8 interrupt + Factor 9 error compaction | 中（LLM call） |
| 程序執行層 | Credential exfiltration / filesystem 誤寫 | bubblewrap mount namespace | 極低 |

**目前 Hermes 只在最左邊那層**：EVOLVE 的 `_check_script_integrity()` 做 syntax check（類似靜態分析），但 code quality smell（空 catch、debug leftover）完全沒被捕捉。LLM decision 層只有粗糙的 `enabled_toolsets` switch，沒有 per-call interrupt。程序執行層是零隔離。

### 可行動下一步

在 `heartbeat/evolve.py` 現有 `_check_script_integrity()` 之後，新增 `_check_code_quality()`，直接移植 Endless Toil 的 10 patterns + 3 structural signals（見原筆記表格），評分寫入 heartbeat state。分數 ≥25 視為 warning，≥40 視為 critical。同時在 `talos` policy layer 評估 bubblewrap 的可行性和威脅模型——如果無 root 可用，優先走 user namespace mode。

---

## Cross-Cutting Theme 2: Self-Healing 接力棒：Scanner → Compact Error → Sandbox-gated Retry

**支援筆記**: 2026-05-17-12-factor-agents-endless-toil-reliability, 2026-05-17-sandboxing-agent-linux-bubblewrap-kernel

### 分析

Factor 9（Compact Errors into Context Window）談的是「EVOLVE 發現錯誤 → 讓 LLM 自己修」。Endless Toil 談的是「在錯誤發生之前就攔截 code quality smell」。bubblewrap 談的是「即使其他層都失敗，process 也接觸不到 credential」。

把三個概念串成一個 pipeline：

```
Code Quality Scanner (Endless Toil) 
  → 攔截 static smell，preventable error 在寫入前消除
  
EVOLVE error detection
  → 運行時發現的 error，進 Factor 9 self-heal loop
  
bubblewrap filesystem boundary
  → self-heal 失敗或 credential 嘗試外洩時的最後物理隔離
```

這個 pipeline 的關鍵 property：**每一層處理的 failure 類型不同，互不重疊**。Scanner 處理「確定是問題但從未被執行」的 dead code smell。Factor 9 處理「實際發生、且需要 LLM 判斷怎麼修」的 runtime error。bubblewrap 處理「所有上層都失效」的 worst-case credential exfiltration。

Factor 9 的 `_attempt_self_heal()` 設計（errorCounter ≤3 spin-out 限制）防止 LLM 在無法修復的錯誤上无限循环。bubblewrap 的威脅模型（明確放棄 kernel escape 防守）則是對的——不該用 sandbox 來防禦「聰明的 LLM 找到 kernel 漏洞」，而是用來防「意外的 credential 誤寫入」。

### 可行動下一步

在 EVOLVE 新增 self-heal 層之前，先完成 code quality scanner（Theme 1 的 next step）。原因是：code quality scanner 成本為零，且能消除大部分可預防的 error，讓 self-heal loop 真正需要處理的 error 類型更少、更明確。Self-heal 的錯誤定址只有在 error pool 足夠穩定時才有意义——否則 scanner 都還沒穩定，就急著做 self-heal pipeline，會製造更多 spin-out。

---

## 備註：三層與 Policy Lifecycle 的對應

| 層次 | 對應 Policy Lifecycle |
|------|----------------------|
| 靜態分析層（Endless Toil） | Definition 前置——不符合 quality 標準的 code 從一開始就不該進入 codebase |
| LLM Decision 層（Factor 8/9） | Enforcement——runtime interrupt + self-heal |
| 程序執行層（bubblewrap） | Audit 最後防線——所有上層失效後的物理隔離 |

Policy Lifecycle 筆記（2026-05-17-0300）指出 Hermes 的 Definition→Enforcement→Audit 是斷裂的。這兩篇筆記的回答是：三層 enforcement 各自對應不同的 policy phase，且三層是串接的，不是並列的。
