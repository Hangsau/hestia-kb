---
_slug: 40-Resources-_mixed-explorations-2026-05-15-DeepSeek-Context-Caching-實證---Timestamp-Cache-Buster-源碼確認
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-DeepSeek-Context-Caching-實證---Timestamp-Cache-Buster-源碼確認.md
title: DeepSeek Context Caching 實證 + Timestamp Cache Buster 源碼確認
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- cache
- deepseek
- hermes
- hit
- line
- prefix
- prompt
- session
- system
- timestamp
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# DeepSeek Context Caching 實證 + Timestamp Cache Buster 源碼確認

**延續自**: [[2026-05-15-prompt-caching-kv]] 的未追蹤 leads（#1 DeepSeek caching 支援 + #2 timestamp template source）

**日期**: 2026-05-15

---

## Insight 1: DeepSeek 確實支援 Context Caching（Disk-Based）

來源：[DeepSeek API Docs — Context Caching](https://api-docs.deepseek.com/guides/kv_cache)

### 機制

DeepSeek 用的是 **hard disk cache**，不是 Anthropic 的 in-memory KV cache：

| 特性 | Anthropic | DeepSeek |
|------|-----------|----------|
| Cache 類型 | In-memory KV cache | Disk-based prefix cache |
| 控制方式 | Explicit（手動標記 cache_control） | Automatic（預設開啟，零程式碼改動） |
| TTL | ~5 分鐘 | 幾小時到幾天 |
| Hit 條件 | Prefix 由 developer 指定 | 完整匹配 cached prefix unit |
| 成本差異 | Cache read 10x cheaper | 免費 tier，無定價差異 |

### Cache Prefix Unit 機制（關鍵）

DeepSeek 產生三種 cache prefix unit：

1. **Request boundary units**：每次請求的 user input 結尾 + model output 結尾各自形成一個 unit
2. **Common prefix detection**：系統偵測多個請求的共用 prefix 後自動持久化
3. **Fixed token interval units**：長文字在固定 token 間隔處切出 unit（避免長 prefix 永遠無法命中）

**Cache hit 條件：必須 FULL MATCH 一個 cache prefix unit。** 這是和 Anthropic 最大的差異 — Anthropic 的 cache 允許 partial prefix match，DeepSeek 不行。

### 範例 2（長文件 Q&A）最接近 Hermes 情境

```
Request 1: system("分析師 persona") + user("財報全文 + 摘要")
Request 2: system("分析師 persona") + user("財報全文 + 獲利分析")
→ 前兩次都不會 hit cache（user message 後半不同）
→ 系統偵測到 system + "財報全文" 是 common prefix → 持久化為 cache unit
→ Request 3: system("分析師 persona") + user("財報全文 + 收支分析") → CACHE HIT
```

**對 Hermes 的意義**：system prompt 中 persona + skills + context 是穩定的（不隨 session 變），只要它們在 prompt 的 prefix 位置一致，DeepSeek 的 common prefix detection 就會把這整段持久化為 cache unit。

### Usage 欄位

API response 的 `usage` 新增兩個欄位：
- `prompt_cache_hit_tokens`：本次 cache hit 的 token 數
- `prompt_cache_miss_tokens`：本次 cache miss 的 token 數

### 限制

- **Best-effort**：不保證 100% hit rate
- **Cache 建立耗時數秒**：首次請求後才建立，不是即時
- **TTL 不固定**：幾小時到幾天後自動清除

---

## Insight 2: Timestamp Cache Buster 源碼確認

**檔案**：`/usr/local/lib/hermes-agent/run_agent.py`

### 注入點

```python
# Line 4949-4958
from hermes_time import now as _hermes_now
now = _hermes_now()
timestamp_line = f"Conversation started: {now.strftime('%A, %B %d, %Y %I:%M %p')}"
if self.pass_session_id and self.session_id:
    timestamp_line += f"\nSession ID: {self.session_id}"
if self.model:
    timestamp_line += f"\nModel: {self.model}"
if self.provider:
    timestamp_line += f"\nProvider: {self.provider}"
prompt_parts.append(timestamp_line)
```

### System Prompt 完整建構順序

`_build_system_prompt()` 的 `prompt_parts` append 順序（line 4814-4991）：

| # | 內容 | Line | 穩定性 |
|---|------|------|:---:|
| 1 | SOUL.md / DEFAULT_AGENT_IDENTITY | 4830/4835 | ✅ 穩定 |
| 2 | HERMES_AGENT_HELP_GUIDANCE | 4838 | ✅ 穩定 |
| 3 | Tool guidance (memory/session/skill/kanban) | 4840-4855 | ✅ 隨 tools 變 |
| 4 | Nous subscription prompt | 4857-4859 | ✅ 穩定 |
| 5 | Tool use enforcement | 4882 | ✅ 穩定 |
| 6 | system_message (user-provided) | 4897-4898 | ✅ 穩定 |
| 7 | MEMORY.md + USER.md | 4900-4909 | ✅ 穩定 |
| 8 | External memory provider | 4912-4918 | ✅ 穩定 |
| 9 | Skills (`<available_skills>`) | 4929-4936 | ✅ 隨 tools 變 |
| 10 | Context files (AGENTS.md) | 4944-4947 | ✅ 穩定 |
| **11** | **Timestamp** | **4958** | **❌ 每次 session 不同** |
| 12 | Alibaba model identity | 4963-4970 | ✅ 條件式（僅 Alibaba） |
| 13 | Environment hints (WSL, Termux) | 4974-4976 | ✅ 穩定 |
| 14 | Platform hints (Telegram, Discord) | 4978-4989 | ✅ 穩定 |

然後 `"\n\n".join(prompt_parts)` 組成 system message（line 4991）。

### 問題

Timestamp 在 #11 位置 — 不是最尾端，而是卡在 skills/context 和 platform hints 之間。這意味著：

- **同一個 session 內**：`_cached_system_prompt` 保持不變 → turns 2+ 全部 cache hit ✅
- **跨 session（互動）**：每次新 session 的第一個 turn 都 cache miss ❌
- **跨 session（cron）**：cron session 都是 single-turn → 每次都是 cache miss ❌

### 現有改善提案

`proposals/2026-05-15-session-timestamp-cache-buster.md` 已經開了 CHANGE 提案，三個前提條件：
1. ✅ **確認 DeepSeek API 是否支援 prompt caching** — 本次調查完成，確認支援
2. ⬜ **確認 `Conversation started` 的 template source** — 本次調查完成，確認為 `run_agent.py:4951`
3. ⬜ **確認移動後不影響其他依賴 timestamp 位置的邏輯**

---

## Hermes 啟發

### 1. 修法很簡單

把 `prompt_parts.append(timestamp_line)`（line 4958）移到 line 4990（`return` 前一行），讓 timestamp 成為 system prompt 的最後一部分。這樣做的好處：

- Persona + skills + context 全部在 timestamp 之前 → DeepSeek 的 common prefix detection 會把這整段持久化為 cache unit
- 跨 session 的第一個 turn 還需要 cache warmup（common prefix detection 需要 2 個請求），但第 3+ 個 session 開始就會命中
- **更重要的是**：同一 session 內的 cache 機制不受影響（system prompt 整段不變，已經是 cache hit）

### 2. 更好的架構：timestamp 進 user message？

另一個思路：把 `Conversation started` 從 system prompt 移到第一條 user message。這樣 system prompt 完全 immutable，每次都 cache hit。但這需要改 gateway 層的 message construction。

### 3. 驗證方式

DeepSeek API response 的 `usage.prompt_cache_hit_tokens` 可以直接驗證改善效果。修完後可以：
- 啟動一個 session，跑兩個 turn，看 turn 2 的 `prompt_cache_hit_tokens` 是否 > 0
- 關掉重開新 session，跑一個 turn，看是否有 cache hit（如果 common prefix detection 已生效）

### 4. DeepSeek 免費但 cache 仍有意義

雖然 DeepSeek 目前是免費 tier，cache hit/miss 不影響成本，但 latency 有差（Anthropic 宣稱 cache hit 減少 up to 85% latency）。而且 **如果未來換付費 provider，這個優化會直接變成成本節省**。

---

## 跨文章 Synthesis

- **[[2026-05-15-prompt-caching-kv]]** — 本篇是該筆記「未追蹤」leads #1 和 #2 的直接追蹤
- **[[2026-05-15-agent-architecture-design]]** — 該筆記提到 DeepSeek 免費所以 cache 不重要，但實情是 latency 仍有差，而且架構上要為未來付費做準備
- **`proposals/2026-05-15-session-timestamp-cache-buster.md`** — 提案的前提條件 #1 和 #2 已在本篇完成

---

## 未追蹤

- [ ] 確認移動 timestamp 後不影響其他依賴 timestamp 位置的邏輯（`session_search` indexing、`hermes_state.py` 等）
- [ ] 實驗性驗證：改完後跑兩個 session 看 `prompt_cache_hit_tokens` 變化
- [ ] DeepSeek 的 cache TTL 實測（幾小時到幾天太模糊）
- [ ] Anthropic explicit cache control 對 Hermes session continuity 的價值（從 prompt-caching 筆記的 lead #3）

