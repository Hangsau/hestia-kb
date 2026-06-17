---
_slug: 40-Resources-_mixed-explorations-2026-05-17-WUPHF-Lint---Query-Prompt-Templates
_vault_path: 40-Resources/_mixed/explorations/2026-05-17-WUPHF-Lint---Query-Prompt-Templates.md
title: WUPHF Lint & Query Prompt Templates
date: 2026-05-17
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- json
- lint
- llm
- prompt
- query
- retrieval
- staleness
- tmpl
- wiki
- wuphf
created: '2026-05-17'
updated: '2026-06-15'
status: budding
---

# WUPHF Lint & Query Prompt Templates

**日期**: 2026-05-17 | **延續自**: [[2026-05-17-talos-governance-policy-wuphf-pipeline]]
**來源**: [nex-crm/wuphf](https://github.com/nex-crm/wuphf) `prompts/` 目錄
**時間**: 06:16 CST

---

## Source 1: lint_contradictions.tmpl

**檔案**: `prompts/lint_contradictions.tmpl`（Go template，由 `wiki_lint.go` 和 `run_lint` MCP tool 調用）

### 核心設計

一個 LLM-as-judge 的結構化 contradiction detector。輸入是共享 `(subject, predicate)` 的事實群（cluster），輸出是單一 JSON：`{contradicts: bool, reason: string}`。

### 判決規則（七條）

| # | 規則 | Hermes 對標 |
|---|------|------------|
| 1 | **Temporal validity 優先**：`valid_until` 過期的事實不與當前事實矛盾 | ↔ Known-issue TTL / dynamic staleness |
| 2 | **Specificity ≠ contradiction**："Sarah in sales" vs "Sarah in enterprise sales" | ↔ 同一提案的 detail 層次不同不算衝突 |
| 3 | **真正矛盾 = 互斥**："reports to Michael" vs "reports to David"，兩者同時有效 | ↔ 兩個 skill 對同一 config key 給不同預設值 |
| 4 | **Paraphrase ≠ contradiction**：輕微措辭差異不算 | ↔ 同一事實的不同表述 |
| 5 | **來源不同 ≠ 矛盾**：兩個來源說同一件事是 corroboration | ↔ 兩個 agent log 記錄同一事件 |
| 6 | **null valid_until = 當前有效** | ↔ 我們的提案若無 `Mute TTL` 則視為 active |
| 7 | **合理共存解釋 → 不矛盾**：err on the side of `false` | ↔ 保守 bias：寧漏報不誤報 |

### 設計亮點

- **嚴格 JSON-only 輸出**：Go caller 用 strict parser，任何 prose 前綴/後綴會導致 silent skip。這是 programmatic consumption 的強制約束。
- **Calibrated against spec**：提示詞第一行就是「Read WIKI-SCHEMA.md Section 10.4」，確保 LLM 行為與規格文件一致——不是靠提示詞本身，而是靠規格文件當 ground truth。
- **下游寫入分離**：linter 只判斷，不編輯。Go worker 根據判斷結果寫入。防止 LLM 在 judge 角色中越權。

### 對 Talos EVOLVE lint expansion 的啟發

1. **contradiction detection 的輸入應該是 cluster**：把同一 subject 的事實預先分組，再送 LLM。不要讓 LLM 自己在整個 knowledge base 裡找矛盾。
2. **temporal validity 是矛盾判斷的第一道防線**：我們的 dynamic TTL staleness formula 可以 borrow 這個設計——過期事實自動從 contradiction scan 排除。
3. **保守 bias 是必要設計**：自動化 linter 誤報比漏報更糟（alert fatigue）。

---

## Source 2: answer_query.tmpl

**檔案**: `prompts/answer_query.tmpl`（Go template，用於 `/lookup` 和 `wuphf_wiki_lookup` MCP tool）

### 核心設計

Cited-answer retrieval：輸入 query + top-K 來源，輸出帶 citation `[n]` 的 markdown + 結構化 metadata JSON。

### Query 分類系統

| QueryClass | 行為 | Hermes 應用 |
|------------|------|------------|
| `status` | 過濾 staleness > 20 的事實 | ↔ 提案狀態查詢、系統健康查詢 |
| `relationship` | 優先引用 `graph.log` 的 typed edge | ↔ agent 間相依性查詢 |
| `counterfactual` | 識別因果鏈，標記依賴條件 | ↔ "如果沒裝這個 package 會怎樣" |
| `multi_hop` | 鏈式引用來源，展示連結事實 | ↔ "誰改了這個 config → 什麼 cron 受影響" |
| `general` | 標準 cited retrieval | ↔ 通用 vault 查詢 |

### Temporal validity 處理（三層）

1. **`staleness > 20`** → status query 自動排除（Section 8.1 threshold）
2. **`valid_until` 過期** → 轉為過去式 + 標註日期範圍
3. **全部 stale** → 回「wiki 無當前資訊」+ 引用最近的歷史事實

### 引用紀律

- 每個事實宣告必須 cite 來源 index：`[1]` 或 `[1][3]`
- 引用的號碼必須對應實際來源列表
- 不允許無來源的 claim
- 不允許抄錄來源全文（>200 chars）

### 拒答政策

| 情況 | 回應 |
|------|------|
| Out-of-scope（天氣、八卦） | "I don't have information about that." 無補充 |
| 來源不足以回答 | "The wiki doesn't have information on that. What I do have: ..." |
| 不從自身知識回答 | 即使 LLM 知道答案，不允許 |

### 對 Hermes retrieval 的啟發

1. **Query classification 是 retrieval quality 的前置條件**：在查 vault 之前先分類 query type，不同 type 不同 filter。
2. **Staleness threshold (20) 值得校準**：WUPHF 用絕對值，我們可以用相對值（staleness percentile within entity）。
3. **Counterfactual query 模式新穎**：目前 Hermes 沒有 "what if" 查詢能力。可以加到 memory-consolidator 的 retrieval prompt。
4. **Citation discipline 可直接移植**：vault `/lookup` 應強制 `[n]` citation，防止 hallucinated retrieval。

---

## 跨來源 Synthesis

WUPHF 的 prompt 設計有一個統一的 pattern，Talos EVOLVE lint expansion 可以整個 borrow：

### 三層架構

```
Layer 1: Spec-anchored prompt（提示詞第一行指向 WIKI-SCHEMA.md）
Layer 2: Rules-as-constraints（正面規則 + 反面禁止）
Layer 3: Strict output schema（JSON-only，Go caller 強制 parse）
```

這個架構確保：
- **正確性**：規格文件是單一真理來源，提示詞只是執行規格
- **安全邊界**：JSON-only 輸出防止 LLM 自由文本被誤解析
- **角色隔離**：judge 不寫入，retriever 不發明

### 對 EVOLVE lint expansion 的直接移植路徑

| WUPHF 組件 | Talos 對應 |
|-----------|-----------|
| `lint_contradictions.tmpl` | EVOLVE step 7: `_check_contradictions()` |
| `answer_query.tmpl` staleness filter | Dynamic TTL formula for known issues |
| QueryClass 路由 | memory-consolidator retrieval router |
| `WIKI-SCHEMA.md` as spec anchor | `ISSUES.md` + `HEARTBEAT_MAP.md` as spec anchor |
| Go caller strict JSON parse | `heartbeat/utils.py` JSON schema validation |

### 一個未解決的設計問題

WUPHF 的 contradiction detection 需要 **pre-clustered facts**（共享 subject+predicate 的事實預先分組）。Talos 的 knowledge base（ISSUES.md、proposals/、skill frontmatter、autonomous_notes/）要如何做這個 clustering？

可能方案：
- **方案 A**：手動定義 cluster key（`subject = skill_name`, `predicate = status`）
- **方案 B**：用 embedding similarity 自動分組（成本高，Phase 3+）
- **方案 C**：先從已知的 enumeration 開始（`predicate ∈ {status, version, dependency, config}`），再逐步擴展

---

## ⏳ 未追蹤

- WUPHF `lint_orphans.tmpl` — orphan detection prompt（本筆記只 cover contradictions，orphans 的 prompt 設計可能有不同的 cluster 策略）
- WUPHF `lint_stale.tmpl` — staleness detection prompt（可能比 answer_query 的 staleness threshold 更精細）
- WUPHF `lint_crossrefs.tmpl` — broken cross-reference detection
- WUPHF WIKI-SCHEMA.md Section 10 其他 lint types 的 prompt 規格

## ✅ 本次探索完成

