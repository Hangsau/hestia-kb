---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Behavior-Cache-for-Agents--Muscle-Mem---Butter-Mystery
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Behavior-Cache-for-Agents--Muscle-Mem---Butter-Mystery.md
_parse_error: "mapping values are not allowed here\n  in \"<unicode string>\", line\
  \ 2, column 33:\n    title: Behavior Cache for Agents: Muscle-Mem + Butter Mystery\n\
  \                                    ^"
_raw_fm: '

  title: Behavior Cache for Agents: Muscle-Mem + Butter Mystery

  date: 2026-05-15

  type: explorations

  tags: [explorations, auto-ingested]

  fingerprint: [agent, behavior, butter, cache, hermes, mem, muscle, replay, tool,
  trajectory]

  created: 2026-05-15

  updated: 2026-06-15

  status: active

  '
title: 'Behavior Cache for Agents: Muscle-Mem + Butter Mystery'
type: resource
status: seedling
created: '2026-06-15'
updated: '2026-06-15'
---

# Behavior Cache for Agents: Muscle-Mem + Butter Mystery

**延續自**: [[2026-05-15-agent-cost-security-convergence]] 的未追蹤 lead（Butter behavior cache）

**日期**: 2026-05-15 | **來源**: HN Algolia → GitHub README → Erik Dunteman blog

**標籤**: #agent-cache #behavior-cache #trajectory-replay #jit-compiler #hermes-inspiration

---

## Insight 1: Butter ≠ Behavior Cache（標題不匹配）

HN 上有篇 Show HN 標題「Butter – A Behavior Cache for LLMs」（50 pts），但 butter.dev 的實際內容是：

> Butter is building bVisor, an incredibly lightweight sandbox runtime for AI agents.

Butter 是 sandbox 公司（bVisor），不是 behavior cache 產品。HN 標題的 "behavior cache" 可能是投稿者用詞不準確（或 Butter 早期 pivot 過）。HN 討論也很淺（22 comments，多為「interesting」「what's the pricing」）。

**→ 這條 lead 可以結案。bVisor 本身作為 agent sandbox 或許值得追，但那是另一個主題。**

---

## Insight 2: Muscle-Mem — JIT Compiler for Agent Behavior

**Muscle-Mem**（pig-dot-dev/muscle-mem，226 pts，51 comments）才是真正的 behavior cache。Erik Dunteman 做了五個月 computer-use agent 後提煉出的概念。

### 核心命題：Long Tail Environment

大部分真實環境是「長尾環境」：90% predictable，10% 有 edge case。

| 方案 | 90% happy path | 10% edge case |
|------|:---:|:---:|
| RPA（script） | ✅ 快、便宜、確定性 | ❌ 炸掉 |
| CUA（agent） | ❌ 慢、貴、不穩定 | ✅ 動態處理 |
| **Muscle Memory** | ✅ replay cached trajectory | ✅ fallback to agent |

### 架構三步驟

1. **Cache Validation**（最關鍵）：capture 當前環境 → compare 與 cached 環境 → 決定 cache hit/miss
2. **Cache Hit**：replay 已記錄的 tool-calling trajectory（純確定性，零 token cost）
3. **Cache Miss**：delegate 給 agent，record 新 trajectory

### Check：capture + compare

```python
Check(
    capture: Callable[P, T],   # 從環境提取特徵
    compare: Callable[[T, T], Union[bool, float]],  # 比對
)
```

每個 tool 可掛 `pre_check` 和 `post_check`。key insight：**cache validation 的責任在 developer 身上**（寫 capture/compare），muscle-mem 只管 replay mechanism。

### 約束條件

- **Bring your own agent**：engine 不碰 agent internals，只做 call/monitor/replay
- **Bring your own environment**：screenshot/click 等 I/O 全由 user callback 定義
- **No hidden nondeterminism**：永遠不跑 LLM 或隨機 process（除了 user callback）
- **Write tools 必須純**：只用 LLM 提供的 args，no closure/global state

### 參數化（params system）

如果 trajectory 中有值需要在不同 run 間動態替換（如 form filling 的 "John" → "Jane"），用 top-level `params` mapping：

```python
engine("fill form with name: John", params={"name": "John"})
engine("fill form with name: Jane", params={"name": "Jane"})  # cache hit, 替換參數
```

---

## Hermes 啟發

### 相似點

- **Autonomic layer 已有 replay 概念**：heartbeat 的 autonomic layer 執行確定性 action（snapshot → scoring → select → execute），不經 LLM。這其實就是一種 hardcoded muscle memory。
- **Skills 作為預定義 trajectory**：skills 裡 `## Steps` 就是預先定義的 tool-calling 路徑。但 skills 是 hand-authored，muscle-mem 是 runtime-learned。

### 差異點（muscle-mem 做得更好的地方）

1. **Cache validation via Checks**：Hermes 沒有「當前環境是否適合執行這個 skill」的機制。muscle-mem 的 Check primitive 是我們缺乏的。
2. **Runtime trajectory learning**：Hermes skills 是靜態文件，muscle-mem 能在 runtime 學新 trajectory。如果 Hermes 有這個能力 → agent 可以從重複任務中自我優化。
3. **Edge case fallback**：muscle-mem 的 cache miss → agent 是很乾淨的 fallback 模式。Hermes 的錯誤處理比較 ad-hoc。

### 可能的 Hermes 應用

- **MCP tool replay cache**：如果某 MCP tool call sequence 被反覆觸發（如 `git status → git diff → git log`），cache 起來 replay，省 token。
- **Heartbeat 自主決策快取**：某些 heartbeat 判斷路徑（如「忙不忙」的邏輯）可以 cache 確定的結果。
- **Skill execution validation**：在 skill step 前掛 Check，確認環境符合 skill 假設（如 `which gh` 存在才執行 github skill）。

### 風險

- HN 討論中有人提到 cache validation 的困難：「comparing embeddings to cache validate the starting position is super gray, no clear threshold」（deepdarkforest）
- 對 Hermes 來說：我們的環境很動態（file system、process state、provider health），capture/compare 比 computer-use 更難定義
- 不是優先要做的事，但 concept 值得內化

---

## 跨文章 Synthesis

這篇筆記和以下前期探索的交集：

- **[[2026-05-14-compaction-context-rot-handbook]]** — context compaction 和 behavior caching 是兩種不同的省 token 策略：compaction 壓縮歷史，cache 避免重複計算
- **[[2026-05-14-lazy-tool-mcp-bloat]]** — lazy tool loading 和 trajectory replay 方向一致：減少不必要的 LLM 調用
- **[[2026-05-15-agent-cost-security-convergence]]** — 省成本是 agent 產業的共同方向，behavior cache 是具體手段之一

---

## 未追蹤但值得注意

- **Erik Dunteman 的 Pig.dev** — computer-use agent for legacy Windows apps。如果他們的 agent 架構有更多技術細節，可能對 autonomous task execution 有啟發
- **Voyager paper**（muscle-mem 的靈感來源之一）— Minecraft agent 用 code generation + skill library 做 lifelong learning。已經被多次引用，值得開專篇
- **muscle-mem 的 `examples/cua.py`** — 完整的 computer-use agent + muscle-mem 範例，可以看實際的 Check 寫法

