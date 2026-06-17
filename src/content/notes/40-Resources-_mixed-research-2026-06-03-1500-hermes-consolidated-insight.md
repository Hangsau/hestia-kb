---
_slug: 40-Resources-_mixed-research-2026-06-03-1500-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-06-03-1500-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-06-03'
confidence: medium
title: Context Dumps Are the Wrong Abstraction — All Four Notes Converge on Structured
  Pipelines
updated: '2026-06-15'
type: research
status: budding
---

# Context Dumps Are the Wrong Abstraction — All Four Notes Converge on Structured Pipelines

**消化筆記**: 2026-06-02-rlm-paper-reinforcement-codeRLM, 2026-06-03-forge-gambit-agent-harness, 2026-06-03-llamagym-online-rl-fine-tune, 2026-06-03-shapedql-multi-stage-ranking

四篇筆記出自不同領域（RLM 理論、agent 可靠性、R L 微調、檢索引擎），但都独立地收斂到同一個否定命題：**把資料丢進 context 是錯誤的抽象**。每篇筆記提出的解法剛好構成一個互補的 pipeline 階段。

---

## Cross-Cutting Theme 1: Context Dump 否定 — 四種語言說同一件事

**支援筆記**: RLM paper (Symbolic handle + programmatic recursion), Forge (ResponseValidator + rescue parsing dual-layer), LlamaGym (Agent abstract class), ShapedQL (Retrieve → Filter → Score → Reorder pipeline)

| 筆記 | 對 context dump 的批評 | 替代方案 |
|---|---|---|
| RLM paper | 把 prompt 放進 LLM context → 受限於 context window；sub-call 是語言化的无法循环 | 變數 + REPL + 代碼檢查，metadata 常數大小 |
| Forge | 小模型無法在 text vs tool 之間 stable 選擇 | Synthetic respond tool + ResponseValidator 双层守护 |
| LlamaGym | supervised fine-tuning 不提供オンライン信號 | Agent abstract class：observation → action → reward → termination 分離 |
| ShapedQL | retrieval 不是 retrieval（只是拿到 1000 個），真正需要的是 ranking pipeline | 4-stage：Retrieve / Filter / Score / Reorder |

根本模式：**把整個輸入当作要处理的对象（context）→ 改为把输入当作要被 pipeline 流经的结构化对象**。各階段職責分明，每一 stage 只做一件事。

**可行動下一步**: 在 `heartbeat_learning.py` 的 distillate  accumulation 逻辑中，提取出 `HeartbeatDistillatePipeline` 类：
1. **Retrieve** — 语义召回相關 distillates（BM25 + embedding hybrid）
2. **Filter** — 檢查 `confidence_valid_until`，移除矛盾或過期節點
3. **Score** — 根據矛盾次數、時間衰減、使用頻率給每個 distillate 打分
4. **Reorder** — 只取 top-K 進 context，不再做 full dump

不要一次性實作四個階段——先只做 **Filter stage**：新增邏輯，當 new distillate 與 existing distillate 存在 `contradiction_edge`（用 embedding 相似度 < threshold 檢測）時，將舊節點標記為 invalidated 而非單純衰減。

---

## Cross-Cutting Theme 2: Reliable Tool Use 需要雙層機制（守衞 + 測量）

**支援筆記**: Forge (ResponseValidator + synthetic respond tool 雙層), Gambit (eval harness + trace regression), CodeRLM drift detection (符號級變化追蹤)

Forge 和 Gambit 看似無關——Forge 是 L1 guardrails（强制正確的 tool call），Gambit 是 L2 eval harness（測量並回歸測試行為）。但它們共同構成**可信賴 agent 行為的兩層架構**：

- **L1（enforcement）**: Forge 的 ResponseValidator + Rescue parsing — 每個 tool call 發出前檢查格式，輸出前 strip synthetic tool，模型看不見 guardrail 存在
- **L2（measurement）**: Gambit 的 trace grading + scenario regression — 運行真實 scenario，捕捉行為drop，回歸 suite 保存失敗案例
- **L2.5（drift detection）**: CodeRLM Studio 的 `3h Drift: verify_token() now takes device_id` — 持續監控規格與實作之間的飄移

Hermes 的現有設計：`sanitize_fetch.py` 是 L1 的部分（input sanitization），但 `WS-035` 的 observability 追蹤目標沒有實質的 eval harness。Heartbeat 有監控但沒有 drift regression。

**可行動下一步**: 在 `/srv/hearth/` 或 `observations/` 建立 **agent behavior regression suite**：
1. 定義 5-8 個 golden scenario（各含 input + expected behavior fingerprint）
2. 每次 heartbeat 运行時，随機抽樣 1-2 個 scenario 驗證行為稳定性
3. 記錄結果到 `~/.hermes/workspace/behavior_regression.jsonl`
4. 不要急於构建完整的 Gambit-like framework——先用 bash + jq 脚本实现 scenario runner，確保数据格式兼容，未來可升级到 Gambit

---

## 附：明確的單一筆記連結（跳過）

以下連結是**顯然的**（同一系統内部引用），不構成 cross-cutting：
- RLM paper → heartbeat_learning drift penalty（直接應用）
- Forge + Gambit → Talos governance（直接應用）
- LlamaGym → heartbeat_learning concept（直接應用）
- ShapedQL → Synix 8-systems research（已在同一篇筆記内部引用）
