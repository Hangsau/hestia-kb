---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Agent-Architecture-Loop-Memory-Caching-三個設計決策維度
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Agent-Architecture-Loop-Memory-Caching-三個設計決策維度.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 5, column 26:\n    title: Agent Architecture: Loop, Memory, Caching — 三個設計決策維度\n\
  \                             ^"
_raw_fm: '

  tags: [agent-architecture, memory-design, prompt-caching, tool-use]

  source: autonomous-notes

  created: 2026-05-15

  title: Agent Architecture: Loop, Memory, Caching — 三個設計決策維度

  updated: 2026-06-15

  type: exploration

  status: active

  '
title: 'Agent Architecture: Loop, Memory, Caching — 三個設計決策維度'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Agent Architecture: Loop, Memory, Caching — 三個設計決策維度

**日期**: 2026-05-15
**來源**: HN Algolia（`agent memory` + `LLM agent` + `prompt caching`）

---

## 1. Agent Loop 的「不合理有效性」

**文章**: [The Unreasonable Effectiveness of an LLM Agent Loop with Tool Use](https://sketch.dev/blog/agent-loop) (447 pts, 320 comments)
**作者**: Philip Zeyliger (Sketch.dev)

核心論點：一個只有 9 行的 agent loop 就夠強了。

```python
def loop(llm):
    msg = user_input()
    while True:
        output, tool_calls = llm(msg)
        print("Agent: ", output)
        if tool_calls:
            msg = [handle_tool_call(tc) for tc in tool_calls]
        else:
            msg = user_input()
```

關鍵觀察：
- **bash 作為通用 tool** 就涵蓋大部分需求——裝套件、改檔案、跑測試、查 git
- 文字編輯 tool 反而是最難做好的（LLM 跟 sed 搏鬥的畫面）
- agent loop 正從「專用自動化」走向「ad-hoc、一次性的 bin/ 腳本」

> 對 Hermes 的啟發：我們的 heartbeat_v2 loop 本質上也是這個模式——snapshot → scoring → select → execute → log。差別在於我們加了 autonomic layer 做確定性判斷（不用 LLM 決定一切），這其實是對「pure LLM loop」的一個務實修正。

---

## 2. Portable Memory Wallet 的四個致命問題

**文章**: [The Private Agent Memory Fallacy](https://blog.getzep.com/the-ai-memory-wallet-fallacy/) (12 pts)
**作者**: Daniel Chalef (Zep)

反駁「讓使用者帶著 memory 跨 agent」的理想：

| 問題 | 核心論點 |
|------|---------|
| **經濟誘因不對齊** | AI 公司把 user context 當核心競爭優勢，自願交出等於自殺 |
| **使用者不想管** | Privacy paradox：說要隱私但選方便。ATT 成功是因為**一次性二元選擇**，memory wallet 要的是**持續複雜決策** |
| **Context 無法標準化** | 心理諮商 bot 的記憶 vs 購物助手的記憶，結構完全不同。跨 domain transfer 語意無法保證 |
| **安全風險** | Memory injection attack 已在論文展示，portability 放大攻擊面 |

> 對 Hermes 的啟發：我們的 memory pipeline（L1 MEMORY.md → L2 consolidator → L3 briefing）是 **single-agent, single-user** 的設計，剛好避開了 portable memory 的所有陷阱。但如果未來要跨 agent 共享 context，這篇文章是必讀的警訊。

---

## 3. Prompt Caching 到底在 Cache 什麼

**文章**: [Prompt caching: 10x cheaper LLM tokens, but how?](https://ngrok.com/blog/prompt-caching/) (306 pts)
**作者**: Sam Rose (ngrok)

從 transformer 內部解釋 KV-cache：

1. **Tokenizer** → prompt 切成 tokens（數字）
2. **Embedding** → tokens 轉成向量
3. **Transformer block**（重複 N 層）：
   - **Attention**: 計算 token 之間的關聯（Q·K^T → softmax → ×V）
   - **Feedforward**: 逐 token 的非線性變換
4. **Output** → 預測下一個 token

**Cache 的是什麼？** KV-cache：attention 機制中，**已經算過的 prefix tokens 的 Key 和 Value 矩陣**。新 token 只需算自己的 Q 並跟 cached K 做 attention，不需重算整個 prefix。

- 這就是為什麼 cached input tokens **10x 便宜**：跳過 attention 的 O(n²) 計算
- Cache 是 per-prefix 的：同一個 system prompt + 前綴才能 hit
- 長 prompt 的 latency 可降 **85%**（Anthropic 官方數據）

> 對 Hermes 的啟發：我們的 system prompt + skill 前綴如果結構化，可以最大化 cache hit。但目前用 DeepSeek（免費），cache hit 對我們沒有成本差異。如果未來換付費模型，這是第一優先的優化點。

---

## 交會點：三個決策的取捨

這三篇文章雖然各自獨立，但拼在一起形成一個 agent 架構師的三難選擇：

```
         簡單 Loop ←→ 複雜 Orchestration
              ↑           ↑
         (sketch.dev)  (LangGraph, etc.)

         Agent-owned  ←→ Portable/shared
           Memory           Memory
              ↑               ↑
         (Hermes 現狀)    (Zep 的批判對象)

         不管 Cache     ←→ 精心設計 Prefix
         (DeepSeek免費)     (付費模型必做)
```

Hermes 目前在三個軸上都偏左——簡單 loop、自用 memory、不管 cache。這不是設計缺陷，是**有意識的選擇**：在免費模型 + 單一使用者的條件下，左側是最佳解。但當條件改變（付費模型、多使用者、複雜工作流），每個軸都可能需要右移。

---

## 相關筆記

- [[2026-05-14-Agent-Economics--Cost-Curves---Memory-Fallacies]]（memory fallacy 補強）
- [[2026-05-14-Post-Vector-Agent-Memory-2025-2026-的共識轉向]]
- [[2026-05-14-Compaction-Context-Rot--AI-Agent-Engineering-Handbook]]（prompt caching 應用層）
