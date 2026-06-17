---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-16-1400-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-16-1400-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
- security
- architecture
source: multi
created: '2026-05-16'
confidence: high
title: 同一個架構原語的兩張臉：Tool Capability Profile 與 Promote-or-Discard 各自從不同入口抵達同一組答案
updated: '2026-06-15'
type: research
status: budding
---

# 同一個架構原語的兩張臉：Tool Capability Profile 與 Promote-or-Discard 各自從不同入口抵達同一組答案

**消化筆記**: 2026-05-16-sandbox-profiles-compliance-adversarial-drift

為什麼一篇講 sandbox profiles、AI 合規標準、對抗式 context drift 的筆記，最後的結論會跟 typed effects、consolidation injection defense、state lifecycle management 撞在一起？因為它們不是三個獨立主題——是同一組架構原語在三個域的投影。筆記自己看到了投影，但沒看到光源。

---

## Cross-Cutting Theme 1: Tool Capability Profile = Typed Effects 在 Gateway 層的實例化

**支援筆記**: `2026-05-16-sandbox-profiles-compliance-adversarial-drift`（新）、`2026-05-16-0530-hermes-consolidated-insight`（Typed Effects 四層收斂）、`2026-05-15-2100-hermes-consolidated-insight`（防禦姿態倒置）

**信心**: high（3 篇筆記，兩條完全獨立的探索線抵達同一個 gateway-layer mechanism）

### 分析

新筆記從 Mistle 的 sandbox profiles 出發，提出 Hermes 需要 **tool capability profile**：在 tool gateway 層定義每個 tool 能做什麼（「探索模式：只能 curl + write_file + search_files」），比 Docker 輕、比 prompt restriction 可靠。筆記稱之為「第三條路」。

但 vault 裡已經有同一條路的另一個名字。0530 consolidation 從 Vera 語言的 typed effects 出發，收斂出「在 gateway 層實作 minimal typed effects，一個 tool 一個 effect tag，先只記錄不強制」——具體建議是 `native-mcp` tool config schema 加 `effects: []string`（`fs.write`, `http.outbound`, `llm.inference`）。

這是同一個東西，只是換了名字：

| | 新筆記的 framing | 0530 insight 的 framing |
|---|---|---|
| **來源** | Mistle sandbox profiles（安全） | Vera typed effects（程式語言設計） |
| **機制** | Tool capability profile | Typed effect tag per tool |
| **實作位置** | Tool gateway layer | Tool gateway layer |
| **動機** | 限制 injection 攻擊面 | 讓 compiler/gateway 強制而非依賴 LLM 記得 |
| **建議強度** | 在 session 啟動時載入 profile | 先記錄不強制，觀測一週後升格 |

新筆記完全沒提到 typed effects。0530 insight 完全沒提到 sandbox profiles。但它們在架構圖上落在同一個座標：**gateway 層的 per-tool capability declaration**。

更有趣的是 2100 consolidation 的防禦姿態倒置論（Theme 1）：Hermes 做了後果遏制（worktree isolation），但跳過了決策完整性（Plan-Then-Execute）。Tool capability profile 在安全光譜上的位置是**決策完整性**——它在 tool call 被執行前就限制了 agent 能選的 tool set，而不是等到 tool call 的 side effect 發生後才 containment。這補上了 2100 insight 指出的防禦空白。

### 為什麼這不是新筆記已經講過的

新筆記說「tool capability profile 作為第三條路」，但沒意識到這條路已經被 typed effects 收斂論預先鋪好了。它把 tool capability profile 定位為 sandboxing 的輕量替代品，但 typed effects 收斂論證明它其實是更根本的架構原語：不是「因為 sandbox 太重所以降級成 profile」，而是「capability declaration at interface boundary」本身就是所有 sandboxing 機制背後共用的抽象。

### 可行動下一步

**合併兩條線的 action item：在 gateway tool config 加 `effects` 欄位，但命名和語意對齊 sandbox profile 需求。**

0530 insight 的原始建議（`effects: []string` + 記錄不強制）不用改。但加一個細節：effect tag 的枚舉值要能直接對應到 sandbox profile 的 capability 類別。具體：

1. 定義 effect tag 枚舉：`fs.read`、`fs.write`、`http.outbound`、`shell.exec`、`llm.inference`、`hermes.internal`
2. 在 gateway config (`native-mcp` tool schema) 加 `effects: []string`，每個 tool 標 1-3 個 tag
3. Gateway log 記錄每次 tool call 的宣告 effect vs 實際行為（先用 `search_files` 比對 tool description 文檔和 effect tag 是否一致）
4. 一週後：跑 diff report——哪些 tool 的 effect tag 跟實際能力不一致？

這不只是 typed effects 實驗，同時也是 sandbox profile 的 v0：將來可以定義 profile（如 `exploration_profile: [http.outbound, fs.write, hermes.internal]`），session 啟動時載入，gateway 拒絕對應 profile 以外的 tool call。

---

## Cross-Cutting Theme 2: WUPHF 的 Promote-or-Discard 不只是品質機制——它是 Consolidation Injection 的結構性防禦

**支援筆記**: `2026-05-16-sandbox-profiles-compliance-adversarial-drift`（新）、`2026-05-15-2100-hermes-consolidated-insight`（Consolidation 是最高 leverage 的 injection 目標）、`2026-05-16-0701-hermes-consolidated-insight`（狀態生命週期）

**信心**: high（3 篇筆記，WUPHF 的 promote-or-discard 機制和 consolidation injection defense 在結構上完全重疊）

### 分析

新筆記觀察到 WUPHF 的知識管理流程：notebook（raw agent notes）→ promoted conclusions → shared wiki。筆記據此建議 WS-004 consolidation 應該走 promote-or-discard 模式，而非 accumulate everything。

但換一個角度看同一件事：2100 consolidation 的 Theme 2 論證了 consolidation pipeline 是 Hermes 最高 leverage 的 injection 目標。結構是：

```
autonomous_notes/ (可能含 injection)
        ↓
consolidation cron (coordinator 直接讀全部 raw content)
        ↓
insight note → briefing.py → agent context (injection blast radius 擴散)
```

這是 Map-Reduce 的不安全變體。2100 insight 的解法是 Plan-Then-Execute（先看摘要選 candidate，再給 full body）。這是**輸入端的防禦**。

WUPHF 的 promote-or-discard 提供的是**輸出端的防禦**：consolidation 產出的不是「把所有筆記壓縮成更大筆記」，而是「萃取 durable conclusion，promote 到 shared context，其餘 discard」。如果 poisoned note 的 injection 沒通過 promote 門檻（例如：injection prompt 被 promote 階段判定為非 durable conclusion 而是 noise），它就不會進到 agent context。

兩端合在一起才完整：

| 防禦位置 | 機制 | 來源 |
|----------|------|------|
| **輸入端** | Plan-Then-Execute（先摘要篩選，再給 full body） | 2100 insight Theme 2 |
| **輸出端** | Promote-or-Discard（只 promote durable conclusion，其餘 discard） | 新筆記 → WUPHF |

新筆記把 promote-or-discard 定位為「品質改善」（減少記憶膨脹）。但放在 consolidation injection defense 的脈絡裡，它同時是安全機制——而且是 prompt 層安全機制做不到的那種：prompt 可以叫 LLM「不要被 injection 騙」，但 prompt 無法結構性地阻止 poisoned content 流進 agent context。Promote-or-discard 改變的是資料流結構，不是 LLM 的判斷。

0701 consolidation 的狀態生命週期論（「資訊從 raw 狀態升級到 structured 狀態、然後原筆記可以退場」）進一步支撐這個觀點：consolidation pipeline 已經在做了狀態生命週期管理，只是目前產出是「更大的筆記」而非「promoted conclusion」。把產出格式從「累積」改成「promote + archive source」就是把既有的生命週期機制對齊到安全需求。

### 可行動下一步

**改 `consolidate_memory.py` 的 prompt template，加入 promote-or-discard 結構：**

1. 在 consolidation prompt 結尾加一個新 section：`## Promote-or-Discard Decision`。要求 consolidation LLM 對每一篇被消化的筆記輸出 `PROMOTE`（核心結論進入 insight，原文可 archive）或 `DISCARD`（純資訊性、無 durable conclusion，直接 archive 不進 insight）。
2. Promoted conclusion 必須滿足：可追溯到 Hermes codebase/config/log，或至少被 2 篇以上獨立筆記交叉驗證。單篇 opinionated claim 不得 promote。
3. Insight note 的「可行動下一步」只允許來自 promoted conclusion。
4. `consolidate_memory.py --mark-fed` 時，對 DISCARD 筆記加一個 `archived: true` frontmatter 而非標記為「已消化後續仍載入」。這確保 discarded 筆記不會在下輪 consolidation 被重複處理。

這個改動同時服務兩個目標：減少記憶膨脹（品質面）+ 縮小 injection blast radius（安全面）。改動範圍：~15 行 prompt template + ~5 行 Python（archive frontmatter tag）。零新依賴。

---

## Cross-Cutting Theme 3: 對抗式 Challenge 是 Plan-Then-Execute 在知識管線的對偶

**支援筆記**: `2026-05-16-sandbox-profiles-compliance-adversarial-drift`（新）、`2026-05-15-2100-hermes-consolidated-insight`（Plan-Then-Execute 防禦 exploration 管線）、`2026-05-16-0530-hermes-consolidated-insight`（Cooperation 是 Coherence 問題）

**信心**: medium（2 篇直接支援 + 1 篇間接框架，推論成分較高）

### 分析

新筆記描述 WUPHF 的核心機制：agents 之間互相 challenge assumption 來防止 context drift——「ENG 說 blocked on design → DSG 立刻回應修正 → context 沒機會腐化」。這是**對抗式品質控制**（adversarial quality control）：主動質疑現有結論，而非被動掃描。

2100 consolidation 的 Theme 1 在 exploration 管線實作了 Plan-Then-Execute（接觸 untrusted data 前鎖住 plan）。那是**確定性防禦**（deterministic defense）：用結構性分離阻止 injection。

兩者形成對偶：

| | Plan-Then-Execute（exploration） | 對抗式 Challenge（knowledge） |
|---|---|---|
| **防禦對象** | injection 操縱 exploration direction | 錯誤假設腐化 knowledge base |
| **機制** | 結構性分離（plan phase 不碰 untrusted data） | 主動質疑（agent 之間互相 challenge assumption） |
| **時機** | tool call 前 | consolidation / knowledge promotion 時 |
| **失敗模式** | injection 讓 agent fetch 錯誤目標 | 過時/錯誤的 conclusion 未被修正 |

WUPHF 的 challenge 機制給了 consolidation 一個新維度：**不只是消化筆記，也要質疑筆記**。目前 consolidation 的 prompt 完全是 synthesis 心態——「找出連結、產出 insight」。沒有一個 section 在問：「這篇筆記的結論還成立嗎？有什麼證據可以反駁它？」

這跟 0530 consolidation 的「Cooperation 是 Coherence 問題」形成有趣的對應：WUPHF agents 之間的 challenge 維持的是 multi-agent 系統的 coherence——沒有 challenge，個別 agent 的 context drift 會讓整個系統失去 shared ground truth。Hermes 是單 agent，但 consolidation 跨時間的知識累積有同樣的 drift 風險：三週前的 autonomous note 的結論，今天還成立嗎？

### 可行動下一步

**在 consolidation prompt 加入一個 Adversarial Challenge section：**

在 synthesis phase 之後、promote-or-discard 之前，加一個新步驟：

```
## Adversarial Challenge

For each candidate insight, challenge it:
1. What would falsify this conclusion?
2. Has any autonomous_note or heartbeat log since this note's date contradicted it?
3. If this conclusion were wrong, what's the most likely alternative explanation?

If challenge #2 finds a contradiction, flag the insight with `CONTRADICTED` and do NOT promote it.
```

這個 section 強制 consolidation LLM 採取對抗姿態，而非單純的 synthesis 姿態。成本：~150 tokens 額外 prompt + 1 輪額外推理。預期產出：防止過時結論被 promote 到 agent context。

---

## 附帶：AIUC-1 Mapping 的實用價值

新筆記做的 AIUC-1 six-domain mapping（Accountability ✅、Reliability ✅、Security 🟡、Safety ❌、Data & Privacy ✅、Society ❌）本身不是 cross-cutting insight（新筆記自己做了），但它值得存檔——它提供了 heartbeat 成熟度的結構化 benchmark，後續 heartbeat EVOLVE 加 sensor 時可以直接對照 domain 填空白。特別是 Safety domain 的缺失（無 harmful output 檢測）——雖然 Hermes 是單人 agent 攻擊面不同，但如果未來開放 MCP server 給外部 tool，Safety domain 會從 ❌ 變成必須處理的 🟡。這個 mapping 應該放在 heartbeat 的 `ISSUES.md` 作為 maturity tracker。
