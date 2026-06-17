---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-15-1200-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-15-1200-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-15'
confidence: high
title: Thin Interface、Isolation Spectrum、Feedback Trap：三條跨主題收斂線
updated: '2026-06-15'
type: research
status: budding
---

# Thin Interface、Isolation Spectrum、Feedback Trap：三條跨主題收斂線

**消化筆記**: 2026-05-15-claws-agent-sandboxing, 2026-05-15-mcpc-mcp-cli-proxy, 2026-05-15-agent-architecture-design, 2026-05-15-mysti-multi-agent-debate, 2026-05-15-agent-cost-security-convergence, 2026-05-15-agent-tool-simplicity

六篇筆記表面分散——從 VM 隔離到 MCP CLI、從多 agent 辯論到 prompt cache 數學——但三條收斂線貫穿全部：工具介面該多薄、隔離成本決定安全架構、feedback loop 同時是成本炸彈和 injection 漏洞的根源。

---

## Cross-Cutting Theme 1: 「Thin Interface × Thick Implementation」的跨領域收斂

**支援筆記**: mcpc-mcp-cli-proxy, mysti-multi-agent-debate, agent-tool-simplicity
**信心**: high（3 篇獨立筆記，不同 domain，同一結論）

三個完全不同的領域各自抵達了同一個架構結論：**給 agent 最薄、最可預測的介面，把複雜度壓到 agent 看不到的那一層。**

| 領域 | Thin Interface | Thick Implementation |
|------|---------------|---------------------|
| MCP 工具整合（mcpc） | agent 只用一個 `Bash()` tool + `mcpc` 指令 | mcpc 內部管理 sessions、OAuth proxy、tool discovery |
| 多 agent 協作（Mysti 討論） | Tmux 切窗 / `claude -p` 管線 / MCP call | 協作邏輯在 CLI 組合層，不在平台裡 |
| 搜尋（Doug Turnbull） | 純 BM25，無同義詞、無意圖偵測 | agent 自己疊 query refinement layer + knowledge graph recall |

這不是巧合。三條線匯聚的背後是同一個力：**LLM agent 的 cognitive bandwidth 有限。** 每多一個 tool schema、多一個參數、多一個需要建立 mental model 的 API behavior，agent 的 reasoning 品質就衰減一點（mhher 的 context pollution 論點提供理論基礎——見 claws-agent-sandboxing 筆記）。Thin interface 不只是「簡單比較好」，而是 agent 架構的必要條件。

Hermes 目前違反了這個原則。我們的 skill 系統有 128 個 skill，每個都有參數和模式，`native-mcp` 更是在 startup 時把所有 MCP tools 註冊進 registry。從 agent 視角看，tool surface 是亂槍打鳥的。

**可行動下一步**：
1. 做一次 tool surface audit：用 `search_files` 統計 heartbeat loop 實際呼叫過哪些 skills/MCP tools（過去 30 天），標出從未被呼叫的工具
2. 挑一個「厚 skill」（例如 `native-mcp` 或某個 multi-mode skill），做 thin wrapper 實驗：agent 只看到一個 Bash 指令，thin wrapper 內部 routing 到實際邏輯
3. 用 mcpc（`npm i -g @apify/mcpc`）取代一個 MCP server 的 native integration，對比 agent 在該 server 上的 task 成功率。不需要全面切換——一個 A/B 就夠驗證方向

---

## Cross-Cutting Theme 2: 隔離機制的選擇本質上是成本決策，不是安全決策

**支援筆記**: claws-agent-sandboxing, mcpc-mcp-cli-proxy, agent-cost-security-convergence
**信心**: high（3 篇筆記各自貢獻隔離光譜的一個刻度）

三篇筆記各自描述了一種隔離方案，拼在一起形成一條完整的**隔離成本光譜**：

```
每 call 成本（overhead）→

  ~0          人類反應時間      網路延遲       2ms          秒級
  │               │              │            │            │
Canary token   OTP gate      mcpc proxy    bVisor    libvirt VM
(檔案 watch)   (人機迴圈)    (token隔離)   (seccomp)  (full sandbox)
  │               │              │            │            │
最低防禦      中等防禦        credential    process     完整隔離
(偵測而已)    (阻斷高風險)    保護         隔離         可rollback
```

這條光譜的核心洞察：**傳統安全思維是「選最安全的方案」，但 agent 安全的正確思維是「選你能負擔的隔離成本，然後在該成本下最大化防禦」。** bVisor 之所以重要不是因為它比 VM 安全（它不是），而是因為 2ms 的 overhead 意味著你可以**每個 tool call 都 sandbox**——這完全改變了安全架構的設計空間。從「哪些 task 值得 sandbox」變成「哪些 task 可以不 sandbox」。

Hermes 目前只有一個隔離層：git worktree（WS-002），擋不住 `rm -rf /`。WS-009（hijacking resilience）還在 proposal 階段。這條光譜提供了**漸進式部署路徑**——不需要一次到位，但需要知道每一層的切入點。

**可行動下一步**：
1. **第一層（本週可做）**：在 heartbeat loop 加一個 canary token——在檔案系統放一個 bait 檔（例如 `~/.hermes/DO_NOT_DELETE_THIS`），每次 tool execution 後檢查它還在不在。如果消失了，立刻 terminate session + 發 Telegram alert。成本幾乎為零。
2. **第二層（需 30 分鐘實作）**：試跑 mcpc proxy 模式——`mcpc login <MCP-server>` → `mcpc connect <MCP-server> @relay --proxy 8080` → agent 只連 proxy。驗證 agent 能否在看不到原始 token 的情況下正常使用 MCP tools。成本是一個 localhost proxy process。
3. **第三層（需研究，不急）**：等 bVisor 出 Python SDK 或找到 Zig FFI 方案後，評估 per-call seccomp sandbox 在 Hermes 環境（Linux VM）上的可行性。目前不用做，但要持續追蹤。

---

## Cross-Cutting Theme 3: Feedback Loop = 成本放大器 ∩ Injection 漏洞

**支援筆記**: agent-architecture-design, agent-cost-security-convergence
**信心**: medium（2 篇直接支援，claws-agent-sandboxing 的 context pollution 論點間接呼應）

agent 最核心的機制——iterative tool-calling + context accumulation——同時是兩個看似無關的問題的根源：

```
Agent loop 結構：
  LLM → tool call → tool output → append to context → LLM 再推理 → ...
           ↑                              ↑
           │                              │
    成本爆炸點：                   安全漏洞點：
    每一輪重讀前面                   injection payload 藏在
    所有 cached prefix             tool output 裡進入 context
    (quadratic cache read)         (Willison 論文的核心威脅模型)
```

Philip Zeyliger 的 quadratic cost curve（agent-cost-security-convergence）和 Willison 六種 injection 防禦模式（同一篇筆記）在架構層級是同一件事：**縮短 feedback loop、限制 context 累積、把 iteration 外移到 subagent——這些動作同時降低 cache read 成本和 injection 攻擊面。**

最具體的例子是 Willison 的 Action-Selector 模式：agent 可以觸發 tool，但**看不到 tool output**。從安全角度看，這切斷了 injection 路徑。從成本角度看，這消滅了 quadratic cache read 的根源——agent 不需要重讀前面的 tool output，因為根本沒 output 可以讀。

對 Hermes 的實際意義：目前我們用 DeepSeek（免費），quadratic cost 不痛。但架構上，heartbeat loop（snapshot → scoring → select → execute → log）如果不控制 context 膨脹，將來換付費模型時會直接撞牆。而且 injection 威脅不會因為用免費模型就消失——攻擊者不關心你的帳單是誰付的。

**可行動下一步**：
1. **Context 長度追蹤（5 分鐘）**：在 heartbeat loop log 加一欄 `context_tokens_est`（用 `len(context) / 4` 粗估），跑一週看實際膨脹速度。數據先有，決策後下。
2. **強制 fresh session（低風險實驗）**：設一個 threshold（例如 20K tokens），超過就 auto-spawn subagent 處理剩餘工作而不是繼續 append。這同時測試「subagent 外移是否降低 task 品質」——如果品質不降，cost-security 雙贏。
3. **WS-009 優先實作 Action-Selector（高 leverage）**：挑 Hermes 最高風險的 2-3 個 tools（例如直接操作檔案系統的、可以 curl 外部 URL 的），實作「agent 可觸發但看不到 raw output」模式。tool output 先經過 sanitizer（例如只回傳 exit code + 前 200 chars），再餵回 agent。這同時降低 injection 面和 context 膨脹。

---

## 補註：為什麼三條線都指向同一個方向

三個 theme 不是各自獨立的發現——它們是同一張圖的三個視角：

1. **Thin interface** 讓 agent 的 context 更短（→ 降低成本 + 減少 injection 面）
2. **Isolation-as-cost-spectrum** 讓安全機制可以被部署在正確的粒度（→ 不只在「高風險 task」才防禦）
3. **Feedback loop as root cause** 識別出 agent 架構中最需要被約束的機制（→ 短 feedback loop = 低成本 + 高安全）

Hermes 不需要一次處理全部。但這三條線形成一個 coherent 的架構方向：**往「更短的 feedback loop、更薄的 tool interface、更細粒度的隔離」移動。** 每一個單獨的改動（canary token、mcpc proxy、context threshold）都在這個方向上推進一步。
