---
_slug: 40-Resources-_mixed-explorations-2026-05-16-Open-Edison-Trifecta-Firewall---Snyk-Agent-Scan---架構深讀
_vault_path: 40-Resources/_mixed/explorations/2026-05-16-Open-Edison-Trifecta-Firewall---Snyk-Agent-Scan---架構深讀.md
title: Open Edison Trifecta Firewall + Snyk Agent Scan — 架構深讀
date: 2026-05-16
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- edison
- file
- private
- skill
- skills
- snyk
- tool
- trifecta
- write
created: '2026-05-16'
updated: '2026-06-15'
status: budding
---

# Open Edison Trifecta Firewall + Snyk Agent Scan — 架構深讀

**延續自**: [[2026-05-16-lethal-trifecta-deep-dive]] 的未追蹤 leads

**日期**: 2026-05-16 | **來源**: Open Edison GitHub (51pts HN) + Snyk Agent Scan / Invariant Labs (3pts HN)

## Per-Source Insight

### 1. Open Edison — Trifecta Firewall 的實作解剖

**一句話**：Open Edison 是一個 MCP gateway，在 client 和 MCP server 之間攔截每個 tool call，用三個 permission file + session-level ACL tracking 實作 lethal trifecta 防禦。

**核心架構**：

```
Agent Client → Open Edison Gateway → MCP Servers
                    ↓
          tool_permissions.json
          resource_permissions.json
          prompt_permissions.json
```

**三層 Permission 系統**：

每層 permission file 對每個 item 標記四個 flag：
- `write_operation`: 是否寫出
- `read_private_data`: 是否讀本地私密資料
- `read_untrusted_public_data`: 是否讀外部不可信內容
- `acl`: PUBLIC | PRIVATE | SECRET

範例（`tool_permissions.json`）：
```json
"filesystem": {
  "read_file": {
    "enabled": true,
    "write_operation": false,
    "read_private_data": true,       // ← trifecta leg 1
    "read_untrusted_public_data": false,
    "acl": "PRIVATE"
  },
  "write_file": {
    "enabled": true,
    "write_operation": true,         // ← trifecta leg 3: external comm
    "read_private_data": true,       // ← trifecta leg 1: private data
    "read_untrusted_public_data": false,
    "acl": "PRIVATE"
  }
}
```

**Session-Level ACL Tracking（關鍵機制）**：
- 每個 session 追蹤最高 ACL level（PUBLIC < PRIVATE < SECRET）
- 若 tool 嘗試 write 到低於 session 最高 ACL 的層級 → 阻擋（write-down prevention）
- 這是 Bell-LaPadula 的 "no write down" 原則應用在 agent 場景

**Lethal Trifecta Detection**：
- Session 累積三條腿（private data + untrusted content + external comm）→ 封鎖進一步危險操作
- 不阻止已發生的，但阻止後續 escalation

**Wildcard 支援**：`filesystem/*`、`file:*`、`template:*` 做 bulk config

**Integration**：`@edison.track()` decorator，一行接入 LangGraph/LangChain/plain Python

**Default-Deny**：未知的 tool/resource/prompt 一律拒絕

### 2. Snyk Agent Scan（原 Invariant Labs mcp-scan）— Skills 安全掃描

**一句話**：Invariant Labs 被 Snyk 收購，mcp-scan 改名 snyk-agent-scan。v0.4 新增 skills scanning，偵測 15+ 種安全風險。

**關鍵事實**：
- **Snyk 收購了 Invariant Labs** — 這解釋了為什麼原始 "Invariant Labs GitHub MCP attack report" 難以找到獨立連結：它被合併到 Snyk 產品線
- **Skills scanning 是新的**（v0.4）：偵測 skill file 裡的 prompt injection (E004)、malware payloads (E006)、untrusted content (W011)、credential handling (W007)、hardcoded secrets (W008)
- **Auto-discovery**：自動掃描 Claude Code、Cursor、Windsurf、Gemini CLI、VS Code 等 agent 的 MCP config 和 skills 目錄
- **技術報告**：`skills-report.pdf` 在 repo 內（`.github/reports/skills-report.pdf`），主題是 "Emerging Threats of the Agent Skill Ecosystem"
- **Closed development**：不接受外部 contribution，Snyk 產品

**掃描機制**：
- MCP scanning：實際啟動 MCP server 來擷取 tool description（有安全風險，需 sandbox）
- Skills scanning：靜態分析 SKILL.md 內容
- 結果送到 Snyk Evo 平台做 centralized monitoring

**對 Hermes 的啟發**：
- 我們的 `validate_note.py` 是 note-level 的 injection 殘留掃描（5 patterns），但 Snyk 的 skills scanning 是 proactive 的（掃 skill file 本身而非產出）
- Hermes 有 128 個 skill，部分來自自動生成（system-map、cron job output 等）— 這些是 supply chain attack surface
- Snyk 偵測的 malware payloads in natural language（E006）是我們目前沒 cover 的攻擊面

## Hermes 啟發

### 1. Trifecta Tagging：可以加到現有 tool matrix

我們在 [[2026-05-16-lethal-trifecta-deep-dive]] 已經盤點了 Hermes 的 tool × trifecta 矩陣。Open Edison 的實作告訴我們**具體的 tagging schema**：

```
每個 tool call 標記：
- trifecta_legs: Set<PRIVATE_DATA | UNTRUSTED_CONTENT | EXTERNAL_COMM>
- acl: PUBLIC | PRIVATE | SECRET
```

Session 累積 tracking：
- `session_max_acl`: 隨 tool call 升級（PUBLIC → PRIVATE → SECRET）
- `session_trifecta_legs`: 累積所有被用過的 legs
- Write-down gate: 若 tool 是 write + 目標 ACL < session_max_acl → warn/block
- Trifecta gate: 若三條腿全亮 → warn

**成本**：這不需要改 tool execution layer，只需要在 prompt 層注入 warning（類似我們已有的 plan-then-execute lock）。成本極低。

### 2. Write-Down Prevention 是之前沒注意到的關鍵機制

我們之前的分析聚焦在「trifecta 湊齊 → 封鎖」，但 Open Edison 的 write-down prevention 是一個**更細緻的防禦層**：

- 即使 trifecta 還沒湊齊，若 session 碰過 PRIVATE 資料（如 `read_file ~/.hermes/config.yaml`）然後嘗試 write 到 PUBLIC 輸出（如 `write_file /tmp/public_output.md`），這本身就是 risky flow
- Write-down prevention 攔的是「資訊從高機密流向低機密」— 經典的 Bell-LaPadula 模型
- 不需要等三條腿湊齊，兩條就該警示

**Hermes 場景舉例**：
- 探索時 fetch 了 remote 網頁（untrusted content），然後 read 了 local skill file（private data），接著嘗試 write 回 note — 這時 write-down gate 該介入
- 目前我們的 sanitizer + plan-then-execute 擋了 injection，但沒擋「正常內容被 agent 誤判後混合私密資料輸出」

### 3. Skills 安全掃描是盲點

Snyk Agent Scan 掃 skills 這件事提醒我們：Hermes 的 128 個 skill 是 supply chain attack surface。

目前我們有：
- `validate_note.py`：掃**產出**（autonomous_notes）的 injection 殘留
- `plan-then-execute`：擋**探索過程**中的 injection 操控

我們沒有：
- **Skill file 本身的靜態安全掃描**：檢查 skill content 是否有 hidden instruction、malware payload、credential leak
- **Auto-generated skill 的信任鏈**：`system-map` 和某些 cron job output 會自動生成/更新 skill file — 如果上游 data 被污染，skill 就會被污染

**可行的低成本動作**：寫一個簡單的 `scan_skill_security.py`（類似 `validate_note.py` 但針對 skill file），檢查：
- Hidden Unicode / zero-width chars
- Embedded URLs pointing to unknown domains
- Shell command patterns in skill body
- Hardcoded credentials pattern

### 4. 名詞政治學：Hermes 內部該怎麼命名

Simon Willison 的「名詞政治學」觀察在這次深讀中得到印證：
- Open Edison 用 **Lethal Trifecta** 這個詞（直接引用 Simon 的 coin）
- Snyk Agent Scan 用 **Toxic Flows** 來描述多步驟攻擊鏈
- 兩個詞都不是技術社群既有術語，但**定義清晰且不易被誤解**

對 Hermes 內部命名的啟發：
- `Plan-Then-Execute` — 好名字：自解釋、不易被誤解為其他東西
- `sanitize_fetch.py` — 可能太 generic（和其他 sanitization 混淆）
- 如果要加 trifecta awareness layer，命名需謹慎：`trifecta_gate`？`triple_lock`？`session_boundary_check`？— 值得先想好再寫 code

## 跨文章 Synthesis

從 Camel 筆記 → Lethal Trifecta 深讀 → Open Edison 實作 → Snyk skills scan，形成一條完整的 prompt injection 防禦光譜：

| Layer | Mechanism | 具體產物 | Hermes 狀態 |
|-------|-----------|---------|-------------|
| Supply Chain | Skills static scanning | snyk-agent-scan / validate_note.py | 🟡 部分（只有產出掃描，無 skill 本身掃描） |
| Input | Sanitization + Plan-Then-Execute | sanitize_fetch.py + explore plan lock | ✅ 已實作 |
| Runtime Monitoring | Trifecta tracking + ACL enforcement | Open Edison gateway | ❌ 未實作 |
| Runtime Prevention | Write-down gate + trifecta gate | Open Edison session tracking | ❌ 未實作 |
| Architectural | CaMeL capability tracking | Google DeepMind | ❌ 不需要 |

**下一步優先級判斷**：

Trifecta tracking + write-down gate 是**成本最低、覆蓋面最廣**的下一層防禦：
- 不需要改 tool execution layer
- 只需在每次 tool call 時 accumulate session state
- Warning 注入 prompt（不阻擋 execution，讓 agent 自己判斷）
- 實作量：一個 Python dict + ~30 行 tracking logic + tool tagging table

Skills scanning 是**長期防禦**，但目前威脅模型下優先級較低（Hermes 是單人 agent，supply chain attack 需要 attacker 先能寫入 skill file）。

## 未追蹤

- Open Edison 的 source code — `tool_permissions.json` 的 write-down prevention 實作細節（`src/` 目錄下的 gate logic）
- Snyk Agent Scan 的 `skills-report.pdf`（`.github/reports/skills-report.pdf`）— agent skill ecosystem 的新興威脅全景
- Simon Willison 的「名詞政治學」talk/blog（如果有的話）— 對命名 convention 有啟發
- Invariant Labs 被 Snyk 收購的時間線與動機（2025-2026 MCP security 市場信號）

## ✅ 本次探索完成

