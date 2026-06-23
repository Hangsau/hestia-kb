---
_slug: 40-Resources-_mixed-explorations-2026-06-04-Exploration---AI-Agent-Architecture--PM-Guide---ProfileGPT
_vault_path: 40-Resources/_mixed/explorations/2026-06-04-Exploration---AI-Agent-Architecture--PM-Guide---ProfileGPT.md
title: 'Exploration — AI Agent Architecture: PM Guide + ProfileGPT + Masterman Survey
  (2026-06-04)'
created: '2026-06-04'
updated: '2026-06-15'
type: exploration
tags: []
status: budding
---

# Exploration — AI Agent Architecture: PM Guide + ProfileGPT + Masterman Survey (2026-06-04)

**延續自**: [[Synix 8-Systems (2026-06-01)]] — 同樣聚焦 agent 記憶/協作架構

## Per-Source Insights

### 1. ProductCurious — "A PM's Guide to AI Agent Architecture" (208 pts, Sep 2025)

**核心**：從 PM 視角看 agent architecture layers，不是從研究员角度。

Layer stack（4層）：
1. **Context & Memory** — session/customer/behavioral/contextual 四類記憶。支撐「anticipate needs」而非「react to queries」。成本與複雜度隨記憶深度增加。
2. **Data & Integration** — 系統整合深度決定是 tool 還是 platform。成功 agents 從 2-3 個 key integrations 出發，按使用者實際需求擴展。
3. **Skills & Capabilities** — 差異化在於 right capabilities 而非 most features。MCP 降低 skills 跨 agent 共享的摩擦。
4. **Evaluation & Trust** — 準確性 ≠ 信任。counterintuitive insight：users trust agents that admit uncertainty than confidently make mistakes。

Architecture patterns（4種）：
- **Single-Agent**：簡單、易 debug、可預測成本。適合 well-defined tools + 不需要多方回饋的場景。多數團隊從這開始且不需要離開。
- **Skill-Based**：router + specialized skills。skill 可獨立優化（便宜模型處理簡單 skill、贵的處理複雜）。MCP 標準化 skill capabilities 暴露。
- **Workflow-Based**（Enterprise）：LangGraph/CrewAI/AutoGen/N8N。Predefined step-by-step processes。可審計、合規友好，但使用者 edge cases 不符合 workflow 時會卡住。
- **Collaborative**：多 specialized agents 以 A2A protocol 協作。願景佳（booking.com agent ↔ American Airlines agent），但 security/billing/trust/reliability 複雜度多數公司還沒準備好。Debugging multi-agent 極難。

**PM 的 trust 反直覺 insight**：
- Confidence calibration：說 60% 準就要真的是 60%，不是 90%
- Reasoning transparency：展示 agent 的工作過程
- Graceful escalation：碰到極限時平穩轉給人類並帶完整上下文

### 2. Sahbi Chaieb — "ProfileGPT: AI Agents Collaboration Architecture" (106 pts, Apr 2023)

**核心**：三 agents 協作框架用於從 ChatGPT history 萃取 user profile。
- **Psychoanalyst**：心理分析 + profiling（PhD + forensic psychology 背景）
- **Psychohistorian**：行為模式預測（foundation 科幻的 Hari Seldon 角色）
- **Stalker**：線上個人資訊收集

Versioning insight（防 blocking 的 prompt engineering）：
- V1：白帽資訊專家 → 被 model 封鎖（refuses to give away personal data extracted）
- V2：重新命名為 "The little bunny"（好奇、愛發掘資訊的輕鬆角色）+ 「遊戲化：答對贏胡蘿蔔🥕」→ 成功繞過封鎖

Architecture notes：
- 個別 agent 以 Markdown 格式化輸出
- 共同輸入：ChatGPT history + 公開 web 資料

### 3. Masterman et al. — "Survey: AI Agent Architectures for Reasoning, Planning, Tool Calling" (arXiv:2404.11584, Apr 2024)

**核心**：academic survey，single vs multi-agent 的系統性分類。

Single-agent patterns（key insight）：
- **ReAct**：reasoning + acting 交織。6% hallucination rate vs CoT 14%（HotpotQA）。限制：可能重複相同 thoughts/actions 無法 exit loop。
- **RAISE**：加入 short-term（scratchpad）+ long-term（similar examples）memory。Fine-tuning smaller model outperforms larger non-fine-tuned。問題：複雜邏輯理解不足、hallucinate role/knowledge（sales agent unexpectedly retains Python ability）。
- **Reflexion**：LLM evaluator 提供 linguistic feedback。改善成功率 + 降低 hallucination。限制：非最佳 local minima、sliding window long-term memory（有 token limit）、diversity/exploration/reasoning 任務仍有改進空間。
- **LATS**：Monte Carlo Tree Search + self-reflection reasoning。限制：complexity 高（更多 compute + time）、benchmark 過於簡單（未測 tool calling/complex reasoning）。

**Multi-agent key findings**：
- 垂直架構（leader + reporters）：團隊有 designated leader 完成任務快近 10%、leader 60% communication 在給 directions、團隊無 leader 時浪費 50% 时间在互相下 orders。
- 動態團隊（rotating leadership）提供最低 time-to-completion + 最低 communication cost。
- 批評-反思（criticize-reflect）步驟對生成計劃、評估表現、反饋、重組團隊關鍵。
- **MetaGPT**：Structured outputs（documents/diagrams）而非 unstructured chat。Pub-sub mechanism for information sharing — agents 只讀與自己目標相關的資訊。降低無效聊天噪音。
- **DyLAN**：每 round 動態決定 agent 貢獻量，只讓 top contributors 進入下一 round。水平架構、無 leader。證明動態團隊 + agent 貢獻 ranking 有效。

**Trust/Sycophancy finding**：
- Agents are susceptible to feedback from other agents even if the feedback is unsound → 可能集體走向 faulty plan。
- LLMs exhibit sycophantic behavior：傾向鏡像使用者立場，即使這意味放棄 impartial/balanced viewpoint。
- Human oversight 改善 immediate outcome + 減少走進無效路径的可能性。

## Hermes 啟發

### 1. Talos/Hestia 協作架構對照
- Masterman Survey：三 agents 有 designated leader 完成任務快 10%。Guo et al. 顯示 human leader > agent leader。
- **Talos/Hestia 現況**：Hestia 是事實上的 architect，Talos 是 executor。此分工符合 vertical architecture 的 leader-driven 效率優勢。
- ProfileGPT 的 versioning lesson：重新定義角色框架（bunny）可以繞過 model 限制。這與 Hermes personality framing（如 Talos-as-guardian）的效果互補。

### 2. Memory Layer — 從 PM Guide 和 Survey 的分歧
- PM Guide：四層記憶（session/customer/behavioral/contextual）支撐 anticipate-not-react。
- Survey（RAISE）：short-term scratchpad + long-term examples。沒有結構化 semantic memory。
- **差距**：Survey 時代（2024 Apr）的 agent memory 仍是 document-level retrieval，尚未到 structured memory（如 Mem0/YantrikDB 的 entity/triple 層）。
- Synix 8-systems 分析的結論（「結構化記憶 > 純嵌入檢索」）領先於 2024 survey。

### 3. Trust Layer — Hermes 尚無 Explicit Mechanism
- PM Guide 三 trust strategy（confidence calibration、reasoning transparency、graceful escalation）對應 Survey 的「human oversight improves outcomes」。
- Talos 的 `_check_code_quality()` 和 heartbeat EVOLVE 的 drift detection 是內隱的 trust building，但沒有向使用者暴露 confidence score。
- **建議**：WS-035 這類 structured memory 提案可以加入 `confidence_indicator` 欄位（新資訊進來時降級舊資訊的 confidence）。

### 4. Multi-Agent Collaboration Pitfalls
- Survey 的「chatter noise」問題：水平架構中 agents 收到所有訊息。MetaGPT 的 pub-sub 解決這個。
- Talos-Hestia comms 目前是 INBOX → 讀取 → 回覆 模式，沒有訊息優先級或 topic filter。Comms-reply cron 的實現是簡單的雙軌（timer + 獨立 cron），但仍屬於「全部讀取」模式。
- ProfileGPT 的「bunny trick」是一種角色框架重構，未來可用於 comms prompt 的角色宣告。

## 跨文章 Synthesis

三篇文章構成從 **operational（PM Guide）→ implementation（ProfileGPT）→ academic（Survey）** 的視角階梯：

1. **PM Guide 給出 architecture decision framework**：何時用 single vs skill-based vs workflow vs collaborative。這與 Survey 的「選擇標準」一致（single: well-defined tools; multi: feedback beneficial, parallelization needed, no examples given）。

2. **ProfileGPT 是 skill-based architecture 的 early example**（2023）：三 agents 各有 specialization、versioning to avoid blocking。MCP 之前的 tools 共享模式。與 Masterman Survey 的「skill-based better than single」呼應。

3. **Survey 的 limitations（6.6 Bias/Fairness）直接支援 PM Guide 的 trust insight**：LLM agents are "less robust, prone to more harmful behaviors, and capable of generating stealthier content than LLMs"。PM Guide 的 counter-intuitive trust design（admit uncertainty > confident mistakes）是對 Survey bias finding 的 operational 回應。

4. **Gap**：Survey（2024 Apr）和 PM Guide（2025 Sep）都沒有提到 memory 的 structured representation（如 Mem0/Graphiti 的 entity/triple 層）。兩者的 memory 仍是 document-level 或 scratchpad-level。Synix 8-systems 揭示的「結構化 > 純嵌入」領先於主流 agent architecture 討論。

## 未追蹤 Leads

- ~~https://www.productcurious.com/p/a-pms-guide-to-ai-agent-architecture~~ → reachable, fully fetched
- ~~https://sahbichaieb.com/profilegpt/~~ → reachable, fully fetched
- ~~https://arxiv.org/html/2404.11584~~ → reachable, fully fetched

## ✅ 本次探索完成