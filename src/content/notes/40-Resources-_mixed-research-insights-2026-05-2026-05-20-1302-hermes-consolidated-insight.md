---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-20-1302-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-20-1302-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-20'
confidence: high
title: 自主記憶系統的兩個正交維度：抑制迴路與反射迴路
updated: '2026-06-15'
type: research
status: budding
---

# 自主記憶系統的兩個正交維度：抑制迴路與反射迴路

**消化筆記**: agent-memory-taxonomy-survey, aegis-memory-deep-dive, llm-agent-memory-biological-decay, r2-mem-reflective-experience-memory-search, google-titans-neural-memory, autoagents-rust-multi-agent-framework

兩天六篇筆記集中研究 LLM agent 記憶系統，涵蓋學術論文（Titans、R²-Mem）、產業實現（Aegis、YourMemory）和框架層面（AutoAgents）。看似都在談「記憶」，但 cross-cutting 分析揭示兩個完全不同維度的設計決策——多數論文只處理其中一個，**兩者同時實作者極少**。

---

## Cross-Cutting Theme 1: 抑制比存取更重要（The Suppression-First Principle）

**支援筆記**: agent-memory-taxonomy-survey, aegis-memory-deep-dive, llm-agent-memory-biological-decay, google-titans-neural-memory

### 分析

四篇來源從四個角度獨立抵達同一結論：

**YourMemory（生物衰減）**：核心機制是指數衰減函數 `strength = importance × e^(−λ×active_days) × (1 + recall_count × 0.2)`，category-specific 半衰期（failure ~11天、assumption ~19天、fact ~24天）。**主動清除**低於 0.05 的記憶是系統的核心動作，而非儲存動作。

**Aegis Memory（矛盾追蹤）**：不做刪除，而是建立 `contradicts` typed edge。當新聲稱與舊記憶矛盾時，建立審計軌跡，而非覆寫或丟棄。這是**抑制的另一種形式**——抑制的不是記憶本身，而是記憶之間的衝突擴散。

**arXiv Taxonomy Survey（學術框架）**：將「Learned forgetting」列為五大 Open Challenges 之一，與 continual consolidation、causally grounded retrieval 並列。explicit forgetting（Hermes ISSUES.md 已有）不等於 learned forgetting（根據 metric 動態調整）。

**Google Titans（神經記憶）**：Gated Branch 變體的核心思想是「門控機制動態選擇使用哪種 memory」——不是存更多，而是選擇何時不存取。與 decay curve 家族同構，只是實作層面是神經網路而非規則引擎。

### 共同模式

```
存儲（Store）            抑制（Suppress）
  │                          │
  ├── yourmemory: decay      ├── decay rate（category-specific）
  ├── aegis: typed edge      ├── contradiction edge
  ├── titans: gated branch   ├── attention gating
  └── hermes: vault ingest   └── ISSUES.md（static, manual）
```

**單篇筆記內沒說的**：這四個系統都在試圖解決「噪聲累积、矛盾事實並存」這個共同問題，但各自只解決了抑制的一個子維度。把它們放在一起，浮現的原則是：**抑制機制必須與存儲機制正交設計，不能是存儲的附屬品**。Hermes 的 vault ingest 是存儲側，ISSUES.md suppression 是抑制側，但兩者完全獨立、沒有 metric-driven 互動。

### 可行動下一步

在 ISSUES.md 加入 `access_count` 和 `last_resolved_check` 欄位，每 24 小時做一次 recency decay：

```python
# 如果錯誤已經 N 天沒出現，降低 severity 直到明確修復
decay_factor = e^(-lambda * days_since_last_seen)
if decay_factor < threshold and not "config" in issue_tag:
    demote_severity(issue, new_level="info")
```

這讓抑制從「手動標記」升級為「metric-driven decay」，同時保留手動 override 能力。

---

## Cross-Cutting Theme 2: 反射不需要大模型（Reflection is RL-free and Model-size-agnostic）

**支援筆記**: aegis-memory-deep-dive, r2-mem-reflective-experience-memory-search, llm-agent-memory-biological-decay

### 分析

**Aegis ACE Loop**：Completion → 自動投票（success=True → 所有用過的 memories vote helpful；failure → vote harmful + 建立 reflection memory）→ Curation。核心 claim：**self-improvement 是 automatic loop，不需要人工干預**。

**R²-Mem Ablation 發現**：只用低質量經驗 > 只用高質量經驗。Table 10 顯示即使不用 GPT-4o 做 evaluator，self-evo 版本仍能持續打敗 GAM baseline，與 GPT-4o-evaluated 版本差距極小（Qwen-14B 只差 0.43 F1）。

**HN Practitioner 共識**（YourMemory 討論串）：giancarlostoro：「ticketing > 記憶，agent 完成後 compact memory 再接下一個 task」。這是另一種形式的即時反射：不是等下一輪 planning 才改進，是 action 結束後立刻做 memory compaction。

### 共同模式

```
Aegis:    completion → auto-vote → reflection memory → curate
R²-Mem:   trajectory → rubric scoring → IF-THEN experience → guide future
YourMem:  (no reflection; decay IS the feedback)
Hermes:   ??? (heartbeat_learning.py = pure pattern extraction, no loop)
```

**單篇筆記內沒說的**：Aegis 和 R²-Mem 的作者群完全獨立，但都得出「RL-free reflection 有效」+「小模型足夠」的結論。更重要的是，HN practitioners 的實務經驗（Aegis 討論串）直接驗證了這個方向——有人已經從 Beads 改到 SQLite guardrails，因為「ticketing > 記憶」。

三者的共同前提：**reflection 的目標不是「記得更多」，而是「讓下一個 action 的決策品質更高」**。這把 self-improvement 的衡量標準從「recall rate」轉移到「action quality improvement per action」。

### 可行動下一步

升級 `heartbeat_learning.py`，加入 completion signal：

1. 在每個 heartbeat action 完成後，立即執行：`record_action_outcome(action_type, success, duration, resources_used)`
2. 每小時計算每個 action type 的 success rate trend
3. 當某個 action type 的 success rate 下降超過 20% 持續 3 個週期 → 自動在 ISSUES.md 建立「action quality degradation」條目，並附上 trend data

這不需要 LLM，用簡單的 sliding window 統計即可實現，卻能把 heartbeat 從「錯誤偵測器」升級為「action quality monitor」。

---

## 觀察：框架層（AutoAgents）的橋接角色

AutoAgents 的設計處在一個微妙位置：它的 sliding window memory 是純粹的 storage-side，而 LLMLayer guardrails 是純粹的 suppression-side。**兩者之間沒有反射迴路**——framework level 的 reflection 需要應用層實現。

這意味著：未來無論採用哪個 memory framework（Aegis / R²-Mem / YourMemory），都需要在 framework 之上疊加一個自定義的 reflection layer。Hermes 的 vault + heartbeat 架構恰好提供了這個疊加層的天然棲息點——問題只是要讓兩者真正互動，而不是各自運作。

---

## Confidence Summary

| Theme | 交叉驗證筆記數 | 信心 |
|-------|--------------|------|
| 抑制 > 存取（正交設計） | 4（taxonomy, aegis, yourmemory, titans）| HIGH |
| RL-free 小模型反射 | 3（aegis, r²-mem, yourmemory HN）| HIGH |