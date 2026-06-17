---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-17-0700-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-17-0700-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-17'
confidence: medium
title: WUPHF Staleness-contradiction 耦合與 Role-Separation 設計債
updated: '2026-06-15'
type: research
status: budding
---

# WUPHF Staleness-contradiction 耦合與 Role-Separation 設計債

**消化筆記**: 2026-05-17-wuphf-lint-query-prompt-templates, 2026-05-17-wuphf-complete-schema-templates

兩篇 WUPHF 筆記覆蓋了不同 prompt template 與 schema 文件，但放在一起浮現了單篇沒說的架構連結。

---

## Cross-Cutting Theme 1: Staleness Formula 是 Contradiction Detection 的必要前置過濾

**支援筆記**: 2026-05-17-wuphf-lint-query-prompt-templates, 2026-05-17-wuphf-complete-schema-templates

### 分析

Note 1 討論 contradiction detection 時將「過期事實不參與矛盾判斷」列為規則 #1（`valid_until` 過期的事實不與當前事實矛盾），但沒有給出具體公式。Note 2 的 WIKI-SCHEMA.md §8.1 提供了staleness 公式：

```
staleness = (days_old × type_weight) − (confidence × 10) − reinforcement_bonus
```

其中 `type_weight: status=1.0, observation=0.5, relationship=0.2, background=0.1`。

關鍵在於：staleness > 20 → 自動排除（query-time filter）。這不是 contradiction detection 的附屬規則，而是獨立的**攔截層**——過期事實在抵達 LLM judge 之前就已被過濾，不消耗 LLM token，也不產生誤報。

### 架構意義

```
輸入事實群 → Staleness Filter (>20 → drop) → Pre-clustered facts → Contradiction Judge (LLM)
```

Note 1 描述的七條 judge 規則，隱含假設輸入已經過濾。如果把過期事實直接送進 judge，規則 #1 的邏輯會變成「judge 自己判斷是否過期」——將 temporal validity 判斷責任放在 LLM 層而非資料層，是對 LLM 的過度要求。

### 可行動下一步

在 `heartbeat/evolve.py` 的 `_check_contradictions()` 之前，新增 `_filter_stale_facts(facts, threshold=20)` 函式。計算每個 issue/proposal fact 的 staleness分數，過 threshold 的不送進 contradiction judge，直接標記為 stale 並從当前 scan 排除。reinforcement bonus 來自 heartbeat 成功 pass 該 check 的次數。

---

## Cross-Cutting Theme 2: Role-Separation 是 anti-hallucination 的主要防線

**支援筆記**: 2026-05-17-wuphf-lint-query-prompt-templates, 2026-05-17-wuphf-complete-schema-templates

### 分析

兩篇筆記各自記錄了不同的 role-separation 設計：

| Role | 職責 | 禁則 |
|------|------|------|
| Linter (judge) | 判斷是否矛盾 | 不寫入 wiki |
| Retriever | 回答查詢，附 citation | 不從自身知識回答 |
| Synthesizer | 綜合事實寫 brief | 不、原件、原樣引用 |

WUPHF 的 **三不寫** 規則（synthesis_v2.tmpl）尤其精確：synthesizer 不寫 `## Related`（graph.log 決定）、不寫 `## Sources`（renderer 決定）、不寫 frontmatter（broker 決定）。每個 role 有明確的「這不是我的事」邊界。

Note 2 的 extract_entities_lite.tmpl 更進一步：11 條 anti-pattern 規則构成显式的 "never" 清單——不是「盡量避免」而是「違反即犯規」。這種格式比彌散的「小心別 hallucinate」指示更可執行。

### 架構意義

Role-separation 減少 hallucination 的原理是：**把「發明」（fabrication）的機會從每個 role 拿掉**。Judge 不能寫，所以無法竄改輸入。Retriever 不能從自身知識回答，所以無法摻入 training data 記憶。Synthesizer 不能自己引用來源，所以無法虛構 citation。

這比「在 prompt 裡加一句 'don't make things up'」更有架構約束力——是將 hallucination 防範建立在 workflow 層次而非 prompt 層次。

### 可行動下一步

審視 `heartbeat/evolve.py` 現有的 `_check_contradictions()` 是否同時做了判斷和寫入（如果是，表示 judge 和 writer 的角色未分離）。將其拆分為 `_judge_contradictions(facts) → {contradicts, reason}` 和 `_write_verdict(issue_id, verdict)` 兩步。EVOLVE 主流程只呼叫前者，後者由 wiki worker queue 執行。

同步更新 memory-consolidator 的 retrieval prompt，加入「不從自身知識回答」的禁則（目前只有「cited retrieval」的一般性描述）。

---

## 補充觀察：WUPHF Schema 與 Hermes 架構的對稱性

Note 2 的三層架構（Raw sources → Wiki → Schema）與 Hermes 有結構造癮：

| WUPHF | Hermes |
|-------|--------|
| `wiki/artifacts/{source}/{sha}.md` | `autonomous_notes/` |
| `wiki/facts/{kind}/{slug}.jsonl` | `vault/explorations/` |
| `WIKI-SCHEMA.md` | `HEARTBEAT_MAP.md` + `ISSUES.md` |

但 Hermes 缺少 WUPHF 的 **rebuild contract**（§7.4）——刪除 index 後重啟能從 markdown 完整重建。EVOLVE 的 `_safe_json_read` + `_safe_json_append` 是類似概念的雛形，但缺少正式測試（rm `heartbeat_state.json` → 重跑 → 比對 canonical hash）。這不是本次 action item，但值得列入 Phase 3 待辦。
