---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-15-1500-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-15-1500-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-15'
confidence: medium
title: 'Two Missing Primitives: Deterministic Layer + Runtime Memory'
updated: '2026-06-15'
type: research
status: budding
---

# Two Missing Primitives: Deterministic Layer + Runtime Memory

**消化筆記**: 2026-05-15-behavior-cache-muscle-mem, 2026-05-15-arch-router-deep-dive, 2026-05-13-adk-evaluation-gap, 2026-05-13-mcp-memory-layer, 2026-05-13-mcp-gateway-orchestrator-convergence, 2026-05-13-connect-warmup

六篇看似發散的筆記（behavior cache、routing、eval、cross-tool memory、gateway convergence、cold session warmup）指向同一個深層問題：Hermes 的架構在 LLM 之下缺乏兩個 primitive——一個**確定性執行層**（deterministic layer below the LLM）和一個**運行時記憶機制**（runtime memory that learns）。不是隨手可加的功能，而是架構層級的缺失。

---

## Cross-Cutting Theme 1: 確定性層的系統性缺席

**支援筆記**: behavior-cache-muscle-mem, arch-router-deep-dive, adk-evaluation-gap, mcp-gateway-orchestrator-convergence

**信心**: high（4 篇筆記交叉驗證）

### 分析

四篇筆記各自描述一個確定性機制，彼此不認識，但它們在架構中的位置一模一樣——**LLM 下面那層**：

| 筆記 | 確定性機制 | 位置 | 角色 |
|------|-----------|------|------|
| muscle-mem | `Check` primitive（cache validation） | tool call 前 | 決定 cache hit/miss，不經 LLM |
| arch-router | 1.5B router（preference-to-model mapping） | LLM 調用前 | 決定 routing，不經主 LLM |
| mcp-gateway | Plano filter chains（HTTP/MCP proxy pipeline） | request 到 LLM 之前 | guardrails + query rewriting |
| adk-eval | pytest for non-LLM components | LLM 執行後 | 驗證輸出正確性 |

這些機制的共同點不是「它們做什麼」，而是**它們刻意繞過 LLM**。Muscle-mem 的架構設了一條鐵律：「No hidden nondeterminism — 永遠不跑 LLM 或隨機 process」。Arch-Router 的 51ms 延遲之所以能碾壓 Claude-Sonnet，就是因為它不做 general reasoning。Plano 的 filter chains 用 HTTP status code 溝通，不呼叫任何 LLM。

Hermes 目前的架構沒有這一層。Tool calling、skill selection、error handling 全部經過 LLM。Autonomic layer 的 heartbeat 是唯一例外（snapshot → scoring → select → execute 是確定性的），但那是系統健康監控，不是 task execution 層。

### 這個缺席的後果

具體的痛點散落在各筆記裡，但之前沒被串在一起：

- **CONNECT warmup** 記錄了一個 missing report（「17:00 還是沒有報告」）——沒有確定性層去驗證「cron job 輸出了嗎？輸出有效嗎？」
- **ADK eval gap** 指出「改了 scoring 公式沒人知道 REST 決策是否還是對的」——沒有確定性層去跑 regression
- **Muscle-mem 的啟發**明確說「Hermes 沒有『當前環境是否適合執行這個 skill』的機制」——沒有確定性層去做 pre-condition check

這些都是同一個 pattern 的不同症狀。

### 可行動下一步

**實作一個 minimal Check/Guard 機制，範圍極小、先用在一個地方證明價值。**

具體：在 heartbeat cron job 的結尾加一個 post-check script：

```bash
# ~/.hermes/scripts/checks/cron_output_check.sh
# 檢查上次 cron 輸出是否為空或純 error
# 失敗時寫入 heartbeat 的 stuck/anomaly channel
```

不用 framework、不用新 dependency、不用部署。只是一個 shell script + heartbeat 的 anomaly hook。做完後觀察一週：如果這個 check 抓到至少一次 silent failure（目前沒有任何機制能抓到的），就證明確定性層在 Hermes 有存在價值，再討論下一步（也許是 skill pre-condition check、也許是 eval harness）。

---

## Cross-Cutting Theme 2: 運行時記憶——靜態 Skills vs 動態 Learning

**支援筆記**: behavior-cache-muscle-mem, mcp-memory-layer, connect-warmup

**信心**: medium（3 篇筆記各自觸及，但方向不完全一致）

### 分析

Hermes 的「記憶」目前有兩種形式：

1. **靜態記憶**：skills（hand-authored markdown）、session 搜尋（log retrieval）、Obsidian vault
2. **被動記憶**：cold session warmup（偵測到閒置 session，等用戶回來才用）

兩種都是**人寫的或被動紀錄的**。沒有任何機制讓 Hermes 從自己的執行經驗中學到東西。

三篇筆記從不同角度碰到同一件事：

- **muscle-mem** 的核心價值是「runtime 學 trajectory，下次 replay」。不是工程師預先定義 cache rule，是 agent 自己跑過的 path 自動變成 cache。
- **mcp-memory-layer**（second-brain）提供跨工具的 `remember`/`recall`——但它的寫入是 agent 主動發起的（`remember` tool），不是自動的。這和 muscle-mem 的自動 trajectory recording 形成對比：一個是被動記憶（要 agent 自己記得記），一個是自動記憶（跑過就記）。
- **connect-warmup** 發現了 10 個 cold session，其中一個是「17:00 沒有報告」，但 warmup 只能做 re-engagement prompt，不能從那次失敗中學到「以後要檢查報告是否產出」。

這三篇拼在一起浮現一個模式：**Hermes 有記憶儲存（sessions、Obsidian），但沒有記憶形成機制（memory formation）**。

Muscle-mem 的 trajectory learning + second-brain 的 persistent storage = 一個 agent 可以從自己的執行歷史中自動建立 reusable knowledge。但這兩個東西目前在 Hermes 裡都不存在。

### 和 Theme 1 的交集

運行時記憶和確定性層有自然交集：trajectory replay（muscle-mem 的 cache hit）是確定性層的理想候選。如果某個 tool call sequence 被 replay，它根本不應該經過 LLM——直接執行即可。這和 Plano filter chains 的「request 一律經過，不經 LLM 判斷」是同一個哲學。

→ 兩條線如果在 Hermes 落地，可能會匯聚成同一個架構元件：**一個在 LLM 之下的 runtime layer，同時做 cache replay + guard check + output validation**。

### 可行動下一步

**在一個高頻、低變異的操作上做一次 trajectory logging 實驗，只記錄不 replay。**

挑一個候選：Hermes 每次啟動時載入 skill 的 sequence（`skill_view → read skill file → parse frontmatter`）。這個 sequence 幾乎不變。做法：

1. 在一個 session 中記錄 skill loading 的完整 tool-calling trajectory（包括 args、return values 的 signature）
2. 將 trajectory 寫成一個 JSON log（`~/.hermes/trajectories/skill_load_20260515.json`）
3. 手動比對下次 skill load 的 trajectory 是否相同

如果連續三次相同，就證明這個 trajectory 可以 cache，省下的 token 可以量化。關鍵是**只記錄不自動 replay**——先證明可行性再談工程化。

---

## 未使用但有關聯的觀察

- **Gateway convergence（筆記 5）+ Arch-Router（筆記 2）**：如果 Hermes 長出一個 gateway layer，Arch-Router 的 preference-aligned routing 和 Plano 的 filter chains 會是該 layer 的兩個自然元件。但目前 gateway 還在 SPIKE 階段，這條線先標記不展開。
- **Cold session warmup（筆記 6）+ ADK eval（筆記 3）**：warmup 裡的「17:00 沒有報告」如果當時有 eval harness（哪怕只是一個 output-nonempty check），就不會等到 5/13 heartbeat CONNECT 才被發現。這是 Theme 1 的具體案例而非新 theme。
