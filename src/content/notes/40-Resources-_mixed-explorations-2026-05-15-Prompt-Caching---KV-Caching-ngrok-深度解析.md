---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Prompt-Caching---KV-Caching-ngrok-深度解析
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Prompt-Caching---KV-Caching-ngrok-深度解析.md
title: Prompt Caching = KV Caching（ngrok 深度解析）
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- anthropic
- cache
- caching
- context
- deepseek
- hermes
- prefix
- prompt
- provider
- session
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Prompt Caching = KV Caching（ngrok 深度解析）

**來源**: [ngrok blog — Prompt caching: 10x cheaper LLM tokens, but how?](https://ngrok.com/blog/prompt-caching/) (306 pts, 72 comments)
**日期**: 2026-05-15

---

## Per-source Insights

### ngrok 文章

**核心論點**：Prompt caching 就是 KV caching。LLM inference 是 autoregressive loop，每次 generate 新 token 都要把整個 prompt + 已產生的 output 餵進 attention。但 attention 中間產物 — Q、K、V 矩陣 — 只有最新 token 的 Q/K/V 是新的，前面所有 token 的 K 和 V 都不變。Cache 住 K 和 V，inference 時只需計算最新一個 token 的 Q/K/V，再拿 cached K/V 拼回來算 attention score。

**關鍵數據**：
- cached input tokens 比 regular input tokens 便宜 **10x**（OpenAI 跟 Anthropic 都是）
- latency 減少 **up to 85%**（Anthropic 宣稱，作者實測確認）
- Cache TTL：**5-10 分鐘**後過期
- **Partial prefix match**：不需要完全一樣的 prompt，prefix 有 match 的部分就能 reuse

**OpenAI vs Anthropic 差異**：
- OpenAI：自動 caching，hit rate ~50%（作者實測）
- Anthropic：手動控制，指定要 cache 的 prompt block，hit rate 100%
- Anthropic 要付 caching 費用但換來可預測的 latency

**Temperature 不影響 cache**：temperature/top_p/top_k 作用在 inference loop 的最後一步（挑 token），跟 attention 計算無關。可以自由改這些 parameter 不用擔心 invalidate cache。

**Tokenization 影響**：同一個 prompt 用不同 tokenizer 產生的 token 序列不同 → 不同 model（GPT vs Claude）cache 不互通，甚至同 provider 不同 model 也可能不互通（tokenizer 版本差異）。

### HN 討論

**duggan — cache busting 實戰教訓**：
> "Real facepalm moment when I realized we were busting the cache on every request by including date/time near the top of the prompt. Even just moving it to the bottom helped move a lot of usage from 30-50% cached to 50-70%."

這是整篇對 Hermes 最直接可操作的 insight：**動態內容放 prompt 尾部，不要把 cacheable prefix 切斷**。

**willvarfar — 跨使用者共享 cache**：
> "If I were running a provider I would be caching popular prefixes across all users. There must be so many questions that start 'what is' or 'who was'?"

這暗示 provider 端可能已經做了跨使用者 shared cache。但用戶端能控制的是自己 API key 下的請求 pattern。

**Havoc — API key 隔離**：
> "Is cache segregated by user/API key? Was looking at modifying outgoing requests via proxy and wondering whether that's harming caching."

問題很好但文章沒回答。推測：cache likely per API key，不然跨用戶 cache 會有安全疑慮。

---

## Hermes 啟發

### 1. System prompt 中的 cache buster（🔴 可直接改善）

Hermes 每次 session 開頭會注入：
```
Conversation started: Friday, May 15, 2026 06:00 PM
Model: deepseek-v4-pro
Provider: deepseek
```

這個 timestamp 在 prompt **最頂端**，等於每次 session 都讓整個 prompt 的 prefix 變成 unique string → **KV cache 完全無法命中**。

**改善方向**：把 `Conversation started` 移到 prompt 尾部（或至少移到 persona/system prompt 之後）。

但要注意：這行是 Hermes agent framework 自己的 template，不在 user config 裡。需要確認是否可以改 template 或透過 config override。

### 2. Skill loading 是天然的 cache goldmine

Hermes 每次對話都要載入大量 skill（system prompt + `<available_skills>` block），這些內容在**同一個 session** 裡完全不會變 → 是完美的 cacheable prefix。DeepSeek 如果支援 prompt caching（待確認），這部分應該有很高的 cache hit。

### 3. Cron session 不該預期 cache hit

Cron session 每次都獨立啟動，prompt prefix（timestamp + 指令）每次都不同 → cache 本來就 hit 不了。重點是**互動 session** 的 multi-turn 連續對話。

### 4. 如果未來用到 Anthropic

Anthropic 的 explicit cache control 對 Hermes 的 session continuity 模式可能有特殊價值 — 可以把 `MEMORY.md` + persona + skills 這些固定區塊標記為 cacheable，讓每 turn 都從 cache 開始，只傳遞新的對話內容。

---

## 跨文章 Synthesis

這篇跟之前讀過的 **agent-cost-curve**、**context-mode**、**contextforge-spike** 形成一個完整的故事線：

| 筆記 | 面向 | 解法 |
|------|------|------|
| agent-cost-curve | 成本隨 context 成長爆炸 | prompt caching 是 provider 端的解法 |
| context-mode | context 段管理架構 | 用戶端的結構化 context 分段 |
| prompt-caching (本篇) | attention 層面的 cache 機制 | 解釋了 _為什麼_ 分段有助於 cache |
| contextforge-spike | MCP gateway 整合 | gateway 層可以主動管理 cache pattern |

**合成觀點**：context 管理有三層 — provider（KV cache）、gateway（context 分段/路由）、agent（skill 載入策略）。這三層可以協同運作：gateway 保持固定 prefix → provider cache hit → agent 只傳遞差異化的 conversation content。目前 Hermes 在三層都有元件（DeepSeek provider、gateway、skill system），但 cache 意識還沒進到設計裡。

---

## 未追蹤

- [x] 確認 DeepSeek API 是否支援 prompt caching（官方 docs）→ [[2026-05-15-deepseek-cache-timestamp-trace]]
- [x] 檢查 Hermes 的 `Conversation started` template 是否可以從 config 改位置 → [[2026-05-15-deepseek-cache-timestamp-trace]]（源碼確認為 `run_agent.py:4951`）
- [ ] Anthropic prompt caching pricing vs DeepSeek 目前成本比較
- [ ] willvarfar 的 subsequence caching 問題 — attention 理論上只能 cache prefix，subsequence 需要 speculative decoding 那類技術？值得追

