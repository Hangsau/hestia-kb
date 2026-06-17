---
_slug: 40-Resources-_mixed-research-2026-05-27-0808-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/2026-05-27-0808-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-27'
confidence: medium
title: Tool Interface 失敗模式與 Governance 的階段化原則
updated: '2026-06-15'
type: research
status: budding
---

# Tool Interface 失敗模式與 Governance 的階段化原則

**消化筆記**: 2026-05-27-arcade-mcp-tool-patterns, 2026-05-26-cuga-runtime-governance

兩篇來自不同 agent profile 的獨立探索，聚焦於 agent 與工具互動失敗的模式與防禦機制設計。

## Cross-Cutting Theme 1: 「工具正常 ≠ Agent 能用」——介面失敗是獨立的失敗維度

**支援筆記**: arcade-mcp-tool-patterns, cuga-runtime-governance

Arcade 明確提出「Working ≠ Agent-usable」：工具可以回傳正確資料但 agent 仍失敗，因為 agent 無法判断何时该调用它、无法处理错误恢复。CUGA 的五層 runtime governance 也是對這個問題的反應——Intent Guard 在 agent reasoning loop 之前截獲惡意請求，Playbook 在 loop 之中塑形 planning，Tool Approval 在 loop 之後、執行之前把關。

兩個系統獨立得出相同結論：agent-tool 互動失敗的 root cause 不在「工具本身壞掉」，而在**介面層**（interface layer）的設計缺失。解決方案都是對「tool works → agent uses it correctly」這個鏈路插入中間層——Arcade 的 Error-Guided Recovery 與 Tool Composition、CUGA 的三階段 pipeline。

**可行動下一步**: 盤點 Talos 的 governance pipeline 工具（comms reader、memory distill、snapshot），檢查哪些只有「工程師視角」描述而沒有「agent-optimized」描述。優先從 comms reader 開始重寫 tool description。

## Cross-Cutting Theme 2: 外部化原則——機制與職責的正確位置

**支援筆記**: arcade-mcp-tool-patterns, cuga-runtime-governance

Arcade 的「Context Injection」pattern：身份、權限、憑證全部透過 server-side context object 傳遞，絕不通過 LLM prompt。「Security Boundaries」：prompt 表達意圖，程式碼強制規則。CUGA 的 Tool Approval 發生在 code generation 之後、實際執行之前，脫離 agent reasoning loop，確保高風險操作有獨立把關。

兩個系統都指向同一個原則：**信任邊界**（trust boundary）必須在 LLM 控制範圍之外。LLM 的職責是表達意圖和選擇工具，不應承擔安全審查或credential 管理的職責。

**可行動下一步**: 審查 ws-028 的 policy_engine plugin 三 profile（block/allow/redact），確認 block 邏輯是否完全在 LLM prompt 之外，還是有任何環節依賴 LLM 判斷而不是程式碼強制。

## Cross-Cutting Theme 3: Policy 動態性——靜態規則不足

**支援筆記**: cuga-runtime-governance, arcade-mcp-tool-patterns

CUGA 的 policy 儲存在 Milvus vector DB，以 keyword/embedding/application/state/tool 動態觸發。Arcade 的 Tool Guide 在 tool description 執行前動態充實，附加 warning/context（如「known-unreliable endpoint」），可疊加（cumulative）而非 mutually exclusive。

兩個系統都發現靜態 policy（純 regex matching、寫死的 tool description）不足以應對多變的 agent 行為。需要動態的、上下文敏感的 policy 注入機制。

**可行動下一步**: 參考 CUGA 的分層觸發機制（keyword → similarity → state），為 Hestia/Talos 雙 agent 的 inter-agent comms 設計動態 policy 注入，用於通訊格式異常的早期偵測。
