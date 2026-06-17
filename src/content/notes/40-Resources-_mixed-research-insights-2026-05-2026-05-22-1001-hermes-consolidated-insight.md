---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-22-1001-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-22-1001-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- memory
- heartbeat
source: multi
created: '2026-05-22'
confidence: high
title: Memory System 收斂：Failure Signal > Success、Expand-on-Demand 雙軸
updated: '2026-06-15'
type: research
status: budding
---

# Memory System 收斂：Failure Signal > Success、Expand-on-Demand 雙軸

**消化筆記**: 2026-05-22-agent-memory-rubric-scoring-memori-r2mem, 2026-05-22-r2-mem-rubric-thresholds-deep-dive, 2026-05-21-memori-production-memory-engine, 2026-05-21-context-compression-production-agents, 2026-05-20-r2-mem-reflective-experience-memory-search, 2026-05-20-agent-memory-taxonomy-survey

（摘要）過去一週的記憶系統探索收斂到兩個 cross-cutting insight：failure experience 的學習價值系統性高於 success experience，以及 context compression 應該是 reversible 的而非破壞性的。

## Cross-Cutting Theme 1: 失敗案例比成功案例更有價值 — 跨系統驗證

**支援筆記**: 2026-05-22-r2-mem-rubric-thresholds-deep-dive, 2026-05-20-r2-mem-reflective-experience-memory-search, 2026-05-22-agent-memory-rubric-scoring-memori-r2mem

這個結論在三篇獨立的 R²-Mem 筆記中被重複發現，且來自同一篇論文的不同維度閱讀：

- **Ablation study 數據**：只用 low-quality experience > 只用 high-quality experience（Table 4）。失敗案例提供更正信號，成功案例本來就有效不需要引導。
- **閾值設定**：最佳 K_low=5, K_high=10（score < 5 的才值得蒸餾成 corrective experience，5-10 的 skip）。
- **邏輯基礎**：R²-Mem 的 rubric 將每個 step 切成 Planning + Reflection 兩模組，每模組 4 維度共 8 個 0-3 分。低分 step（Reflection < 2）才是高價值 signal，不只是「發生 ERROR」這種粗粒度訊號。

這個 pattern 不是 R²-Mem 獨有——它只是用量化方式確認了一個原則：**真正有效的 learning signal 來自「為什麼做錯了」，不是「為什麼做對了」**。

**可行動下一步**：
- 更新 `heartbeat_learning.py` 的 pattern extraction：加入 step-level scoring（Planning/Reflection 兩維），把「Reflection < 5 的 step 指紋」當作首要萃取目標，不是 ERROR count
- 改 ISSUES.md 的 root cause 格式：從 free-text 改為 `IF-THEN experience pair`（R²-Mem 的結構），錯誤模式 explicit 化而非敘事化
- 在 vault_decay 的 decision logic 加入：低 quality + 久未用 → prune；低 quality + 最近用 → 保留但標記為 corrective lesson

---

## Cross-Cutting Theme 2: Context Compression 必須可逆 — Expand-on-Demand

**支援筆記**: 2026-05-21-context-compression-production-agents, 2026-05-21-memori-production-memory-engine, 2026-05-22-agent-memory-rubric-scoring-memori-r2mem

Context Gateway 的架構核心不是「怎麼壓」，而是「壓完的東西放哪裡」：壓縮不是刪除，是換地方存，需要時能召回。

對照 Hermes 現有系統：
- `memory-auto-distill` 是**破壞性**的：distill 後原文丟，沒有 expand 機制
- Heartbeat 的 EVOLVE snapshot 每次都存完整狀態，但長期歷史的存取成本會隨 vault 膨脹線性增加
- Memori 的 4.97% token footprint 數據說明：壓縮效果可達 20x，但代價是需要維護另一個存取層

Context Gateway 的 85% threshold proactive compaction 結合 Memori 的 dual representation（entity/process/session attribution + augmentation），構成一個可實現的架構：不刪除原文，但把「壓縮版本」作為 primary context，「未壓縮版本」放到 background storage 當 expand source。

**可行動下一步**：
- 建立 `~/.hermes/context_cache/` 目錄：存放 distill 前未壓縮的原始工具輸出，heartbeat idle 時被動觸發（容量驅動，非 cron）
- 在 `memory-auto-distill` 加入 expand flag：`--keep-raw`，保留一份原始內容供日後召回
- 實作 shallow compression（低風險 win）：tag mapping + path shortening + verbose prefix stripping，不需要 SLM classifier，效果 10-30% reduction 馬上可測

---

## 非顯然連結（排除的）

以下不是 cross-cutting theme，因為單篇筆記自己已經說完，沒有跨來源新意：
- Memori vs Titans vs R²-Mem 的機制對比（三篇各自的「跨文章 Synthesis」都做過）
- 記憶系統五大家族（arXiv survey 內部敘述，沒跨來源）
- 「selective memory 是核心問題」（Aegis + DPM 那篇已明顯）