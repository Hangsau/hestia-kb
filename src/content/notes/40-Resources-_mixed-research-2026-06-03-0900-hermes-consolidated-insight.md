---
_slug: 40-Resources-_mixed-research-2026-06-03-0900-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-03-0900-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-03'
confidence: high
title: Hermes 記憶架構：符號化存取與多階段管線的收斂
updated: '2026-06-15'
type: research
status: budding
---

# Hermes 記憶架構：符號化存取與多階段管線的收斂

**消化筆記**: 2026-06-02-rlm-paper-reinforcement-codeRLM, 2026-06-03-shapedql-multi-stage-ranking

兩篇看似無關的探索——RLM 理論與 ShapedQL SQL 引擎——在「外部知識必須結構化存取而非 context dump」這一點上收斂，指向同一個 Hermes 記憶改革方向。

---

## Cross-Cutting Theme 1: 符號化存取（Symbolic Access）取代語境填充（Context Dump）

**支援筆記**: rlm-paper-reinforcement-codeRLM, shapedql-multi-stage-ranking

### 模式

兩篇筆記攻擊的是同一個根本問題的不同變體：

| 系統 | Naive 做法 | 結構化做法 |
|------|-----------|-----------|
| RLM paper | 把 prompt 全部塞進 LLM context | 將 prompt 存為 REPL 變數，LLM 生成代碼檢查/遞迴呼叫 |
| CodeRLM | glob/grep/read loop（高噪音） | 即時符號索引作為 JSON API，精確Symbols/Callers/Implementations |
| ShapedQL | 無架構的候選檢索 | Retrieve→Filter→Score→Reorder 四階段聲明式管線 |
| Hermes（現狀） | distillates 以純文字文本塞進 context | **未實現** |

三個系統都獨立的走到了同一個結論：**外部數據必須作為可程序查詢的結構對象，而非 context buffer**。這不是巧合——這是 2026 年 AI 架構的收斂方向。

### 可行動下一步

在 `heartbeat_learning.py` 中實作「symbolic handle」介面：
1. distillates 不再以原始文本追加到 hist，改為建立 `distillate_id → {content, timestamp, confidence, supersedes}` 的映射表
2. LLM 透過 `query_distillates(topic, recency_weight, confidence_threshold)` 讀取，而非全量 dump
3. 參考 CodeRLM 的符號圖架構：建立「概念 → distillate」的 invert index

---

## Cross-Cutting Theme 2: 雙重失效檢測（Temporal + Structural）

**支援筆記**: rlm-paper-reinforcement-codeRLM（矛盾邊緣觸發失效）, shapedql-multi-stage-ranking（Filter 階段移除過期條目）

### 模式

兩篇筆記都描述了知識失效的檢測機制，但維度不同：

- **RLM/CodeRLM**: **結構性失效** — 當新 distillate 與舊节点创建矛盾邊（contradiction edge）時，失效是由於「内容衝突」而非「時間久遠」
- **ShapedQL**: **時間性失效** — Filter 階段基於 `confidence_valid_until` 移除過期條目，是基於有效期限而非內容變化

Hermes heartbeat 目前只有時間性衰減（time-based decay），缺少結構性失效檢測。結合兩者才是完整方案：

```
新 distillate 到來 → 檢索語義相似舊 distillates → 
  ├─ 若存在矛盾 → 建立 contradiction edge → 降權舊節點
  └─ 若無矛盾 → 檢查 timestamp → 若超窗則從管線 Filter 階段排除
```

這解決了 RLM 筆記中點出的核心 gap：「當新的 distillate 否定舊的，沒有機制廢除舊 distillate 的 confidence」。

### 可行動下一步

在 SSGM 实现中加入 contradiction detection：
1. 當新 distillate 寫入時，對其 topic embedding 做最近鄰檢索
2. 找出 cosine similarity > 0.85 但語意方向相反的舊 distillate
3. 建立 `supersedes` 邊，舊 distillate confidence 降至 0（而非時間衰減）
4. 這使「主題觀點演變」可以被追蹤，不只是「知識變舊」

---

## 備註

Theme 1 的可操作性更明確，Theme 2 尚屬設計階段概念。兩者都指向同一個底層原則：**Hermes 記憶需要從「文本容器」進化為「可查詢圖結構」**。