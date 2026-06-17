---
_slug: 40-Resources-_mixed-research-insights-2026-05-2026-05-16-0530-hermes-consolidated-insight
_vault_path: 40-Resources/_mixed/research/insights/2026-05/2026-05-16-0530-hermes-consolidated-insight.md
tags:
- consolidation
- synthesis
source: multi
created: '2026-05-16'
confidence: high
title: Typed Effects 的四層收斂 × Cooperation 是 Coherence 問題
updated: '2026-06-15'
type: research
status: budding
---

# Typed Effects 的四層收斂 × Cooperation 是 Coherence 問題

**消化筆記**: 2026-05-16-vera-language-llm-design-crm-agent-eval-cooperation

這篇筆記的內部 synthesis 已經很強（Vera + CRMArena + Cultural Evolution 三軸交叉），但跟已消化的 vault 並置後浮現兩個筆記自己沒完整展開的模式：(1) Vera 的 typed effects 不是孤例，是四層收斂中的一層；(2) Cultural Evolution 的 cooperation 資料補上了 multi-step coherence 論的最後一塊拼圖——cooperation 本身是 coherence-at-scale 問題。

---

## Cross-Cutting Theme 1: Typed Effects 在四個架構層獨立收斂

**支援筆記**: `2026-05-16-vera-language-llm-design-crm-agent-eval-cooperation`（新）、`2026-05-13-shepherd-a-runtime-substrate-for-meta-agents-with-formalized-execution-traces`、`2026-05-16-0200-hermes-consolidated-insight`（trifecta firewall）、`2026-05-15-1303-hermes-consolidated-insight`（確定性工具 > 聰明模型）

**信心**: high（4 篇筆記交叉驗證，四層各自獨立抵達同一個設計原則）

### 分析

新筆記指出 Vera 的 `effects(<Http>, <Inference>)` ≒ Open Edison 的 `tool_permissions.json`，定位為「同一個 pattern」。但 vault 裡還有兩層同一個 pattern 的實例，新筆記沒注意到：

| 層 | 實作 | 機制 | 強制時機 |
|---|------|------|---------|
| **Language** | Vera `effects(...)` | typed effects in function signature | compile time |
| **Runtime** | Shepherd typed effect streams | every agent action is a typed event | execution time（emit 即記錄） |
| **Gateway** | Open Edison `tool_permissions.json` | capability whitelist per tool | runtime（gateway 攔截） |
| **Prompt** | Trifecta `trifecta_legs` + `acl` tagging | per-tool-call metadata in system prompt | prompt time（LLM self-policing） |

這不是四個類似但獨立的東西。它們是**同一個設計原則在四個不同信任邊界上的實例化**：

> **在介面層宣告 capability/effect，讓系統層強制執行，不要依賴 LLM 記得或推理。**

Vera 的論證最徹底：「不要讓 LLM 做對，讓 compiler 可以檢查對錯。」Shepherd 的版本是「intent 和 outcome 是分開的 typed events，meta-agent 在 outcome 發生前就能介入。」Open Edison 的版本是「tool 的 permission 不在 prompt 裡（LLM 會忘），在 gateway config 裡（gateway 不會忘）。」Trifecta 的版本是最輕量的：「在 system prompt 裡標記每個 tool call 的 trifecta 類別，session 累積追蹤。」

**為什麼這不是新筆記已經講過的東西**：新筆記只畫了 Vera ↔ Open Edison 的連線。Shepherd 和 Trifecta 都在 vault 裡、都已經消化過、都描述同一個 pattern——但新筆記沒引用它們。把四層攤開的意義是：它證明了這個 pattern 不是兩個專案偶然撞車，而是**不同團隊在不同信任邊界上獨立發明了同一個解法**。這是該成為 Hermes 架構常識的 design pattern。

### 對 Hermes 的 implication

新筆記建議 Hermes 做在「tool description level（prompt time）— 最輕量」。但把四層收斂攤開後，這個建議需要修正：

- **Prompt 層最輕量，但也最不可靠**——它依賴 LLM 讀取並遵守 tool description 裡的 capability 宣告。跟 CRMArena 的保密意識 trade-off（同篇筆記自己引用的）矛盾：加更多 prompt 層的安全標記會吃掉 LLM attention budget。
- **Gateway 層是 Hermes 的正確落點**。既有的 `hermes gateway run` 已經有 transport、有 health check、正在加 auto-diagnosis（見 `2026-05-15-1700-hermes-consolidated-insight.md` Theme 1）。在 gateway 層加 typed effects / capability check 是架構自然延伸，不依賴 LLM attention。
- Shepherd 的 typed effect **stream**（不只是 typed effect **declaration**）提供了一個更遠的目標：不只是「這個 tool 能不能打 HTTP」，而是「這個 tool call 實際打了什麼 HTTP、回了什麼、有沒有 side effect」——runtime trace 本身變成 typed。這和 `2026-05-15-1500-hermes-consolidated-insight.md` 的 Theme 2（trajectory logging 實驗）可以直接對接。

### 可行動下一步

**在 gateway 層實作 minimal typed effects，一個 tool 一個 effect tag，先只記錄不強制。**

1. 在 `native-mcp` 的 tool config schema 加一個 `effects: []string` 欄位（例如 `["fs.write", "http.outbound", "llm.inference"]`）
2. Gateway 收到 tool call 時記錄 effect tag 到 session log（不改行為，純觀測）
3. 跑一週後分析：哪些 tool 的 effect tag 跟實際行為不一致？哪些 effect combo 是危險的（例如 `fs.write` + `http.outbound` 同時出現）？
4. 只有在觀測資料支持後，才把記錄升格為強制（gateway reject mismatched effect）

這是 ~30 行 schema change + ~50 行 gateway logging。跟新筆記的「tool description level」建議相容——可以先兩邊都做，prompt 層當 hint、gateway 層當 enforcement。但 gateway 層是最終的信任邊界。

---

## Cross-Cutting Theme 2: Cooperation 是 Coherence-at-Scale 問題——不只是一個新 benchmark 類別

**支援筆記**: `2026-05-16-vera-language-llm-design-crm-agent-eval-cooperation`（新）、`2026-05-15-1303-hermes-consolidated-insight`（Cost ⇄ Context ⇄ Orchestration）、`2026-05-15-2230-hermes-consolidated-insight`（觀測盲區）

**信心**: medium（3 篇筆記疊出推論，但 cooperation-as-coherence 的因果鏈需要更多數據驗證）

### 分析

新筆記把 Cultural Evolution 論文定位為「提議作為新的 LLM benchmark 類別：不只測 capability，測 cooperative infrastructure。」但跟 vault 裡的 coherence 相關筆記疊在一起後，cooperation data 的意義更深：

**Vera 作者診斷**：LLM 最大的問題是 coherence at scale——「maintaining invariants across a codebase, understanding ripple effects of changes, reasoning about state over time.」

**CRMArena 數據**：多步任務 35% 成功率（掉 23pp from 單步）。多步 = 需要維持 state coherence 的步數增加。

**Cultural Evolution 數據**：Claude 3.5 Sonnet 在 iterated Donor Game 顯著優於 GPT-4o，且是唯一能有效使用 costly punishment 的模型。

這三條線放在一起的推論：**Donor Game 的多回合合作決策本質上是 coherence-at-scale 問題**。Agent 需要追蹤：同伴上一輪合作還是背叛？我該懲罰嗎？懲罰的成本值得嗎？社會規範正在形成還是瓦解？——這些全部是跨多步的 state tracking。Claude 贏 GPT-4o 不是因為 Claude 更「善良」或更「合作」，而是因為 Claude 在跨回合 state tracking 上更強。

換句話說：**cooperation benchmark 不是一個新的 benchmark 類別，它是 coherence benchmark 的一個特例**。跟 CRMArena 的多步 CRM 任務、Vera 的 codebase invariant maintenance 是同一個底層能力的不同表現形式。

### 為什麼這不是新筆記已經講過的

新筆記的 synthesis 表把三篇的診斷並列（coherence at scale / multi-step failure / inter-model variation），暗示它們有共同線索。但它停在三條平行診斷，沒有把 cooperation 摺進 coherence 論——它把 Cultural Evolution 的主要貢獻定位為「model-specific deployment strategy」而非「cooperation = coherence 問題」。

一旦摺進去，一個新的 implication 浮現：**如果 Hermes 未來要跑 multi-agent cooperation（delegate_task 並行 + 結果合併），model selection 不是「選最強 coding model」，而是「選 coherence 最強的 model」**。Cultural Evolution 的數據暗示 Claude > Gemini > GPT-4o 在 cooperative coherence 上——但這是 Donor Game，不是 coding。需要驗證這個排序在 coding cooperation 場景下是否成立。

### 跟既有 vault 的連接

`2026-05-15-1303-hermes-consolidated-insight.md` Theme 2 的洞察——「Cost ⇄ Context ⇄ Orchestration 是同一個問題的三個名字」——在這裡得到新維度：**cooperation 是第四個名字**。Bounded context = predictable behavior = effective cooperation。Cooperation 失敗的機制和 task 失敗的機制是同一個：agent 失去對互動歷史的 coherent model。

`2026-05-15-2230-hermes-consolidated-insight.md` 的「行為品質盲點」也跟這有關：Heartbeat 不會偵測到 agent 的 cooperative behavior degradation——如果 Hermes 開始跑 multi-agent 合作，需要一個新的 sensor 來追蹤 cooperative success rate（delegate_task 的成功/失敗/partial 比率變化）。

### 可行動下一步

**在 delegate_task 的結果 log 加入 cooperative outcome tag，建立 baseline。**

1. 在 `delegate_task` 回傳值加一個 `cooperation_outcome` 欄位：`"success"` | `"partial"` | `"timeout"` | `"conflict"`（兩個 delegate 產出矛盾的結果）
2. 寫入 `heartbeat_action_log.jsonl`，跟現有的 action log 格式相容
3. 累積兩週數據後分析：哪種 task type 的 cooperation 失敗率最高？哪個 model 的 cooperation 成功率最高？
4. 這個數據直接回答「Hermes 要不要為 cooperative task 切換 model」——不需要先做 Donor Game benchmark，用自己生產數據回答。

這是 ~20 行 Python（加一個欄位 + 寫入 log），零新依賴。跟 Theme 1 的 typed effects logging 可以共用同一批 gateway/logging 基礎建設。

---

## 附帶：新筆記內部 synthesis 已覆蓋、不重複的軸線

- **Safety-attention budget competition**（CRMArena 保密 trade-off ≒ Lethal Trifecta）：新筆記已完整分析，且正確指出 runtime mechanism > prompt-time safety。直接引用既有結論，不需要新 theme。
- **Vera 的「為 LLM 設計介面」vs Hermes 的「幫 LLM 補強既有流程」**：新筆記已展開討論並給出合成（短期補丁、長期重新設計）。這個張力是真實的，但不需要再包裝成新 theme。
- **CRMArena 35% 支持 James Shore 維護成本論**：新筆記已明確畫出這條連線。不再重複。

## 已消化筆記標記

本次消化筆記: `2026-05-16-vera-language-llm-design-crm-agent-eval-cooperation`
