---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-18-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-18-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-18'
confidence: high
title: Agent 安全與自主性：跨主題綜合洞察
updated: '2026-06-15'
type: research
status: budding
---

# Agent 安全與自主性：跨主題綜合洞察

**消化筆記**: 2026-05-16-prompt-injection-patterns-agent-graph, 2026-05-16-lethal-trifecta-deep-dive, 2026-05-15-claws-agent-sandboxing, 2026-05-15-mcpc-mcp-cli-proxy, 2026-05-15-agent-architecture-design, 2026-05-16-coding-agents-browser-otel

（把 prompt injection 防禦、lethal trifecta、沙箱隔離、MCP 安全代理與 agent 架構三篇文章交叉比對，找出非顯然的模式。）

---

## Cross-Cutting Theme 1: 信任邊界是首要設計 primitive，不是事後追加

**支援筆記**: prompt-injection-patterns, lethal-trifecta, claws-agent-sandboxing, mcpc-mcp-cli-proxy

（4 篇，交叉驗證信心：**high**）

### 分析

四篇文章表面上在講四件不同的事：

| 筆記 | 核心主題 |
|------|---------|
| prompt-injection-patterns | 六個防禦 pattern（Plan-Then-Execute、Context-Minimization 等） |
| lethal-trifecta | private data + untrusted content + external comm = trifecta 湊齊 = 可外洩 |
| claws-agent-sandboxing | OTP human-in-the-loop、VM isolation、permission spectrum |
| mcpc-mcp-cli-proxy | Token-isolating proxy，agent 永遠碰不到 OAuth token |

合在一起看，這四篇文章全在說**同一件事的不同切面**：把系統的 trust boundary 當成首要設計決策，而不是事後追加的安全層。

**具體的共享結構**：

```
Trust Boundary 模型：
  ┌─────────────────────────────────────────────┐
  │  Agent core                                 │
  │  （處理 trusted logic 的部分）              │
  │        ↑         ↑          ↑              │
  │   [Plan lock] [Token iso] [OTP gate]       │
  │        │         │          │              │
  │   untrusted → trusted 的每一條 edge        │
  │   都必須有 explicit contract                │
  └─────────────────────────────────────────────┘
```

- `prompt-injection-patterns` 的 Plan-Then-Execute 是 **plan edge 的 trust contract**：plan 鎖定後，untrusted content 不得影響 action。
- `lethal-trifecta` 是 **threat model 的 trust boundary**：三條腿同時湊齊時，任何一條腿到下一條腿的 edge 都是危險的。
- `claws-agent-sandboxing` 的 OTP gate 和 VM isolation 是 **permission edge 的 enforcement**：越線前先確認，不只是 rely on LLM 的判斷。
- `mcpc` 的 token-isolating proxy 是 **credential edge 的隔離**：MCP server 的 auth token 不該流進 agent 的 context。

**非顯然的 insight**：Hermes 現有的架構已經在實作這件事，但**不一致**——sanitize_fetch（信任邊界）、worktree isolation（credential/檔案邊界）、Plan-Then-Execute（action 邊界）各自存在，但**沒有一個 unified trust boundary framework** 把它們一致地描述成同一件事的不同實例。這導致 WS-009（hijacking resilience）的 spec 和其他安全 spec 在描述邏輯上不相通。

### 可行動下一步

寫一份 `agent-trust-boundaries.md` 技術規範，把 Hermes 的所有 trust edge 分類：

1. **Untrusted input edges**：`fetch` → agent context、`web_search` → agent context
2. **Credential edges**：`terminal` 可存取 credential、`patch` 可寫入設定檔
3. **Action edges**：`terminal` 可執行 shell、`write_file` 可寫入系統路徑
4. **State edges**：`read_file` 可讀 session state、`session_search` 可讀歷史 context

每個 edge 的 enforcement 現狀（plan lock / sanitizer / worktree / none），缺口在哪（見 lethal-trifecta 的 Trifecta 偵測）。

---

## Cross-Cutting Theme 2: Hermes 的設計決策其實正確——問題是缺乏系統性的表達

**支援筆記**: claws-agent-sandboxing, lethal-trifecta, prompt-injection-patterns, agent-architecture-design

（4 篇，交叉驗證信心：**high**）

### 分析

`claws-agent-sandboxing` 引用 HN comment（`blakec`）說 Hermes 的演化路徑和 accidental claw 一樣——不是設計出來的，是修補出來的。

但把四篇筆記合在一起，實際上可以逆推出：**Hermes 每次「修補」都踩在學術界後來才系統化的模式上**。

| Hermes 的實際選擇 | 對應的論文/框架 |
|------------------|----------------|
| Plan-Then-Execute（explore 鎖定機制） | prompt-injection-patterns Pattern #2 |
| sanitize_fetch.py | lethal-trifecta 的 sanitizer 建議 |
| worktree isolation | claws-agent-sandboxing 的 VM isolation 的輕量版 |
| DeepSeek 免費模型 + 不管 cache | agent-architecture-design 的「不管 Cache」軸（正確的代價取捨） |
| Single-agent single-user memory pipeline | agent-architecture-design 對 Zep portable memory 的批判（Hermes 避開所有陷阱） |

**非顯然的 insight**：Hermes 的架構演化其實比多數正式設計的 agent 系統更一致——因為它的 constraint（免費模型、單一使用者、自主演化）逼它排除錯誤的複雜度。但這個「一致性」沒有被文件化，導致：
- WS-009 spec 不知道自己是 Plan-Then-Execute 的實例
- `heartbeat` 的 autonomic scoring 不知道自己是 agent-architecture-design 裡「務實修正 pure LLM loop」的實例
- Memory pipeline 不知道自己是避開 portable memory 陷阱的有意識設計

沒有文件化 = 無法自述 = 無法評估取捨 = 新功能可能破壞這些隱含的約束。

### 可行動下一步

在 `~/obsidian-vault/research/` 建 `hermes-architecture-rationale.md`，把上述表格寫成「約束 → 決策 → 後果」的格式。這份文件是給未來的自己看的：當有人說「要不要加 portable memory」或「要不要支援 multi-agent」，對照這份清單就知道在挑戰哪個隱含約束。

---

## Cross-Cutting Theme 3: 從「笨工具」到「漸進式防禦」——Hermes 的 tool philosophy 需要升級

**支援筆記**: mcpc-mcp-cli-proxy, agent-architecture-design, coding-agents-browser-otel

（3 篇，交叉驗證信心：**medium**）

### 分析

`mcpc` 文章引用 Doug Turnbull 的「笨工具」哲學：給 agent 一個 `Bash` + mcpc，而不是 50 個 MCP tools。`coding-agents-browser-otel` 的 ABP（Agent Browser Protocol）也在說同一件事——把瀏覽器從「async event chaos」封裝成「one request = one deterministic result」。

但 Hermes 目前的 tool 模型是 **thick interface 為主**（native-mcp 把所有 tools 註冊成 first-class tools）。這在 128 個 skills 的規模下已經開始有代價：

- `agent-architecture-design` 提到的 prompt caching 分析：tool schema 也是 context 的一部分。200 個 tool schema = O(n) context cost。
- `mcpc` 的 Progressive Tool Discovery（`grep` 跨 server 搜尋 tools）正是對這個問題的回應。
- Hermes 的 cost tracking 已經看到 token 用量成長，但沒有對應的 tool reduction 策略。

**非顯然的 insight**：`mcpc` 的三層工具哲學（thin Bash + mcpc CLI / thick native-mcp tools / progressive discovery）給了 Hermes 一個具體的遷移框架。不是把現有 tools 全部改成 CLI，而是**新增一個 thin interface 層**，讓特定場景（大量工具的探索、MCP server 整合）走漸進式發現而非全量註冊。

### 可行動下一步

在 `native-mcp` skill 的 `future_improvements` 段落加入一項：評估哪些 tool groups 適合從 thick 改成 progressive discovery。優先從 `productivity/` 和 `software-development/` 開始——這兩個 domain 的 tool 數量最多但使用頻率最低（可從 heartbeat 的 tool usage log 確認）。