---
_slug: 40-Resources-_mixed-explorations-2026-05-14-Agent-Economics--Cost-Curves---Memory-Fallacies
_vault_path: 40-Resources/_mixed/explorations/2026-05-14-Agent-Economics--Cost-Curves---Memory-Fallacies.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 23:\n    title: Agent Economics: Cost Curves & Memory Fallacies\n  \
  \                        ^"
_raw_fm: '

  title: Agent Economics: Cost Curves & Memory Fallacies

  date: 2026-05-14

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, cache, context, conversation, cost, domain, loop, memory, reads,
  tool]

  created: 2026-05-14

  updated: 2026-06-15

  status: active

  '
title: 'Agent Economics: Cost Curves & Memory Fallacies'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Agent Economics: Cost Curves & Memory Fallacies

**日期**: 2026-05-14 | **來源**: HN Algolia

---

## 1. Expensively Quadratic: the LLM Agent Cost Curve

**作者**: Philip Zeyliger (exe.dev/Shelley) | **日期**: 2026-02-03
**連結**: https://blog.exe.dev/expensively-quadratic

### 核心發現

Agent loop 的成本結構不是線性，而是**實質上的二次曲線**（cache reads 在 context 增長時變成 dominant cost）。

**關鍵數字**：
- 在 ~27,500 tokens 時，cache reads 已佔總成本 **50%**
- 到 conversation 結尾，cache reads 佔總成本 **87%**
- 一個普通的 feature implementation session 花 $12.93

**成本結構**（Anthropic Opus 4.5 費率）：input = x, cache write = 1.25x, output = 5x, cache read = x/10

雖然 cache read 單價只有 input 的 1/10，但因為**每一輪都重讀整個 context**，累積起來就變成那條可怕的三角形。

### 實用建議

1. **少做 LLM call**：每個 call 都要 re-read cache，call 數比 token 數更決定成本
2. **Subagents / LLM-assisted tools**：把 iteration 移出 main context window（Shelley 的 keyword search tool 就是這樣）
3. **重開 conversation**：感覺浪費 context，但 re-establish context 的成本通常比繼續舊對話便宜
4. **不要閹割 tool output**：與其分 5 次讀檔案，不如一次讀完——反正最終都要讀

### 一個框架問題

> Are cost management, context management, and agent orchestrations all really the same problem?

這三者在 agent loop 結構下本質上是同一件事。RLM（Recursive Language Models）可能是方向。

---

## 2. The Portable Memory Wallet Fallacy

**作者**: Daniel Chalef (Zep) | **日期**: 2025-06-19
**連結**: https://blog.getzep.com/the-ai-memory-wallet-fallacy/

### 四個根本問題

**問題 1: 經濟誘因相反**
AI 公司的 memory = 護城河。不像銀行（賺利息、手續費，不是賺 data），AI 公司靠 user context 做個人化 lock-in。要他們自願交出 memory 等於要他們自願放棄競爭優勢。

**問題 2: 使用者其實不想管**
Privacy paradox：大家都說要 privacy，但行為相反。Cambridge Analytica 事件後 Facebook 使用量反而上升。Portable memory 要求使用者持續做 granular permission decisions（哪些記憶給哪個 agent、什麼用途、多久）——這是「不會 scale 的無盡計畫」。Apple ATT 成功因為它是 binary choice；portable memory 是相反的設計。

**問題 3: AI context 無法標準化**
銀行 data 是標準化的（日期、金額、商家）。AI context 是 high-dimensional 且 domain-specific：心理諮商 bot 的筆記 vs 購物助理的偏好 vs 自駕車的媒體偏好——彼此不相通，也不該通。更難的是 semantic interoperability：「想要健康」在電商是推薦有機食品，在生產力 app 是約醫生——同一句話在不同 context 完全不同。

**問題 4: 安全風險倍增**
Memory injection attacks、liability chain 不清——誰負責 memory 被污染的後果？

### 一個共鳴點

> Cross-domain AI data offers limited utility.

這跟 Hermes 的 skill system 設計是呼應的——skill 是 domain-specific 的 procedural memory，不是 universal context。不試圖做萬能記憶，而是每個 domain 自己管自己的。

---

## 3. 短篇：Agent Loop 的 unreasonable effectiveness

**作者**: Philip Zeyliger | **連結**: https://sketch.dev/blog/agent-loop

一句話：9 行的 while loop + bash tool use 就已經非常有效。Claude 3.7 Sonnet 加一個 bash tool 能處理大多數開發任務。作者的核心論點：我們會看到更多 custom, ad-hoc, throw-away agent loops 出現在 `bin/` 目錄裡。

---

## 對 Hermes 的啟發

- **Cost curve 教訓**：Hermes 的 conversation 如果持續很長，成本結構會往 cache reads 傾斜。可以考慮實作「重開 conversation + summary injection」的 pattern
- **Memory fallacy 教訓**：不要做 universal memory。Skill system 的分 domain 設計是對的
- **Agent loop 教訓**：簡單就是力量。不要 over-engineer 主迴圈

