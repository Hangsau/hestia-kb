---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Moltis-Deep-Features-BeforeCompaction-MessageReceived-Block-
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Moltis-Deep-Features-BeforeCompaction-MessageReceived-Block-.md
title: Moltis Deep Features — BeforeCompaction, MessageReceived/Block, ToolPolicy,
  AgentPresets
created: '2026-05-18'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Moltis Deep Features — BeforeCompaction, MessageReceived/Block, ToolPolicy, AgentPresets

**延續自**: [[2026-05-18-moltis-hooks-self-extending-skills]], [[2026-05-18-moltis-lifecycle-hooks-session-branching-checkpoints]]

## 來源

- https://docs.moltis.org/hooks.html — 完整 hooks 參考（含 BeforeCompaction、MessageReceived/Block）
- https://docs.moltis.org/tool-policy.html — 六層工具政策系統
- https://docs.moltis.org/agent-presets.html — Agent preset 系統（含 markdown agent definitions）
- https://docs.moltis.org/compaction.html — 四種 compaction 模式（**Hermes 被引為 structured mode 參考實作**）

## Per-source Insight

### 1. BeforeCompaction Hook — 攔截 context compaction

**位置**：Modifying Events（sequential），可 modify/block。

Moltis 在 context compaction 執行前觸發此 hook。這讓 policy 可以在 compaction 前決定：
- 是否允許本次 compaction（block = 暫停）
- 是否修改 compaction 參數（如 threshold）
- 是否在 compaction 前先做某件事（如存檔關鍵 context）

對 Hermes 的啟發：memory-consolidator 是 Hermes 的核心管線（L1 MEMORY.md → L2 memory-consolidator → L3 briefing-updater），但目前沒有 compaction 前的 hook 點。若加入 `BeforeCompaction` hook，可以在以下場景攔截：
- 偵測到 critical task 未完成 → 延遲 compaction
- compaction threshold 動態調整（依 session 類型）
- compaction 前自動將關鍵決策寫入 vault

**Moltis 的 compaction 系統本身值得注意**：四種模式
1. `deterministic`（預設）：零 LLM call、零 token 成本、離線可用。建結構化 summary（message count、tool name、file path、head-3 + tail-5 timeline）
2. `recency_preserving`：保留 head + tail ~20% verbatim，中間 prune tool output
3. `structured`：Head + LLM summary + tail。模板格式包含 Goal/Constraints/Progress/Key Decisions/Relevant Files/Next Steps/Critical Context
4. `llm_replace`：舊式，全部取代為 LLM summary

**重要**：Moltis 的文件明確引用 Hermes：
> "hermes-agent/agent/context_compressor.py — reference implementation of the head + LLM summary + tail strategy that inspired structured mode."

Hermes 的 context_compressor 被 Moltis 列為 structured mode 的參考實作。但 Hermes 目前缺少 deterministic 和 recency_preserving 這兩種零成本方案。

### 2. MessageReceived Hook + Block(reason) — Comms 防火牆

這是 Moltis hook 系統中對 Talos 最有啟發的機制：

**運作方式**：
- `MessageReceived` 是 Modifying Event（sequential）
- 當 hook 回傳 `exit 1`（block）時，系統行為：
  - User message **不被持久化**到 session store
  - **不啟動 agent run**
  - `reason`（stderr 輸出）**被遞送回發送者**，經由原始 channel（Telegram/Discord/Web）
  - Web client 則 broadcast 為 chat rejection event

**Payload 結構**：
```json
{
  "event": "MessageReceived",
  "session_key": "telegram:bot-main:-100123",
  "content": "user's raw text",
  "channel_binding": {
    "surface": "telegram",
    "session_kind": "channel",
    "channel_type": "telegram",
    "account_id": "bot-main",
    "chat_id": "-100123",
    "chat_type": "channel_or_supergroup"
  }
}
```

**對 Talos comms 治理的意義**：
- 目前 Talos/Hestia 的 comms 沒有 message-level blocking——所有 thread message 都會被讀取和處理
- 若移植 MessageReceived/Block 模式：可以在 message ingestion 層就攔截惡意或無效訊息
- Block(reason) 的 channel-aware response 設計精妙：不是 silent drop，而是告知發送者「為什麼被擋」
- Channel provenance（surface/session_kind/channel_type）讓 policy 可以依來源做不同處理

**安全性**：Moltis 也用了 `BeforeLLMCall` + `AfterLLMCall` 做 prompt injection filtering，這是雙層防禦（ingestion + LLM boundary）。

### 3. ToolPolicy — 六層 deny-always-wins 系統

這是目前看過最完整的 agent tool governance 模型：

| Layer | Config path | Applies to |
|-------|------------|------------|
| 1 Global | `[tools.policy]` | All sessions |
| 2 Per-provider | `[providers.<name>.policy]` | Requests through that provider |
| 3 Per-agent preset | `[agents.presets.<id>.tools]` | Sub-agents with that preset |
| 4 Per-channel group | `[channels.<type>.<account>.tools.groups.<chat_type>]` | Channel sessions |
| 5 Per-sender | `...by_sender.<sender_id>` | Messages from that sender |
| 6 Sandbox | `[tools.exec.sandbox.tools_policy]` | Sandboxed execution |

**Merge 規則**：
- **Deny accumulates**：任何層 deny 的工具，後續層無法 re-allow
- **Allow replaces**：非空 allow list 取代前一層的 allow list；空 allow = permit all（非 deny 的）
- **Glob patterns**：支援 `"*"`、`"browser*"`、`"exec"` 三種精細度
- **Profiles**：`"minimal"` → exec only；`"coding"` → exec/browser/memory；`"full"` → *

**與 Hermes 對標**：
- Hermes 目前有 cron job 層的 `enabled_toolsets` 欄位（binary：全開 or 限定）
- Moltis 的 deny-always-wins + 六層 merge 更細緻：可以對不同 channel/provider/agent 設不同政策
- 關鍵差異：Hermes 沒有 per-channel、per-sender、sandbox 層
- Moltis 的 "deny always wins" 設計比 "allow overrides" 更安全——防止權限意外擴大

### 4. AgentPresets — System Prompt Version Management

Moltis 的 agent preset 系統是 sub-agent 配置管理方案：

**兩種定義方式**：
1. **TOML**（`moltis.toml` 中的 `[agents.presets.<name>]`）：優先級最高
2. **Markdown + YAML frontmatter**（`~/.moltis/agents/*.md`）：輕量版

**Config 欄位**：
- `identity.{name, emoji, theme}` — agent 身分
- `model` — 指定模型（fallback 到 session provider）
- `tools.{allow, deny}` — 工具政策
- `system_prompt_suffix` — 附加 system prompt（markdown body 成為 suffix）
- `max_iterations, timeout_secs` — 資源限制
- `sessions.*` — 跨 session 存取權限（key_prefix, allowed_keys, can_send, cross_agent）
- `memory.{scope, max_lines}` — per-agent persistent memory（MEMORY.md）
- `delegate_only` — 限制為 delegation/session 工具

**Built-in presets**：researcher, coder, reviewer, qa, ux, docs, coordinator（各預設不同工具集和行為）

**對 Hermes 的啟發**：
- Hermes 已有 Talos/Hestia 兩個 profile，但 preset 系統更 granular——不只是 personality，而是完整的 model/tool/memory/session 配置
- Markdown agent definitions（YAML frontmatter + body as system_prompt_suffix）是優雅的版本管理方案——agent 配置本身就是文件
- Per-agent memory scope（user/project/local）讓 sub-agent 可以有獨立持久記憶，而非依賴共用 vault——這解決了 multi-agent 的記憶隔離問題

### 5. Compaction — Moltis 引用 Hermes，但多了零成本方案

**驚喜發現**：Moltis 的 structured compaction mode 明確引用 Hermes 的 `context_compressor.py` 作為參考實作：
> "hermes-agent/agent/context_compressor.py — reference implementation of the head + LLM summary + tail strategy that inspired structured mode."

**Hermes 的優勢**：structured mode（head + LLM summary + tail）已被業界認可為 best practice。

**Hermes 的缺口**：
1. **無 deterministic mode**：Moltis 的預設模式——零 token、零延遲、離線可用。Hermes 每次 compaction 都要 LLM call
2. **無 recency_preserving mode**：保留 tail verbatim、中間 prune tool output——也是零成本。適合短 session 或低成本場景
3. **無 BeforeCompaction hook**：無法在 compaction 前做 policy 判斷
4. **無 summary_model 分離**：Moltis 規劃支援 cheap auxiliary model 做 compaction，主模型專注 coding

## Hermes 啟發

### 可行動的改進（依優先序）

1. **移植 MessageReceived/Block 到 Talos comms**（高優先）
   - Talos 的 comms reader 可以在 message ingestion 層加入 policy check
   - Block 時不 silent drop，而是寫 rejection 回 thread
   - 最簡單的實作：在 `comms_reader.py` 加一個 `--policy` flag，讀取 policy file

2. **Hermes memory-consolidator 加 deterministic mode**（中優先）
   - 零 LLM call 的 compaction：message count + tool name + file path + head/tail timeline
   - 作為 fallback（LLM call 失敗時）或低優先 session 的預設
   - Moltis 的 deterministic 實作在 `crates/chat/src/compaction.rs`，可參考邏輯

3. **Tool policy 從 binary 升級為 layered**（中優先，長期）
   - 目前 Hermes 的 `enabled_toolsets` 是 flat list
   - 移植 deny-always-wins + 分層 merge（至少：global + per-profile + per-channel）
   - 對 Talos 的守護者角色尤其重要——可對 Telegram channel 設不同 policy 於 Web UI

4. **Agent preset 系統**（低優先，長期）
   - Hermes 已有兩個 agent profile，短期不需要 preset 系統
   - 但 markdown agent definitions（YAML + body）是值得學習的配置格式

### 意外收穫

Moltis 文件引用 Hermes 的 context_compressor 代表：
- Hermes 的 structured compaction 設計已被外部專案認可
- 但 Hermes 需要補上零成本模式（deterministic/recency_preserving）才能完整
- BeforeCompaction hook 是 Hermes memory-consolidator 下一步自然的擴展點

## ⏳ 未追蹤

- Moltis 的 `dcg` (destructive_command_guard) — 49+ destructive pattern categories，外部工具整合，可對標 Hermes 的 dangerous command blocklist
- Moltis 的 `session-memory` surface — 在 hooks.html 有連結但未深入
- Moltis 的 `BOOT.md` / `TOOLS.md` / `AGENTS.md` workspace context files — 對標 Hermes 的 workspace-context skill

## ✅ 本次探索完成
