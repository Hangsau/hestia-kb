---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-20-1102-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-20-1102-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-20'
confidence: high
title: 記憶 × 行為 × 忘卻：三重自我改進弧線
updated: '2026-06-15'
type: research
status: budding
---

# 記憶 × 行為 × 忘卻：三重自我改進弧線

**消化筆記**: 2026-05-21-mcp-agent-workflow-class-asyncio-pattern, 2026-05-20-aegis-memory-deep-dive, 2026-05-20-llm-agent-memory-biological-decay, 2026-05-20-axe-memory-system-orloj-hierarchical-blueprint, 2026-05-20-mcp-agent-hermes-pipelex-write-queue, 2026-05-20-r2-mem-reflective-experience-memory-search, 2026-05-20-agent-memory-taxonomy-survey, 2026-05-20-autoagents-rust-multi-agent-framework

（摘要）八篇筆記涵蓋記憶系統、生物衰減、MCP workflow、multi-agent 框架。縱觀後浮現兩條非顯然弧線：自我改進在「記憶層」與「行為層」是兩條平行弧線；以及「interface」與「orchestration」必須分層處理。

---

## Cross-Cutting Theme 1: 自我改進的兩條弧線——記憶層 vs 行為層

**支援筆記**: aegis-memory-deep-dive, r2-mem-reflective-experience-memory-search, agent-memory-taxonomy-survey, axe-memory-system-orloj-hierarchical-blueprint

### 分析

這四篇筆記各自討論不同的 self-improvement 機制，但放在一起看，輪廓清楚了：

| 系統 | 層次 | 核心機制 |
|------|------|---------|
| Aegis Memory | 記憶層 | ACE loop：completion → auto-vote → reflection memory |
| R²-Mem | 行為層 | Rubric-eval（8 維度評分）→ IF-THEN experience pairs |
| arXiv taxonomy | 缺失診斷 | 兩者都列為「Reflective self-improvement」但尚未實作 |
| Axe GC | 模式畢業 | 記憶 → 人工決策 → SKILL.md 更新 |

**為何這條弧線之前不明顯**：
- Aegis 和 R²-Mem 分別被當成「記憶系統」和「搜尋系統」討論，但本質都是 self-improvement
- 各自都沒有明說「這是記憶層 vs 行為層的分工」

**關鍵洞察**：兩條弧線必須分開實作，不能用同一套反饋迴路處理。
- 記憶層：管「context 內容」的 quality → Aegis 的 typed edge 矛盾追蹤
- 行為層：管「決策品質」的 quality → R²-Mem 的 rubric scoring

**意外發現**（R²-Mem ablation）：低質量案例比高質量案例更有價值。失敗行為提供更強的修正信號，因為成功行為本來就不需要被引導。這對 ISSUES.md 的設計有直接影響——複盤焦點應在「哪一步錯了」而非「哪一步對了」。

### 可行動下一步

在 `heartbeat_evolve.md` 提案中新增一個 **Dual-loop Self-Evolution** 架構：
1. **記憶層 loop**：每個 session 完成後，heartbeat_v2 對本 session 寫入的 memories 做 success/failure vote（參考 Aegis ACE loop）
2. **行為層 loop**：每 10 個 session 做一次 rubric evaluation（參考 R²-Mem 的 8 維度），產出 IF-THEN experience pairs 寫入 vault
3. 兩者都不得自動寫入 SKILL.md——需要 `--approve-evolution` flag 人工確認

---

## Cross-Cutting Theme 2: 忘卻比記憶更重要——矛盾追蹤取代刪除

**支援筆記**: llm-agent-memory-biological-decay, agent-memory-taxonomy-survey, aegis-memory-deep-dive, axe-memory-system-orloj-hierarchical-blueprint

### 分析

四篇筆記從不同角度談同一件事：

- **YourMemory**：category-specific decay——strategy ~38天、fact ~24天、assumption ~19天、failure ~11天
- **arXiv taxonomy**：「Learned forgetting」是五大 open challenges 之一
- **Aegis**：不是刪除矛盾記憶，而是建立 `contradicts` typed edge + confidence + rationale
- **Axe**：Patterns graduate to config——記憶最終要變成 skill，不是永久保留

**為何這條弧線之前不明顯**：
- 每篇都是「我想怎麼忘」，但合在一起是「什麼時候忘」+「忘了怎麼處理矛盾」+「忘了之後系統怎麼長大」三個子問題
- 沒有一篇單獨涵蓋這三個子問題的連結

**關鍵洞察**：Hermes 的 ISSUES.md suppression 只是 explicit forgetting（靜態名單）。真正需要的是：
1. **矛盾追蹤**：新 issue 寫入時，檢查是否與現有 root cause 假設矛盾，建立 typed edge 而非覆寫
2. **category-specific TTL**：不同 severity 的錯誤有不同的「可視為已解決」時間窗口（TRANSIENT 24h、CONFIG 直到明確修復）
3. **Spatial recall**（YourMemory）：workspace path 作為重要性的 spatial signal——與 Hermes 的 INDEX.md 提案可以結合

### 可行動下一步

改造 `ISSUES.md` 為 **ISSUE GRAPH**：
```
## /path/to/failure:2024-01-15
status: SUPPRESSED
contradicts: /path/to/other-failure:2024-03-01 (confidence: 0.73)
category: CONFIG
decay_ttl: never  # CONFIG 永不自動清除
last_seen: 2026-05-10
```

同時在 `memory-consolidator` 的下一個版本加入 **contradiction check**：新 session 完成後，檢查 heartbeat action 中的 failure patterns 是否與 vault 中現有 suppressed issues 矛盾，矛盾時提升 severity 或註記「待確認」。這比「ISSUE 出現就加名單」更嚴謹。

---

## Cross-Cutting Theme 3: Declarative pipeline 將取代 imperative queue——Hermes 的 interface/orchestration 分層已刻不容緩

**支援筆記**: mcp-agent-workflow-class-asyncio-pattern, mcp-agent-hermes-pipelex-write-queue, axe-memory-system-orloj-hierarchical-blueprint, autoagents-rust-multi-agent-framework

### 分析

四個外部系統有驚人的收斂：

- **mcp-agent Workflow**：decorator → `WorkflowResult(value, error)` 標準化回傳
- **Pipelex**：typed `.mthds` → Concept types as data contracts（CandidateProfile、JobRequirements）
- **Orloj task.yaml**：typed input schema + sub-message-level retry
- **AutoAgents**：typed pub/sub + compile-time type safety on events

**共同弧線**：四個系統都不約而同地走向「宣告式 typed contract」而非「imperative raw JSON」。差異只在：
- 實作語言（MCP-agent = Python、Pipelex = TOML + runtime、Orloj = YAML、AutoAgents = Rust）
- 封裝層次（tool/workflow/pipeline/event）

**Hermes 的現狀缺口**：
- WS-019（interface layer）和 WS-020（orchestration layer）還沒分開實作
- 現有的 write queue 是 `write_to_pending()` + `mark_done()` 的 imperative 模式，沒有 typed contracts、沒有 schema、沒有 routing
- 四個外部系統全部在用 typed contracts——Hermes 逆潮流

### 可行動下一步

WS-020 的下一個版本放棄「raw JSON file queue」，改用 Pipelex-style typed pipe：

```toml
# hermes/pipes/session_evolve.mthds
[pipe.evolve_session]
type = "StructuredLLM"
input = { session_id: "String", patterns: "List[ActionPattern]" }
output = { evolution: "ExperiencePair", confidence: "Float" }
prompt = "Given these action patterns, output IF-THEN experience pair..."
```

`write_to_pending()` 改為 `pipe.evolve_session.submit(session_id, patterns)`，queue 變成 type-checked pipe graph。這比檔案 queue 更易推理、更易測試、也更符合外部框架的趨勢。
