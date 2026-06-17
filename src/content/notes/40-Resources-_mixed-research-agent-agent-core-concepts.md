---
_slug: 40-Resources-_mixed-research-agent-agent-core-concepts
_vault_path: 40-Resources/_mixed/research/agent/agent-core-concepts.md
tags:
- hermes
- research
- synthesis
- agent
created: '2026-05-23'
title: Agent Core Concepts
updated: '2026-06-15'
type: research
status: budding
---

# Agent Core Concepts

> 消化 Hermes Agent 研究知識庫的核心整合層。來源：60+ 篇 consolidated insights + 5 篇深度報告。

---

## M1: Memory System Design

### 核心命題

Agent 的記憶瓶頸不在容量，在**萃取與回收機制**。Mem0 v3 的 benchmark 顯示：LLM-based agent 在多 session  後浪費大量 context 在重複學習相同東西，token 效率比單一 pass extraction 低 53%。

### 2026-05-23 → 2026-06-08 新增（48 篇 consolidation 整理）

**獨立新命題（cross-validated 3+ 來源）：**

- **三層架構獨立收斂**（MLMF × Memori × HeLa-Mem × StructMemEval）：working/episodic/semantic 三層在學術理論、實作、benchmark 三方都各自收斂。瓶頸不是容量，是**組織能力**。StructMemEval 證明：給予組織提示，效能提升幅度遠大於選擇更好的記憶系統。

- **Staleness ≠ Decay**（Mem0 × SSGM × Graphiti × Memento × Mnemonic Sovereignty 五源匯聚）：這是 5 個獨立來源在 5 月底 → 6 月初收斂出的最大架構發現。
  - Decay = 低相關性事實隨時間平滑衰減（心臟已有處理）
  - Staleness = **高信心事實突然變錯**（換工作了 / skill 版本號過期）— 是獨立失敗維度
  - 解決方案：bitemporal model（Graphiti `valid_at`/`invalid_at`）或 `confidence_valid_until` 欄位（Zep-style）
  - Hermes 現狀：只做 decay，staleness 完全無產品解

- **多訊號檢索已成共識**（Mem0 × agentmemory × YantrikDB × Graphiti × Memori 五源匯聚）：semantic + BM25 + entity matching 三路並行 → RRF 融合。純向量檢索在生產環境中失敗：entity-level 精確匹配、keyword 口語表達差異、semantic 語義覆蓋三者互補。
  - Mem0 數字：新增 BM25 + entity 後，temporal reasoning +29.6 pts，multi-hop +23.1 pts

- **Write-Gate 是全系統共同盲點**（Mnemonic Sovereignty × MemMachine × Mem0 × OpenMemory × SSGM × Graphiti 六源）：所有生產級記憶系統都缺少寫入前驗證層。OWASP ASI06 (Memory Poisoning) 的根本成因。
  - MemMachine ground-truth anchor（矛盾分數閾值）是目前唯一部分實作

- **Template-level abstraction 是 drift penalty 的正確顆粒度**（APC × agentmemory × Entelgia 三源）：純快取 input/output 失敗，因為同 intent 在不同 context 產生不同計劃。解法是快取「去 entity/numeric」的 plan template。
  - 對 Hermes：distillate 不再追加 raw text，改為 `distillate_id → {content, contradicts, supersedes, confidence_valid_until}` 結構

- **Context Dump 已被四源否定**（RLM paper × Forge × LlamaGym × ShapedQL 四源）：把外部資料塞進 LLM context 是錯誤抽象。RLM 提出 constant-size metadata + REPL 變數；CodeRLM 建 symbol graph as queryable API；ShapedQL 提 Retrieve→Filter→Score→Reorder 四階段。
  - **非顯然結論**：記憶不進入 LLM context，而是 LLM 去查詢外部結構。「讓模型記憶」→「讓模型查表」

- **Bounded Memory Growth 是結構性約束**（RLM × Forge × LlamaGym × ShapedQL 四源）：記憶/狀態必須有界，否則 agent 必然崩潰（時間常數不同）。目前 `heartbeat_learning.py` 是 unbounded distillate accumulation — 結構性風險。

- **Procedural Memory 是被同步識別的缺口**（Mem0 × agentmemory × Metamind × Synix 四源）：episodic（發生什麼）+ semantic（是什麼）+ **procedural（怎麼做）** 三分。Hermes 現有 `skills/` 是靜態寫死，是這個缺口的具體表現。
  - 解法：觀測重複出現的 tool-use sequence，萃取 `(tool_sequence, trigger_condition, outcome_pattern)` triplet

- **Forgetting 是設計 primitive**（Supermemory × MLMF Survey）：唯一 Supermemory 把 explicit forgetting 當 first-class。所有其他框架預設只增不減。Hermes `skills/` 有 `deprecated` frontmatter 但沒 depletion trigger / archive 流程 / 跨 skill 版本繼承。

- **Multi-signal × Action-level Granularity**（Mem0 × AxonFlow × Pomerium × Graphiti 四源）：記憶（ADD-only extraction）+ 治理（per-action auth）從不同方向都收斂到「action-level」是正確粒度。Session-level 太粗；action-level 才是有意義的控制平面。

- **Self-Hosted 是治理工具的預設**（Graphiti × AxonFlow × Pomerium 三源）：所有需要資料主權 + 審計合規 + audit trail 的系統，self-hosted 是架構起點而非選項。

- **構造性失效 vs 時間性失效**（RLM × ShapedQL 雙源）：Hermes 心跳目前只有時間性衰減。需加入結構性失效檢測：當新 distillate 與舊的有矛盾邊（embedding cosine > 0.85 但語意方向相反），**直接將舊節點 confidence 階梯下降至 0**，不依賴時間。

### 關鍵洞察

**1. 雙時間尺度記憶架構**

從 LoCoMo × Memori × ChatIndex 三個研究收斂出一個共同模式：

| 層級 | 時間尺度 | 功能 | 代表的 Hermes 組件 |
|------|----------|------|-------------------|
| L0 | Session 內 | working context，LLM 直接讀取 | run.py prompt injection |
| L1 | 跨 Session | 中期有事實價值的觀察 | observations/ |
| L2 | 長期知識 | 蒸餾後的結構化知識 | vault/research/ |

問題：目前 Hermes 的 L0→L1→L2 傳遞幾乎是斷的。Session 結束時 context 蒸發，observations/ 幾乎不更新，vault/research/ 是純靜態存儲。

**2. 失敗重於成功（Failure-First Learning）**

記憶系統設計的兩個核心對立之一：失敗案例比成功案例更能改進行為。這呼應 Error Notebook 的核心概念——每次失敗應該寫入 action trace，但更重要的是萃取出「什麼情況下這個修復路徑有效」的 pattern。

Hermes 的心跳日誌（heartbeat_decisions.jsonl）是失敗資料庫，但目前沒有從中萃取出結構化的維修知識。

**3. Schema 顯式化**

從 RAIL Protocol × Memori × AgentCore 三個系統的收斂：記憶檢索結果應該帶有 quality score，而不只是純文字。

Memori 的 RankedFact 格式（similarity + rank_score）是參考方向，Hermes 的 session_search 如果能回傳結構化 + 分數，後續的 filtering 和 injection 就能自動化。

### 來自
- `2026-05-20-hermes-knowledge-digestion-plan.md`
- `2026-05-22-hermes-consolidated-insight.md`（三方收斂）
- `2026-05-22-hermes-memory-architecture.md`

### Hermes 啟發
- 建立 L1→L2 的蒸餾管線（目前只有 L0→L1）
- 記憶檢索結果加 rank_score（從 session_search 開始）

---

## M2: Governance & Enforcement

### 核心命題

**能力的瓶頸不在能力本身，在監督層。** Supervisor Agent 研究的實驗數據：Gemini 2.5 Flash 在多步驟任務中約 22.9% 的推理成本浪費在無效 JSON 重試上，Kimi K2.5 的浪費率為零。差距不是模型能力，是監督機制。

### 2026-05-23 → 2026-06-08 新增

- **Enforcement + Measurement 雙層架構**（Forge × Gambit × Cupcake × RLM 四源）：production-grade agent 架構都已收斂到 enforcement（執行）+ measurement（測量）兩層分離。
  - L1 Enforce：Forge ResponseValidator + Rescue parsing + Synthetic respond tool / Cupcake OPA/Wasm
  - L2 Measure：Gambit trace grading + scenario regression / Cupcake LLM-as-Judge watchdog
  - **非顯然結論**：這是 Actor-Critic 同構 — Actor 管動作合法性，Critic 管動作品質。兩層可獨立升級/替換。
  - **Hermes gap**：`sanitize_fetch.py` 是 L1 的部分，但 WS-035 的 observability 沒有 L2 eval harness。Heartbeat 有監控沒有 drift regression。

- **Inline Enforcement > Post-Hoc Monitoring**（AxonFlow × Mem0 × Graphiti 三源）：三個系統（治理、記憶、graph DB）獨立碰到同一個牆：旁觀式架構應付不了高風險、高關聯、長時距的變化。Mem0 staleness 問題根源：retrieval 仍是旁觀式。
  - 對應 Hermes：`heartbeat_learning.py` 是 post-hoc（已存在的 distillate 不會主動標記失效）。Graphiti `invalid_at` 提供 inline 模式參考。

- **MCP 是 Governance 的天然執行層**（Docker AI Governance × MCP Server Patterns 雙源）：MCP Gateway = single chokepoint for auth/authorization/logging。MCP 協議層本身就是 enforcement point，不需另外建 governance bridge。
  - **具體行動**：`hermes_mcp_server.py` 現有「expose tools」邏輯，無 governance layer。可新增 `governed_tool()` decorator，內部呼叫 `govern()` (policy engine)，對每個 tool call 做 deny/allow/logging。優先從 `vault_search` 試點。

- **Tool 用 JSON Schema 做 input/output validation + User consent for tool execution + Activity logs** 是 governance 構件（MCP Server Patterns）。AGT red-team 數據：prompt-based safety 26.67% violation rate，application-layer enforcement 0.00%。**差距 = 26.67%**。單靠 agent 內部意圖識別是不夠的。

- **Decoupled Policy Layer 是 agent 可靠性的核心設計原則**（RLM × Cupcake × Forge 三源）：可靠 agent 不依賴模型自我約束，把約束拉到 agent 外部成獨立 Policy Layer。**anti-pattern**：把 policy/enforcement 放進 model（fine-tuning / system prompt）；**correct pattern**：獨立、可審計、確定性的 policy layer。

- **Action-Level Granularity 是正確粒度**（AxonFlow × Pomerium × Mem0 × Graphiti 四源）：session-level auth 太粗，per-action auth 才有意義。LLM-powered agents make decisions at runtime that static credentials can't anticipate。
  - 對應：Talos 工具呼叫審計 log 結構採 `agent.{tool_name}` 命名慣例（非 session/conversation 維度）。

- **三層隔離梯度**（RLM × Forge × Talos governance 三源）：隔離不是開關，是漸層。
  - L1 最小隔離：local exec、proxy drop-in、tool scoping
  - L2 中介隔離：ipython subprocess、WorkflowRunner、gateway mediation
  - L3 完全隔離：cloud sandbox、guardrails middleware、container
  - **原則**：根據錯誤成本決定隔離等級。Forge + RLM + Talos 都有同款設計，印證此模式是 production 必備。

- **Inline（路徑內）治理比 post-hoc 更有價值**（Graphiti × AxonFlow 雙源）：Graphiti edge-level semantic search 在查詢時過濾 stale facts；AxonFlow WCP 在執行時阻斷危險操作。共同方向：把 enforcement 推到 execution path 內。

- **Fail-Closed > Comprehensive**（Constraint Decay × Forge × CUGA 三源獨立驗證）：**限制 agent 的 action surface，比監控 agent 的所有 action 更有效**。Constraint Decay 量化：comprehensive implicit tooling = -30pp 效能。
  - 三源獨立：學術（Constraint Decay paper 2026-06-06）、開源工程（Forge 2026-06-03）、企業治理（CUGA 2026-05-30）。

- **Policy 動態性 > 靜態規則**（CUGA × Arcade 雙源）：policy 儲存從「靜態規則」走向「可查詢向量空間」是共同方向。Milvus vector DB + keyword/embedding/application/state/tool 動態觸發。靜態 regex matching、寫死 tool description 不足以應對多變行為。
  - 對應 Hermes：FTS5 doc index 是文件級 embedding，缺 metadata 過濾能力。可將 `vault_access.json` access log 結構轉化為 embedding metadata store。

- **Token Budget 必須是 per-proposal exit-code 執法**（Axe × Context Engineering 2026 雙源）：Axe `exit code 4 on token budget exceeded` 是 process-level 契約 — 看到 exit 4 = budget 耗盡，可優雅 abort + 寫 partial state + 通知。
  - **Hermes gap**：`cost.md` 與 `agent-state.json` 有 token tracker，但無 per-proposal budget cap。30 分鐘研究 cron 可燒 $20 USD Opus 4.5，無 code-level 攔截。
  - 具體路徑：`~/.hermes/board/budget_caps.toml`，middleware 檢查 cumulative cost → 超過 → `sys.exit(4)` + 寫 `partial_state.json`。

### 關鍵洞察

**1. Taxonomy-First 失敗分類**

Supervisor Agent 的第一步不是寫代碼，是先發布一個公開的、以真實事件為基礎的失敗模式清單。每個 entry 包含：
- 短名、一行描述
- 真實 incident 範例
- 嚴重性（nudge/block等裁決）
- 檢測方法標籤（deterministic / small-classifier / narrow-llm / hybrid）

這是 supervisor 的 foundation，決定了所有 Specialist 的設計方向。

**2. 三層防禦架構收斂**

從 AWS Security Box × CSS honey-pot × ACE Loop 三個研究，出現一個共同的設計模式：

```
Layer 1 (Sandbox)    — 執行範圍隔離，把危險隔在 agent 能力範圍外
Layer 2 (Policy)     — 顯式規則，infrastructure-level enforcement
Layer 3 (Hook)        — 行為改寫，post-action inspection
```

核心原則：**不要試圖教育 agent 避開什麼，而是把危險隔離在執行範圍之外。**

**3. Enforcement 級別的光譜**

從架構研究中出現一個連續光譜：

| 級別 | 強制力 | 例子 |
|------|--------|------|
| Advisory | soft，LLM 自己判斷 | CLAUDE.md、system prompt |
| Config | 配置層限制 | vault_access.json、feature flag |
| Runtime | 執行時攔截 | sandbox、policy engine |
| Formal | 密碼學驗證 | typed protocol、signature |

Hermes 目前多數 enforcement 在 Advisory 層，缺少 Runtime 層的自動執行。

### 來自
- `2026-05-21-研究報告-supervisor-agent-架構.md`
- `2026-05-23-hermes-architecture-convergence.md`
- `2026-05-20-1401-hermes-consolidated-insight.md`（三層防禦）

### Hermes 啟發
- 建立 Failure Taxonomy（`~/.hermes/errors/taxonomy.md`）
- 現有 sandboxing 機制升級：從 advisory → runtime enforcement

---

## M3: Self-Improvement

### 核心命題

Agent 的改進不只是更強的推理，而是**把每次失敗轉化為可復用的修復資產**。Carnegie Mellon 的研究：leading AI agents 在多步驟任務中成功率只有 30–35%。多數框架專注在「讓成功的跑得更快」，忽略了「讓失敗的變成可學習的經驗」。

### 關鍵洞察

**1. Error Notebook 的五步閉環**

錯誤發生時的處理流程：
```
錯誤輸入 → 分類（classifier）→ 相似 notebook 檢索 → 修復路徑提取 → 顯式驗證清單 → 寫入 action trace
```

分類器（classifier.py）是 pure rules，無 LLM。錯誤進來後用 keyword matching 分五個錯誤域：
- `provider_auth`：api key、auth、unauthorized
- `transient_network`：timeout、rate limit、429
- `file_io`：file not found、encoding、config
- `web_scraping`：selector、extracted content empty
- `workflow_or_logic`：cron、delivery、wrong branch

**2. Self-Referential 的 Meta-Agent**

HyperAgents（Meta, 2026/03）的關鍵創新：meta agent 不僅改 task agent 的行為，也會改 meta agent 自身的 prompt 和策略。這形成一個自我改進的 loop。

對 Hermes 的啟發：每次 heartbeat action 的 retrospective analysis，如果產出的 pattern 能影響下次的 planning strategy，這就是一個 micro self-referential loop。

**3. 失敗模式的蒸餾**

從錯誤日誌到結構化知識需要一個蒸餾層：

```
原始錯誤日誌 → 失敗分類 → 修復路徑 → Pattern 識別 → Action Guideline
```

這個管線目前只有起點（錯誤日誌），缺少後面的環節。

### 來自
- `2026-05-18-研究報告-agent-error-notebook-錯誤治理的務實架構.md`
- `2026-05-16-研究報告-self-improving-ai-agents-的實現方案-2026-年全景.md`

### Hermes 啟發
- Error Notebook 分類層直接適配 Hermes 的 tool calling 失敗
- 心跳 action retrospective 加入 proposed_tool_sequence 分析

---

## M4: Multi-Agent Coordination

### 核心命題

從「單一超強 agent」到「多個專業化 agent 協作網絡」是 2026 年的主流範式轉移。成本、穩定性、可觀測性都因共享記憶層而改善，但知識不共享、行動衝突、協調失效仍是三個根本挑戰。

### 關鍵洞察

**1. 三種記憶層方案**

| 方案 | 代表系統 | 特點 |
|------|----------|------|
| Vector-based Semantic | Mem0 v3 | 多信號檢索（語義 + BM25 + 實體 + 時間），single-pass ADD-only |
| Context Database | OpenViking | L0/L1/L2 三層加載，filesystem paradigm |
| Shared Brain + Lock | junto-memory | MongoDB + ChromaDB，file locking，overlap detection |

**2. Contract-First 輸出格式**

多 agent 協作的核心問題之一：輸出格式不可預測。Contract-first 模式讓每個 agent 的輸出遵循預定義的 schema，降低 LLM 隨機性帶來的介面斷裂風險。

這與 M1 的 Schema 顯式化呼應，也與 Supervisor Agent 的 Specialist verdict 格式一致。

**3. 協調失效的根因**

multi-agent coordination 報告指出三個常見失效模式：
- 知識不共享：每個 agent 重複學習相同東西
- 行動衝突：同時修改同一個檔案（file clobbering）
- 協調失效：沒有結構化的任務分配與結果聚合

Hermes 的委派模式（delegate_task）是目前唯一的協調機制，但缺少 shared state 和 file locking。

### 來自
- `2026-05-19-研究報告-multi-agent-coordination-architectures.md`

### Hermes 啟發
- delegate_task 加 shared memory 機制
- 輸出格式 schema 化（每個 tool call 的 return 結構化）

---

## M5: Architecture Design

### 核心命題

工具邊界、Schema顯式化、執行追蹤是 Hermes 架構當前最需要關注的三個方向。目前 heartbeat 日誌和 session_search 都是無結構的黑盒，無法做 automated policy check 和 ranked filtering。

### 2026-05-23 → 2026-06-08 新增

- **符號化存取（Symbolic Access）取代 Context Dump**（RLM paper × CodeRLM × ShapedQL × Hermes 現狀 四源）：把整個輸入當作 context 處理 → 改為把輸入當作要被 pipeline 流經的結構化對象。
  - RLM paper：把 prompt 存成 REPL 變數，LLM 用 code 檢查（sub-call 是程式化的、可嵌套），只有常數大小 metadata 每輪附加。
  - CodeRLM：symbol graph as queryable API（precise symbols/callers/implementations），不用 glob/grep 把專案塞進 context。
  - ShapedQL：4-stage pipeline (Retrieve→Filter→Score→Reorder) 取代單層向量檢索。
  - **Hermes gap**：distillates 以純文字文本塞進 context。**未實現 symbolic handle 介面**。
  - 具體：建立 `distillate_id → {content, timestamp, confidence, supersedes}` 映射表，LLM 透過 `query_distillates(topic, recency_weight, confidence_threshold)` 讀取。

- **三層可靠性棧**（Forge × LlamaGym × RLM codebase 三源獨立收斂）：

  | 層 | Forge | LlamaGym | RLM codebase |
  |---|---|---|---|
  | **L1 執行層** | ResponseValidator + Rescue parsing | `assign_reward(reward)` | REPL 隔離三層（local → ipython → cloud sandbox）|
  | **L2 驗證層** | SlotWorker | Agent abstract class | Metadata-only trajectory logging |
  | **L3 行為層** | TieredCompact | PPO training loop | Trajectory visualizer |

  **核心洞察**：small models（~8B）需要強制結構，別靠信任。三系統都拒絕「模型自律」。

- **Constrained Decay — 結構約束累積破壞性**（Constraint Decay paper 2026-06-06 二次探索）：80 個 greenfield tasks，structural constraints 累積 → 表現掉 30 pts；其中 45% failures 來自 data-layer defects（壞 query composition + ORM runtime violations）。三層各自獨立的 failure mode（Clean Architecture / PostgreSQL / ORM）。
  - **非顯然結論**：失敗不是「找不到正確 memory」，而是「系統沒有能力將結構約束整合進 decision-making layer」。
  - 對應：現有 `consolidate_memory.py` 輸出 markdown 而非 structured JSON，下游 regex parsing → 改為 PocketFlow shared store 風格 JSON schema。

- **Loop 是普世 pattern，但 Hermes 把它實作成 cron 而非真 loop**（sketch.dev 9-line loop × PocketFlow Prep/Exec/Post graph 雙源）：
  - sketch.dev：agent loop 本質就是 9 行 `while True`，差別在 persistence
  - PocketFlow：所有框架（OpenAI Agents、LangChain、LangGraph、Pydantic Agents）解構成同一個 Prep/Exec/Post graph pattern
  - **Hermes 缺**：in-process loop。心跳是分散式 loop（cron 觸發 → cold start → rehydrate state），缺少 active persistence。

- **雙軌記憶（Mutable Graph + Append-Only Ledger）**（SSGM §6.1 Principle 4）：`Mclean ← argmin_M E[δ(R(M, Kledger), Ktrue)]` — mutable active graph（快速推理） + append-only episodic ledger（事實來源）。
  - **對應 Hermes**：`~/hermes/memories/` 應是 mutable layer；`~/hermes/memory_archive/` 應是 append-only ledger。需驗證目前是否符合雙軌策略。
  - SSGM Theorem 1：reconciliation every N steps 可讓 drift bound 與 horizon T 解耦 → 支持 heartbeat 定期 distillate refresh 設計。

- **Validation Gate 是記憶寫入的必要關卡**（SSGM §6.1 Principle 1 × PycoClaw 雙源）：`Gwrite(ΔM, Mcore)` — write 前做 contradiction check（formal NLI），拒絕與核心事實衝突的更新。沒有 gate 的 autonomous write 會導致 poisoning/drifting。
  - 對應：心跳 distillate pipeline 缺 explicit contradiction check。需在寫入前用 DeepSeek 做 NLI entailment check。

- **Bounded Memory Growth 是結構性約束**（RLM × Forge × LlamaGym × ShapedQL 四源）：
  - RLM：metadata 常數大小（每次只加一行）— 否則 10M+ token prompt context 爆掉
  - Forge TieredCompact：保持最近 N turns，自動截斷 — 小模型承擔不了完整 history
  - LlamaGym `assign_reward()`：直接進 RL loop — observation 不能堆積
  - ShapedQL top-K：1,000,000 候選 → 只取 top-10 進 ranking
  - **共同點**：四個完全無關的系統獨立使用同一個約束。**沒有有界記憶的 agent 必然崩潰**（時間常數不同）。

- **Query-as-Learning**（MuninnDB × Synrix 雙源）：Query 本身就是 learning event。每次 session_search 呼叫時自動遞增該 topic 的 access_count（輕量版 MuninnDB ACT-R 激活）。Push vs pull 是假對立 — hybrid architecture 才是 target。
  - 對應：facts.jsonl 寫入時可加 `RECENCY:` / `PATTERN:` / `RESULT_STORE:` 前綴（Synrix-style namespace），等同 Hebbian association graph 簡化版。

- **Behavioral Delta 是 memory quality 的正確評估**（Synix 8 Systems 雙源）：retrieval accuracy 不是正確的 metric — 真正想要的是 agent 因為經歷而行為不同。
  - 對應實作：兩個 identical agent，一個有特定 memory chunk，一個沒有，跑相同 plan/decision 任務，測量 output 差異。
  - heartbeat_learning.py 的 drift penalty 計算邏輯加入「有/無記憶區塊的輸出差異」作為權重因子。

### 關鍵洞察

**1. 工具隔離的兩個維度合流**

功能隔離（讓 agent 只看到 sanitized surface）與安全隔離（防 prompt injection）正在合流。Hermes 的 sanitize_fetch.py 同時做到了這兩件事——normalize HTML、strip tracking 的同時，也降低了 prompt injection 的隱藏表面積。

**2. Schema 顯式化的三層 gap**

| 層 | 現狀 | 目標 |
|----|------|------|
| Tool registry | vault_access.json 存在，無 version/capability metadata | 完整 capability schema |
| Action output | heartbeat_decisions 無結構，無法 policy check | JSON schema + typed |
| Retrieval output | session_search 無 quality score，無法 ranked filtering | RankedFact + score |

**3. Planning 與 Execution 的 Isolation Boundary**

ACE architecture 的兩階段 planning（abstract plan → concrete plan）在執行前先產出 proposed_tool_sequence。這把 isolation boundary 前移，降低了錯誤決策的執行成本。

對 Hermes 的直接應用：heartbeat Phase 1 產出 proposed_tool_sequence，在執行前可以先做 plan-level retrospective analysis。

### 來自
- `2026-05-23-hermes-architecture-convergence.md`
- `2026-05-22-hermes-mcp-pipeline-consolidated-insight.md`

### Hermes 啟發
- Tool Registry 加入 version/capability metadata
- Heartbeat decision log 結構化
- Session search 回傳加 rank_score

---

---

## M6: Hermes-Specific Gaps & Implementation

### 核心命題

研究與實作之間存在系統性的落差：多個共識模式在 Hermes 中有明確的実装缺口，但從未被正式識別為優先事項。

### 2026-05-23 → 2026-06-08 新增缺口

**16. Staleness 處理完全缺失**（高優先 — 5 源匯聚）
WS-035 設計文件目前只解 staleness 在 retrieval filtering，未做 penalty 觸發。Graphiti `valid_at`/`invalid_at` 4-field bi-temporal model 已存在但無人用於 penalty。
- **Action**：distillate 結構加入 `confidence_valid_until` 欄位。當新 distillate 與舊的存在 contradiction edge（embedding cosine > 0.85 + 語意方向相反），**直接階梯降舊節點 confidence 至 0**，不依賴時間。

**17. Write-Gate Validation 完全缺失**（高優先 — 6 源匯聚）
Mnemonic Sovereignty 指出 Write-gate 是九個治理原語中唯一「共同盲點」。OWASP ASI06 (Memory Poisoning) 直接對應。
- **Action**：心跳 distillate pipeline 加 pre-write NLI check（DeepSeek 做 entailment model），輸出 contradiction score > threshold → 寫入失敗並 log。

**18. Procedural Memory 完全缺失**（中優先 — 4 源匯聚）
`skills/` 系統是靜態文件，不是 agent 從 session 學到的 procedural memory。
- **Action**：snapshot 層新增工具呼叫序列 pattern extraction，`procedural_tags: ["tool-use:{tool_name}", ...]` 寫入 distillate。

**19. Heartbeat Score Loop 仍斷裂**（延續 M6 缺口 #1，5 月已記錄但未修）
heartbeat_patterns.json 寫入了分數，無任何消費者觸發行為。2026-06-08 已累積 16 天的蒸餾產物，無自動 penalty 觸發。
- **Action**：在 `heartbeat_v2.py` 加入 `check_staleness()` + `check_contradiction()` 觸發器，每 N tick 跑一次，distillate graph 自動 invalidate stale nodes。

**20. Bounded Memory 無保證**（中優先 — 4 源匯聚）
目前 distillate accumulation 是 unbounded。RLM 證明：沒有有界記憶的 agent 必然崩潰（時間常數不同）。
- **Action**：滑動窗口（max 20 distillates）；新 distillate 抵達 → 滿則丟掉最低分（recency × confidence × usage_freq）。

**21. Per-Proposal Token Budget Cap 缺失**（高優先 — Axe 模式）
30 分鐘研究 cron 可燒 $20 USD Opus 4.5，無 code-level 攔截。
- **Action**：`~/.hermes/board/budget_caps.toml`，middleware 檢查 cumulative cost → 超過 → `sys.exit(4)` + 寫 `partial_state.json`。consolidate_memory.py 為第一個 reference 實作（加 `--budget-tokens 50000` flag）。

**22. L1 Enforce + L2 Measure 雙層 governance 不存在**（高優先 — 4 源匯聚）
Forge（執行層）+ Gambit（測量層）模式未在 Hermes 實作。
- **Action**：建 `talos-proposals/WS-NNN-governance-dual-layer.md`。L1：sanitize_fetch.py 升級為 ResponseValidator + Rescue parsing 風格。L2：5-8 個 golden scenario + bash + jq 腳本 + behavior_regression.jsonl。

**23. symbolic handle 介面缺失**（中優先 — 4 源匯聚）
distillates 仍以純文字文本塞進 context。RLM paper 證明這是錯誤抽象。
- **Action**：建立 `distillate_id → {content, timestamp, confidence, supersedes}` 映射表，LLM 透過 `query_distillates()` 查詢（不是全量 dump）。

**24. Triple Extraction 沒有 frontend validator**（中優先 — Constraint Decay 啟發）
heartbeat_learning.py 的 triple extraction 沒有 sanitization layer。如果有 hallucinated triples，整個 drift detection cascade 會被放大。
- **Action**：在 extraction function 後插入 `validate_triples()`（schema check：subject/predicate/object 非空、predicate 在白名單內、object token 上限）。預期 noise floor 砍 30-50%。

**25. consolidate_memory.py 輸出非結構化**（低優先 — Constraint Decay 啟發）
輸出 markdown，下游 regex parsing。改為 JSON schema 下游更穩。
- **Action**：在 stdout 末尾附加 `## MACHINE_OUTPUT` 區塊 emit 結構化 JSON。下游 consumer 改吃 JSON。

**26. Hermes 缺少 in-process loop**（低優先 — sketch.dev/PocketFlow 啟發）
心跳是分散式 cron loop，無 in-memory shared store。
- **Action**：prototype `heartbeat_loop.py`（≤ 50 行），用 `while True` + in-memory shared store 跑 5 個 tick。量化 cold-start rehydrate cost 與 cron-based latency 差異。目標不是替換 cron，是量化 constraint decay 啟發的 noise floor 放大器。

**27. Three-Layer Memory（`~/hermes/memories/` vs `~/hermes/memory_archive/`）未驗證是否符合雙軌策略**（SSGM §6.1 Principle 4 啟發）
應為 mutable layer + append-only episodic ledger。
- **Action**：驗證 `~/hermes/memories/` 是否真的執行 mutable active graph 邏輯。若不是，設計 migration plan：writes → validation gate → dual write（mutable + append-only）；read path 先查 mutable，ledger 作為 fallback/fact source。

**28. Constraint Decay paper 5 天內被二次探索且結論獨立**（元觀察）
5 月底 → 6 月初累積 5+ 個 governance / memory / structural 層共識。是 hermes 對該 topic 已「成熟理解」的訊號。
- **Action**：下次 cron 若又跑出 Constraint Decay 相關新筆記，應主動懷疑是否重複探索。consolidate_memory.py 加 dedup 機制（比對 source arxiv id）。

### 關鍵缺口

**1. Heartbeat 系統架構（M6 / M3 交叉）**

來源：`2026-05-14-hermes-heartbeat-project-proposal.md`

雙層設計：
- 自主層（30s，零 token）— WORK/CONNECT/EVOLVE/REST/REPORT 五個閉環
- 認知層（30min，決策迴路）

現狀：心跳日誌存在，但 Rubin Score Loop 斷裂 — 分數被寫入 `heartbeat_patterns.json`，但無任何消費者觸發行為（蒸餾/驅逐/暫停）。

→ **Action**：補上 threshold-trigger circuit

**2. LoopTrap — 自我終止可被遊戲（M3 安全性）**

來源：研究報告（2026-05-13、05-15、05-20）

自我評估的終止條件可被 prompt manipulation 放大 3.57×（最高 25×）。對 Hermes 的直接衝擊：heartbeat 的內省階段若依賴 self-evaluation 作為終止信號，存在同樣漏洞。

→ **Action**：所有 heartbeat 循環必須有確定性的停止條件（不只是 LLM 自我判斷）

**3. Architect / Executive 分離（架構重構方向）**

來源：研究報告（2026-05-13、05-15）

「Attention Latch」：長期對話中累積的 context weight 使 correction instruction 被覆蓋。解決：planning 與 execution 不共享 context，防止 attention contamination。

對 Hermes 的直接應用：heartbeat Phase 1（proposed_tool_sequence）與 Phase 2（execution）之間需要有明確的 context boundary，而非連續堆疊。

**4. 信任邊界：Sub-Agent 審計追蹤（M6）**

來源：`2026-05-18-1748-hermes-consolidated-insight.md`

`delegate_task` 的 traceability 為空白：`action_log.json` 只有 action 層，沒有 sub-agent 級的 provenance metadata。DCG Robot Mode JSON 具備 Hermes session detection，可餵入 Talos audit trail。

→ **Action**：每個 sub-agent 的 tool calls 需要寫入含 provenance 的 structured log

**5. 知識邊界：L1/L2 分離缺失（M6）**

來源：`2026-05-18-1748-hermes-consolidated-insight.md`

WUPHF 的 L1（不可變原始來源）vs L2（蒸餾後知識）邊界防止 agent self-reinforcement bias。Hermes 的 `autonomous_notes/` 同時充當 L1 和 L2，沒有不可變性保證。

→ **Action**：考慮 RAW/（append-only）+ PROCESSED/（LLM workspace）的雙層分離

**6. EvolveMem — 檢索機制本身需要演化（M1）**

來源：研究報告（2026-05-16）

現有 memory 系統凍結檢索機制，只演化內容。EvololveMem 將檢索評分本身作為 action space。

→ **Action**：vault lookup 的 BM25 re-rank 層缺失（Memori 生產級標配）

**7. Token Budget 三維優化（M6）**

來源：`2026-05-15-0005-hermes-consolidated-insight.md`

Token 同時佔用：(1) context window、(2) prompt cache cost、(3) attention dilution。壓縮同時優化三個維度。Hermes 缺少 zero-token deterministic fallback path（當預算耗盡時的優雅降級）。

---

## 待補充空缺

- [x] M6 新增：Hermes-specific gaps（上方 7 個模式）
- [ ] M1: EvolveMem 啟發的 retrieval 演化機制實作方向
- [ ] M3: LoopTrap 的確定性停止條件實作（heartbeat terminator）
- [ ] M5: Tool Registry 加 version/capability metadata（Schema 顯式化第一步）
- [ ] M2: Failure Taxonomy 建立（`~/.hermes/errors/taxonomy.md`）

---

*本文件是迭代整理的產出，每次閱讀新報告後更新相應章節。*
*最後更新：2026-06-08（第三次消化迭代：48 篇 consolidated insight，2026-05-24 → 2026-06-08；新增 M1 三層架構 + Staleness + 多訊號 + Write-Gate + Template abstraction + Context Dump 否定 + Bounded memory + Procedural memory + Forgetting + Multi-signal × Action-level + Self-hosted + 構造性失效、M2 雙層 governance + Inline enforcement + MCP governance + JSON Schema validation + Decoupled policy + Action-level + 三層隔離梯度 + Fail-closed + Policy 動態 + Token budget exit-code、M5 符號化存取 + 三層可靠性棧 + Constraint Decay + In-process loop + 雙軌記憶 + Validation gate + Bounded memory + Query-as-learning + Behavioral delta；M6 新增缺口 #16-#28，共 12 個 hermes-specific implementation gaps）*