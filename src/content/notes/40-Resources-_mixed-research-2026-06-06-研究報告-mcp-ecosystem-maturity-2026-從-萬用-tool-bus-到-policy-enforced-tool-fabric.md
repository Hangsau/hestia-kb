---
_slug: 40-Resources-_mixed-research-2026-06-06-研究報告-mcp-ecosystem-maturity-2026-從-萬用-tool-bus-到-policy-enforced-tool-fabric
_vault_path: 40-Resources/_mixed/research/2026-06-06-研究報告-mcp-ecosystem-maturity-2026-從-萬用-tool-bus-到-policy-enforced-tool-fabric.md
tags:
- research
- knowledge
- ai-agent
created: '2026-06-06'
version: 1
source_report: 2026-06-06-mcp-ecosystem-maturity-security-gateway.md
source_url: null
type: research
fingerprint: mcp, tool, server, llm, registry, defender, https, description, call,
  injection
title: 研究報告：MCP Ecosystem Maturity 2026 — 從「萬用 tool bus」到「policy-enforced tool fabric」
updated: '2026-06-15'
status: budding
---

# 研究報告：MCP Ecosystem Maturity 2026 — 從「萬用 tool bus」到「policy-enforced tool fabric」

## Version 1 — 2026-06-06

### 核心觀念
**問題**：Model Context Protocol（MCP）在 2024 年底由 Anthropic 提出時的定位是「agent ↔ tool 的 USB-C」—— 一個統一 JSON-RPC 介面讓任意 LLM client 接任意 tool server。2025-2026 年這條曲線指數爆發：`hangwin/mcp-chrome` 11.8k stars、`modelcontextprotocol/registry` 6.9k stars、Awesome MCP Security 收錄 800+ server。Chrome、Playwright、Figma、GitHub、Excel、IDA …

**洞見**：**對 AI agent 領域的影響**： 1. **MCP 從「tool bus」變成「policy-enforced tool fabric」是 2026 年最大範式轉移**。Tool list 不再是「我能接什麼」而是「我**應該**讓 LLM 看到什麼」。每個 host（Claude Desktop、Cursor、Cline、Windsurf）的預設行為是「LLM 看得到 = LLM 能 call」，這是根本錯誤。 2. **Output sanitizer 變成 agent 必備**。Anthropic Claude / OpenAI 都不會幫你過濾 tool result。Defe…

### 架構 / 機制
## 2. Core Mechanism

### 2.1 三層防禦模型（從本次研究綜合得出）

| 層級 | 攔截點 | 代表實作 | 防什麼 |
|------|--------|---------|--------|
| **L1 Tool-list filter** | client 看到 tools 之前 | `mcp-routing-gateway`, `Epydios gateway` | 危險 tool 不給 LLM 看、virtualize 替換 |
| **L2 Call-time policy** | tool 執行前 | `Epydios` (allow/deny + step-up approval), `microsoft/mcp-gateway` (RBAC) | 需要 user 在場同意的 destructive ops |
| **L3 Output sanitizer** | tool 結果回給 LLM 前 | `StackOneHQ/defender` (2-tier: regex + ONNX ML), `mcp-guard` (GA moderation API) | indirect prompt injection |
| **(配套) L0 Registry/Discovery** | 載入 MCP server 時 | `mcp-contextprotocol/registry`, `agentseal scan-mcp` | 防止裝到已知惡意 server |

### 2.2 StackOne Defender 兩層架構（最值得抄的 output sanitizer 設計）

```typescript
// https://github.com/StackOneHQ/defender
import { createPromptDefense } from '@stackone/defender';

const defense = createPromptDefense({ blockHighRisk: true });

// 攔截在 tool 結果回給 LLM 之前
const result = await defense.defendToolResult(toolOutput, 'gmail_get_message');

if (!result.allowed) {
  // Tier 1: 規則 pattern (Unicode tag, Base64, BiDi override, zero-width)
  // Tier 2: ONNX classifier (22MB, ~10ms latency, F1 90.8%)
  console.log(`Blocked: risk=${result.riskLevel}, score=${result.tier2Score}`);
  throw new Error('Tool output blocked by Defender');
}
// 把 sanitized 過的內容丟回 LLM
passToLLM(result.sanitized);
```

**為什麼這個設計重要**：
- **CPU only**、**~10ms latency**、**22MB model** —— 真的能塞進 agent loop，不會拖垮 tool call
- 兩層：規則擋 90% 已知攻擊快又便宜，ML 補 10% 變體
- `blockHighRisk: true` 是 fail-closed 預設，**反向**於大多數 LLM library 的 fail-open

### 2.3 Epydios Policy Gateway（最完整的 policy engine 雛形）

```text
[archestra-ai inspired] MCP Client → Policy Gateway → MCP Server(s)
                                    ↓
                          ┌──────────┴──────────┐
                          │ 1. allow/deny list  │
                          │ 2. step-up approval │  ← 2-min TTL, JSONL audit
                          │ 3. capability-limited approver token │
                          │ 4. append-only evidence log │
                          └─────────────────────┘
```

關鍵 primitive：
- **Step-up approval**：高風險 tool (`fs.write` 預設) 必須 user 透過 CLI `aimxs-cli approve <id>` 才能執行
- **Separation of duties**：approver token 跟 executor token 是不同的 capability，**自己不能 approve 自己的 call**
- **Append-only JSONL audit**：每一次 tool call 的 allow/deny/approve 都有 SHA-256 chain 串接
- **Sandboxing 三層**：built-in POSIX rlimits（CPU/memory/file size/proc count）+ Docker `--network none` + 強制 sandbox cwd

### 2.4 MCP 官方 spec 2025-06-18 的安全補強（權威但保守）

從官方 changelog 抓出來這次 revision 加的東西：
- **Classify MCP servers** —— 開始區分 trusted / untrusted server
- **Resource Links in tool results** —— 讓 server 可以回傳 typed resource link，client 知道是結構化資料不是自由文字（降低 injection 風險）
- **RFC 8707 Resource Indicators** —— 防止 malicious server 拿到 access token 亂用
- **Security best practices page** —— 官方終於寫了「Don't put credentials in tool descriptions」「Validate tool output server-side」「Treat tool output as untrusted」

**這些都是「衛生建議」級別**，不是 protocol-level enforcement。就像 HTTP/1.1 加了 security considerations section，但 HTTPS 是後來 optional 的。

---

### 思考
## 4. Limitations / Honest Assessment

**作者坦承的限制**：
- `StackOneHQ/defender` 22MB ONNX model 對中文、日文等非英文 injection 效果未公開 benchmark；F1 90.8% 是英文 corpus
- `mcp-routing-gateway` 是 pure proxy 哲學，**故意不做 payload inspection**（它自己說的）—— 擋不住 tool result 內的 injection
- `Epydios-MCP-Policy-Gateway` README 自承「**Not production-ready**」「Sample config tokens must be changed」；step-up approval 用 2-min TTL 是 UX 取捨
- MCP 官方 spec 的 security best practices 沒有 protocol-level enforcement —— 是建議不是必做
- Archestra 的 96% cost reduction claim 沒有公開方法論，極可能是 marketing 數字

**我們的獨立批判**：

1. **Defender F1 90.8% 在 adversarial 設定下可能掉到 70% 以下**。任何 ML classifier 面對 adaptive attacker 都會掉 precision/recall，這是經驗法則。實戰應該 fail-closed + 人工 review queue。

2. **「LLM 看到 tools = LLM 執行」這個根本問題沒人解**。所有 L1 filter（routing gateway、policy gateway）都是「別讓 LLM 看到」，但這跟 LLM 本身能 infer 出工具存在的能力衝突。例如「刪除檔案」的 tool 被 filter 掉，但 user 問「能刪檔嗎」LLM 還是會在 description 之外找到其他寫檔路徑（shell.exec、fs.write）。**真正的解法是 capability-based security**：tool 本身要有 unforgeable capability token，LLM 「看到」≠「擁有 capability」。

3. **Confused deputy 沒被徹底解決**。RFC 8707 強制 resource indicator，但實際 OAuth provider 沒幾個正確 implement。Anthropic 自己 demo 的 MCP client 早期有這個 bug，現在 fix 但社群 copy-paste 的 client 大量有同樣問題。

4. **Registry 是新的 supply chain 風險**。`getagentseal/awesome-mcp-security` 對 800+ server 評分結果應該被當作必要前置檢查，但每個 MCP user 跑 agentseal 之前要先決定 trust model。`awesome-mcp-security` 的 score 來源是 9 個 analyzer 的合議，**如果 attacker 同時控 5 個 analyzer 就 false negative**。**這跟 X.509 PKI 早期 CA 信任問題同構** —— 需要 Web of Trust 或 transparency log。

5. **多層防禦的代價是延遲堆疊**。Defender 10ms + Policy gateway 5ms + Registry scan 200ms + Audit log 5ms = ~220ms per tool call。agent 跑 20 個 tool call 浪費 4.4 秒。對 human-in-loop task 沒差，對 fast reflex agent 是痛點。

6. **本次研究找不到一篇 2026 年 arXiv 學術論文**專門針對 MCP 攻擊面（arXiv API 在 2026-06-06 持續回空，這是已知 pitfall）。所有洞見都來自工程實作而非正式 paper。學術圈落後實作 6-12 個月。

---

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### 5.1 firn（首要目標 — firn 已經有 `mcp/registry.py` 跟 `mcp/server_wrapper.py` 但**完全沒有防禦層**）

**P0：L3 Output sanitizer（MODERATE, 1-2 天）**
- 新增 `src/firn/mcp/sanitizer.py`
- 第一階段：抄 `StackOneHQ/defender` Tier 1 的 regex pattern（Unicode tag、Base64、BiDi override、zero-width chars）—— 純 Python 寫，零 ML 依賴
- 對應檔案：`src/firn/mcp/server_wrapper.py` 的 `call_tool()` 回傳後立即過 `sanitizer.sanitize()`
- **免費方案**：regex 即可覆蓋 60-70% 已知 injection patterns，無需付費 API
- **測試**：用 `getagentseal/agentseal` 的 225+ 攻擊 corpus 跑 regression

**P1：L1 Tool-list filter（TRIVIAL, 半天）**
- 在 `src/firn/mcp/registry.py` 的 `as_tool_schemas()` 加 `allowlist` 參數
- 預設 deny dangerous patterns：`fs.write`、`fs.delete`、`exec`、`shell`、`send_*`、`delete_*`
- 對應 `src/firn/config.py` 的 `MCPServerConfig` 加 `tool_allowlist: list[str] | None = None`
- **零成本**：純 config 過濾

**P1：Step-up approval 雛形（MODERATE, 1 天）**
- 抄 Epydios 模式：destructive tool 預設需要 confirmation
- 實作：`src/firn/mcp/policy.py`，hook 在 `server_wrapper.call_tool()` 前
- 短期：寫 approval 進 SQLite + 印 CLI 提示；長期：接 TelegramGateway
- **免費方案**：本地 SQLite + CLI 即可，無需付費

**P2：JSONL audit log（TRIVIAL, 2 小時）**
- 在 `observability/spans.py` 加 `MCP_CALL_SPAN`，記錄 (server, tool, args_hash, result_hash, decision, timestamp)
- 對應 `observability/turns_logger.py` 已經有的 turns log infrastructure
- **零成本**：append-only JSONL 即可

### 5.2 managed-agents（本系統）

**P3：研究者本身不需要 MCP 改動**。但研究的 cron job 可以加一個 sentinel：
- 每次研究報告送出前，掃 `reports/` 內的 URL 列表，跑一次 `agentseal scan-mcp` 等價的 pattern 檢查
- 防止「推薦了一個被植入 malicious description 的 MCP server」
- **難度**：MODERATE，**理由**：需要 LLM 用 query 對 source URL 反查 registry 評分，過度工程；可改用人工 review

### 5.3 Hermes Agent

**P3：MCP gateway 整合是可選未來方向**。當前 Hermes 用 native tool 不走 MCP，不需要急著改。
- 若未來開 MCP 給 user 加 tool，`archestra-ai/archestra` 的 docker-compose 模式是最快 reference
- **難度**：RESEARCH-ONLY（先看 firn 的 5.1 結果再決定）

### 5.4 不需要做的事

- ❌ **不要自己寫 ML classifier**。Defender 的 22MB ONNX 是 SOTA trade-off，自己從零訓練超不划算
- ❌ **不要把 tool description 過 LLM 再過濾**（meta-prompt 攻擊面）。規則 regex + ML classifier 才是對的層級
- ❌ **不要做自己的 MCP registry**。官方 registry v0.1 已 freeze，等 v1 GA

---


### 來源

- 原始報告：2026-06-06-mcp-ecosystem-maturity-security-gateway.md
- 類型：
- 連結：
