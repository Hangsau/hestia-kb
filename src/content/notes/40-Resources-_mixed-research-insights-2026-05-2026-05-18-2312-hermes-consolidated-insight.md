---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-18-2312-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-18-2312-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-18'
confidence: high
title: 代價、安全、上下文：三篇文章指向同一個架構方向
updated: '2026-06-15'
type: research
status: budding
---

# 代價、安全、上下文：三篇文章指向同一個架構方向

**消化筆記**: 2026-05-14-agent-cost-curve, 2026-05-14-agent-defense-landscape, 2026-05-14-agent-economics, 2026-05-15-agent-cost-security-convergence, 2026-05-17-12-factor-agents-endless-toil-reliability, 2026-05-18-zerostack-semble, 2026-05-18-moltis-dcg-session-memory-deep-dive, 2026-05-17-mcp-gateway-deployment-spectrum

（來自七個不同角度（成本分析、安全架構、系統程式、12-factor reliability、MCP gateway、Rust agent、shell guard）的筆記，全部收斂到同一個結論：架構越薄、context 越短、agent 能力越受限，整個系統越好。）

## Cross-Cutting Theme 1: 代價曲線 × 安全防御 = 同一套架構Pressure

**支援筆記**: 2026-05-14-agent-cost-curve, 2026-05-14-agent-defense-landscape, 2026-05-14-agent-economics, 2026-05-15-agent-cost-security-convergence, 2026-05-17-12-factor-agents-endless-toil-reliability

（5 篇，High confidence）

### 分析

三條完全獨立的資訊流同時指向「薄 interface = 好架構」：

**成本端**（Expensively Quadratic）：
- Cache read 在 ~27,500 tokens 佔 50% 成本，到對話結束佔 87%
- 解法：subagent delegation 把 iteration 移出 main context、短 context window、頻繁重開 conversation

**安全端**（FireClaw / AgentArmor / Lilith-zero）：
- 三大安全工具全在補同一個洞：LLM 強制混合 trusted instructions 和 untrusted data
- 解法：Constrained tool interface、feedback loop 中斷、sub-agent 隔離 untrusted content
- Simon Willison 的六種安全模式全都trade agent capability換 security

**Reliability端**（12-factor agents）：
- Factor 8: 在 tool selection ↔ invocation 之間插入 interrupt point
- Factor 9: 把 error 塞回 context window 讓 LLM 自己修
- Factor 10: 每個 agent 只做 10-20 steps

**非顯然之處**：這三個問題（帳單太貴、安全被破、系統可靠性差）看起來是完全不同的 concerns，但它們的共同解法是同一個——**把 agent 的能力邊界收窄、把 context window 維持在 40-60%、把危險操作移出 LLM loop**。任何一個壓力改善，另外兩個也跟著改善。這是 triple win。

### 可行動下一步

在 `heartbeat_v2.py` 加一個 `_check_context_efficiency()` sensor：
- 追蹤每個 session 的 token/cost 曲線（用現有的 stats log）
- 不改行為，只加 visibility
- 目標：先有數據，確認 Hermes 的代價曲線形狀，再決定是否需要干預（目前 DeepSeek 免費，曲線形狀比帳單數字更重要）

---

## Cross-Cutting Theme 2: Hermes 已經有對的零件，缺的是膠水

**支援筆記**: 2026-05-14-beads-agent-memory, 2026-05-14-compaction-context-rot-handbook, 2026-05-17-12-factor-agents-endless-toil-reliability, 2026-05-18-moltis-dcg-session-memory-deep-dive, 2026-05-18-zerostack-semble

（5 篇，High confidence）

### 分析

Hermes 的組件庫已經覆蓋了業界共識的記憶系統三層：

| 層次 | 業界共識 | Hermes 現況 |
|------|---------|------------|
| File-based search | ✅ Beads, Semble | ✅ search_files (rg backend) |
| Episodic extraction | ✅ Handbook 最創新 | ✅ Memory pipeline (compaction 前萃取) |
| Cross-session consolidation | ❌ 大家都缺 | ❌ 正在補（本文） |
| Observational facts | ✅ Mastra (4-10x 節省) | ❌ 沒有 |
| LLM-free quality check | ✅ Endless Toil | ❌ 沒有 |

**非顯然之處**：Hermes 的 episodic memory 被 Handbook 認證為「2026 年最創新的 pattern」，但 Observational memory（L3）和 code quality scanner（L4）是直接可移植的低 hanging fruit，不需要新基礎設施：

- **L3 Observational facts**: 每次 compaction/session 結束時，從對話萃取 3-5 條離散事實（每條 ~20 token）。不需要 LLM API 串接，直接用 prompt template。

- **L4 Endless Toil scanner**: 10 個 regex pattern + 3 個結構化信號，純 static analysis，零 token 成本。可直接加到 EVOLVE 的 `_check_code_quality()` sensor。

**另一條線**：Moltis 的 pre-compaction flush（compaction 前隱藏 LLM turn 寫入 memory）vs Hermes 的 post-compaction consolidation（cron job 事後消化）。兩者可互補——Moltis 管 session 內的及時寫入，Hermes 管跨 session 的結構化消化。

### 可行動下一步

1. **立即**：把 Endless Toil 的 10 個 regex patterns（`console.log`、`TODO/FIXME`、ignored lint、explicit any、dynamic execution、shell execution、broad exception、empty catch、secret-shaped literal、force unwrap）寫進 `heartbeat/evolve.py` 的新 `_check_code_quality()` 方法。不需要 LLM，不需要 pip install。

2. **本週**：在 `consolidate_memory.py` 加 Observational fact extraction：在 compact 之前，用 prompt template 從 session 萃取 3-5 條「用戶偏好 / API 行為 / 系統狀態」的離散事實，寫入 `~/.hermes/observations/`。格式：
   ```
   ## 2026-05-18
   - "User prefers YAML over JSON for config"
   - "hermes-gateway run uses port 8080"
   ```
   這比 summary 更省 token，且事實顆粒可被 LLM 直接使用。

3. **下週**：在 `dcg test --robot <cmd>` 對高風險 shell commands 跑一遍（`rm -rf`、database commands、docker commands），確認 DCG 的 Robot Mode JSON 格式可用於 Talos audit trail。這是 Talos governance 從 blueprint 到實際整合的最短路徑。
