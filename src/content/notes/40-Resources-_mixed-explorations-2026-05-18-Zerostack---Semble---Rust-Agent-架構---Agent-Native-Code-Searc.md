---
_slug: 40-Resources-_mixed-explorations-2026-05-18-Zerostack---Semble---Rust-Agent-架構---Agent-Native-Code-Searc
_vault_path: 40-Resources/_mixed/explorations/2026-05-18-Zerostack---Semble---Rust-Agent-架構---Agent-Native-Code-Searc.md
title: Zerostack & Semble — Rust Agent 架構 + Agent-Native Code Search
date: 2026-05-18
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- code
- config
- hermes
- loop
- prompt
- search
- semble
- token
- zerostack
created: '2026-05-18'
updated: '2026-06-15'
status: budding
---

# Zerostack & Semble — Rust Agent 架構 + Agent-Native Code Search

**延續自**: 無（全新探索）

## Zerostack — Unix-inspired coding agent in pure Rust (522 pts HN)

**來源**: HN [48164287](https://news.ycombinator.com/item?id=48164287), GitHub [gi-dellav/zerostack](https://github.com/gi-dellav/zerostack), crates.io

### Per-source insight

Zerostack 宣稱是最輕量的 coding agent：7k LoC、8.9MB binary、8MB RAM idle、12MB working。對比 opencode 的 300MB，差 25 倍。

**架構特色**：

1. **Prompt system 取代 Skills**：內建 10 種 system prompt mode（`code`/`plan`/`review`/`debug`/`ask`/`brainstorm`/`frontend-design`/`review-security`/`simplify`/`write-prompt`），用 `/prompt` runtime 切換。這和 Claude Code skills 不同——skills 是疊加 instructions，prompt mode 是整份替換。自訂 prompt 放在 `$XDG_CONFIG_HOME/zerostack/prompts/`，markdown 檔案直接就是 system prompt。

2. **Permission system（四級）**：restrictive → standard → accept-all → yolo。支援 per-tool glob patterns（例如 `write **.rs` auto-approve，其他 write 詢問）。Session allowlist 記住本次 session 內已批准的決策。**Doom-loop detection**：3+ 次相同 tool call → warning/denial（防止 runaway agent）。

3. **Ralph Wiggum loops**：`/loop "Implement auth"` → agent 反覆讀 task、選 plan item、實作、跑測試、更新 plan、循環。支援 headless CLI（`--loop --loop-prompt "..." --loop-run "cargo test"`）。這和 Hermes 的 heartbeat 自我維護循環是同一血統，但作用在 task execution 層而非系統健康層。

4. **Git worktrees 內建**：`/worktree feature-x` 建立 worktree + 切換，`/wt-merge` 合併 + push + 清理。比 Hermes 的 `worktree-subagent-isolation` skill 更 seamless——是原生 slash command 而非外部腳本。

5. **Bubblewrap sandbox**：`--sandbox` flag 把每個 bash command 包在 bubblewrap 隔離環境內。Arch 上只需 `pacman -S bubblewrap`。這和我們 sandboxing 研究中的 L3 容器隔離對齊。

6. **Compile-time feature flags**：MCP、loop、git-worktree、ACP 全是 optional features。Hermes 沒有等效機制——所有能力常駐，無法按需裁剪。

7. **ACP（Agent Communication Protocol）**：JSON-RPC based，讓 Zed 等編輯器可以連接 zerostack 作為 coding agent backend。editor 整合的標準化嘗試。

### Hermes 啟發

- **Doom-loop detection（3+ 相同 tool call）**是 heartbeat 可以直接借鏡的確定性 sensor。不需要 LLM 判斷——純 counter-based，false positive rate 極低。heartbeat EVOLVE 已有 `check_workspace_sync()` 和 `plan_drift`，但沒有 loop detection。這可以是一個新的 EVOLVE step。
- **Prompt system vs Skills** 的設計取捨值得思考：Hermes 用 skills 疊加（128 skills），Zerostack 用 prompt 替換（10 modes）。前者彈性高但 token 成本大（cache hit 受影響），後者精簡但覆蓋面窄。不是哪個比較好——是不同 scaling 策略。
- **Feature flags** 的概念對 Hermes 有意義，但實作難度高（Python 不像 Rust 有 compile-time）。替代方案：run-time feature toggles（config flag），但和 compile-time 的 binary size / RAM 優化不同路線。
- Zerostack 的 **8MB RAM idle** 是 Rust 的先天優勢，Python agent 做不到。但 Hermes 的優勢不在資源效率，在自主性（heartbeat + exploration + self-evolve）——這是 Zerostack 完全沒有的層次。

---

## Semble — Code search for agents (98% fewer tokens than grep)

**來源**: HN [48169874](https://news.ycombinator.com/item?id=48169874), GitHub [MinishLab/semble](https://github.com/MinishLab/semble), MIT

### Per-source insight

Semble 解決一個精準問題：agent 用 grep+read 找程式碼極度浪費 token。技術方案：

1. **雙檢索 + RRF 融合**：
   - Model2Vec static embeddings（potion-code-16M，16M params）→ semantic similarity
   - BM25 → lexical matches（identifiers, API names）
   - Reciprocal Rank Fusion 合併兩者

2. **Code-aware reranking signals**（五層）：
   - Adaptive weighting：symbol-like queries 加重 lexical，natural language queries 平衡
   - Definition boosts：`class`/`def`/`func` 宣告排在 references 之上
   - Identifier stems：query token 的 stem 比對 chunk 內的 identifier stem
   - File coherence：同檔案多個 chunks 命中 → 檔案級 boost
   - Noise penalties：test files / compat shims / examples / `.d.ts` stubs 降級

3. **性能**：263ms index、1.5ms query、NDCG@10 = 0.854（99% of 137M-param CodeRankEmbed Hybrid，但 index 快 218x）。

4. **三種整合模式**：MCP server（Claude Code/Cursor/Codex/OpenCode）、bash 整合（`AGENTS.md` snippet）、Python API。

5. **`find_related`**：給定 file+line，回傳語意相近的 chunks。這是 rg/grep 完全做不到的——lexical search 沒有 "find similar code" 的能力。

6. **Token savings 追蹤**：`semble savings` 顯示節省的 token 數（總字元數差 / 4 = conservative estimate）。存在 `~/.semble/savings.jsonl`。

7. **From MinishLab**：和 Model2Vec 同一團隊。potion-code-16M 是專為 code 訓練的 static embedding model。這種「自己做底層模型，再做上層工具」的 vertical integration 少見。

### Hermes 啟發

- **直接實用價值最高**：Hermes agent 每天用 `search_files`（rg backend）數千次。Semble 可作為 MCP tool 加入，對 token 使用有立即可量化的改善。測試路徑：`pip install semble` → MCP config → 跑幾個現有 search_files call 對比。
- **`find_related` 補了 Hermes 的工具盲點**：Hermes 的 search_files 是純 lexical（regex），沒有 semantic similarity。當 agent 想找「和這段 code 類似的實作」時只能靠經驗猜 regex pattern。`find_related` 解決這個問題。
- **BM25 + static embeddings 的架構值得學習**：不需要 API key、不需要 GPU、不需要外部服務。和 Hermes 的 self-contained 設計哲學一致。如果以後要自建 agent-native code search，這是正確架構（不是 Pinecone/向量資料庫的 overkill 路線）。
- **Token savings 追蹤是聰明的 UX**：讓 agent 和使用者都能看到節省了多少 token。Hermes 的 heartbeat 已經有 cost tracking，但沒有 per-tool efficiency tracking。
- **potion-code-16M 的 vertical integration**：MinishLab 做 Model2Vec → 做 Semble。控制底層模型讓上層工具的品質和性能都可預測。這是 Hermes 沒有的優勢——我們依賴 DeepSeek API，沒有自己的 embedding model。

---

## 跨文章 Synthesis

兩篇看似無關——一個是 coding agent 架構，一個是 code search 工具——但有三條共同線索：

| | Zerostack | Semble | Hermes 對標 |
|---|---|---|---|
| **設計哲學** | Unix-inspired（do one thing well） | Single-purpose（只做 code search） | Multi-purpose（heartbeat + exploration + comms + code） |
| **資源效率** | 8MB RAM, 8.9MB binary | 263ms index, CPU-only | Python venv, ~300MB RAM (估) |
| **整合模式** | Native CLI + MCP + ACP | MCP + bash + Python API | Native tools + skills + MCP gateway |
| **自主性** | Loops (task execution) | None | Heartbeat (system health + exploration) |
| **權限控制** | 4-level + per-tool glob + session allowlist | N/A | Config-level toolset restriction（cron `enabled_toolsets`） |

**Talos 視角的收穫**：

1. **Doom-loop detection 是最容易實作的 quick win**：3+ 相同 tool call → warning/denial。這是確定性 counter，不需要 LLM。可以加到 heartbeat EVOLVE 或直接成為新的 cron sensor。提案價值：低風險、高信號、立即部署。

2. **Semble 是立即可測試的外部工具**：`pip install semble` → MCP config → 跑對比。不需要架構變更。如果 token savings 顯著（預期 80-95% on code search tasks），可能成為 Hermes 的標準工具。

3. **Permission system 梯度是 Talos governance 的 concrete reference**：Zerostack 的四級 + per-tool glob + session allowlist + doom-loop detection 完整覆蓋了我們在 governance blueprint 裡討論的所有控制面。不是「要不要做」的問題——是 reference implementation 已經存在，可以直接對標。

4. **Feature flags 概念可轉化為 runtime toggles**：Hermes 不需要 compile-time features，但可以考慮 config-level 的能力開關（例如：`features.exploration = false` 關閉自主探索，`features.loop = false` 關閉 delegate_task 循環）。這是未來架構方向，不需要現在實作。

---

## ⏳ 未追蹤

- https://github.com/gi-dellav/zerostack/tree/main/src — Zerostack source code，看 doom-loop detection 的具體實作（counter-based or pattern-based?）
- https://github.com/gi-dellav/zerostack/blob/main/CONFIG.md — Zerostack config schema，看 permission rules 的完整語法
- https://github.com/MinishLab/semble/tree/main/benchmarks — Semble benchmark methodology，看 token efficiency 的計算方法細節
- Semble 在 Hermes 上的實際 token savings 測試（安裝 → MCP config → A/B 對比 search_files vs semble search）

## ✅ 本次探索完成

