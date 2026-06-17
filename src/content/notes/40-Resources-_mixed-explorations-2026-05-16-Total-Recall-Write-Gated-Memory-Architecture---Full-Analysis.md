---
_slug: 40-Resources-_mixed-explorations-2026-05-16-Total-Recall-Write-Gated-Memory-Architecture---Full-Analysis
_vault_path: 40-Resources/_mixed/explorations/2026-05-16-Total-Recall-Write-Gated-Memory-Architecture---Full-Analysis.md
title: Total Recall Write-Gated Memory Architecture — Full Analysis
date: 2026-05-16
type: explorations
tags:
- explorations
- auto-ingested
fingerprint:
- agent
- channel
- gate
- memory
- recall
- session
- shared
- total
- wiki
- wuphf
created: '2026-05-20'
updated: '2026-06-15'
status: budding
---

# Total Recall Write-Gated Memory Architecture — Full Analysis

**日期**: 2026-05-16 11:31 CST  
**來源**: 
- https://github.com/davegoldblatt/total-recall — `docs-architecture.md`, `docs-spec.md`
- https://github.com/nex-crm/wuphf — `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `docs/agents/INSTRUCTIONS.md`, `DESIGN-WIKI.md`
**狀態**: analyzed, ready for design discussion

---

## 1. 總覽

兩個來自不同作者、不同設計哲學的記憶架構專案，但核心問題一致：**AI agent 如何在跨 session 維持有意義的記憶，而不讓記憶變成雜訊抽屜**。

| 面向 | Total Recall | WUPHF |
|------|-------------|-------|
| 主要作者 | Dave Goldblatt（個人） | nex-crm（團隊，MIT 開源） |
| 目標平台 | Claude Code plugin | 獨立 multi-agent runtime |
| 記憶模型 | 三層 + 三道閘門 | 個人筆記本 → 共享 wiki |
| 核心機制 | Write Gate（寫入前檢查） | Promotion（筆記本 → wiki 晉升） |
| Agent 間挑戰 | 無（單 agent 設計） | Shared channel + @mention（prompt 驅動） |
| 抗 drift | Trust Gate（verify dates） | Fresh session per turn |
| 子 agent 隔離 | 明確禁止寫入核心記憶 | Per-agent worktree 隔離 |

---

## 2. Total Recall 的寫入閘門架構（核心）

### 2.1 三層記憶

```
Tier 0: Conversation Cache (session transcript — ephemeral)
   │
   ▼ WRITE GATE ("does this change future behavior?")
   │
Tier 1: Daily Log (memory/YYYY-MM-DD.md)
   │  Raw capture. 30-day retention.
   ▼ PROMOTION ("will this matter in 30 days?")
   │
Tier 2: Registers (memory/registers/*.md)
   │  Structured domain knowledge. Loaded on-demand.
   ▼ DISTILLATION ("essential for every session?")
   │
Tier 3: Working Memory (memory/MEMORY.md)
   │  ~1500 words. Loaded EVERY session.
   ▼ EXPIRY
   │
Archive (memory/archive/)
   Searchable, never auto-loaded.
```

### 2.2 三道閘門（這是精華）

**Gate 1: Write Gate** — 寫入前問："這會改變未來的行為嗎？"
五個通過條件（任一成立即寫入）：
1. 改變未來行為（偏好、邊界、重複失敗模式）
2. 有後果的承諾（死線、跟進、交付物）
3. 有理由的決策（為什麼選 X 不選 Y）
4. 穩定的、會再次用到的資訊
5. 人類明確說「記住這個」

不寫的範例：
- 一次性格式請求（「幫我用條列」）
- 確認語（「謝謝，看起來不錯」）
- 剛處理完的檔案內容（已經在磁碟上）
- 除錯細節

**Gate 2: Trust Gate** — 每個持久性聲明帶：
- `confidence`: high / med / low
- `last_verified`: YYYY-MM-DD
- `evidence`: 來源指針

矛盾處理：不覆蓋，標記舊的為 `[superseded]`，寫新的，保留變遷歷史。

**Gate 3: Correction Gate** — 人類修正觸發四次寫入：
1. Daily log（永遠）
2. Register（如果是領域知識）
3. MEMORY.md（如果是行為改變）
4. 確保跨 session 持久

### 2.3 Session Boundary 問題

Total Recall 明確指出的關鍵設計挑戰：
- **Isolated cron jobs 沒有 conversation history**。不能依賴「上次對話中授權過」。
- 解法：**approval artifacts on disk** — 把授權寫進 runbook 檔案，讓孤立 session 讀取。
- Pre-compaction flush：在 context 被壓縮前，掃描未儲存的決策、承諾、修正，寫入 daily log。

### 2.4 失敗模式（與我們直接相關）

| 失敗模式 | 症狀 | 與我們的關聯 |
|---------|------|------------|
| **Filing Cabinet Intelligence** | 整理得很好，對決策無用 | WS-004 的 promote-or-discard 必須過濾這個 |
| **Fossilized Wrongness** | agent 自信地用過時資訊 | 我們的 drift detection 要抓的正是這個 |
| **Correction Decay** | 同一件事被反覆修正 | 我們的心跳應檢測「同類型修正是否反覆出現」 |
| **Context Pollution** | MEMORY.md >3000 字 | 我們的 consolidate 輸出不能超過 1500 字 |
| **Summary Instead of Synthesis** | 壓縮後只是短版原文，沒洞察 | 我們的 promote pipeline 必須產出「pattern + 行為改變建議」 |

---

## 3. WUPHF 的 Agent 挑戰機制

### 3.1 「互相吐槽」的本質

原始線索說 WUPHF agents "bully each other into staying on track"。經原始碼驗證：

**這不是硬編碼機制，是架構設計促成的社會動態。**

關鍵架構元素：
1. **Shared channel (#general)** — 所有 agent 看到所有訊息（collaborative mode 預設）
2. **@mention routing** — agent 可以指名挑戰其他 agent
3. **Fresh session per turn** — 每個 agent 回合從零開始，沒有累積 context
4. **Per-agent notebook → promotion → shared wiki** — 個人觀察晉升為團隊事實後，所有人可見

挑戰流程：
```
Agent A 在 #general 宣稱某事
Agent B 的 prompt 包含 shared wiki context
Agent B 發現矛盾 → @Agent A: "不對，wiki 說 X，你為什麼說 Y？"
Agent A 被喚醒 → 回應（修正自己 or 反駁）
```

**這個挑戰不是硬編碼規則，是 prompt 裡的行為指引 + shared channel 可見性 + @mention 路由的組合。**

### 3.2 與我們 drift detection 的關聯

WUPHF 的抗 drift 策略是多層的：
- **Session 層**：fresh session per turn（沒有長 session 中的 drift）
- **記憶層**：notebook → wiki promotion（個人觀察需晉升才成為共享事實）
- **社交層**：shared channel 讓 agent 互相看見並質疑

我們的 system 目前沒有 shared channel（agents 不互相對話），但我們有 **heartbeat drift detection**。WUPHF 的做法啟發：我們可以在 drift detection 報告中加入「如果 agent X 和 agent Y 的記錄矛盾，生成一個針對性挑戰 prompt」。

### 3.3 Sub-agent Triangulation（代碼審查用）

WUPHF 的 sub-agent dispatch 合約有一個值得借鑑的模式：
```
1. Spawn 3-5 sub-agents，每個用不同 lens（security, perf, API, SRE, architecture）
2. 2+ agent 獨立標記的 finding → high confidence
3. 單一 agent 標記 → 驗證後再修
4. 直接衝突 → 升級到人類審查
```

這可以直接用於我們的 memory verification：**heartbeat 維護時，spawn 多個 verification agent 檢查同一批 register claims，用 triangulation 判斷哪些是真的 stale、哪些是單一 agent 的誤判。**

---

## 4. 可借鑑的具體設計

### 4.1 立即可用（低風險）

| 設計 | 來源 | 如何用在 Hermes |
|------|------|---------------|
| Write Gate 五條件 | Total Recall | 加入 WS-004 promote-or-discard 邏輯 — 每個 consolidate candidate 必須通過至少一個條件 |
| `last_verified` 欄位 | Total Recall | 所有 register entry 強制帶 `last_verified`；heartbeat 週期檢查 >30 天的 |
| Correction Gate 多寫 | Total Recall | 當人類修正時，一次寫入 daily log + register + MEMORY.md |
| Sub-agent 只能寫 daily log | Total Recall | 限制 sub-agent 的 write 權限，產出進 staging area |
| Approval artifacts | Total Recall | Cron job 執行外部動作前，必須讀取磁碟上的授權 artifact |

### 4.2 需要調適（中風險）

| 設計 | 來源 | 調適方案 |
|------|------|---------|
| Shared channel agent challenge | WUPHF | 我們的 agents 不共用 channel。替代：heartbeat drift report 中生成針對性挑戰 prompt，由 main session 執行 |
| Triangulation verification | WUPHF | 用現有 sub-agent 基礎設施，生成 3 個不同 lens 的 verify agent，交叉驗證 register claims |
| Promotion flow（notebook → wiki） | WUPHF | 我們的 consolidate pipeline 可以分兩階段：daily → register candidate（自動）、register candidate → register（需 review） |
| Pre-compaction flush | Total Recall | 我們的 session 沒有 compaction 概念（cron job）。替代：每個 cron job 結束時 flush 未儲存發現 |

### 4.3 暫緩（高風險或需要基礎設施）

| 設計 | 原因 |
|------|------|
| Full role separation（Operator/Reader/Librarian） | 我們目前是單 agent，不需要 |
| WUPHF 的 shared channel | 需要多 agent runtime，與現有架構衝突 |
| Quarterly archive distillation | 我們還沒有足夠的歷史資料 |

---

## 5. 行動建議

### 立即（本回合）
- [x] 完整分析完成，寫入知識庫 ✅

### 短期（下一個 heartbeat）
- [ ] 將 Write Gate 五條件整合進 `WS-004` consolidate 邏輯
- [ ] 為所有 register 格式加上 `last_verified` 欄位規範
- [ ] 在 heartbeat drift detection 中加入「>30 天未驗證的 claims」

### 中期（下週）
- [ ] 設計 triangulation verification：heartbeat 維護時 spawn 3 個 verify agent
- [ ] 設計 pre-compaction flush 等效機制（cron job 結束時 flush）
- [ ] 評估是否需要 approval artifacts for isolated cron

### 長期
- [ ] 評估 WUPHF shared channel 模式是否適合作為 Hermes 的「agent 間校對層」
- [ ] 積累足夠歷史資料後，設計 quarterly archive distillation

---

## 6. 參考

- Total Recall architecture: `docs-architecture.md` (full text fetched 2026-05-16)
- Total Recall spec: `docs-spec.md` (full text fetched 2026-05-16)
- WUPHF README: `README.md` (full text fetched 2026-05-16)
- WUPHF ARCHITECTURE: `ARCHITECTURE.md` (full text fetched 2026-05-16)
- WUPHF Agent Instructions: `docs/agents/INSTRUCTIONS.md` (full text fetched 2026-05-16)
- WUPHF Wiki Design: `DESIGN-WIKI.md` (full text fetched 2026-05-16)

