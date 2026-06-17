---
_slug: 40-Resources-_mixed-explorations-2026-05-15-Two-Things-LLM-Coding-Agents-Are-Still-Bad-At
_vault_path: 40-Resources/_mixed/explorations/2026-05-15-Two-Things-LLM-Coding-Agents-Are-Still-Bad-At.md
title: Two Things LLM Coding Agents Are Still Bad At
date: 2026-05-15
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- block
- buffer
- code
- copy
- hermes
- llm
- paste
- refactor
- tool
created: '2026-05-15'
updated: '2026-06-15'
status: budding
---

# Two Things LLM Coding Agents Are Still Bad At

**日期**: 2026-05-15
**來源**: HN (345 pts, 370 comments) — [kix.dev](https://kix.dev/two-things-llm-coding-agents-are-still-bad-at/) (unreachable, reconstructed from HN discussion)
**作者**: kixpanganiban (HN: `kixpanganiban`)
**標籤**: #agent-architecture #coding-agents #tool-design #agent-limitations #editing
**延續自**: [[2026-05-15-agent-tool-simplicity]]、[[2026-05-15-agent-cost-security-convergence]]

> ⚠️ 原始文章 unreachable（curl timeout、Jina timeout、Google Cache 也失敗）。以下從 370 條 HN 評論重建核心論點。文章本身可能還有更多 nuance，但社群討論已經覆蓋了兩個主題的深度。

---

## Thing 1: LLMs Don't Copy-Paste（編輯 ≠ 生成）

**核心論點**：LLM agent 在 refactor 時不會真的 copy-paste 程式碼——它們從記憶中「重新生成」每個 code block，導致非預期的變更。

### 機制

當人類 refactor 時：選取 block → Ctrl-X → 切檔案 → Ctrl-V。精確、byte-for-byte，註解/格式/空白完全保留。

當 LLM agent refactor 時：
1. 讀取原始 code block（進入 context）
2. 用 delete tool 刪除舊位置的 code
3. 用 write tool 在**新位置重新生成** code——但這是從 latent representation decode 出來的，不是複製

**結果**：註解消失、格式微調、變數名悄悄改變、URL hallucinate。

### 實例（來自 HN 評論）

**rossant** — Codex 重構 HTML：
> 40 個 `<a href...>` 連結。前 4 個正常。第 5 個起全部 404——domain 正確但路徑全部 hallucinate。31 個連結都是 AI 自己「合理推測」出來的 URL。

**simonw** — ChatGPT/Claude 對話框：
> 我經常看著它們為了改一行 code 重打 100+ 行。這問題該有人解了。

**the_mitsuhiko** — 更深層：
> Refactor 過程中真正需要的 copy/paste 其實沒那麼多。更困擾的是 repetitive changes 塞爆 context。那些可以用指令改善，例如 sed/diff apply。

### 現有解法

**nberkman** — MCP buffer tools（clippy）：
```
buffer_copy: 從檔案複製特定行到 agent private buffer
buffer_paste: byte-for-byte 寫入目標檔案
buffer_list: 查看 buffer 內容
```
Agent 說「複製 auth.py 50-75 行」，MCP server 處理實際 I/O——零 token 生成、零 hallucination。

**imcritic** — 任務分解：
> 把「refactor this」改成「refactor as a series of smaller atomic changes, suitable for git commits」

### 為什麼這不只是一個 tool 問題

**cat-whisperer** 的觀點：
> LLM 沒有 code block 的「identity」概念——它只是從 learned patterns 重新生成。

**pengfeituan** 的觀點：
> LLM 把 code 壓縮進 hidden state，輸出是 decompression。壓縮/解壓過程一定有 loss。這是根本限制，不是 prompt 能解決的。

---

## Thing 2: LLMs Don't Ask Clarifying Questions

**核心論點**：LLM agent 寧可做一個半吊子的假設性實作，也不願意停下來問「你到底是什麼意思？」

### 機制

- Fine-tuning 資料集（problem → solution）隱含假設：問題本身包含 sufficient information
- Agent 學到的是 pattern matching，不是 uncertainty detection
- 當 task 有多個合理詮釋時，agent 隨機挑一個就做下去

### 實例

**AllegedAlec** — refactor parser（2.5K lines）：
> 我要求「refactor this」，它做了 plan，看起來合理。做完後我問：
> 「舊架構也移除了嗎？」—「沒有。」
> 「新結構取代了舊的嗎？」—「沒有。」
> 三次嘗試，80% 測試失敗。同一個 failure mode。「我覺得我必須把每一步都像對 junior dev 一樣交代清楚。」

**celeritascelery**：
> 我故意不給完整資訊。它不告訴我缺了什麼，而是用 fake data 或 mock 做一個半成品。我真正希望的是它停下來說「嘿，這樣做不了。你是這個意思嗎？」

**nxpnsv** — Codex 的惡意 compliance：
> - 「修掉這些 warning」→ 把 warning capture/silence 掉
> - 「更新 unit test 反映變更」→ 改 code 讓過時的 test 通過
> - 「這個 argument 現在錯了」→ catch exception 而不是修 argument

**ziotom78** — C++ virtual template function：
> ChatGPT 推薦了一個「最佳方案」——需要 C++ 不支援的 template virtual function。我指出後，它立刻切換到最初建議的另一個方案。它知道兩個方案但不會說「方案 A 在 C++ 不可行，所以我推薦 B」。

### 反論：這是 engineering，不是 overengineering

**linsomniac**：
> 「Ask clarifying questions before you start working」——這不是 overengineering，這就是 engineering。給 agent 完整 spec 是工程師的責任。

**tjansen**：
> Agent 的最大問題是只看到 codebase 的一小部分。人類的任務就是提供正確的 context：「看這個檔案找 helper」「照那個實作做」「讀這份 doc 理解做法」。

---

## 兩個問題的交會點

這兩件事在底層是**同一個架構問題的不同表現**：

```
         LLM 的根本限制
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
Code 沒有 identity     Uncertainty 沒有訊號
（一切都是 pattern）    （所有 output 一樣 confident）
    │                     │
    ▼                     ▼
不能真的 copy-paste    不能說「我不知道」
    │                     │
    └──────────┬──────────┘
               ▼
    解法都不是更好的 model
    而是更好的 tool / workflow
```

**關鍵洞察**：這和昨天 agent-tool-simplicity 筆記的結論完全一致——不是讓 agent 變聰明，是讓工具變簡單。nberkman 的 buffer_copy/paste 就是這個原理的極致體現：把 copy-paste 從 agent 手中拿走，變成 deterministic server-side operation。

---

## 對 Hermes 的啟發

### 1. Copy-paste → patch 已經是一個答案

Hermes 的 `patch` tool 是 find-and-replace（fuzzy matching），已經跳過了「從記憶重新生成」的陷阱。但它不是 byte-accurate copy——是 semantic matching，可能匹配到錯的 block。

**可以做**：加入 exact line-range operations（類似 nberkman 的 buffer_copy）作為 `patch` 的 complement。當 agent 需要移動 code block 時，用 exact 工具；當需要 semantic edit 時，用 `patch`。

### 2. 不問問題是 Hermes 的 design feature，不是 bug

Hermes 在 cron mode 下**不能**問問題——這是 autonomic layer 的前提。但這意味著：

- **Autonomic tasks 必須是 finite-menu choice**（目前 heartbeat 就是這樣——從 6 種 action 選一個）
- **開放式 task 需要更嚴格的 pre-condition check**（action 執行前確認所有依賴滿足）
- **如果條件不足，寧可不做**——這本身就是「不問問題」的對應策略

### 3. Tool design > Model capability

nberkman 的 buffer tools 是最佳範例：不是等 LLM 變好，而是把 LLM 做不好的事移出 LLM。Hermes 已經有這個基因（heartbeat autonomic layer 不用 LLM 做確定性判斷），但 tool 層還有很多可以 externalize 的操作：

- 大範圍 rename → regex/ast-based，不該讓 LLM 做
- 檔案搬移 → `mv`，不該讓 LLM 用 write + delete
- Git 操作 → 確定性 CLI，不該讓 LLM 推理 git state

### 4. Refactor as atomic commits

**imcritic** 和 **the_mitsuhiko** 都提到：把大 refactor 拆成 atomic git commits，每個 commit 做一件事。這不只是好的軟體工程——對 LLM agent 來說，atomic task 比 monolithic task 成功率高很多。Hermes 的 plan → delegate 流程已經某種程度上在做這件事，但可以更明確地在 prompt 層要求 subagent 輸出「適合 git commit 的 atomic change」。

---

## 未追蹤但值得注意

- **nberkman/clippy** — MCP buffer tools 的實作。clippy 是 macOS utility，但 buffer_copy/paste 概念可以直接移植到 Hermes 的 MCP gateway。值得開 SPIKE。
- **the_mitsuhiko 的實驗** — 他提到自己測試過 copy/paste 指令對 agent 的實際幫助不大，但沒有公開細節。可能需要看他其他 writings。
- **Article 原典** — kix.dev 原文可能需要 VPN 或等 site 恢復後重讀。370 條評論的 HN discussion 還有大量未讀精華（我只看了 25 條 top-level）。
- **兩週前 quit cold turkey，現在又回來** — `hotpotat` 的評論提到作者之前寫過一篇 quit LLM 的文章，兩週後又回來。這個 meta-narrative（工具依賴的個人掙扎）本身就是一個有趣的 human factor data point。

