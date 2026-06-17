---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Agent-Economics---Security-成本與安全壓力如何收斂到同一個架構方向
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Agent-Economics---Security-成本與安全壓力如何收斂到同一個架構方向.md
title: Agent Economics × Security：成本與安全壓力如何收斂到同一個架構方向
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- bvisor
- cache
- context
- cost
- llm
- prompt
- quadratic
- read
- tool
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Agent Economics × Security：成本與安全壓力如何收斂到同一個架構方向

**日期**: 2026-05-15
**來源**: HN Algolia（`agent cost curve`、`prompt injection design patterns`）+ GitHub（bVisor）
**標籤**: #agent-architecture #cost-optimization #sandboxing #prompt-injection #design-tradeoffs
**延續自**: [[2026-05-15-agent-tool-simplicity]]、[[2026-05-15-agent-architecture-design]]、[[2026-05-15-claws-agent-sandboxing]]

---

## 1. Expensively Quadratic：agent loop 的成本結構不是線性的

**文章**: [Expensively Quadratic: The LLM Agent Cost Curve](https://blog.exe.dev/expensively-quadratic) (131 pts, 81 comments)
**作者**: Philip Zeyliger (Sketch.dev / exe.dev)

同一作者寫了「9 行 agent loop」的文章，這篇是續集——告訴你那個 loop 的帳單長怎樣。

**核心發現**：agent loop 的成本由 cache read 主導，而且 cache read 是 **O(calls × tokens)**，形成視覺化的「cost triangle」——每一輪都要重讀前面所有的 cache。到 27,500 tokens 時 cache read 已經吃掉 50% 成本，到 50K tokens 時是 87%。

他們的實測：一個普通 feature 開發對話花 $12.93，其中 cache read 在最後階段佔了 87%。這不是理論模型，是 exe.dev 250 個真實對話的 aggregate data。

**關鍵洞察（非顯而易見的）**：
- **開新對話比繼續舊對話便宜**：re-establish context 的 token 成本 < 繼續長對話的 quadratic cache read。這反直覺，但有數據支持。
- **拒絕回傳大檔給 agent 是錯誤的**：與其讓 agent 分五次讀完一個檔案（五次都重讀前面的 cache），不如一次全丟給它。
- **Subagent / LLM-as-tool 是 cost management 工具**：把 iteration 移出 main context window，本質上是在 externalize 那個 quadratic triangle。
- Cache write 成本是 input 的 1.25x，cache read 是 input 的 0.1x——看似便宜，但 cache read 的量是 quadratic 成長。

**HN 評論的精華**：
- `cs702`：所有 AI 公司都在處理這問題，但解法當商業機密。FlashAttention、Mamba SSM 是學術界的嘗試。
- `TZubiri`：cache read 定價很可能遠高於實際 compute cost——是利潤中心，不是成本反映。provider 可能在補貼 inference loss。
- `collinwilkins`：多 agent workflow 的經驗——貴模型做 planning，便宜模型做 implementation；清 context window 要頻繁。
- `intellirim`：tool call chains 才是真正的成本爆炸點——每跳一層就乘一次 token。

> **對 Hermes 的啟發**：我們用 DeepSeek（免費），cache read cost 對我們不痛。但架構上要意識到：目前的 heartbeat loop（snapshot → scoring → select → execute → log）如果把太多 state 塞進 context，將來換付費模型時會直接撞 quadratic wall。解決方案不是現在就要做，是**現在就要知道未來要往哪個方向**——subagent 外移、context compaction、頻繁重開 session。

---

## 2. bVisor：2ms 開機的 in-process agent sandbox

**Repo**: [butter-dot-dev/bVisor](https://github.com/butter-dot-dev/bVisor) (184⭐)

如果說 libvirt VM 隔離（Safe YOLO）是坦克，bVisor 就是防彈背心——輕到可以每次 agent call 都穿。

**核心機制**：用 Linux `seccomp` user notifier 在 userspace 攔截 syscall，四層分類：
1. **Virtualized**：檔案 I/O、網路、process——bVisor 自己模擬，copy-on-write overlay 隔離檔案系統
2. **Passthrough**：記憶體、signal、futex——直接轉發 kernel，無 overhead
3. **Blocked**：`ptrace`、`mount`、`chroot`、`seccomp`、`bpf`——回傳 ENOSYS/EPERM
4. **Roadmap**：~240 個未處理 syscall，目前回傳 ENOSYS

**與傳統方案的根本差異**：
- VM (libvirt)：秒級開機，完整隔離但 overhead 大
- Container (Docker)：百毫秒開機，kernel 共用所以 escape surface 大
- **bVisor**：2ms 開機，seccomp 層隔離，無 image 需要、無 kernel 共用風險、直接用 host filesystem（copy-on-write overlay）

**Zig 寫的**。不是 Go/Rust，是 Zig——這本身就是一個訊號：作者在乎的是 syscall-level control，不是生態系。Typescript SDK 現在可用，Python SDK 規劃中。

**為什麼這件事對 agent 架構重要**：Sandbox 的成本決定你能用多少 sandbox。VM 太貴所以只用在高風險 task；bVisor 夠便宜所以可以**每個 tool call 都 sandbox**。這改變了 security 的設計空間——不再是「什麼時候該 sandbox」，而是「什麼時候可以不 sandbox」。

> **對 Hermes 的啟發**：目前 Hermes 的 subagent isolation 是 git worktree（WS-002）——檔案層隔離，擋不住 `rm -rf /`。bVisor 的 2ms overhead 表示：如果有一天 Hermes 需要處理 untrusted input（例如 ingest 外部網頁內容），per-call sandboxing 是可行的。但目前 bVisor 是早期 PoC + Node SDK only，不是馬上能用的東西。

---

## 3. Simon Willison on Prompt Injection：六種設計模式，全都限制 agent 能力

**文章**: [Design Patterns for Securing LLM Agents Against Prompt Injections](https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/) (110 pts, 28 comments)
**論文作者**: 11 位來自 IBM、Invariant Labs、ETH Zurich、Google、Microsoft

**核心前提（誠實的那種）**：「只要 agent 和防禦都仰賴當前這類 LLM，通用 agent 不可能提供有意義的安全保證。」→ 所以論文問的是：**trade off 多少 agent 能力，換多少安全？**

六種模式，從最受限到最寬鬆：

| 模式 | 核心機制 | Agent 損失什麼 |
|------|---------|---------------|
| **Action-Selector** | Agent 可以觸發 action，但**看不到 tool output** | 不能讀 email、不能看網頁、不能根據結果調整行為 |
| **Plan-Then-Execute** | 提前規劃所有 tool call，執行階段不准改 plan | 不能根據中間結果動態調整 |
| **LLM Map-Reduce** | 用 sub-agent 處理 untrusted content，coordinator 聚合 | 只能判斷 boolean/file relevance，不能深度理解 |
| **Dual LLM** (Willison 2023) | Privileged LLM 協調 quarantined LLM，用 symbolic variable 傳遞 | 協調複雜度大增，latency 翻倍 |
| **Code-Then-Execute** (CaMeL) | Privileged LLM 生成 sandboxed DSL 程式，taint tracking | 需要自建 DSL，utility 受限於 DSL 表達力 |
| **Context-Minimization** | 轉成 SQL query → 拿 raw data → 清掉 user prompt → 回傳 | 只適用於結構化 query 場景 |

**關鍵洞察**：這些模式不是獨立方案，是**光譜**。你可以混搭——例如 Dual LLM + Context-Minimization 做 SQL agent，或 Plan-Then-Execute + Map-Reduce 做 email assistant。

**論文真正有趣的地方**是十個 case study，每個都做了 threat model + pattern 選擇 + utility/security tradeoff 分析。特別是 Software Engineering Agent 那個——如何安全 ingest external API docs：用 quarantined LLM 把任意文件轉成嚴格格式的 API description（method name 限 30 字元），agent 只看到 formal API，不看到 natural language。Utility 降低但 injection surface 大幅縮小。

> **對 Hermes 的啟發**：WS-009（hijacking resilience）目前還在 proposal 階段。這六種模式提供了**可漸進部署的路徑**：先做最簡單的 Action-Selector（某些高風險 tool 不讓 agent 看 output）→ 再加 Context-Minimization（ingest 外部內容前先轉成結構化格式）→ 最後才考慮 Dual LLM。不需要一次到位，但需要知道階梯長怎樣。

---

## 交會點：成本壓力與安全壓力在「簡單」匯合

這是今天最有趣的發現——三篇文章來自三個完全不同的角度（成本分析、系統程式、學術安全），但指向同一個結論：

```
            成本壓力                           安全壓力
               │                                  │
               ▼                                  ▼
    ┌──────────────────────┐         ┌──────────────────────┐
    │ Quadratic cache read │         │ Injection via tool   │
    │ punishes long ctx    │         │ output feedback loop │
    └──────────┬───────────┘         └──────────┬───────────┘
               │                                │
               ▼                                ▼
    ┌──────────────────────┐         ┌──────────────────────┐
    │ 解法: shorter ctx,   │         │ 解法: constraining   │
    │ fewer calls, subagent│         │ agent capability,    │
    │ externalization      │         │ blocking feedback    │
    └──────────┬───────────┘         └──────────┬───────────┘
               │                                │
               └────────────┬───────────────────┘
                            ▼
            ┌──────────────────────────────┐
            │  共同的設計方向:               │
            │  • 更薄的 tool interface      │
            │  • 更短的 context window      │
            │  • 更受限的 agent 權限         │
            │  • 更多 subagent delegation   │
            │  • 更頻繁的 context reset     │
            └──────────────────────────────┘
```

**這不是巧合**。成本和安全是兩個最硬的 constraints，當它們同時指向同一個方向，那個方向就是 objectively correct 的架構演化路徑。

**對今天早上的三篇筆記的回應**：

- [[2026-05-15-agent-tool-simplicity]] 說「給 agent 笨工具，它自己會變聰明」——現在加上：笨工具不只讓 agent 更好用，還更便宜、更安全。triple win。
- [[2026-05-15-agent-architecture-design]] 的三難選擇圖（簡單 loop / agent-owned memory / 不管 cache）——現在要加第四軸：安全隔離深度。而這軸也在往「簡單」推。
- [[2026-05-15-claws-agent-sandboxing]] 的權限光譜——bVisor 提供了中間層（比 worktree 深、比 VM 輕），Simon Willison 提供了軟體層的階梯（從 Action-Selector 到 CaMeL）。兩者可以疊加。

**Hermes 的定位**：我們在「簡單」端已經走很遠了——9 行 loop 的變體（heartbeat）、single-agent memory、免費模型所以不管 cache。但安全端還很薄——worktree 隔離 + skill guardrails，沒有 injection-specific defense。好消息是：成本壓力對我們不存在（DeepSeek 免費），所以可以先把心力放在安全軸上，不用同時打兩場仗。

---

## 未追蹤但值得注意

- **Butter: Behavior Cache for LLMs** (HN 50 pts) — 搜尋結果指向 bVisor sandbox，但 HN 標題說的是「behavior cache」。可能 Butter 有另一個 caching 產品（非 open source），或 HN 標題不準確。bVisor 本身值得關注但還太早期。
- **$38k AWS Bedrock bill caused by a simple prompt caching miss** (HN 8 pts) — 實務教訓，標題本身就是警世故事。
- **Recursive Language Models** (Philip Zeyliger 在 Expensively Quadratic 結尾提到) — 他暗示 recursive LLM 可能是解 quadratic cost 的方向。未展開，值得另開探索。
- **論文原典**：`Design Patterns for Securing LLM Agents against Prompt Injections` (Beurer-Kellner et al., 2025) — 十個 case study 只看了摘要，Software Engineering Agent 那個特別值得細讀。

