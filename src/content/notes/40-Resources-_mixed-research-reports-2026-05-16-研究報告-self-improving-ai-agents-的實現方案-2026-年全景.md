---
_slug: 40-Resources-_mixed-research-reports-2026-05-16-研究報告-self-improving-ai-agents-的實現方案-2026-年全景
_vault_path: 40-Resources/_mixed/research/reports/2026-05-16-研究報告-self-improving-ai-agents-的實現方案-2026-年全景.md
tags:
- research
- knowledge
- ai-agent
created: '2026-05-16'
version: 1
source_report: 2026-05-16-self-improving-ai-agents.md
source_url: null
type: research
fingerprint: agent, meta, code, dgm, memory, github, self-improving, coral, benchmark,
  https
title: 研究報告：Self-Improving AI Agents 的實現方案 — 2026 年全景
updated: '2026-06-15'
status: budding
---

# 研究報告：Self-Improving AI Agents 的實現方案 — 2026 年全景

## Version 1 — 2026-05-16

### 核心觀念
**問題**：**為什麼這個問題重要？** 目前的 LLM-based agent 有一個根本性的矛盾：模型權重是靜態的（訓練完就凍結），但 agent 需要在動態環境中持續學習。傳統 RL finetuning 昂貴、慢、且需要大量標註資料。Self-improving agent 的核心命題是：**能否讓 agent 在部署期間自行發現弱點、修正錯誤、累積經驗，而不需要重新訓練模型？** 這不是一個新的問題——從 Schmidhuber 的 Gödel Machine（2003）到近年 AutoGPT 的興起，self-improvement 一直是 AI agent 的聖杯。但 2025-2026 年…

**洞見**：這波 self-improving agent 的進展，標誌著 agent 設計正從 **hand-crafted prompt engineering** 走向 **automated design + continuous evolution**。幾個重要影響： 1. **Agent 不再是靜態的**：HyperAgents 和 DGM 展示了 agent 可以在部署後持續變好，不需要人類介入。這意味著「部署即凍結」的時代正在結束。 2. **Meta-agent 的湧現**：當一個 LLM 可以程式設計另一個 LLM 的行為時，我們看到了一種新的抽象層次——agent 成為 meta a…

### 架構 / 機制
## 2. Core Mechanism

2026 年的 self-improving agent 實現方案可以歸納為四條技術路線：

### 路線一：Meta-Agent 寫 Code 進化（Code-as-Thought）

這是 2026 年最重要的突破方向。核心思路是：讓一個 **meta agent**（本身是 LLM）**寫程式碼來定義/改進 task agent**，然後在 benchmark 上驗證。

**HyperAgents（Meta, 2026/03）** 的架構：
```
meta_agent.py  ──programs──>  task_agent.py  ──evaluates──>  benchmark score
       ↑                                                          |
       └──────────────── feedback loop ──────────────────────────┘
```
- Meta agent 讀取現有 task agent 程式碼 + benchmark 分數
- 提出 diff/patch 來改進 task agent
- 改進後的 agent 在 benchmark 上跑，分數回饋給 meta agent
- **關鍵創新**：meta agent 不僅改 task agent 的行為，也會改 meta agent 自身的 prompt 和策略（self-referential）

**Darwin Gödel Machine（Sakana AI, 2025/05）** 的架構：
```
Archive of agents (sorted by score)
       ↓
  Select promising agents ──→  Mutate (LLM proposes code edits)
       ↓                           ↓
  Evaluate on SWE-bench    ←  New agent variant
       ↓
  Add to archive if better
```
- 維護一個不斷增長的 agent 存檔（archive），按 benchmark 分數排序
- 每次迭代：從存檔選出有潛力的 agent → LLM 提出 code 改動 → 評估 → 好的保留
- **關鍵創新**：結合了達爾文演化（多樣性 + 選擇）和 Gödel Machine（自我修改程式碼）的概念
- 實驗顯示 DGM 發現了 patch validation、更好的 file viewing、multi-solution ranking、failure history 等有效改進

**ADAS / Meta Agent Search（Hu, Lu, Clune, 2024）** 開了第一槍：
- Meta agent 用程式碼定義 agentic system（prompts、tool use、control flow）
- 反覆程式設計新的 agent，維護 archive
- 發現了超越 hand-designed agent 的新設計
- **強調**：因為 code 是 Turing-complete，理論上可以發現任何可能的 agent 設計

### 路線二：語言化反思與記憶（Verbal Reinforcement Learning）

不是改 code，而是改「agent 的內部文字記錄」。

**Reflexion（Shinn et al., 2023）** — 這個方向的奠基論文：
```
Task attempt → 失敗/成功訊號 → LLM 生成「反思文字」 → 存入 episodic memory
                                              ↓
                               下一次嘗試時載入作為 context
```
- 不需要更新模型權重
- 反思內容存在 episodic memory buffer
- 在 HumanEval 上達到 91%（GPT-4 baseline 80%）

**Autocontext（greyhaven-ai, 2026）** 把反思推向工程化：
- 五個角色協作：**competitor** 提出方案 → **analyst** 分析結果 → **coach** 轉化為 playbook → **architect** 在卡住時改 harness → **curator** 控管跨 run 的知識繼承
- 關鍵產物是 **playbook.md** — 存活下來的經驗會自動傳給下一輪 agent
- 支援 10+ provider（Anthropic, OpenAI, Gemini, Pi, Claude Code, Codex CLI 等）

**Letta（前 MemGPT）** 的 dreaming/reflection 機制：
- Agent 跨 session 持久存在，擁有 self-editing memory
- 「Dreaming」= agent 在閒置時自動回顧對話、提取學習、更新 memory blocks
- Memory blocks 分為 `human`（關於使用者的知識）和 `persona`（agent 的自我認知）

### 路線三：Multi-Agent 協作演化（Swarm Self-Evolution）

**CORAL（Human-Agent Society, 2026/04）**：
- 每個 agent 跑在獨立的 git worktree 中（檔案隔離 + 低成本）
- `.coral/public/` 作為共享知識空間，symlink 進每個 worktree
- Agent 彼此可以看到嘗試結果、notes、skills，即時共享
- 支援 Claude Code、Codex、OpenCode、Cursor Agent、Kiro 五種 runtime
- Eval loop：agent 呼叫 `coral eval` 來 staging、commit、grading 一氣呵成

**GPTSwarm（KAUST, ICML 2024）**：
- 將 agent swarm 建模為可優化的 graph
- Edge optimization：用 RL 調整 agent 之間的連接權重
- 邊的優化自動決定哪些 agent 之間應該通訊、哪些應該被修剪
- 支援 edge pruning（移除無效連接）和 edge creation（建立新連接）

### 路線四：從 Deployment Trace 學習（Production Learning）

**Autocontext** 也提供了 production trace capture：
- `instrument_client()` 包裝 Anthropic/OpenAI client，擷取所有 API call
- 自動建立 scoped dataset
- 從 production 行為中提取改進策略

### 思考
## 4. Limitations / Honest Assessment

這些系統的潛在缺陷和我們的獨立評估：

### (a) 評估瓶頸（Evaluation Bottleneck）
所有 self-improving 系統都依賴可靠的 evaluation signal。如果 benchmark 太簡單或太窄，agent 會 overfit；如果 evaluation 需要人類判斷，scale 不起來。DGM 在 SWE-bench 上的改進是否可泛化到真實世界的程式碼任務，仍是未解問題。

### (b) 安全風險（Safety Concerns）
Meta 和 Sakana AI 都在 README 中加了⚠️警告：系統會執行 LLM 生成的未信任程式碼。DGM 明確說「可能在模型能力或 alignment 限制下產生破壞性行為」。這不是理論風險——一個自我修改的 agent 理論上可以刪除自己的 safety guard。

### (c) Model Collapse / Mode Collapse
當 agent 用自己的輸出訓練自己時，可能出現品質退化。Autocontext 的 curator 角色試圖緩解這點，但 gate 機制本身也是 LLM-based，可能出錯。

### (d) 成本問題
HyperAgents 和 DGM 需要大量 LLM API 呼叫。一次完整的演化週期（meta agent 提案 → task agent 評估 → 回饋）可能需要數百到數千次呼叫。對個人開發者而言，用 GPT-5/Opus 跑完整 DGM 循環成本可能高達數百美元。

### (e) 可靠性與複製性
- HyperAgents 的 license 是 CC BY-NC-SA 4.0（非商業），限制了應用場景
- DGM 需要 NVIDIA GPU 跑 Docker 隔離評估
- 很多系統宣稱的改進是在特定 benchmark 上，缺乏跨領域驗證
- 大多數 repo 的 star 數和實際活躍貢獻者不成比例（有些千星 repo 只有 1-2 個主要 contributor）

### (f) 對比既有方案
| 方案 | 與 AutoGPT 差異 | 與 CrewAI 差異 |
|------|----------------|----------------|
| HyperAgents | 不靠 hand-crafted prompt，meta agent 寫 code 進化 | 沒有固定 agent role，agent 設計自動演化 |
| DGM | 演化對象是 agent 的 code，不是 task plan | 非 multi-agent 協調，是 single agent 的自我改進 |
| GPTSwarm | graph-based 優化取代線性 pipeline | RL 優化連接而非靜態拓撲 |
| CORAL | git worktree 隔離 + 共享知識空間 | 真正的自主演化，非預設 workflow |

**來源類型**：unknown

### 應用
## 5. Actionable for Our Projects

### 對 firn（我們的 agent 系統）的具體建議

#### 🔴 立即可行（TRIVIAL-MODERATE）

**a) 引入 playbook 機制（靈感：Autocontext）**
- 在 firn 的 session 結束時，自動生成一個 `playbook.md`，總結本 session 學到的教訓
- 下次 session 開始時自動載入
- 實作難度：**MODERATE**（需要 prompt 設計 + 檔案管理）
- 免費方案可運作

**b) 反思步驟（靈感：Reflexion）**
- 在 firn agent 每次完成大型任務後，追加一個 reflection step
- Agent 自問：「剛才的執行中有什麼可以改進的？下次遇到類似任務我會怎麼做？」
- 將反思結果 append 到 session context
- 實作難度：**TRIVIAL**（就是多加一個 prompt）
- 免費方案完全可運作

**c) Memory 持久化（靈感：Letta）**
- 讓 firn agent 擁有跨 session 的 self-editing memory
- Memory blocks 可以包含：使用者偏好、常用 workflow、已知的 pitfall
- Agent 可以在執行中主動更新自己的 memory（「我注意到你偏好 X 格式，我記錄下來了」）
- 實作難度：**MODERATE**（需要設計 memory schema + 讀寫介面）
- 免費方案可運作（存在本地 JSON/SQLite）

#### 🟡 中期規劃（MODERATE-HARD）

**d) Multi-agent 隔離執行（靈感：CORAL）**
- 用 git worktree 為每個 sub-agent 建立隔離環境
- 共享 `.firn/public/` 目錄作為知識交換空間
- 實作難度：**HARD**（需要 git worktree 管理 + sub-agent spawn + 狀態同步）
- 免費方案可運作

**e) Agent graph optimization（靈感：GPTSwarm）**
- 將 firn 的 agent pipeline 建模為 graph
- 用簡單的 edge weight 調整來優化 agent 間的連接
- 實作難度：**HARD**（需要 graph 引擎 + 優化演算法）
- 免費方案可運作，但 RL 部分可能需要較多 API 呼叫

#### 🟢 長期追蹤（RESEARCH-ONLY）

**f) Meta-agent 寫 code 進化（靈感：HyperAgents/DGM）**
- 讓 firn 的 meta-agent 可以修改 firn 自身的程式碼來改進效能
- 需要 sandbox 執行環境 + benchmark 評估
- 實作難度：**RESEARCH-ONLY**（安全風險高、成本高、需要大量 infra）
- **不建議現階段實作**，但值得追蹤 Meta/Sakana 的後續發展

### 對其他專案的建議

- **hermes-agent** 本身已經有 skill system 和 memory，接近 Letta 的設計方向。可以借鑑 Letta 的 dreaming 機制，讓 Hermes 在閒置時自我回顧和優化 skills。
- **managed-agents** 可以借鑑 CORAL 的 worktree 隔離 + shared knowledge 架構。


### 來源

- 原始報告：2026-05-16-self-improving-ai-agents.md
- 類型：
- 連結：
