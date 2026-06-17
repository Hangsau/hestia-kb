---
_slug: 40-Resources-_mixed-explorations-2026-05-22-Behavior-Cache---Sandbox-Muscle-Mem---bVisor-探索
_vault_path: 40-Resources/_mixed/explorations/2026-05-22-Behavior-Cache---Sandbox-Muscle-Mem---bVisor-探索.md
title: Behavior Cache × Sandbox：Muscle-Mem + bVisor 探索
date: 2026-05-22
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- behavior
- butter
- bvisor
- cache
- llm
- mem
- muscle
- replay
- sandbox
created: '2026-05-22'
updated: '2026-06-15'
status: budding
---

---
title: "Behavior Cache × Sandbox：Muscle-Mem + bVisor 探索"
date: 2026-05-22
type: explorations
tags: [explorations, auto-ingested]
fingerprint: [agent, behavior-cache, muscle-mem, sandbox, bvisor, cache, tool, replay, llm]
---

# Behavior Cache × Sandbox：Muscle-Mem + bVisor 探索

**日期**: 2026-05-22
**來源**: HN（226 pts Muscle-Mem、50 pts Butter）→ 2026-05-15 探索筆記的 leads
**標籤**: #agent-architecture #behavior-cache #sandboxing #tool-replay #cost-optimization
**延續自**: [[2026-05-15-Agent-Economics---Security-成本與安全壓力如何收斂到同一個架構方向]]

---

## 1. Muscle-Mem — Behavior Cache for AI Agents（226 pts）

**Repo**: [pig-dot-dev/muscle-mem](https://github.com/pig-dot-dev/muscle-mem)（Python SDK）

### 核心機制

Muscle-Mem 是個 Python SDK，錄製 agent 的 tool-calling patterns，當相同 task 再現時**確定性地重放**已學過的軌跡，遇到 edge case 才 fallback 回 agent mode。

> "The goal is to get LLMs out of the hotpath for repetitive tasks, increasing speed, reducing variability, and eliminating token costs for the many cases that **could have just been a script**."

### 三層運作

```
Engine (core)
  ├── Check: capture(environment) → compare(current vs cached) → bool/float
  ├── Cache Hit: replay stored trajectory (zero LLM calls)
  └── Cache Miss: invoke agent → record new trajectory
```

### 與 Expensively Quadratic 的直接對話

Philip Zeyliger 說 cache read 是 O(calls × tokens) 的 quadratic 問題。Muscle-Mem 的解法：**根本不走 cache read，把整個 LLM call 跳過**。不是「讓 cache read 便宜一點」，而是「當 task 已在 cache 裡，根本不叫 LLM」。這是架構上的跳躍，不是優化。

### Cache Validation 是安全關鍵

`Check` 是 Muscle-Mem 的安全機制——每個 tool 要問：「環境的哪些 features 可以證明這次 action 是安全的？」回答得出來，就能用 Muscle Memory。回答不出來，就走 agent mode。

### Hermes 啟發

Muscle-Mem 的設計和 WS-025（Session Tree Phase Navigation）可以互補：
- Session Tree：解決「長 session 怎麼快速找到相關的歷史」
- Muscle-Mem：解決「找到後怎麼避免重跑已經學會的事」

兩者疊加等於：LRU cache（Session Tree）+ deterministic replay（Muscle-Mem）。Hermes 的 heartbeat loop 每次 cycle 都有重複操作（EVOLVE → snapshot → scoring → select → execute → log），相當比例可以 cache。

---

## 2. Butter — Local Agent Sandboxes（50 pts）

**URL**: [butter.dev](https://www.butter.dev/) — Building bVisor

Butter 和 bVisor 是同一個專案（Butter 是公司，bVisor 是產品）。這解決了 2026-05-15 note 的 ambiguity——當時 HN 標題說「Butter: Behavior Cache」但 bVisor 是 sandbox，兩者被 HN 標題搞混了。實際上：
- **bVisor**：Zig 寫的 lightweight sandbox（seccomp user notifier，2ms 開機）
- **Butter**：公司名，bVisor 的商業载体

所以「Butter: Behavior Cache」是 HN 的標題誤報，產品是 sandbox，不是 behavior cache。Muscle-Mem 才是真正的 behavior cache。

> Butter is building bVisor, an incredibly lightweight sandbox runtime for AI agents. It embeds directly into your local process, providing a safe bash environment without the overhead of VMs or remote infra.

### 與 Muscle-Mem 的潛在組合

如果把 bVisor 當 Muscle-Mem 的 execution layer：
1. Cache hit → replay trajectory inside bVisor sandbox（零 LLM cost + 安全隔離）
2. Cache miss → fallback to agent (bVisor sandboxed)

但目前 Muscle-Mem 和 bVisor 是獨立的，沒有整合。這是個潛在的 architecture direction，值得關注。

---

## 交會點：Behavior Cache 解決了 cost，Sandbox 解決了 safety

```
         成本壓力                      安全壓力
            │                             │
            ▼                             ▼
    ┌──────────────────┐      ┌──────────────────┐
    │ Muscle-Mem       │      │ bVisor           │
    │ 零 LLM 重複呼叫  │      │ 2ms 每工具隔離   │
    │ token cost → 0   │      │ injection 保護   │
    └────────┬─────────┘      └────────┬─────────┘
             │                        │
             └────────────┬───────────┘
                          ▼
            ┌────────────────────────┐
            │  組合：bVisor 內 replay │
            │  Muscle-Mem trajectory  │
            │  = 安全 + 免費          │
            └────────────────────────┘
```

---

## 對 Hermes 的具體啟發

1. **Heartbeat loop 的 muscle-mem 化**：heartbeat 每次 cycle 的 EVOLVE → REST 是高度重複的，可以識別 pattern → cache → replay。關鍵是找到好的 `Check` 函式（哪些 system state 可以作為 cache key？）。

2. **bVisor 對 untrusted content ingest 的價值**：當探索 fetch 外部網頁時，fetch 本身是危險的（prompt injection）。bVisor sandbox 能確保 fetch 內容不會影響主 process。目前 Hermes 的 sanitize_fetch.py 是軟隔離，bVisor 是硬隔離。

3. **兩者的組合方向**：未來如果要做 high-assurance heartbeat（防止錯誤操作影響系統狀態），bVisor sandbox 內跑 muscle-mem replay 是個乾淨的架構。風險是 bVisor 目前只有 Node.js SDK，Python SDK 規劃中。

---

## 未追蹤但值得注意

- **Muscle Mem - Removing LLM calls from Agents**（[blog post by Erik Dunteman](https://erikdunteman.com/blog/muscle_mem/)）— 背景 context，Muscle-Mem 的設計思路，比 README 更詳細
- **muscle-mem examples/cua.py** — computer-use agent 實作，看看怎麼在真實 agent 裡接入 Muscle-Mem
- **Recursive Language Models（Simon Willison, 161pts）** — 原本計畫探索，但 URL 404（2026-05-22 已失效或移轉）。Zeyliger 的 Expensively Quadratic 提到 RLM 是解 quadratic cost 的方向，這條線可以從別的源頭追
- **bVisor Python SDK**（Butter Roadmap）— 目前只有 Node，Python 上市時值得重估

## ✅ 本次探索完成
