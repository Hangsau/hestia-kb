---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-19-1002-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-19-1002-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-19'
confidence: medium
title: MCP Gateway × Agent Orchestrator × Agent-as-Server：收斂成一層
updated: '2026-06-15'
type: research
status: budding
---

# MCP Gateway × Agent Orchestrator × Agent-as-Server：收斂成一層

**消化筆記**: 2026-05-13-mcp-gateway-architecture, 2026-05-13-mcp-gateway-orchestrator-convergence, 2026-05-13-agent-orchestrator-patterns, 2026-05-20-mcp-agent-agent-as-mcp-server-deep-dive, 2026-05-13-adk-evaluation-gap

（摘要）三個月內 MCP gateway 生態經歷了從「credential proxy」到「orchestrator」的快速演化，加上 mcp-agent 的 agent-as-MCP-server pattern，Hermes 原本分散的三層——gateway、MCP client、orchestrator——正在收斂成同一層 infrastructure，且 eval 缺口是這個收斂過程中被遺漏的品質支柱。

---

## Cross-Cutting Theme 1：Gateway 與 Orchestrator 的功能邊界已消融

**支援筆記**: mcp-gateway-architecture, mcp-gateway-orchestrator-convergence, agent-orchestrator-patterns, mcp-agent-agent-as-mcp-server-deep-dive

（分析）

表面上四篇筆記在討論不同項目（IBM ContextForge、Archestra、Composio agent-orchestrator、mcp-agent SDK），但放在一起看會發現一個清晰的收斂方向：

1. **ContextForge** 把 REST/gRPC/A2A 全部轉成 MCP 對外——這是 protocol federation
2. **Archestra** 在 gateway 之上疊加了 K8s pod per agent、OAuth lifecycle、cost tracking——這是 agent lifecycle management
3. **agent-orchestrator** 本身就有 gateway 內建（plugin slot 架構）——orchestrator 吸收了 gateway
4. **mcp-agent 的 agent-as-MCP-server** 更激進：直接用 `create_mcp_server_for_app()` 把整個 agent 變成標準 MCP server——連「gateway 是什麼」都被重新定義了

這四個點湊在一起，隱含的結論是：**Gateway、Orchestrator、Agent Runtime 的邊界正在消失**，最終會長成一層東西。這跟 Scion orchestration skeptic 那篇的「less is more」呼應——複雜度不是被消滅，是被吸收到 infrastructure 層，讓上層應用變簡單。

對 Hermes 的直接影響：`hermes gateway run`、`native-mcp` skill、`delegate_task`、`kanban-orchestrator` 這四個元件目前是分開的，但它們遲早會面臨「整合成同一層」的壓力。不是因為架構愛好，是因為這個生態的 momentum 會把門關上——如果 ContextForge 或 Archestra 足夠成熟，繼續自己維護 gateway 就變成重造輪子。

**可行動下一步**: 下次探索 ContextForge Python SDK 的實際整合成本——如果 `pip install mcp-context-forge` + 兩行 config 就能讓 Hermes 的所有 MCP servers 統一走 gateway，替換成本是多少？

---

## Cross-Cutting Theme 2：Eval 是 Hermes 架構圖裡最大的黑洞

**支援筆記**: adk-evaluation-gap, agent-orchestrator-patterns, mcp-gateway-orchestrator-convergence

（分析）

三篇筆記都間接或直接點到了同一個問題：**沒有人在測量 agent 的行為品質**。

- ADK 那篇明確指出：Hermes heartbeat 監控系統健康（disk、mem、stuck），但不監控 agent 正確性。heartbeat_v2 scoring 改了公式，REST 決策是否還是對的，沒人知道。
- agent-orchestrator 那篇提到 3,288 個 test cases 但 README 沒說清楚測的是什麼——可能是 UI render + terminal output，不一定是 agent 行為對錯。
- mcp-gateway-orchestrator-convergence 全部在討論 security/cost/observability，但 observability 在這裡指的是 tool call 的可追蹤性，不是 agent decision quality。

把三篇放一起，浮現的是：**整個 MCP 生態都在加強工具層的可靠性，但 agent decision layer 幾乎是黑箱**。ContextForge 有 audit trail，但 audit trail 記的是「agent call 了哪個 tool」，不是「agent 應該 call 哪個 tool 才是對的」。

這個缺口跟 memory system 那篇（post-vector-agent-memory-pt3）也暗暗呼應：Beads 的 compaction 解決的是 context rot，但 consolidation 解決的是「context 裡有 pattern 但 agent 看不見」。兩者都是在 agent 輸出之後補救，而不是在 agent 決策當下介入。

**可行動下一步**: 寫一個最陽春的 eval set——只測 `heartbeat_v2.py` 的 scoring 邏輯。定義 5-8 個 (disk, mem, stuck, pending) → expected_action 配對，用 pytest 跑。這是 pure Python deterministic test，不需要動 LLM，30 分鐘內可以完成。

---

## 觀望但不足夠構成 Theme 的觀察

- **mcp-agent agent-as-server** 是 Hermes 可以直接試的方向——`create_mcp_server_for_app(app)` 把 Hermes 變成可被 Claude Desktop 呼叫的 MCP server。代價是需要驗證 mcp-agent SDK 是否能 import 进 Hermes 的 Python 環境。
- **connect-warmup** 是 user re-engagement 的實際案例，但跟其他 9 篇筆記沒有 cross-cutting 連結，純粹是 heartbeat 決策的執行報告。已標記為已消化，下次不再進入 consolidation pool。